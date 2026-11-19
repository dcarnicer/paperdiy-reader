#include "BatteryLog.h"

#include <BoardConfig.h>
#include <HalPowerManager.h>
#include <HalStorage.h>
#include <Logging.h>
#include <TrustedTime.h>

#include <cstdio>
#include <cstring>

#ifndef CROSSPOINT_VERSION
#define CROSSPOINT_VERSION "unknown"
#endif

namespace {
constexpr const char* LOG_PATH = "/battery-log.csv";
constexpr const char* OLD_LOG_PATH = "/battery-log.old.csv";
constexpr uint64_t MAX_LOG_BYTES = 1024 * 1024;
constexpr unsigned long SAMPLE_INTERVAL_MS = 5 * 60 * 1000;

constexpr const char GLOBAL_HEADER[] =
    "# battery-log v2 board=%s fw=%s\n"
    "epoch,uptime_s,event,mv,pct,chg,usb,reader,wifi,vin_mv,vout_mv,pwr_src,pages\n";

bool writeHeader(HalFile& file) {
  char header[256];
  const int length =
      snprintf(header, sizeof(header), GLOBAL_HEADER, BoardConfig::ACTIVE.name, CROSSPOINT_VERSION);
  if (length <= 0 || length >= static_cast<int>(sizeof(header))) return false;
  return file.write(reinterpret_cast<const uint8_t*>(header), static_cast<size_t>(length)) ==
         static_cast<size_t>(length);
}

// A power loss during an append can leave half a CSV line at the end. Truncate
// back to the last complete line so the next row is not glued to the fragment.
bool repairTornTail() {
  if (!Storage.exists(LOG_PATH)) return true;

  HalFile file = Storage.open(LOG_PATH, O_RDWR);
  if (!file || !file.isOpen()) {
    LOG_ERR("BATLOG", "Tail check: open failed");
    return false;
  }

  const uint64_t size = file.fileSize64();
  if (size == 0) return true;
  if (file.seek64(size - 1) && file.read() == '\n') return true;

  constexpr size_t CHUNK = 256;
  uint8_t buffer[CHUNK];
  uint64_t end = size;
  while (end > 0) {
    const uint64_t start = end > CHUNK ? end - CHUNK : 0;
    const size_t length = static_cast<size_t>(end - start);
    if (!file.seek64(start)) break;
    const int got = file.read(buffer, length);
    if (got <= 0) break;
    for (int i = got - 1; i >= 0; --i) {
      if (buffer[i] != '\n') continue;
      const uint64_t keep = start + static_cast<uint64_t>(i) + 1;
      if (!file.truncate(keep)) {
        LOG_ERR("BATLOG", "Tail repair: truncate failed");
        return false;
      }
      file.flush();
      LOG_INF("BATLOG", "Dropped torn tail (%llu -> %llu bytes)", static_cast<unsigned long long>(size),
              static_cast<unsigned long long>(keep));
      return true;
    }
    end = start;
  }

  if (!file.truncate(0)) return false;
  file.flush();
  LOG_INF("BATLOG", "Dropped torn file (%llu bytes, no complete line)", static_cast<unsigned long long>(size));
  return true;
}

// v1 rows have no `pages` column. Rotate the old file instead of appending
// rows with a different width under the old header.
bool legacyLogNeedsRotation() {
  if (!Storage.exists(LOG_PATH)) return false;
  HalFile file = Storage.open(LOG_PATH, O_RDONLY);
  if (!file || !file.isOpen()) return false;
  char header[24] = {};
  const int got = file.read(header, sizeof(header) - 1);
  return got > 0 && strncmp(header, "# battery-log v1", 16) == 0;
}
}  // namespace

