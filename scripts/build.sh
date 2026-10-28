#!/usr/bin/env bash
# Build the PaperDIY firmware with an isolated PlatformIO core.
set -euo pipefail
cd "$(dirname "$0")/.."
export PLATFORMIO_CORE_DIR="${PLATFORMIO_CORE_DIR:-$PWD/.platformio-core}"
exec pio run -e paperdiy "$@"
