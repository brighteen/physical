#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime


def safe_read(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return f'_missing: {path}_\n'
    text = path.read_text(encoding='utf-8', errors='replace')
    return text[:limit]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='results/final_report.md')
    args = ap.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append('# ND3-15 Lab 0~8 Final Report\n')
    lines.append(f'- Generated: {datetime.now().isoformat(timespec="seconds")}\n')
    lines.append('\n## 1. Map files\n')
    for p in [Path('maps/lab_map.yaml'), Path('maps/lab_map.pgm')]:
        lines.append(f'- {p}: {"OK" if p.exists() else "MISSING"}\n')
    lines.append('\n## 2. Planner offline metrics\n')
    lines.append('```\n' + safe_read(Path('results/planner_metrics_offline.csv')) + '\n```\n')
    lines.append('\n## 3. DWB Safe/Agile offline metrics\n')
    lines.append('```\n' + safe_read(Path('results/dwb_safe_agile.csv')) + '\n```\n')
    lines.append('\n## 4. Rosbag folders\n')
    bags = sorted(Path('results').glob('nav2_*'))
    if bags:
        for b in bags:
            lines.append(f'- {b}\n')
    else:
        lines.append('- No rosbag folder found yet.\n')
    lines.append('\n## 5. Student notes\n')
    lines.append('- RViz capture files: attach separately.\n')
    lines.append('- Describe: map quality, initial pose, goal success, obstacle response, and any failure.\n')
    out.write_text(''.join(lines), encoding='utf-8')
    print(f'Saved: {out}')

if __name__ == '__main__':
    main()
