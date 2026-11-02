#!/usr/bin/env python3
"""Persistent study tasks exposed as MCP tools. Dates use Europe/Moscow."""
from datetime import date, datetime
import os
from pathlib import Path
import re
import sqlite3
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stdio import serve

ROOT = Path(__file__).resolve().parents[4]
STATUSES = ("todo", "in_progress", "done")


def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 500:
        raise ValueError(f"{field}: expected non-empty text, at most 500 characters")
    return value.strip()


def parse_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Date must use YYYY-MM-DD")
    return date.fromisoformat(value)


def database():
    path = Path(os.environ.get("STUDY_TRACKER_DB", str(ROOT / "practices/practice_04/mcp/study_tracker/data/tasks.sqlite3")))
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY, title TEXT NOT NULL, course TEXT NOT NULL,
        deadline TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'todo',
        created_at TEXT NOT NULL)""")
    return connection


def task_view(row, today=None):
    today = today or datetime.now(ZoneInfo("Europe/Moscow")).date()
    task = dict(row)
    task["days_left"] = (date.fromisoformat(task["deadline"]) - today).days
    task["overdue"] = task["days_left"] < 0 and task["status"] != "done"
    return task


def add_task(title, course, deadline):
    title, course = text(title, "title"), text(course, "course")
    deadline = parse_date(deadline).isoformat()
    connection = database()
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, course, deadline, created_at) VALUES (?, ?, ?, ?)",
                (title, course, deadline, datetime.now(ZoneInfo("Europe/Moscow")).isoformat()))
            return task_view(connection.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())
    finally:
        connection.close()


def list_tasks(course=None, status=None):
    conditions, values = [], []
    if course is not None:
        conditions.append("course = ?")
        values.append(text(course, "course"))
    if status is not None:
        if status not in STATUSES:
            raise ValueError("status must be todo, in_progress or done")
        conditions.append("status = ?")
        values.append(status)
    connection = database()
    try:
        query = "SELECT * FROM tasks" + (" WHERE " + " AND ".join(conditions) if conditions else "")
        rows = connection.execute(query + " ORDER BY deadline, id", values).fetchall()
        return {"tasks": [task_view(row) for row in rows], "count": len(rows)}
    finally:
        connection.close()


def update_task_status(task_id, status):
    if type(task_id) is not int or task_id < 1:
        raise ValueError("task_id must be a positive integer")
    if status not in STATUSES:
        raise ValueError("status must be todo, in_progress or done")
    connection = database()
    try:
        with connection:
            if connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)).rowcount == 0:
                raise ValueError(f"Task {task_id} not found")
            return task_view(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())
    finally:
        connection.close()


def study_dashboard(as_of=None):
    today = parse_date(as_of) if as_of is not None else datetime.now(ZoneInfo("Europe/Moscow")).date()
    tasks = [task_view(task, today) for task in list_tasks()["tasks"]]
    counts = {status: sum(task["status"] == status for task in tasks) for status in STATUSES}
    active = [task for task in tasks if task["status"] != "done"]
    return {"as_of": today.isoformat(), "timezone": "Europe/Moscow", "total": len(tasks),
            "by_status": counts, "progress_percent": round(100 * counts["done"] / len(tasks), 1) if tasks else 0,
            "overdue": [task for task in active if task["overdue"]],
            "due_soon": [task for task in active if 0 <= task["days_left"] <= 7],
            "next_task": active[0] if active else None}


def tool(name, description, properties, required=(), readonly=True):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties,
                            "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": readonly, "destructiveHint": False, "openWorldHint": False}}


STRING = {"type": "string"}
STATUS = {"type": "string", "enum": list(STATUSES)}
TOOLS = [
    tool("add_task", "Добавить учебное задание; сохраняет данные в SQLite. Дедлайн YYYY-MM-DD.",
         {"title": STRING, "course": STRING, "deadline": STRING}, ("title", "course", "deadline"), False),
    tool("list_tasks", "Показать задания по дедлайну, можно фильтровать по курсу и статусу.",
         {"course": STRING, "status": STATUS}),
    tool("update_task_status", "Изменить статус существующего задания по ID.",
         {"task_id": {"type": "integer", "minimum": 1}, "status": STATUS}, ("task_id", "status"), False),
    tool("study_dashboard", "Сводка прогресса, просроченные задания, дедлайны на 7 дней и следующая задача.",
         {"as_of": {"type": "string", "description": "Дата YYYY-MM-DD; по умолчанию сегодня в Москве"}}),
]

if __name__ == "__main__":
    serve("study-tracker", TOOLS, {item["name"]: globals()[item["name"]] for item in TOOLS})
