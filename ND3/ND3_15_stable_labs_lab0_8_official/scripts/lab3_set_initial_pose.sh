#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
X="${1:-0.0}"
Y="${2:-0.0}"
YAW="${3:-0.0}"
python3 python/initial_pose.py --x "$X" --y "$Y" --yaw "$YAW"
