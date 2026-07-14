#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"

echo "== RMW / Environment =="
echo "ROS_DISTRO=${ROS_DISTRO:-not_set}"
echo "TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL:-not_set}"
echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-not_set}"
echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"

echo
echo "== Nav2 nodes =="
ros2 node list | sort | grep -E "map_server|amcl|planner|controller|bt_navigator|lifecycle" || true

echo
echo "== Lifecycle states with timeout =="
for n in /map_server /amcl /planner_server /controller_server /bt_navigator; do
  printf "%-24s" "$n"
  timeout 3 ros2 lifecycle get "$n" || echo "[TIMEOUT/MISSING]"
done

echo
echo "== Lifecycle note =="
echo "This script only reports state. If nodes are inactive, wait for launch bringup or set the initial pose."

echo
echo "== /map topic =="
ros2 topic list -t | grep -E "^/map|/map_metadata" || echo "[MISS] /map not visible"
if timeout 5 ros2 topic echo /map --once --qos-durability transient_local --qos-reliability reliable >/tmp/nd3_map_echo.txt 2>&1; then
  echo "[OK] /map sample available"
else
  echo "[WARN] /map sample unavailable"
  cat /tmp/nd3_map_echo.txt || true
fi
