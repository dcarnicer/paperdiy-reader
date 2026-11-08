#!/usr/bin/env python3
"""Validate a PaperDIY release tag against the project version.

Releases are versioned <CrossPoint X.Y.Z>-<N> (N = port revision): tag
vX.Y.Z-N (or vX.Y.Z-N-rc.M), and ``[crosspoint] version`` in
platformio.ini must be the same string without the leading ``v``. See
.agents/rules/release-versioning.md.

Usage:
    python3 scripts/check_release_version.py v2.0.0-1
    GITHUB_REF_NAME=v2.0.0-1 python3 scripts/check_release_version.py
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RELEASE_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+-[1-9]\d*(?:-rc\.[1-9]\d*)?)$")


def read_project_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    section = re.search(r"^\[crosspoint\]\s*$(.*?)(?=^\[|\Z)", text, re.MULTILINE | re.DOTALL)
    if section is None:
        raise SystemExit(f"missing [crosspoint] section in {path}")
    match = re.search(r"^version\s*=\s*(\S+)\s*$", section.group(1), re.MULTILINE)
    if match is None:
        raise SystemExit(f"missing [crosspoint] version in {path}")
    return match.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tag",
        nargs="?",
        default=os.environ.get("GITHUB_REF_NAME", ""),
        help="release tag (defaults to GITHUB_REF_NAME)",
    )
    args = parser.parse_args()

    tag = args.tag.strip()
    if not tag:
        raise SystemExit("release tag is required (argument or GITHUB_REF_NAME)")
    match = RELEASE_RE.fullmatch(tag)
    if match is None:
        raise SystemExit(
            f"invalid release tag {tag!r}: expected vX.Y.Z-N or vX.Y.Z-N-rc.M "
            "(X.Y.Z = CrossPoint version, N = port revision)"
        )

    tag_version = match.group("version")
    project_version = read_project_version(PROJECT_DIR / "platformio.ini")
    if tag_version != project_version:
        raise SystemExit(
            f"release tag {tag!r} does not match [crosspoint] version "
            f"{project_version!r} in platformio.ini"
        )

    print(f"release version OK: {tag} -> {project_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
