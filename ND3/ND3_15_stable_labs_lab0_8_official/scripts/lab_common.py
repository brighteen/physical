#!/usr/bin/env python3
"""Shared helpers for the Lab 0-8 practice scripts."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shlex
import shutil
import subprocess
import sys
from typing import Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
PYTHON_DIR = ROOT / "python"
MPLCONFIGDIR = Path("/tmp/nd3_matplotlib")

MPLCONFIGDIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

SYSTEM_PATH_PREFIX = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
SYSTEM_PYTHON = "/usr/bin/python3" if Path("/usr/bin/python3").exists() else sys.executable
ROS_PYTHON_ENTRYPOINTS = {
    "python/initial_pose.py",
    "python/mission_runner.py",
    "python/send_goal.py",
}

if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


@dataclass
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def use_repo_root() -> None:
    os.chdir(ROOT)


def rel(path: str | Path) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def quote_command(args: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in args)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def ros_process_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{SYSTEM_PATH_PREFIX}:{env.get('PATH', '')}"
    env.setdefault("TURTLEBOT3_MODEL", "burger")
    env.setdefault("ROS_DOMAIN_ID", "30")
    if "RMW_IMPLEMENTATION" not in env and Path("/opt/ros/humble/share/rmw_cyclonedds_cpp").exists():
        env["RMW_IMPLEMENTATION"] = "rmw_cyclonedds_cpp"
    return env


def needs_ros_process_env(args: Sequence[str]) -> bool:
    ros_commands = {"ros2", "rviz2", "gz", "gzserver", "gzclient", "gazebo"}
    for arg in args:
        name = Path(str(arg)).name
        if name in ros_commands:
            return True
        normalized = str(arg).replace(os.sep, "/")
        if normalized in ROS_PYTHON_ENTRYPOINTS:
            return True
    return False


def print_status(ok: bool, label: str, detail: str = "") -> None:
    mark = "OK" if ok else "MISS"
    suffix = f" - {detail}" if detail else ""
    print(f"[{mark}] {label}{suffix}")


def run_capture(
    args: Sequence[str],
    *,
    timeout: float | None = None,
    check: bool = False,
    dry_run: bool = False,
) -> CommandResult:
    cmd = [str(arg) for arg in args]
    if dry_run:
        print(f"[DRY-RUN] {quote_command(cmd)}")
        return CommandResult(cmd, 0, "", "")

    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        env=ros_process_env() if needs_ros_process_env(cmd) else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    result = CommandResult(cmd, proc.returncode, proc.stdout, proc.stderr)
    if check and result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def run_stream(args: Sequence[str], *, dry_run: bool = False) -> int:
    cmd = [str(arg) for arg in args]
    if dry_run:
        print(f"[DRY-RUN] {quote_command(cmd)}")
        return 0
    return subprocess.call(cmd, cwd=ROOT, env=ros_process_env() if needs_ros_process_env(cmd) else None)


def ros2(args: Sequence[str], **kwargs) -> CommandResult:
    return run_capture(["ros2", *[str(arg) for arg in args]], **kwargs)


def latest_path(pattern: str) -> Path | None:
    matches = sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def require_file(path: str | Path, label: str) -> bool:
    p = ROOT / path if not Path(path).is_absolute() else Path(path)
    ok = p.exists()
    print_status(ok, label, rel(p) if ok else f"not found: {rel(p)}")
    return ok
