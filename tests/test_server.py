"""Tests for the TaskFlow MCP server."""

from __future__ import annotations

import io
import zipfile

import pytest

# We need to test tools by importing and registering them
from tools.task_tools import register


class FakeMCP:
    """Minimal stand-in that collects @mcp.tool registrations."""

    def __init__(self) -> None:
        self.tools: dict[str, callable] = {}

    def tool(self, fn):
        self.tools[fn.__name__] = fn
        return fn


@pytest.fixture(autouse=True)
def _reset_task_store():
    """Clear the task store before each test."""
    import tools.task_tools as mod

    mod._tasks.clear()
    # Reset counter - create a new one
    import itertools

    mod._counter = itertools.count(1)
    yield


@pytest.fixture
def tools():
    """Register tools on a FakeMCP and return the tools dict."""
    fake = FakeMCP()
    register(fake)
    return fake.tools


class TestCreateTask:
    def test_creates_task_with_defaults(self, tools) -> None:
        result = tools["create_task"]("Buy groceries")
        assert result["id"] == "TASK-0001"
        assert result["title"] == "Buy groceries"
        assert result["priority"] == "P2"
        assert result["status"] == "open"
        assert result["assignee"] is None

    def test_creates_task_with_all_fields(self, tools) -> None:
        result = tools["create_task"]("Deploy v2", priority="P0", assignee="alice")
        assert result["priority"] == "P0"
        assert result["assignee"] == "alice"

    def test_invalid_priority_returns_error(self, tools) -> None:
        result = tools["create_task"]("Bad task", priority="P9")
        assert "error" in result

    def test_auto_incrementing_ids(self, tools) -> None:
        r1 = tools["create_task"]("Task A")
        r2 = tools["create_task"]("Task B")
        assert r1["id"] == "TASK-0001"
        assert r2["id"] == "TASK-0002"


class TestListTasks:
    def test_list_empty(self, tools) -> None:
        result = tools["list_tasks"]()
        assert result == []

    def test_list_all(self, tools) -> None:
        tools["create_task"]("A")
        tools["create_task"]("B")
        result = tools["list_tasks"]()
        assert len(result) == 2

    def test_filter_by_status(self, tools) -> None:
        tools["create_task"]("A")
        result = tools["list_tasks"](status="open")
        assert len(result) == 1
        result = tools["list_tasks"](status="done")
        assert len(result) == 0

    def test_filter_by_assignee(self, tools) -> None:
        tools["create_task"]("A", assignee="alice")
        tools["create_task"]("B", assignee="bob")
        result = tools["list_tasks"](assignee="alice")
        assert len(result) == 1
        assert result[0]["assignee"] == "alice"


class TestSearchTasks:
    def test_search_matches_title(self, tools) -> None:
        tools["create_task"]("Deploy backend API")
        tools["create_task"]("Write frontend tests")
        result = tools["search_tasks"]("backend")
        assert len(result) == 1
        assert "backend" in result[0]["title"].lower()

    def test_search_case_insensitive(self, tools) -> None:
        tools["create_task"]("Deploy Backend API")
        result = tools["search_tasks"]("BACKEND")
        assert len(result) == 1

    def test_search_no_match(self, tools) -> None:
        tools["create_task"]("Deploy")
        result = tools["search_tasks"]("nonexistent")
        assert result == []


class TestGetTaskStats:
    def test_stats_empty(self, tools) -> None:
        result = tools["get_task_stats"]()
        assert result["total"] == 0
        assert result["by_status"] == {}
        assert result["by_priority"] == {}

    def test_stats_with_tasks(self, tools) -> None:
        tools["create_task"]("A", priority="P0")
        tools["create_task"]("B", priority="P0")
        tools["create_task"]("C", priority="P2")
        result = tools["get_task_stats"]()
        assert result["total"] == 3
        assert result["by_priority"]["P0"] == 2
        assert result["by_priority"]["P2"] == 1
        assert result["by_status"]["open"] == 3


class TestSkillBundle:
    @pytest.mark.asyncio
    async def test_bundle_returns_valid_zip(self) -> None:
        from server import skill_bundle

        data = await skill_bundle("task-management")
        assert len(data) > 0

        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
        assert "SKILL.md" in names
        assert any("prioritisation-guide" in n for n in names)

    @pytest.mark.asyncio
    async def test_bundle_nonexistent_skill(self) -> None:
        from server import skill_bundle

        data = await skill_bundle("nonexistent-skill")
        assert data == b""

    @pytest.mark.asyncio
    async def test_bundle_code_review(self) -> None:
        from server import skill_bundle

        data = await skill_bundle("code-review")
        assert len(data) > 0

        zf = zipfile.ZipFile(io.BytesIO(data))
        names = zf.namelist()
        assert "SKILL.md" in names
