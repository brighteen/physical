#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, subprocess, sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--waypoints', default='docs/waypoints_default.csv')
    ap.add_argument('--timeout', type=float, default=120.0)
    args = ap.parse_args()
    wp = Path(args.waypoints)
    if not wp.exists():
        print(f'Missing waypoints file: {wp}', file=sys.stderr)
        sys.exit(1)
    rows = list(csv.DictReader(wp.open()))
    for i, row in enumerate(rows, start=1):
        x, y, yaw = float(row['x']), float(row['y']), float(row.get('yaw', 0.0))
        print(f'== Waypoint {i}/{len(rows)}: x={x} y={y} yaw={yaw} ==', flush=True)
        cmd = [sys.executable, 'python/send_goal.py', '--x', str(x), '--y', str(y), '--yaw', str(yaw), '--timeout', str(args.timeout)]
        ret = subprocess.call(cmd)
        if ret != 0:
            print(f'Waypoint {i} failed with code {ret}', file=sys.stderr)
            sys.exit(ret)
    print('Mission completed', flush=True)

if __name__ == '__main__':
    main()
