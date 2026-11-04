# 07 — User guide (PaperDIY)

**Languages:** [Español](07-user-guide.md) · **English** · [简体中文](07-user-guide.zh-CN.md) · [日本語](07-user-guide.ja.md)

This guide assumes you have already flashed the firmware. If not, see the
[README](../../README.en.md) and `06-porting.md`.

## First boot

1. Copy `.epub` books to the SD card (FAT32 or exFAT). Folders are allowed.
2. Insert the SD card.
3. Turn it on with a short press of the power button.
4. The first screen is the library/home. Use A/B to move; long B confirms; long
   A goes back.

The first time a book is opened, a cache is generated in `/.crosspoint/` (it
takes a few seconds). Later opens are much faster.

## Controls

| Gesture | Action |
|---|---|
| A short | up / previous page |
| B short | down / next page |
| A long | back / exit |
| B long | confirm / select |
| A+B | power (menu/sleep) |
| Power click | power on; while running, the configured action (default sleep/power off) |
| Power double-click | power off (hardware, if the PM1 keeps it enabled) |
| Power ~10 s | download mode (red LED; screen may freeze) |

The power click no longer performs the factory reset: the PM1 delivers it to
the firmware. If you prefer the original behavior, build with
`-DPAPERDIY_PM1_APP_POWER_BUTTON=0` and use A+B to sleep.

In the reader, A/B turn pages. In lists, they move the selection; long B opens
the item; long A goes back.

Short clicks are registered **on release**, not on press: that is what makes
it possible to tell a click from a long press with only two buttons. If it were
changed to "page on press", a long press could trigger a page/movement before
opening the menu; it is a UX trade-off still to be decided.

## Library

- The home screen shows recent books/covers; the file browser lets you enter
  folders.
- Long B on a book opens the menu (open, details, delete, etc.).
- Metadata and covers are cached in `/.crosspoint/`; if something looks wrong,
  delete that folder and it will be regenerated.

## Reading

- Long B opens the reader menu: TOC, bookmarks, highlights, dictionary, go to
  %, text settings, orientation, etc.
- Long A goes back to the previous menu.
- The reading position is saved automatically.
- Highlights/clippings are saved to the SD card (see the reader menu).

## Comics

- The firmware does not open `.cbz`/`.cbr` directly; convert them to EPUB
  first.
- Recommended: `scripts/comic_to_epub.py`, which creates one XHTML page per
  image (A/B page turns work). It accepts CBZ/ZIP or PDF:

  ```sh
  python3 scripts/comic_to_epub.py tome.cbz tome.epub
  python3 scripts/comic_to_epub.py tome.pdf tome.epub --title "Volume 1" --author "Author"
  ```

  PDF input needs `pdftoppm` (`brew install poppler` on macOS).
- Calibre also works: add the CBZ and convert it to EPUB; it produces one page
  per image.
- Copy the EPUBs to `/Comics/` on the SD card. On first open the reader indexes
  the book: it can take tens of seconds, and buttons are ignored until it
  finishes.
- The EPUB must have one XHTML page per image. PDF-reflow EPUBs with a single
  HTML file (or optimized by the Calibre plugin) can collapse to `1/1` and stop
  paginating.
- The menu may show `Ch.: 1/1 page` because every page is its own document;
  check `Page N` and `Book: %` for real progress.

## Fonts

- Copy `.ttf`, `.otf` or `.ttc` files to `/fonts/` or `/.fonts/` on the SD card.
- You can group a family in a subfolder.
- In reading settings, select the font; regular/bold/italic styles are matched
  by family.
- For IPA (dictionary) you need a font that covers those glyphs.

## Dictionaries

- Copy each StarDict dictionary to `/dictionaries/<name>/` (or
  `/.dictionaries/`), with an uncompressed `.idx` and `.dict`/`.dict.dz`.
- In **Settings → Reader → Dictionary**, select the dictionary.
- The first lookup builds the index (creates `.qidx`/`.sidx`); after that it is
  fast.
- For Spanish, look for a Wiktionary/RAE/WikDict StarDict and try it.

## Wi-Fi, Calibre, OPDS and web UI

- **Settings → Network**: scan/join a Wi-Fi network (2.4 GHz).
- **Web UI**: the address appears on screen; from a browser you can upload
  books, view files, change settings and update.
- **Calibre**: use "Connect to wireless device" in Calibre; the reader shows
  the flow.
- **OPDS**: add catalogs (Project Gutenberg, Standard Ebooks, etc.) and browse
  them from the reader.
- **KOReader Sync**: configure credentials and sync progress.
- **OTA**: check for updates from Settings; you can also flash over USB.

## Power and sleep

- The reader sleeps by itself after an inactivity timeout.
- To sleep manually: hold A+B or press power (depending on the configured
  action).
- On battery, when sleeping it asks the PM1 to **power off**: the device turns
  off and a click turns it back on (the page remains on the panel).
- With USB connected, the PM1 may also cut power; in that case only the power
  button turns it back on. The **deep sleep** fallback with A/B wake only
  happens if USB keeps the board alive.
- If you will not use the device for a long time, power it off with a double
  click.
- The battery is 140 mAh: battery life depends on sleeping. Reading with Wi-Fi
  on drains it much faster.

## SD: recommended layout

```
/
├── Books/                 # your EPUB files (folders allowed)
├── Comics/                # comics converted to EPUB
├── fonts/                 # TTF/OTF
├── dictionaries/          # one StarDict folder per dictionary
└── .crosspoint/           # reader cache (do not touch unless resetting)
```

## Common problems

| Symptom | What to try |
|---|---|
| Blank screen | PM1 GPIO2/GPIO46? DCDC? Full flash? |
| Inverted image | change `rotation` in `paperdiyLgfxConfig` (0 ↔ 2) |
| Ghosting when turning pages | try `Refresh Frequency` at 5, then 1 in Settings > Display; the new fast LUT is under validation |
| SD does not mount | FAT32/exFAT, contact, try another card; if there is no card at boot, insert it and the device restarts |
| Page does not turn | battery? A/B? is it in sleep mode? |
| Does not wake | is the button OK? `ext1` GPIO3/4? |
| Strange battery reading | check `About > Battery` (VBAT/status) or the `[PWR] Battery:` log; recalibrate if the cell is changed |
| Wi-Fi does not connect | 2.4 GHz, password, isolated AP; try a hotspot |
| Book does not open | valid EPUB, size, RAM; delete the book cache |
| Strange UI after update | delete `/.crosspoint/` and reboot |

## Recovery

If something fails:

1. Hold power for ~10 s until the red LED comes on → download mode.
2. Flash `firmware.factory.bin` at `0x0`.
3. If it does not enter download mode, try another cable/USB port; the native
   ESP32-S3 does not need an adapter.

Always keep a backup of the original firmware before experimenting.
