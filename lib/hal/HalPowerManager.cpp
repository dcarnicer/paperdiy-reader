#include "HalPowerManager.h"

#include <BoardConfig.h>
#include <Logging.h>
#include <PowerManager.h>
#include <Preferences.h>
#include <WiFi.h>
#include <esp_sleep.h>
#include <soc/soc_caps.h>

#include <cassert>

#include "HalGPIO.h"

#if FREEINK_DEVICE_EEGO_A4 || FREEINK_DEVICE_PICCO
#include <HalFrontlight.h>
#endif

#if FREEINK_DEVICE_PICCO
#include <driver/gpio.h>
#endif

#if FREEINK_DEVICE_PAPERMONO || FREEINK_DEVICE_PAPERDIY
#include <M5Pm1.h>
#endif
#if FREEINK_DEVICE_PAPERDIY
#include <BoardPaperDiy.h>
#endif

HalPowerManager powerManager;  // Singleton instance

// GPIO13 controls the X4 battery latch and the X3 SD power rail on the C3
// Xteink boards. Other boards use it for unrelated signals, including the
// X4 Pro display chip select.
static constexpr gpio_num_t XTEINK_C3_GPIO13 = GPIO_NUM_13;

namespace {
constexpr unsigned long PAPERDIY_SETTLE_MS = 2 * 60 * 1000;
constexpr const char* BATTERY_PREFS_NAMESPACE = "cpbat";
constexpr const char* BATTERY_PREFS_KEY = "lastpct";

BatteryMonitor& batteryMonitor() {
  static BatteryMonitor battery;
  return battery;
}

// Takes the battery mutex for the whole read. A null handle is allowed while
// boot is still constructing the manager.
class BatteryReadLock {
 public:
  explicit BatteryReadLock(const SemaphoreHandle_t mutex) : mutex_(mutex) {
    if (mutex_) xSemaphoreTake(mutex_, portMAX_DELAY);
  }
  ~BatteryReadLock() {
    if (mutex_) xSemaphoreGive(mutex_);
  }
  BatteryReadLock(const BatteryReadLock&) = delete;
  BatteryReadLock& operator=(const BatteryReadLock&) = delete;

 private:
  SemaphoreHandle_t mutex_;
};
}  // namespace

void HalPowerManager::begin() {
  if (BoardConfig::ACTIVE.batteryAdc >= 0) {
    pinMode(BoardConfig::ACTIVE.batteryAdc, INPUT);
  }
  // Board charger setup (Picco SGM41562: stock charge voltage and limits); a
  // no-op on boards without a configurable charger.
  if (BatteryMonitor::configureCharger()) LOG_INF("PWR", "Charger configured");
#if FREEINK_DEVICE_PAPERDIY
  // PaperDIY's PM1 exposes only voltage, not a coulomb counter. Log the raw
  // rails once at boot so a percentage that looks stuck can be compared with
  // the actual cell voltage and charge source.
  if (BoardConfig::isPaperDiy()) {
    const BatteryMonitor battery;
    const auto status = battery.readStatus();
    uint8_t pwrCfg = 0;
    uint8_t gpioIn = 0;
    freeink::m5pm1::readReg(freeink::m5pm1::REG_PWR_CFG, &pwrCfg);
    freeink::m5pm1::readReg(freeink::m5pm1::REG_GPIO_IN, &gpioIn);
    LOG_INF("PWR", "Battery: VBAT=%dmV VIN=%dmV 5VOUT=%dmV PWR_SRC=%d pct=%d chg=%d ext=%d cfg=%02x gpio=%02x",
            status.millivolts, status.pm1VinMv, status.pm1VinOutMv, status.pm1PowerSource, status.percentage,
            status.charging, status.externalPower, pwrCfg, gpioIn);
  }
#endif
  normalFreq = getCpuFrequencyMhz();
  modeMutex = xSemaphoreCreateMutex();
  assert(modeMutex != nullptr);
  batteryMutex = xSemaphoreCreateMutex();
  assert(batteryMutex != nullptr);
#if FREEINK_DEVICE_PAPERDIY
  if (BoardConfig::isPaperDiy()) {
    Preferences prefs;
    if (prefs.begin(BATTERY_PREFS_NAMESPACE, /*readOnly=*/true)) {
      const uint8_t value = prefs.getUChar(BATTERY_PREFS_KEY, 0xFF);
      prefs.end();
      if (value <= 100) {
        _lastDischargePercent = value;
        _hasLastDischargePercent = true;
      }
    }
  }
#endif
}

