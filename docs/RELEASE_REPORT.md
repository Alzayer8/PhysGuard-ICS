# Public release report

This report tracks the pre-release verification state. See
`release_manifest.json` for the exact file inventory and `SHA256SUMS.txt` for verification.

- Target release: PhysGuard-ICS v1.0.0
- Audit status: Pre-release verification pending
- Audited commit: `<COMMIT_SHA>`
- GitHub Release: Not yet published
- Scope: public, offline, synthetic-data-first toolkit
- Sealed research modified: no
- Total release size: 2337644 bytes
- SHA-256 manifest: generated and verified
- README: complete
- Dashboard: import and headless startup verified
- License: Apache License 2.0 (`Apache-2.0`)
- NOTICE: present
- SPDX headers: 13 project-authored Python files
- Legacy-license references: 0
- Verification: local checks must pass before the corrected release commit is created

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
the release integrity manifest.

## Research boundary

This public educational toolkit is separate from the sealed Revised Study v2. It excludes
the HAI datasets, frozen baseline artifacts, study-specific configurations, fitted models,
checkpoints, and sealed study results. Its toy-baseline output does not reproduce or
validate that sealed study.
