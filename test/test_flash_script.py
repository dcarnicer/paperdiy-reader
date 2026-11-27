"""scripts/flash.sh builds, checks the board with esptool, then uploads."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FLASH = ROOT / "scripts" / "flash.sh"
BUILD = ROOT / "scripts" / "build.sh"
PORT = "/dev/cu.test-port"

ESPTOOL_16MB = """esptool v5.3.0
Connected to ESP32-S3 on /dev/cu.test-port:
Detected flash size: 16MB
Flash type set in eFuse: quad (4 data lines)
Flash voltage set by eFuse: 3.3V
"""

UPLOAD = ["run", "-e", "paperdiy", "-t", "upload", "--upload-port", PORT]


class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.calls = self.directory / "calls"
        # Every fake appends one line "<tool> <args>" to the same log.
        (self.directory / "pio").write_text('#!/bin/sh\necho "pio $*" >> "$CALLS"\n')
        (self.directory / "pio").chmod(0o755)

    def esptool(self, output, exit_code=0, later=""):
        """Fake esptool: prints `output`, then `later` after a pause."""
        (self.directory / "esptool-output").write_text(output)
        (self.directory / "esptool-later").write_text(later)
        script = self.directory / "esptool"
        script.write_text(
            "#!/bin/sh\n"
            'echo "esptool $*" >> "$CALLS"\n'
            f'cat "{self.directory / "esptool-output"}"\n'
            + ("sleep 0.3\n" if later else "")
            # Like esptool, fail when writing to a closed pipe.
            + f'cat "{self.directory / "esptool-later"}" || exit 1\n'
            f"exit {exit_code}\n")
        script.chmod(0o755)

    def run_script(self, script, *args):
        env = {
            **os.environ,
            "PATH": f"{self.directory}{os.pathsep}{os.environ['PATH']}",
            "CALLS": str(self.calls),
            "PLATFORMIO_CORE_DIR": str(self.directory / "core"),
        }
        env.pop("PAPERDIY_FLASH_LOCKED", None)
        return subprocess.run(["bash", str(script), *args], env=env,
                              capture_output=True, text=True)

    def logged(self):
        if not self.calls.exists():
            return []
        return [line.split() for line in self.calls.read_text().splitlines()]


class FlashScriptTest(ScriptTestCase):
    def test_builds_then_checks_then_uploads(self):
        self.esptool(ESPTOOL_16MB)
        result = self.run_script(FLASH, PORT)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.logged()
        self.assertEqual(calls[0], ["pio", "run", "-e", "paperdiy"])
        self.assertEqual(calls[1][0], "esptool")
        self.assertIn("no-reset", calls[1])
        self.assertEqual(calls[2], ["pio", *UPLOAD])
        self.assertEqual(len(calls), 3)

    def test_output_after_the_size_line_does_not_stop_the_script(self):
        # An `esptool | awk '... exit'` pipe broke here and, under pipefail,
        # the script exited non-zero without a message. The pause makes
        # esptool write again after such a reader would have exited.
        self.esptool(ESPTOOL_16MB, later="Leaving...\n" * 100)
        result = self.run_script(FLASH, PORT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.logged()[-1], ["pio", *UPLOAD])

    def test_esptool_failure_is_reported_and_nothing_is_uploaded(self):
        self.esptool("A fatal error occurred: Could not open /dev/cu.test-port\n", exit_code=2)
        result = self.run_script(FLASH, PORT)
        self.assertEqual(result.returncode, 1)
        self.assertIn("could not read the board", result.stderr)
        self.assertIn("Could not open", result.stderr)
        self.assertNotIn(["pio", *UPLOAD], self.logged())

    def test_other_flash_size_is_refused(self):
        self.esptool(ESPTOOL_16MB.replace("16MB", "8MB"))
        result = self.run_script(FLASH, PORT)
        self.assertEqual(result.returncode, 1)
        self.assertIn("detected flash size '8MB'", result.stderr)
        self.assertIn("download mode", result.stderr)
        self.assertNotIn(["pio", *UPLOAD], self.logged())

    def test_preset_lock_marker_does_not_skip_the_core_choice(self):
        # With PLATFORMIO_CORE_DIR unset the script must ask pio_core_dir.py
        # (the fake pio has no project config, so that fails) instead of
        # building with the global ~/.platformio.
        self.esptool(ESPTOOL_16MB)
        env = {
            **os.environ,
            "PATH": f"{self.directory}{os.pathsep}{os.environ['PATH']}",
            "CALLS": str(self.calls),
            "PAPERDIY_FLASH_LOCKED": "1",
        }
        env.pop("PLATFORMIO_CORE_DIR", None)
        result = subprocess.run(["bash", str(FLASH), PORT], env=env,
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(["pio", "run", "-e", "paperdiy"], self.logged())

    def test_core_lock_is_held_for_the_whole_run(self):
        self.esptool(ESPTOOL_16MB)
        result = self.run_script(FLASH, PORT)
        self.assertEqual(result.returncode, 0, result.stderr)
        lock = (self.directory / "core" / ".build.lock").read_text()
        self.assertIn("scripts/flash.sh", lock)


class BuildScriptTest(ScriptTestCase):
    def test_passes_arguments_to_pio(self):
        result = self.run_script(BUILD, "-t", "size")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.logged(), [["pio", "run", "-e", "paperdiy", "-t", "size"]])

    def test_refuses_the_serial_monitor(self):
        for args in (("-t", "upload", "-t", "monitor"), ("-tmonitor",), ("--target=monitor",)):
            with self.subTest(args=args):
                result = self.run_script(BUILD, *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("make monitor", result.stderr)
                self.assertEqual(self.logged(), [])


if __name__ == "__main__":
    unittest.main()
