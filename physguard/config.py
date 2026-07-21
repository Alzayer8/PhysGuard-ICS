# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Configuration loading for the public example pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_config(path: Path) -> dict[str, Any]:
    """Load and minimally validate a YAML configuration."""

    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("configuration root must be a mapping")
    required = {"anomaly_z_threshold", "physics_limits"}
    missing = sorted(required - payload.keys())
    if missing:
        raise ValueError(f"configuration missing keys: {', '.join(missing)}")
    return payload
