#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
mkdir -p results
python3 python/dwb_safe_agile_offline.py \
  --output-csv results/dwb_safe_agile.csv \
  --output-png results/dwb_safe_agile.png
python3 python/summarize_csv.py results/dwb_safe_agile.csv
