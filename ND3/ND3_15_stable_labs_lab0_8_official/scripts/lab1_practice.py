#!/usr/bin/env python3
"""Lab 1 practice: start Gazebo or verify runtime topics and TF."""
from __future__ import annotations

import argparse
import shutil

from lab_common import print_status, quote_command, ros2, run_capture, run_stream, use_repo_root


REQUIRED_TOPICS = ["/clock", "/scan", "/odom", "/tf"]
SAMPLE_TOPICS = ["/scan", "/odom", "/clock"]


def topic_list() -> set[str]:
    result = ros2(["topic", "list"], timeout=5.0)
    if result.returncode != 0:
        print(result.stderr.strip())
        return set()
    return set(line.strip() for line in result.stdout.splitlines() if line.strip())


def sample_topic(topic: str, timeout_s: float) -> bool:
    timeout_bin = shutil.which("timeout")
    if timeout_bin:
        cmd = [timeout_bin, str(timeout_s), "ros2", "topic", "echo", topic, "--once"]
        result = run_capture(cmd, timeout=timeout_s + 2.0)
    else:
        result = ros2(["topic", "echo", topic, "--once"], timeout=timeout_s)
    ok = result.returncode == 0
    detail = "sample received" if ok else (result.stderr.strip() or result.stdout.strip())
    print_status(ok, f"{topic} sample", detail[:160])
    return ok


def check_tf(timeout_s: float) -> bool:
    timeout_bin = shutil.which("timeout")
    frames = [("odom", "base_link"), ("odom", "base_footprint")]
    for parent, child in frames:
        base = ["ros2", "run", "tf2_ros", "tf2_echo", parent, child]
        cmd = [timeout_bin, str(timeout_s), *base] if timeout_bin else base
        result = run_capture(cmd, timeout=timeout_s + 2.0)
        text = result.stdout + result.stderr
        ok = "Translation" in text or "Rotation" in text
        if ok:
            print_status(True, f"TF {parent} -> {child}")
            return True
    print_status(False, "TF odom -> base_link/base_footprint", "not confirmed yet")
    return False


def check_runtime(timeout_s: float) -> int:
    failures = 0
    topics = topic_list()
    for topic in REQUIRED_TOPICS:
        ok = topic in topics
        print_status(ok, f"topic {topic}")
        failures += 0 if ok else 1
    for topic in SAMPLE_TOPICS:
        failures += 0 if sample_topic(topic, timeout_s) else 1
    check_tf(timeout_s)
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=["check", "start-gazebo", "commands"], default="check")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.action == "commands":
        commands = [
            ["source", "scripts/env.sh"],
            ["./scripts/lab1_start_gazebo.sh"],
            ["./scripts/lab1_runtime_smoke_check.sh"],
            ["python3", "scripts/lab1_practice.py", "--action", "check"],
        ]
        for command in commands:
            print(quote_command(command))
        return

    if args.action == "start-gazebo":
        raise SystemExit(
            run_stream(
                ["ros2", "launch", "turtlebot3_gazebo", "turtlebot3_world.launch.py"],
                dry_run=args.dry_run,
            )
        )

    failures = check_runtime(args.timeout)
    if failures:
        print(f"Runtime check found {failures} missing item(s).")
        raise SystemExit(1)
    print("Runtime smoke check passed.")


if __name__ == "__main__":
    main()
