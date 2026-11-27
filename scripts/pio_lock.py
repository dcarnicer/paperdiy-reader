#!/usr/bin/env python3
"""Run a command while holding an exclusive lock on its PlatformIO core.

Checkouts that build the same platform release share one core (see
scripts/pio_core_dir.py), and a build also rewrites state inside it: the
builder and cache markers patched by scripts/patch_pioarduino_cache.py, the
temporary lib_ignore patch pioarduino applies to <chip>/pioarduino-build.py,
and the first install of a new release. While one command holds the lock, a
second one that uses the same core waits until the first ends.

Usage: pio_lock.py COMMAND [ARGS...]
The core is PLATFORMIO_CORE_DIR, which must be set; a leading ~ is expanded,
as PlatformIO does. The lock is taken on <core>/.build.lock, which also
records the PID and command of the holder, and the command inherits the
locked descriptor, so the lock lasts exactly as long as the command and its
children. Only commands started through this script take the lock. On a
host without fcntl (native Windows Python) it warns and runs the command
without the lock.
"""
import os
import subprocess
import sys
from pathlib import Path

try:
    import fcntl
except ImportError:  # native Windows Python
    fcntl = None

LOCK_NAME = ".build.lock"


def holder(fd):
    os.lseek(fd, 0, os.SEEK_SET)
    return os.read(fd, 4096).decode(errors="replace").strip() or "unknown"


def main(argv):
    if not argv:
        print("usage: pio_lock.py COMMAND [ARGS...]", file=sys.stderr)
        return 2
    core = os.environ.get("PLATFORMIO_CORE_DIR")
    if not core:
        print("pio_lock: PLATFORMIO_CORE_DIR is not set", file=sys.stderr)
        return 2
    core = Path(core).expanduser()
    if fcntl is None:
        print("pio_lock: no fcntl on this host; running without the core lock",
              file=sys.stderr)
        # exec on Windows would end this process with status 0 at once.
        try:
            return subprocess.call(argv)
        except OSError as exc:
            print(f"pio_lock: cannot run {argv[0]}: {exc}", file=sys.stderr)
            return 127
    else:
        core.mkdir(parents=True, exist_ok=True)
        fd = os.open(core / LOCK_NAME, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"pio_lock: waiting for another build that uses {core} "
                  f"(held by {holder(fd)})", file=sys.stderr, flush=True)
            fcntl.flock(fd, fcntl.LOCK_EX)
        os.ftruncate(fd, 0)
        os.pwrite(fd, f"pid {os.getpid()}: {' '.join(argv)}\n".encode(), 0)
        os.set_inheritable(fd, True)
    try:
        os.execvp(argv[0], argv)
    except OSError as exc:
        print(f"pio_lock: cannot run {argv[0]}: {exc}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
