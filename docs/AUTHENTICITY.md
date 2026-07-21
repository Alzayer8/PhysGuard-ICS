# Release authenticity

- Official project name: **PhysGuard-ICS**
- Author: **Ahmad Alzayer**
- Copyright: Copyright (c) 2026 Ahmad Alzayer
- Official license: **Apache License 2.0 (`Apache-2.0`)**
- Release identifier: `physguard-ics-public-v1.0.0`
- Release status: **Final**
- Release date: `2026-07-22`
- Repository identifier: `Alzayer8/PhysGuard-ICS`
- Repository URL: <https://github.com/Alzayer8/PhysGuard-ICS>

`SHA256SUMS.txt` contains a SHA-256 digest for every release file except itself and the
manifest. `release_manifest.json` records every payload file plus the checksum file. The
manifest excludes itself because a file cannot contain a stable digest of its own final
bytes.

Verify from the repository root:

```bash
sha256sum --check SHA256SUMS.txt
```

On Windows PowerShell, compare a listed digest with:

```powershell
Get-FileHash -Algorithm SHA256 .\README.md
```

---

## Official Release Authenticity Statement

PhysGuard-ICS  
Author: Ahmad Alzayer

This statement is descriptive metadata only. It is not a digital signature and does not
authenticate the repository cryptographically.
