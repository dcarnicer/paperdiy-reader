# PaperDIY Reader (CrossPoint port)

EPUB reader firmware for the **M5Stack PaperDIY (K159)**. Built on CrossPoint
Reader and the FreeInk SDK.

> This package is only for the M5Stack PaperDIY. Do not flash it on a PaperS3,
> PaperColor or another board.

## Install

1. Open M5Burner and select **M5Stack PaperDIY**.
2. Use **Erase** first if the device has another firmware or old settings.
3. Select the `crosspoint-paperdiy-latest.bin` firmware, the USB port and
   **Burn**.
4. Insert a FAT32/exFAT SD card with `.epub` files and power on.

The first book open builds a cache in `/.crosspoint/` and takes a few seconds.
The first `About` visit scans the SD FAT to show used/free space.

## Known limitations

- BLE page-turner pairing is not validated with a real BLE remote yet.
- Sleep current is not measured. Battery life was measured only with the
  extended 604050 cell (45.4 h / 5,448 pages in a drain test); the original
  140 mAh kit cell was not measured in that test. Both curves still need
  validation in normal reading.
- The original 140 mAh cell gives short battery life. If you install a larger
  cell, select **Extended (1500 mAh)** under **Settings > System > Battery
  profile**; it changes only the percentage curve, not charging.
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
