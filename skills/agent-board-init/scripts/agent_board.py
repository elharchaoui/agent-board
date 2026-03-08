#!/usr/bin/env python3
import argparse
import ast
import datetime
import os
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(".agents/board")
TASK_DIR = BASE_DIR / "tasks"
CONFIG_FILE = BASE_DIR / "config.yml"
DEFAULT_SECTIONS = ["Context", "Acceptance", "Plan", "Progress Log", "Handoff", "Next"]


def ensure_dirs():
    TASK_DIR.mkdir(parents=True, exist_ok=True)


def read_config() -> Dict[str, str]:
    config: Dict[str, str] = {}
    if not CONFIG_FILE.exists():
        return config
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        config[key.strip()] = value.strip()
    return config


def parse_frontmatter(lines: List[str]) -> Tuple[Dict[str, object], List[str]]:
    data: Dict[str, object] = {}
    order: List[str] = []
    for raw in lines:
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            parsed = None
        else:
            if value.startswith("[") or value.startswith("{"):
                try:
                    parsed = ast.literal_eval(value)
                except Exception:
                    parsed = value
            else:
                parsed = value
        data[key] = parsed
        order.append(key)
    return data, order


def format_value(value):
    if isinstance(value, list):
        quoted = []
        for item in value:
            item = str(item)
            if '"' in item:
                item = item.replace('"', '\\"')
            quoted.append(f'"{item}"')
        return "[%s]" % ", ".join(quoted)
    if value is None:
        return ""
    return str(value)


def serialize_frontmatter(data: Dict[str, object], order: List[str]) -> str:
    lines = ["---"]
    for key in order:
        if key not in data:
            continue
        value = data[key]
        lines.append(f"{key}: {format_value(value)}")
    for key in data:
        if key in order:
            continue
        lines.append(f"{key}: {format_value(data[key])}")
    lines.append("---")
    return "\n".join(lines)


def parse_sections(body: str) -> Tuple[Dict[str, List[str]], List[str]]:
    sections: Dict[str, List[str]] = {}
    order: List[str] = []
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            order.append(current)
            sections[current] = []
            continue
        if current is None:
            continue
        sections[current].append(line)
    return sections, order


def render_sections(sections: Dict[str, List[str]], order: List[str]) -> str:
    lines: List[str] = []
    for name in order:
        lines.append(f"## {name}")
        lines.extend(sections.get(name, []))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def load_task(task_id: str) -> Tuple[Dict[str, object], List[str], Dict[str, List[str]], List[str]]:
    path = TASK_DIR / f"{task_id}.md"
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text()
    if not text.startswith("---"):
        raise ValueError("Missing frontmatter in %s" % task_id)
    _, rest = text.split("---", 1)
    front_lines, body = rest.split("---", 1)
    front_data, front_order = parse_frontmatter(front_lines.strip().splitlines())
    body = body.strip("\n")
    sections, section_order = parse_sections(body)
    return front_data, front_order, sections, section_order


def save_task(task_id: str, front: Dict[str, object], front_order: List[str], sections: Dict[str, List[str]], section_order: List[str]):
    path = TASK_DIR / f"{task_id}.md"
    front["updated_at"] = datetime.datetime.utcnow().isoformat()
    ensure_dirs()
    content = serialize_frontmatter(front, front_order) + "\n\n" + render_sections(sections, section_order)
    path.write_text(content)


def normalize_sections(sections: Dict[str, List[str]], section_order: List[str]) -> Tuple[Dict[str, List[str]], List[str]]:
    for name in DEFAULT_SECTIONS:
        if name not in sections:
            sections[name] = []
            section_order.append(name)
    seen = []
    for name in section_order:
        if name not in seen:
            seen.append(name)
    return sections, seen


def cmd_list(args):
    tasks = sorted(TASK_DIR.glob("*.md"))
    for path in tasks:
        task_id = path.stem
        front, order, _, _ = load_task(task_id)
        status = front.get("status", "unknown")
        if args.status and status != args.status:
            continue
        title = front.get("title", "") or ""
        owner = front.get("owner", "") or ""
        claimed_by = front.get("claimed_by", "") or ""
        print(f"{task_id:10} {status:12} {owner:10} {claimed_by:10} {title}")


def cmd_show(args):
    path = TASK_DIR / f"{args.task}.md"
    if not path.exists():
        raise FileNotFoundError(path)
    print(path.read_text())


def create_default_sections() -> Tuple[Dict[str, List[str]], List[str]]:
    sections = {}
    for name in DEFAULT_SECTIONS:
        sections[name] = [
            "" if name not in ("Progress Log", "Handoff", "Next") else ""
        ]
    return sections, DEFAULT_SECTIONS.copy()


def cmd_create(args):
    task_id = args.id or f"T-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    path = TASK_DIR / f"{task_id}.md"
    if path.exists():
        raise FileExistsError(task_id)
    front: Dict[str, object] = {
        "id": task_id,
        "title": args.title,
        "type": args.type or "feature",
        "priority": args.priority or "medium",
        "status": "backlog",
        "owner": args.owner or "",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "updated_at": datetime.datetime.utcnow().isoformat(),
    }
    if args.labels:
        front["labels"] = [label.strip() for label in args.labels.split(",") if label.strip()]
    sections, order = create_default_sections()
    sections["Context"] = [args.context or ""]
    sections["Acceptance"] = [args.acceptance or ""]
    sections["Plan"] = [args.plan or ""]
    sections["Progress Log"] = ["- created"]
    save_task(task_id, front, list(front.keys()), sections, order)
    print(f"Created {task_id}")


