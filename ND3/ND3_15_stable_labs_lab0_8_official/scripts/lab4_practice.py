#!/usr/bin/env python3
"""Lab 4 practice: compare offline Dijkstra, A*, Greedy, Weighted A*, and RRT."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import time

from lab_common import ROOT, print_status, use_repo_root
from map_utils import SUPPORTED_PLANNERS, grid_to_world, load_map, path_length_world, plan_path, world_to_grid

import matplotlib.pyplot as plt


def write_metrics(rows: list[dict[str, object]], output_csv: Path) -> None:
    fields = ["planner", "status", "planning_ms", "path_length_m", "nodes_expanded", "path_cells", "error"]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def plot_paths(gmap, paths: dict[str, list[tuple[int, int]]], output_png: Path) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(gmap.image, cmap="gray")
    for label, path in paths.items():
        xs = [col for row, col in path]
        ys = [row for row, col in path]
        ax.plot(xs, ys, label=label)
    if paths:
        ax.legend()
    ax.set_title("Lab 4 Practice Planner Comparison")
    ax.set_xlabel("grid col")
    ax.set_ylabel("grid row")
    fig.tight_layout()
    fig.savefig(output_png, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", default="maps/lab_map.yaml")
    parser.add_argument("--start-x", type=float, default=0.0)
    parser.add_argument("--start-y", type=float, default=0.0)
    parser.add_argument("--goal-x", type=float, default=1.0)
    parser.add_argument("--goal-y", type=float, default=1.0)
    parser.add_argument("--algorithms", nargs="+", default=["dijkstra", "astar", "weighted_astar", "greedy", "rrt"], choices=SUPPORTED_PLANNERS)
    parser.add_argument("--heuristic-weight", type=float, default=1.5, help="Weighted A* heuristic multiplier.")
    parser.add_argument("--rrt-iterations", type=int, default=4000)
    parser.add_argument("--rrt-step-cells", type=int, default=10)
    parser.add_argument("--rrt-goal-sample-rate", type=float, default=0.15)
    parser.add_argument("--rrt-goal-radius-cells", type=int, default=10)
    parser.add_argument("--rrt-seed", type=int, default=7)
    parser.add_argument("--sparse-step", type=int, default=5)
    parser.add_argument("--output-csv", default="results/lab4_practice_metrics.csv")
    parser.add_argument("--output-png", default="results/lab4_practice_paths.png")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--list-algorithms", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.list_algorithms:
        print("dijkstra: optimal grid search without a heuristic; slow but a good baseline.")
        print("astar: optimal grid search with a distance heuristic; usually much faster.")
        print("weighted_astar: faster A* variant; may trade optimality for speed.")
        print("greedy: follows the heuristic strongly; fast but can make poor routes.")
        print("rrt: random sampling planner; useful for motion-planning intuition, not shortest-path optimal.")
        return
    if args.sparse_step < 1:
        raise SystemExit("--sparse-step must be at least 1")

    map_yaml = ROOT / args.map
    if not map_yaml.exists():
        print_status(False, "requested map", f"{map_yaml} not found; using examples/simple_map.yaml")
        map_yaml = ROOT / "examples/simple_map.yaml"

    gmap = load_map(map_yaml)
    start = world_to_grid(gmap, args.start_x, args.start_y)
    goal = world_to_grid(gmap, args.goal_x, args.goal_y)

    rows: list[dict[str, object]] = []
    paths: dict[str, list[tuple[int, int]]] = {}

    for algorithm in args.algorithms:
        t0 = time.perf_counter()
        try:
            path, expanded = plan_path(
                gmap,
                start,
                goal,
                algorithm,
                heuristic_weight=args.heuristic_weight,
                rrt_iterations=args.rrt_iterations,
                rrt_step_cells=args.rrt_step_cells,
                rrt_goal_sample_rate=args.rrt_goal_sample_rate,
                rrt_goal_radius_cells=args.rrt_goal_radius_cells,
                rrt_seed=args.rrt_seed,
            )
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            rows.append(
                {
                    "planner": algorithm,
                    "status": "failed",
                    "planning_ms": round(elapsed_ms, 3),
                    "path_length_m": "",
                    "nodes_expanded": "",
                    "path_cells": "",
                    "error": str(exc),
                }
            )
            continue

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        paths[algorithm] = path
        rows.append(
            {
                "planner": algorithm,
                "status": "ok",
                "planning_ms": round(elapsed_ms, 3),
                "path_length_m": round(path_length_world(gmap, path), 3),
                "nodes_expanded": expanded,
                "path_cells": len(path),
                "error": "",
            }
        )

    if "astar" in paths and args.sparse_step > 1:
        astar_path = paths["astar"]
        sparse = astar_path[:: args.sparse_step]
        if sparse[-1] != astar_path[-1]:
            sparse.append(astar_path[-1])
        paths[f"astar_sparse_{args.sparse_step}"] = sparse
        rows.append(
            {
                "planner": f"astar_sparse_{args.sparse_step}",
                "status": "ok",
                "planning_ms": 0.0,
                "path_length_m": round(path_length_world(gmap, sparse), 3),
                "nodes_expanded": 0,
                "path_cells": len(sparse),
                "error": "",
            }
        )

    write_metrics(rows, ROOT / args.output_csv)
    if not args.no_plot:
        plot_paths(gmap, paths, ROOT / args.output_png)

    print(f"map: {map_yaml}")
    print(f"start_cell: {start} -> world {grid_to_world(gmap, *start)}")
    print(f"goal_cell: {goal} -> world {grid_to_world(gmap, *goal)}")
    for row in rows:
        print(row)
    print(f"saved_csv: {args.output_csv}")
    if not args.no_plot:
        print(f"saved_png: {args.output_png}")


if __name__ == "__main__":
    main()
