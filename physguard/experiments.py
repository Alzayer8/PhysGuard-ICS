# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Immutable experiment workspace management."""

from __future__ import annotations

import json
import secrets
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from physguard.analysis import fit_baseline, score_telemetry, summarize, validate_frame


def new_experiment_id() -> str:
    """Return a sortable, collision-resistant experiment identifier."""

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"exp-{stamp}-{secrets.token_hex(3)}"


def run_experiment(
    *,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    workspace: Path,
    config: dict[str, Any],
    experiment_id: str | None = None,
) -> Path:
    """Validate, score, and atomically persist a never-overwritten experiment."""

    identifier = experiment_id or new_experiment_id()
    if not identifier or any(
        character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        for character in identifier
    ):
        raise ValueError(
            "experiment ID may contain only letters, numbers, hyphens, and underscores"
        )
    experiments = workspace.resolve() / "experiments"
    experiments.mkdir(parents=True, exist_ok=True)
    destination = experiments / identifier
    staging = experiments / f".staging-{identifier}-{secrets.token_hex(3)}"
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing experiment: {destination}")
    if staging.exists():
        raise FileExistsError(f"staging path already exists: {staging}")
    staging.mkdir()
    try:
        clean_train = validate_frame(train, split="train")
        clean_validation = validate_frame(validation, split="validation")
        clean_test = validate_frame(test, split="test")
        baseline = fit_baseline(clean_train, clean_validation)
        scored = score_telemetry(clean_test, baseline, config)
        inputs = staging / "inputs"
        outputs = staging / "outputs"
        inputs.mkdir()
        outputs.mkdir()
        clean_train.to_csv(inputs / "train.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
        clean_validation.to_csv(
            inputs / "validation.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ"
        )
        clean_test.to_csv(inputs / "test.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
        scored.to_csv(outputs / "analysis.csv", index=False, date_format="%Y-%m-%dT%H:%M:%SZ")
        metadata = {
            "experiment_id": identifier,
            "created_at": datetime.now(UTC).isoformat(),
            "baseline": {"mean": baseline.mean, "scale": baseline.scale},
            "summary": summarize(scored),
        }
        (outputs / "summary.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        staging.rename(destination)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return destination
