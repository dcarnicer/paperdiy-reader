"""scripts/pio_lock.py serializes builds that share a PlatformIO core."""

import fcntl
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
import time
import unittest


LOCK = Path(__file__).resolve().parents[1] / "scripts" / "pio_lock.py"


class PioLockTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name).resolve()
        self.core = self.directory / "core"
        self.env = {**os.environ, "PLATFORMIO_CORE_DIR": str(self.core)}

    def run_lock(self, *command, env=None, cwd=None):
        return subprocess.run([sys.executable, str(LOCK), *command], env=env or self.env,
                              cwd=cwd, capture_output=True, text=True)

    def test_returns_the_command_exit_code(self):
        result = self.run_lock("sh", "-c", "exit 3")
        self.assertEqual(result.returncode, 3)
        self.assertIn("sh -c exit 3", (self.core / ".build.lock").read_text())

    def test_command_holds_the_lock_while_it_runs(self):
        probe = (
            "import fcntl, os, sys\n"
            "fd = os.open(sys.argv[1], os.O_RDWR)\n"
            "try:\n"
            "    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
            "    print('free')\n"
            "except BlockingIOError:\n"
            "    print('held')\n"
        )
        result = self.run_lock(sys.executable, "-c", probe, str(self.core / ".build.lock"))
        self.assertEqual(result.stdout.strip(), "held", result.stderr)

    def test_second_build_waits_for_the_first_and_names_the_holder(self):
        self.core.mkdir(parents=True)
        fd = os.open(self.core / ".build.lock", os.O_RDWR | os.O_CREAT)
        self.addCleanup(os.close, fd)
        fcntl.flock(fd, fcntl.LOCK_EX)
        os.write(fd, b"pid 1234: pio run -e paperdiy\n")
        waiting = subprocess.Popen([sys.executable, str(LOCK), "sh", "-c", "echo ran"],
                                   env=self.env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        self.addCleanup(waiting.kill)
        # Wait for the "waiting" line instead of a fixed delay.
        selector = selectors.DefaultSelector()
        selector.register(waiting.stderr, selectors.EVENT_READ)
        line, deadline = "", time.monotonic() + 10
        while "waiting" not in line and time.monotonic() < deadline:
            if selector.select(timeout=0.5):
                line = waiting.stderr.readline()
        self.assertIn("waiting for another build", line)
        self.assertIn("pid 1234: pio run -e paperdiy", line)
        self.assertIsNone(waiting.poll(), "the second build did not wait")
        fcntl.flock(fd, fcntl.LOCK_UN)
        out, _ = waiting.communicate(timeout=10)
        self.assertEqual(waiting.returncode, 0)
        self.assertEqual(out.strip(), "ran")

    def test_leading_tilde_is_expanded_like_platformio(self):
        env = {**self.env, "HOME": str(self.directory), "PLATFORMIO_CORE_DIR": "~/cores/x"}
        work = self.directory / "checkout"
        work.mkdir()
        result = self.run_lock("true", env=env, cwd=work)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.directory / "cores" / "x" / ".build.lock").is_file())
        self.assertFalse((work / "~").exists())

    def test_without_fcntl_runs_unlocked_with_a_warning(self):
        runner = (
            "import runpy, sys\n"
            "sys.modules['fcntl'] = None\n"
            "sys.argv = [sys.argv[1], 'sh', '-c', 'exit 0']\n"
            "runpy.run_path(sys.argv[0], run_name='__main__')\n"
        )
        result = subprocess.run([sys.executable, "-c", runner, str(LOCK)],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("without the core lock", result.stderr)
        self.assertFalse((self.core / ".build.lock").exists())

    def test_missing_core_variable_fails(self):
        env = {k: v for k, v in self.env.items() if k != "PLATFORMIO_CORE_DIR"}
        result = self.run_lock("true", env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("PLATFORMIO_CORE_DIR", result.stderr)

    def test_missing_command_fails(self):
        result = self.run_lock("/no/such/command")
        self.assertEqual(result.returncode, 127)


if __name__ == "__main__":
    unittest.main()
