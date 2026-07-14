#!/usr/bin/env bash
set -e
source "$(dirname "$0")/env.sh"
MAP="${1:-maps/lab_map.yaml}"
echo "== Map file check =="
ls -lh "$MAP" || { echo "Map YAML missing: $MAP"; exit 1; }
IMG=$(python3 - <<PY
import sys,yaml,os
with open('$MAP') as f: d=yaml.safe_load(f)
print(d.get('image',''))
PY
)
if [ -n "$IMG" ]; then
  if [ -f "$(dirname "$MAP")/$IMG" ]; then ls -lh "$(dirname "$MAP")/$IMG"; else echo "[WARN] image path not found: $(dirname "$MAP")/$IMG"; fi
fi

echo "== Runtime /map check =="
ros2 lifecycle get /map_server || true
ros2 topic list -t | grep -E "^/map|/map_metadata" || true
timeout 5 ros2 topic echo /map --once --qos-durability transient_local --qos-reliability reliable || true
