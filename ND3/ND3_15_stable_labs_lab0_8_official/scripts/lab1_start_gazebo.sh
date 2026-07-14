#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
echo "Starting TurtleBot3 Gazebo world..."
echo "TURTLEBOT3_MODEL=$TURTLEBOT3_MODEL ROS_DOMAIN_ID=$ROS_DOMAIN_ID RMW=${RMW_IMPLEMENTATION:-default}"
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
