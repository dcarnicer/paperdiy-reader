#include "LauncherEnv.h"

#include <Arduino.h>
#include <BoardConfig.h>
#include <Logging.h>
#include <esp_partition.h>
#include <esp_sleep.h>
#include <nvs.h>

#if FREEINK_DEVICE_PAPERDIY || FREEINK_DEVICE_PAPERMONO
#include <M5Pm1.h>
#endif

namespace launcher_env {
namespace {

constexpr const char* TAG = "LAUNCHER";

const esp_partition_t* residentPartition() {
  return esp_partition_find_first(ESP_PARTITION_TYPE_APP, ESP_PARTITION_SUBTYPE_APP_TEST, nullptr);
}

BootConfig readBootConfig() {
  // Same namespace, keys and types as Launcher's settings.cpp (bool = u8,
  // int = i32) and its keyboot bootloader. A missing key keeps the default.
  BootConfig cfg;
  nvs_handle_t handle;
  if (nvs_open("launcher", NVS_READONLY, &handle) != ESP_OK) return cfg;
  uint8_t u8 = 0;
  if (nvs_get_u8(handle, "DDLB", &u8) == ESP_OK) cfg.ddlb = u8 != 0;
  int32_t i32 = -1;
  if (nvs_get_i32(handle, "LauncherOnKey", &i32) == ESP_OK) cfg.keyGpio = i32;
  if (nvs_get_u8(handle, "LauncherKeyLvl", &u8) == ESP_OK) cfg.keyLevel = u8 != 0;
  nvs_close(handle);
  return cfg;
}

[[noreturn]] void deepSleepRestart() {
  // RESET_REASON_CORE_DEEP_SLEEP: the bootloader starts Launcher unless DDLB.
  LOG_INF(TAG, "Restarting into M5Launcher via deep-sleep wake");
  logSerial.flush();
  esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_ALL);
  esp_sleep_enable_timer_wakeup(1000);
  esp_deep_sleep_start();
  // esp_deep_sleep_start() does not return; satisfy [[noreturn]] regardless.
  ESP.restart();
  while (true) {
  }
}

bool pmicPowerOnReset() {
#if FREEINK_DEVICE_PAPERDIY || FREEINK_DEVICE_PAPERMONO
  if (!BoardConfig::isPaperDiy() && !BoardConfig::isPaperMono()) return false;
  // SYS_CMD: KEY 0xA in the high nibble, 2 = reset. The PM1 resets the ESP32
  // through CHIP_EN, which the bootloader sees as RESET_REASON_CHIP_POWER_ON.
  constexpr uint8_t SYS_CMD_RESET = 0xA2;
  LOG_INF(TAG, "Restarting into M5Launcher via M5PM1 reset");
  logSerial.flush();
  freeink::m5pm1::beginBus();
  // Same settle time the PMIC reference driver uses before a system command.
  delay(120);
  if (!freeink::m5pm1::writeReg(freeink::m5pm1::REG_SYS_CMD, SYS_CMD_RESET)) {
    LOG_ERR(TAG, "M5PM1 reset command was not acknowledged");
    return false;
  }
  delay(2000);
  LOG_ERR(TAG, "M5PM1 reset did not restart the device");
#endif
  return false;
}

}  // namespace

bool isUnderLauncher() {
  // The partition table is fixed for the lifetime of this boot; Launcher only
  // rewrites it from its own firmware and then reboots.
  static const bool detected = residentPartition() != nullptr;
  return detected;
}

const BootConfig& bootConfig() {
  // Launcher cannot change these while this app runs.
  static const BootConfig cfg = readBootConfig();
  return cfg;
}

void logStatus() {
  if (!isUnderLauncher()) return;
  const BootConfig& cfg = bootConfig();
  LOG_INF(TAG, "M5Launcher detected: DDLB=%d LauncherOnKey=%d LauncherKeyLvl=%d", cfg.ddlb ? 1 : 0,
          static_cast<int>(cfg.keyGpio), cfg.keyLevel ? 1 : 0);
}

bool exitToLauncher() {
  if (!isUnderLauncher()) {
    LOG_INF(TAG, "Not running under M5Launcher; refusing to leave the app");
    return false;
  }
  const BootConfig& cfg = bootConfig();
  if (cfg.hasKey()) {
    LOG_INF(TAG, "LauncherOnKey=%d: Launcher starts only with that key held", static_cast<int>(cfg.keyGpio));
    return false;
  }
  // A plain ESP.restart() (RTC_SW_CPU_RST) never starts Launcher. The
  // deep-sleep wake was validated on hardware and needs no PMIC; use the
  // PMIC power-on reset only when DDLB makes a deep-sleep wake skip Launcher.
  if (!cfg.ddlb) deepSleepRestart();
  return pmicPowerOnReset();
}

void restartWithKeyHeld() {
  LOG_INF(TAG, "Restarting with LauncherOnKey held");
  logSerial.flush();
  ESP.restart();
  while (true) {
  }
}

}  // namespace launcher_env
