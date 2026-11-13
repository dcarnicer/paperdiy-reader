#!/usr/bin/env python3
"""Summarize the device's /battery-log.csv.

The firmware has no current sensor, so this script works with voltage, the
voltage-derived percentage, charge/USB state and timestamps. It reports:

  * the voltage range and charge/USB transitions
  * discharge rates in mV/h and %/h for trusted-time samples
  * optional average-current/runtime estimates from a known cell capacity
  * an optional time-based 11-point voltage curve for a full discharge

Examples:
    python3 scripts/battery_log.py battery-log.csv
    python3 scripts/battery_log.py battery-log.csv --capacity 1500
    python3 scripts/battery_log.py battery-log.csv --curve

Timestamps come from trustedtime: epoch is 0 until the clock has been set by
an RTC or NTP. Rows with epoch 0 are still useful within one boot (uptime_s),
but they cannot measure time spent powered off.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

FIELDS = (
    "epoch",
    "uptime_s",
    "event",
    "mv",
    "pct",
    "chg",
    "usb",
    "reader",
    "wifi",
    "vin_mv",
    "vout_mv",
    "pwr_src",
)


@dataclass
class Sample:
    epoch: int | None
    uptime_s: int | None
    event: str
    mv: int | None
    pct: int | None
    chg: int | None
    usb: int | None
    reader: int | None
    wifi: int | None
    vin_mv: int | None
    vout_mv: int | None
    pwr_src: int | None
    pages: int | None
    line: int

    @property
    def known_clock(self) -> bool:
        return self.epoch is not None and self.epoch > 0


def int_or_none(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        number = int(value)
    except ValueError:
        return None
    return None if number < 0 else number


def read_samples(path: Path) -> tuple[list[Sample], str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        lines = handle.readlines()

    meta = ""
    header = None
    rows: list[dict[str, str]] = []
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            if not meta:
                meta = stripped.lstrip("#").strip()
            continue
        if header is None:
            header = next(csv.reader([stripped]))
            missing = [field for field in FIELDS if field not in header]
            if missing:
                raise ValueError(f"missing CSV columns: {', '.join(missing)}")
            continue
        values = next(csv.reader([stripped]))
        if len(values) != len(header):
            continue
        rows.append(dict(zip(header, values)))

    samples = []
    for number, row in enumerate(rows, start=2):
        samples.append(
            Sample(
                epoch=int_or_none(row.get("epoch")),
                uptime_s=int_or_none(row.get("uptime_s")),
                event=(row.get("event") or "?"),
                mv=int_or_none(row.get("mv")),
                pct=int_or_none(row.get("pct")),
                chg=int_or_none(row.get("chg")),
                usb=int_or_none(row.get("usb")),
                reader=int_or_none(row.get("reader")),
                wifi=int_or_none(row.get("wifi")),
                vin_mv=int_or_none(row.get("vin_mv")),
                vout_mv=int_or_none(row.get("vout_mv")),
                pwr_src=int_or_none(row.get("pwr_src")),
                pages=int_or_none(row.get("pages")),
                line=number,
            )
        )
    return samples, meta


def fmt_epoch(epoch: int | None) -> str:
    if epoch is None or epoch <= 0:
        return "clock?"
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def group_boots(samples: list[Sample]) -> list[list[Sample]]:
    groups: list[list[Sample]] = []
    current: list[Sample] = []
    for sample in samples:
        if sample.event == "boot" and current:
            groups.append(current)
            current = []
        current.append(sample)
    if current:
        groups.append(current)
    return groups


def discharge_pairs(samples: list[Sample], max_gap_s: float) -> list[tuple[Sample, Sample, float]]:
    """Consecutive trusted-time rows that are both on battery and discharging."""
    pairs = []
    for left, right in zip(samples, samples[1:]):
        if left.chg != 0 or right.chg != 0 or left.usb != 0 or right.usb != 0:
            continue
        if not left.known_clock or not right.known_clock:
            continue
        if left.mv is None or right.mv is None or left.pct is None or right.pct is None:
            continue
        dt = right.epoch - left.epoch
        if dt <= 0 or dt > max_gap_s:
            continue
        pairs.append((left, right, float(dt)))
    return pairs


def rate_text(pairs: list[tuple[Sample, Sample, float]]) -> list[str]:
    if not pairs:
        return ["  (no trusted-time discharge pairs)"]
    mv_rates = []
    pct_rates = []
    for left, right, dt in pairs:
        hours = dt / 3600.0
        if left.mv is not None and right.mv is not None:
            mv_rates.append((right.mv - left.mv) / hours)
        if left.pct is not None and right.pct is not None:
            pct_rates.append((right.pct - left.pct) / hours)
    lines = []
    if mv_rates:
        lines.append(
            f"  voltage: median {statistics.median(mv_rates):+.1f} mV/h "
            f"(range {min(mv_rates):+.1f} .. {max(mv_rates):+.1f}, n={len(mv_rates)})"
        )
    if pct_rates:
        lines.append(
            f"  percent: median {statistics.median(pct_rates):+.1f} %/h "
            f"(range {min(pct_rates):+.1f} .. {max(pct_rates):+.1f}, n={len(pct_rates)})"
        )
    return lines


def find_full_cycle(samples: list[Sample]) -> tuple[Sample, Sample] | None:
    starts = [s for s in samples if s.known_clock and s.pct is not None and s.pct >= 95]
    ends = [s for s in samples if s.known_clock and s.pct is not None and s.pct <= 5]
    best = None
    best_hours = 0.0
    for start in starts:
        for end in ends:
            if end.epoch <= start.epoch:
                continue
            hours = (end.epoch - start.epoch) / 3600.0
            if hours > best_hours:
                best_hours = hours
                best = (start, end)
    return best


def suggest_curve(samples: list[Sample]) -> list[int] | None:
    """Median voltage for each 10% of elapsed time between a full and an empty row."""
    cycle = find_full_cycle(samples)
    if cycle is None:
        return None
    start, end = cycle
    run = [
        s
        for s in samples
        if s.known_clock
        and start.epoch <= s.epoch <= end.epoch
        and s.mv is not None
        and s.chg == 0
        and s.usb == 0
    ]
    if len(run) < 6 or end.epoch <= start.epoch:
        return None

    duration = float(end.epoch - start.epoch)
    bins: list[list[int]] = [[] for _ in range(11)]
    for sample in run:
        elapsed = (sample.epoch - start.epoch) / duration
        # elapsed 0 is 100%, elapsed 1 is 0%.
        percent = 100.0 * (1.0 - elapsed)
        index = int(round(percent / 10.0))
        index = max(0, min(10, index))
        bins[index].append(sample.mv)

    values: list[float | None] = []
    for bucket in bins:
        values.append(float(statistics.median(bucket)) if bucket else None)

    # Fill gaps by linear interpolation between the nearest known percentages.
    known = [i for i, value in enumerate(values) if value is not None]
    if not known:
        return None
    for i, value in enumerate(values):
        if value is not None:
            continue
        lower = max((k for k in known if k < i), default=None)
        upper = min((k for k in known if k > i), default=None)
        if lower is None:
            values[i] = values[upper]
        elif upper is None:
            values[i] = values[lower]
        else:
            weight = (i - lower) / (upper - lower)
            values[i] = values[lower] + (values[upper] - values[lower]) * weight

    # The firmware table is ordered 0% .. 100%, matching the bin indexes.
    return [int(round(value)) for value in values]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("path", type=Path, help="path to battery-log.csv")
    parser.add_argument(
        "--capacity",
        type=float,
        metavar="MAH",
        help="nominal cell capacity in mAh; enables current/runtime estimates",
    )
    parser.add_argument(
        "--max-gap",
        type=float,
        default=1800.0,
        metavar="SECONDS",
        help="ignore discharge pairs farther apart than this (default: 1800)",
    )
    parser.add_argument("--curve", action="store_true", help="print a suggested 11-point voltage curve")
    args = parser.parse_args()

    try:
        samples, meta = read_samples(args.path)
    except (OSError, ValueError) as error:
        print(f"[error] {error}", file=sys.stderr)
        return 1

    if not samples:
        print("[error] no samples in the log", file=sys.stderr)
        return 1

    known_clock = [s for s in samples if s.known_clock]
    voltages = [s.mv for s in samples if s.mv is not None]
    percentages = [s.pct for s in samples if s.pct is not None]
    transitions = sum(
        1
        for left, right in zip(samples, samples[1:])
        if (left.chg, left.usb) != (right.chg, right.usb)
    )

    print(f"file: {args.path}")
    if meta:
        print(f"meta: {meta}")
    print(f"rows: {len(samples)}  trusted-clock: {len(known_clock)}  state transitions: {transitions}")
    if known_clock:
        print(f"time: {fmt_epoch(known_clock[0].epoch)}  ->  {fmt_epoch(known_clock[-1].epoch)}")
    else:
        print("time: untrusted (no RTC/NTP); only uptime_s within a boot is usable")
    if voltages:
        print(f"voltage: {min(voltages)} .. {max(voltages)} mV")
    if percentages:
        print(f"percent: {min(percentages)} .. {max(percentages)} %")

    groups = group_boots(samples)
    page_turns = sum(max((s.pages or 0) for s in group) for group in groups)
    print(f"boots: {len(groups)}  page turns: {page_turns}")
    if page_turns and known_clock and len(known_clock) > 1:
        hours = (known_clock[-1].epoch - known_clock[0].epoch) / 3600.0
        if hours > 0:
            print(f"page turns/h: {page_turns / hours:.1f} (trusted-clock span)")
    for index, group in enumerate(groups[:20], start=1):
        first = group[0]
        last = group[-1]
        volts = [s.mv for s in group if s.mv is not None]
        voltage_range = f"{min(volts)}..{max(volts)} mV" if volts else "no voltage"
        pages = max((s.pages or 0) for s in group)
        pages_text = f"  pages={pages}" if any(s.pages is not None for s in group) else ""
        print(
            f"  {index:2d}. {fmt_epoch(first.epoch)}  samples={len(group):3d}  "
            f"{voltage_range}{pages_text}  events={','.join(sorted({s.event for s in group}))}"
        )
    if len(groups) > 20:
        print(f"  ... {len(groups) - 20} more boots")

    pairs = discharge_pairs(samples, args.max_gap)
    print("discharge (battery, trusted time, gap <= --max-gap):")
    for line in rate_text(pairs):
        print(line)

    cycle = find_full_cycle(samples)
    if cycle:
        start, end = cycle
        hours = (end.epoch - start.epoch) / 3600.0
        print(f"full cycle: {start.pct}% -> {end.pct}% in {hours:.1f} h "
              f"({fmt_epoch(start.epoch)} -> {fmt_epoch(end.epoch)})")
        if args.capacity:
            average_ma = args.capacity / hours if hours > 0 else 0.0
            print(f"  at {args.capacity:g} mAh: mean load {average_ma:.1f} mA "
                  f"(voltage-based percentage; treat as an estimate)")
    else:
        print("full cycle: not found (need a trusted-time run from >=95% to <=5%)")

    if args.capacity and pairs:
        estimates = []
        for left, right, dt in pairs:
            if left.pct is None or right.pct is None or left.pct <= right.pct:
                continue
            hours = dt / 3600.0
            if hours <= 0:
                continue
            used_mah = args.capacity * (left.pct - right.pct) / 100.0
            estimates.append(used_mah / hours)
        if estimates:
            print(f"segment estimate: median {statistics.median(estimates):.1f} mA "
                  f"(range {min(estimates):.1f} .. {max(estimates):.1f}, n={len(estimates)})")

    if args.curve:
        curve = suggest_curve(samples)
        if curve is None:
            print("curve: need a trusted-time full discharge with at least 6 samples")
        else:
            print("suggested curve (time-based, 0% -> 100%):")
            print("constexpr uint16_t PROPOSED_NOTCH_MV[11] = {")
            for percent, value in zip(range(0, 101, 10), curve):
                print(f"    {value:4d},  // {percent:3d}%")
            print("};")
            print("note: measured under the test's load pattern; resting-voltage anchors may differ.")

    if not known_clock:
        print("warning: no trusted timestamps. Connect WiFi once (NTP) before a long test.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
