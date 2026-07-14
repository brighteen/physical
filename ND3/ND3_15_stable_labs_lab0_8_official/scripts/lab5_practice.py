#!/usr/bin/env python3
"""Lab 5 practice: compare safe and agile velocity limits offline."""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import math

from lab_common import ROOT, use_repo_root

import matplotlib.pyplot as plt


@dataclass
class Policy:
    label: str
    max_v: float
    max_w: float


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def angle_wrap(rad: float) -> float:
    return math.atan2(math.sin(rad), math.cos(rad))


def simulate(
    policy: Policy,
    *,
    target_x: float,
    target_y: float,
    dt: float,
    samples: int,
    linear_gain: float,
    angular_gain: float,
) -> tuple[dict[str, object], list[dict[str, float | str]]]:
    x = 0.0
    y = 0.0
    yaw = 0.0
    effort = 0.0
    trajectory: list[dict[str, float | str]] = []

    for step in range(samples):
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        desired_yaw = math.atan2(dy, dx)
        yaw_error = angle_wrap(desired_yaw - yaw)
        v = min(policy.max_v, linear_gain * distance)
        w = clamp(angular_gain * yaw_error, -policy.max_w, policy.max_w)

        if distance < 0.04:
            v = 0.0
            w = 0.0

        x += v * math.cos(yaw) * dt
        y += v * math.sin(yaw) * dt
        yaw = angle_wrap(yaw + w * dt)
        effort += abs(v) + abs(w)

        trajectory.append(
            {
                "policy": policy.label,
                "time_s": round(step * dt, 3),
                "x": x,
                "y": y,
                "yaw": yaw,
                "v": v,
                "w": w,
                "distance_to_target": distance,
            }
        )
        if distance < 0.04 and abs(yaw_error) < 0.1:
            break

    last = trajectory[-1]
    metrics = {
        "policy": policy.label,
        "max_v": policy.max_v,
        "max_w": policy.max_w,
        "duration_s": round(float(last["time_s"]), 2),
        "final_error_m": round(float(last["distance_to_target"]), 3),
        "samples": len(trajectory),
        "cmd_effort": round(effort, 3),
    }
    return metrics, trajectory


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_trajectories(trajectories: dict[str, list[dict[str, float | str]]], target: tuple[float, float], output_png: Path) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    for label, trajectory in trajectories.items():
        ax.plot([float(p["x"]) for p in trajectory], [float(p["y"]) for p in trajectory], label=label)
    ax.scatter([target[0]], [target[1]], marker="x", label="target")
    ax.set_title("Lab 5 Practice Safe vs Agile")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_png, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--safe-v", type=float, default=0.15)
    parser.add_argument("--safe-w", type=float, default=0.8)
    parser.add_argument("--agile-v", type=float, default=0.26)
    parser.add_argument("--agile-w", type=float, default=1.2)
    parser.add_argument("--target-x", type=float, default=2.0)
    parser.add_argument("--target-y", type=float, default=0.8)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--samples", type=int, default=250)
    parser.add_argument("--linear-gain", type=float, default=0.8)
    parser.add_argument("--angular-gain", type=float, default=2.0)
    parser.add_argument("--output-csv", default="results/lab5_practice_metrics.csv")
    parser.add_argument("--trajectory-csv", default="results/lab5_practice_trajectory.csv")
    parser.add_argument("--output-png", default="results/lab5_practice_paths.png")
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args()

    use_repo_root()
    if args.samples < 1:
        raise SystemExit("--samples must be at least 1")
    if args.dt <= 0:
        raise SystemExit("--dt must be greater than 0")

    policies = [
        Policy("safe", args.safe_v, args.safe_w),
        Policy("agile", args.agile_v, args.agile_w),
    ]

    metric_rows: list[dict[str, object]] = []
    trajectory_rows: list[dict[str, object]] = []
    trajectories: dict[str, list[dict[str, float | str]]] = {}

    for policy in policies:
        metrics, trajectory = simulate(
            policy,
            target_x=args.target_x,
            target_y=args.target_y,
            dt=args.dt,
            samples=args.samples,
            linear_gain=args.linear_gain,
            angular_gain=args.angular_gain,
        )
        metric_rows.append(metrics)
        trajectory_rows.extend(trajectory)
        trajectories[policy.label] = trajectory

    write_csv(ROOT / args.output_csv, metric_rows)
    write_csv(ROOT / args.trajectory_csv, trajectory_rows)
    if not args.no_plot:
        plot_trajectories(trajectories, (args.target_x, args.target_y), ROOT / args.output_png)

    for row in metric_rows:
        print(row)
    print(f"saved_csv: {args.output_csv}")
    print(f"saved_trajectory_csv: {args.trajectory_csv}")
    if not args.no_plot:
        print(f"saved_png: {args.output_png}")


if __name__ == "__main__":
    main()
