# Evidence Checklist

## Lab 0
- [ ] `lab0_env_check.sh` 결과 캡처

## Lab 1
- [ ] Gazebo TurtleBot3 화면 캡처
- [ ] runtime smoke check passed 로그

## Lab 2
- [ ] SLAM RViz 지도 캡처
- [ ] `maps/lab_map.yaml`
- [ ] `maps/lab_map.pgm`

## Lab 3
- [ ] Official Nav2 실행 로그
- [ ] `/map_server`, `/amcl`, `/planner_server`, `/controller_server`, `/bt_navigator` active 확인
- [ ] RViz map + robot pose 캡처
- [ ] Nav2 Goal 이동 캡처

## Lab 4
- [ ] `results/planner_metrics_offline.csv`
- [ ] `results/planner_compare_offline.png`

## Lab 5
- [ ] `results/dwb_safe_agile.csv`
- [ ] `results/dwb_safe_agile.png`

## Lab 6
- [ ] 장애물 삽입 전/후 캡처
- [ ] 바꾼 장애물 파라미터 기록: `x`, `y`, `size_x`, `size_y`, `size_z`, `static`
- [ ] costmap clear 실행 로그

## Lab 7
- [ ] `results/nav2_*` rosbag 폴더
- [ ] `ros2 bag info` 출력

## Lab 8
- [ ] mission 성공 로그
- [ ] `results/final_report.md`
