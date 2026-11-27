#!/usr/bin/env bash
# Build and flash the PaperDIY firmware under the PlatformIO core lock, refusing
# to touch a board that is not a 16 MB N16R8 module (the PaperDIY). While the
# firmware exposes the USB-Serial/JTAG port, esptool resets the board into
# download mode by itself. If the port does not appear, enter download mode by
# hand: hold the power button ~10 s until the red LED blinks.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-${PORT:-}}"
if [[ -z "$PORT" ]]; then
  echo "Usage: $0 /dev/cu.usbmodemXXXX" >&2
  exit 1
fi

if [[ -z "${PLATFORMIO_CORE_DIR:-}" ]]; then
  # Same choice as the Makefile; fails (set -e) instead of using another core.
  PLATFORMIO_CORE_DIR="$(python3 scripts/pio_core_dir.py paperdiy)"
fi
export PLATFORMIO_CORE_DIR

if [[ -z "${PAPERDIY_FLASH_LOCKED:-}" ]]; then
  # Run again under the core lock (scripts/pio_lock.py), so one lock covers the
  # build, the board check and the upload.
  exec env PAPERDIY_FLASH_LOCKED=1 python3 scripts/pio_lock.py bash scripts/flash.sh "$PORT"
fi

# Build first, so a failing build never leaves the board in download mode.
pio run -e paperdiy

# Capture esptool's output before parsing it: an awk that exits at the size
# line would close the pipe and, under pipefail, stop the script without a
# message. --after no-reset keeps the board in download mode for the upload.
if ! FLASH_ID="$(esptool --port "$PORT" --after no-reset flash-id 2>&1)"; then
  echo "esptool could not read the board on $PORT:" >&2
  printf '%s\n' "$FLASH_ID" | tail -n 5 >&2
  echo "If the port is missing, enter download mode by hand (power ~10 s). If the" >&2
  echo "board is stuck in download mode, press its power button to restart it." >&2
  exit 1
fi
SIZE="$(awk '/Detected flash size/ {print $4; exit}' <<<"$FLASH_ID")"
if [[ "$SIZE" != "16MB" ]]; then
  echo "Refusing to flash: detected flash size '${SIZE:-unknown}', expected 16MB." >&2
  echo "The PaperDIY uses an ESP32-S3 N16R8 (16 MB). Check the port/cable." >&2
  echo "The board stays in download mode; press its reset or power button, or" >&2
  echo "unplug it, to restart it." >&2
  exit 1
fi

# The upload rebuilds, which is a no-op right after the build above. It cannot
# use `-t nobuild`: without a build pioarduino does not set the flash addresses
# and the project's post scripts stop before esptool runs.
exec pio run -e paperdiy -t upload --upload-port "$PORT"
