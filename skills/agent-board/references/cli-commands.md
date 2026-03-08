# Agent Board CLI Commands

1. `python3 agent_board.py list [--status STATUS]` — prints all tasks, optionally filtering by status (`backlog`, `claimed`, `in_progress`, `blocked`, `review`, `done`).

2. `python3 agent_board.py show T-123` — prints the raw Markdown for task `T-123`.

3. `python3 agent_board.py create --title "..." --context "..." --acceptance "..." --plan "..."` — creates a new `.agents/board/tasks/T-YYYYMMDDHHMMSS.md` file with the default section skeleton.

4. `python3 agent_board.py claim T-123 --agent claude` — marks the task as `claimed`, sets `claimed_by`, rotates a TTL (default 120 min in `.agents/board/config.yml`), appends a Progress Log entry.

5. `python3 agent_board.py log T-123 --note "Implemented parser"` — appends a timestamped Progress Log entry and updates `updated_at`.

6. `python3 agent_board.py handoff T-123 --note "Need integration test" --next "Validate retry loops"` — rewrites the `Handoff` and `Next` sections.

7. `python3 agent_board.py status T-123 --status review --owner claude` — changes `status`, optionally updates `owner`, records a Progress Log entry.

8. `python3 agent_board.py validate --statuses claimed,in_progress,blocked --require-next --require-handoff` — scans active tasks and fails if `Next` or `Handoff` sections are empty. Used by the pre-commit hook.

Always run the CLI from the project root so `agent_board.py` can find `.agents/board`.
