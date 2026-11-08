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
2. **Launcher-managed updates.** `Check for Updates` only notifies: it queries
   LauncherHub and, when a newer version exists, offers `Exit to M5Launcher`
   so it can be installed from `OTA`. `SD Card Firmware Update` is hidden.
   Under Launcher the app runs from a dynamically chosen OTA partition;
   writing the "next" partition could overwrite another installed app and
   corrupt Launcher's registry.
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

## OTA and updates

| Installation | In-app OTA | How to update |
|---|---|---|
| Standalone | Yes, `crosspoint-<tag>-paperdiy.bin` via `Check for Updates` | OTA or SD |
| Under M5Launcher | Notice only: `Check for Updates` queries LauncherHub | `M5Launcher > OTA` (catalog) or `PaperDIYReader-launcher.bin` from SD/WUI |

Under Launcher the app runs from a dynamic OTA partition. Writing the "next"
partition could overwrite another installed app or corrupt Launcher's
registry, so the reader never writes flash: the updater refuses the write even
if reached another way.

The notice looks up the app named
**`CrossPoint for PaperDIY (community port)`** (ignoring case) in
`https://api.launcherhub.net/firmwares?category=paper-diy` (LauncherHub mirrors
M5Burner, where it is published under that name) and takes the highest version
from `?fid=<fid>`. Until the app is in the catalog the reader reports no update.
If it is renamed on M5Burner, change `launcherHubAppName` in
`src/network/OtaUpdater.cpp`.

Not yet validated on hardware: Launcher's installer (catalog or SD) picks a
free label (`paper1` when `paperd` exists) and, when there is room, may create
a second app instead of replacing the existing one
(`installFirmwareDynamic` → `launcherInstallNextAppLabel`). If that happens,
delete the old version from its app menu in Launcher.

## Install

Requirements:

- M5Launcher **3.0.0 or newer** with PaperDIY support.
- An **app-only** `.bin` (`firmware.bin`), not the M5Burner combined image or
  `firmware.factory.bin`.

### From the SD card

1. Copy `PaperDIYReader-launcher.bin` (the release's stable alias) to a
   FAT32/exFAT SD card.
2. Insert the card and open M5Launcher.
3. Open **SD**, select the file and choose **Install**.
4. Launch the reader from the Launcher menu.

Use the same file name (`PaperDIYReader-launcher.bin`) for installs and
updates. Launcher names the app after the file: installing
`PaperDIYReader-<version>-launcher.bin` creates a new app instead of replacing
the existing one. The versioned file is only an archive. Even with the same
name, it is not yet verified that an SD or catalog install replaces `paperd`:
see [OTA and updates](#ota-and-updates).

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
python3 scripts/make_launcher_package.py --version 2.1.0
```

The script produces:

```
dist/launcher/
├── PaperDIYReader-2.1.0-launcher.bin
└── README.md
```

`make launcher LAUNCHER_VERSION=2.1.0` does the same. The release workflow also
publishes `PaperDIYReader-<tag>-launcher.bin` and the stable
`PaperDIYReader-launcher.bin` alias next to the factory image.

## Update

1. Download the new `PaperDIYReader-launcher.bin` (the stable alias).
2. Install it from Launcher (SD, WUI or Favorites) over the existing app.
3. SD data is untouched. Serial `flash overwrite` reuses the `paperd`
   partition; from SD, WUI or the catalog, Launcher may create a second app
   (`paper1`) when there is free space (not yet verified). If it shows up
   twice, delete the old version from Launcher.

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

Validated on 2026-11-07 on a PaperDIY with M5Launcher 3.0.0, before
`Check for Updates` returned under Launcher as a notice (hence the entries
saying in-app updates are hidden):

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
  `0x0`, and the `v0.1.0` release installed from the SD card. The
  `paperd` partition matches the release asset byte for byte
  (`sha256 05f68e10…`).
- [x] The clean install preserves the SD library, settings and reading progress,
  plus Launcher's `/config.conf`. Only the NVS Wi-Fi credentials are lost.
- [x] After the clean install: `Exit to M5Launcher` is visible, in-app updates
  are hidden, A exits and B cancels, and waking from sleep boots the reader
  directly.
- [ ] Installation from WUI/Favorites: it uses the same Launcher installer but
  was not tested separately on this unit.

Update notice, validated on 2026-11-08 with M5Launcher 3.0.0 (reader installed
with `flash firmware` and `flash overwrite`):

- [x] Under Launcher, `System` shows `Check for Updates` and
  `Exit to M5Launcher`, and hides the SD firmware update.
- [x] With a temporary 1.0.0 build looking up the catalog app
  `PaperDIY Reader`: shows current 1.0.0, new 1.0.1, the
  "Install it from M5Launcher > OTA" hint and Cancel / Exit to M5Launcher.
- [x] Exit to M5Launcher from the notice, with key A configured: opens the
  hold-A screen and reaches Launcher's menu.
- [ ] Exit to M5Launcher from the notice with no key configured (deep sleep or
  PM1 reset).
- [ ] Notice against the real app published on M5Burner.
- [ ] Updating from the catalog or SD replaces `paperd` instead of creating
  `paper1`.
