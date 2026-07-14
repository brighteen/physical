#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
BAG="${1:-$(ls -td results/nav2_* 2>/dev/null | head -1 || true)}"
if [ -z "$BAG" ]; then echo "No results/nav2_* bag found."; exit 1; fi
ros2 bag info "$BAG"
