#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
MAP="${1:-maps/lab_map.yaml}"
if [ ! -f "$MAP" ]; then
  echo "Map YAML not found: $PWD/$MAP"
  echo "Run Lab 2 and save map first: ./scripts/lab2_save_map.sh maps/lab_map"
  exit 1
fi
MAP_ABS="$(readlink -f "$MAP")"
echo "Starting official TurtleBot3 Navigation2 with map: $MAP_ABS"
echo "RMW=${RMW_IMPLEMENTATION:-default} ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:="$MAP_ABS"
