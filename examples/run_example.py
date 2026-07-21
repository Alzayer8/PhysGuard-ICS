# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Run the bundled synthetic example from a source checkout."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from physguard.config import load_config
from physguard.experiments import run_experiment

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    destination = run_experiment(
        train=pd.read_csv(ROOT / "sample_data" / "train.csv"),
        validation=pd.read_csv(ROOT / "sample_data" / "validation.csv"),
        test=pd.read_csv(ROOT / "sample_data" / "test.csv"),
        workspace=ROOT / "example-workspace",
        config=load_config(ROOT / "configs" / "example.yaml"),
    )
    print(f"Created {destination}")


if __name__ == "__main__":
    main()
