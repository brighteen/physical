# START HERE — ND3-15 Stable Labs

## 1. 압축 해제

```bash
cd ~/Desktop
unzip ND3_15_stable_labs_lab0_8_official.zip
cd ND3_15_stable_labs_lab0_8_official
chmod +x scripts/*.sh python/*.py
```

## 2. 모든 터미널 공통

새 터미널을 열 때마다:

```bash
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
```

## 3. Lab 0 — 환경 점검

```bash
./scripts/lab0_env_check.sh
```

## 4. Lab 1 — Gazebo 실행

터미널 1:

```bash
./scripts/lab1_start_gazebo.sh
```

터미널 2:

```bash
source scripts/env.sh
./scripts/lab1_runtime_smoke_check.sh
```

## 5. Lab 2 — SLAM 지도 생성

터미널 1은 Gazebo 유지.

터미널 2:

```bash
source scripts/env.sh
./scripts/lab2_start_slam_toolbox.sh
```

터미널 3:

```bash
source scripts/env.sh
./scripts/lab2_start_rviz_safe.sh
```

터미널 4:

```bash
source scripts/env.sh
./scripts/lab2_teleop.sh
```

지도 저장:

```bash
source scripts/env.sh
./scripts/lab2_save_map.sh maps/lab_map
```

## 6. Lab 3 — 공식 Nav2

SLAM 관련 터미널은 모두 종료한 뒤 진행합니다.

터미널 1:

```bash
source scripts/env.sh
./scripts/lab1_start_gazebo.sh
```

터미널 2:

```bash
source scripts/env.sh
./scripts/lab3_start_nav2_official.sh maps/lab_map.yaml
```

터미널 3:

```bash
source scripts/env.sh
./scripts/lab3_nav2_status.sh
```

터미널 4:

```bash
source scripts/env.sh
./scripts/lab3_start_rviz_safe.sh
```

RViz에서 `2D Pose Estimate`를 먼저 찍고 `Nav2 Goal`을 보냅니다.

## 7. Lab 4~5 — Python 안정형 분석

```bash
python3 -m pip install -r requirements_python.txt
./scripts/lab4_planner_offline.sh
./scripts/lab5_dwb_safe_agile_offline.sh
```

## 8. Lab 6~8 — 장애물, rosbag, mission, 보고서

```bash
./scripts/lab6_spawn_box.sh 0.5 0.0 0.25
./scripts/lab6_clear_costmaps.sh
./scripts/lab6_delete_box.sh
./scripts/lab7_record_bag.sh
./scripts/lab8_run_mission.sh
./scripts/lab8_make_report.sh
```
