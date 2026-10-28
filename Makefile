# PaperDIY Reader — build helpers.
#
# The project pins a pioarduino platform; the isolated core directory keeps the
# build reproducible even when the global ~/.platformio has older packages.
# It is git-ignored and only needs to be downloaded once (~5 GB with toolchain).

PIO       ?= pio
ENV       ?= paperdiy
CORE_DIR  ?= $(CURDIR)/.platformio-core
PORT      ?=

PIO_RUN = PLATFORMIO_CORE_DIR="$(CORE_DIR)" $(PIO) run -e $(ENV)
UPLOAD_PORT = $(if $(PORT),--upload-port "$(PORT)",)

.PHONY: build flash flash-factory monitor clean size menuconfig

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
	PLATFORMIO_CORE_DIR="$(CORE_DIR)" $(PIO) device monitor -e $(ENV) $(if $(PORT),--port "$(PORT)",)

size:
	$(PIO_RUN) -t size

clean:
	$(PIO_RUN) -t clean

# Print the exact flash commands without touching the device.
flash-commands:
	@echo "App-only update (keeps bootloader/partition table):"
	@echo "  esptool --chip esp32s3 --port <PORT> write_flash 0x10000 .pio/build/$(ENV)/firmware.bin"
	@echo "Full factory image (first install / recovery):"
	@echo "  esptool --chip esp32s3 --port <PORT> write_flash 0x0 .pio/build/$(ENV)/firmware.factory.bin"
