#!/usr/bin/env python3
"""Lab 8 practice: preview/run waypoint missions and generate the report."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from lab_common import ROOT, SYSTEM_PYTHON, latest_path, print_status, run_stream, use_repo_root


def read_waypoints(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        print_status(False, "waypoints csv", str(path))
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def preview(waypoints: Path) -> int:
    rows = read_waypoints(waypoints)
    if not rows:
        return 1
    print_status(True, "waypoints csv", str(waypoints))
    print(f"waypoint_count: {len(rows)}")
    for index, row in enumerate(rows, start=1):
        print(f"{index}: x={row.get('x')} y={row.get('y')} yaw={row.get('yaw', '0.0')}")

    print("\n== Evidence files ==")
    for path in [
        "maps/lab_map.yaml",
        "maps/lab_map.pgm",
        "results/planner_metrics_offline.csv",
        "results/planner_compare_offline.png",
        "results/dwb_safe_agile.csv",
        "results/dwb_safe_agile.png",
    ]:
        print_status((ROOT / path).exists(), path)
    bag = latest_path("results/nav2*")
    print_status(bag is not None, "rosbag folder", str(bag) if bag else "not found")
    return 0


def run_mission(waypoints: Path, timeout: float) -> int:
    return run_stream(
        [
            SYSTEM_PYTHON,
            "python/mission_runner.py",
            "--waypoints",
            str(waypoints),
            "--timeout",
            str(timeout),
        ]
    )


def make_report(output: Path) -> int:
    return run_stream([SYSTEM_PYTHON, "python/make_report.py", "--output", str(output)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["preview", "mission", "report", "both"], default="preview")
    parser.add_argument("--waypoints", default="docs/waypoints_default.csv")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--output", default="results/final_report.md")
    args = parser.parse_args()

    use_repo_root()
    waypoints = ROOT / args.waypoints
    output = ROOT / args.output

    if args.mode == "preview":
        raise SystemExit(preview(waypoints))
    if args.mode == "mission":
        raise SystemExit(run_mission(waypoints, args.timeout))
    if args.mode == "report":
        raise SystemExit(make_report(output))
    if args.mode == "both":
        code = run_mission(waypoints, args.timeout)
        if code == 0:
            code = make_report(output)
        raise SystemExit(code)


if __name__ == "__main__":
    main()
