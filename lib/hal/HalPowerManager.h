#pragma once

#include <Arduino.h>
#include <BatteryMonitor.h>
#include <InputManager.h>
#include <Logging.h>
#include <freertos/semphr.h>

#include <cassert>

#include "HalGPIO.h"

class HalPowerManager;
extern HalPowerManager powerManager;  // Singleton

class HalPowerManager {
  int normalFreq = 0;  // MHz
  bool isLowPower = false;

  mutable int _batteryCachedPercent = 0;         // Last read battery percentage (0-100)
  mutable unsigned long _batteryLastPollMs = 0;  // Timestamp of last battery read in milliseconds
  // The PM1 read is several blocking I2C transfers; the status bar asks for it
  // more than once per frame. Share one snapshot for a poll interval.
  mutable BatteryMonitor::Status _batteryStatusCache{};
  mutable unsigned long _batteryStatusLastPollMs = 0;
  mutable bool _batteryStatusCacheValid = false;
  // PaperDIY has no coulomb counter, so charging voltage cannot estimate SoC.
  // Hold the last discharge estimate while external power is present and wait
  // for the cell to relax after unplugging.
  mutable uint16_t _lastDischargePercent = 0;
  mutable bool _hasLastDischargePercent = false;
  mutable bool _batterySettling = false;
  mutable unsigned long _batterySettleStartMs = 0;
  mutable bool _lastExternalPowerKnown = false;
  mutable bool _lastExternalPower = false;
  mutable bool _batteryPresentationFixed = false;
#if defined(PAPERDIY_SERIAL_TEST)
  mutable bool _forceNotFullForTest = false;
#endif
  // Serializes battery reads: the render task paints the status bar while the
  // main loop samples the same PM1/ADC for the battery log.
  mutable SemaphoreHandle_t batteryMutex = nullptr;

  BatteryMonitor::Status readBatteryStatusLocked() const;
  void applyPaperDiyBatteryPresentation(BatteryMonitor::Status& status) const;

  enum LockMode { None, NormalSpeed };
  LockMode currentLockMode = None;
  SemaphoreHandle_t modeMutex = nullptr;  // Protect access to currentLockMode

 public:
#if BOARD_HAS_PSRAM
  static constexpr int LOW_POWER_FREQ = 80;  // MHz
#else
  static constexpr int LOW_POWER_FREQ = 10;  // MHz
#endif
  static constexpr unsigned long IDLE_POWER_SAVING_MS = 3000;  // ms
  static constexpr unsigned long BATTERY_POLL_MS = 1500;       // ms

  void begin();

  // Control CPU frequency for power saving
  void setPowerSaving(bool enabled);

  // Setup wake up GPIO and enter deep sleep
  // Should be called inside main loop() to handle the currentLockMode
  // wakeOnHeldButton: arm the wake without waiting for the power button's
  // release, so a press that is still down wakes the device straight back up
  // through the normal power-button wake path.
  void startDeepSleep(HalGPIO& gpio, bool wakeOnHeldButton = false) const;

#if FREEINK_DEVICE_PICCO
  // While USB powers the device, light-sleep instead of deep sleep (deep sleep
  // cannot observe the charger), calling onStatus whenever the charging state
  // or percentage changes. Returns true when the power button ended the hold,
  // false when USB went away or was never present.
  bool holdWhileUsbPowered(HalGPIO& gpio, void (*onStatus)(bool charging, uint16_t percent)) const;
#endif

  // Get battery percentage (range 0-100)
  uint16_t getBatteryPercentage() const;

  // Full battery snapshot (voltage, percentage, charger/USB state). Serialized
  // with the percentage path because both touch the same I2C/ADC backend.
  BatteryMonitor::Status getBatteryStatus() const;

  // PaperDIY only: select the original-kit or extended-cell discharge curve.
  // The profile changes the percentage mapping; it does not change charging.
  void setPaperDiyBatteryProfile(bool extended) const;

  // Persist the last discharge estimate for the next boot. PaperDIY powers off
  // on sleep and may boot while charging, where voltage cannot estimate SoC.
  void persistBatteryEstimate() const;

#if defined(PAPERDIY_SERIAL_TEST)
  // Test-only: inject a discharge estimate and optionally make the filter
  // ignore the charger's full signal, so the hold path can be exercised on a
  // full battery. pass -1 to clear the override.
  void setBatteryHoldForTest(int percent, bool forceNotFull) const;
#endif

  // RAII helper class to manage power saving locks
  // Usage: create an instance of Lock in a scope to disable power saving, for example when running a task that needs
  // full performance. When the Lock instance is destroyed (goes out of scope), power saving will be re-enabled.
  class Lock {
    friend class HalPowerManager;
    bool valid = false;

   public:
    explicit Lock();
    ~Lock();

    // Non-copyable and non-movable
    Lock(const Lock&) = delete;
    Lock& operator=(const Lock&) = delete;
    Lock(Lock&&) = delete;
    Lock& operator=(Lock&&) = delete;
  };
};
