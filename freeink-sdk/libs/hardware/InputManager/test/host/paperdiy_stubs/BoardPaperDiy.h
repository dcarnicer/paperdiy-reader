#pragma once

#ifndef PAPERDIY_PM1_APP_POWER_BUTTON
#define PAPERDIY_PM1_APP_POWER_BUTTON 1
#endif

namespace BoardPaperDiy {

inline bool powerButtonClicked = false;

inline bool ensureBooted() { return true; }

inline bool pollPowerButtonClicked(unsigned long) {
  const bool clicked = powerButtonClicked;
  powerButtonClicked = false;
  return clicked;
}

}  // namespace BoardPaperDiy
