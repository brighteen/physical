#!/bin/bash
# ─────────────────────────────────────────────────────────────
# run.sh — M8 CP3 전체 실행 스크립트 (1줄 재실행용)
# 사용: bash run.sh [cp1|cp2|cp3|bridge]
# ─────────────────────────────────────────────────────────────
set -e

MODE=${1:-cp3}
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

echo "=== ND1 M8 run.sh | mode=${MODE} ==="

case "$MODE" in
  cp1)
    echo "CP1 robot_mover 실행"
    echo "  T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=empty"
    echo "  T2: ros2 run m8_robot robot_mover  ← 이 파일"
    ros2 run m8_robot robot_mover
    ;;

  cp2)
    echo "CP2 SLAM 4개 터미널 구성 안내"
    cat << 'EOF'
T1: ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze
T2: ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
T3: ros2 launch nav2_bringup rviz_launch.py
T4: ros2 run teleop_twist_keyboard teleop_twist_keyboard
[탐색 완료 후] ros2 run nav2_map_server map_saver_cli -f ~/map/my_map
EOF
    ;;

  cp3)
    echo "CP3 nav2_client 실행"
    ros2 run m8_robot cp3_nav2_client
    ;;

  bridge)
    echo "M7→M8 브릿지 실행"
    ros2 run m8_robot m7_to_ros2_bridge
    ;;

  *)
    echo "사용법: bash run.sh [cp1|cp2|cp3|bridge]"
    exit 1
    ;;
esac
