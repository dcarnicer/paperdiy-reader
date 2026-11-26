#include <BoardPaperDiy.h>
#include <InputManager.h>

#include <cassert>
#include <cstdio>

namespace {

void tick(InputManager& input, unsigned long now, unsigned sides, bool click = false) {
  fakeNow = now;
  gpioLevels[BoardConfig::ACTIVE.input.up] = sides & 1 ? LOW : HIGH;
  gpioLevels[BoardConfig::ACTIVE.input.down] = sides & 2 ? LOW : HIGH;
  BoardPaperDiy::powerButtonClicked = click;
  input.update();
}

}  // namespace

int main() {
  // A PMIC pulse is a click, not a hold, even if the next poll is late.
  for (unsigned sides : {0u, 1u, 2u, 3u}) {
    InputManager input;
    tick(input, 1000, sides);
    tick(input, 1100, sides, true);
    assert(input.wasPressed(InputManager::BTN_POWER));
    assert(input.isPressed(InputManager::BTN_POWER));
    assert(input.getPowerButtonHeldTime() == 0);
    fakeNow = 1600;
    assert(input.getPowerButtonHeldTime() == 0);
    tick(input, 1600, sides);
    assert(input.wasReleased(InputManager::BTN_POWER));
    assert(!input.isPressed(InputManager::BTN_POWER));
    assert(input.getPowerButtonHeldTime() == 0);
    tick(input, 1601, sides);
    assert(!input.wasReleased(InputManager::BTN_POWER));
    assert(input.getPowerButtonHeldTime() == 0);
  }

  // A click during a side-button hold keeps the side action and stays a click.
  for (unsigned sides : {1u, 2u}) {
    InputManager input;
    tick(input, 2000, sides);
    tick(input, 2100, sides, true);
    assert(input.wasPressed(InputManager::BTN_POWER));
    assert(input.getPowerButtonHeldTime() == 0);
    const auto sideAction = sides == 1 ? InputManager::BTN_BACK : InputManager::BTN_CONFIRM;
    tick(input, 2700, sides);
    assert(input.wasReleased(InputManager::BTN_POWER));
    assert(input.getPowerButtonHeldTime() == 0);
    assert(input.isPressed(sideAction));
  }

  // A PMIC click during an active chord does not duplicate Power or reset the
  // chord's hold duration.
  InputManager input;
  tick(input, 3000, 3);
  tick(input, 3650, 3);
  assert(input.wasPressed(InputManager::BTN_POWER));
  assert(input.isPressed(InputManager::BTN_POWER));
  assert(input.getPowerButtonHeldTime() == 650);
  tick(input, 3800, 3, true);
  assert(!input.wasPressed(InputManager::BTN_POWER));
  assert(input.getPowerButtonHeldTime() == 800);
  tick(input, 4000, 0);
  assert(input.wasReleased(InputManager::BTN_POWER));
  assert(input.getPowerButtonHeldTime() == 1000);

  // A click before the chord matures must not create a second Power press.
  {
    InputManager early;
    tick(early, 6000, 3);
    tick(early, 6100, 3, true);
    assert(early.wasPressed(InputManager::BTN_POWER));
    assert(early.getPowerButtonHeldTime() == 0);
    tick(early, 6650, 3);
    assert(!early.wasPressed(InputManager::BTN_POWER));
    assert(early.isPressed(InputManager::BTN_POWER));
    assert(early.getPowerButtonHeldTime() == 650);
    tick(early, 7000, 0);
    assert(early.wasReleased(InputManager::BTN_POWER));
    assert(early.getPowerButtonHeldTime() == 1000);
  }

  // A click on the physical transition into the chord keeps the chord's hold.
  {
    InputManager transition;
    tick(transition, 8000, 3, true);
    assert(transition.wasPressed(InputManager::BTN_POWER));
    assert(transition.getPowerButtonHeldTime() == 0);
    tick(transition, 8650, 3);
    assert(!transition.wasPressed(InputManager::BTN_POWER));
    assert(transition.getPowerButtonHeldTime() == 650);
    tick(transition, 9000, 0);
    assert(transition.wasReleased(InputManager::BTN_POWER));
    assert(transition.getPowerButtonHeldTime() == 1000);
  }

  // A fresh click after the chord must not inherit the chord's hold time.
  tick(input, 4100, 0, true);
  assert(input.wasPressed(InputManager::BTN_POWER));
  assert(input.getPowerButtonHeldTime() == 0);
  tick(input, 5000, 0);
  assert(input.wasReleased(InputManager::BTN_POWER));
  assert(input.getPowerButtonHeldTime() == 0);

  std::puts("PaperDIY PMIC click duration and two-button Power chords passed");
}
