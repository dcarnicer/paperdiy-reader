#include <BoardPaperDiy.h>
#include <LgfxEpdConfig.h>

namespace freeink {

// The PaperDIY panel bus is pin-for-pin the PaperS3 bus (M5GFX uses the same
// Bus_EPD config for board_M5PaperDIY and board_M5PaperS3). The only extra
// hardware is the M5PM1 EPD rail, raised in prepare() before Bus_EPD init.
const LgfxEpdConfig& paperdiyLgfxConfig() {
  static const LgfxEpdConfig cfg = {
      {PAPERDIY_EP_D0, PAPERDIY_EP_D1, PAPERDIY_EP_D2, PAPERDIY_EP_D3, PAPERDIY_EP_D4, PAPERDIY_EP_D5,
       PAPERDIY_EP_D6, PAPERDIY_EP_D7},
      PAPERDIY_EP_SPH,
      PAPERDIY_EP_SPV,
      PAPERDIY_EP_OE,
      PAPERDIY_EP_LE,
      PAPERDIY_EP_CL,
      PAPERDIY_EP_CKV,
      PAPERDIY_EP_PWR,
      16000000,  // busHz — M5GFX's bus_speed for this board
      8,         // linePadding — M5GFX's line_padding for this board
      0,         // rotation: native-landscape 960x540 framebuffer
      {&BoardPaperDiy::prepareEpdPower, nullptr, nullptr},  // stock Bus_EPD power sequence
  };
  return cfg;
}

}  // namespace freeink
