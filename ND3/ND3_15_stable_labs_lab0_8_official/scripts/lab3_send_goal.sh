#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
X="${1:-0.5}"
Y="${2:-0.0}"
YAW="${3:-0.0}"
python3 python/send_goal.py --x "$X" --y "$Y" --yaw "$YAW"
