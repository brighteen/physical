#!/usr/bin/env python3
from __future__ import annotations
import ast
from pathlib import Path
import subprocess
import yaml
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

def ok(msg: str): print(f"[OK] {msg}")
def fail(msg: str): print(f"[FAIL] {msg}"); raise SystemExit(1)

def main() -> None:
    for sh in sorted((ROOT/'scripts').glob('*.sh')):
        r = subprocess.run(['bash', '-n', str(sh)], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr); fail(f'bash syntax {sh}')
    ok('bash syntax scripts/*.sh')
    for py in list((ROOT/'python').glob('*.py')) + list((ROOT/'tests').glob('*.py')):
        try:
            ast.parse(py.read_text(encoding='utf-8'))
        except SyntaxError as e:
            fail(f'python syntax {py}: {e}')
    ok('python syntax python/*.py tests/*.py')
    for yml in list((ROOT/'examples').glob('*.yaml')) + list((ROOT/'maps').glob('*.yaml')):
        yaml.safe_load(yml.read_text(encoding='utf-8'))
    ok('YAML parse examples/maps')
    sdf = ROOT/'models'/'box.sdf'
    if sdf.exists():
        ET.parse(sdf)
        ok('SDF XML parse models/box.sdf')
    required = ['README.md','START_HERE.md','COMMANDS_ONLY.txt','scripts/env.sh','scripts/lab3_start_nav2_official.sh','python/planner_offline.py']
    for rel in required:
        if not (ROOT/rel).exists(): fail(f'missing {rel}')
    ok('required files exist')

if __name__ == '__main__': main()
