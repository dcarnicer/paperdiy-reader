#!/usr/bin/env python3
"""Check the two PaperDIY release images before they are published.

- The full image (flashed at 0x0) must carry a partition table at 0x8000 and
  the same app the OTA image contains, at 0x10000.
- The OTA image must be an app-only ESP32-S3 image (starts with 0xE9).

Usage:
    python3 scripts/check_release_assets.py crosspoint-paperdiy-latest.bin crosspoint-paperdiy-2.0.0-1-ota.bin
"""
from __future__ import annotations

import argparse
from pathlib import Path

ESP_IMAGE_MAGIC = 0xE9
ESP32S3_CHIP_ID = 0x0009
PARTITION_TABLE_OFFSET = 0x8000
PARTITION_MAGIC = b"\xaa\x50"
APP_OFFSET = 0x10000


def check_app_header(data: bytes, what: str) -> None:
    if len(data) < 24 or data[0] != ESP_IMAGE_MAGIC:
        raise SystemExit(f"{what}: not an ESP app image (no 0xE9 magic)")
    chip_id = int.from_bytes(data[12:14], "little")
    if chip_id != ESP32S3_CHIP_ID:
        raise SystemExit(f"{what}: chip id 0x{chip_id:04X}, expected ESP32-S3 (0x{ESP32S3_CHIP_ID:04X})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("full", type=Path, help="full image flashed at 0x0")
    parser.add_argument("ota", type=Path, help="app-only OTA image")
    args = parser.parse_args()

    full = args.full.read_bytes()
    ota = args.ota.read_bytes()

    check_app_header(ota, str(args.ota))
    if full[:1] != bytes([ESP_IMAGE_MAGIC]):
        raise SystemExit(f"{args.full}: no bootloader at 0x0")
    if full[PARTITION_TABLE_OFFSET : PARTITION_TABLE_OFFSET + 2] != PARTITION_MAGIC:
        raise SystemExit(f"{args.full}: no partition table at 0x{PARTITION_TABLE_OFFSET:X}")
    check_app_header(full[APP_OFFSET:], f"{args.full} at 0x{APP_OFFSET:X}")
    if full[APP_OFFSET : APP_OFFSET + len(ota)] != ota:
        raise SystemExit(f"{args.full}: app at 0x{APP_OFFSET:X} differs from {args.ota}")

    print(f"release assets OK: {args.full.name} ({len(full)} bytes), {args.ota.name} ({len(ota)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
