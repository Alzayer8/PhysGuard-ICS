# Public release report

This report is finalized after the content audit and checksum pass. See
`release_manifest.json` for the exact file inventory and `SHA256SUMS.txt` for verification.

- Release: PhysGuard-ICS v1.0.0
- Scope: public, offline, synthetic-data-first toolkit
- Sealed research modified: no
- Total release size: 2327624 bytes
- SHA-256 manifest: generated and verified
- README: complete
- Dashboard: import and headless startup verified
- License: Apache License 2.0 (`Apache-2.0`)
- NOTICE: present
- SPDX headers: 13 project-authored Python files
- Legacy-license references: 0
- Verification: Ruff passed; strict MyPy passed; pytest 5/5 passed; wheel build passed
- GitHub readiness score: 100/100

## Intentionally excluded

- Sealed studies and all HAI datasets or study-specific configurations
- External datasets and research-only documentation
- Checkpoints, trained models, experiment outputs, regression outputs, and reports
- Phase/revision automation scripts and research-only dashboard pages
- Virtual environments, caches, coverage files, temporary renders, and logs
- Release archives, local IDE settings, hidden build state, and source repository history

## Included scope

The release contains the installable `physguard` package, upload-first dashboard,
synthetic toy CSV splits, example configuration, tests, documentation, project artwork,
community health files, CI configuration, license, citation metadata, checksum list, and
the signed release manifest.
