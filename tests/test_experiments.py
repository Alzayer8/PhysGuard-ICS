# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

import pandas as pd
import pytest

from physguard.config import load_config
from physguard.experiments import run_experiment

ROOT = Path(__file__).resolve().parent.parent


def test_experiment_is_created_and_never_overwritten() -> None:
    workspace = ROOT / "tests" / f"_workspace-{uuid4().hex}"
    kwargs = {
        "train": pd.read_csv(ROOT / "sample_data" / "train.csv"),
        "validation": pd.read_csv(ROOT / "sample_data" / "validation.csv"),
        "test": pd.read_csv(ROOT / "sample_data" / "test.csv"),
        "workspace": workspace,
        "config": load_config(ROOT / "configs" / "example.yaml"),
        "experiment_id": "test-run",
    }
    try:
        destination = run_experiment(**kwargs)
        assert (destination / "outputs" / "analysis.csv").is_file()
        assert (destination / "outputs" / "summary.json").is_file()
        with pytest.raises(FileExistsError, match="refusing to overwrite"):
            run_experiment(**kwargs)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
