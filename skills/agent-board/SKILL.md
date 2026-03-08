---
name: agent-board
description: "Agent-friendly task board for this repo. Use when planning work, claiming tasks, logging progress, updating status, or handing off to another agent. Triggers on any mention of tasks, board, claim, handoff, or in-progress work."
allowed-tools: Bash
---

# Agent Board

The board lives under `.agents/board/tasks/*.md`. Each file is a task with structured frontmatter and sections. `agent_board.py` is the CLI that reads and writes those files.

## Workflow

1. **Session start** — review active work:
   ```
   python3 agent_board.py list --status claimed
   python3 agent_board.py list --status in_progress
   python3 agent_board.py list --status blocked
   ```

2. **Claim before editing** — always claim a task before making changes:
   ```
   python3 agent_board.py claim T-XXX --agent <your-name>
   ```

3. **Log progress** — after any meaningful change:
   ```
   python3 agent_board.py log T-XXX --note "What you did"
   ```

4. **Handoff before pausing** — so the next agent knows what remains:
   ```
   python3 agent_board.py handoff T-XXX --note "State of things" --next "What to do next"
   python3 agent_board.py status T-XXX --status done
   ```

## Commands

See `references/cli-commands.md` for the full command reference with examples.

## Hooks

- `SessionStart` hook — automatically lists claimed/in-progress/blocked tasks when Claude Code starts.
- `PreToolUse` hook on `Bash` — blocks `git commit` if any active task is missing `Next` or `Handoff`.

## Templates and Examples

When creating a task conversationally, follow the structure in [template.md](template.md).

For reference on what well-formed tasks look like at each stage:
- [examples/backlog-task.md](examples/backlog-task.md) — a ready-to-claim task with full context and acceptance criteria
- [examples/in-progress-task.md](examples/in-progress-task.md) — an active task with progress log entries and a proper handoff
- [examples/done-task.md](examples/done-task.md) — a completed task showing the expected quality of notes and handoff
