#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

X="${1:-0.5}"
Y="${2:-0.0}"
Z="${3:-0.25}"
MODEL="${4:-lab_box}"
if [ "$#" -gt 4 ]; then
  shift 4
else
  set --
fi

python3 "$SCRIPT_DIR/lab6_practice.py" --action spawn --x "$X" --y "$Y" --z "$Z" --model "$MODEL" "$@"
