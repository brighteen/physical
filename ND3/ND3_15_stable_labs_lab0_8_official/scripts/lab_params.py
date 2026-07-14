#!/usr/bin/env python3
"""Build or run lab practice commands from configs/lab_parameters.yaml."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import yaml

from lab_common import ROOT, quote_command, run_stream, use_repo_root


LAB_SCRIPTS = {
    "lab0": "scripts/lab0_practice.py",
    "lab1": "scripts/lab1_practice.py",
    "lab2": "scripts/lab2_practice.py",
    "lab3": "scripts/lab3_practice.py",
    "lab4": "scripts/lab4_practice.py",
    "lab5": "scripts/lab5_practice.py",
    "lab6": "scripts/lab6_practice.py",
    "lab7": "scripts/lab7_practice.py",
    "lab8": "scripts/lab8_practice.py",
}


def load_config(path: Path) -> dict[str, object]:
    if not path.exists():
        raise SystemExit(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"Config root must be a mapping: {path}")
    return data


def parse_value(raw: str) -> object:
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise SystemExit(f"Invalid YAML value in --set: {raw}\n{exc}") from exc


def apply_override(config: dict[str, object], selected_lab: str, assignment: str) -> None:
    if "=" not in assignment:
        raise SystemExit(f"--set must use key=value form. Got: {assignment}")
    raw_key, raw_value = assignment.split("=", 1)
    raw_key = raw_key.strip()
    if not raw_key:
        raise SystemExit("--set key cannot be empty")

    if "." in raw_key:
        lab, key = raw_key.split(".", 1)
    else:
        if selected_lab == "all":
            raise SystemExit("--set with --lab all must use lab.key=value form, for example lab6.x=0.8")
        lab, key = selected_lab, raw_key

    if lab not in LAB_SCRIPTS:
        raise SystemExit(f"Unknown lab in --set: {lab}")
    if not key:
        raise SystemExit(f"--set parameter name cannot be empty: {assignment}")

    section = config.setdefault(lab, {})
    if not isinstance(section, dict):
        raise SystemExit(f"{lab} section must be a mapping before applying --set")
    section[key] = parse_value(raw_value)


def option_name(key: str) -> str:
    return "--" + key.replace("_", "-")


def value_to_args(key: str, value: object) -> list[str]:
    if value is None:
        return []
    opt = option_name(key)
    if isinstance(value, bool):
        return [opt] if value else []
    if isinstance(value, list):
        if not value:
            return []
        return [opt, *[str(item) for item in value]]
    return [opt, str(value)]


def build_command(lab: str, params: dict[str, object]) -> list[str]:
    script = LAB_SCRIPTS[lab]
    command = ["python3", script]
    for key, value in params.items():
        command.extend(value_to_args(key, value))
    return command


def print_parameter_summary(lab: str, params: dict[str, object]) -> None:
    print(f"[{lab}] editable parameters")
    for key, value in params.items():
        print(f"- {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/lab_parameters.yaml")
    parser.add_argument("--lab", choices=[*LAB_SCRIPTS.keys(), "all"], required=True)
    parser.add_argument("--run", action="store_true", help="Run the command. Without this, only print it.")
    parser.add_argument("--show-values", action="store_true", help="Print parameter values before the command.")
    parser.add_argument(
        "--set",
        dest="overrides",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Temporarily override a YAML value. Example: --set x=0.8 or --set lab6.x=0.8",
    )
    args = parser.parse_args()

    use_repo_root()
    config = load_config(ROOT / args.config)
    for assignment in args.overrides:
        apply_override(config, args.lab, assignment)
    labs = list(LAB_SCRIPTS.keys()) if args.lab == "all" else [args.lab]

    if args.run and args.lab == "all":
        raise SystemExit("--run is allowed for one lab at a time. Use --lab lab4, not --lab all.")

    exit_code = 0
    for lab in labs:
        section = config.get(lab, {})
        if not isinstance(section, dict):
            raise SystemExit(f"{lab} section must be a mapping in {args.config}")
        if args.show_values:
            print_parameter_summary(lab, section)
        command = build_command(lab, section)
        print(quote_command(command), flush=True)
        if args.run:
            exit_code = run_stream([sys.executable, *command[1:]])
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
