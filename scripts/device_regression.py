#!/usr/bin/env python3
"""Deterministic PaperDIY device regression over the USB serial console.

Prerequisites:
  - `paperdiy-test` flashed (key injection is compiled out of production).
  - The device connected over USB, starting on Home (the script also tries to
    return there).
  - `tesseract` with the English model installed (`brew install tesseract`).
  - macOS `diskutil` for the USB mass-storage setup/teardown.

The script:
  1. Enters USB drive mode and backs up the user state it touches.
  2. Installs a deterministic EPUB and StarDict dictionary.
  3. Sets English UI, Lyra theme, dictionary and "sleep never" in settings.
  4. Runs a fixed key sequence and asserts expected text with OCR.
  5. Restores the backed-up files and removes the fixtures.

Artifacts and screenshots are written under build/device-regression/<run>/.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import paperdiy_serial as pd
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "build" / "device-regression" / "fixtures"
BASE_ARTIFACTS = ROOT / "build" / "device-regression"
SD_VOLUME_NAME = "DABI"
HOME_LABELS = ("Browse Files", "File Browser", "Explorador de archivos")
HOME_LABELS_LOWER = tuple(label.lower() for label in HOME_LABELS)
SETTINGS_PATH = ".crosspoint/settings.json"
RECENT_PATH = ".crosspoint/recent.json"
STATE_PATH = ".crosspoint/state.json"
KOREADER_PATH = ".crosspoint/koreader.json"
CLIPPINGS_PATH = "My Clippings.txt"
VOCABULARY_PATH = "Vocabulary.txt"
BACKUP_FILES = (SETTINGS_PATH, RECENT_PATH, STATE_PATH, KOREADER_PATH, CLIPPINGS_PATH, VOCABULARY_PATH)


class RegressionError(RuntimeError):
    pass


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def edit_distance(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, 1):
        current = [i]
        for j, char_right in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (char_left != char_right),
            ))
        previous = current
    return previous[-1]


def matches_alias(text: str, alias: str) -> bool:
    text = normalize(text)
    alias = normalize(alias)
    if alias in text:
        return True
    compact_text = re.sub(r"[^a-z0-9]", "", text)
    compact_alias = re.sub(r"[^a-z0-9]", "", alias)
    if compact_alias and compact_alias in compact_text:
        return True
    if compact_alias and edit_distance(compact_text, compact_alias) <= 1:
        return True
    words = re.findall(r"[a-z0-9]+", text)
    alias_words = re.findall(r"[a-z0-9]+", alias)
    if not alias_words:
        return False
    allowed = lambda word: 1 if len(word) >= 3 else 0
    return all(any(edit_distance(word, alias_word) <= allowed(alias_word) for word in words) for alias_word in alias_words)


def require_tools() -> None:
    if shutil.which("tesseract") is None:
        raise RegressionError("tesseract no está instalado; hace falta para las aserciones OCR")
    if shutil.which("diskutil") is None:
        raise RegressionError("diskutil no está disponible; este runner es para macOS")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, capture_output=True, **kwargs)


class Device:
    def __init__(self, port: str | None, artifacts: Path) -> None:
        self.port = port or pd.find_port()
        self.fd = pd.open_port(self.port, 115200)
        self.reader = pd.SerialReader(self.fd)
        self.artifacts = artifacts

    def close(self) -> None:
        try:
            os.close(self.fd)
        except OSError:
            pass

    def reopen(self, timeout: float = 30.0) -> None:
        self.close()
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                self.port = pd.find_port()
                self.fd = pd.open_port(self.port, 115200)
                self.reader = pd.SerialReader(self.fd)
                return
            except (OSError, SystemExit):
                time.sleep(0.5)
        raise RegressionError("el puerto serie no reappeared después de expulsar la SD")

    def key(self, name: str, retry: int = 4, settle: float = 0.7) -> bool:
        args = SimpleNamespace(key=name, retry=retry, settle=settle, timeout=10.0)
        try:
            pd.key(args, self.fd, self.reader)
            return True
        except (SystemExit, pd.SerialTimeout):
            return False

    def probe_test_build(self) -> bool:
        args = SimpleNamespace(key="A", retry=0, settle=0.0, timeout=2.0)
        try:
            pd.key(args, self.fd, self.reader)
            return True
        except (SystemExit, pd.SerialTimeout):
            return False

    def screenshot(self, name: str, rotate: int = 90) -> Path:
        path = self.artifacts / f"{name}.png"
        args = SimpleNamespace(
            output=str(path),
            raw=None,
            width=pd.DEFAULT_WIDTH,
            height=pd.DEFAULT_HEIGHT,
            rotate=rotate,
            no_rotate=False,
            invert=False,
            timeout=35.0,
        )
        pd.screenshot(args, self.fd, self.reader)
        return path

    def ocr(self, path: Path) -> str:
        result = run(["tesseract", str(path), "stdout", "-l", "eng", "--psm", "6"])
        if result.returncode != 0:
            raise RegressionError(f"tesseract falló con {path}: {result.stderr.strip()}")
        return result.stdout

    def ocr_lines(self, path: Path) -> list[dict]:
        result = run(["tesseract", str(path), "stdout", "-l", "eng", "--psm", "6", "tsv"])
        if result.returncode != 0:
            raise RegressionError(f"tesseract TSV falló con {path}: {result.stderr.strip()}")
        groups: dict[tuple[str, str, str], list[tuple[int, int, int, int, str]]] = {}
        for line in result.stdout.splitlines()[1:]:
            fields = line.split("\t")
            if len(fields) < 12 or not fields[11].strip():
                continue
            key = (fields[2], fields[3], fields[4])
            groups.setdefault(key, []).append(
                (int(fields[6] or 0), int(fields[7] or 0), int(fields[8] or 0), int(fields[9] or 0), fields[11].strip())
            )
        lines = []
        for words in groups.values():
            left = min(word[0] for word in words)
            top = min(word[1] for word in words)
            right = max(word[0] + word[2] for word in words)
            bottom = max(word[1] + word[3] for word in words)
            text = " ".join(word[4] for word in words)
            lines.append({"text": text, "left": left, "top": top, "right": right, "bottom": bottom})
        return sorted(lines, key=lambda item: item["top"])

    def wait_text(self, name: str, expected: tuple[str, ...], timeout: float = 45.0) -> str:
        needles = tuple(item.lower() for item in expected)
        deadline = time.time() + timeout
        last_text = ""
        while time.time() < deadline:
            try:
                path = self.screenshot(name)
                last_text = self.ocr(path)
            except pd.SerialTimeout:
                time.sleep(1.0)
                continue
            normalized = normalize(last_text)
            if any(needle in normalized for needle in needles):
                return last_text
            time.sleep(1.0)
        raise RegressionError(f"{name}: no encontré {expected!r}. OCR: {normalize(last_text)[:400]!r}")


def home_screen(dev: Device) -> bool:
    path = dev.screenshot("00-home")
    text = normalize(dev.ocr(path))
    return any(label in text for label in HOME_LABELS_LOWER)


HOME_ORDER = [
    ("file-browser", ("browse files", "file browser", "explorador de archivos", "explorador")),
    ("library", ("library", "biblioteca")),
    ("opds", ("opds browser", "navegador opds", "plugins", "complementos")),
    ("file-transfer", ("file transfer", "transferir archivos")),
    ("settings", ("settings", "ajustes")),
]
NETWORK_ORDER = [
    ("join", ("join network", "unirse a una red")),
    ("calibre", ("calibre wireless", "calibre inalámbrico", "calibre inalambrico")),
    ("hotspot", ("create hotspot", "crear punto de acceso")),
    ("usb", ("usb drive", "unidad usb")),
]
READER_MENU_ORDER = [
    ("clippings", ("view clippings", "ver recortes")),
    ("toc", ("select chapter", "seleccionar capítulo", "seleccionar capitulo")),
    ("links", ("links and footnotes", "enlaces y notas al pie")),
    ("bookmark", ("toggle bookmark", "alternar marcador")),
    ("clip", ("create clipping", "crear recorte")),
    ("night", ("night mode", "modo nocturno")),
    ("lookup", ("look up", "buscar palabra")),
    ("orientation", ("orientation", "orientación", "orientacion")),
    ("percent", ("go to percent", "ir a %")),
    ("screenshot", ("screenshot", "captura")),
    ("qr", ("show page as qr", "código qr", "codigo qr")),
    ("home", ("go home", "volver al menú inicio", "volver al menu inicio")),
    ("cache", ("delete cache", "borrar caché", "borrar cache")),
    ("text", ("text settings", "ajustes de texto")),
]


def go_home(dev: Device, attempts: int = 12) -> None:
    for _ in range(attempts):
        if home_screen(dev):
            return
        dev.key("A_LONG", retry=1, settle=0.8)
        time.sleep(0.8)
    raise RegressionError("no pude volver a Home")


def highlighted_ratio(path: Path, line: dict) -> float:
    image = Image.open(path).convert("L")
    top = max(0, line["top"] - 6)
    bottom = min(image.height, line["bottom"] + 6)
    band = image.crop((10, top, image.width - 10, bottom))
    pixels = band.tobytes()
    return sum(1 for pixel in pixels if pixel < 128) / max(1, len(pixels))


def select_item(dev: Device, order: list[tuple[str, tuple[str, ...]]], target: str, name: str,
                max_steps: int = 14) -> str:
    """Move the menu/list selection to `target` by reading the highlighted row.

    The order of visible rows is derived from OCR positions, so dynamic menus
    (Links and Footnotes present or absent, dictionary configured or not) and
    optional rows do not shift the key count.
    """
    keys = [key for key, _ in order]
    if target not in keys:
        raise RegressionError(f"target {target!r} no está en el orden del menú")
    last_text = ""
    for step in range(max_steps):
        path = dev.screenshot(f"{name}-{step:02d}")
        lines = dev.ocr_lines(path)
        last_text = normalize(" ".join(line["text"] for line in lines))
        matches = []
        for key, aliases in order:
            candidates = []
            for line in lines:
                if any(matches_alias(line["text"], alias) for alias in aliases):
                    candidates.append((line, highlighted_ratio(path, line)))
            if candidates:
                # Prefer the highlighted occurrence for a selected row; for an
                # unselected row the topmost occurrence is the list entry.
                line, ratio = max(candidates, key=lambda item: item[1])
                matches.append((key, line, ratio))
        matches.sort(key=lambda item: item[1]["top"])
        if not matches:
            raise RegressionError(f"{name}: no encontré entradas conocidas. OCR: {last_text[:400]!r}")
        selected = max(matches, key=lambda item: item[2])
        if selected[2] < 0.15:
            # Nothing highlighted: on Home the cover is selected; one B enters
            # the menu. On a list the first row should be highlighted already.
            dev.key("B", retry=2, settle=0.9)
            continue
        keys_visible = [key for key, _, _ in matches]
        if selected[0] == target:
            return last_text
        if target not in keys_visible:
            raise RegressionError(f"{name}: {target!r} no está visible. OCR: {last_text[:400]!r}")
        target_index = keys_visible.index(target)
        selected_index = keys_visible.index(selected[0])
        dev.key("A" if target_index < selected_index else "B", retry=2, settle=0.9)
    raise RegressionError(f"{name}: no llegué a {target!r}. OCR: {last_text[:400]!r}")


def find_sd_device() -> str | None:
    result = run(["diskutil", "list"])
    for line in result.stdout.splitlines():
        if SD_VOLUME_NAME in line:
            match = re.search(r"\b(disk\d+s\d+)\b", line)
            if match:
                return match.group(1)
    return None


def wait_for_serial(timeout: float = 40.0) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            return pd.find_port()
        except SystemExit:
            time.sleep(0.5)
    raise RegressionError("no apareció el puerto serie; ¿está encendido el PaperDIY?")


def recover_sd() -> None:
    """Eject a stale USB-drive session left by a failed run."""
    device = find_sd_device()
    if device is None:
        return
    run(["diskutil", "unmount", "force", device])
    run(["diskutil", "eject", device])
    time.sleep(2)
    wait_for_serial(40)


def mount_sd() -> tuple[Path, str]:
    deadline = time.time() + 40
    device = None
    while time.time() < deadline:
        device = find_sd_device()
        if device is not None:
            break
        time.sleep(0.5)
    if device is None:
        raise RegressionError(f"no apareció el volumen {SD_VOLUME_NAME}; ¿está activo USB MSC?")
    # Force a clean mount at the standard location. Reusing a stale
    # /Volumes/DABI directory previously produced EACCES on writes.
    run(["diskutil", "unmount", "force", device])
    result = run(["diskutil", "mount", device])
    if result.returncode != 0:
        raise RegressionError(f"diskutil mount falló: {result.stderr.strip()}")
    info = run(["diskutil", "info", device]).stdout
    match = re.search(r"Mount Point:\s*(.+)", info)
    if not match or match.group(1).strip() == "Not mounted":
        raise RegressionError(f"no pude obtener el punto de montaje de {device}")
    mount_point = Path(match.group(1).strip())
    probe = mount_point / ".pd-write-test"
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return mount_point, device
        except OSError:
            time.sleep(0.5)
    raise RegressionError(f"{mount_point} no es escribible; revisa permisos/montaje de {SD_VOLUME_NAME}")


def select_text(dev: Device, target_aliases: tuple[str, ...], name: str, max_steps: int = 14) -> str:
    """Select the row whose text matches `target_aliases` in an arbitrary list."""
    aliases = tuple(alias.lower() for alias in target_aliases)
    last_text = ""
    for step in range(max_steps):
        path = dev.screenshot(f"{name}-{step:02d}")
        lines = dev.ocr_lines(path)
        last_text = normalize(" ".join(line["text"] for line in lines))
        target_lines = [line for line in lines if any(matches_alias(line["text"], alias) for alias in aliases)]
        scored = sorted(
            ((highlighted_ratio(path, line), line) for line in lines),
            key=lambda item: item[0],
            reverse=True,
        )
        selected = scored[0] if scored and scored[0][0] >= 0.15 else None
        if target_lines and selected is not None:
            target = target_lines[0]
            if any(matches_alias(selected[1]["text"], alias) for alias in aliases):
                return last_text
            dev.key("A" if target["top"] < selected[1]["top"] else "B", retry=2, settle=0.9)
            continue
        # No target on screen or no highlighted row: advance one row and retry.
        dev.key("B", retry=2, settle=0.9)
    raise RegressionError(f"{name}: no encontré {target_aliases!r}. OCR: {last_text[:400]!r}")


def enter_usb_mode(dev: Device) -> tuple[Path, str]:
    go_home(dev)
    select_item(dev, HOME_ORDER, "file-transfer", "01-home-nav")
    dev.key("B_LONG")
    dev.wait_text("02-transfer-menu", ("Join Network", "Unirse a una red", "Calibre"), timeout=15)
    select_item(dev, NETWORK_ORDER, "usb", "03-network-nav")
    dev.key("B_LONG")
    return mount_sd()


def eject(dev: Device, device: str) -> None:
    dev.close()
    # Spotlight (mdsync) can dissent a normal eject. Force-unmount first, then
    # eject to make the reader leave USB-drive mode.
    run(["diskutil", "unmount", "force", device])
    run(["diskutil", "eject", device])
    dev.reopen()
    go_home(dev)


def copy_into(backup: Path, mount: Path) -> None:
    manifest = {}
    for name in BACKUP_FILES:
        src = mount / name
        if src.exists():
            dst = backup / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            manifest[name] = True
        else:
            manifest[name] = False
    (backup / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def restore_from(backup: Path, mount: Path) -> None:
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    for name, existed in manifest.items():
        src = backup / name
        dst = mount / name
        if existed and src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif not existed and dst.exists():
            dst.unlink()


def prepare(dev: Device, artifacts: Path, run_id: str) -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_device_smoke_fixtures.py")], check=True)
    mount, sd_device = enter_usb_mode(dev)
    backup = artifacts / "backup"
    backup.mkdir(parents=True, exist_ok=True)
    copy_into(backup, mount)

    smoke_dir = mount / "SmokeTest"
    if smoke_dir.exists():
        shutil.rmtree(smoke_dir)
    smoke_dir.mkdir()
    smoke_name = f"paperdiy-smoke-{run_id}.epub"
    shutil.copy2(FIXTURES / "paperdiy-smoke.epub", smoke_dir / smoke_name)

    dict_dir = mount / "dictionaries" / "smoke"
    if dict_dir.exists():
        shutil.rmtree(dict_dir)
    dict_dir.mkdir(parents=True)
    for name in ("smoke.ifo", "smoke.idx", "smoke.dict"):
        shutil.copy2(FIXTURES / "dictionaries" / "smoke" / name, dict_dir / name)

    (mount / ".crosspoint").mkdir(exist_ok=True)
    settings_path = mount / SETTINGS_PATH
    settings = {}
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    settings.update(
        {
            "language": "EN",
            "uiTheme": 1,
            "dictionaryName": "smoke",
            "sleepTimeoutMinutes": 31,
            "showHiddenFiles": 0,
        }
    )
    settings_path.write_text(json.dumps(settings, ensure_ascii=False), encoding="utf-8")

    recent = {
        "books": [
            {
                "path": f"/SmokeTest/{smoke_name}",
                "title": "PaperDIY Smoke Test",
                "author": "PaperDIY",
                "coverBmpPath": "",
            }
        ]
    }
    (mount / RECENT_PATH).write_text(json.dumps(recent), encoding="utf-8")

    state_path = mount / STATE_PATH
    state = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    state["openEpubPath"] = ""
    state_path.write_text(json.dumps(state), encoding="utf-8")

    cache_before = {path.name for path in (mount / ".crosspoint").glob("epub_*") if path.is_dir()}
    (artifacts / "cache-before.json").write_text(json.dumps(sorted(cache_before)), encoding="utf-8")

    eject(dev, sd_device)


def restore_files(mount: Path, artifacts: Path) -> None:
    for path in (mount / "SmokeTest", mount / "dictionaries" / "smoke"):
        if path.exists():
            shutil.rmtree(path)
    dictionaries = mount / "dictionaries"
    if dictionaries.is_dir() and not any(dictionaries.iterdir()):
        dictionaries.rmdir()

    cache_file = artifacts / "cache-before.json"
    if cache_file.exists():
        cache_before = set(json.loads(cache_file.read_text(encoding="utf-8")))
        crosspoint = mount / ".crosspoint"
        for path in crosspoint.glob("epub_*"):
            if path.is_dir() and path.name not in cache_before:
                shutil.rmtree(path)

    restore_from(artifacts / "backup", mount)


def teardown(dev: Device, artifacts: Path) -> None:
    mount, sd_device = enter_usb_mode(dev)
    restore_files(mount, artifacts)
    eject(dev, sd_device)


def restore_without_eject(dev: Device, artifacts: Path) -> str:
    """Restore files and leave the reader in USB mode for a power cycle.

    The firmware saves its in-memory settings when it leaves USB-drive mode, so
    restoring and ejecting can be overwritten. Unmount the host side and ask
    the human to power-cycle instead.
    """
    mount, sd_device = enter_usb_mode(dev)
    restore_files(mount, artifacts)
    run(["diskutil", "unmount", "force", sd_device])
    dev.close()
    return sd_device


TOC_ORDER = [
    ("chapter-one", ("chapter one",)),
    ("chapter-two", ("chapter two",)),
]
def scenario_core(dev: Device) -> dict:
    results: list[dict] = []

    def step(name: str, expected: tuple[str, ...], action) -> None:
        if action is not None:
            action()
        text = dev.wait_text(name, expected)
        results.append({"name": name, "ok": True, "ocr": normalize(text)[:300]})

    def open_menu(name: str) -> None:
        dev.key("B_LONG")
        step(name, ("Select Chapter", "Seleccionar capítulo", "Seleccionar capitulo"), lambda: None)

    go_home(dev)
    step("10-browser", ("SD Card", "Tarjeta SD", "SmokeTest"),
         lambda: (select_item(dev, HOME_ORDER, "file-browser", "10-home"), dev.key("B_LONG")))
    step("11-smoke-folder", ("paperdiy-smoke", "paperdiy smoke", "SMOKE"),
         lambda: (select_text(dev, ("smoke", "smoketest", "smoke test"), "11-folder"), dev.key("B_LONG")))
    step("12-reader-open", ("Chapter One", "SMOKE PAGE ONE"),
         lambda: (select_text(dev, ("paperdiy-smoke", "paperdiy smoke"), "12-file"), dev.key("B_LONG")))
    step("11-page-two", ("SMOKE PAGE TWO",), lambda: dev.key("B"))
    step("12-page-one", ("SMOKE PAGE ONE",), lambda: dev.key("A"))
    open_menu("13-menu")
    step("14-toc-nav", ("Select Chapter", "Seleccionar capítulo", "Seleccionar capitulo"),
         lambda: select_item(dev, READER_MENU_ORDER, "toc", "14-menu"))
    step("15-toc", ("Chapter One", "Chapter Two"), lambda: dev.key("B_LONG"))
    step("16-toc-target", ("SMOKE CHAPTER TWO",),
         lambda: (select_item(dev, TOC_ORDER, "chapter-two", "16-toc-nav"), dev.key("B_LONG")))
    open_menu("17-menu")
    step("18-toc-back-nav", ("Select Chapter", "Seleccionar capítulo", "Seleccionar capitulo"),
         lambda: select_item(dev, READER_MENU_ORDER, "toc", "18-menu"))
    step("19-toc-back", ("Chapter One", "Chapter Two"), lambda: dev.key("B_LONG"))
    step("20-toc-back-target", ("SMOKE PAGE ONE", "Chapter One"),
         lambda: (select_item(dev, TOC_ORDER, "chapter-one", "20-toc-nav"), dev.key("B_LONG")))
    open_menu("21-menu")
    step("22-links-nav", ("Links and Footnotes", "Enlaces y notas al pie", "link to chapter two"),
         lambda: select_item(dev, READER_MENU_ORDER, "links", "22-menu"))
    step("23-links", ("link to chapter two", "SMOKE FOOTNOTE"), lambda: dev.key("B_LONG"))
    step("24-link-target", ("SMOKE CHAPTER TWO",), lambda: dev.key("B_LONG"))
    open_menu("25-menu")
    step("26-clip-nav", ("Create Clipping", "Crear recorte", "SMOKE"),
         lambda: select_item(dev, READER_MENU_ORDER, "clip", "26-menu"))
    step("27-clip-select", ("Select", "SMOKE", "Clip"), lambda: dev.key("B_LONG"))
    # Saving a clipping needs two confirms in the selection activity; serial
    # injection does not deliver them reliably. Validate entry/cancel here and
    # leave the save for the physical-button pass.
    step("28-clip-cancel", ("Chapter Two", "SMOKE"), lambda: (time.sleep(1.0), dev.key("A_LONG", settle=1.0)))
    open_menu("30-menu")
    step("31-lookup-nav", ("Look Up", "Buscar palabra", "SMOKEDEF"),
         lambda: select_item(dev, READER_MENU_ORDER, "lookup", "31-menu"))
    step("32-lookup-select", ("Select", "SMOKEDEF", "Look Up"), lambda: dev.key("B_LONG"))

    def confirm_lookup() -> None:
        for _ in range(4):
            dev.key("B_LONG", settle=1.0)
            time.sleep(0.5)
            if "smokedef" in normalize(dev.ocr(dev.screenshot("33-lookup-check"))):
                return
        raise RegressionError("lookup no mostró SMOKEDEF")

    step("33-lookup-result", ("SMOKEDEF",), confirm_lookup)
    go_home(dev)
    return {"steps": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic PaperDIY device regression")
    parser.add_argument("--port")
    parser.add_argument("--scenario", choices=("core",), default="core")
    parser.add_argument("--skip-prepare", action="store_true", help="usar los fixtures ya instalados")
    parser.add_argument("--no-restore", action="store_true", help="no restaurar el estado del usuario")
    parser.add_argument("--restore-only", type=Path, help="restaurar el backup de un directorio de artifacts")
    parser.add_argument("--restore-hold", type=Path,
                        help="restaurar y dejar el equipo en USB para un ciclo de power")
    parser.add_argument("--eject", action="store_true",
                        help="expulsar al terminar en vez de dejar el equipo para un ciclo de power")
    args = parser.parse_args()

    require_tools()
    run_id = time.strftime("%Y%m%d-%H%M%S")
    artifacts = BASE_ARTIFACTS / run_id
    artifacts.mkdir(parents=True, exist_ok=True)
    dev: Device | None = None
    report = {"run": run_id, "ok": False, "scenario": args.scenario, "steps": []}
    try:
        recover_sd()
        if args.restore_only or args.restore_hold:
            source = args.restore_only or args.restore_hold
            artifacts = source
            dev = Device(args.port, artifacts)
            if not dev.probe_test_build():
                raise RegressionError("paperdiy-test no responde a CMD:KEY; flashea ese entorno")
            if args.restore_hold:
                device = restore_without_eject(dev, artifacts)
                report["ok"] = True
                report["restore_hold"] = str(source)
                print(f"RESTORED-AND-HELD {artifacts} on {device}; power-cycle the reader now")
            else:
                teardown(dev, artifacts)
                report["ok"] = True
                report["restored"] = str(source)
                print(f"RESTORED {artifacts}")
            return 0
        dev = Device(args.port, artifacts)
        if not dev.probe_test_build():
            raise RegressionError("paperdiy-test no responde a CMD:KEY; flashea ese entorno")
        if not args.skip_prepare:
            prepare(dev, artifacts, run_id)
        if args.scenario == "core":
            report.update(scenario_core(dev))
        report["ok"] = True
        print(f"PASS {args.scenario}: {len(report['steps'])} pasos")
        return 0
    except Exception as exc:  # keep the report and screenshots for diagnosis
        report["error"] = str(exc)
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        (artifacts / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        if dev is not None and not args.no_restore and not args.restore_only and not args.restore_hold:
            try:
                recover_sd()
                dev.reopen()
            except Exception:
                pass
            try:
                if args.eject:
                    teardown(dev, artifacts)
                else:
                    device = restore_without_eject(dev, artifacts)
                    print(f"RESTORED-AND-HELD on {device}; power-cycle the reader to load the original state")
            except Exception as exc:
                print(f"WARN: teardown incompleto: {exc}", file=sys.stderr)
        if dev is not None:
            dev.close()


if __name__ == "__main__":
    raise SystemExit(main())