void HalPowerManager::setPowerSaving(bool enabled) {
  if (normalFreq <= 0) {
    return;  // invalid state
  }

  auto wifiMode = WiFi.getMode();
  if (wifiMode != WIFI_MODE_NULL) {
    // Wifi is active, force disabling power saving
    enabled = false;
  }

  // Held across the check and the switch: a Lock taken in between would find full speed, do
  // nothing, and then run at LOW_POWER_FREQ until the next key press.
  xSemaphoreTake(modeMutex, portMAX_DELAY);
  const LockMode mode = currentLockMode;

  if (mode == None && enabled && !isLowPower) {
    LOG_DBG("PWR", "Going to low-power mode");
    if (!setCpuFrequencyMhz(LOW_POWER_FREQ)) {
      LOG_DBG("PWR", "Failed to set CPU frequency = %d MHz", LOW_POWER_FREQ);
      xSemaphoreGive(modeMutex);
      return;
    }
    isLowPower = true;

  } else if ((!enabled || mode != None) && isLowPower) {
    LOG_DBG("PWR", "Restoring normal CPU frequency");
    if (!setCpuFrequencyMhz(normalFreq)) {
      LOG_DBG("PWR", "Failed to set CPU frequency = %d MHz", normalFreq);
      xSemaphoreGive(modeMutex);
      return;
    }
    isLowPower = false;
  }

  // Otherwise, no change needed
  xSemaphoreGive(modeMutex);
}

