# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Build or verify the deterministic public-release integrity metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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


def _payload_files() -> list[Path]:
    return sorted(
        (path for path in ROOT.rglob("*") if path.is_file() and path.name not in METADATA_NAMES),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


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
                "release_timestamp": "2026-07-21T23:55:00+03:00",
                "repository_identifier": "PhysGuard-ICS/github-release",
                "hash_algorithm": "SHA-256",
                "manifest_scope": "all files except release_manifest.json itself",
                "total_file_count": len(manifest_entries) + 1,
                "total_release_bytes": total_bytes,
            },
            "files": manifest_entries,
            "official_release_signature": {
                "project": "PhysGuard-ICS",
                "author": "Ahmad Alzayer",
                "notice": (
                    "This signature is for authenticity only and is NOT a cryptographic "
                    "code-signing certificate."
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
    """Verify every manifest entry, checksum line, signature, and inventory boundary."""

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
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and path.name != MANIFEST_PATH.name
    }
    if actual_paths != expected_paths:
        raise RuntimeError("manifest inventory does not match the release tree")
    signature = manifest["official_release_signature"]
    if signature["project"] != "PhysGuard-ICS" or signature["author"] != "Ahmad Alzayer":
        raise RuntimeError("official release signature is invalid")
    for line in CHECKSUM_PATH.read_text(encoding="utf-8").splitlines():
        expected_hash, relative = line.split("  ", 1)
        if _sha256_file(ROOT / relative) != expected_hash:
            raise RuntimeError(f"checksum mismatch: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="rebuild integrity metadata")
    args = parser.parse_args()
    if args.write:
        build()
    verify()
    print("Release integrity verified: all hashes, sizes, files, and signature match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
