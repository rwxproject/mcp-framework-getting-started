# MCP Framework Getting Started

FastMCP server providing task management tools and skill resources. Companion to the agent-framework-getting-started project.

## Project Structure

```
server.py               # FastMCP entry point — registers tools + providers, runs HTTP
tools/
  task_tools.py         # Four task tools: create_task, list_tasks, search_tasks, get_task_stats
skills/
  task-management/      # SKILL.md + references/prioritisation-guide.md
  code-review/          # SKILL.md
tests/
  test_server.py        # Tests for tools and bundle resources
```

## Key Patterns

### FastMCP Server

```python
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP("taskflow-mcp", providers=[SkillsDirectoryProvider(str(SKILLS_DIR))])
```

### Tool Registration

Tools are registered on the FastMCP instance via a `register(mcp)` function:

```python
@mcp_instance.tool
def create_task(title: str, priority: str = "P2", assignee: str | None = None) -> dict:
    """Create a new task."""
    ...
```

### Resource Endpoints

- **Skills** — auto-served by `SkillsDirectoryProvider` from the `skills/` directory
- **Bundles** — `bundle://{skill_name}` serves a zip of the skill directory

### Running

```bash
uv run python server.py          # HTTP on port 8000
uvx fastmcp inspect server.py    # MCP Inspector
```

## Coding Conventions

- Always use `from __future__ import annotations`
- Type-hint all function signatures
- Tools use sync functions (FastMCP handles async wrapping)
- Run tests with `uv run pytest`
- Format with `uv run ruff format .` and lint with `uv run ruff check .`
