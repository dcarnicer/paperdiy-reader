#pragma once

#include <cstdint>

// Append-only battery drain log on the SD card.
//
// The device has no current sense, so a long-term log of voltage, percentage
// and charge/USB state is what lets us calibrate the voltage curve and measure
// real runtime. Sampling is driven by the main loop; this module never arms a
// timer or wakes the MCU. One line per boot, sleep, USB transition and every
// few minutes while awake.
class BatteryLog {
 public:
  // Opens/repairs the log and writes the boot sample. Safe to call when the SD
  // card is unavailable: logging stays disabled for this boot.
  void begin();

  // Writes a periodic sample when the interval has elapsed.
  void tick(bool readerActive, bool wifiActive);

  // Forces a sample for a named state change (sleep, USB plug/unplug).
  void logEvent(const char* event, bool readerActive, bool wifiActive);

  // Convenience wrapper used by the sleep path.
  void logSleep(bool readerActive, bool wifiActive);

  // Counts a successful page turn for the periodic samples (the drain-test
  // mode uses this; ordinary reading does not call it).
  void notePageTurn() { ++pageTurns; }

 private:
  bool appendSample(const char* event, bool readerActive, bool wifiActive);
  bool appendLine(const char* line, unsigned int length);

  unsigned long lastSampleMs = 0;
  uint32_t pageTurns = 0;
  bool ready = false;
  bool rotationFailed = false;
};
