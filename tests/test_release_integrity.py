# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

import pytest

from scripts import release_integrity


def test_final_status_requires_a_date(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="2"):
        release_integrity.main(["--release-status", "final"])
    assert "final release status requires --release-date" in capsys.readouterr().err


def test_invalid_release_date_is_rejected(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="2"):
        release_integrity.main(["--release-status", "final", "--release-date", "2026-02-30"])
    assert "release date must be a valid ISO date" in capsys.readouterr().err


def test_pre_release_rejects_a_release_date(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit, match="2"):
        release_integrity.main(["--release-date", "2026-07-22"])
    assert "pre-release status requires the release date to be unset" in capsys.readouterr().err


def test_pre_release_metadata_has_null_date() -> None:
    _, manifest_bytes, _ = release_integrity._render_metadata(
        release_status="pre-release",
        release_date=None,
    )
    release = json.loads(manifest_bytes)["release"]
    assert release["release_status"] == "pre-release"
    assert release["release_date"] is None


def test_final_metadata_stores_supplied_date() -> None:
    _, manifest_bytes, _ = release_integrity._render_metadata(
        release_status="final",
        release_date="2026-07-22",
    )
    release = json.loads(manifest_bytes)["release"]
    assert release["release_status"] == "final"
    assert release["release_date"] == "2026-07-22"


def test_normal_verification_passes_without_rewriting(
    capsys: pytest.CaptureFixture[str],
) -> None:
    checksum_before = release_integrity.CHECKSUM_PATH.read_bytes()
    manifest_before = release_integrity.MANIFEST_PATH.read_bytes()

    assert release_integrity.main([]) == 0

    assert release_integrity.CHECKSUM_PATH.read_bytes() == checksum_before
    assert release_integrity.MANIFEST_PATH.read_bytes() == manifest_before
    assert "Release integrity verified" in capsys.readouterr().out
