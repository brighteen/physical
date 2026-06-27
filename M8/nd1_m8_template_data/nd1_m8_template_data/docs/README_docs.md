# docs — 참고 문서 모음

이 폴더에는 M8 실습에 필요한 참고 문서가 저장됩니다.

## 교재 (강사로부터 배포)

| 파일 | 내용 |
|------|------|
| `M8_표준안_교재.docx` | ND1 M8 표준안 교재 (강사 배포) |
| `M8_강의용_PPT.pptx` | 강의 슬라이드 (강사 배포) |
| `M8_강사용_지도서.docx` | 강사용 운영 가이드 |

## 외부 참고 자료

- **ROS2 Humble 공식 문서**: https://docs.ros.org/en/humble/
- **Nav2 공식 문서**: https://navigation.ros.org/
- **SLAM Toolbox**: https://github.com/SteveMacenski/slam_toolbox
- **TurtleBot4**: https://turtlebot.github.io/turtlebot4-user-manual/
- **Gazebo Fortress**: https://gazebosim.org/docs/fortress

## M7 연계 자료

M7 교재에서 학습한 개념이 M8에 적용되는 방식:

| M7 개념 | M8 활용 |
|---------|---------|
| FK (정기구학) | `m7_to_ros2_bridge.py` → `/joint_states` 발행 |
| IK (역기구학) | 관절각 → `JointTrajectory` → Gazebo 로봇 팔 |
| 야코비안 | TF2 프레임 속도 제어 참고 |
| 동차변환행렬 | TF2 프레임 변환 (map → odom → base_link) |

## M13 연계

M8 이후 M13 (물리 시뮬레이션)에서 다루는 내용:

| M8 산출물 | M13 활용 |
|---------|---------|
| SLAM 지도 (my_map.yaml) | 3D 환경으로 확장 |
| Nav2 자율 이동 | 물리 기반 장애물 회피 통합 |
| m7_to_ros2_bridge.py | Gazebo 물리 파라미터 세밀화 |
