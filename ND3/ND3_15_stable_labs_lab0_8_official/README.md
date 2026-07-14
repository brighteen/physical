# ND3-15 Stable Labs — TF · SLAM · Navigation · Nav2

이 자료는 **공식 TurtleBot3 Gazebo + 공식 TurtleBot3 Navigation2 launch**를 기준으로 만든 안정형 실습 자료입니다.
복잡한 custom Nav2 lifecycle 패키지 대신, 수업에서 먼저 성공해야 하는 기본 Navigation 흐름을 안정적으로 수행하도록 구성했습니다.

## 기준 범위

- Lab 0: 환경 점검
- Lab 1: Gazebo TurtleBot3 실행 및 runtime topic/TF 확인
- Lab 2: SLAM Toolbox 지도 생성 및 `maps/lab_map.yaml`, `maps/lab_map.pgm` 저장
- Lab 3: 저장 지도 기반 공식 Nav2 + AMCL + RViz Navigation
- Lab 4: Planner 비교 안정형 실습 — Python offline Dijkstra/A* 분석
- Lab 5: DWB Safe/Agile 안정형 실습 — Python offline 속도 정책 비교
- Lab 6: 장애물 삽입, costmap clear, recovery 관찰
- Lab 7: rosbag 기록 및 evidence 수집
- Lab 8: 다중 goal mission 및 최종 보고서 생성

## 왜 official launch를 기준으로 하는가

이전 custom `05_nav.sh` 방식은 planner YAML, lifecycle, component container, DDS 설정이 한꺼번에 섞이면서 환경에 따라 불안정할 수 있습니다. 이 안정판은 다음 원칙을 사용합니다.

1. Gazebo는 `turtlebot3_gazebo turtlebot3_world.launch.py` 사용
2. Navigation은 `turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=...` 사용
3. Planner/DWB 비교는 ROS2 lifecycle에 덜 의존하는 Python offline 실습으로 분리
4. RViz는 `use_sim_time:=True`, 필요 시 software rendering 사용
5. AMCL initial pose는 RViz `2D Pose Estimate` 또는 `scripts/set_initial_pose.sh` 사용

## 빠른 시작

```bash
cd ~/Desktop
unzip ND3_15_stable_labs_lab0_8_official.zip
cd ND3_15_stable_labs_lab0_8_official
chmod +x scripts/*.sh python/*.py
```

환경 점검:

```bash
source scripts/env.sh
./scripts/lab0_env_check.sh
```

Gazebo:

```bash
source scripts/env.sh
./scripts/lab1_start_gazebo.sh
```

공식 Navigation2:

```bash
source scripts/env.sh
./scripts/lab3_start_nav2_official.sh maps/lab_map.yaml
```

RViz:

```bash
source scripts/env.sh
./scripts/lab3_start_rviz_safe.sh
```

RViz에서 `Fixed Frame = map`, Map display `Topic=/map`, `Durability=Transient Local`, 그다음 `2D Pose Estimate` → `Nav2 Goal` 순서로 진행합니다.

## 지도 파일

`Lab 3`부터는 반드시 아래 두 파일이 필요합니다.

```text
maps/lab_map.yaml
maps/lab_map.pgm
```

없으면 Lab 2에서 SLAM으로 지도를 만든 뒤 저장하세요.

```bash
./scripts/lab2_save_map.sh maps/lab_map
```

## Lab별 Python3 실습 명령어

아래 명령어들은 `scripts/lab0_practice.py` ~ `scripts/lab8_practice.py`를 직접 실행하는 실습용 Python 명령어입니다. ROS/Gazebo/Nav2가 필요한 Lab은 새 터미널에서 먼저 `source scripts/env.sh`를 실행하세요.

각 스크립트의 전체 옵션은 다음 형식으로 확인할 수 있습니다.

```bash
python3 scripts/lab4_practice.py --help
```

### 파라미터 바꾸는 방법

