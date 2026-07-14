#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
python3 python/mission_runner.py --waypoints docs/waypoints_default.csv
