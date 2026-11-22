---
name: upstream-sync
description: Check CrossPoint, the FreeInk SDK and the M5Stack source repositories for upstream updates or new components before an update. Use whenever the user asks to look for upstream changes, new components to bring in, or to prepare/perform an upstream sync.
---

# Upstream and component check

Start every upstream-update request by running the fixed checker; do not answer
from memory or with an ad-hoc `git log`:

```bash
make check-upstreams
# or: python3 scripts/check_upstreams.py [--json] [--strict]
```

The script is read-only and always checks the same sources against the
baselines in `scripts/upstreams.json`. It never changes branches and never
vendors anything.

## Fixed sources

- **CrossPoint**: `main..upstream/develop` in this repository.
- **FreeInk SDK**: the pin in `upstream/develop` versus the pin in `main`, plus
  the SDK `origin/main`.
- **M5GFX**: the `m5stack/M5GFX @ …` pin in `platformio.ini` versus its latest
  release.
- **M5 reference sources**: `m5stack/M5PM1`, `M5IOE1`,
  `M5PaperDIY-UserDemo`, `M5PaperS3-UserDemo`, `uiflow-micropython`
  (`m5pm1.py`) and `M5Unified`.
- **M5_Hardware**: only the PaperDIY 3D files; hardware is informational.

## Classify before reporting

A **new component** is a new top-level `lib/<name>/`, `libs/<name>/` or
`src/components/<name>/`, a new `library.json`, a new PlatformIO dependency, or
a new board profile/display driver. Fixes, refactors, comment changes,
dead-code removal and a new tag of an existing dependency are **not** new
components.

- CrossPoint and FreeInk are the firmware/SDK sources we sync.
- M5GFX is a dependency, not a component to copy.
- M5PM1, M5IOE1, M5PaperDIY-UserDemo, M5PaperS3-UserDemo, uiflow-micropython
  and M5Unified are reference sources; we extracted register maps and
  behaviour, not whole libraries.
- CrossPoint's submodule pin wins. Never vendor FreeInk `main` commits that
  CrossPoint has not pinned, and never bump an M5 dependency tag on our own.

## Report

Answer in the user's language, and lead with the classification:

1. Whether there are new components (yes/no).
2. A table with source, baseline, current, commits, added files and action.
3. The relevant fixes or releases, and whether they affect PaperDIY.
4. Merge risks in our patches, if a sync is being considered.

If a source could not be checked (network, missing ref), say so explicitly; do
not present it as up to date.

Known conflict hotspots in a sync are `src/activities/settings/AboutActivity.*`
(upstream `ITEM_COUNT` versus our battery row) and any file that appears in
both `git diff --name-only main..upstream/develop` and
`patches/firmware.patch`. The SDK patch usually reapplies with
`git apply --3way`; verify it rather than assuming.

## Syncing is a separate, explicit step

Only run the sync when the user asks for it:

```bash
./scripts/sync-upstream.sh --apply
```

Follow `docs/paperdiy/10-fork-maintenance.md`. The script needs a clean work
tree, updates `main`, creates `paperdiy-next`, vendors the SDK and applies the
patches. Resolve conflicts, run `make build`, and run `make smoke` only when
the hardware is available. Do not commit, merge into `paperdiy` or publish
without explicit approval.

Update a baseline in `scripts/upstreams.json` only after the change has been
reviewed and accepted; merely seeing drift is not a reason to move it.
