#include <BoardPaperDiy.h>
#include <M5Pm1.h>

namespace {

// PM1 GPIO2 is the PaperDIY EPD rail enable, in addition to the panel's own
// GPIO46 pin. M5GFX's autodetect does the same four GPIO register writes; the
// PM1's PWR_CFG auto-clears on reset, so the charge/DCDC policy must be
// re-applied on every boot.
bool raisePm1EpdRail() {
  using namespace freeink::m5pm1;

  beginBus();
  // PaperDIY needs the charger and the 5 V DCDC (panel boost) on. Unlike
  // PaperColor it has no Grove/5VINOUT boost and no RGB rail, so keep BOOST_EN,
  // LDO_EN and LED_R_EN off. PWR_CFG auto-clears on reset: re-apply each boot.
  updateReg(REG_PWR_CFG, BOOST_EN | LDO_EN | LED_R_EN, CHG_EN | DCDC_EN);
  writeReg(REG_NEO_CFG, 0x00);

  bool ok = updateReg(REG_GPIO_FUNC0, 0x03 << 4, 0);  // GPIO2 = plain GPIO
  ok = updateReg(REG_GPIO_MODE, 0, GPIO2) && ok;      // output
  ok = updateReg(REG_GPIO_DRV, GPIO2, 0) && ok;       // push-pull
  ok = updateReg(REG_GPIO_OUT, 0, GPIO2) && ok;       // high

  // PM1 GPIO3 is CHG_STAT (active-low, needs a pull-up); BatteryMonitor reads it.
  ok = updateReg(REG_GPIO_FUNC0, 0x03 << 6, 0) && ok;          // GPIO3 = plain GPIO
  ok = updateReg(REG_GPIO_MODE, GPIO3, 0) && ok;               // input
  ok = updateReg(REG_GPIO_PULL0, 0x03 << 6, 0x01 << 6) && ok;  // pull-up

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
