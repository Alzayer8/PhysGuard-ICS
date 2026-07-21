# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Build or verify the deterministic public-release integrity metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHECKSUM_PATH = ROOT / "SHA256SUMS.txt"
MANIFEST_PATH = ROOT / "release_manifest.json"
REPORT_PATH = ROOT / "docs" / "RELEASE_REPORT.md"
METADATA_NAMES = {CHECKSUM_PATH.name, MANIFEST_PATH.name}


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tracked_relative_paths() -> list[Path]:
    """Return the repository's tracked files without inspecting untracked content."""

    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z", "--"],
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as error:
        raise RuntimeError(
            "Git is required to inventory release files but was not found"
        ) from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace").strip()
        message = "Git could not list tracked release files"
        if detail:
            message = f"{message}: {detail}"
        raise RuntimeError(message) from error

    relative_paths = [
        Path(os.fsdecode(raw_path)) for raw_path in result.stdout.split(b"\0") if raw_path
    ]
    missing = [path.as_posix() for path in relative_paths if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError(f"tracked release files are missing: {', '.join(sorted(missing))}")
    return sorted(relative_paths, key=lambda path: path.as_posix())


def _payload_files() -> list[Path]:
    return [
        ROOT / path for path in _tracked_relative_paths() if path.as_posix() not in METADATA_NAMES
    ]


def _entry(path: Path) -> dict[str, str | int]:
    return {
        "filename": path.relative_to(ROOT).as_posix(),
        "size": path.stat().st_size,
        "sha256": _sha256_file(path),
    }


def _render_metadata() -> tuple[bytes, bytes, int]:
    entries = [_entry(path) for path in _payload_files()]
    sums = "".join(f"{entry['sha256']}  {entry['filename']}\n" for entry in entries).encode("utf-8")
    manifest_entries = [
        *entries,
        {
            "filename": CHECKSUM_PATH.name,
            "size": len(sums),
            "sha256": _sha256_bytes(sums),
        },
    ]
    payload_bytes = sum(int(entry["size"]) for entry in manifest_entries)
    total_bytes = payload_bytes
    manifest_bytes = b""
    for _ in range(10):
        manifest: dict[str, Any] = {
            "release": {
                "official_project_name": "PhysGuard-ICS",
                "author": "Ahmad Alzayer",
                "version": "v1.0.0",
                "release_identifier": "physguard-ics-public-v1.0.0",
                "release_status": "pre-release",
                "release_timestamp": None,
                "repository_identifier": "Alzayer8/PhysGuard-ICS",
                "repository_url": "https://github.com/Alzayer8/PhysGuard-ICS",
                "hash_algorithm": "SHA-256",
                "manifest_scope": "all Git-tracked files except release_manifest.json itself",
                "total_file_count": len(manifest_entries) + 1,
                "total_release_bytes": total_bytes,
            },
            "files": manifest_entries,
            "authenticity_statement": {
                "project": "PhysGuard-ICS",
                "author": "Ahmad Alzayer",
                "notice": (
                    "This statement is descriptive metadata only. It is not a digital "
                    "signature and does not authenticate the repository cryptographically."
                ),
            },
        }
        manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        updated_total = payload_bytes + len(manifest_bytes)
        if updated_total == total_bytes:
            break
        total_bytes = updated_total
    return sums, manifest_bytes, total_bytes


def build() -> None:
    """Write checksum and manifest metadata after stabilizing the report size."""

    for _ in range(5):
        sums, manifest, total_bytes = _render_metadata()
        report = REPORT_PATH.read_text(encoding="utf-8")
        updated = re.sub(
            r"^- Total release size: (?:__TOTAL_BYTES__|\d+) bytes$",
            f"- Total release size: {total_bytes} bytes",
            report,
            flags=re.MULTILINE,
        )
        if updated == report:
            CHECKSUM_PATH.write_bytes(sums)
            MANIFEST_PATH.write_bytes(manifest)
            return
        REPORT_PATH.write_text(updated, encoding="utf-8", newline="\n")
    raise RuntimeError("release size did not stabilize")


def verify() -> None:
    """Verify every manifest entry, checksum line, statement, and inventory boundary."""

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected_paths: set[str] = set()
    for entry in manifest["files"]:
        relative = str(entry["filename"])
        path = ROOT / relative
        expected_paths.add(relative)
        if not path.is_file():
            raise RuntimeError(f"missing release file: {relative}")
        if path.stat().st_size != int(entry["size"]):
            raise RuntimeError(f"size mismatch: {relative}")
        if _sha256_file(path) != entry["sha256"]:
            raise RuntimeError(f"hash mismatch: {relative}")
    actual_paths = {
        path.as_posix()
        for path in _tracked_relative_paths()
        if path.as_posix() != MANIFEST_PATH.name
    }
    if actual_paths != expected_paths:
        raise RuntimeError("manifest inventory does not match the release tree")
    release = manifest["release"]
    if int(release["total_file_count"]) != len(expected_paths) + 1:
        raise RuntimeError("manifest total file count is invalid")
    total_release_bytes = sum((ROOT / path).stat().st_size for path in expected_paths)
    total_release_bytes += MANIFEST_PATH.stat().st_size
    if int(release["total_release_bytes"]) != total_release_bytes:
        raise RuntimeError("manifest total release size is invalid")
    statement = manifest["authenticity_statement"]
    if statement["project"] != "PhysGuard-ICS" or statement["author"] != "Ahmad Alzayer":
        raise RuntimeError("release authenticity statement is invalid")
    if "not a digital signature" not in str(statement["notice"]).lower():
        raise RuntimeError("release authenticity statement lacks the signature disclaimer")

    checksum_paths: set[str] = set()
    for line_number, line in enumerate(
        CHECKSUM_PATH.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            raise RuntimeError(f"invalid checksum format on line {line_number}")
        expected_hash, relative = match.groups()
        if relative in checksum_paths:
            raise RuntimeError(f"duplicate checksum path: {relative}")
        checksum_paths.add(relative)
        if _sha256_file(ROOT / relative) != expected_hash:
            raise RuntimeError(f"checksum mismatch: {relative}")
    expected_checksum_paths = expected_paths - {CHECKSUM_PATH.name}
    if checksum_paths != expected_checksum_paths:
        raise RuntimeError("checksum inventory does not match the release payload")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rebuild integrity metadata")
    args = parser.parse_args()
    if args.write:
        build()
    verify()
    print("Release integrity verified: all tracked files, hashes, sizes, and metadata match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
