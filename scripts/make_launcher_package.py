#!/usr/bin/env python3
"""Build an M5Launcher (bmorcelli/Launcher) app package for the PaperDIY.

Launcher installs app-only ESP32 images, not the combined factory image used
by M5Burner. This script copies `.pio/build/paperdiy/firmware.bin` to a
clearly named asset and writes install notes next to it.

Usage:
    python3 scripts/make_launcher_package.py --version 2.1.0
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BUILD = PROJECT_DIR / ".pio" / "build" / "paperdiy"
DEFAULT_OUTPUT = PROJECT_DIR / "dist" / "launcher"
FIRMWARE_SLUG = "PaperDIYReader"
ESP_IMAGE_MAGIC = 0xE9
ESP32S3_CHIP_ID = 0x0009
IMAGE_HEADER_SIZE = 24


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_version(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._+-]+", "-", value.strip()).strip("-")
    return cleaned or "2.1.0"


def validate_app_image(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:IMAGE_HEADER_SIZE]
    if len(data) < IMAGE_HEADER_SIZE:
        raise SystemExit(f"{path} is too small to be an ESP app image")
    if data[0] != ESP_IMAGE_MAGIC:
        raise SystemExit(
            f"{path} does not start with the ESP image magic (0xE9); "
            "pass the app-only firmware.bin, not a merged factory image"
        )
    chip_id = int.from_bytes(data[12:14], "little")
    return chip_id, path.stat().st_size


def write_readme(output_dir: Path, version: str, repository: str, digest: str) -> Path:
    readme = output_dir / "README.md"
    readme.write_text(
        f"""# PaperDIY Reader {version} for M5Launcher

App-only firmware for the **M5Stack PaperDIY** (ESP32-S3, 16 MB flash).
This is not a full factory image and must not be flashed at `0x0`.

## Install

1. Copy `{FIRMWARE_SLUG}-launcher.bin` (the stable alias) to a FAT32/exFAT SD
   card.
2. Insert the card and open M5Launcher.
3. Go to **SD**, select the file and choose **Install**.
4. Launch the app from the Launcher menu.

Launcher may also install it from the WebUI or from a direct URL saved in
Favorites. For Favorites, use the stable release URL:

`https://github.com/{repository}/releases/latest/download/{FIRMWARE_SLUG}-launcher.bin`

Use the same stable file name for every update. Launcher names the app after
the file, so installing a versioned file such as
`{FIRMWARE_SLUG}-{version}-launcher.bin` creates a second app instead of
replacing the existing one. Keep the versioned file only as an archive.

## Wake straight into the reader (recommended)

The PaperDIY sleeps by asking the M5PM1 to power down, so every wake is a
power-on, and Launcher shows its screen on every power-on by default. In
Launcher, set **CFG > GPIO on boot starts Launcher** to **A** (GPIO Level 0).
Launcher then appears only when A is held at boot; every other boot goes
straight to the reader. To open Launcher, hold A and press power.

## Return to M5Launcher

Open **Settings > General > Exit to M5Launcher**:

- With a key configured, hold that key when asked; the reader restarts while
  it is held and Launcher opens. Any other button cancels.
- Without a key, confirm. The reader restarts through a 1 ms deep sleep (or an
  M5PM1 reset when `DeepSleep starts Launcher` is off) and Launcher's boot
  screen appears; long-press A to enter its menu before the last app
  auto-boots.

## Updates

When the reader runs under M5Launcher, in-app OTA and SD firmware updates are
disabled: Launcher owns the OTA slots, and writing to the "next" slot could
overwrite another installed app. Update by installing a newer app-only `.bin`
from Launcher. Books, settings and caches live on the SD card and are kept.

## Source and license

- Source: https://github.com/{repository}
- SHA256: `{digest}`

The combined firmware is GPLv3 because it includes wolfSSL. See the repository
for the full license and third-party notices.
""",
        encoding="utf-8",
    )
    return readme


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2.1.0")
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repository", default="dcarnicer/paperdiy-reader")
    args = parser.parse_args()

    firmware = args.build_dir / "firmware.bin"
    if not firmware.is_file():
        raise SystemExit(f"missing {firmware}; run `make build ENV=paperdiy` first")

    chip_id, size = validate_app_image(firmware)
    if chip_id != ESP32S3_CHIP_ID:
        raise SystemExit(f"{firmware} targets chip id 0x{chip_id:04X}, expected ESP32-S3 (0x{ESP32S3_CHIP_ID:04X})")

    version = safe_version(args.version)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{FIRMWARE_SLUG}-{version}-launcher.bin"
    shutil.copy2(firmware, output)

    # Launcher names the app after the file. The stable alias keeps its name
    # across releases, so installing a newer version replaces the same app
    # instead of creating a second partition. The versioned file is an archive.
    stable = args.output_dir / f"{FIRMWARE_SLUG}-launcher.bin"
    shutil.copy2(output, stable)

    digest = sha256(output)
    readme = write_readme(args.output_dir, version, args.repository, digest)

    print(f"launcher image: {output}")
    print(f"stable alias:   {stable}")
    print(f"install notes:  {readme}")
    print(f"source image:   {firmware} ({size} bytes, chip id 0x{chip_id:04X})")
    print(f"sha256:         {digest}")
    print("Next: test installing the stable alias from M5Launcher on a PaperDIY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
