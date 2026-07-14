#!/usr/bin/env bash
# 파일명: master_launch.sh

echo "==== ROS2 멀티 터미널 자동 제어를 시작합니다 ===="

# 1번 새 창: 가제보 시뮬레이터 실행
cmd.exe /c start wsl -d Ubuntu bash -c "source /opt/ros/humble/setup.bash; cd ~/ND3_15_stable_labs_lab0_8_official; ./scripts/lab1_start_gazebo.sh; exec bash"

# 2번 새 창: ROS2 Talker(송신 노드) 실행
cmd.exe /c start wsl -d Ubuntu bash -c "source /opt/ros/humble/setup.bash; ros2 run demo_nodes_cpp talker; exec bash"

# 3번 새 창: ROS2 Listener(수신 노드) 실행
cmd.exe /c start wsl -d Ubuntu bash -c "source /opt/ros/humble/setup.bash; ros2 run demo_nodes_cpp listener; exec bash"

echo "==== 모든 터미널 창이 독립적으로 구동되었습니다 ===="