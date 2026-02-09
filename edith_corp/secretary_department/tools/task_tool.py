#!/usr/bin/env python3
"""
秘書部門 - タスク管理ツール
tasks.json に対する CRUD 操作を提供する。
秘書エージェントが Bash で実行する。

Usage:
  python3 task_tool.py list [--status pending] [--category business] [--due today|week|overdue] [--assignee ai] [--urgency now]
  python3 task_tool.py add "タスクタイトル" [--description "詳細"] [--priority high] [--urgency now] [--assignee tsuruta] [--category business] [--project room8] [--due 2026-02-15]
  python3 task_tool.py update <id> [--title "新タイトル"] [--status completed] [--priority low] [--urgency anytime] [--assignee outsource] [--due 2026-03-01]
  python3 task_tool.py complete <id>
  python3 task_tool.py delete <id>
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, date, timedelta

_THIS_DIR = Path(__file__).resolve().parent
_SECRETARY_OUTPUT = Path.home() / "Documents" / "edith_output" / "secretary"
TASKS_FILE = _SECRETARY_OUTPUT / "tasks.json"


def _ensure_dir():
    _SECRETARY_OUTPUT.mkdir(parents=True, exist_ok=True)


def _load_tasks() -> dict:
    _ensure_dir()
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"tasks": [], "next_id": 1}


def _save_tasks(data: dict):
    _ensure_dir()
    TASKS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _make_id(n: int) -> str:
    return f"t{n:03d}"


def cmd_list(args) -> dict:
    """タスク一覧（フィルタ可）"""
    data = _load_tasks()
    tasks = data["tasks"]

    # フィルタ
    if args.status:
        tasks = [t for t in tasks if t["status"] == args.status]
    if args.category:
        tasks = [t for t in tasks if t.get("category") == args.category]
    if args.project:
        tasks = [t for t in tasks if t.get("project") == args.project]
    if args.assignee:
        tasks = [t for t in tasks if t.get("assignee") == args.assignee]
    if args.urgency:
        tasks = [t for t in tasks if t.get("urgency") == args.urgency]

    today = date.today()
    if args.due == "today":
        tasks = [t for t in tasks if t.get("due_date") == today.isoformat()]
    elif args.due == "week":
        week_end = today + timedelta(days=7)
        tasks = [
            t for t in tasks
            if t.get("due_date") and t["due_date"] <= week_end.isoformat()
        ]
    elif args.due == "overdue":
        tasks = [
            t for t in tasks
            if t.get("due_date")
            and t["due_date"] < today.isoformat()
            and t["status"] not in ("completed", "cancelled")
        ]

    return {
        "status": "success",
        "tasks": tasks,
        "count": len(tasks),
        "total": len(data["tasks"]),
    }


def cmd_add(args) -> dict:
    """タスク追加"""
    data = _load_tasks()
    task_id = _make_id(data["next_id"])
    now = _now_iso()

    task = {
        "id": task_id,
        "title": args.title,
        "description": args.description or "",
        "status": "pending",
        "priority": args.priority or "medium",
        "urgency": args.urgency or "soon",
        "assignee": args.assignee or "tsuruta",
        "category": args.category or "business",
        "project": args.project or "",
        "due_date": args.due or None,
        "created_at": now,
        "updated_at": now,
        "completed_at": None,
    }

    data["tasks"].append(task)
    data["next_id"] += 1
    _save_tasks(data)

    return {
        "status": "success",
        "action": "added",
        "task": task,
    }


def cmd_update(args) -> dict:
    """タスク更新"""
    data = _load_tasks()

    for task in data["tasks"]:
        if task["id"] == args.id:
            if args.title:
                task["title"] = args.title
            if args.description:
                task["description"] = args.description
            if args.status:
                task["status"] = args.status
                if args.status == "completed":
                    task["completed_at"] = _now_iso()
            if args.priority:
                task["priority"] = args.priority
            if args.due:
                task["due_date"] = args.due
            if args.project:
                task["project"] = args.project
            if args.category:
                task["category"] = args.category
            if args.urgency:
                task["urgency"] = args.urgency
            if args.assignee:
                task["assignee"] = args.assignee
            task["updated_at"] = _now_iso()
            _save_tasks(data)
            return {
                "status": "success",
                "action": "updated",
                "task": task,
            }

    return {"status": "error", "error": f"Task {args.id} not found"}


def cmd_complete(args) -> dict:
    """タスク完了"""
    data = _load_tasks()

    for task in data["tasks"]:
        if task["id"] == args.id:
            task["status"] = "completed"
            task["completed_at"] = _now_iso()
            task["updated_at"] = _now_iso()
            _save_tasks(data)
            return {
                "status": "success",
                "action": "completed",
                "task": task,
            }

    return {"status": "error", "error": f"Task {args.id} not found"}


def cmd_delete(args) -> dict:
    """タスク削除"""
    data = _load_tasks()
    original_count = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != args.id]

    if len(data["tasks"]) == original_count:
        return {"status": "error", "error": f"Task {args.id} not found"}

    _save_tasks(data)
    return {
        "status": "success",
        "action": "deleted",
        "deleted_id": args.id,
    }


def main():
    parser = argparse.ArgumentParser(description="秘書部門タスク管理ツール")
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # list
    p_list = subparsers.add_parser("list", help="タスク一覧")
    p_list.add_argument("--status", choices=["pending", "in_progress", "completed", "cancelled"])
    p_list.add_argument("--category", choices=["business", "personal"])
    p_list.add_argument("--project")
    p_list.add_argument("--due", choices=["today", "week", "overdue"])
    p_list.add_argument("--assignee", choices=["tsuruta", "ai", "outsource"])
    p_list.add_argument("--urgency", choices=["now", "soon", "anytime"])

    # add
    p_add = subparsers.add_parser("add", help="タスク追加")
    p_add.add_argument("title", help="タスクタイトル")
    p_add.add_argument("--description", "-d", help="詳細")
    p_add.add_argument("--priority", "-p", choices=["high", "medium", "low"])
    p_add.add_argument("--urgency", "-u", choices=["now", "soon", "anytime"], help="緊急度 (now=今すぐ, soon=近いうち, anytime=いつでも)")
    p_add.add_argument("--assignee", "-a", choices=["tsuruta", "ai", "outsource"], help="誰がやるか")
    p_add.add_argument("--category", "-c", choices=["business", "personal"])
    p_add.add_argument("--project", help="プロジェクトタグ")
    p_add.add_argument("--due", help="期限 (YYYY-MM-DD)")

    # update
    p_update = subparsers.add_parser("update", help="タスク更新")
    p_update.add_argument("id", help="タスクID (例: t001)")
    p_update.add_argument("--title")
    p_update.add_argument("--description")
    p_update.add_argument("--status", choices=["pending", "in_progress", "completed", "cancelled"])
    p_update.add_argument("--priority", choices=["high", "medium", "low"])
    p_update.add_argument("--urgency", choices=["now", "soon", "anytime"])
    p_update.add_argument("--assignee", choices=["tsuruta", "ai", "outsource"])
    p_update.add_argument("--category", choices=["business", "personal"])
    p_update.add_argument("--project")
    p_update.add_argument("--due", help="期限 (YYYY-MM-DD)")

    # complete
    p_complete = subparsers.add_parser("complete", help="タスク完了")
    p_complete.add_argument("id", help="タスクID")

    # delete
    p_delete = subparsers.add_parser("delete", help="タスク削除")
    p_delete.add_argument("id", help="タスクID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "list": cmd_list,
        "add": cmd_add,
        "update": cmd_update,
        "complete": cmd_complete,
        "delete": cmd_delete,
    }

    try:
        result = commands[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        import traceback
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
