# 01 — Hardware and pins

**Languages:** [Español](01-hardware.md) · **English** · [简体中文](01-hardware.zh-CN.md) · [日本語](01-hardware.ja.md)

## Specs

| | |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8 (dual-core LX7, 240 MHz) |
| Flash | 16 MB |
| PSRAM | 8 MB Octal (OPI) |
| Display | ED047TC1, 4.7", 960×540, 16 gray levels, 234 PPI |
| Display interface | 8-bit parallel, **no IT8951 controller** |
| Buttons | A=GPIO4, B=GPIO3 (active low); power via M5PM1 |
| Battery | 140 mAh, charged by M5PM1 |
| SD | microSD over SPI (SCLK39/MISO40/MOSI38/CS47), CARD_DET GPIO48 active low |
| USB | native ESP32-S3 USB-C (Serial/JTAG) |
| Radio | 2.4 GHz Wi-Fi, BLE 5.0 |
| Missing | touch, frontlight, RTC, IMU, audio, Grove |

## Pin map

### Panel (identical to the M5Paper S3)

| Signal | GPIO | Notes |
|---|---:|---|
| D0 | 6 | data bus |
| D1 | 14 | |
| D2 | 7 | |
| D3 | 12 | |
| D4 | 9 | |
| D5 | 11 | |
| D6 | 8 | |
| D7 | 10 | |
| XCL / CL | 16 | pixel clock |
| XLE / LE | 15 | latch |
| XSTL / SPH | 13 | horizontal start pulse |
| XOE / OE | 45 | output enable |
| CKV | 18 | gate clock |
| SPV | 17 | vertical start pulse |
| PWR | 46 | panel boost enable |
| PM1 GPIO2 | — | additional EPD rail, via I²C |

The port's `LgfxEpdConfig` uses exactly these pins. LovyanGFX's `Panel_EPD`
sequences OE → PWR → SPV; the PM1 rail is raised first, in the `prepare()`
hook.

### SD

| Signal | GPIO |
|---|---:|
| SCLK | 39 |
| MISO | 40 |
| MOSI | 38 |
| CS | 47 |

SPI, SdFat, FAT32/exFAT. Does the SD share the SPI bus with the panel? No: the
panel is parallel; the SD has its own SPI bus. Even so, the SDK uses `SdFat`
over SPI.

### Buttons

| Button | GPIO | Type |
|---|---:|---|
| A | 4 | active low, external pull-up |
| B | 3 | active low, external pull-up |
| Power | — | M5PM1; single click on/reset, double click off, long press download |

`InputStyle::DigitalTwoButton` maps:

- short A → `BTN_UP`
- short B → `BTN_DOWN`
- long A → `BTN_BACK`
- long B → `BTN_CONFIRM`
- A+B → `BTN_POWER`

### M5PM1

| Signal | GPIO |
|---|---:|
| I²C SDA | 41 |
| I²C SCL | 42 |
| Address | 0x6E |
| GPIO2 | EPD rail |
| GPIO3 | CHG_STAT (input, active low) |

The PM1 also manages charging, the power button and shutdown. The firmware uses
it to:

- raise the EPD rail before initializing the panel;
- read VBAT/VIN/VOUT and the charge status;
- power off the device (`SYS_CMD 0xA1`);
- cut the EPD rail before deep sleep.

## Panel refresh

M5GFX exposes four modes:

| Mode | Typical use | Trade-off |
|---|---|---|
| `epd_quality` | cover, images, first paint | slower, more grays/quality |
| `epd_text` | full page of text | clean, may flicker |
| `epd_fast` | small changes, UI | fast, more ghosting |
| `epd_fastest` | animations/feedback | very fast, high ghosting |

CrossPoint uses a 1 bpp framebuffer + gray planes for antialiasing;
`LgfxEpdDriver` maps `Full/Half` to `epd_text` and `Fast/Fastest` to `epd_fast`.
The port keeps `Panel_EPD`'s standard LUTs for `quality` and `text`.
For `fast`/`fastest` it uses the ED047TC1 AA waveform validated on the LilyGo
T5 S3: a single LUT for the B/W base and the gray plane, with a specific push
for the levels produced by antialiasing. It is still pending validation on
PaperDIY because the PMIC/VCOM is different. See
[`06-porting.en.md`](06-porting.en.md#page-turn-ghosting).

## Power

- 140 mAh battery: small. Average consumption matters more than peak.
- Deep sleep: the ESP32-S3 drops to tens of µA, but the PM1 rails, SD and
  panel can add mA. The port cuts the PM1 EPD rail in
  `PowerManager::powerDownRailsForSleep()`; this needs measurement.
- Wake: `ext1` on GPIO3/4 (S3 RTC GPIOs), active low. Either button wakes the
  device.
- Charging: the PM1's `CHG_EN` enables the LGS4056H. The K159 schematic uses
  `R11=2K`, which sets 500 mA; with the original 140 mAh cell that is ~3.6C,
  and with a ~2000 mAh 604050 it is ~0.25C.
- `CHG_STAT` is PM1 GPIO3, active low: it is read to know whether the device is
  actually charging, not just whether USB is present.
- Low-voltage protection: `REG_BATT_LVP` at 3.4 V.
- The physical power button is not an ESP32 GPIO; the firmware cannot read it.
  To sleep from the UI, use A+B.

### Rough budget (to be measured)

| State | Expected current | Runtime with 140 mAh |
|---|---:|---:|
| Active reading (Wi-Fi off) | 40–80 mA | 2–3.5 h |
| Active with Wi-Fi | 100–150 mA | <1.5 h |
| Deep sleep (properly configured) | 20–100 µA | weeks/months |
| Deep sleep with rails not cut | 1–5 mA | days |

The practical conclusion: the reader must sleep after a short timeout and
between sessions; the page button wakes it, paints and goes back to sleep.
CrossPoint already has auto-sleep; the timeout needs tuning and measurement.

## 3D case

The complete-kit model is in
[`hardware/3d/PaperDIY_kit_completo.3mf`](../../hardware/3d/PaperDIY_kit_completo.3mf).
It is a remix of the official STL of the **PaperDIY Complete Kit (K159-B)**
published by M5Stack in
[`M5_Hardware/Products/K159-B_PaperDIY_Complete_Kit/Structures`](https://github.com/m5stack/M5_Hardware/tree/master/Products/K159-B_PaperDIY_Complete_Kit/Structures).
It includes the back shell, front frame and buttons; the project is prepared
for Bambu Studio. MIT license (© 2021 M5Stack for the original; © 2026
PaperDIY Reader contributors for the remix). See
[`hardware/README.en.md`](../../hardware/README.en.md).

## Optional hardware mods

- **Bigger battery**: the kit ships 140 mAh; a 500–1000 mAh cell in the case
  cavity multiplies runtime. Check space, connector and charging (the PM1
  regulates).
- **I²C RTC**: a DS3231/PCF8563 on the internal bus (41/42) would provide real
  time and alarms; support must be added in `BoardConfig`/`Rtc`.
- **Rotary encoder or 5-way**: an extra GPIO + I²C/ADC would allow a
  wheel-style UI; the case must be modified.
- **Hall sensor in the cover**: sleep/wake on close/open; a free GPIO plus a
  magnet.
- **Frontlight**: not trivial; the realistic solution is an external light
  clip. There is no rail or integrated LED.

## Download mode and recovery

- Hold power for ~2 s until the red LED blinks → download mode.
- `esptool --chip esp32s3 --port ... write_flash 0x0 firmware.factory.bin`
  recovers the device even if the app is corrupted.
- Keep a backup of the original firmware before the first install.
