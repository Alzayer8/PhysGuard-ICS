# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from physguard.cli import main


def test_doctor(capsys: object) -> None:
    assert main(["doctor"]) == 0
