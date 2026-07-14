#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

MODEL="${1:-lab_box}"
if [ "$#" -gt 0 ]; then
  shift
else
  set --
fi

python3 "$SCRIPT_DIR/lab6_practice.py" --action delete --model "$MODEL" "$@"
