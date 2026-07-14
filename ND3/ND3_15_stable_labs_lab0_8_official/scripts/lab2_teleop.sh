#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
echo "Starting TurtleBot3 teleop. Use keyboard window focus."
ros2 run turtlebot3_teleop teleop_keyboard