def claim_task(task_id: str, agent: str, ttl_minutes: int):
    front, order, sections, section_order = load_task(task_id)
    front["claimed_by"] = agent
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=ttl_minutes)
    front["claimed_until"] = expires.isoformat()
    front["status"] = "claimed"
    log_entry = _progress_entry(agent, "claimed")
    append_progress(sections, "Progress Log", log_entry, section_order)
    save_task(task_id, front, order, sections, section_order)


def _progress_entry(agent: str, text: str):
    timestamp = datetime.datetime.utcnow().isoformat(timespec="seconds")
    return f"- {timestamp} {agent}: {text}"


def append_progress(sections: Dict[str, List[str]], name: str, entry: str, section_order: List[str]):
    if name not in sections:
        sections[name] = []
        section_order.append(name)
    sections[name].append(entry)


def cmd_claim(args):
    config = read_config()
    ttl = int(config.get("default_ttl_minutes", "120"))
    claim_task(args.task, args.agent or "agent", ttl)
    print(f"Claimed {args.task} for {ttl} minutes")


def cmd_log(args):
    front, order, sections, section_order = load_task(args.task)
    append_progress(sections, "Progress Log", _progress_entry(args.agent or "agent", args.note), section_order)
    save_task(args.task, front, order, sections, section_order)
    print(f"Appended log to {args.task}")


def cmd_handoff(args):
    front, order, sections, section_order = load_task(args.task)
    sections["Handoff"] = [args.note]
    sections["Next"] = [args.next or ""]
    if "Handoff" not in section_order:
        section_order.append("Handoff")
    if "Next" not in section_order:
        section_order.append("Next")
    save_task(args.task, front, order, sections, section_order)
    print(f"Handoff updated for {args.task}")


def has_content(lines: List[str]) -> bool:
    for line in lines:
        if line.strip():
            return True
    return False


def ensure_section(name: str, sections: Dict[str, List[str]], section_order: List[str]) -> None:
    if name not in sections:
        sections[name] = []
        section_order.append(name)


def cmd_update_status(args):
    front, order, sections, section_order = load_task(args.task)
    front["status"] = args.status
    if args.owner:
        front["owner"] = args.owner
    append_progress(sections, "Progress Log", _progress_entry(args.agent or "agent", f"status -> {args.status}"), section_order)
    save_task(args.task, front, order, sections, section_order)
    print(f"{args.task} marked {args.status}")


def cmd_validate(args):
    statuses = []
    if args.statuses:
        statuses = [status.strip() for status in args.statuses.split(",") if status.strip()]
    issues: List[str] = []
    for path in sorted(TASK_DIR.glob("*.md")):
        task_id = path.stem
        front, _, sections, section_order = load_task(task_id)
        if statuses and front.get("status") not in statuses:
            continue
        if args.require_next:
            ensure_section("Next", sections, section_order)
            if not has_content(sections.get("Next", [])):
                issues.append(f"{task_id}: missing Next entry")
        if args.require_handoff:
            ensure_section("Handoff", sections, section_order)
            if not has_content(sections.get("Handoff", [])):
                issues.append(f"{task_id}: missing Handoff entry")
    for issue in issues:
        print(issue)
    if issues:
        print("Validation failed: update the board before committing.")
        raise SystemExit(1)
    print("Validation passed.")


def main():
    ensure_dirs()
    parser = argparse.ArgumentParser(description="Agent Board CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    parser_validate = sub.add_parser("validate")
    parser_validate.add_argument("--statuses")
    parser_validate.add_argument("--require-next", action="store_true")
    parser_validate.add_argument("--require-handoff", action="store_true")
    parser_validate.set_defaults(func=cmd_validate)

    parser_list = sub.add_parser("list")
    parser_list.add_argument("--status")
    parser_list.set_defaults(func=cmd_list)

    parser_show = sub.add_parser("show")
    parser_show.add_argument("task")
    parser_show.set_defaults(func=cmd_show)

    parser_create = sub.add_parser("create")
    parser_create.add_argument("--id")
    parser_create.add_argument("--title", required=True)
    parser_create.add_argument("--type")
    parser_create.add_argument("--priority")
    parser_create.add_argument("--owner")
    parser_create.add_argument("--labels")
    parser_create.add_argument("--context")
    parser_create.add_argument("--acceptance")
    parser_create.add_argument("--plan")
    parser_create.set_defaults(func=cmd_create)

    parser_claim = sub.add_parser("claim")
    parser_claim.add_argument("task")
    parser_claim.add_argument("--agent")
    parser_claim.set_defaults(func=cmd_claim)

    parser_log = sub.add_parser("log")
    parser_log.add_argument("task")
    parser_log.add_argument("--note", required=True)
    parser_log.add_argument("--agent")
    parser_log.set_defaults(func=cmd_log)

    parser_handoff = sub.add_parser("handoff")
    parser_handoff.add_argument("task")
    parser_handoff.add_argument("--note", required=True)
    parser_handoff.add_argument("--next")
    parser_handoff.set_defaults(func=cmd_handoff)

    parser_status = sub.add_parser("status")
    parser_status.add_argument("task")
    parser_status.add_argument("--status", required=True)
    parser_status.add_argument("--agent")
    parser_status.add_argument("--owner")
    parser_status.set_defaults(func=cmd_update_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
