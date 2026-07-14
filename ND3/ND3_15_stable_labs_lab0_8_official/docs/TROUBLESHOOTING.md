# Troubleshooting — ND3-15 Stable Labs

## ROS2는 roscore가 없다

ROS2 Humble은 ROS1의 `roscore`를 사용하지 않는다. DDS discovery로 node/topic/action/service가 서로를 찾는다.

## rclpy import 오류

증상: `_rclpy_pybind11.cpython-313...` 오류.

원인: conda Python 3.13이 ROS2 Humble Python 3.10 패키지를 import하려고 함.

해결:

```bash
conda deactivate
conda deactivate
source scripts/env.sh
which python3
```

정상은 `/usr/bin/python3`.

## FastDDS SHM 오류

증상: `RTPS_TRANSPORT_SHM Error`, `fastrtps_port... open_and_lock_file failed`.

해결:

```bash
./scripts/reset_ros.sh
sudo apt install -y ros-humble-rmw-cyclonedds-cpp
source scripts/env.sh
echo $RMW_IMPLEMENTATION
```

정상은 `rmw_cyclonedds_cpp`.

## Lab 2 RViz에서 SLAM map이 안 보임

Lab 2는 `map_server`가 아니라 `slam_toolbox`가 `/map`을 만든다. 먼저 Gazebo와 SLAM이 둘 다 켜져 있는지 확인한다.

```bash
source scripts/env.sh
./scripts/lab2_map_status.sh
```

정상 조건:

- `/clock`, `/scan`, `/odom`, `/tf`, `/map` topic이 보인다.
- `/map` sample이 수신된다.
- RViz Fixed Frame이 `map`이다.
- RViz Map display의 Topic이 `/map`이다.

RViz에서 수동으로 확인할 항목:

1. 왼쪽 `Global Options`에서 `Fixed Frame=map`
2. `Add → By display type → Map`
3. Map display `Topic=/map`
4. Map display `Durability Policy=Transient Local`
5. 화면이 너무 확대/축소되어 있으면 `Focal Point`를 초기화하거나 마우스 휠로 줌아웃

처음에는 지도 크기가 아주 작거나 빈 것처럼 보일 수 있다. `lab2_teleop.sh`로 로봇을 천천히 움직여 `/scan`이 여러 방향에서 들어오면 map이 커진다.

RViz를 기본 설정으로 열었다면 Lab 2 전용 설정으로 다시 열 수 있다.

```bash
source scripts/env.sh
./scripts/lab2_start_rviz_safe.sh
```

## Lab 3 RViz에서 저장 map이 안 보임

1. `/map_server active` 확인
2. `/map` topic 확인
3. RViz에서 `Add → By display type → Map`
4. `Topic=/map`
5. `Durability Policy=Transient Local`
6. `Fixed Frame=map`

## AMCL initial pose 필요

증상: `AMCL cannot publish a pose... Please set the initial pose`.

해결: RViz의 `2D Pose Estimate` 또는:

```bash
./scripts/lab3_set_initial_pose.sh 0.0 0.0 0.0
ros2 run tf2_ros tf2_echo map odom
```

## Goal rejected

보통 원인:

- `bt_navigator` active가 아님
- `2D Pose Estimate`를 안 찍음
- `map -> odom` TF가 없음
- goal이 지도 밖 또는 장애물 위

확인:

```bash
./scripts/lab3_nav2_status.sh
ros2 run tf2_ros tf2_echo map odom
```

## Lab 6 costmap clear가 응답 없이 멈춤

Nav2를 CycloneDDS로 실행했는데 다른 터미널에서 기본 FastDDS로 service call을 하면 응답을 못 받을 수 있다.

```bash
source scripts/env.sh
echo $ROS_DOMAIN_ID
echo $RMW_IMPLEMENTATION
python3 scripts/lab6_practice.py --action clear
```

정상은 `ROS_DOMAIN_ID=30`, `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`이다. 장애물 삽입/삭제는 `/spawn_entity` 대신 `gz model`을 사용하므로, Gazebo가 켜져 있다면 아래처럼 단독 확인할 수 있다.

```bash
python3 scripts/lab6_practice.py --action spawn --model lab_box
gz model --model-name lab_box --pose
python3 scripts/lab6_practice.py --action delete --model lab_box
```
