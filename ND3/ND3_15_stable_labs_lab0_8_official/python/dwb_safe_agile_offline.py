#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
import matplotlib.pyplot as plt


def simulate(max_v: float, max_w: float, label: str):
    # Toy unicycle tracking of a 2 m straight + turn. This is not DWB internals;
    # it is a stable offline comparison of conservative vs aggressive limits.
    dt = 0.1
    x = y = th = 0.0
    target = (2.0, 0.8)
    traj = []
    total_cmd = 0.0
    for k in range(250):
        dx, dy = target[0] - x, target[1] - y
        dist = math.hypot(dx, dy)
        desired = math.atan2(dy, dx)
        err = math.atan2(math.sin(desired - th), math.cos(desired - th))
        v = min(max_v, 0.8 * dist)
        w = max(-max_w, min(max_w, 2.0 * err))
        if dist < 0.04:
            v = 0.0; w = 0.0
        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += w * dt
        total_cmd += abs(v) + abs(w)
        traj.append((k*dt, x, y, th, v, w, dist))
        if dist < 0.04 and abs(err) < 0.1:
            break
    return {'policy': label, 'max_v': max_v, 'max_w': max_w, 'duration_s': round(traj[-1][0], 2), 'final_error_m': round(traj[-1][-1], 3), 'samples': len(traj), 'cmd_effort': round(total_cmd, 3)}, traj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-csv', default='results/dwb_safe_agile.csv')
    ap.add_argument('--output-png', default='results/dwb_safe_agile.png')
    args = ap.parse_args()
    configs = [('safe', 0.15, 0.8), ('agile', 0.26, 1.2)]
    rows, trajectories = [], {}
    for label, v, w in configs:
        row, traj = simulate(v, w, label)
        rows.append(row); trajectories[label] = traj
    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader(); writer.writerows(rows)
    fig, ax = plt.subplots(figsize=(6, 5))
    for label, traj in trajectories.items():
        ax.plot([p[1] for p in traj], [p[2] for p in traj], label=label)
    ax.scatter([2.0], [0.8], marker='x', label='target')
    ax.set_title('Lab 5 Safe vs Agile Offline Policy')
    ax.set_xlabel('x [m]'); ax.set_ylabel('y [m]'); ax.axis('equal'); ax.legend()
    Path(args.output_png).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(args.output_png, dpi=150); plt.close(fig)
    print(f"Saved: {args.output_csv}")
    print(f"Saved: {args.output_png}")

if __name__ == '__main__':
    main()