void HalPowerManager::startDeepSleep(HalGPIO& gpio, const bool wakeOnHeldButton) const {
#if FREEINK_DEVICE_EEGO_A4 || FREEINK_DEVICE_PICCO
  // The frontlight driver and touch share I2C; turn the light off before touch
  // releases the bus. On Picco this also puts the TMA525C to sleep.
  Frontlight.setOn(false);
  gpio.prepareForDeepSleep();
#endif
#ifdef ENABLE_SERIAL_LOG
  // Tear down HWCDC so the host sees a clean disconnect and the peripheral
  // doesn't hold power domains that interfere with USB-powered GPIO wake.
  // logSerial is the raw HWCDC reference; Serial is the MySerialImpl proxy
  // (which doesn't expose end()).
  logSerial.end();
#endif

#if !SOC_PM_SUPPORT_EXT1_WAKEUP
  if (gpio.isXteinkDevice()) {
    // GPIO13 gates the battery MOSFET on both Xteink C3 boards; driving it low
    // is the battery power-off (the SDK wake source still handles USB power).
    // Release any surviving pad hold first: hold_en survives deep sleep via
    // the SDK's deepSleep() (esp_sleep_config_gpio_isolate +
    // gpio_deep_sleep_hold_en), and a held pad silently ignores the drive.
    gpio_hold_dis(XTEINK_C3_GPIO13);
    gpio_set_direction(XTEINK_C3_GPIO13, GPIO_MODE_OUTPUT);
    gpio_set_level(XTEINK_C3_GPIO13, 0);
    gpio_hold_en(XTEINK_C3_GPIO13);
  }
#endif

  // Hold every configured power-latch pin HIGH through deep sleep. These are
  // keep-alive enables (the X4 Pro's master peripheral rail on GPIO1, the
  // Sticky's PWR_HOLD/PWR_LOCK): deepSleep() isolates all pads
  // (esp_sleep_config_gpio_isolate), so a latch without an armed hold loses its
  // output driver and floats — on the X4 Pro the latch drops as soon as
  // external power leaves (serial/pogo adapter unplugged), and the next power-
  // button press cold-boots instead of fast-waking. holdPowerRails() asserted
  // the latches at boot but arms no sleep hold; arm it here instead. Skips
  // XTEINK_C3_GPIO13: it IS power.latch0 on the C3 Xteink boards, where the
  // block above drives it LOW on purpose (battery power-off).
  for (const int8_t pin : {BoardConfig::ACTIVE.power.latch0, BoardConfig::ACTIVE.power.latch1}) {
    if (pin < 0 || static_cast<gpio_num_t>(pin) == XTEINK_C3_GPIO13) continue;
    const auto g = static_cast<gpio_num_t>(pin);
    // Release any surviving pad hold first: a held pad silently ignores the
    // drive below (same trap as the GPIO13 block above).
    gpio_hold_dis(g);
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
    gpio_hold_en(g);
  }

  // Cut the gated peripheral rails (touch/SD/EPD on boards like the Sticky) and
  // hold the enables off through deep sleep — otherwise the GT911 and SD card
  // stay powered all through "off" and drain the battery. No-op on boards with
  // no switched rails (X4/X3). Trade-off: no touch-to-wake; wake is the power
  // button. Must run after display.deepSleep() so the panel controller gets its
  // deep-sleep command while its rail is still up (enterDeepSleep() in main.cpp
  // guarantees that ordering).
  freeink::PowerManager::powerDownRailsForSleep();

#if FREEINK_DEVICE_PAPERMONO || FREEINK_DEVICE_PAPERDIY
  // Its power button is behind the M5PM1 PMIC rather than an ESP GPIO, so
  // normal GPIO deep sleep would have no wake source. Ask the PMIC to shut the
  // device down; a button click then restarts it through a cold boot.
  if (freeink::m5pm1::requestShutdown()) {
    delay(1000);  // allow the PMIC firmware time to drop power
  }
#endif
#if FREEINK_DEVICE_METALIO_EINK4
  // Deep sleep leaves the board, 4G modem and audio module powered, so cut
  // power instead; the button cold-boots it. Returns only on USB power.
  freeink::metalio::powerOff();
#endif
#if FREEINK_DEVICE_PAPERDIY
  // If USB keeps the board powered after the PMIC shutdown request, fall back
  // to deep sleep. Either navigation key wakes it (the PM1 power button is not
  // an ESP32 GPIO).
  BoardPaperDiy::powerDownEpdPower();
  const auto& keys = BoardConfig::ACTIVE.input;
  while (digitalRead(keys.up) == LOW || digitalRead(keys.down) == LOW) delay(10);
  freeink::PowerManager::armWakeOnPins((1ULL << keys.up) | (1ULL << keys.down));
  freeink::PowerManager::deepSleep();
#endif

  if (wakeOnHeldButton) {
    freeink::PowerManager::armPowerButtonWakeup();
    freeink::PowerManager::deepSleep();
  }
  // Waits for the power button to be physically released (so holding it doesn't
  // immediately wake the device again), then arms the wake source and sleeps.
  freeink::PowerManager::deepSleepUntilPowerButton();
}

#if FREEINK_DEVICE_PICCO
// ponytail: 30 s poll; the SGM41562 status is I2C-only, so USB unplug and
// charge progress are only seen when the timer fires.
static constexpr uint64_t USB_HOLD_POLL_US = 30ULL * 1000 * 1000;

bool HalPowerManager::holdWhileUsbPowered(HalGPIO& gpio, void (*onStatus)(bool charging, uint16_t percent)) const {
  if (!gpio.isUsbConnected()) return false;
  LOG_DBG("PWR", "USB power present, holding in light sleep");
  const auto powerPin = static_cast<gpio_num_t>(BoardConfig::ACTIVE.input.power);
  // The press that requested sleep may still be down; it must not end the hold.
  while (digitalRead(powerPin) == LOW) delay(10);  // Picco power button is active-low
  const BatteryMonitor battery;
  int lastCharging = -1;
  int lastPercent = -1;
  while (gpio.isUsbConnected()) {
    const bool charging = battery.isCharging();
    const uint16_t percent = getBatteryPercentage();
    if (static_cast<int>(charging) != lastCharging || percent != lastPercent) {
      lastCharging = charging;
      lastPercent = percent;
      onStatus(charging, percent);
    }
    esp_sleep_enable_timer_wakeup(USB_HOLD_POLL_US);
    gpio_wakeup_enable(powerPin, GPIO_INTR_LOW_LEVEL);
    esp_sleep_enable_gpio_wakeup();
    esp_light_sleep_start();
    gpio_wakeup_disable(powerPin);
    // gpio_wakeup_disable() keeps the LOW_LEVEL type, and a later pinMode() would
    // enable it as an interrupt that storms while the button is held.
    gpio_set_intr_type(powerPin, GPIO_INTR_DISABLE);
    esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_ALL);
    if (digitalRead(powerPin) == LOW) return true;
  }
  return false;
}
#endif