파라미터는 세 가지 방식으로 바꿀 수 있습니다. 처음에는 명령어에서 바로 바꾸는 방식이 이해하기 쉽고, 반복 실습할 때는 YAML 프리셋을 수정하는 방식이 편합니다. 한 번만 값을 바꿔 시험할 때는 `lab_params.py --set`을 쓰면 YAML 파일을 망가뜨릴 위험이 적습니다.

방법 1: 명령어 뒤 옵션 값을 직접 바꿉니다.

```bash
python3 scripts/lab4_practice.py \
  --map maps/lab_map.yaml \
  --start-x 0.0 --start-y 0.0 \
  --goal-x 2.0 --goal-y 1.2 \
  --algorithms astar rrt \
  --rrt-seed 21
```

방법 2: [configs/lab_parameters.yaml](configs/lab_parameters.yaml)을 수정한 뒤, 그 값으로 명령을 만들거나 실행합니다.

```bash
python3 scripts/lab_params.py --lab lab4 --show-values
python3 scripts/lab_params.py --lab lab4 --run
```

방법 3: YAML은 그대로 두고 이번 실행에서만 값을 덮어씁니다.

```bash
python3 scripts/lab_params.py --lab lab6 \
  --set action=cycle \
  --set x=0.8 \
  --set size_x=0.6 \
  --set static=true \
  --set dry_run=true \
  --show-values
```

실제로 실행하려면 `dry_run=false`로 바꾸고 `--run`을 붙입니다. ROS/Gazebo/Nav2가 필요한 Lab은 먼저 `source scripts/env.sh`를 실행하세요.

`--run`을 붙이지 않으면 실제 실행하지 않고 실행될 명령어만 출력합니다. 먼저 명령어를 확인하고, 맞으면 `--run`을 붙이는 흐름을 권장합니다.

```bash
python3 scripts/lab_params.py --lab all
```

YAML 파라미터 이름은 `_`를 쓰고, 명령어 옵션은 `-`를 씁니다. 예를 들어 YAML의 `goal_x: 2.0`은 명령어의 `--goal-x 2.0`으로 변환됩니다.

YAML 작성 규칙:

- 숫자는 그대로 씁니다: `timeout: 120`, `safe_v: 0.15`
- 문자열 경로도 그대로 씁니다: `map: maps/lab_map.yaml`
- 켜고 끄는 값은 `true` 또는 `false`를 씁니다: `dry_run: true`
- 여러 개를 고르는 값은 목록으로 씁니다: `algorithms: [astar, rrt]`
- `null`은 해당 옵션을 명령어에 넣지 않는다는 뜻입니다.

자주 바꾸는 파라미터는 아래를 먼저 보면 됩니다.

| Lab | 자주 바꾸는 값 | 의미 |
| --- | --- | --- |
| Lab 0 | `skip_ros`, `static_check`, `strict` | ROS 포함 여부와 실패 처리 방식 |
| Lab 1 | `action`, `timeout`, `dry_run` | Gazebo 실행, topic check, 대기 시간 |
| Lab 2 | `action`, `map`, `prefix`, `confirm_delete`, `dry_run` | 지도 확인/저장/백업/삭제/복구 대상 |
| Lab 3 | `action`, `map`, `x`, `y`, `yaw`, `timeout` | Nav2 상태 확인, 초기 위치, goal 위치 |
| Lab 4 | `start_x`, `start_y`, `goal_x`, `goal_y`, `algorithms`, `rrt_seed` | planner 비교 시작점/목표점/알고리즘 |
| Lab 5 | `safe_v`, `safe_w`, `agile_v`, `agile_w`, `target_x`, `target_y` | DWB safe/agile 속도 정책 |
| Lab 6 | `action`, `x`, `y`, `z`, `size_x`, `size_y`, `size_z`, `static`, `wait_after_spawn` | 장애물 위치/크기/고정 여부, 관찰 대기 |
| Lab 7 | `duration`, `topics`, `bag` | rosbag 기록 시간과 topic 목록 |
| Lab 8 | `mode`, `waypoints`, `timeout`, `output` | mission waypoint와 report 출력 |

