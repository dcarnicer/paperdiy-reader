# PaperDIY Reader — build helpers.
#
# The project pins a pioarduino platform; the isolated core directory keeps the
# build reproducible even when the global ~/.platformio has older packages.
# scripts/pio_core_dir.py picks it: one core per pinned platform release under
# ~/.platformio-cores, shared by every clone and worktree, so the ~5 GB
# toolchain is downloaded once per release and not once per checkout.
# Environments with custom_sdkconfig keep ./.platformio-core, because
# pioarduino rebuilds the framework inside the core for them. Bumping the
# platform creates a new core; delete the old one when no branch needs it.

PIO       ?= pio
ENV       ?= paperdiy
# CORE_DIR=/path on the command line overrides the choice for one run; an
# exported PLATFORMIO_CORE_DIR (as for scripts/ and CI) overrides it for every
# ENV. It is resolved only by the targets that run pio.
CORE_DIR  ?= $(or $(PLATFORMIO_CORE_DIR),$(shell python3 "$(CURDIR)/scripts/pio_core_dir.py" --pio "$(PIO)" "$(ENV)"))
PIO_CORE   = $(or $(strip $(CORE_DIR)),$(error Cannot choose the PlatformIO core for ENV=$(ENV) (see the message above); set CORE_DIR=/path))
PORT      ?=

# pio_lock.py makes a second build on the same core wait for the first.
PIO_RUN = PLATFORMIO_CORE_DIR="$(PIO_CORE)" python3 "$(CURDIR)/scripts/pio_lock.py" $(PIO) run -e $(ENV)
UPLOAD_PORT = $(if $(PORT),--upload-port "$(PORT)",)

.PHONY: build flash flash-factory monitor clean size menuconfig smoke check-upstreams core-dir

build:
	$(PIO_RUN)

# App-only update (keeps the installed bootloader/partition table).
flash:
	$(PIO_RUN) -t upload $(UPLOAD_PORT)

# First install / recovery: bootloader + partition table + app at 0x0.
flash-factory:
	@test -n "$(PORT)" || (echo "Usage: make flash-factory PORT=/dev/cu.usbmodemXXXX" && exit 1)
	esptool --chip esp32s3 --port "$(PORT)" write_flash 0x0 .pio/build/$(ENV)/firmware.factory.bin

monitor:
	PLATFORMIO_CORE_DIR="$(PIO_CORE)" $(PIO) device monitor -e $(ENV) $(if $(PORT),--port "$(PORT)",)

# Hardware regression. Requires a paperdiy-test build flashed and tesseract.
# It installs fixtures over USB MSC, runs the OCR assertions, and restores the
# user state it touched. Artifacts go to build/device-regression/<run>/.
smoke:
	python3 scripts/device_regression.py $(if $(PORT),--port "$(PORT)",)

size:
	$(PIO_RUN) -t size

# Read-only upstream report. Uses scripts/upstreams.json for the fixed source
# list and baselines; clones go to the user cache, not the repository.
check-upstreams:
	python3 scripts/check_upstreams.py

clean:
	$(PIO_RUN) -t clean

# Print the PlatformIO core for ENV (for manual pio commands, see README).
core-dir:
	@echo "$(PIO_CORE)"

# Print the exact flash commands without touching the device.
flash-commands:
	@echo "App-only update (keeps bootloader/partition table):"
	@echo "  esptool --chip esp32s3 --port <PORT> write_flash 0x10000 .pio/build/$(ENV)/firmware.bin"
	@echo "Full factory image (first install / recovery):"
	@echo "  esptool --chip esp32s3 --port <PORT> write_flash 0x0 .pio/build/$(ENV)/firmware.factory.bin"
