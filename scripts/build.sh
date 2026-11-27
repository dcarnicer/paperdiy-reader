#!/usr/bin/env bash
# Build the PaperDIY firmware with the isolated PlatformIO core the Makefile uses.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -z "${PLATFORMIO_CORE_DIR:-}" ]]; then
  # Same choice as the Makefile; fails (set -e) instead of using another core.
  PLATFORMIO_CORE_DIR="$(python3 scripts/pio_core_dir.py paperdiy)"
fi
export PLATFORMIO_CORE_DIR
exec pio run -e paperdiy "$@"
