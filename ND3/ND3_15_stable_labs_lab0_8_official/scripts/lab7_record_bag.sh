#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
mkdir -p results
OUT="results/nav2_$(date +%Y%m%d_%H%M%S)"
echo "Recording rosbag to $OUT"
ros2 bag record -o "$OUT" /scan /odom /tf /tf_static /map /cmd_vel /amcl_pose /goal_pose /plan /local_plan || true
echo "Bag stopped. Check with: ros2 bag info $OUT"
