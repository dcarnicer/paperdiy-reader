#!/usr/bin/env python3
"""Print the PlatformIO core directory to build a project environment with.

Environments that only use a pinned platform release share one core per
release under ~/.platformio-cores (for example pioarduino-55.03.311), so every
clone and worktree downloads the toolchain and framework once. Different
pinned releases never share a core: pioarduino and the official platform both
install packages called framework-arduinoespressif32, and pioarduino keeps a
single version of each tool under tools/.

Environments that make pioarduino rebuild or swap framework packages inside
the core keep the core inside the checkout, <repo>/.platformio-core, as
before: those that set custom_sdkconfig (even empty), custom_component_add or
_remove, platform_packages or any board_espidf.* option, or whose project
board manifest has espidf.custom_sdkconfig. pioarduino writes their libraries
into the core and reinstalls the framework when another environment needs the
stock one, so a shared core would mix builds across checkouts. Board manifests
that ship with the platform are not inspected; none used here sets
espidf.custom_sdkconfig.

Usage: pio_core_dir.py [--pio PIO] ENV
Prints the directory and exits 0, or prints nothing and exits 1 with the
reason on stderr. It never falls back to another core silently.
"""
import hashlib
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
CORES = Path.home() / ".platformio-cores"
CHECKOUT_CORE = PROJECT / ".platformio-core"
# Options that make pioarduino rebuild or replace framework packages in the core.
CHECKOUT_CORE_OPTIONS = (
    "custom_sdkconfig",
    "custom_component_add",
    "custom_component_remove",
    "platform_packages",
)


def project_config(env, pio):
    out = subprocess.run(
        shlex.split(pio) + ["project", "config", "--json-output"],
        cwd=PROJECT, capture_output=True, text=True, check=True,
    ).stdout
    # `pio project config` already applies [env] and `extends` inheritance.
    sections = {name: dict(options) for name, options in json.loads(out)}
    if f"env:{env}" not in sections:
        raise LookupError(f"platformio.ini has no [env:{env}]")
    return sections[f"env:{env}"], sections.get("platformio", {})


def board_custom_sdkconfig(options, project_options):
    # boards_dir is a [platformio] option, relative to the project.
    boards_dir = Path(project_options.get("boards_dir") or "boards")
    if not boards_dir.is_absolute():
        boards_dir = PROJECT / boards_dir
    manifest = boards_dir / f"{options.get('board', '')}.json"
    if not manifest.is_file():
        return False
    return bool(json.loads(manifest.read_text()).get("espidf", {}).get("custom_sdkconfig"))


def core_key(platform):
    release = re.search(
        r"/pioarduino/platform-espressif32/releases/download/([^/]+)/", platform)
    if release:
        return f"pioarduino-{release.group(1)}"
    # Registry spec, URL or path. The digest keeps ranges (espressif32@^6.12.0)
    # and exact pins (espressif32@6.12.0) in different cores.
    name = platform.rstrip("/").split("?")[0].split("/")[-1]
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "platform"
    digest = hashlib.sha1(platform.encode()).hexdigest()[:8]
    return f"{name}-{digest}"


def core_dir(env, pio):
    options, project_options = project_config(env, pio)
    # pioarduino checks that the option is present, not that it has a value.
    if (any(name in options for name in CHECKOUT_CORE_OPTIONS)
            or any(name.startswith("board_espidf.") for name in options)
            or board_custom_sdkconfig(options, project_options)):
        return CHECKOUT_CORE
    platform = options.get("platform")
    if not platform:
        raise LookupError(f"[env:{env}] has no platform")
    return CORES / core_key(platform)


def main(argv):
    pio = "pio"
    if len(argv) >= 2 and argv[0] == "--pio":
        pio, argv = argv[1], argv[2:]
    if len(argv) != 1:
        print("usage: pio_core_dir.py [--pio PIO] ENV", file=sys.stderr)
        return 2
    try:
        print(core_dir(argv[0], pio))
    except Exception as exc:  # any failure must stop the build, not pick a core
        print(f"pio_core_dir: cannot choose the PlatformIO core for {argv[0]}: {exc}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
