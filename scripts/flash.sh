#!/usr/bin/env bash
# Flash the PaperDIY firmware, refusing to touch a board that is not a 16 MB
# N16R8 module (the PaperDIY). Put the device in download mode first: hold the
# power button ~2 s until the red LED blinks.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-${PORT:-}}"
if [[ -z "$PORT" ]]; then
  echo "Usage: $0 /dev/cu.usbmodemXXXX" >&2
  exit 1
fi

SIZE="$(esptool --port "$PORT" flash-id 2>/dev/null | awk '/Detected flash size/ {print $4; exit}')"
if [[ "$SIZE" != "16MB" ]]; then
  echo "Refusing to flash: detected flash size '${SIZE:-unknown}', expected 16MB." >&2
  echo "The PaperDIY uses an ESP32-S3 N16R8 (16 MB). Check the port/cable." >&2
  exit 1
fi

export PLATFORMIO_CORE_DIR="${PLATFORMIO_CORE_DIR:-$PWD/.platformio-core}"
exec pio run -e paperdiy -t upload --upload-port "$PORT"
