#!/usr/bin/env python3
"""PaperDIY USB test helper.

Works with the `paperdiy-test` build, which exposes the development-only
`CMD:KEY:<key>` serial command. The regular `paperdiy` build still supports
`CMD:SCREENSHOT`; key injection is compiled out on purpose.

Examples:
    python3 scripts/paperdiy_serial.py screenshot /tmp/home.png
    python3 scripts/paperdiy_serial.py key B
    python3 scripts/paperdiy_serial.py key B_LONG
    python3 scripts/paperdiy_serial.py key A_LONG
"""

from __future__ import annotations

import argparse
import glob
import os
import select
import struct
import sys
import termios
import time
import zlib


DEFAULT_WIDTH = 960
DEFAULT_HEIGHT = 540


class SerialTimeout(TimeoutError):
    pass


class SerialReader:
    def __init__(self, fd: int) -> None:
        self.fd = fd
        self.buffer = bytearray()

    def _fill(self, deadline: float) -> None:
        remaining = deadline - time.time()
        if remaining <= 0:
            return
        ready, _, _ = select.select([self.fd], [], [], min(0.2, remaining))
        if not ready:
            return
        try:
            data = os.read(self.fd, 8192)
        except BlockingIOError:
            return
        if data:
            self.buffer.extend(data)

    def wait_for(self, marker: bytes, timeout: float) -> None:
        deadline = time.time() + timeout
        while marker not in self.buffer:
            if time.time() >= deadline:
                raise SerialTimeout(f"timeout waiting for {marker!r}")
            self._fill(deadline)
        index = self.buffer.find(marker)
        del self.buffer[: index + len(marker)]

    def read_until(self, marker: bytes, timeout: float) -> bytes:
        deadline = time.time() + timeout
        while True:
            index = self.buffer.find(marker)
            if index >= 0:
                data = bytes(self.buffer[:index])
                del self.buffer[: index + len(marker)]
                return data
            if time.time() >= deadline:
                raise SerialTimeout(f"timeout waiting for {marker!r}")
            self._fill(deadline)

    def read_exact(self, size: int, timeout: float) -> bytes:
        deadline = time.time() + timeout
        while len(self.buffer) < size:
            if time.time() >= deadline:
                raise SerialTimeout(f"timeout reading {size} bytes")
            self._fill(deadline)
        data = bytes(self.buffer[:size])
        del self.buffer[:size]
        return data

    def drain(self) -> None:
        while True:
            ready, _, _ = select.select([self.fd], [], [], 0)
            if not ready:
                return
            try:
                if not os.read(self.fd, 8192):
                    return
            except BlockingIOError:
                return


def open_port(port: str, baud: int) -> int:
    fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    attrs = termios.tcgetattr(fd)
    attrs[0] = 0  # iflag: raw
    attrs[1] = 0  # oflag: raw
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
    attrs[3] = 0  # lflag: raw
    speed = getattr(termios, f"B{baud}")
    attrs[4] = speed
    attrs[5] = speed
    attrs[6][termios.VMIN] = 0
    attrs[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    return fd


def write_all(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        _, ready, _ = select.select([], [fd], [], 1.0)
        if not ready:
            raise SerialTimeout("timeout writing to serial port")
        written = os.write(fd, view)
        view = view[written:]


def find_port() -> str:
    patterns = ("/dev/cu.usbmodem*", "/dev/tty.usbmodem*", "/dev/ttyACM*")
    candidates: list[str] = []
    for pattern in patterns:
        candidates.extend(sorted(glob.glob(pattern)))
    if not candidates:
        raise SystemExit("No USB serial port found. Connect the PaperDIY or pass --port.")
    return candidates[0]


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path: str, rows: list[bytearray], width: int, height: int) -> None:
    raw = b"".join(b"\x00" + bytes(row) for row in rows)
    with open(path, "wb") as output:
        output.write(b"\x89PNG\r\n\x1a\n")
        output.write(png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)))
        output.write(png_chunk(b"IDAT", zlib.compress(raw, 9)))
        output.write(png_chunk(b"IEND", b""))


