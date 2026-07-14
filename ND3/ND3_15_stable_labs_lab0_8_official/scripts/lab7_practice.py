#!/usr/bin/env python3
"""Lab 7 practice: record or inspect Nav2 rosbag evidence."""
from __future__ import annotations

import argparse
from datetime import datetime
import shutil

from lab_common import ROOT, latest_path, print_status, quote_command, run_stream, use_repo_root


DEFAULT_TOPICS = [
    "/scan",
    "/odom",
    "/tf",
    "/tf_static",
    "/map",
    "/cmd_vel",
    "/amcl_pose",
    "/goal_pose",
    "/plan",
    "/local_plan",
]


def print_commands() -> None:
    commands = [
        ["source", "scripts/env.sh"],
        ["python3", "scripts/lab7_practice.py", "--action", "record", "--duration", "30"],
        ["python3", "scripts/lab7_practice.py", "--action", "info"],
    ]
    for command in commands:
        print(quote_command(command))


def record_bag(duration: float, topics: list[str], dry_run: bool) -> int:
    out = ROOT / "results" / f"nav2_practice_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    out.parent.mkdir(parents=True, exist_ok=True)
    base = ["ros2", "bag", "record", "-o", str(out), *topics]
    if duration > 0:
        timeout_bin = shutil.which("timeout")
        if not timeout_bin:
            print_status(False, "timeout command", "install coreutils or run without --duration")
            return 1
        cmd = [timeout_bin, str(duration), *base]
    else:
        cmd = base
    code = run_stream(cmd, dry_run=dry_run)
    print(f"bag_path: {out}")
    return 0 if code in (0, 124) else code


def bag_info(path: str | None) -> int:
    bag = ROOT / path if path else latest_path("results/nav2*")
    if bag is None or not bag.exists():
        print_status(False, "rosbag", "no results/nav2* folder found")
        return 1
    return run_stream(["ros2", "bag", "info", str(bag)])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=["commands", "record", "info", "topics"], default="info")
    parser.add_argument("--duration", type=float, default=0.0, help="Seconds to record. Use 0 for Ctrl+C.")
    parser.add_argument("--bag")
    parser.add_argument("--topics", nargs="+", default=DEFAULT_TOPICS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.action == "commands":
        print_commands()
    elif args.action == "topics":
        for topic in args.topics:
            print(topic)
    elif args.action == "record":
        raise SystemExit(record_bag(args.duration, args.topics, args.dry_run))
    elif args.action == "info":
        raise SystemExit(bag_info(args.bag))


if __name__ == "__main__":
    main()
