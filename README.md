# MCP Framework Getting Started

A [FastMCP](https://github.com/jlowin/fastmcp) server that provides task management tools and skill resources. This is the companion MCP server for the [agent-framework-getting-started](../agent-framework-getting-started) project.

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
git clone <repo-url>
cd mcp-framework-getting-started

uv venv --python 3.13
source .venv/bin/activate
uv sync --all-groups
```

### Run the Server

```bash
uv run python server.py
```

The server starts on `http://localhost:8000/mcp` using Streamable HTTP transport.

### Test with MCP Inspector

```bash
uvx fastmcp inspect server.py
```

## Architecture

```
server.py               # FastMCP server entry point
tools/
  task_tools.py         # Task management tools (create, list, search, stats)
skills/
  task-management/      # Task management skill (SKILL.md + references/)
  code-review/          # Code review skill (SKILL.md)
tests/
  test_server.py        # Tool + bundle tests
```

### Server (`server.py`)

The server uses FastMCP with a `SkillsDirectoryProvider` to automatically expose skills as MCP resources. Tools are registered via the `tools/task_tools.py` module.

```python
from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP(
    "taskflow-mcp",
    providers=[SkillsDirectoryProvider(str(SKILLS_DIR))],
)
```

## Tools

The server exposes four task management tools:

| Tool | Description | Key Args |
|---|---|---|
| `create_task` | Create a new task | `title` (required), `priority` (P0-P3), `assignee` |
| `list_tasks` | List tasks with optional filters | `status`, `assignee` |
| `search_tasks` | Search tasks by title substring | `query` |
| `get_task_stats` | Summary statistics | (none) |

Tasks are stored in memory and reset when the server restarts.

### Example

```python
# From an agent framework client:
from agent_framework import MCPStreamableHTTPTool

tool = MCPStreamableHTTPTool(
    name="taskflow",
    url="http://localhost:8000/mcp",
)
```

## Skills

Skills are Markdown files with YAML frontmatter, served as MCP resources via `SkillsDirectoryProvider`.

| Skill | Path | Description |
|---|---|---|
| Task Management | `skills/task-management/SKILL.md` | Prioritisation, lifecycle, best practices |
| Code Review | `skills/code-review/SKILL.md` | Review checklist, tone guidelines |

Skills are discoverable through the MCP resources API. The agent-framework project uses `MCPSkillsClient` to discover both tools and skills from this server.

### Bundle Resources

Each skill directory can be served as a zip bundle via the `bundle://` resource:

```
bundle://task-management  → zip of skills/task-management/
bundle://code-review      → zip of skills/code-review/
```

This is useful for clients that want to download an entire skill directory (SKILL.md + reference files) in one request.

## Running Tests

```bash
uv run pytest
```

Tests cover all four tools and the skill bundle resource endpoint.

## Integration with Agent Framework

From the companion agent-framework-getting-started project:

```python
from taskflow.mcp import MCPSkillsClient
from taskflow.middleware import MCPSkillsChatMiddleware
from taskflow.config import create_client

# 1. Start this server: uv run python server.py

# 2. Discover tools + skills
mcp_client = MCPSkillsClient("http://localhost:8000/mcp")
result = await mcp_client.discover()

# 3. Create an agent with MCP tools and skill context
client = create_client()
agent = client.as_agent(
    name="task-agent",
    instructions="You are a task management assistant.",
    tools=result.tools,
    middleware=[MCPSkillsChatMiddleware(result.skills)],
)
```

See Phase 5 (Skills & MCP) and Phase 8 (Dynamic Agents) in the agent-framework project for detailed examples.

## Configuration

| Option | Default | Description |
|---|---|---|
| Host | `0.0.0.0` | Bind address |
| Port | `8000` | HTTP port |
| Transport | `http` | Streamable HTTP (default) |

To change the port:

```python
# In server.py
mcp.run(transport="http", host="0.0.0.0", port=9000)
```
