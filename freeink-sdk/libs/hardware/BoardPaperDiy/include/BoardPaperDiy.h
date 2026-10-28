#pragma once

#include <Arduino.h>

#include "BoardPaperDiyPins.h"

namespace BoardPaperDiy {

// Raise the M5PM1's EPD rail (PM1 GPIO2) and apply the PMIC boot power policy.
// Called by the LgfxEpdConfig prepare() hook before Bus_EPD powers the panel.
// Idempotent.
bool prepareEpdPower();

// Cut the PM1 EPD rail (used by the deep-sleep path, after the panel has been
// put to sleep). Wake re-runs prepareEpdPower().
void powerDownEpdPower();

// Full system power-off through the M5PM1 (SYS_CMD 0xA1). The PM1 owns the
// PaperDIY power button, so this is the firmware equivalent of a double-click.
void powerOff();

}  // namespace BoardPaperDiy
