#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}"
