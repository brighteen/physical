#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
echo "Stopping RViz/Gazebo/Nav2/TurtleBot3 processes..."
pkill -f rviz2 || true
pkill -f nav2 || true
pkill -f bt_navigator || true
pkill -f planner_server || true
pkill -f controller_server || true
pkill -f map_server || true
pkill -f amcl || true
pkill -f slam_toolbox || true
pkill -f turtlebot3_teleop || true
pkill -f turtlebot3_gazebo || true
pkill -f gzserver || true
pkill -f gzclient || true
ros2 daemon stop || true
rm -f /dev/shm/fastrtps_* 2>/dev/null || true
rm -f /dev/shm/sem.fastrtps_* 2>/dev/null || true
ros2 daemon start || true
echo "ROS reset done. RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}" 
