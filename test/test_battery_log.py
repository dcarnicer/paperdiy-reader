"""Battery CSV parsing, rate math and curve ordering."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("battery_log", ROOT / "scripts/battery_log.py")
battery_log = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = battery_log
spec.loader.exec_module(battery_log)

HEADER = (
    "# battery-log v1 board=paperdiy fw=test\n"
    "epoch,uptime_s,event,mv,pct,chg,usb,reader,wifi,vin_mv,vout_mv,pwr_src\n"
)
HEADER_V2 = (
    "# battery-log v2 board=paperdiy fw=test\n"
    "epoch,uptime_s,event,mv,pct,chg,usb,reader,wifi,vin_mv,vout_mv,pwr_src,pages\n"
)
ROWS = (
    "1763000000,0,boot,4180,100,0,0,0,0,-1,-1,-1\n"
    "1763003600,3600,periodic,4100,90,0,0,1,0,-1,-1,-1\n"
    "1763007200,7200,periodic,4000,80,0,0,1,0,-1,-1,-1\n"
    "1763014400,14400,periodic,3900,60,0,0,1,0,-1,-1,-1\n"
    "1763018000,18000,periodic,3800,50,0,0,1,0,-1,-1,-1\n"
    "1763025200,25200,periodic,3700,30,0,0,1,0,-1,-1,-1\n"
    "1763032400,32400,periodic,3500,10,0,0,1,0,-1,-1,-1\n"
    "1763036000,36000,sleep,3400,0,0,0,0,0,-1,-1,-1\n"
)


class BatteryLogTest(unittest.TestCase):
    def write_log(self, body: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "battery-log.csv"
        path.write_text(body, encoding="utf-8")
        return path

    def test_parses_meta_and_rows(self):
        samples, meta = battery_log.read_samples(self.write_log(HEADER + ROWS))
        self.assertIn("board=paperdiy", meta)
        self.assertEqual(len(samples), 8)
        self.assertEqual(samples[0].event, "boot")
        self.assertEqual(samples[-1].mv, 3400)
        self.assertTrue(samples[0].known_clock)

    def test_missing_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing CSV columns"):
            battery_log.read_samples(self.write_log("# meta\nepoch,uptime_s\n0,0\n"))

    def test_v2_page_counter_is_optional(self):
        rows = (
            "1763000000,0,boot,4180,100,0,0,0,0,-1,-1,-1,0\n"
            "1763000300,300,periodic,4170,100,0,0,1,0,-1,-1,-1,12\n"
        )
        samples, _ = battery_log.read_samples(self.write_log(HEADER_V2 + rows))
        self.assertEqual(samples[0].pages, 0)
        self.assertEqual(samples[1].pages, 12)

    def test_rates_and_full_cycle(self):
        samples, _ = battery_log.read_samples(self.write_log(HEADER + ROWS))
        pairs = battery_log.discharge_pairs(samples, 7200)
        self.assertEqual(len(pairs), 7)

        cycle = battery_log.find_full_cycle(samples)
        self.assertIsNotNone(cycle)
        start, end = cycle
        self.assertEqual((start.pct, end.pct), (100, 0))
        hours = (end.epoch - start.epoch) / 3600.0
        self.assertAlmostEqual(1500 / hours, 150.0, places=1)

    def test_curve_is_ordered_from_empty_to_full(self):
        samples, _ = battery_log.read_samples(self.write_log(HEADER + ROWS))
        curve = battery_log.suggest_curve(samples)
        self.assertIsNotNone(curve)
        self.assertEqual(len(curve), 11)
        self.assertLess(curve[0], curve[-1])
        self.assertLessEqual(curve[0], 3500)
        self.assertGreaterEqual(curve[-1], 4100)


if __name__ == "__main__":
    unittest.main()
