# ND3-15 Lab 0~8 Runbook — Stable Official Version

## 운영 원칙

실시간 Navigation은 공식 TurtleBot3 Gazebo + 공식 TurtleBot3 Navigation2 launch를 사용한다. Planner/DWB 비교는 ROS2 lifecycle 불안정성을 줄이기 위해 Python offline 분석으로 분리한다.

## Python 실습 스크립트

각 Lab의 동작을 직접 수정하며 연습할 수 있도록 `scripts/lab0_practice.py` ~ `scripts/lab8_practice.py`를 추가했다. ROS/Gazebo가 필요한 Lab은 먼저 `source scripts/env.sh`를 실행한 뒤 사용한다.

```bash
python3 scripts/lab0_practice.py --skip-ros
python3 scripts/lab2_practice.py --action inspect-map --map maps/lab_map.yaml
python3 scripts/lab2_practice.py --action list-maps
python3 scripts/lab4_practice.py --list-algorithms
python3 scripts/lab4_practice.py --map maps/lab_map.yaml --algorithms astar rrt
python3 scripts/lab5_practice.py
python3 scripts/lab8_practice.py --mode preview
```

각 파일의 수정 가능한 파라미터와 실행 옵션은 아래처럼 확인한다.

```bash
python3 scripts/lab4_practice.py --help
```

## Lab 0 — 환경 점검

목표: Ubuntu 22.04, ROS2 Humble, TurtleBot3, Gazebo, Nav2, rclpy, Python 분석 코드가 준비되었는지 확인한다.

```bash
source scripts/env.sh
./scripts/lab0_env_check.sh
```

## Lab 1 — Gazebo 실행 및 runtime smoke check

터미널 1:

```bash
source scripts/env.sh
./scripts/lab1_start_gazebo.sh
```

터미널 2:

```bash
source scripts/env.sh
./scripts/lab1_runtime_smoke_check.sh
```

통과 기준: `/clock`, `/scan`, `/odom`, `/tf`가 존재하고 sample이 나온다.

## Lab 2 — SLAM 지도 생성

Gazebo를 켜둔 상태에서 SLAM Toolbox와 RViz, teleop을 실행한다. 지도가 어느 정도 만들어지면 `lab2_save_map.sh`로 저장한다.

```bash
./scripts/lab2_start_slam_toolbox.sh
./scripts/lab2_start_rviz_safe.sh
./scripts/lab2_teleop.sh
./scripts/lab2_save_map.sh maps/lab_map
```

통과 기준: `maps/lab_map.yaml`, `maps/lab_map.pgm` 생성.

RViz에서 map이 안 보이면 먼저 `/map` topic과 TF를 진단한다.

```bash
source scripts/env.sh
./scripts/lab2_map_status.sh
```

Lab 2의 RViz는 `rviz/lab2_slam.rviz`를 자동으로 사용한다. 수동으로 설정할 때는 `Fixed Frame=map`, Map display `Topic=/map`, `Durability=Transient Local`로 둔다.

### Lab 2-1 — 지도 파일 관리 실습

저장된 지도는 YAML 파일과 이미지 파일이 한 쌍이다. 삭제 전에 반드시 목록 확인과 백업을 먼저 한다.

```bash
python3 scripts/lab2_practice.py --action list-maps
python3 scripts/lab2_practice.py --action inspect-map --map maps/lab_map.yaml
python3 scripts/lab2_practice.py --action backup-map --map maps/lab_map.yaml
```

삭제 명령은 먼저 삭제 대상만 보여주고 멈춘다.

```bash
python3 scripts/lab2_practice.py --action delete-map --map maps/lab_map.yaml
```

출력된 `maps/lab_map.yaml`, `maps/lab_map.pgm` 대상이 맞는지 확인한 뒤 실제 삭제한다. 기본값은 삭제 전에 `maps/backups/` 아래에 한 번 더 백업한다.

```bash
python3 scripts/lab2_practice.py --action delete-map --map maps/lab_map.yaml --confirm-delete
```

백업에서 복구할 때는 백업 폴더명을 지정한다.

```bash
python3 scripts/lab2_practice.py --action restore-map --backup-dir maps/backups/lab_map_YYYYMMDD_HHMMSS
```

이미 같은 이름의 지도 파일이 있으면 복구가 막힌다. 덮어쓰려면 `--overwrite`를 추가한다.

## Lab 3 — 저장 지도 기반 공식 Nav2

SLAM은 종료하고 Gazebo와 official Navigation2만 실행한다.

