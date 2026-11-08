# PaperDIY Reader (CrossPoint port)

EPUB reader firmware for the **M5Stack PaperDIY (K159)**. Built on CrossPoint
Reader and the FreeInk SDK.

> This package is only for the M5Stack PaperDIY. Do not flash it on a PaperS3,
> PaperColor or another board.

## Install

1. Open M5Burner and select **M5Stack PaperDIY**.
2. Use **Erase** first if the device has another firmware or old settings.
3. Select the `PaperDIYReader-<version>.bin` firmware, the USB port and
   **Burn**.
4. Insert a FAT32/exFAT SD card with `.epub` files and power on.

The first book open builds a cache in `/.crosspoint/` and takes a few seconds.
The first `About` visit scans the SD FAT to show used/free space.

## Known limitations

- BLE page-turner pairing is not validated with a real BLE remote yet.
- Sleep current and real battery life are not measured.
- The original 140 mAh cell gives short battery life; a 604050 cell is planned
  but not validated in this build.
- Ghosting after long reading is slight with the default 5-page refresh; the
  1-page setting is available but slower.
- KOReader Sync was validated against a local KOSync server, not the public
  service.

## Source and license

The combined firmware is GPLv3 because it includes wolfSSL. The full license
and third-party notices are in `LICENSE` next to this file. Corresponding
source, patches and the vendored FreeInk SDK are in the repository and its
release tag:

- <https://github.com/dcarnicer/paperdiy-reader>

Do not redistribute this package without `LICENSE` and the source link.
