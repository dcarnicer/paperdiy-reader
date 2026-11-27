# PaperDIY Reader agent guide

This repository is a fork of CrossPoint Reader for the M5Stack PaperDIY
(ESP32-S3 N16R8, 16 MB flash, 8 MB PSRAM). Work happens on the `paperdiy`
branch; the personal remote is `fork`. Upstream's agent guide is archived in
[docs/upstream/AGENTS-crosspoint.md](docs/upstream/AGENTS-crosspoint.md); the
rules in `.agents/rules/` and the skills in `.agents/skills/` still apply,
except where this file says otherwise. To find the guidance for a decision,
use the routing table in that archived guide; read its paths from the
repository root.

## Build and flash

- Build with `make build` (`ENV=paperdiy` by default) or `scripts/build.sh`;
  flash with `scripts/flash.sh /dev/cu.usbmodemXXXX` or `make flash PORT=...`.
- Do not run a bare `pio run`. The Makefile and the scripts pick a PlatformIO
  core per platform release (`scripts/pio_core_dir.py`, `make -s core-dir`)
  and lock it while pio runs (`scripts/pio_lock.py`). A bare `pio run` uses
  the global `~/.platformio`, which mixes framework versions, and skips the
  lock that keeps parallel worktrees from writing the same core.
- `pio_lock: waiting for another build ...` means the build is queued behind
  another checkout on the same core: wait, do not kill it or change the core.
- Python tests: `python3 -m unittest discover -s test -p 'test_*.py'`.
  `test_firmware_stats` fails to import: it loads an upstream CI script this
  fork removed. That failure is known; do not chase it.
- Hardware: if the board's port does not appear, the human enters download
  mode by holding the power button ~10 s until the red LED blinks. Hardware
  tests are the human's; never claim them.

## Changes and review

- Firmware and build changes go through
  [firmware-handoff](.agents/skills/firmware-handoff/SKILL.md) before a local
  commit, including the human's explicit acceptance of the design.
- `README*.md` and the translated `docs/paperdiy` guides (01-hardware,
  06-porting, 07-user-guide) exist in Spanish, English, Japanese and
  Simplified Chinese, and 13-m5launcher in Spanish and English: when you
  change one language of a file, change all its languages. The other
  `docs/paperdiy` files are Spanish only.
- Upstream syncs follow [upstream-sync](.agents/skills/upstream-sync/SKILL.md).

## Human ownership

- Local commits need explicit human approval; push only on an explicit
  instruction to push. Never open or close a PR; the human writes PR text.
- Commit messages: `<type>: <summary>`, summary at most 50 characters, see
  [git-workflow](.agents/rules/git-workflow.md). No assistant co-author or
  generated-by trailers.
- Review subagents only read code, diffs, history and recorded checks; they
  do not write files, build, test, commit or flash.
