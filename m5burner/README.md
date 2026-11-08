# M5Burner package

This directory holds the M5Burner metadata template and the publishing
checklist. Generated packages go to `dist/m5burner/` (ignored by git).

## Build the package

```bash
make build ENV=paperdiy
python3 scripts/make_m5burner_package.py   # version from platformio.ini
```

The script produces:

```
dist/m5burner/
├── crosspoint-paperdiy-latest.bin    # for the desktop Publish dialog
├── paperdiy-reader-<version>.zip      # for the repo/PR route
└── paperdiy-reader-<version>/
    ├── m5burner.json
    ├── LICENSE
    ├── README.md
    ├── cover.png
    └── firmware/
        └── PaperDIYReader_0x0.bin
```

`crosspoint-paperdiy-latest.bin` and `firmware/PaperDIYReader_0x0.bin` are the combined
`firmware.factory.bin` (bootloader + partition table + app). Use the `.bin` in
the M5Burner desktop **Publish** dialog; use the `.zip` only for the
`M5Stack-Firmware` repository/PR route. Do not use the `paperdiy-test` build:
it exposes serial key injection.

## Test before publishing

1. Build and package from a clean `paperdiy` build.
2. On a clean PaperDIY, erase flash and burn the package with M5Burner.
3. Check boot, Home, A/B, SD, EPUB page turn, About SD/battery and Wi-Fi.
4. Verify the package starts with an empty NVS: no Wi-Fi credentials or
   KOReader credentials from the development device.

## Publish

Use your own M5Stack account. There are two supported routes:

1. **M5Burner desktop app**: `USER CUSTOM` → `Publish`, fill name, version,
   description, device type, GitHub URL, the `.bin` firmware and cover.
2. **M5Stack-Firmware PR**: fork `m5stack/M5Stack-Firmware`, add this
   repository to `firmware-repo.list`, and include `m5burner.json` plus the
   `firmware/` folder in this repository. M5Stack reviews the first submission.

For this package the expected device type is `M5Stack PaperDIY`. Confirm the
exact string shown by the current M5Burner device list before publishing; if it
differs, update `firmware_category.device` in `m5burner.json`.

## Legal checklist

- [ ] Release tag exists for the exact firmware binary.
- [ ] `LICENSE` was generated from the installed dependencies and is included.
- [ ] Source archive includes the vendored `freeink-sdk` and `patches/`.
- [ ] No `paperdiy-test` or debug binary is uploaded.
- [ ] No M5Stack logo or “official firmware” claim is used.
- [ ] The LPPL hyphenation question in `licenses/README.md` is accepted or
      resolved before a public release.
- [ ] M5Stack terms and review requirements are accepted.

## Notes

- `m5burner.json` here is a template; the packaging script replaces
  `version` and normalizes `repository`.
- M5Burner uses the same version as the GitHub release, without the `v`:
  `2.0.0-1`, `2.0.0-2`… (CrossPoint version + port revision, kept short
  because M5Burner limits the field; see
  `.agents/rules/release-versioning.md`). The reader's update
  notice compares this field and picks the highest one, so type it exactly
  and never leave an old-scheme version such as `2.1.0` in the entry. Do not
  upload RCs.
- The cover is `m5burner/cover.png` (1280×720) and is used by default by
  `scripts/make_m5burner_package.py`. Pass `--cover` to use another image.
- Keep `README.md` and `LICENSE` inside the uploaded package.
- The same full image serves M5Launcher: LauncherHub mirrors M5Burner and
  Launcher copies only the app at `0x10000`. Prefer uploading the GitHub
  release asset `crosspoint-paperdiy-latest.bin`, so M5Burner gets the exact
  binary of the tagged release. See `docs/paperdiy/13-m5launcher.md`.
