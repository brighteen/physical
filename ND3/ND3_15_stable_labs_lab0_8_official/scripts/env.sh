#!/usr/bin/env bash
# Source this file in every terminal before running a lab script.
# It intentionally avoids `set -u` because ROS setup files may reference unset variables.

# If conda is active, prefer system Python for ROS2 Humble rclpy compatibility.
case "$(command -v python3 2>/dev/null || true)" in
  *miniconda*|*anaconda*)
    export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
    ;;
esac

if [ -f /opt/ros/humble/setup.bash ]; then
  set +u
  source /opt/ros/humble/setup.bash
fi

if [ -f "$HOME/turtlebot3_ws/install/setup.bash" ]; then
  set +u
  source "$HOME/turtlebot3_ws/install/setup.bash"
fi

export TURTLEBOT3_MODEL="${TURTLEBOT3_MODEL:-burger}"
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/nd3_matplotlib}"
mkdir -p "$MPLCONFIGDIR"

# Use CycloneDDS when installed to avoid repeated FastDDS SHM lock errors in lab PCs.
if command -v ros2 >/dev/null 2>&1 && ros2 pkg prefix rmw_cyclonedds_cpp >/dev/null 2>&1; then
  export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_cyclonedds_cpp}"
fi

export PYTHONUNBUFFERED=1
