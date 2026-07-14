#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
MAP="${1:-maps/lab_map.yaml}"
if [ "$#" -gt 0 ]; then shift; fi
if [ ! -f "$MAP" ]; then
  echo "Map $MAP not found. Using examples/simple_map.yaml for offline planner."
  MAP="examples/simple_map.yaml"
fi
mkdir -p results
python3 python/planner_offline.py \
  --map "$MAP" \
  --start-x 0.0 --start-y 0.0 \
  --goal-x 1.0 --goal-y 1.0 \
  --output-csv results/planner_metrics_offline.csv \
  --output-png results/planner_compare_offline.png \
  "$@"
python3 python/summarize_csv_mo.py results/planner_metrics_offline.csv
