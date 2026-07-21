# Contributing

Thank you for helping improve PhysGuard-ICS.

1. Open an issue describing the problem, proposed behavior, and safety implications.
2. Create a focused branch and keep unrelated changes out of the pull request.
3. Add or update tests and public documentation.
4. Run the complete local check before submitting:

   ```bash
   python -m ruff check .
   python -m ruff format --check .
   python -m mypy physguard
   python -m pytest
   ```

5. Complete the pull-request checklist and explain any threshold or dataset assumption.

Do not commit proprietary or sensitive telemetry, secrets, model checkpoints, generated
experiment workspaces, archives, logs, or third-party datasets. Synthetic fixtures should
be small, deterministic, and clearly labeled. Security vulnerabilities belong in a
private report under [SECURITY.md](SECURITY.md), not a public issue.

By contributing, you agree that your contribution is licensed under the Apache License 2.0.
