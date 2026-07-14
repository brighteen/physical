#!/usr/bin/env python3
"""Lab 3 practice: check Nav2 state, set an initial pose, or send a goal."""
from __future__ import annotations

import argparse

from lab_common import ROOT, SYSTEM_PYTHON, print_status, quote_command, ros2, run_stream, use_repo_root


NAV2_NODES = [
    "/map_server",
    "/amcl",
    "/planner_server",
    "/controller_server",
    "/bt_navigator",
]


def print_commands(map_yaml: str) -> None:
    commands = [
        ["source", "scripts/env.sh"],
        ["./scripts/lab1_start_gazebo.sh"],
        ["./scripts/lab3_start_nav2_official.sh", map_yaml],
        ["./scripts/lab3_start_rviz_safe.sh"],
        ["python3", "scripts/lab3_practice.py", "--action", "status"],
        ["python3", "scripts/lab3_practice.py", "--action", "initial-pose", "--x", "0.0", "--y", "0.0"],
        ["python3", "scripts/lab3_practice.py", "--action", "goal", "--x", "0.5", "--y", "0.0"],
    ]
    for command in commands:
        print(quote_command(command))


def map_check(map_yaml: str) -> int:
    yaml_path = ROOT / map_yaml
    ok = yaml_path.exists()
    print_status(ok, "map yaml", str(yaml_path))
    if not ok:
        return 1
    result = ros2(
        [
            "topic",
            "echo",
            "/map",
            "--once",
            "--qos-durability",
            "transient_local",
            "--qos-reliability",
            "reliable",
        ],
        timeout=6.0,
    )
    print_status(result.returncode == 0, "/map sample", "available" if result.returncode == 0 else "not available")
    return 0 if result.returncode == 0 else 1


def status() -> int:
    failures = 0
    nodes = ros2(["node", "list"], timeout=5.0)
    node_text = nodes.stdout if nodes.returncode == 0 else ""
    print("== Nav2 node presence ==")
    for node in NAV2_NODES:
        ok = node in node_text
        print_status(ok, node)
        failures += 0 if ok else 1

    print("\n== Lifecycle states ==")
    for node in NAV2_NODES:
        result = ros2(["lifecycle", "get", node], timeout=4.0)
        text = (result.stdout or result.stderr).strip()
        ok = result.returncode == 0
        print_status(ok, node, text)

    return failures


def call_initial_pose(x: float, y: float, yaw: float, frame: str) -> int:
    return run_stream(
        [
            SYSTEM_PYTHON,
            "python/initial_pose.py",
            "--x",
            str(x),
            "--y",
            str(y),
            "--yaw",
            str(yaw),
            "--frame",
            frame,
        ]
    )


def call_goal(x: float, y: float, yaw: float, frame: str, timeout: float) -> int:
    return run_stream(
        [
            SYSTEM_PYTHON,
            "python/send_goal.py",
            "--x",
            str(x),
            "--y",
            str(y),
            "--yaw",
            str(yaw),
            "--frame",
            frame,
            "--timeout",
            str(timeout),
        ]
    )


def stop_robot() -> int:
    return run_stream(
        [
            "ros2",
            "topic",
            "pub",
            "--once",
            "/cmd_vel",
            "geometry_msgs/msg/Twist",
            "{linear: {x: 0.0}, angular: {z: 0.0}}",
        ]
    )


def start_nav2(map_yaml: str, dry_run: bool) -> int:
    map_path = (ROOT / map_yaml).resolve()
    if not map_path.exists():
        print_status(False, "map yaml", str(map_path))
        return 1
    return run_stream(
        [
            "ros2",
            "launch",
            "turtlebot3_navigation2",
            "navigation2.launch.py",
            "use_sim_time:=True",
            f"map:={map_path}",
        ],
        dry_run=dry_run,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--action",
        choices=["commands", "map-check", "status", "start-nav2", "initial-pose", "goal", "stop"],
        default="status",
    )
    parser.add_argument("--map", default="maps/lab_map.yaml")
    parser.add_argument("--x", type=float, default=0.0)
    parser.add_argument("--y", type=float, default=0.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--frame", default="map")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.action == "commands":
        print_commands(args.map)
    elif args.action == "map-check":
        raise SystemExit(map_check(args.map))
    elif args.action == "status":
        raise SystemExit(status())
    elif args.action == "start-nav2":
        raise SystemExit(start_nav2(args.map, args.dry_run))
    elif args.action == "initial-pose":
        raise SystemExit(call_initial_pose(args.x, args.y, args.yaw, args.frame))
    elif args.action == "goal":
        raise SystemExit(call_goal(args.x, args.y, args.yaw, args.frame, args.timeout))
    elif args.action == "stop":
        raise SystemExit(stop_robot())


if __name__ == "__main__":
    main()
