# ND1 M8 — ROS2 기초 및 로봇 시스템 통합

> TurtleBot4 + Gazebo 환경에서 ROS2 Publisher/Subscriber, SLAM, Nav2 자율 이동을 구현하는 PBL 템플릿

## 📝 프로젝트 개요

본 저장소는 **ND1 피지컬 AI 전문가 과정 M8 모듈**의 PBL 학습 산출물 템플릿입니다.
ROS2 Humble 기반으로 토픽 통신·SLAM 지도 생성·Nav2 자율 이동을 직접 구현하고,
M7(로봇공학 기초)에서 계산한 IK 결과를 ROS2 토픽으로 연동하는 파이프라인을 제공합니다.

### 핵심 결과 (작성 예시)

| 항목 | 결과 |
|------|------|
| CP1 cmd_vel 발행 주파수 | **≥ 2.0 Hz** ✓ |
| CP2 SLAM 커버리지 | **≥ 70 %** ✓ |
| CP3 Nav2 목표 도달 | **3 / 3** ✓ |
| 단위 테스트 통과 | **15 / 15** ✓ |

## 🛠 환경 설정 및 실행

### 1. ROS2 패키지 설치

```bash
sudo apt install -y \
    ros-humble-desktop \
    ros-humble-ros-gz \
    ros-humble-navigation2 ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-turtlebot4-simulator \
    ros-humble-teleop-twist-keyboard

source /opt/ros/humble/setup.bash
```

### 2. 워크스페이스 빌드

```bash
mkdir -p ~/ros2_ws/src
cp -r nd1_m8_template ~/ros2_ws/src/m8_robot
cd ~/ros2_ws
colcon build --packages-select m8_robot
source install/setup.bash
```

### 3. 환경 검증

```bash
python scripts/verify_environment.py
# ✅ 6/6 모두 통과 — 실습 준비 완료!
```

### 4. 단위 테스트 실행 (ROS2 불필요)

```bash
pip install pytest
pytest tests/ -v
# 15 passed (ROS2 미설치 시 test_ros2_topics.py SKIPPED)
```

### 5. 실습 실행

```bash
# CP1 — robot_mover (TODO 3개 완성 후)
bash run.sh cp1

# CP2 — SLAM 지도 생성 (4개 터미널 — RUNBOOK.md 섹션 4 참조)
bash run.sh cp2

# CP3 — Nav2 자율 이동 (TODO 2개 완성 후)
bash run.sh cp3

# M7 → M8 브릿지 (M7 IK 결과 → /joint_states)
bash run.sh bridge
```

> 📋 **전체 재현 절차**는 `RUNBOOK.md` 참조 — CP0~CP3 + CP1 심화 단계별 정리

## 📂 디렉터리 구조

```
nd1_m8_studentname/
├── README.md           ⭐ 채점 시 가장 먼저 읽힘
├── RUNBOOK.md          재현 절차 (CP1~CP3 + 오류 대응)
├── requirements.txt    Python 의존성 (pytest, numpy, matplotlib)
├── package.xml         ROS2 패키지 메타데이터
├── setup.py            ROS2 엔트리포인트 등록
├── run.sh              CP 실행 단축 스크립트
├── .gitignore          빌드 아티팩트 · 지도 파일 제외
│
├── m8_robot/           핵심 ROS2 노드 (재사용 가능)
│   ├── __init__.py
│   ├── cp0_square_mover.py     Turtlesim 정사각형 주행 (완성본, 워밍업)
│   ├── cp1_robot_mover.py      /cmd_vel 발행 + /odom 수신 [TODO 3개]
│   ├── cp1_5_sensor_filter.py  LaserScan 이상치 필터링 → RViz2 (CP1 심화)
│   ├── cp2_slam_mapper.py      SLAM 커버리지 모니터 (완성본)
│   ├── cp3_nav2_client.py      Nav2 3목표 자율 이동 [TODO 2개]
│   └── m7_to_ros2_bridge.py    M7 IK 결과 → /joint_states 발행
│
├── tests/              단위 테스트 (ROS2 불필요)
│   ├── conftest.py             pytest 전역 설정 (ROS2 SKIP 처리)
│   ├── test_coverage_calc.py   CP2 커버리지 계산 로직 (8 testcase)
│   ├── test_nav2_goals.py      CP3 쿼터니언 변환 + 목표 좌표 (7 testcase)
│   └── test_ros2_topics.py     ROS2 메시지 타입 검증 (ROS2 환경 전용)
│
├── scripts/            보조 스크립트
│   ├── analyze_map.py          CP2 지도 커버리지 분석 (PGM 파일 읽기)
│   └── verify_environment.py   실습 환경 사전 검증 (6개 항목)
│
├── notebooks/          학습용 Jupyter 노트북 (ROS2 불필요)
│   └── 01_quickstart.ipynb     CP1~CP3 + CP1심화 사전 개념 확인
│
├── results/            산출물 (실행 시 생성 또는 스크린샷 저장)
│   ├── M8_cp1_odom_log.png     CP1 odom 로그 스크린샷       ✅ 필수
│   ├── M8_cp2_map.pgm          SLAM 지도 파일               ✅ 필수
│   ├── M8_cp3_success_log.png  CP3 완료 로그 스크린샷       ✅ 필수
│   ├── M8_cp1_shimhwa_rviz.png CP1 심화 RViz2 스크린샷     가산점 +4
│   ├── M8_cp2_coverage_sim.png 커버리지 시뮬 (노트북 생성)  권장
│   └── M8_cp3_goals.png        목표 좌표 시각화 (노트북 생성) 권장
│
├── docs/               참고 문서
│   └── README_docs.md          교재·PPT·외부 참고자료 링크
│
└── solutions/          ⚠️ 강사용 모범답안 — 학생 배포 금지
    ├── cp1_robot_mover_solution.py
    ├── cp3_nav2_client_solution.py
    └── README.md
```

