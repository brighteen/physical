#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"

echo "== Lab 2 SLAM / RViz map status =="
echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-not_set}"
echo "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"
echo

echo "== Nodes =="
ros2 node list | sort | grep -E "slam|gazebo|robot_state|rviz" || true
echo

echo "== Required topics =="
fail=0
for topic in /clock /scan /odom /tf /map; do
  if ros2 topic list | grep -qx "$topic"; then
    echo "[OK] $topic"
  else
    echo "[MISS] $topic"
    fail=1
  fi
done
echo

echo "== /map topic info =="
if ros2 topic list | grep -qx /map; then
  ros2 topic info -v /map || true
  echo
  echo "== Try reading one /map sample =="
  if timeout 8 ros2 topic echo /map --once --qos-durability transient_local --qos-reliability reliable >/tmp/nd3_lab2_map_echo.txt 2>&1; then
    echo "[OK] /map sample received with transient_local/reliable"
  elif timeout 8 ros2 topic echo /map --once >/tmp/nd3_lab2_map_echo.txt 2>&1; then
    echo "[OK] /map sample received with default QoS"
  else
    echo "[MISS] /map sample not received yet"
    cat /tmp/nd3_lab2_map_echo.txt || true
    fail=1
  fi
else
  echo "[MISS] /map topic is not visible. SLAM Toolbox may not be running or has not received scan/odom yet."
fi
echo

echo "== TF checks =="
if timeout 5 ros2 run tf2_ros tf2_echo odom base_link >/tmp/nd3_lab2_tf_echo.txt 2>&1 || grep -q "Translation:" /tmp/nd3_lab2_tf_echo.txt; then
  echo "[OK] odom -> base_link"
elif timeout 5 ros2 run tf2_ros tf2_echo odom base_footprint >/tmp/nd3_lab2_tf_echo.txt 2>&1 || grep -q "Translation:" /tmp/nd3_lab2_tf_echo.txt; then
  echo "[OK] odom -> base_footprint"
else
  echo "[WARN] odom -> base_link/base_footprint not confirmed"
  cat /tmp/nd3_lab2_tf_echo.txt || true
fi

if timeout 5 ros2 run tf2_ros tf2_echo map odom >/tmp/nd3_lab2_map_odom.txt 2>&1 || grep -q "Translation:" /tmp/nd3_lab2_map_odom.txt; then
  echo "[OK] map -> odom"
else
  echo "[WARN] map -> odom not confirmed yet. This can happen before SLAM publishes the map frame."
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "[OK] Lab 2 map pipeline looks ready. In RViz use Fixed Frame=map and Map Topic=/map."
else
  echo "[CHECK] Fix missing items above, then restart RViz or run this script again."
  exit 1
fi
