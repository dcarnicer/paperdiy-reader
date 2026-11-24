#!/usr/bin/env python3
"""Record the synced CrossPoint commit and FreeInk SDK pin in NOTICE.

The fork vendors the SDK, so `scripts/build_release_license.py` reads the SDK
revision from NOTICE. Run this after every upstream sync (sync-upstream.sh does
it) so the release LICENSE names the sources the firmware was built from.

Usage: update_notice_pins.py [--ref main] [--notice NOTICE] [--check]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

UPSTREAM_RE = re.compile(
    r"(CrossPoint Reader .*?\n(?:  .*\n)*?  Commit: )([0-9a-f]{40}) \((\d{4}-\d{2}-\d{2})\)"
)
VERSION_RE = re.compile(r"(  CrossPoint Reader )(\S+)( \(develop branch\))")
SDK_RE = re.compile(r"(FreeInk SDK\n(?:  .*\n)*?  Commit: )([0-9a-f]{40})")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=PROJECT_DIR, text=True).strip()


def crosspoint_version(commit: str) -> str:
    section = None
    for line in git("show", f"{commit}:platformio.ini").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped
        elif section == "[crosspoint]" and line.startswith("version = "):
            return line.split("=", 1)[1].strip()
    raise SystemExit(f"{commit}: [crosspoint] version not found")


def pins(ref: str) -> tuple[str, str, str, str]:
    commit = git("rev-parse", f"{ref}^{{commit}}")
    date = git("show", "-s", "--format=%cs", commit)
    # A gitlink names a commit of another repository, so read it from the tree.
    entry = git("ls-tree", commit, "freeink-sdk").split()
    if len(entry) < 3 or entry[0] != "160000":
        raise SystemExit(f"{ref} does not pin freeink-sdk as a submodule")
    return commit, date, entry[2], crosspoint_version(commit)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="main", help="upstream mirror ref (default: main)")
    parser.add_argument("--notice", type=Path, default=PROJECT_DIR / "NOTICE")
    parser.add_argument("--check", action="store_true", help="fail if NOTICE is stale")
    args = parser.parse_args()

    commit, date, sdk, version = pins(args.ref)
    text = args.notice.read_text(encoding="utf-8")
    if not (UPSTREAM_RE.search(text) and SDK_RE.search(text) and VERSION_RE.search(text)):
        raise SystemExit("NOTICE: CrossPoint version/commit or FreeInk SDK commit line not found")
    updated = VERSION_RE.sub(lambda m: f"{m.group(1)}{version}{m.group(3)}", text, count=1)
    updated = UPSTREAM_RE.sub(lambda m: f"{m.group(1)}{commit} ({date})", updated, count=1)
    updated = SDK_RE.sub(lambda m: f"{m.group(1)}{sdk}", updated, count=1)

    if args.check:
        if updated != text:
            print(f"NOTICE is stale: expected CrossPoint {version} {commit[:8]} / SDK {sdk[:8]}", file=sys.stderr)
            return 1
        print(f"NOTICE OK: CrossPoint {version} {commit[:8]} / SDK {sdk[:8]}")
        return 0
    if updated != text:
        args.notice.write_text(updated, encoding="utf-8")
    print(f"NOTICE: CrossPoint {version} {commit[:8]} ({date}) / SDK {sdk[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
