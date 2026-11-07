#include "LauncherExitActivity.h"

#include <Arduino.h>
#include <BoardConfig.h>
#include <GfxRenderer.h>
#include <I18n.h>
#include <Logging.h>

#include <cstdio>

#include "MappedInputManager.h"
#include "components/UITheme.h"
#include "fontIds.h"
#include "platform/LauncherEnv.h"

namespace {

// Short of the 650 ms two-button long press, so holding A never becomes Back.
constexpr unsigned long KEY_HOLD_MS = 300;

constexpr MappedInputManager::Button BUTTONS[] = {
    MappedInputManager::Button::Back,     MappedInputManager::Button::Confirm,     MappedInputManager::Button::Left,
    MappedInputManager::Button::Right,    MappedInputManager::Button::Up,          MappedInputManager::Button::Down,
    MappedInputManager::Button::PageBack, MappedInputManager::Button::PageForward,
};

bool isBoardInputPin(const int pin) {
  const auto& in = BoardConfig::ACTIVE.input;
  for (const int8_t p : {in.back, in.confirm, in.left, in.right, in.up, in.down}) {
    if (p >= 0 && p == pin) return true;
  }
  return false;
}

std::string labelForPin(const int pin) {
  // PaperDIY's buttons are printed A (GPIO4) and B (GPIO3), as Launcher calls them.
  if (BoardConfig::isPaperDiy()) {
    if (pin == BoardConfig::ACTIVE.input.up) return "A";
    if (pin == BoardConfig::ACTIVE.input.down) return "B";
  }
  return "GPIO " + std::to_string(pin);
}

}  // namespace

void LauncherExitActivity::onEnter() {
  Activity::onEnter();
  const auto& cfg = launcher_env::bootConfig();
  keyPin = static_cast<int8_t>(cfg.keyGpio);
  keyLevel = cfg.keyLevel;
  canPoll = isBoardInputPin(keyPin);
  keyLabel = labelForPin(keyPin);
  armed = false;
  keyTouched = false;
  keyHeldSince = 0;
  LOG_INF("LAUNCHER", "Waiting for LauncherOnKey GPIO%d==%d (poll=%d)", keyPin, keyLevel ? 1 : 0, canPoll ? 1 : 0);
  requestUpdate();
}

bool LauncherExitActivity::keyHeld() const { return canPoll && digitalRead(keyPin) == (keyLevel ? HIGH : LOW); }

bool LauncherExitActivity::anyButtonPressed() const {
  for (const auto b : BUTTONS) {
    if (mappedInput.isPressed(b)) return true;
  }
  return false;
}

bool LauncherExitActivity::anyButtonReleased() const {
  for (const auto b : BUTTONS) {
    if (mappedInput.wasReleased(b)) return true;
  }
  return false;
}

void LauncherExitActivity::loop() {
  if (!armed) {
    armed = !anyButtonPressed() && !keyHeld();
    return;
  }

  if (keyHeld()) {
    keyTouched = true;
    const unsigned long now = millis();
    if (keyHeldSince == 0) {
      keyHeldSince = now == 0 ? 1 : now;
    } else if (now - keyHeldSince >= KEY_HOLD_MS) {
      // The user is still holding the key: the bootloader sees it and
      // starts Launcher instead of this app.
      launcher_env::restartWithKeyHeld();
    }
    return;
  }
  keyHeldSince = 0;

  if (!anyButtonReleased()) return;
  if (keyTouched) {
    // A tap on the key itself, too short to restart on: not a cancel.
    keyTouched = false;
    return;
  }
  finish();
}

void LauncherExitActivity::render(RenderLock&&) {
  const auto& metrics = UITheme::getInstance().getMetrics();
  const auto pageWidth = renderer.getScreenWidth();
  const auto pageHeight = renderer.getScreenHeight();

  renderer.clearScreen();
  GUI.drawHeader(renderer, Rect{0, metrics.topPadding, pageWidth, metrics.headerHeight}, tr(STR_EXIT_TO_LAUNCHER));

  char title[96];
  snprintf(title, sizeof(title), tr(STR_LAUNCHER_HOLD_KEY), keyLabel.c_str());
  const int width = pageWidth - metrics.contentSidePadding * 2;
  const int titleTop = pageHeight / 3;
  const int titleHeight = renderer.getLineHeight(UI_12_FONT_ID) * 3;
  UITheme::drawCenteredWrappedText(renderer, Rect{metrics.contentSidePadding, titleTop, width, titleHeight},
                                   UI_12_FONT_ID, title, 3, true, EpdFontFamily::BOLD,
                                   UITheme::TextVerticalAlignment::TOP);

  const int hintTop = titleTop + titleHeight + metrics.verticalSpacing;
  UITheme::drawCenteredWrappedText(
      renderer, Rect{metrics.contentSidePadding, hintTop, width, pageHeight - hintTop - metrics.buttonHintsHeight},
      UI_10_FONT_ID, canPoll ? tr(STR_LAUNCHER_HOLD_KEY_HINT) : tr(STR_LAUNCHER_HOLD_KEY_AT_POWER_ON), 4, true,
      EpdFontFamily::REGULAR, UITheme::TextVerticalAlignment::TOP);

  // No button hints: the Back slot is A's long press, which may be the very
  // key the user must hold. The hint text says how to cancel.
  renderer.displayBuffer();
}