void BatteryLog::begin() {
  ready = false;
  rotationFailed = false;
  lastSampleMs = 0;
  pageTurns = 0;

  if (!Storage.ready()) {
    LOG_ERR("BATLOG", "SD not ready; battery log disabled");
    return;
  }

  repairTornTail();
  if (legacyLogNeedsRotation()) {
    Storage.remove(OLD_LOG_PATH);
    if (!Storage.rename(LOG_PATH, OLD_LOG_PATH)) {
      LOG_ERR("BATLOG", "v1 log rotation failed; battery log disabled");
      return;
    }
    LOG_INF("BATLOG", "Rotated v1 log to %s", OLD_LOG_PATH);
  }
  ready = true;
  appendSample("boot", false, false);
  lastSampleMs = millis();
  if (ready) LOG_INF("BATLOG", "Logging to %s", LOG_PATH);
}

void BatteryLog::tick(const bool readerActive, const bool wifiActive) {
  if (!ready) return;
  const unsigned long now = millis();
  if (lastSampleMs != 0 && now - lastSampleMs < SAMPLE_INTERVAL_MS) return;
  appendSample("periodic", readerActive, wifiActive);
  lastSampleMs = now;
}

void BatteryLog::logEvent(const char* event, const bool readerActive, const bool wifiActive) {
  if (!ready) return;
  appendSample(event, readerActive, wifiActive);
  lastSampleMs = millis();
}

void BatteryLog::logSleep(const bool readerActive, const bool wifiActive) {
  logEvent("sleep", readerActive, wifiActive);
}

bool BatteryLog::appendSample(const char* event, const bool readerActive, const bool wifiActive) {
  const BatteryMonitor::Status status = powerManager.getBatteryStatus();
  const int mv = status.millivoltsKnown ? static_cast<int>(status.millivolts) : -1;
  const int pct = status.percentageKnown ? static_cast<int>(status.percentage) : -1;
  const int chg = status.chargingKnown ? (status.charging ? 1 : 0) : -1;
  const int usb = status.externalPowerKnown ? (status.externalPower ? 1 : 0) : -1;

  char line[192];
  const int length = snprintf(line, sizeof(line), "%lld,%lu,%s,%d,%d,%d,%d,%d,%d,%ld,%ld,%d,%lu\n",
                              static_cast<long long>(trustedtime::trustedNow()),
                              static_cast<unsigned long>(millis() / 1000), event, mv, pct, chg, usb,
                              readerActive ? 1 : 0, wifiActive ? 1 : 0, static_cast<long>(status.pm1VinMv),
                              static_cast<long>(status.pm1VinOutMv), static_cast<int>(status.pm1PowerSource),
                              static_cast<unsigned long>(pageTurns));
  if (length <= 0 || length >= static_cast<int>(sizeof(line))) {
    LOG_ERR("BATLOG", "Sample line too long");
    return false;
  }
  return appendLine(line, static_cast<unsigned int>(length));
}

bool BatteryLog::appendLine(const char* line, const unsigned int length) {
  HalFile file = Storage.open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND);
  if (!file || !file.isOpen()) {
    LOG_ERR("BATLOG", "Open failed: %s", LOG_PATH);
    ready = false;
    return false;
  }

  if (!rotationFailed && file.fileSize64() >= MAX_LOG_BYTES) {
    file.close();
    Storage.remove(OLD_LOG_PATH);
    if (!Storage.rename(LOG_PATH, OLD_LOG_PATH)) {
      // Keep appending rather than dropping samples; the cap is a courtesy.
      LOG_ERR("BATLOG", "Rotate failed; continuing in %s", LOG_PATH);
      rotationFailed = true;
    }
    file = Storage.open(LOG_PATH, O_WRONLY | O_CREAT | O_APPEND);
    if (!file || !file.isOpen()) {
      LOG_ERR("BATLOG", "Open after rotate failed");
      ready = false;
      return false;
    }
  }

  if (file.fileSize64() == 0 && !writeHeader(file)) {
    LOG_ERR("BATLOG", "Header write failed");
    ready = false;
    return false;
  }

  if (file.write(reinterpret_cast<const uint8_t*>(line), length) != length) {
    LOG_ERR("BATLOG", "Short append (%u bytes)", length);
    ready = false;
    return false;
  }
  file.flush();
  return true;
}
