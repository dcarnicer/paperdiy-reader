#!/usr/bin/env bash
# Flash the PaperDIY firmware, refusing to touch a board that is not a 16 MB
# N16R8 module (the PaperDIY). While the firmware exposes the USB-Serial/JTAG
# port, esptool resets the board into download mode by itself. If the port does
# not appear, enter download mode by hand: hold the power button ~10 s until the
# red LED blinks.
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

if [[ -z "${PLATFORMIO_CORE_DIR:-}" ]]; then
  # Same choice as the Makefile; fails (set -e) instead of using another core.
  PLATFORMIO_CORE_DIR="$(python3 scripts/pio_core_dir.py paperdiy)"
fi
export PLATFORMIO_CORE_DIR
exec pio run -e paperdiy -t upload --upload-port "$PORT"
