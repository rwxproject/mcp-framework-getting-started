"""Task management MCP tools — in-memory task store."""

from __future__ import annotations

import itertools
from datetime import datetime, timezone
from typing import Any

# The FastMCP instance is injected by server.py after import
_mcp: Any = None

_tasks: dict[str, dict] = {}
_counter = itertools.count(1)

VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}
VALID_STATUSES = {"open", "in_progress", "done"}


def register(mcp_instance: Any) -> None:
    """Register tools on the given FastMCP instance."""
    global _mcp
    _mcp = mcp_instance

    @mcp_instance.tool
    def create_task(
        title: str, priority: str = "P2", assignee: str | None = None
    ) -> dict:
        """Create a new task.

        Args:
            title: Task title (required).
            priority: Priority level — P0 (critical) to P3 (low). Default P2.
            assignee: Optional person assigned to the task.
        """
        if priority not in VALID_PRIORITIES:
            return {
                "error": f"Invalid priority: {priority}. Use one of {sorted(VALID_PRIORITIES)}"
            }

        task_id = f"TASK-{next(_counter):04d}"
        task = {
            "id": task_id,
            "title": title,
            "priority": priority,
            "status": "open",
            "assignee": assignee,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _tasks[task_id] = task
        return task

    @mcp_instance.tool
    def list_tasks(
        status: str | None = None, assignee: str | None = None
    ) -> list[dict]:
        """List tasks, optionally filtered by status and/or assignee.

        Args:
            status: Filter by status (open, in_progress, done).
            assignee: Filter by assignee name.
        """
        results = list(_tasks.values())
        if status:
            results = [t for t in results if t["status"] == status]
        if assignee:
            results = [t for t in results if t.get("assignee") == assignee]
        return results

    @mcp_instance.tool
    def search_tasks(query: str) -> list[dict]:
        """Search tasks by case-insensitive substring match on title.

        Args:
            query: Search string to match against task titles.
        """
        q = query.lower()
        return [t for t in _tasks.values() if q in t["title"].lower()]

    @mcp_instance.tool
    def get_task_stats() -> dict:
        """Get summary statistics about all tasks."""
        all_tasks = list(_tasks.values())
        by_status: dict[str, int] = {}
        by_priority: dict[str, int] = {}
        for t in all_tasks:
            by_status[t["status"]] = by_status.get(t["status"], 0) + 1
            by_priority[t["priority"]] = by_priority.get(t["priority"], 0) + 1
        return {
            "total": len(all_tasks),
            "by_status": by_status,
            "by_priority": by_priority,
        }
