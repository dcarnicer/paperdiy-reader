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

git checkout main
git merge --ff-only upstream/develop
git checkout -B paperdiy-next main

echo "Vendoring the upstream FreeInk SDK..."
git submodule update --init --recursive freeink-sdk
rm -rf /tmp/paperdiy-sdk-new
cp -R freeink-sdk /tmp/paperdiy-sdk-new
git rm -f -q freeink-sdk
mkdir -p freeink-sdk
rsync -a --exclude='.git' /tmp/paperdiy-sdk-new/ freeink-sdk/
git add freeink-sdk

echo "Applying patches/sdk.patch..."
git apply --3way patches/sdk.patch

echo "Applying patches/firmware.patch..."
git apply --3way patches/firmware.patch

echo "Overlaying docs, Makefile, scripts and workflows..."
rm -rf .github
git checkout paperdiy -- README.md Makefile NOTICE LICENSE .gitignore \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules

echo
echo "paperdiy-next prepared. Review the diff, then run:"
echo "  make build"
echo "  # hardware smoke test"
echo "  git checkout paperdiy && git merge --no-ff paperdiy-next"
