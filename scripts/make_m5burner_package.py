#!/usr/bin/env python3
"""Build an M5Burner package from the production PaperDIY firmware.

The M5Burner format is a directory with m5burner.json and a firmware/ folder
whose files are named <name>_<hex-address>.bin. We ship the combined factory
image at 0x0 so bootloader, partition table and app stay together.

Usage:
    python3 scripts/make_m5burner_package.py  # version from platformio.ini
"""
from __future__ import annotations

import argparse
import re
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_BUILD = PROJECT_DIR / ".pio" / "build" / "paperdiy"
DEFAULT_OUTPUT = PROJECT_DIR / "dist" / "m5burner"
DEFAULT_COVER = PROJECT_DIR / "m5burner" / "cover.png"
TEMPLATE = PROJECT_DIR / "m5burner" / "m5burner.json"
FIRMWARE_SLUG = "PaperDIYReader"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def packages_dir() -> Path:
    """Packages of the core `make build ENV=paperdiy` uses by default.

    That is PLATFORMIO_CORE_DIR when exported, else the core
    scripts/pio_core_dir.py picks. Without --packages-dir,
    build_release_license.py falls back to ~/.platformio when the variable is
    unset. After `make build CORE_DIR=/path`, export PLATFORMIO_CORE_DIR=/path;
    check_linked_core() refuses a mismatch.
    """
    core = os.environ.get("PLATFORMIO_CORE_DIR")
    if not core:
        result = subprocess.run(
            [sys.executable, str(PROJECT_DIR / "scripts" / "pio_core_dir.py"), "paperdiy"],
            cwd=PROJECT_DIR, capture_output=True, text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            raise SystemExit(result.stderr.strip() or "cannot choose the PlatformIO core for paperdiy")
        core = result.stdout.strip()
    return Path(core).expanduser() / "packages"


def check_linked_core(build_dir: Path, packages: Path) -> None:
    """Stop when the firmware was not linked against `packages`."""
    linker_map = build_dir / "firmware.map"
    if not linker_map.is_file():
        raise SystemExit(f"missing {linker_map}; run `make build ENV=paperdiy` first")
    # abspath, not resolve: PlatformIO keeps symlinked core paths unresolved.
    libs = os.path.join(os.path.abspath(packages), "framework-arduinoespressif32-libs")
    if libs not in linker_map.read_text(encoding="utf-8", errors="replace"):
        raise SystemExit(
            f"{linker_map} was not linked against {libs}; export the "
            "PLATFORMIO_CORE_DIR the firmware was built with")


def build_license(output: Path, repository: str, packages: Path) -> None:
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
            "--packages-dir",
            str(packages),
        ],
        cwd=PROJECT_DIR,
        check=True,
    )


def project_version() -> str:
    text = (PROJECT_DIR / "platformio.ini").read_text(encoding="utf-8")
    section = re.search(r"^\[crosspoint\]\s*$(.*?)(?=^\[|\Z)", text, re.MULTILINE | re.DOTALL)
    match = section and re.search(r"^version\s*=\s*(\S+)\s*$", section.group(1), re.MULTILINE)
    if not match:
        raise SystemExit("missing [crosspoint] version in platformio.ini")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="defaults to [crosspoint] version in platformio.ini")
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cover", type=Path, default=DEFAULT_COVER)
    parser.add_argument("--repository", default="dcarnicer/paperdiy-reader")
    args = parser.parse_args()
    if not args.version:
        args.version = project_version()

    factory = args.build_dir / "firmware.factory.bin"
    if not factory.is_file():
        raise SystemExit(f"missing {factory}; run `make build ENV=paperdiy` first")
    if not TEMPLATE.is_file():
        raise SystemExit(f"missing {TEMPLATE}")
    if not args.cover.is_file():
        raise SystemExit(f"missing cover image {args.cover}")
    # Resolve and check the core before touching the output directory.
    packages = packages_dir()
    check_linked_core(args.build_dir, packages)

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

    firmware_name = f"{FIRMWARE_SLUG}_0x0.bin"
    shutil.copy2(factory, package_dir / "firmware" / firmware_name)
    shutil.copy2(args.cover, package_dir / "cover.png")

    build_license(package_dir / "LICENSE", args.repository, packages)
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
    # Same name as the GitHub release asset; the version goes in M5Burner's field.
    binary = args.output_dir / "crosspoint-paperdiy-latest.bin"
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
