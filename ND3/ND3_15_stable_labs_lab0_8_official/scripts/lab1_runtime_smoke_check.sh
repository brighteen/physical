#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"

echo "== Lab 1 Runtime Smoke Check =="
fail=0
for t in /clock /scan /odom /tf; do
  if ros2 topic list | grep -qx "$t"; then echo "[OK] topic $t"; else echo "[MISS] topic $t"; fail=1; fi
done

echo "== Topic samples =="
for t in /scan /odom /clock; do
  if timeout 5 ros2 topic echo "$t" --once >/tmp/nd3_${t//\//_}.txt 2>&1; then echo "[OK] $t sample"; else echo "[MISS] $t sample"; cat /tmp/nd3_${t//\//_}.txt || true; fail=1; fi
done

echo "== TF check =="
if timeout 8 ros2 run tf2_ros tf2_echo odom base_link >/tmp/nd3_tf_base_link.txt 2>&1 && grep -q -E "Translation|Rotation" /tmp/nd3_tf_base_link.txt; then
  echo "[OK] odom -> base_link"
elif grep -q -E "Translation|Rotation" /tmp/nd3_tf_base_link.txt; then
  echo "[OK] odom -> base_link"
elif timeout 8 ros2 run tf2_ros tf2_echo odom base_footprint >/tmp/nd3_tf_base_footprint.txt 2>&1 && grep -q -E "Translation|Rotation" /tmp/nd3_tf_base_footprint.txt; then
  echo "[OK] odom -> base_footprint"
elif grep -q -E "Translation|Rotation" /tmp/nd3_tf_base_footprint.txt; then
  echo "[OK] odom -> base_footprint"
else
  echo "[WARN] odom -> base_link/base_footprint not confirmed yet"
fi

if [ "$fail" -eq 0 ]; then echo "[OK] Runtime smoke check passed."; else echo "[FAIL] Runtime smoke check failed."; exit 1; fi
