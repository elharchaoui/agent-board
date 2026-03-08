---
name: agent-board-init
description: "Initialize the agent board in this project. Creates agent_board.py, .agents/board/ structure, config, and templates. Run this once when adding the board to a new project."
disable-model-invocation: true
allowed-tools: Bash, Write
---

# Agent Board — Init

Check if `agent_board.py` already exists in the project root. If it does, tell the user the board is already initialized and stop.

Otherwise, perform every step below in order, then confirm with `python3 agent_board.py list`.

## Step 1 — Copy CLI

```bash
cp ${CLAUDE_SKILL_DIR}/scripts/agent_board.py ./agent_board.py
chmod +x ./agent_board.py
```

## Step 2 — Create directory structure

```bash
mkdir -p .agents/board/tasks .agents/board/sessions .agents/board/log .agents/board/templates .agents/hooks
```

## Step 3 — Copy config

Only if `.agents/board/config.yml` does not already exist:

```bash
cp ${CLAUDE_SKILL_DIR}/scripts/config.yml .agents/board/config.yml
```

## Step 4 — Copy task template

Only if `.agents/board/templates/task_template.md` does not already exist:

```bash
cp ${CLAUDE_SKILL_DIR}/scripts/task_template.md .agents/board/templates/task_template.md
```

## Step 5 — Copy pre-commit hook script

```bash
cp ${CLAUDE_SKILL_DIR}/scripts/pre_commit_check.sh .agents/hooks/pre_commit_check.sh
chmod +x .agents/hooks/pre_commit_check.sh
```

## Step 6 — Offer to wire the git pre-commit hook

If a `.git/` directory exists, ask the user:
"Wire `.agents/hooks/pre_commit_check.sh` as the git pre-commit hook? This blocks commits when active tasks are missing Handoff or Next entries. [y/N]"

If yes:
```bash
ln -sf ../../.agents/hooks/pre_commit_check.sh .git/hooks/pre-commit
```

## Step 7 — Confirm

Run `python3 agent_board.py list` and show the output.

Tell the user: "Agent board initialized. Use `/agent-board` for workflow guidance or `python3 agent_board.py --help` to explore commands."
