## Summary

Describe the user-visible change and why it is needed.

## Validation

- [ ] `python -m ruff check .`
- [ ] `python -m ruff format --check .`
- [ ] `python -m mypy physguard`
- [ ] `python -m pytest`

## Safety and release hygiene

- [ ] I added or updated tests and documentation.
- [ ] I used only synthetic, redistributable fixtures.
- [ ] I did not add secrets, telemetry, checkpoints, experiment outputs, logs, or archives.
- [ ] I documented threshold, unit, topology, or interpretation changes.
