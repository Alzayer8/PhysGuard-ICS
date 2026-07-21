# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from physguard.analysis import DataValidationError, fit_baseline, score_telemetry, validate_frame
from physguard.config import load_config

ROOT = Path(__file__).resolve().parent.parent


def _data(name: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / "sample_data" / name)


def test_sample_splits_validate() -> None:
    train = validate_frame(_data("train.csv"), split="train")
    validation = validate_frame(_data("validation.csv"), split="validation")
    test = validate_frame(_data("test.csv"), split="test")
    assert len(train) == 120
    assert len(validation) == 60
    assert len(test) == 120


def test_duplicate_timestamp_is_rejected() -> None:
    frame = _data("train.csv")
    frame.loc[1, "timestamp"] = frame.loc[0, "timestamp"]
    with pytest.raises(DataValidationError, match="unique and increasing"):
        validate_frame(frame, split="train")


def test_scoring_retains_independent_evidence() -> None:
    train = validate_frame(_data("train.csv"), split="train")
    validation = validate_frame(_data("validation.csv"), split="validation")
    test = validate_frame(_data("test.csv"), split="test")
    scored = score_telemetry(
        test, fit_baseline(train, validation), load_config(ROOT / "configs" / "example.yaml")
    )
    assert {"normal", "physics_only", "hybrid"}.issuperset(set(scored["fusion_category"]))
    assert bool(scored["physics_alert"].any())
