#!/usr/bin/env python3
"""Add the fork's one-line changes to upstream-owned files after a sync.

The patch set does not carry these lines because they live in files that
upstream also edits. Start from upstream's version and insert only the fork
lines, failing if an anchor moved so a sync cannot silently lose them.
"""

from __future__ import annotations

from pathlib import Path
import sys

# (path, anchor line, line to insert after the anchor)
EDITS = (
    (
        Path(".agents/README.md"),
        "- `git-workflow.md`: repository context, branches, commits, and publication controls\n",
        "- `release-versioning.md`: `<CrossPoint X.Y.Z>-<N>` versions, tags, ordering, and OTA asset naming\n",
    ),
    (
        Path("test/CMakeLists.txt"),
        "add_subdirectory(release_json_parser)\n",
        "add_subdirectory(firmware_version)\n",
    ),
    (
        Path("test/koreader_xpath_resolver/CMakeLists.txt"),
        "  ${REPO_ROOT}/lib/expat/xmltok.c\n",
        "  ${REPO_ROOT}/lib/expat/xcs.c\n",
    ),
)


def main() -> int:
    # Validate every anchor before writing anything, so a moved anchor cannot
    # leave a partially overlaid tree.
    pending: list[tuple[Path, str, str, str]] = []
    for path, anchor, line in EDITS:
        text = path.read_text(encoding="utf-8")
        if line in text:
            continue
        if anchor not in text:
            print(
                f"{path}: anchor not found; update scripts/apply_downstream_overlay.py "
                "and merge it to paperdiy before running the sync",
                file=sys.stderr,
            )
            return 1
        pending.append((path, text, anchor, line))

    for path, text, anchor, line in pending:
        path.write_text(text.replace(anchor, anchor + line, 1), encoding="utf-8")
        print(f"{path}: inserted downstream line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
