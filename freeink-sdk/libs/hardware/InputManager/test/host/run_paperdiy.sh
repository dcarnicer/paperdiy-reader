#!/bin/sh
set -eu
cd "$(dirname "$0")"
BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/freeink-paperdiy-input.XXXXXX")
trap 'rm -rf "$BUILD_DIR"' EXIT
c++ -std=c++17 -Wall -Wextra -Wno-unused-parameter \
  -DFREEINK_DEVICE_PAPERDIY=1 -DFREEINK_CAP_TOUCH=0 -DARDUINO_USB_CDC_ON_BOOT=1 \
  -Ipaperdiy_stubs -Imetalio_stubs -I../../include -I../../../BoardConfig/include \
  test_paperdiy.cpp ../../src/InputManager.cpp -o "$BUILD_DIR/test_paperdiy"
"$BUILD_DIR/test_paperdiy"
