#include <BoardPaperDiy.h>
#include <LgfxEpdConfig.h>

namespace {

#define LUT_MAKE(d0, d1, d2, d3, d4, d5, d6, d7, d8, d9, da, db, dc, dd, de, df)                                \
  (uint32_t)((d0 << 0) | (d1 << 2) | (d2 << 4) | (d3 << 6) | (d4 << 8) | (d5 << 10) | (d6 << 12) | (d7 << 14) | \
             (d8 << 16) | (d9 << 18) | (da << 20) | (db << 22) | (dc << 24) | (dd << 26) | (de << 28) | (df << 30))

// Single waveform for BOTH the B/W base push and the AA gray overlay push.
// Panel_EPD's per-pixel diff embeds the epd_mode LUT offset in the stored
// value, so alternating modes between the two pushes of a page turn defeats
// the diff and re-drives the whole screen -- the LovyanGFX default lut_fast
// then flashes every white pixel black for two frames (the full-screen black
// "swipe"). Using one LUT under one mode keeps unchanged pixels skipped.
// Columns 0/15 carry the default lut_fast drive (changed B/W text pixels);
// columns 1-6 / 9-14 carry the AA nudge for the gray levels AA produces.
//
// The paperdiy panel is the same ED047TC1 used by the LilyGo T5 S3, so this
// reuses the waveform validated there. It is a trial: the PMIC/VCOM path is
// different on PaperDIY, so verify contrast and ghosting on hardware.
constexpr uint32_t kFastLut[] = {
    LUT_MAKE(2, 1, 1, 1, 1, 1, 1, 3, 3, 2, 2, 2, 2, 2, 2, 1),
    LUT_MAKE(2, 3, 1, 1, 1, 1, 3, 3, 3, 3, 2, 2, 2, 2, 3, 1),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    LUT_MAKE(1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2),
    ~0u,
    0u,
};

#undef LUT_MAKE

}  // namespace

namespace freeink {

// The PaperDIY panel bus is pin-for-pin the PaperS3 bus (M5GFX uses the same
// Bus_EPD config for board_M5PaperDIY and board_M5PaperS3). The only extra
// hardware is the M5PM1 EPD rail, raised in prepare() before Bus_EPD init.
const LgfxEpdConfig& paperdiyLgfxConfig() {
  static const LgfxEpdConfig cfg = {
      {PAPERDIY_EP_D0, PAPERDIY_EP_D1, PAPERDIY_EP_D2, PAPERDIY_EP_D3, PAPERDIY_EP_D4, PAPERDIY_EP_D5, PAPERDIY_EP_D6,
       PAPERDIY_EP_D7},
      PAPERDIY_EP_SPH,
      PAPERDIY_EP_SPV,
      PAPERDIY_EP_OE,
      PAPERDIY_EP_LE,
      PAPERDIY_EP_CL,
      PAPERDIY_EP_CKV,
      PAPERDIY_EP_PWR,
      16000000,                                             // busHz — M5GFX's bus_speed for this board
      8,                                                    // linePadding — M5GFX's line_padding for this board
      0,                                                    // rotation: native-landscape 960x540 framebuffer
      {&BoardPaperDiy::prepareEpdPower, nullptr, nullptr},  // stock Bus_EPD power sequence
      // Stock quality/text banks; fast and fastest share the ED047TC1 AA
      // waveform above so the base and gray pushes of a page turn stay on the
      // same LUT offset.
      nullptr,
      0,
      nullptr,
      0,
      kFastLut,
      sizeof(kFastLut) / sizeof(kFastLut[0]),
      kFastLut,
      sizeof(kFastLut) / sizeof(kFastLut[0]),
  };
  return cfg;
}

}  // namespace freeink
