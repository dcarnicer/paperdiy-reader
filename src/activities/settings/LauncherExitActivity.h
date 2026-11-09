#pragma once

#include <cstdint>
#include <string>

#include "activities/Activity.h"

// Exit to M5Launcher when Launcher is set to start only with a key held
// (CFG > GPIO on boot starts Launcher). Launcher's bootloader samples that key
// on every reset, so this screen waits until the user holds it and then
// restarts while it is still down. Any other button cancels.
class LauncherExitActivity final : public Activity {
  int8_t keyPin = -1;
  bool keyLevel = false;
  // False when the key is not one of this board's input pins; the screen then
  // only explains how to hold it at power-on.
  bool canPoll = false;
  std::string keyLabel;
  // Buttons still down from the Settings press must be released first, so
  // their release is not taken as a cancel.
  bool armed = false;
  // Set while the key is seen down, so its own short-press event does not
  // count as a cancel.
  bool keyTouched = false;
  unsigned long keyHeldSince = 0;

  bool keyHeld() const;
  bool anyButtonPressed() const;
  bool anyButtonReleased() const;

 public:
  explicit LauncherExitActivity(GfxRenderer& renderer, MappedInputManager& mappedInput)
      : Activity("LauncherExit", renderer, mappedInput) {}
  void onEnter() override;
  void loop() override;
  void render(RenderLock&&) override;
};
