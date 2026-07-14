#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-/tmp/nd3_pip_cache}"
mkdir -p "$PIP_CACHE_DIR"
"$PYTHON_BIN" -m pip install -q -r requirements_python.txt
"$PYTHON_BIN" tools/static_check.py
"$PYTHON_BIN" -m pytest -q tests
./scripts/lab4_planner_offline.sh examples/simple_map.yaml
./scripts/lab5_dwb_safe_agile_offline.sh
./scripts/lab8_make_report.sh
