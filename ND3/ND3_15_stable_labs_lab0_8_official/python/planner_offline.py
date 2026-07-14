#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, os, time
from pathlib import Path

Path("/tmp/nd3_matplotlib").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", "/tmp/nd3_matplotlib")

import matplotlib.pyplot as plt

from map_utils import SUPPORTED_PLANNERS, load_map, plan_path, path_length_world, world_to_grid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--map', required=True)
    ap.add_argument('--start-x', type=float, required=True)
    ap.add_argument('--start-y', type=float, required=True)
    ap.add_argument('--goal-x', type=float, required=True)
    ap.add_argument('--goal-y', type=float, required=True)
    ap.add_argument('--algorithms', nargs='+', default=['dijkstra', 'astar', 'weighted_astar', 'greedy', 'rrt'], choices=SUPPORTED_PLANNERS)
    ap.add_argument('--heuristic-weight', type=float, default=1.5)
    ap.add_argument('--rrt-iterations', type=int, default=4000)
    ap.add_argument('--rrt-step-cells', type=int, default=10)
    ap.add_argument('--rrt-goal-sample-rate', type=float, default=0.15)
    ap.add_argument('--rrt-goal-radius-cells', type=int, default=10)
    ap.add_argument('--rrt-seed', type=int, default=7)
    ap.add_argument('--output-csv', default='results/planner_metrics_offline.csv')
    ap.add_argument('--output-png', default='results/planner_compare_offline.png')
    args = ap.parse_args()

    gmap = load_map(args.map)
    start = world_to_grid(gmap, args.start_x, args.start_y)
    goal = world_to_grid(gmap, args.goal_x, args.goal_y)

    rows = []
    paths = {}
    fields = ['planner', 'status', 'planning_ms', 'path_length_m', 'nodes_expanded', 'path_cells', 'error']
    for alg in args.algorithms:
        t0 = time.perf_counter()
        try:
            path, expanded = plan_path(
                gmap,
                start,
                goal,
                alg,
                heuristic_weight=args.heuristic_weight,
                rrt_iterations=args.rrt_iterations,
                rrt_step_cells=args.rrt_step_cells,
                rrt_goal_sample_rate=args.rrt_goal_sample_rate,
                rrt_goal_radius_cells=args.rrt_goal_radius_cells,
                rrt_seed=args.rrt_seed,
            )
        except Exception as exc:
            ms = (time.perf_counter() - t0) * 1000.0
            rows.append({'planner': alg, 'status': 'failed', 'planning_ms': round(ms, 3), 'path_length_m': '', 'nodes_expanded': '', 'path_cells': '', 'error': str(exc)})
            continue
        ms = (time.perf_counter() - t0) * 1000.0
        length = path_length_world(gmap, path)
        rows.append({'planner': alg, 'status': 'ok', 'planning_ms': round(ms, 3), 'path_length_m': round(length, 3), 'nodes_expanded': expanded, 'path_cells': len(path), 'error': ''})
        paths[alg] = path

    # Simple post-processing row: same A* path with every 5th point retained for visualization only.
    if 'astar' in paths:
        astar_path = paths['astar']
        sparse = astar_path[::5] + ([astar_path[-1]] if astar_path[-1] != astar_path[::5][-1] else [])
        rows.append({'planner': 'astar_sparse_waypoints', 'status': 'ok', 'planning_ms': 0.0, 'path_length_m': round(path_length_world(gmap, sparse), 3), 'nodes_expanded': 0, 'path_cells': len(sparse), 'error': ''})

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(gmap.image, cmap='gray')
    for alg, path in paths.items():
        xs, ys = zip(*[(c, r) for r, c in path])
        ax.plot(xs, ys, label=alg)
    if 'astar' in paths:
        xs, ys = zip(*[(c, r) for r, c in sparse])
        ax.plot(xs, ys, '--', label='astar sparse')
    ax.scatter([start[1], goal[1]], [start[0], goal[0]], marker='o')
    ax.set_title('Lab 4 Offline Planner Comparison: Dijkstra / A* / Greedy / RRT')
    ax.set_xlabel('grid col'); ax.set_ylabel('grid row'); ax.legend()
    Path(args.output_png).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(args.output_png, dpi=150); plt.close(fig)
    print(f"Saved: {args.output_csv}")
    print(f"Saved: {args.output_png}")

if __name__ == '__main__':
    main()
