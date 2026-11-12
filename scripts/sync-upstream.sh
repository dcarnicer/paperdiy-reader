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

# These files are shared with upstream but also carry fork edits, and the
# overlay replaces them wholesale. Stop instead of silently overwriting a new
# upstream version.
SHARED_OVERLAY="lib/expat .gitattributes .gitignore LICENSE"
if ! git diff --quiet main..upstream/develop -- $SHARED_OVERLAY; then
  echo "Upstream changed shared overlay files. Reconcile the fork edits before syncing:" >&2
  git diff --stat main..upstream/develop -- $SHARED_OVERLAY >&2
  exit 1
fi

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

echo "Overlaying docs, Makefile, scripts and workflows..."
# Fork-owned files: docs/infra, agent policy, the pinned expat tree and the
# FirmwareVersion test. Shared upstream files are edited by
# scripts/apply_downstream_overlay.py instead of being replaced wholesale.
rm -rf .github
git checkout paperdiy -- README.md README.en.md README.ja.md README.zh-CN.md \
  CHANGELOG.md Makefile NOTICE LICENSE .gitignore .gitattributes hardware m5burner \
  .agents/rules/release-versioning.md lib/expat test/firmware_version \
  docs/paperdiy docs/README.md docs/upstream scripts patches .github
python3 scripts/apply_downstream_overlay.py
rm -f ROADMAP.md SCOPE.md GOVERNANCE.md AGENTS.md USER_GUIDE.md CLAUDE.md .gitmodules

echo "Refreshing the vendored upstream docs snapshot..."
for doc in README AGENTS GOVERNANCE ROADMAP USER_GUIDE; do
  git show main:"${doc}.md" > "docs/upstream/${doc}-crosspoint.md"
done

echo
echo "paperdiy-next prepared. Review the diff, then run:"
echo "  make build"
echo "  # hardware smoke test"
echo "  git checkout paperdiy && git merge --no-ff paperdiy-next"
