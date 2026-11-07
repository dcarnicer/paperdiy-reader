# 13 — M5Launcher

**Languages:** [Español](13-m5launcher.md) · **English**

[bmorcelli/Launcher](https://github.com/bmorcelli/Launcher) — commonly called
**M5Launcher** — is a resident firmware that installs and boots other
applications from dynamic OTA partitions. Version 3.0.0 includes the
**M5Stack PaperDIY** port, so the reader can coexist with other firmware on the
same device.

## Recommended setup

By default, Launcher shows its screen on **every power-on**, and on the
PaperDIY that includes waking from sleep: the reader sleeps by asking the PM1
to power down, so waking is a cold boot. To wake straight into the reader, set
this in Launcher:

**`CFG > GPIO on boot starts Launcher` = `A`** (with `GPIO Level` = `0`).

Launcher then only appears when **A** is held at boot. Every other boot
(power-on, wake, restart) goes straight to the reader. To open Launcher, hold A
and press power, or use `Exit to M5Launcher` from the reader.

## How Launcher decides what to boot

Launcher 3.0.0's bootloader reads its settings from the `launcher` NVS
namespace on every reset:

| Launcher setting | Power-on (PM1) | Deep-sleep wake | Software restart |
|---|---|---|---|
| Default | Launcher | Launcher | Reader |
| `DeepSleep starts Launcher` off | Launcher | Reader | Reader |
| `GPIO on boot starts Launcher` = A | Reader (Launcher with A held) | Reader (same) | Reader (same) |

`DeepSleep starts Launcher` does not affect the PaperDIY's normal sleep, which
is a PM1 power-off rather than deep sleep. It only changes the deep-sleep
fallback used when the PM1 does not cut power.

## What changes in the reader

The binary is the same one used for a normal installation: there is no
separate Launcher build. At runtime the reader detects that it is running under
M5Launcher, logs its settings at boot
(`M5Launcher detected: DDLB=… LauncherOnKey=… LauncherKeyLvl=…`) and adapts
four things:

1. **Exit to M5Launcher.** Appears under `Settings > General` and works in all
   three modes:
   - **Key configured:** shows "Hold A to open M5Launcher". Once A has been
     held for 0.3 s, the reader restarts with A still down; the bootloader sees
     it and starts Launcher. Keep holding until its menu appears. Any other
     button cancels.
   - **No key, `DeepSleep starts Launcher` on:** confirm, then a 1 ms deep
     sleep; the `DEEPSLEEP` reset opens Launcher.
   - **No key, `DeepSleep starts Launcher` off:** confirm, then the PM1 resets
     the ESP32, which the bootloader sees as a power-on.

   In the last two cases Launcher's boot screen appears: long-press **A** to
   enter its menu before the last app auto-boots.
2. **Launcher-managed updates.** `Check for Updates` and `SD Card Firmware
   Update` are hidden. Under Launcher the app runs from a dynamically chosen
   OTA partition; writing the "next" partition could overwrite another
   installed app and corrupt Launcher's registry. Update by installing a new
   `.bin` from Launcher instead.
3. **Defense in depth.** Even if an update path is reached another way,
   `OtaUpdater` and `FirmwareFlasher` refuse to write OTA partitions while
   Launcher is present.
4. **No recovery mode at boot.** Under Launcher, holding A at power-on is how
   Launcher is opened, so the reader never enters its SD firmware picker when
   it boots with A held.

Settings, library, caches, books and reading progress stay on the SD card
(`/.crosspoint/`), so they survive reinstalling the app or erasing the flash.
Launcher additionally keeps its own settings in `/config.conf` at the SD card
root, so the A key and `DDLB` also survive. What is lost when the flash is
erased is the reader's Wi-Fi credentials (`nvs.net80211`); they must be entered
again.

## Install

Requirements:

- M5Launcher **3.0.0 or newer** with PaperDIY support.
- An **app-only** `.bin` (`firmware.bin`), not the M5Burner combined image or
  `firmware.factory.bin`.

### From the SD card

1. Copy `PaperDIYReader-<version>-launcher.bin` to a FAT32/exFAT SD card.
2. Insert the card and open M5Launcher.
3. Open **SD**, select the file and choose **Install**.
4. Launch the reader from the Launcher menu.

### From the WebUI or Favorites

You can also upload the `.bin` through **WUI > OTA Update**, or save the direct
release-asset URL in **Favorites**. For Favorites use the stable URL:

```
https://github.com/dcarnicer/paperdiy-reader/releases/latest/download/PaperDIYReader-launcher.bin
```

The file must be the app binary; Launcher recognizes it by the ESP image header
(`0xE9`).

## Build and package

```bash
make build ENV=paperdiy
python3 scripts/make_launcher_package.py --version 0.1.0
```

The script produces:

```
dist/launcher/
├── PaperDIYReader-0.1.0-launcher.bin
└── README.md
```

`make launcher LAUNCHER_VERSION=0.1.0` does the same. The release workflow also
publishes `PaperDIYReader-<tag>-launcher.bin` and the stable
`PaperDIYReader-launcher.bin` alias next to the factory image.

## Update

1. Download the new `PaperDIYReader-<version>-launcher.bin`.
2. Install it from Launcher (SD, WUI or Favorites) over the existing app.
3. Launcher replaces the app partition contents; SD data is untouched.

Do not use `make flash` or `esptool ... write_flash 0x10000` while Launcher is
installed: that writes to Launcher's resident partition. To return to a
standalone install, flash `firmware.factory.bin` at `0x0`, and erase the flash
first if you want to remove the dynamic partitions.

## Technical notes

- Launcher marks its resident partition with the `test` subtype (`0x20`) at
  `0x10000`. The reader looks for that subtype with `esp_partition_find_first()`;
  it is the signal that enables the integration and never appears in the
  reader's normal `partitions.csv`.
- The bootloader logic lives in
  `patches/esp-idf/components/bootloader/subproject/main/bootloader_start.c`
  on the `launcher_keyboot` branch of
  [bmorcelli/myLibBuilder](https://github.com/bmorcelli/myLibBuilder). It reads
  `DDLB` (u8), `LauncherOnKey` (i32) and `LauncherKeyLvl` (u8); the reader reads
  the same keys, once per boot.
- With a key configured, the bootloader ignores the reset reason and only looks
  at the key. Neither deep sleep nor the PM1 reset open Launcher in that mode,
  which is why the exit restarts with the key held.
- The PM1 reset is `SYS_CMD` = `0xA2` (`KEY` 0xA, command 2). It resets the
  ESP32 through `CHIP_EN`, and the bootloader sees a power-on.
- The app is about 5.2 MB. Launcher creates an OTA partition sized to fit it in
  the free flash space; the reader's `spiffs` partition from `partitions.csv`
  is not used.
- Exiting does not erase `otadata`: the app stays selected for Launcher's
  auto-boot.

## Validation status

Validated on 2026-11-07 on a PaperDIY with M5Launcher 3.0.0:

- [x] The `paperdiy` environment builds with the changes.
- [x] The packager validates the ESP header, ESP32-S3 chip id and asset name.
- [x] Installation from M5Launcher (serial console, `flash firmware`).
- [x] The app boots under Launcher, shows `Exit to M5Launcher` and hides the
  in-app update rows.
- [x] Update from Launcher (`flash overwrite`) with the SD card and reading
  position preserved.
- [x] Exit with `DeepSleep starts Launcher` on (1 ms deep sleep).
- [x] Exit with `DeepSleep starts Launcher` off (PM1 reset): opens Launcher's
  boot screen.
- [x] With `GPIO on boot starts Launcher` = A: sleeping and powering on boots
  the reader directly (twice); exiting while holding A opens Launcher's menu;
  B cancels the exit.
- [x] Clean install from scratch: 16 MB erase, official M5Launcher 3.0.0 at
  `0x0`, and the `v0.1.0-paperdiy` release installed from the SD card. The
  `paperd` partition matches the release asset byte for byte
  (`sha256 efe8b795…`).
- [x] The clean install preserves the SD library, settings and reading progress,
  plus Launcher's `/config.conf`. Only the NVS Wi-Fi credentials are lost.
- [x] After the clean install: `Exit to M5Launcher` is visible, in-app updates
  are hidden, A exits and B cancels, and waking from sleep boots the reader
  directly.
- [ ] Installation from WUI/Favorites: it uses the same Launcher installer but
  was not tested separately on this unit.