주의: Lab 2의 지도 삭제는 `confirm_delete: true` 또는 `--confirm-delete`가 있어야 실제로 삭제됩니다. `dry_run: true`로 먼저 연습하면 파일을 지우지 않고 삭제 절차만 확인할 수 있습니다.



```bash
bash scripts/reset_ros.sh
```

### Lab 0 — 환경 점검

```bash
source scripts/env.sh
bash scripts/lab0_env_check.sh
python3 scripts/lab0_practice.py --static-check --strict
```

### Lab 1 — Gazebo 실행 및 기본 Topic 확인

터미널 1, Gazebo:

```bash
source scripts/env.sh
bash scripts/lab1_start_gazebo.sh
```

터미널 2, runtime check:

```bash
source scripts/env.sh
bash scripts/lab1_runtime_smoke_check.sh
python3 scripts/lab1_practice.py --action check --timeout 5
```

### Lab 2 — SLAM 지도 생성 및 Map 관리

터미널 1은 Lab1 Gazebo를 계속 켜둡니다.

터미널 2, SLAM:

```bash
source scripts/env.sh
bash scripts/lab2_start_slam_toolbox.sh
```

터미널 3, RViz:

```bash
source scripts/env.sh
bash scripts/lab2_start_rviz_safe.sh
```

터미널 4, 로봇 이동:

```bash
source scripts/env.sh
bash scripts/lab2_teleop.sh
```

터미널 5, map 상태 확인 및 저장:

```bash
source scripts/env.sh
bash scripts/lab2_map_status.sh
bash scripts/lab2_save_map.sh maps/lab_map
```

저장된 map 파일 확인/백업/삭제/복구:

```bash
python3 scripts/lab2_practice.py --action inspect-map --map maps/lab_map.yaml
python3 scripts/lab2_practice.py --action list-maps
python3 scripts/lab2_practice.py --action backup-map --map maps/lab_map.yaml
python3 scripts/lab2_practice.py --action delete-map --map maps/lab_map.yaml
python3 scripts/lab2_practice.py --action delete-map --map maps/lab_map.yaml --confirm-delete
python3 scripts/lab2_practice.py --action restore-map --backup-dir maps/backups/lab_map_YYYYMMDD_HHMMSS --overwrite
```

### Lab 3 — 저장 Map 기반 Nav2

SLAM 관련 터미널을 끄고 새로 시작합니다.

터미널 1, Gazebo:

```bash
source scripts/env.sh
bash scripts/lab1_start_gazebo.sh
```

터미널 2, Nav2:

```bash
source scripts/env.sh
bash scripts/lab3_start_nav2_official.sh maps/lab_map.yaml
```

터미널 3, 상태 확인 및 goal:

```bash
source scripts/env.sh
bash scripts/lab3_nav2_status.sh
bash scripts/lab3_set_initial_pose.sh 0.0 0.0 0.0
bash scripts/lab3_send_goal.sh 0.5 0.0 0.0
python3 scripts/lab3_practice.py --action stop
```

터미널 4, RViz:

```bash
source scripts/env.sh
bash scripts/lab3_start_rviz_safe.sh
```

Python 실습 스크립트로도 같은 작업을 할 수 있습니다.

```bash
python3 scripts/lab3_practice.py --action map-check --map maps/lab_map.yaml
python3 scripts/lab3_practice.py --action status
python3 scripts/lab3_practice.py --action initial-pose --x 0.0 --y 0.0 --yaw 0.0
python3 scripts/lab3_practice.py --action goal --x 0.5 --y 0.0 --yaw 0.0 --timeout 120
```

### Lab 4 — Planner 비교

```bash
python3 scripts/lab4_practice.py --list-algorithms
python3 scripts/lab4_practice.py \
  --map maps/lab_map.yaml \
  --start-x 0.0 --start-y 0.0 \
  --goal-x 1.0 --goal-y 1.0 \
  --algorithms dijkstra astar weighted_astar greedy rrt
```

Shell wrapper:

```bash
bash scripts/lab4_planner_offline.sh maps/lab_map.yaml
```

