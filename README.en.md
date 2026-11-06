# PaperDIY Reader

**Languages:** [Español](README.md) · **English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

Feature-rich reading firmware for the **M5Stack PaperDIY** (ESP32-S3 + 4.7"
ED047TC1 E Ink panel, 960×540, 16 grays), built on
[CrossPoint Reader 2.0](https://github.com/crosspoint-reader/crosspoint-reader)
(MIT). The goal is not a POC: it is an e-reader with a library, settings, fonts,
a dictionary, sync, OPDS/Calibre and everything else that makes the device
usable every day.

> **Status:** the firmware **builds, boots and reads EPUB on a real PaperDIY**.
> Validation (2026-11-04): boot, screen/UI, Home, wake, A/B buttons, battery,
> SD and navigation OK after syncing to CrossPoint `5d731041`.
> EPUB reading, Wi-Fi, web UI and book transfer were validated on 2026-10-28.
> Calibre wireless and OTA were validated on 2026-11-04. OPDS (Project
> Gutenberg) was validated on 2026-11-05. Auto-sleep and the cover sleep
> screen were validated on 2026-11-05. Long reading: 250+ page turns without
> errors or leaks on 2026-11-06. KOReader Sync was validated against a local
> KOSync server on 2026-11-06. Pending: pairing a BLE remote, sleep
> current/battery life, the 604050 battery and a physical visual review of
> ghosting. See
> [`docs/paperdiy/06-porting.md`](docs/paperdiy/06-porting.md).
>
> **Downstream fork:** `main` mirrors `upstream/develop`; `paperdiy` is our
> working branch. The `freeink-sdk` SDK is vendored so the repo can be cloned
> and built without submodules. See
> [`docs/paperdiy/10-fork-maintenance.md`](docs/paperdiy/10-fork-maintenance.md).

## Why this repo

The `melastmohican/m5paperdiy-arduino-examples` example repo proves that the
panel and buttons work, but its `EpubReader` is a port of atomic14's reader:
no persistence, no library, no settings, no Wi-Fi, no deep sleep and a full
refresh on every page. CrossPoint already solves the EPUB engine, layout,
fonts, SD cache, library, dictionary, OPDS, Calibre, KOReader Sync, web UI and
OTA. What was missing was the PaperDIY board layer.

This repo adds that layer:

- `M5PAPER_DIY` profile inside `freeink-sdk` (display, buttons, battery,
  power, wake);
- `BoardPaperDiy` with the ED047TC1 parallel bus and the **M5PM1** EPD rail;
- `paperdiyLgfxConfig` reusing the PaperS3 bus (same pins);
- battery/charge status through the M5PM1;
- PM1 power button as `BTN_POWER`, shutdown on battery and deep-sleep fallback
  over USB, waking with A/B;
- framebuffer in PSRAM (`FREEINK_FB_PSRAM`);
- configurable OTA (`CROSSPOINT_OTA_RELEASES_URL`) so it does not download
  official firmware;
- PlatformIO environment `paperdiy`.

## Hardware

| | PaperDIY |
|---|---|
| SoC | ESP32-S3-WROOM-1-N16R8, 240 MHz |
| Flash / PSRAM | 16 MB / 8 MB Octal |
| Display | ED047TC1 4.7" 960×540, 16 grays, 8-bit parallel bus |
| Input | 2 user buttons (GPIO4 = A, GPIO3 = B), power button managed by the PM1 |
| Power | M5PM1; 140 mAh battery; USB-C |
| SD | microSD over SPI (SCLK39 / MISO40 / MOSI38 / CS47) |
| Connectivity | 2.4 GHz Wi-Fi + BLE 5 |
| Missing | touch, frontlight, RTC, IMU, audio |

The panel bus is **pin-for-pin identical to the M5Paper S3**: D0–D7 =
6,14,7,12,9,11,8,10; CL=16, LE=15, SPH=13, SPV=17, CKV=18, OE=45, PWR=46. The
difference is that the PaperDIY also needs the M5PM1 EPD rail (GPIO2 over
I²C on SDA41/SCL42).

### 3D case

The M5Stack **PaperDIY Complete Kit** includes a PLA-printed case. In
[`hardware/3d/PaperDIY_kit_completo.3mf`](hardware/3d/PaperDIY_kit_completo.3mf)
we keep a modified version of the official model for anyone who wants to print
or adapt it. It includes the back shell, front frame and buttons, and opens as
a Bambu Studio project (the geometry can also be reused in another slicer).

The original model, the M5Stack MIT license and the M2 screw warning are in
[`hardware/README.en.md`](hardware/README.en.md).

## Controls (2 buttons)

CrossPoint uses `InputStyle::DigitalTwoButton`, designed for exactly two
buttons:

| Gesture | Action |
|---|---|
| **A** (GPIO4) short | up / previous page / move selection up |
| **B** (GPIO3) short | down / next page / move selection down |
| **A** long | back / exit |
| **B** long | confirm / select |
| **A + B** | power button (power menu / sleep) |
| Power short | configured action; defaults to sleep/power off (the PM1 delivers the click to the firmware) |
| Power double-click | hardware power off (if the PM1 keeps it enabled) |
| Power ~10 s | download mode (red LED; screen may freeze) |
| Power from off | power on |

Power behavior differs from the factory firmware: with
`PAPERDIY_PM1_APP_POWER_BUTTON=1` (default), the PM1 single-click reset is
disabled so the click reaches CrossPoint. If you prefer the factory reset,
build with `-DPAPERDIY_PM1_APP_POWER_BUTTON=0`; then use A+B to sleep.

Navigation is the main hardware limitation. The plan includes button remapping,
contextual shortcuts and **BLE page turner** (already compiled) so pages can
be turned with a remote or a phone.

## What's included (inherited from CrossPoint 2.0)

- **EPUB 2/3 engine**: CSS, images, hyphenation, kerning, tables, footnotes,
  chapter navigation, CJK ruby, RTL, focus mode, orientation.
- **Library**: title/author index, covers, recent books, search, file browser,
  SD cache.
- **Reading**: saved position, bookmarks, highlights/clippings, go to %, auto
  page turn, themes, night mode, typefaces and sizes.
- **StarDict dictionary** and word lookup.
- **Sync**: KOReader Sync, Calibre wireless, OPDS (with search and paging),
  WebDAV, web UI for uploading books, OTA.
- **Formats**: `.epub`, `.xtc/.xtch`, `.txt`, `.bmp`.
- **Fonts**: built-in + TTF/OTF on SD.
- **International**: 35 UI languages (Spanish included).
- **PaperDIY**: BLE HID host (page turner) and USB Mass Storage enabled in the
  `paperdiy` environment.

## Build

Requirements: PlatformIO Core and an internet connection the first time (the
isolated core downloads the platform, framework and toolchain; ~5 GB).

```bash
make build
# equivalent to:
PLATFORMIO_CORE_DIR="$PWD/.platformio-core" pio run -e paperdiy
```

The binary is written to:

```
.pio/build/paperdiy/firmware.bin          # app (offset 0x10000)
.pio/build/paperdiy/firmware.factory.bin  # full image (offset 0x0)
```

If your global `~/.platformio` is healthy, `pio run -e paperdiy` also works.
The `Makefile` uses an isolated core so the build is reproducible even with old
packages. `.platformio-core/` and `.pio/` are local caches (git-ignored); you
can delete them and `make build` will recreate them.

## Flash

1. Connect the PaperDIY over USB-C.
2. Hold the power button for ~10 s until the red LED blinks (download mode).
3. First install (full image, includes bootloader and partition table):

```bash
make flash-factory PORT=/dev/cu.usbmodemXXXX
```

To update the app only (keeps bootloader/partitions):

```bash
make flash PORT=/dev/cu.usbmodemXXXX
```

Or, for full control:

```bash
# app update (keeps bootloader/partitions)
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x10000 .pio/build/paperdiy/firmware.bin

# first install / recovery (full image)
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  write_flash 0x0 .pio/build/paperdiy/firmware.factory.bin
```

Before flashing for the first time, back up the original firmware:

```bash
esptool --chip esp32s3 --port /dev/cu.usbmodemXXXX \
  read_flash 0 0x1000000 paperdiy-original.bin
```

## Structure

```
.
├── src/                  # CrossPoint app (activities, reader, UI, network)
├── lib/                  # Epub, GfxRenderer, EpdFont, HAL, etc.
├── freeink-sdk/          # hardware SDK + board profiles
│   └── libs/hardware/
│       ├── BoardConfig/  # M5PAPER_DIY + M5Pm1
│       └── BoardPaperDiy/# ED047TC1 bus, PM1 rail, power-off
├── docs/paperdiy/        # research, hardware, roadmap, port
├── docs/upstream/        # original CrossPoint README/user guide
├── hardware/3d/          # 3D case (complete-kit remix)
├── platformio.ini        # `paperdiy` environment
└── Makefile
```

## Documentation

The detailed documentation is in Spanish. The
[documentation index](docs/paperdiy/README.en.md),
[user guide](docs/paperdiy/07-user-guide.en.md), and the
[hardware](docs/paperdiy/01-hardware.en.md) and
[port notes](docs/paperdiy/06-porting.en.md) are also available in English.

- [Research and current state](docs/paperdiy/00-research.md)
- [Hardware and pins](docs/paperdiy/01-hardware.md)
- [POC and ecosystem analysis](docs/paperdiy/02-current-state.md)
- [Feature matrix](docs/paperdiy/03-feature-matrix.md)
- [Architecture](docs/paperdiy/04-architecture.md)
- [Roadmap](docs/paperdiy/05-roadmap.md)
- [Port notes and validation](docs/paperdiy/06-porting.md)
- [PaperDIY user guide](docs/paperdiy/07-user-guide.md)
- [Sources](docs/paperdiy/08-sources.md)
- [Prior art: issue #4005 and PaperDIY PRs](docs/paperdiy/09-prior-art.md)
- [Maintaining the fork and updating upstream](docs/paperdiy/10-fork-maintenance.md)
- [Draft comment for issue #4005](docs/paperdiy/11-upstream-note.md)
- [USB testing (Spanish)](docs/paperdiy/12-serial-testing.md)

## Known limitations

- Still to measure: LUTs/ghosting after many pages, sleep current and battery
  life.
- No touch, frontlight, RTC, IMU or audio. The UI must work with 2 buttons.
- 140 mAh battery: when sleeping, the firmware asks the PM1 to power off. If
  the PM1 cuts power (the usual case, including over USB), only the power
  button turns it back on. Verified on 2026-11-05: A+B over USB powered off
  via the PM1 and A did not wake it. If USB keeps the board alive, the
  fallback is deep sleep with A/B wake. Battery life still needs measuring.
- The physical power button is managed by the M5PM1; the firmware receives it
  as an I²C event, not as a GPIO.
- OTA points to the official repo by default, but there is no `-paperdiy`
  asset, so it never installs foreign firmware. For your own OTA, configure
  `CROSSPOINT_OTA_RELEASES_URL`.
- CrossPoint 2.0 is the development branch (2.0.0), not the stable 1.6.x.

## Credits and license

MIT. The engine and most of the code are from
[CrossPoint Reader](https://github.com/crosspoint-reader/crosspoint-reader)
(Copyright 2025 CrossPoint Reader organization); the hardware SDK is
[FreeInk](https://github.com/crosspoint-reader/crosspoint-reader) (MIT); the
panel is driven by M5GFX/LovyanGFX. The 3D case is a remix of
[M5Stack](https://github.com/m5stack/M5_Hardware)'s MIT model. See
[LICENSE](LICENSE) and [NOTICE](NOTICE).

> This is a translation of the Spanish README. If they differ, the Spanish
> version is authoritative. Detailed documentation is currently Spanish-only.