## 🔬 핵심 구현 포인트

### CP1 — Publisher/Subscriber 패턴

```python
# TODO 1: Publisher 생성
self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

# TODO 2: Subscriber 생성
self.sub = self.create_subscription(Odometry, '/odom', self._odom_cb, 10)

# TODO 3: Twist 발행
msg = Twist()
msg.linear.x = 0.2   # 0.2 m/s 전진
self.pub.publish(msg)
```

### CP2 — SLAM 커버리지 공식

```
free_ratio = free_cells / (free_cells + occupied_cells) × 100 %
목표: free_ratio ≥ 70 %
```

### CP3 — Nav2 ActionClient 핵심 3원칙

```python
# ① header.stamp 반드시 설정 (TF lookup 실패 방지)
goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

# ② 상수 사용 (매직넘버 4 금지)
return status == GoalStatus.STATUS_SUCCEEDED

# ③ MultiThreadedExecutor 필수
executor = MultiThreadedExecutor()
executor.add_node(node)
threading.Thread(target=executor.spin, daemon=True).start()
```

## 📊 PBL 평가 기준

| 항목 | 배점 | 합격 기준 |
|------|------|----------|
| CP1 robot_mover | 30 | cmd_vel ≥ 2Hz · odom 로그 · Gazebo 전진 |
| CP2 SLAM 지도 | 30 | 커버리지 ≥ 70% · my_map.yaml 저장 |
| CP3 Nav2 3목표 | 40 | "목표 1/2/3 도달 완료!" 로그 3줄 |
| **합계** | **100** | 이수 기준: 70점 이상 |
| CP1 심화 (가산점) | +4 | /obstacle_markers 빨간 구 + [CP1 심화] 로그 |
| RUNBOOK.md | +3 | CP1·CP2·CP3 재현 절차 기술 |
| README 8항목 + 영상 | +2 | 8항목 완성 + 데모 영상 링크 |
| rosbag2 제출 | +1 | CP3 .db3 파일 존재 |

## 📈 결과 해설 (작성 예시)

| CP | 검증 항목 | 결과 | 비고 |
|----|----------|------|------|
| CP1 | cmd_vel 주파수 | 2.0 Hz | `ros2 topic hz /cmd_vel` |
| CP2 | 커버리지 | 75.2 % | `[CP2] ✅ 커버리지 목표 달성` |
| CP3 | 목표 1 도달 | ✓ 45s | `[CP3] ★ 목표 1 도달 완료!` |
| CP3 | 목표 2 도달 | ✓ 38s | `[CP3] ★ 목표 2 도달 완료!` |
| CP3 | 목표 3 도달 | ✓ 51s | `[CP3] ★ 목표 3 도달 완료!` |
| CP1 심화 | 유효 포인트 | 312/360 | `[CP1 심화] 유효 포인트: 312/360` |

## 🚀 향후 개선 (선택)

- [ ] CP3 목표 좌표를 본인 지도에 맞게 수정 (`GOALS` 리스트)
- [ ] CP1 심화: 필터링 임계값 튜닝 (`range_min`, `range_max`)
- [ ] 실습 4 (미니프로젝트): LLM 명령 → `/cmd_vel` 연동 *(M13·캡스톤 준비)*
- [ ] rosbag2 녹화·재생으로 CP3 경로 분석
- [ ] PyBullet / Isaac Sim 물리 시뮬레이션 연동 (M13)

## 🌉 M7 → M8 브릿지

```bash
# Dry-run 모드 (ROS2 미설치 환경 — IK 계산 + 메시지 구조 출력)
python -m m8_robot.m7_to_ros2_bridge

# ROS2 Humble 환경
source /opt/ros/humble/setup.bash
ros2 run m8_robot m7_to_ros2_bridge
# → /joint_states 발행 → RViz2 로봇 팔 실시간 시각화
```

**핵심**: M7의 `numerical_ik()` 출력(θ) → `sensor_msgs/JointState` → ROS2 표준 인터페이스

## 📚 참고 자료

- **ROS2 Humble 공식 문서**: https://docs.ros.org/en/humble/
- **Nav2 공식 문서**: https://navigation.ros.org/
- **SLAM Toolbox**: https://github.com/SteveMacenski/slam_toolbox
- **TurtleBot4**: https://turtlebot.github.io/turtlebot4-user-manual/
- Macenski et al., *The Marathon 2* (IROS 2020) — SLAM Toolbox 원논문
- Macenski et al., *Nav2* (ICRA 2023)

## 📜 라이선스

MIT License — 학습·포트폴리오 자유 활용

---

**© ND1 피지컬 AI 전문가 과정 / Module 8 — ROS2 기초 및 로봇 시스템 통합**
