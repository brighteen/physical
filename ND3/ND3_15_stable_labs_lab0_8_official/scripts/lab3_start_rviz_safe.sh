#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
echo "Starting RViz. In RViz: Fixed Frame=map, Add Map display /map, Durability=Transient Local."
QT_QPA_PLATFORM=${QT_QPA_PLATFORM:-xcb} LIBGL_ALWAYS_SOFTWARE=${LIBGL_ALWAYS_SOFTWARE:-1} rviz2 --ros-args -p use_sim_time:=True
