#!/usr/bin/env python3
"""Lab 0 practice: check the local ROS and Python environment."""
from __future__ import annotations

import argparse
import importlib
import platform
import sys

from lab_common import ROOT, command_exists, print_status, run_capture, use_repo_root


REQUIRED_ROS_PACKAGES = [
    "turtlebot3_gazebo",
    "turtlebot3_navigation2",
    "turtlebot3_teleop",
    "slam_toolbox",
    "nav2_map_server",
    "nav2_msgs",
    "tf2_ros",
    "rviz2",
    "gazebo_ros",
]

PYTHON_IMPORTS = [
    ("numpy", "numpy"),
    ("matplotlib", "matplotlib"),
    ("pandas", "pandas"),
    ("PyYAML", "yaml"),
    ("Pillow", "PIL"),
]


def check_python_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        print_status(False, f"python import {module_name}", str(exc))
        return False
    print_status(True, f"python import {module_name}")
    return True


def check_ros_package(package: str) -> bool:
    result = run_capture(["ros2", "pkg", "prefix", package], timeout=4.0)
    ok = result.returncode == 0
    detail = result.stdout.strip() if ok else result.stderr.strip()
    print_status(ok, f"ROS package {package}", detail)
    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-ros", action="store_true", help="Only check Python/offline items.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any check fails.")
    parser.add_argument("--static-check", action="store_true", help="Run tools/static_check.py too.")
    args = parser.parse_args()

    use_repo_root()
    failures = 0

    print("== Lab 0 Python Environment ==")
    print(f"Project: {ROOT}")
    print(f"Python: {sys.executable}")
    print(f"Python version: {platform.python_version()}")
    print_status(sys.version_info >= (3, 10), "Python >= 3.10")

    for label, module_name in PYTHON_IMPORTS:
        if not check_python_import(module_name):
            failures += 1

    print("\n== Local Files ==")
    for path in ["requirements_python.txt", "python/map_utils.py", "scripts/env.sh"]:
        ok = (ROOT / path).exists()
        print_status(ok, path)
        failures += 0 if ok else 1

    if args.static_check:
        print("\n== Static Check ==")
        result = run_capture([sys.executable, "tools/static_check.py"], timeout=10.0)
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        failures += 0 if result.returncode == 0 else 1

    if args.skip_ros:
        print("\nROS checks skipped.")
    else:
        print("\n== ROS 2 Environment ==")
        if not command_exists("ros2"):
            print_status(False, "ros2 command", "source scripts/env.sh first or install ROS 2 Humble")
            failures += 1
        else:
            distro = run_capture(["ros2", "--help"], timeout=4.0).returncode == 0
            print_status(distro, "ros2 command")
            for package in REQUIRED_ROS_PACKAGES:
                if not check_ros_package(package):
                    failures += 1

        if not check_python_import("rclpy"):
            failures += 1

    print("\n== Result ==")
    if failures:
        print(f"Lab 0 found {failures} item(s) to fix.")
    else:
        print("Lab 0 checks passed.")
    if failures and args.strict:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
