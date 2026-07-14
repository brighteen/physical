# Mapping to ND3-15 Standard Lecture Material

| Lab | Standard topic | Stable implementation |
|---|---|---|
| Lab 0 | 환경 점검, ROS2 package 확인 | `lab0_env_check.sh` |
| Lab 1 | Gazebo TurtleBot3, `/scan`, `/odom`, `/tf` 확인 | Official TurtleBot3 Gazebo + runtime smoke check |
| Lab 2 | SLAM Toolbox 지도 생성, map 저장 | `slam_toolbox` + `map_saver_cli` |
| Lab 3 | 저장 지도 기반 Nav2 + AMCL + RViz | Official `turtlebot3_navigation2 navigation2.launch.py` |
| Lab 4 | Dijkstra/A*/Planner 비교 | Stable offline Dijkstra/A* analysis |
| Lab 5 | DWB Safe/Agile 비교 | Stable offline Safe/Agile velocity policy analysis |
| Lab 6 | 장애물 삽입, costmap clear, recovery 관찰 | Gazebo spawn/delete + costmap clear scripts |
| Lab 7 | rosbag 기록 | `lab7_record_bag.sh` |
| Lab 8 | 다중 goal mission 및 보고서 | `mission_runner.py`, `make_report.py` |

실시간 Navigation은 안정성을 위해 공식 TurtleBot3 launch를 사용한다. Planner/DWB 비교는 수업 중 lifecycle 불안정성을 줄이기 위해 Python offline 실습으로 분리했다.
