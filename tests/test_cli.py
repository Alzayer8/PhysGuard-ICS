# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from physguard.cli import DEFAULT_CONFIG, main
from physguard.config import load_config


def test_doctor(capsys: object) -> None:
    assert main(["doctor"]) == 0


def test_packaged_default_configuration_is_available() -> None:
    assert DEFAULT_CONFIG.is_file()
    assert load_config(DEFAULT_CONFIG)["anomaly_z_threshold"] == 4.0
