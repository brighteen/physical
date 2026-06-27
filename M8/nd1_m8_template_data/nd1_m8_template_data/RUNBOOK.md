# M8 Runbook — ROS2 기초 및 로봇 시스템 통합

> ND1 피지컬 AI 전문가 과정 · M8 · 유형 B (실습중심형)
> 검증 환경: Ubuntu 22.04 LTS / ROS2 Humble / Gazebo Fortress 6.x / TurtleBot4 Simulator
> 작성 기준: 2026-05 | 무단 배포 금지

---

## 1. 시스템 구성 개요

```
[Gazebo Fortress]
    └─ TurtleBot4 시뮬레이터
          ├─ /cmd_vel  ← robot_mover / Nav2
          ├─ /odom     → robot_mover
          ├─ /scan     → sensor_filter, SLAM Toolbox
          └─ /map      ← SLAM Toolbox → Nav2

[ROS2 Humble 노드 그래프]
  cp1_robot_mover      : /cmd_vel ← Twist (2 Hz)
  cp1_5_sensor_filter  : /scan → /obstacle_markers
  cp2_slam_mapper      : /map → 커버리지 모니터
  cp3_nav2_client      : NavigateToPose Action Client
  m7_to_ros2_bridge    : IK 결과 → /joint_states
```

---

## 2. CP1 재현 절차 — robot_mover

```bash
# 터미널 1: Gazebo 실행
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=empty

# 터미널 2: robot_mover 실행
source ~/ros2_ws/install/setup.bash
ros2 run m8_robot robot_mover

# 터미널 3: 토픽 발행 확인
ros2 topic hz /cmd_vel       # ≥ 2.0 Hz 확인 ★필수
ros2 topic echo /cmd_vel     # linear.x 값 확인
```

### 합격 기준 확인

| 확인 항목 | 명령 | 기대값 |
|----------|------|--------|
| 발행 주파수 | `ros2 topic hz /cmd_vel` | average rate: ≥ 2.000 |
| 위치 로그 | 터미널 2 출력 | `[CP1] 위치: x=..., y=...` |
| Gazebo 이동 | 시각 확인 | 로봇 전진 |

---

## 3. CP1 심화 재현 절차 — sensor_filter (가산점 +4)

```bash
# Gazebo + TurtleBot4 실행 상태에서

# 터미널 2: sensor_filter 실행
ros2 run m8_robot sensor_filter

# 터미널 3: RViz2 실행
ros2 run rviz2 rviz2
# → Fixed Frame: base_scan
# → Add → MarkerArray → Topic: /obstacle_markers
```

### 합격 기준 확인

| 확인 항목 | 기대값 |
|----------|--------|
| 터미널 로그 | `[CP1 심화] 유효 포인트: N/360` |
| RViz2 화면 | /obstacle_markers 빨간 구 표시 |

---

## 4. CP2 재현 절차 — SLAM 지도 생성

```bash
# 터미널 1: Gazebo maze world
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze

# 터미널 2: SLAM Toolbox
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true

# 터미널 3: RViz2
ros2 launch nav2_bringup rviz_launch.py

# 터미널 4: 텔레옵 (커버리지 ≥ 70% 달성까지 탐색)
ros2 run teleop_twist_keyboard teleop_twist_keyboard
# 주의: 속도 linear.x ≤ 0.2 m/s 유지 (스캔 매칭 실패 방지)

# [커버리지 달성 후] 지도 저장
ros2 run nav2_map_server map_saver_cli -f ~/map/my_map
```

### 합격 기준 확인

| 확인 항목 | 명령 | 기대값 |
|----------|------|--------|
| 지도 파일 | `ls ~/map/` | my_map.yaml + my_map.pgm |
| 커버리지 로그 | 터미널 2 | `[CP2] ✅ 커버리지 목표 달성 (≥ 70%)` |

---

## 5. CP3 재현 절차 — Nav2 3목표 자율 이동

```bash
# CP2 완료 (my_map.yaml 존재) 상태에서

# 터미널 1: Gazebo maze world
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py world:=maze

# 터미널 2: Nav2 bringup
ros2 launch nav2_bringup bringup_launch.py \
    map:=$HOME/map/my_map.yaml \
    use_sim_time:=true

# 터미널 3: RViz2 → 2D Pose Estimate ★필수
ros2 launch nav2_bringup rviz_launch.py
# → RViz2 상단 '2D Pose Estimate' 클릭 → 로봇 초기 위치 클릭 지정

# 터미널 4: cp3_nav2_client 실행
ros2 run m8_robot cp3_nav2_client
```

### 합격 기준 확인

| 확인 항목 | 기대값 |
|----------|--------|
| 목표 1 | `[INFO] 목표 1 도달 완료!` |
| 목표 2 | `[INFO] 목표 2 도달 완료!` |
| 목표 3 | `[INFO] 목표 3 도달 완료!` |
| 완료 | `[CP3] ★ 모든 목표 완료!` |

---

## 6. 주요 오류 대응

| 오류 메시지 | 원인 | 해결 |
|-----------|------|------|
| `ros2: command not found` | source 누락 | `source /opt/ros/humble/setup.bash` |
| Gazebo 검은 화면 | GPU 미지원 | `export LIBGL_ALWAYS_SOFTWARE=1` |
| `Nav2 목표 거부됨` | AMCL 초기화 미완료 | RViz2에서 2D Pose Estimate 클릭 |
| `TF lookup failed` | `header.stamp` 누락 | `self.get_clock().now().to_msg()` 사용 |
| CP3 deadlock | spin 중복 | MultiThreadedExecutor 패턴 적용 |
| `Package not found` | setup.bash 미소스 | `source install/setup.bash` |

---

## 7. 환경 검증 명령

```bash
# ROS2 버전 확인
ros2 --version         # ROS 2 humbled ...

# 필수 패키지 확인
ros2 pkg list | grep turtlebot4
ros2 pkg list | grep slam_toolbox
ros2 pkg list | grep nav2

# 워크스페이스 빌드 상태
cd ~/ros2_ws && colcon build --packages-select m8_robot
source install/setup.bash
ros2 run m8_robot --help
```
