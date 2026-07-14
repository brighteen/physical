#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
echo "Starting SLAM Toolbox online async..."
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=True