### Lab 5 — DWB Safe/Agile 비교

```bash
python3 scripts/lab5_practice.py
python3 scripts/lab5_practice.py \
  --safe-v 0.12 --safe-w 0.7 \
  --agile-v 0.30 --agile-w 1.4 \
  --target-x 2.0 --target-y 0.8
bash scripts/lab5_dwb_safe_agile_offline.sh
```

### Lab 6 — 장애물 삽입, Costmap Clear, 삭제

Gazebo + Nav2가 켜진 상태에서 실행합니다.

```bash
source scripts/env.sh
명령어 한줄씩 실행

python3 scripts/lab6_practice.py --action cycle --dry-run

python3 scripts/lab6_practice.py --action spawn --x 0.5 --y 0.0 --z 0.25 --model lab_box

python3 scripts/lab6_practice.py --action clear

python3 scripts/lab6_practice.py --action delete --model lab_box
```

크기/색상/고정 장애물 파라미터를 바꿔 실행합니다.

```bash
python3 scripts/lab6_practice.py --action cycle \
  --x 0.7 --y 0.2 --z 0.25 --model lab_box_big \
  --size-x 0.6 --size-y 0.3 --size-z 0.5 \
  --mass 2.0 \
  --color 0.1 0.4 1.0 1.0 \
  --static \
  --wait-after-spawn 3 \
  --clear-timeout 15
```

Shell wrapper:

```bash
bash scripts/lab6_spawn_box.sh 0.5 0.0 0.25
bash scripts/lab6_clear_costmaps.sh 15
bash scripts/lab6_delete_box.sh lab_box
```

### Lab 7 — Rosbag 기록 및 확인

Gazebo + Nav2가 켜진 상태에서 실행합니다.

```bash
source scripts/env.sh
python3 scripts/lab7_practice.py --action topics
python3 scripts/lab7_practice.py --action record --duration 30
python3 scripts/lab7_practice.py --action info
python3 scripts/lab7_practice.py --action info --bag results/nav2_YYYYMMDD_HHMMSS
```

Shell wrapper:

```bash
bash scripts/lab7_record_bag.sh
bash scripts/lab7_bag_info.sh
```

### Lab 8 — Mission 및 최종 보고서

Nav2가 켜진 상태에서 mission을 실행합니다.

```bash
source scripts/env.sh
python3 scripts/lab8_practice.py --mode preview --waypoints docs/waypoints_default.csv
python3 scripts/lab8_practice.py --mode mission --waypoints docs/waypoints_default.csv --timeout 120
python3 scripts/lab8_practice.py --mode report --output results/final_report.md
python3 scripts/lab8_practice.py --mode both --waypoints docs/waypoints_default.csv --output results/final_report.md
```

Shell wrapper:

```bash
bash scripts/lab8_run_mission.sh
bash scripts/lab8_make_report.sh
```

### YAML 파라미터로 실행

[configs/lab_parameters.yaml](configs/lab_parameters.yaml)을 수정한 뒤 명령을 확인하거나 실행합니다.

```bash
python3 scripts/lab_params.py --lab all
python3 scripts/lab_params.py --lab lab4 --show-values
python3 scripts/lab_params.py --lab lab4 --run
python3 scripts/lab_params.py --lab lab6 --set action=cycle --set size_x=0.6 --set static=true --set dry_run=true --show-values
```

### 최종 점검

```bash
python3 tools/static_check.py
bash scripts/run_python_offline_tests.sh
find maps -maxdepth 1 -type f -print
find results -maxdepth 2 -type f -print
```

## 안정성 주의

- ROS2 Humble은 Python 3.10 기준입니다. conda Python 3.13이 앞에 있으면 `rclpy` import가 깨질 수 있습니다.
- FastDDS shared memory 오류가 반복되면 `CycloneDDS`를 사용합니다. `scripts/env.sh`는 설치되어 있으면 `rmw_cyclonedds_cpp`를 우선 사용합니다.
- `roscore`는 필요 없습니다. ROS2는 DDS discovery로 노드가 서로를 찾습니다.
