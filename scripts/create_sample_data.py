# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Create deterministic, entirely artificial CSV telemetry for the quick start."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def _frame(start: str, rows: int, seed: int, *, attacks: bool) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    timestamp = pd.date_range(start, periods=rows, freq="s", tz="UTC")
    phase = np.arange(rows) % 60
    inlet_valve = (phase < 28).astype(int)
    outlet_pump = ((phase >= 32) & (phase < 55)).astype(int)
    inlet_flow = inlet_valve * (0.92 + rng.normal(0, 0.02, rows))
    outlet_flow = outlet_pump * (0.78 + rng.normal(0, 0.02, rows))
    net_flow = inlet_flow - outlet_flow
    tank_level = 5.0 + np.cumsum(net_flow) * 0.025 + rng.normal(0, 0.015, rows)
    pressure = 0.55 + 0.22 * tank_level + rng.normal(0, 0.012, rows)
    attack = np.zeros(rows, dtype=int)
    if attacks:
        first = slice(rows // 3, rows // 3 + 10)
        second = slice(2 * rows // 3, 2 * rows // 3 + 8)
        outlet_flow[first] = 0.55
        outlet_pump[first] = 0
        pressure[second] = 5.8
        attack[first] = 1
        attack[second] = 1
    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "inlet_flow": inlet_flow.round(5),
            "outlet_flow": outlet_flow.round(5),
            "tank_level": tank_level.round(5),
            "pressure": pressure.round(5),
            "inlet_valve": inlet_valve,
            "outlet_pump": outlet_pump,
            "attack": attack,
        }
    )


def generate(output: Path) -> None:
    """Write all three files, refusing to replace any existing path."""

    output.mkdir(parents=True, exist_ok=True)
    frames = {
        "train.csv": _frame("2026-01-01T00:00:00Z", 120, 731, attacks=False),
        "validation.csv": _frame("2026-01-02T00:00:00Z", 60, 732, attacks=False),
        "test.csv": _frame("2026-01-03T00:00:00Z", 120, 733, attacks=True),
    }
    conflicts = [name for name in frames if (output / name).exists()]
    if conflicts:
        raise FileExistsError(f"refusing to overwrite: {', '.join(conflicts)}")
    for name, frame in frames.items():
        frame.to_csv(output / name, index=False, date_format="%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("sample_data"))
    args = parser.parse_args()
    generate(args.output)
    print(f"Created synthetic sample data in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