```bash
./scripts/lab1_start_gazebo.sh
./scripts/lab3_start_nav2_official.sh maps/lab_map.yaml
./scripts/lab3_nav2_status.sh
./scripts/lab3_start_rviz_safe.sh
```

RViz에서 `Fixed Frame=map`, Map display `Topic=/map`, `Durability=Transient Local`, 이후 `2D Pose Estimate`를 먼저 찍고 `Nav2 Goal`을 보낸다.

터미널 초기 위치 대체:

```bash
./scripts/lab3_set_initial_pose.sh 0.0 0.0 0.0
```

터미널 goal 대체:

```bash
./scripts/lab3_send_goal.sh 0.5 0.0 0.0
```

## Lab 4 — Offline Planner 비교: Dijkstra, A*, Weighted A*, Greedy, RRT

기본 스크립트는 저장된 맵에서 여러 planner를 비교한다. 이 실습의 RRT는 Nav2 내부 planner가 아니라, 샘플링 기반 planner 개념을 관찰하기 위한 offline Python 구현이다.

```bash
python3 -m pip install -r requirements_python.txt
./scripts/lab4_planner_offline.sh maps/lab_map.yaml
```

산출물: `results/planner_metrics_offline.csv`, `results/planner_compare_offline.png`.

알고리즘 설명을 먼저 확인한다.

```bash
python3 scripts/lab4_practice.py --list-algorithms
```

원하는 planner만 골라서 비교할 수 있다.

```bash
./scripts/lab4_planner_offline.sh maps/lab_map.yaml --algorithms astar rrt

python3 scripts/lab4_practice.py \
  --map maps/lab_map.yaml \
  --start-x 0.0 --start-y 0.0 \
  --goal-x 1.0 --goal-y 1.0 \
  --algorithms dijkstra astar weighted_astar greedy rrt
```

RRT의 무작위성, 샘플 수, step 크기도 바꿔본다.

```bash
python3 scripts/lab4_practice.py \
  --map maps/lab_map.yaml \
  --algorithms astar rrt \
  --rrt-seed 21 \
  --rrt-iterations 8000 \
  --rrt-step-cells 8
```

비교 포인트:

- `planning_ms`: 계획 계산 시간
- `path_length_m`: 경로 길이
- `nodes_expanded`: grid planner는 확장 노드 수, RRT는 생성 vertex 수
- `status`, `error`: 실패한 planner가 있으면 이유 확인

## Lab 5 — DWB Safe/Agile 비교

```bash
./scripts/lab5_dwb_safe_agile_offline.sh
```

산출물: `results/dwb_safe_agile.csv`, `results/dwb_safe_agile.png`.

## Lab 6 — 장애물 및 costmap clear

Gazebo + Nav2 실행 중에 사용한다. 장애물 삽입/삭제는 `/spawn_entity`가 멈추는 환경을 피하려고 `gz model` 기반 스크립트를 사용한다.

```bash
./scripts/lab6_spawn_box.sh 0.5 0.0 0.25
./scripts/lab6_clear_costmaps.sh
./scripts/lab6_delete_box.sh
```

크기와 고정 여부를 바꿔 회피 난이도를 조절할 수 있다.

```bash
python3 scripts/lab6_practice.py --action cycle \
  --x 0.7 --y 0.2 --z 0.25 \
  --size-x 0.6 --size-y 0.3 --size-z 0.5 \
  --static \
  --wait-after-spawn 3 \
  --clear-timeout 15
```

프리셋 값을 쓰거나 임시로 덮어쓸 때:

```bash
python3 scripts/lab_params.py --lab lab6 --show-values
python3 scripts/lab_params.py --lab lab6 --set action=cycle --set size_x=0.6 --set dry_run=true
```

## Lab 7 — rosbag 기록

```bash
./scripts/lab7_record_bag.sh
```

RViz에서 goal을 보내고, 기록 터미널에서 Ctrl+C. 확인:

```bash
./scripts/lab7_bag_info.sh
```

## Lab 8 — mission 및 report

```bash
./scripts/lab8_run_mission.sh
./scripts/lab8_make_report.sh
```

## 최종 제출물

- `maps/lab_map.yaml`
- `maps/lab_map.pgm`
- `results/planner_metrics_offline.csv`
- `results/planner_compare_offline.png`
- `results/dwb_safe_agile.csv`
- `results/dwb_safe_agile.png`
- `results/nav2_*` rosbag 폴더
- RViz 캡처 이미지
- `results/final_report.md`
