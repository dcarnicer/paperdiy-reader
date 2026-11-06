#!/usr/bin/env python3
"""Build an M5Burner package from the production PaperDIY firmware.

The M5Burner format is a directory with m5burner.json and a firmware/ folder
whose files are named <name>_<hex-address>.bin. We ship the combined factory
image at 0x0 so bootloader, partition table and app stay together.

Usage:
    python3 scripts/make_m5burner_package.py --version 2.0.0-paperdiy.1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BUILD = PROJECT_DIR / ".pio" / "build" / "paperdiy"
DEFAULT_OUTPUT = PROJECT_DIR / "dist" / "m5burner"
DEFAULT_COVER = PROJECT_DIR / "docs" / "paperdiy" / "images" / "first-read.png"
TEMPLATE = PROJECT_DIR / "m5burner" / "m5burner.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_license(output: Path, repository: str) -> None:
    subprocess.run(
        [
            sys.executable,
            str(PROJECT_DIR / "scripts" / "build_release_license.py"),
            "--env",
            "paperdiy",
            "--output",
            str(output),
            "--repository",
            repository,
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2.0.0-paperdiy.1")
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cover", type=Path, default=DEFAULT_COVER)
    parser.add_argument("--repository", default="dcarnicer/paperdiy-reader")
    args = parser.parse_args()

    factory = args.build_dir / "firmware.factory.bin"
    if not factory.is_file():
        raise SystemExit(f"missing {factory}; run `make build ENV=paperdiy` first")
    if not TEMPLATE.is_file():
        raise SystemExit(f"missing {TEMPLATE}")
    if not args.cover.is_file():
        raise SystemExit(f"missing cover image {args.cover}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"paperdiy-reader-{args.version}"
    package_dir = args.output_dir / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    (package_dir / "firmware").mkdir(parents=True)

    metadata = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    metadata["version"] = args.version
    metadata["repository"] = f"https://github.com/{args.repository}"
    (package_dir / "m5burner.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    firmware_name = f"{metadata['name'].replace(' ', '')}_0x0.bin"
    shutil.copy2(factory, package_dir / "firmware" / firmware_name)
    shutil.copy2(args.cover, package_dir / "cover.png")

    build_license(package_dir / "LICENSE", args.repository)
    shutil.copy2(PROJECT_DIR / "m5burner" / "PACKAGE_README.md", package_dir / "README.md")

    archive = args.output_dir / f"{package_name}.zip"
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(package_dir))

    # The desktop M5Burner publish dialog takes a single .bin; the zip is for
    # the M5Stack-Firmware repository/PR route.
    binary = args.output_dir / f"PaperDIYReader-{args.version}.bin"
    shutil.copy2(factory, binary)

    print(f"package: {package_dir}")
    print(f"archive (repo/PR route): {archive}")
    print(f"binary (desktop Publish dialog): {binary}")
    print(f"firmware: {firmware_name} ({factory.stat().st_size} bytes)")
    print(f"binary SHA256: {sha256(binary)}")
    print(f"archive SHA256: {sha256(archive)}")
    print("Next: test with M5Burner on a clean PaperDIY, then publish via USER CUSTOM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