def framebuffer_rows(
    framebuffer: bytes, width: int, height: int, rotate: int, invert: bool
) -> tuple[int, int, list[bytearray]]:
    row_bytes = (width + 7) // 8
    required = row_bytes * height
    if len(framebuffer) < required:
        raise SystemExit(f"short framebuffer: got {len(framebuffer)} bytes, need {required}")

    if rotate not in (0, 90, 180, 270):
        raise SystemExit(f"invalid rotation {rotate}; use 0, 90, 180 or 270")

    rows: list[bytearray] = []
    if rotate == 90:
        # Rotate the 960x540 panel buffer 90 degrees clockwise into the
        # 540x960 portrait view used by the reader UI.
        out_width, out_height = height, width
        for out_y in range(out_height):
            row = bytearray(out_width)
            src_x = out_y
            for out_x in range(out_width):
                src_y = height - 1 - out_x
                index = src_y * row_bytes + (src_x >> 3)
                bit = (framebuffer[index] >> (7 - (src_x & 7))) & 1
                if invert:
                    bit ^= 1
                row[out_x] = 255 if bit else 0
            rows.append(row)
    elif rotate == 270:
        # 90 degrees counter-clockwise.
        out_width, out_height = height, width
        for out_y in range(out_height):
            row = bytearray(out_width)
            src_x = width - 1 - out_y
            for out_x in range(out_width):
                src_y = out_x
                index = src_y * row_bytes + (src_x >> 3)
                bit = (framebuffer[index] >> (7 - (src_x & 7))) & 1
                if invert:
                    bit ^= 1
                row[out_x] = 255 if bit else 0
            rows.append(row)
    elif rotate == 180:
        out_width, out_height = width, height
        for out_y in range(out_height):
            row = bytearray(out_width)
            src_y = height - 1 - out_y
            for out_x in range(out_width):
                src_x = width - 1 - out_x
                index = src_y * row_bytes + (src_x >> 3)
                bit = (framebuffer[index] >> (7 - (src_x & 7))) & 1
                if invert:
                    bit ^= 1
                row[out_x] = 255 if bit else 0
            rows.append(row)
    else:
        out_width, out_height = width, height
        for out_y in range(out_height):
            row = bytearray(out_width)
            for out_x in range(out_width):
                index = out_y * row_bytes + (out_x >> 3)
                bit = (framebuffer[index] >> (7 - (out_x & 7))) & 1
                if invert:
                    bit ^= 1
                row[out_x] = 255 if bit else 0
            rows.append(row)
    return out_width, out_height, rows


def screenshot(args: argparse.Namespace, fd: int, reader: SerialReader) -> None:
    reader.drain()
    write_all(fd, b"CMD:SCREENSHOT\n")
    reader.wait_for(b"SCREENSHOT_START:", args.timeout)
    size_line = reader.read_until(b"\n", args.timeout).strip()
    try:
        size = int(size_line)
    except ValueError as exc:
        raise SystemExit(f"invalid screenshot size: {size_line!r}") from exc

    framebuffer = reader.read_exact(size, args.timeout)
    reader.wait_for(b"SCREENSHOT_END", args.timeout)

    if args.raw:
        with open(args.raw, "wb") as output:
            output.write(framebuffer)
        print(f"raw framebuffer: {args.raw} ({size} bytes)")

    rotation = 0 if args.no_rotate else args.rotate
    width, height, rows = framebuffer_rows(framebuffer, args.width, args.height, rotation, args.invert)
    write_png(args.output, rows, width, height)
    print(f"screenshot: {args.output} ({width}x{height}, rotate={rotation})")


def key(args: argparse.Namespace, fd: int, reader: SerialReader) -> None:
    name = args.key.upper()
    valid = {"A", "B", "A_LONG", "B_LONG", "NEXT", "PREV", "UP", "DOWN", "CONFIRM", "OK", "BACK"}
    if name not in valid:
        raise SystemExit(f"invalid key {name!r}; choose one of: {', '.join(sorted(valid))}")

    for attempt in range(args.retry + 1):
        reader.drain()
        write_all(fd, f"CMD:KEY:{name}\n".encode())
        reader.wait_for(f"KEY:{name}:".encode(), args.timeout)
        result = reader.read_until(b"\n", args.timeout).strip()
        if result == b"1":
            print(f"key {name}: accepted" + (f" (retry {attempt})" if attempt else ""))
            time.sleep(args.settle)
            return
        if attempt < args.retry:
            time.sleep(0.5)
    print(f"key {name}: ignored after {args.retry + 1} attempt(s)")
    raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PaperDIY USB test helper")
    parser.add_argument("--port", help="serial port (default: first /dev/cu.usbmodem*)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=5.0)
    subparsers = parser.add_subparsers(dest="command", required=True)

    shot = subparsers.add_parser("screenshot", help="capture the e-ink framebuffer")
    shot.add_argument("output", help="output PNG path")
    shot.add_argument("--raw", help="also save the raw framebuffer")
    shot.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    shot.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    shot.add_argument("--rotate", type=int, choices=(0, 90, 180, 270), default=90,
                      help="clockwise rotation from the native panel buffer (default: 90)")
    shot.add_argument("--no-rotate", action="store_true", help="alias for --rotate 0")
    shot.add_argument("--invert", action="store_true", help="invert black/white")
    shot.set_defaults(func=screenshot)

    press = subparsers.add_parser("key", help="inject one key (paperdiy-test build)")
    press.add_argument("key", help="A, B, A_LONG, B_LONG, NEXT, PREV, CONFIRM, BACK")
    press.add_argument("--retry", type=int, default=2, help="retries when the reader is busy (default: 2)")
    press.add_argument("--settle", type=float, default=0.5, help="seconds to wait after an accepted key (default: 0.5)")
    press.set_defaults(func=key)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    port = args.port or find_port()
    fd = open_port(port, args.baud)
    reader = SerialReader(fd)
    try:
        args.func(args, fd, reader)
    except SerialTimeout as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        os.close(fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
