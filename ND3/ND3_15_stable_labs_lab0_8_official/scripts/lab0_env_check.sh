#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"

echo "== Lab 0 Environment Check =="
echo "Ubuntu: $(lsb_release -ds 2>/dev/null || echo unknown)"
echo "ROS_DISTRO: ${ROS_DISTRO:-not_set}"
echo "TURTLEBOT3_MODEL: ${TURTLEBOT3_MODEL:-not_set}"
echo "ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:-not_set}"
echo "RMW_IMPLEMENTATION: ${RMW_IMPLEMENTATION:-default}"
echo "python3: $(command -v python3)"
python3 --version || true

echo
echo "== Required ROS packages =="
missing=0
for p in turtlebot3_gazebo turtlebot3_navigation2 turtlebot3_teleop slam_toolbox nav2_map_server nav2_msgs tf2_ros rviz2 gazebo_ros; do
  if ros2 pkg prefix "$p" >/dev/null 2>&1; then
    echo "[OK] $p"
  else
    echo "[MISS] $p"
    missing=1
  fi
done

echo
echo "== Python ROS import =="
if /usr/bin/python3 - <<'PY'
import rclpy
print('rclpy OK')
PY
then
  echo "[OK] rclpy with /usr/bin/python3"
else
  echo "[MISS] rclpy import failed. Disable conda or use /usr/bin/python3."
  missing=1
fi

echo
echo "== Map files =="
if [ -f maps/lab_map.yaml ] && [ -f maps/lab_map.pgm ]; then
  echo "[OK] maps/lab_map.yaml and maps/lab_map.pgm exist"
else
  echo "[INFO] maps/lab_map.* not found. Run Lab 2 SLAM and save map before Lab 3."
fi

echo
echo "== Static code check =="
python3 tools/static_check.py

if [ "$missing" -ne 0 ]; then
  echo "[WARN] Some runtime packages are missing. Install before ROS labs."
  exit 1
fi

echo "[OK] Lab 0 environment check completed."
