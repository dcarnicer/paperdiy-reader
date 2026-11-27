# CrossPoint for PaperDIY (community port)

EPUB reader firmware for the **M5Stack PaperDIY (K159)**. Built on CrossPoint
Reader and the FreeInk SDK. Community port; not an official M5Stack firmware.

Library and file browser, SD and downloadable fonts, StarDict dictionary,
clippings, OPDS, Calibre wireless, KOReader Sync and CrossPoint Sync
(bookmarks, reading sessions, Sync On Sleep), web UI, USB drive mode,
two-button controls and kit/extended battery profiles. A MagSafe-ready 3D
case (STL) is in the repository.

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

## Updates

- **Standalone:** *Check for Updates* in the reader, or copy the release's
  `-ota.bin` to the SD root and use *SD Card Firmware Update*.
- **Under M5Launcher:** *Check for Updates* only tells you a new version is
  out. Install it from `M5Launcher > OTA` and delete the old copy.

## Known limitations

- BLE page-turner pairing is not validated with a real BLE remote yet.
- Sleep current is not measured. Battery life was measured only with the
  extended 604050 cell (1500 mAh; 45.4 h / 5,448 pages in a drain test); the
  original 140 mAh kit cell gives short battery life. Both curves still need
  validation in normal reading.
- If you install a larger cell, select **Extended (1500 mAh)** under
  **Settings > System > Battery profile**; it changes only the percentage
  curve, not charging.
- Ghosting after long reading is slight with the default 5-page refresh; the
  1-page setting is available but slower.
- KOReader Sync was validated against a local KOSync server, not the public
  service. Sync On Sleep is not yet tested against a real server.

## Source and license

The combined firmware is GPLv3 because it includes wolfSSL. The full license
and third-party notices are in `LICENSE` next to this file. Corresponding
source, patches and the vendored FreeInk SDK are in the repository and its
release tag:

- <https://github.com/dcarnicer/paperdiy-reader>

Do not redistribute this package without `LICENSE` and the source link.
