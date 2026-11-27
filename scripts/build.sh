#!/usr/bin/env bash
# Build the PaperDIY firmware with the isolated PlatformIO core the Makefile uses.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${PLATFORMIO_CORE_DIR:-}" ]]; then
  # Same choice as the Makefile; fails (set -e) instead of using another core.
  PLATFORMIO_CORE_DIR="$(python3 scripts/pio_core_dir.py paperdiy)"
fi
export PLATFORMIO_CORE_DIR
# pio_lock.py holds the core lock while pio runs, so a monitor session here
# would block every other build on the same core: use `make monitor`.
for arg in "$@"; do
  if [[ "$arg" == "monitor" || "$arg" == "-tmonitor" || "$arg" == "--target=monitor" ]]; then
    echo "Use \`make monitor\` for the serial monitor; this script holds the core lock." >&2
    exit 2
  fi
done
exec python3 scripts/pio_lock.py pio run -e paperdiy "$@"
