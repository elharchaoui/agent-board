# Agent Board

A lightweight Jira-like task board that lives inside your repo. Tasks are Markdown files with structured frontmatter. `agent_board.py` is the CLI that claims work, logs progress, and captures handoffs — no external services required.

---

## Install

```
/plugin marketplace add elharchaoui/agent-board
/plugin install agent-board@elharchaoui/agent-board
/agent-board-init
```

That's it. The init skill writes `agent_board.py`, creates `.agents/board/`, and optionally wires the git pre-commit hook directly into your project.

---

## How it works

Tasks live in `.agents/board/tasks/*.md`:

```
---
id: T-20240101120000
title: "Add retry logic"
status: in_progress
claimed_by: claude
claimed_until: 2024-01-01T14:00:00
---

## Context
## Acceptance
## Plan
## Progress Log
## Handoff
## Next
```

### Workflow

```bash
# See what's active
python3 agent_board.py list

# Claim before editing
python3 agent_board.py claim T-XXX --agent claude

# Log progress
python3 agent_board.py log T-XXX --note "Implemented the parser"

# Hand off before pausing
python3 agent_board.py handoff T-XXX --note "Parser done, needs tests" --next "Write unit tests for edge cases"
python3 agent_board.py status T-XXX --status review
```

### All commands

| Command | Description |
|---|---|
| `list [--status STATUS]` | Show tasks, optionally filtered by status |
| `show T-XXX` | Print full task file |
| `create --title "..."` | Scaffold a new task |
| `claim T-XXX --agent NAME` | Claim with TTL (default 120 min) |
| `log T-XXX --note "..."` | Append progress entry |
| `handoff T-XXX --note "..." --next "..."` | Update Handoff + Next sections |
| `status T-XXX --status STATUS` | Change task status |
| `validate --statuses ... --require-next --require-handoff` | Fail if active tasks lack handoff notes |

---

## Repository layout

```
.claude-plugin/
  plugin.json          ← Claude Code plugin manifest
  marketplace.json     ← marketplace catalog for /plugin marketplace add
skills/
  agent-board/
    SKILL.md           ← workflow skill (/agent-board)
    references/
      cli-commands.md  ← command reference loaded on demand
  agent-board-init/
    SKILL.md           ← init skill (/agent-board-init) — embeds all artifacts
hooks/
  hooks.json           ← Claude Code hooks (SessionStart + PreToolUse on Bash)
.agents/               ← board data for this repo (dog-fooding)
  board/
    config.yml         ← statuses, labels, TTL defaults
    templates/
      task_template.md ← scaffold for new tasks
  hooks/
    pre_commit_check.sh ← git hook script (written to user projects by init skill)
agent_board.py         ← CLI source of truth (embedded in init skill)
```

---

## Hooks

### Claude Code hooks (`hooks/hooks.json`)
- **SessionStart** — lists claimed/in-progress/blocked tasks when Claude Code starts.
- **PreToolUse on Bash** — intercepts `git commit` and runs `validate` before allowing it.

### Git hooks (`.agents/hooks/`)
- `pre_commit_check.sh` — same validation, for non-Claude-Code workflows. Symlink to `.git/hooks/pre-commit` or let `install.sh` do it.
