# ND3-15 Lab 0~8 Final Report
- Generated: 2026-07-14T16:32:27

## 1. Map files
- maps/lab_map.yaml: OK
- maps/lab_map.pgm: OK

## 2. Planner offline metrics
```
planner,status,planning_ms,path_length_m,nodes_expanded,path_cells,error
dijkstra,ok,65.7,2.309,4663,36,
astar,ok,8.742,2.309,672,36,
weighted_astar,ok,1.586,2.309,153,36,
greedy,ok,0.722,2.338,73,37,
rrt,ok,153.749,5.347,678,15,
astar_sparse_waypoints,ok,0.0,2.129,0,8,

```

## 3. DWB Safe/Agile offline metrics
```
policy,max_v,max_w,duration_s,final_error_m,samples,cmd_effort
safe,0.15,0.8,15.0,0.039,151,25.123
agile,0.26,1.2,9.6,0.039,97,25.272

```

## 4. Rosbag folders
- results/nav2_20260714_153826

## 5. Student notes
- RViz capture files: attach separately.
- Describe: map quality, initial pose, goal success, obstacle response, and any failure.
