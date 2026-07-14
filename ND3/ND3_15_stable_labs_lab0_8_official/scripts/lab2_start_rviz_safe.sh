#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$SCRIPT_DIR/env.sh"

RVIZ_CONFIG="${1:-$ROOT_DIR/rviz/lab2_slam.rviz}"

echo "Starting RViz with software rendering fallback..."
echo "Lab 2 RViz config: $RVIZ_CONFIG"
echo "If the map is still blank, run: ./scripts/lab2_map_status.sh"

if ! ros2 node list 2>/dev/null | grep -qx "/slam_toolbox"; then
  echo "[WARN] /slam_toolbox node is not visible yet."
  echo "       Start SLAM first in another terminal: bash scripts/lab2_start_slam_toolbox.sh"
fi

if [ -f "$RVIZ_CONFIG" ]; then
  QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-xcb} LIBGL_ALWAYS_SOFTWARE=${LIBGL_ALWAYS_SOFTWARE:-1} rviz2 -d "$RVIZ_CONFIG" --ros-args -p use_sim_time:=True
else
  echo "[WARN] RViz config not found. Starting default RViz."
  QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-xcb} LIBGL_ALWAYS_SOFTWARE=${LIBGL_ALWAYS_SOFTWARE:-1} rviz2 --ros-args -p use_sim_time:=True
fi
