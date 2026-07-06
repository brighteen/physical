# 📋 TurtleBot3 물류창고 자율주행 및 마커 우회 픽업 Runbook

본 문서는 가상 물류창고(Warehouse)에서 **TurtleBot3 Waffle Pi**가 SLAM 지도를 기반으로 자율주행(Nav2)을 수행하며, 주행 중 카메라로 ArUco 마커 상자를 감지하면 동적으로 경로를 우회하여 적재 후 최종 목적지까지 도달하는 통합 시나리오의 실행 가이드입니다.

---

## 🚀 시나리오 실행 단계 (총 6개의 터미널 실행)

모든 터미널 창을 독립적으로 열고 아래 단계에 따라 순차적으로 실행해 주십시오.

### 1단계: 가제보(Gazebo) 가상 창고 실행
창고 도면과 ArUco 마커 상자가 배치된 3D 월드를 구동합니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

# 가제보 모델 경로 병합
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models:/opt/ros/humble/share/aws_robomaker_small_warehouse_world/models:$HOME/.gazebo/models

# ⚡ WSL 환경에서 GPU 렌더링 병목으로 카메라 FPS가 0.6Hz까지 떨어지는 문제를 방지하기 위해
# 소프트웨어 렌더링으로 전환합니다. (이 설정이 없으면 ArUco 마커 인식이 불안정해집니다)
export LIBGL_ALWAYS_SOFTWARE=1

ros2 launch gazebo_ros gazebo.launch.py world:=/home/brightgu1/map/warehouse_with_boxes.world
```

### 2단계: robot_state_publisher 실행 (새 터미널)
로봇의 TF 상태를 퍼블리싱합니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

ros2 launch turtlebot3_gazebo robot_state_publisher.launch.py use_sim_time:=true
```

### 3단계: 로봇 소환 (Spawn) (새 터미널)
가제보 월드의 원점(0.0, 0.0)에 로봇을 생성합니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

ros2 launch turtlebot3_gazebo spawn_turtlebot3.launch.py x_pose:=0.0 y_pose:=0.0 z_pose:=0.01
```

### 4단계: Navigation2 (Nav2) 및 RViz2 구동 (새 터미널)
저장된 지도(`warehouse_map.yaml`)를 읽어와 자율주행 엔진 및 시각화 GUI를 기동합니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

export TURTLEBOT3_MODEL=waffle_pi

# OpenGL 그래픽 오류 방지 환경 변수
export LIBGL_ALWAYS_SOFTWARE=1

# 맵 지정 및 Nav2 런치 실행
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=true map:=/home/brightgu1/map/warehouse_map.yaml
```
> 💡 **초기 정렬 설정**: RViz2 창이 활성화되면 상단 메뉴에서 **`2D Pose Estimate`** 버튼을 클릭하고 지도 상의 로봇의 현재 실제 위치(가제보 상의 원점 방향)에 정렬되도록 녹색 화살표를 드래그하여 정렬합니다.

### 5단계: ArUco 마커 감지 노드 실행 (새 터미널)
카메라 이미지 속 마커를 인식하고 검출 정보를 퍼블리싱하는 비전 노드를 켭니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

python3 /home/brightgu1/aruco_detector.py
```

### 6단계: 동적 자율주행 미션 매니저 실행 (새 터미널)
FSM 기반의 시나리오 주행을 구동합니다.
```bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

python3 /home/brightgu1/tb3_nav_waypoint.py
```

---

## 🧭 미션 진행 모니터링
1. 6단계 실행 즉시 로봇이 **A 지점**으로 주행을 시작합니다.
2. A 지점에 도달하면 1초간 정차한 후, 최종 목적지인 **B 지점**으로 출발합니다.
3. B 지점으로 이동하는 중간 경로 영역에서 5단계 카메라 노드가 ArUco 상자를 시각적으로 검출하면 즉시 B로의 이동을 중단하고 **상자 앞 접근 포인트**로 진로를 변경합니다.
4. 상자 앞에 도달하면 3초간 머무른 뒤(적재 완료 모사), B 지점으로 최종 목적지를 재설정하여 최종 주행을 완수하고 멈춥니다.
