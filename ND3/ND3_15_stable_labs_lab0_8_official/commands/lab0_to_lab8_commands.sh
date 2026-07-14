#!/usr/bin/env bash
# This file is a command reference, not a single-run automation.
# Copy one block at a time into separate terminals.

# LAB 0
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab0_env_check.sh

# LAB 1 Terminal 1
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab1_start_gazebo.sh

# LAB 1 Terminal 2
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab1_runtime_smoke_check.sh

# LAB 2 SLAM terminals
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab2_start_slam_toolbox.sh
# new terminal: ./scripts/lab2_start_rviz_safe.sh
# new terminal: ./scripts/lab2_teleop.sh
# after mapping: ./scripts/lab2_save_map.sh maps/lab_map

# LAB 3 official Nav2
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab3_start_nav2_official.sh maps/lab_map.yaml
# new terminal: ./scripts/lab3_nav2_status.sh
# new terminal: ./scripts/lab3_start_rviz_safe.sh
# RViz: 2D Pose Estimate -> Nav2 Goal

# LAB 4
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab4_planner_offline.sh maps/lab_map.yaml

# LAB 5
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab5_dwb_safe_agile_offline.sh

# LAB 6
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab6_spawn_box.sh 0.5 0.0 0.25
./scripts/lab6_clear_costmaps.sh
./scripts/lab6_delete_box.sh

# LAB 7
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab7_record_bag.sh
./scripts/lab7_bag_info.sh

# LAB 8
cd ~/Desktop/ND3_15_stable_labs_lab0_8_official
source scripts/env.sh
./scripts/lab8_run_mission.sh
./scripts/lab8_make_report.sh
