#include <BoardPaperDiy.h>

#include <M5Pm1.h>

namespace {

// PM1 GPIO2 is the PaperDIY EPD rail enable, in addition to the panel's own
// GPIO46 pin. M5GFX's autodetect does the same four register writes; the
// PM1's PWR_CFG auto-clears on reset, so the DCDC/charge/boost policy must be
// re-applied on every boot.
bool raisePm1EpdRail() {
  using namespace freeink::m5pm1;

  beginBus();
  applyBootPowerPolicy();

  bool ok = updateReg(REG_GPIO_FUNC0, 0x03 << 4, 0);  // GPIO2 = plain GPIO
  ok = updateReg(REG_GPIO_MODE, 0, GPIO2) && ok;       // output
  ok = updateReg(REG_GPIO_DRV, GPIO2, 0) && ok;        // push-pull
  ok = updateReg(REG_GPIO_OUT, 0, GPIO2) && ok;        // high
  if (ok) delay(10);
  return ok;
}

}  // namespace

namespace BoardPaperDiy {

bool prepareEpdPower() { return raisePm1EpdRail(); }

void powerDownEpdPower() {
  using namespace freeink::m5pm1;
  beginBus();
  updateReg(REG_GPIO_OUT, GPIO2, 0);
}

void powerOff() {
  freeink::m5pm1::beginBus();
  freeink::m5pm1::requestShutdown();
}

}  // namespace BoardPaperDiy