BatteryMonitor::Status HalPowerManager::readBatteryStatusLocked() const {
  const unsigned long now = millis();
  if (BoardConfig::isPaperDiy() && _batteryStatusCacheValid && (now - _batteryStatusLastPollMs) < BATTERY_POLL_MS) {
    return _batteryStatusCache;
  }
  BatteryMonitor::Status status = batteryMonitor().readStatus();
  applyPaperDiyBatteryPresentation(status);
  if (BoardConfig::isPaperDiy()) {
    // A transient I2C failure must not be cached as a valid zero-percent
    // sample. Return the last good snapshot and let the next call retry.
    if (!status.millivoltsKnown && !status.externalPowerKnown) {
      return _batteryStatusCacheValid ? _batteryStatusCache : status;
    }
    // Smooth once per fresh PM1 sample; cache hits above skip this block.
    const uint16_t sample = status.percentageKnown ? status.percentage : _batteryCachedPercent / 10;
    if (_batteryPresentationFixed) {
      _batteryCachedPercent = sample * 10;
    } else if (_batteryCachedPercent == 0) {
      _batteryCachedPercent = 10 * sample;
    } else {
      _batteryCachedPercent = (_batteryCachedPercent * 9 + sample * 10) / 10;
    }
    _batteryStatusCache = status;
    _batteryStatusLastPollMs = now;
    _batteryStatusCacheValid = true;
  }
  return status;
}

void HalPowerManager::applyPaperDiyBatteryPresentation(BatteryMonitor::Status& status) const {
#if FREEINK_DEVICE_PAPERDIY
  if (!BoardConfig::isPaperDiy()) return;

  _batteryPresentationFixed = false;
  const unsigned long now = millis();
  const bool externalKnown = status.externalPowerKnown;
  const bool external = externalKnown && status.externalPower;
  bool full = status.chargeCompleteKnown && status.chargeComplete;
#if defined(PAPERDIY_SERIAL_TEST)
  if (_forceNotFullForTest) full = false;
#endif

  if (externalKnown && external) {
    _lastExternalPowerKnown = true;
    _lastExternalPower = true;
    _batterySettling = false;
    if (full) {
      _lastDischargePercent = 100;
      _hasLastDischargePercent = true;
      status.percentage = 100;
      status.percentageKnown = true;
      _batteryPresentationFixed = true;
    } else if (_hasLastDischargePercent) {
      // The charger raises the terminal voltage above the cell's OCV, so a
      // voltage curve would reach 100% early. Keep the last discharge estimate
      // until the charger reports completion.
      status.percentage = _lastDischargePercent;
      status.percentageKnown = true;
      _batteryPresentationFixed = true;
    }
    return;
  }

  if (!externalKnown) return;

  // On battery. After unplugging, the cell relaxes from the charger voltage to
  // its OCV; hold the last estimate for a settling window before trusting the
  // discharge curve again.
  if (_lastExternalPowerKnown && _lastExternalPower) {
    _lastExternalPower = false;
    _batterySettling = true;
    _batterySettleStartMs = now;
  }
  if (_batterySettling) {
    if (now - _batterySettleStartMs < PAPERDIY_SETTLE_MS) {
      if (_hasLastDischargePercent) {
        status.percentage = _lastDischargePercent;
        status.percentageKnown = true;
        _batteryPresentationFixed = true;
      }
      return;
    }
    _batterySettling = false;
  }

  if (status.percentageKnown) {
    _lastDischargePercent = status.percentage;
    _hasLastDischargePercent = true;
  }
#else
  (void)status;
#endif
}

BatteryMonitor::Status HalPowerManager::getBatteryStatus() const {
  const BatteryReadLock lock(batteryMutex);
  return readBatteryStatusLocked();
}

