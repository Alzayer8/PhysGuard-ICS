# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Small, transparent physics-aware analysis engine for CSV telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

CONTINUOUS_FEATURES = (
    "inlet_flow",
    "outlet_flow",
    "tank_level",
    "pressure",
)
DISCRETE_FEATURES = ("inlet_valve", "outlet_pump")
REQUIRED_COLUMNS = ("timestamp", *CONTINUOUS_FEATURES, *DISCRETE_FEATURES)


class DataValidationError(ValueError):
    """Raised when telemetry does not satisfy the public CSV contract."""


@dataclass(frozen=True)
class Baseline:
    """Normal-only feature statistics used for transparent anomaly scoring."""

    mean: dict[str, float]
    scale: dict[str, float]


def validate_frame(frame: pd.DataFrame, *, split: str) -> pd.DataFrame:
    """Validate and normalize one chronological telemetry split."""

    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise DataValidationError(f"{split}: missing required columns: {', '.join(missing)}")
    clean = frame.copy()
    timestamps = pd.to_datetime(clean["timestamp"], utc=True, errors="coerce")
    if timestamps.isna().any():
        raise DataValidationError(f"{split}: timestamp contains invalid values")
    if timestamps.duplicated().any() or not timestamps.is_monotonic_increasing:
        raise DataValidationError(f"{split}: timestamps must be unique and increasing")
    clean["timestamp"] = timestamps
    for column in (*CONTINUOUS_FEATURES, *DISCRETE_FEATURES):
        clean[column] = pd.to_numeric(clean[column], errors="coerce")
        values = clean[column].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise DataValidationError(f"{split}: {column} must contain finite numeric values")
    for column in DISCRETE_FEATURES:
        if not clean[column].isin([0, 1]).all():
            raise DataValidationError(f"{split}: {column} must contain only 0 or 1")
        clean[column] = clean[column].astype(int)
    if "attack" in clean.columns:
        clean["attack"] = pd.to_numeric(clean["attack"], errors="coerce")
        if not clean["attack"].isin([0, 1]).all():
            raise DataValidationError(f"{split}: attack must contain only 0 or 1")
        clean["attack"] = clean["attack"].astype(int)
        if split in {"train", "validation"} and bool(clean["attack"].any()):
            raise DataValidationError(f"{split}: baseline splits must contain normal rows only")
    return clean


def fit_baseline(train: pd.DataFrame, validation: pd.DataFrame) -> Baseline:
    """Fit mean and standard deviation from normal train/validation telemetry."""

    reference = pd.concat([train, validation], ignore_index=True)
    mean: dict[str, float] = {}
    scale: dict[str, float] = {}
    for column in CONTINUOUS_FEATURES:
        mean[column] = float(reference[column].mean())
        feature_scale = float(reference[column].std(ddof=0))
        scale[column] = feature_scale if feature_scale > 1e-12 else 1.0
    return Baseline(mean=mean, scale=scale)


def _physics_reasons(frame: pd.DataFrame, config: dict[str, Any]) -> list[str]:
    limits = config["physics_limits"]
    reasons: list[str] = []
    columns = [*CONTINUOUS_FEATURES, *DISCRETE_FEATURES]
    for inlet_flow, outlet_flow, tank_level, pressure, inlet_valve, outlet_pump in frame[
        columns
    ].to_numpy(dtype=float):
        row_reasons: list[str] = []
        if not limits["tank_level"][0] <= tank_level <= limits["tank_level"][1]:
            row_reasons.append("tank_level_out_of_range")
        if not limits["pressure"][0] <= pressure <= limits["pressure"][1]:
            row_reasons.append("pressure_out_of_range")
        if inlet_flow < 0 or outlet_flow < 0:
            row_reasons.append("negative_flow")
        if inlet_valve == 0 and inlet_flow > limits["closed_valve_max_flow"]:
            row_reasons.append("closed_valve_with_flow")
        if outlet_pump == 0 and outlet_flow > limits["stopped_pump_max_flow"]:
            row_reasons.append("stopped_pump_with_flow")
        reasons.append(";".join(row_reasons))
    return reasons


def score_telemetry(
    test: pd.DataFrame,
    baseline: Baseline,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Score telemetry and retain independent statistical and physics evidence."""

    scored = test.copy()
    z_columns: list[str] = []
    for column in CONTINUOUS_FEATURES:
        z_column = f"z_{column}"
        scored[z_column] = (scored[column] - baseline.mean[column]).abs() / baseline.scale[column]
        z_columns.append(z_column)
    scored["anomaly_score"] = scored[z_columns].max(axis=1)
    scored["ml_alert"] = scored["anomaly_score"] >= float(config["anomaly_z_threshold"])
    scored["physics_reasons"] = _physics_reasons(scored, config)
    scored["physics_alert"] = scored["physics_reasons"].str.len() > 0
    scored["fusion_category"] = np.select(
        [
            scored["ml_alert"] & scored["physics_alert"],
            scored["ml_alert"],
            scored["physics_alert"],
        ],
        ["hybrid", "ml_only", "physics_only"],
        default="normal",
    )
    scored["alert"] = scored["fusion_category"] != "normal"
    return scored


def summarize(scored: pd.DataFrame) -> dict[str, Any]:
    """Create a JSON-serializable run summary."""

    category_counts = {
        str(key): int(value)
        for key, value in scored["fusion_category"].value_counts().sort_index().items()
    }
    summary: dict[str, Any] = {
        "rows": len(scored),
        "alerts": int(scored["alert"].sum()),
        "category_counts": category_counts,
        "start_timestamp": scored["timestamp"].iloc[0].isoformat(),
        "end_timestamp": scored["timestamp"].iloc[-1].isoformat(),
        "max_anomaly_score": float(scored["anomaly_score"].max()),
    }
    if "attack" in scored.columns:
        predicted = scored["alert"].astype(bool)
        actual = scored["attack"].astype(bool)
        true_positive = int((predicted & actual).sum())
        false_positive = int((predicted & ~actual).sum())
        false_negative = int((~predicted & actual).sum())
        summary["labeled_metrics"] = {
            "precision": true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else None,
            "recall": true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else None,
            "true_positive_rows": true_positive,
            "false_positive_rows": false_positive,
            "false_negative_rows": false_negative,
        }
    return summary
