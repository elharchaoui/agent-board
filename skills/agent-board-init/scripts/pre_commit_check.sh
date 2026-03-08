#!/usr/bin/env bash
set -euo pipefail
echo "Running Agent Board pre-commit checks..."
python3 agent_board.py validate --statuses claimed,in_progress,blocked --require-next --require-handoff
echo "Agent Board validation passed."
