#!/usr/bin/env bash
# Fetch upstream and prepare a paperdiy-next branch.
#
# Usage:
#   ./scripts/sync-upstream.sh            # show incoming changes only
#   ./scripts/sync-upstream.sh --apply    # update main + prepare paperdiy-next
#
# The script stops on conflicts. It never deletes the paperdiy branch.
set -euo pipefail
cd "$(dirname "$0")/.."

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

if ! git remote get-url upstream >/dev/null 2>&1; then
  echo "Adding upstream remote..."
  git remote add upstream https://github.com/crosspoint-reader/crosspoint-reader.git
fi

git fetch upstream --prune
echo
echo "Incoming upstream commits (main..upstream/develop):"
git log --oneline main..upstream/develop | head -40 || true
echo

if [[ "$APPLY" -eq 0 ]]; then
  echo "Run with --apply to update main and prepare paperdiy-next."
  exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Working tree is dirty. Commit/stash first." >&2
  exit 1
fi

# paperdiy-next is disposable, but it can hold the only copy of manual conflict
# resolutions between two syncs. Refuse to reset it while it has unmerged work.
if git rev-parse --verify --quiet refs/heads/paperdiy-next >/dev/null; then
  if ! git merge-base --is-ancestor paperdiy-next paperdiy; then
    echo "paperdiy-next has commits not merged into paperdiy." >&2
    echo "Merge or delete the branch before running the sync again." >&2
    exit 1
  fi
fi

# These files are shared with upstream but also carry fork edits, and the
# overlay replaces them wholesale. Stop instead of silently overwriting a new
# upstream version.
SHARED_OVERLAY="lib/expat .gitattributes .gitignore LICENSE"
if ! git diff --quiet main..upstream/develop -- $SHARED_OVERLAY; then
  echo "Upstream changed shared overlay files. Reconcile the fork edits before syncing:" >&2
  git diff --stat main..upstream/develop -- $SHARED_OVERLAY >&2
  exit 1
fi

OLD_MAIN=$(git rev-parse main)
git checkout main
git merge --ff-only upstream/develop
git checkout -B paperdiy-next main

echo "Vendoring the upstream FreeInk SDK..."
# The checkout leaves the previous vendored SDK as untracked files, which blocks
# the submodule clone. Remove it first; the pinned revision is fetched next.
rm -rf freeink-sdk
git submodule update --init --recursive freeink-sdk
rm -rf /tmp/paperdiy-sdk-new
cp -R freeink-sdk /tmp/paperdiy-sdk-new
git rm -f -q freeink-sdk
mkdir -p freeink-sdk
rsync -a --exclude='.git' /tmp/paperdiy-sdk-new/ freeink-sdk/
git add freeink-sdk

# `patches/` only exists on the paperdiy branch, so checking out main removed
# it from the working tree. Restore the patches before applying them.
git checkout paperdiy -- patches

echo "Applying patches/sdk.patch..."
git apply --3way patches/sdk.patch

echo "Applying patches/firmware.patch..."
git apply --3way patches/firmware.patch

# The firmware patch is generated from the fork and can carry the release
# version from the base it was generated against. Keep the fork's current
# release identity; the release commit bumps it deliberately.
crosspoint_version() {
  awk '
    /^\[/ { section = $0 }
    section == "[crosspoint]" && /^version = / && !found {
      sub(/^version = /, "")
      print
      found = 1
    }
  ' "$1"
}
FORK_VERSION=$(crosspoint_version <(git show paperdiy:platformio.ini))
PATCHED_VERSION=$(crosspoint_version platformio.ini)
if [[ -z "$FORK_VERSION" || -z "$PATCHED_VERSION" ]]; then
  echo "Could not find [crosspoint] version in paperdiy or the patched tree." >&2
  exit 1
fi
if [[ "$PATCHED_VERSION" != "$FORK_VERSION" ]]; then
  echo "Restoring [crosspoint] version from paperdiy: $PATCHED_VERSION -> $FORK_VERSION"
  python3 - "$FORK_VERSION" <<'PY'
import sys
from pathlib import Path

version = sys.argv[1]
path = Path("platformio.ini")
lines = path.read_text().splitlines(keepends=True)
section = None
changed = False
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        section = stripped
    elif section == "[crosspoint]" and line.startswith("version = "):
        lines[i] = f"version = {version}\n"
        changed = True
        break
if not changed:
    raise SystemExit("[crosspoint] version line not found")
path.write_text("".join(lines))
PY
fi

echo "Overlaying docs, Makefile, scripts and workflows..."
# Fork-owned files: docs/infra, agent policy, the pinned expat tree, the
# FirmwareVersion test and the release-license test (its git mock covers the
# vendored-SDK branch). Shared upstream files are edited by
# scripts/apply_downstream_overlay.py instead of being replaced wholesale.
rm -rf .github
git checkout paperdiy -- README.md README.en.md README.ja.md README.zh-CN.md \
  CHANGELOG.md Makefile NOTICE LICENSE .gitignore .gitattributes hardware m5burner \
  .agents/rules/release-versioning.md lib/expat test/firmware_version \
  test/test_release_license.py test/test_battery_log.py \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
python3 scripts/apply_downstream_overlay.py

# scripts/ is overlaid from paperdiy, but upstream also edits some of it. Put
# back upstream's version when the fork did not customize that file. A file
# both sides changed, or one upstream deleted/renamed, stops the sync instead
# of silently keeping the old fork copy.
reconcile=0
while IFS=$'\t' read -r status file rest; do
  [[ -z "$status" ]] && continue
  case "$status" in
    A|M)
      if git diff --quiet "$OLD_MAIN"..paperdiy -- "$file"; then
        git checkout main -- "$file"
      else
        echo "WARNING: upstream and fork both changed $file; reconcile it before building." >&2
        reconcile=1
      fi
      ;;
    D|R*)
      echo "WARNING: upstream deleted or renamed $file; reconcile the fork copy before building." >&2
      reconcile=1
      ;;
    *)
      echo "WARNING: unhandled upstream change $status for $file; reconcile it before building." >&2
      reconcile=1
      ;;
  esac
done < <(git diff --name-status "$OLD_MAIN"..main -- scripts)

rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules

echo "Refreshing the vendored upstream docs snapshot..."
for doc in README AGENTS GOVERNANCE ROADMAP USER_GUIDE; do
  git show main:"${doc}.md" > "docs/upstream/${doc}-crosspoint.md"
done

echo
if [[ "$reconcile" -ne 0 ]]; then
  echo "paperdiy-next prepared WITH RECONCILIATION WARNINGS; review them before building." >&2
  exit 2
fi
echo "paperdiy-next prepared. Review the diff, then run:"
echo "  make build"
echo "  # hardware smoke test"
echo "  git checkout paperdiy && git merge --no-ff paperdiy-next"
