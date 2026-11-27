"""The M5Burner LICENSE reads the packages of the core the firmware was linked with."""

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "make_m5burner_package",
    Path(__file__).resolve().parents[1] / "scripts/make_m5burner_package.py",
)
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class PackagesDirTest(unittest.TestCase):
    def test_exported_core_wins(self):
        with patch.dict(os.environ, {"PLATFORMIO_CORE_DIR": "/cores/explicit"}):
            self.assertEqual(packager.packages_dir(), Path("/cores/explicit/packages"))

    def test_without_variable_uses_the_paperdiy_core(self):
        done = subprocess.CompletedProcess([], 0, stdout="/cores/pioarduino-55.03.311\n", stderr="")
        with patch.dict(os.environ, {"PLATFORMIO_CORE_DIR": ""}), \
                patch.object(packager.subprocess, "run", return_value=done) as run:
            self.assertEqual(packager.packages_dir(),
                             Path("/cores/pioarduino-55.03.311/packages"))
        self.assertIn("paperdiy", run.call_args.args[0])

    def test_unresolved_core_stops_instead_of_reading_the_global_one(self):
        failed = subprocess.CompletedProcess([], 1, stdout="", stderr="pio_core_dir: cannot choose")
        with patch.dict(os.environ, {"PLATFORMIO_CORE_DIR": ""}), \
                patch.object(packager.subprocess, "run", return_value=failed):
            with self.assertRaises(SystemExit) as stop:
                packager.packages_dir()
        self.assertIn("cannot choose", str(stop.exception))

    def test_leading_tilde_is_expanded(self):
        with patch.dict(os.environ, {"PLATFORMIO_CORE_DIR": "~/cores/x"}):
            self.assertEqual(packager.packages_dir(), Path.home() / "cores/x/packages")


class LinkedCoreTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.build = Path(temporary.name)
        self.packages = Path("/cores/pioarduino-55.03.311/packages")

    def test_firmware_linked_against_the_core_passes(self):
        (self.build / "firmware.map").write_text(
            f" {self.packages}/framework-arduinoespressif32-libs/esp32s3/lib/libfoo.a(x.o)\n")
        packager.check_linked_core(self.build, self.packages)

    def test_firmware_linked_against_another_core_is_refused(self):
        (self.build / "firmware.map").write_text(
            " /elsewhere/packages/framework-arduinoespressif32-libs/esp32s3/lib/libfoo.a(x.o)\n")
        with self.assertRaises(SystemExit) as stop:
            packager.check_linked_core(self.build, self.packages)
        self.assertIn("PLATFORMIO_CORE_DIR", str(stop.exception))

    def test_missing_map_is_refused(self):
        with self.assertRaises(SystemExit):
            packager.check_linked_core(self.build, self.packages)


if __name__ == "__main__":
    unittest.main()
