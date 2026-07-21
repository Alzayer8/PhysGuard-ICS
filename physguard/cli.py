# Copyright 2026 Ahmad Alzayer
# SPDX-License-Identifier: Apache-2.0

"""Command-line interface for the public PhysGuard-ICS release."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import pandas as pd

from physguard import __version__
from physguard.analysis import validate_frame
from physguard.config import load_config
from physguard.experiments import run_experiment

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def _add_data_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PhysGuard-ICS public example toolkit")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Print runtime information")
    validate = subparsers.add_parser("validate", help="Validate three CSV splits")
    _add_data_arguments(validate)

    analyze = subparsers.add_parser("analyze", help="Create a new immutable experiment")
    _add_data_arguments(analyze)
    analyze.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs" / "example.yaml")
    analyze.add_argument("--workspace", type=Path, default=PROJECT_ROOT / "example-workspace")
    analyze.add_argument("--experiment-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process status."""

    args = _build_parser().parse_args(argv)
    if args.command == "doctor":
        print(json.dumps({"physguard": __version__, "python": platform.python_version()}, indent=2))
        return 0
    train = _read_csv(args.train)
    validation = _read_csv(args.validation)
    test = _read_csv(args.test)
    if args.command == "validate":
        for split, frame in (("train", train), ("validation", validation), ("test", test)):
            validate_frame(frame, split=split)
        print("Validation passed: train, validation, and test are ready.")
        return 0
    destination = run_experiment(
        train=train,
        validation=validation,
        test=test,
        workspace=args.workspace,
        config=load_config(args.config),
        experiment_id=args.experiment_id,
    )
    print(f"Created experiment: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