bool HalPowerManager::readBatteryPercentage(uint16_t& percent) const {
  const BatteryReadLock lock(batteryMutex);
  if (BoardConfig::isPaperDiy()) {
    // The PM1 reads high while charging and the PaperDIY presentation holds
    // the discharge estimate; use it instead of the raw voltage curve.
    const BatteryMonitor::Status status = readBatteryStatusLocked();
    if (!status.percentageKnown) return false;
    percent = status.percentage;
    return true;
  }
  return batteryMonitor().readPercentageChecked(percent);
}

void HalPowerManager::setPaperDiyBatteryProfile(const bool extended) const {
#if FREEINK_DEVICE_PAPERDIY
  const BatteryReadLock lock(batteryMutex);
  BatteryMonitor::setPaperDiyBatteryProfile(extended ? BatteryMonitor::PaperDiyBatteryProfile::Extended
                                                     : BatteryMonitor::PaperDiyBatteryProfile::Kit);
  _batteryStatusCacheValid = false;
#else
  (void)extended;
#endif
}

void HalPowerManager::persistBatteryEstimate() const {
#if FREEINK_DEVICE_PAPERDIY
  const BatteryReadLock lock(batteryMutex);
  if (!BoardConfig::isPaperDiy() || !_hasLastDischargePercent) return;
  Preferences prefs;
  if (!prefs.begin(BATTERY_PREFS_NAMESPACE, /*readOnly=*/false)) return;
  prefs.putUChar(BATTERY_PREFS_KEY, static_cast<uint8_t>(_lastDischargePercent));
  prefs.end();
#endif
}

#if defined(PAPERDIY_SERIAL_TEST)
void HalPowerManager::setBatteryHoldForTest(const int percent, const bool forceNotFull) const {
  const BatteryReadLock lock(batteryMutex);
  if (percent >= 0 && percent <= 100) {
    _lastDischargePercent = static_cast<uint16_t>(percent);
    _hasLastDischargePercent = true;
  }
  _forceNotFullForTest = forceNotFull;
  _batteryStatusCacheValid = false;
}
#endif

uint16_t HalPowerManager::getBatteryPercentage() const {
  const BatteryReadLock lock(batteryMutex);
  if (BoardConfig::ACTIVE.batteryGauge.gaugeAddr != 0) {
    const unsigned long now = millis();
    if (_batteryLastPollMs != 0 && (now - _batteryLastPollMs) < BATTERY_POLL_MS) {
      return _batteryCachedPercent;
    }

    _batteryLastPollMs = now;
    uint16_t percent = 0;
    if (!batteryMonitor().readPercentageChecked(percent)) {
      return _batteryCachedPercent;
    }
    _batteryCachedPercent = percent;
    return _batteryCachedPercent;
  }

  const BatteryMonitor::Status status = readBatteryStatusLocked();
  if (BoardConfig::isPaperDiy()) {
    // readBatteryStatusLocked() already smoothed the fresh sample; a cache
    // hit must not feed the same sample into the filter again.
    return static_cast<uint16_t>(_batteryCachedPercent / 10);
  }
  // smooth the battery %.
  const uint16_t sample = status.percentageKnown ? status.percentage : 0;
  if (_batteryPresentationFixed) {
    _batteryCachedPercent = sample * 10;
    return sample;
  }
  if (_batteryCachedPercent == 0) {
    _batteryCachedPercent = 10 * sample;
  } else {
    _batteryCachedPercent = (_batteryCachedPercent * 9 + sample * 10) / 10;
  }
  return _batteryCachedPercent / 10;
}

HalPowerManager::Lock::Lock() {
  xSemaphoreTake(powerManager.modeMutex, portMAX_DELAY);
  // Current limitation: only one lock at a time
  if (powerManager.currentLockMode != None) {
    LOG_ERR("PWR", "Lock already held, ignore");
    valid = false;
  } else {
    powerManager.currentLockMode = NormalSpeed;
    valid = true;
  }
  xSemaphoreGive(powerManager.modeMutex);
  if (valid) {
    // Immediately restore normal CPU frequency if currently in low-power mode
    powerManager.setPowerSaving(false);
  }
}

HalPowerManager::Lock::~Lock() {
  xSemaphoreTake(powerManager.modeMutex, portMAX_DELAY);
  if (valid) {
    powerManager.currentLockMode = None;
  }
  xSemaphoreGive(powerManager.modeMutex);
}
