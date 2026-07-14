#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
mkdir -p results
python3 python/make_report.py --output results/final_report.md
