#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
PREFIX="${1:-maps/lab_map}"
mkdir -p "$(dirname "$PREFIX")"
echo "Saving map to $PREFIX.{yaml,pgm}"
ros2 run nav2_map_server map_saver_cli -f "$PWD/$PREFIX"
ls -lh "$PREFIX".*
