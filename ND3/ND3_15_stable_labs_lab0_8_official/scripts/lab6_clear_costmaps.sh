#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

CLEAR_TIMEOUT="${1:-10}"
if [ "$#" -gt 0 ]; then
  shift
else
  set --
fi

python3 "$SCRIPT_DIR/lab6_practice.py" --action clear --clear-timeout "$CLEAR_TIMEOUT" "$@"
