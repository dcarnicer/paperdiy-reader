#pragma once

#include <Arduino.h>

#include "BoardPaperDiyPins.h"

// The PaperDIY power button is owned by the M5PM1. When this is enabled the
// PM1 single-click reset is disabled and clicks are surfaced to CrossPoint as
// BTN_POWER (the default short action can sleep/shut down). Set to 0 to keep
// the factory single-click reset behaviour (A+B still synthesizes BTN_POWER).
#ifndef PAPERDIY_PM1_APP_POWER_BUTTON
#define PAPERDIY_PM1_APP_POWER_BUTTON 1
#endif

namespace BoardPaperDiy {

// One-time PM1 bring-up: charger + 5 V DCDC, EPD rail GPIO2, CHG_STAT GPIO3 and
// (optionally) the PM1 power-button event mode. Idempotent, retries on failure.
bool ensureBooted();

// Raise/cut the PM1 EPD rail (GPIO2). setEpdPower(true) waits for the rail to
// settle; the panel's own GPIO46 boost is sequenced by Bus_EPD.
bool setEpdPower(bool enabled);

// Called by the LgfxEpdConfig prepare() hook before Bus_EPD powers the panel.
bool prepareEpdPower();

// Cut the PM1 EPD rail after the panel has been put to sleep.
void powerDownEpdPower();

// Read-clear the PM1 power-button event. Rate-limited to one I2C poll every
// 250 ms; returns true once per click.
bool pollPowerButtonClicked(unsigned long nowMs);

// Full system power-off through the M5PM1 (SYS_CMD 0xA1).
void powerOff();

}  // namespace BoardPaperDiy
