# solutions/ — 강사용 모범답안 폴더

> ⚠️ 강사 전용 — 학생에게 배포 금지

---

## 구성

| 파일 | 대응 스켈레톤 | TODO 완성 내용 |
|------|------------|-------------|
| `cp1_robot_mover_solution.py` | `m8_robot/cp1_robot_mover.py` | TODO 1(Publisher), TODO 2(Subscriber), TODO 3(Twist 발행) |
| `cp3_nav2_client_solution.py` | `m8_robot/cp3_nav2_client.py` | TODO 1(ActionClient 생성), TODO 2(GOALS 순회 + send_goal) |

> CP2(`cp2_slam_mapper.py`)는 TODO 없는 완성 코드이므로 모범답안 불필요

---

## 스켈레톤 vs 모범답안 핵심 차이

### CP1

| 항목 | 스켈레톤 | 모범답안 |
|------|---------|---------|
| `self.pub` | `None` | `self.create_publisher(Twist, '/cmd_vel', 10)` |
| `self.sub` | `None` | `self.create_subscription(Odometry, '/odom', ...)` |
| `_publish_cmd` | `msg = Twist()` 만 생성 | `msg.linear.x = 0.2` + `self.pub.publish(msg)` |

### CP3

| 항목 | 스켈레톤 | 모범답안 |
|------|---------|---------|
| `self._ac` | `None` | `ActionClient(self, NavigateToPose, 'navigate_to_pose')` |
| `run()` for 루프 | `pass` | `send_goal(x, y, yaw)` 호출 + 결과 로그 출력 |

---

## 강사 운영 가이드

- 학생 제출 코드와 이 파일을 **나란히 열어** diff 비교 후 채점
- TODO 항목 하나라도 `None` 또는 `pass` 상태면 해당 CP 0점 처리
- CP1 합격 기준: `ros2 topic hz /cmd_vel` 출력값 ≥ 2.0 Hz
- CP3 합격 기준: "목표 1/2/3 도달 완료!" 로그 3줄 모두 출력
