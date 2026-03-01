# Architecture

## Overview

The MCP Framework Getting Started server is a [FastMCP](https://github.com/jlowin/fastmcp) application that exposes task management tools and skill resources over the Model Context Protocol (MCP) using Streamable HTTP transport.

## Components

### Server (`server.py`)

The entry point creates a `FastMCP` instance with:

1. **SkillsDirectoryProvider** — automatically discovers and serves `SKILL.md` files from the `skills/` directory as MCP resources.
2. **Task tools** — registered via `tools/task_tools.py`.
3. **Bundle resource** — a custom `bundle://{skill_name}` endpoint that serves skill directories as zip archives.

```
Client Request
     │
     ▼
FastMCP Server (port 8000)
     │
     ├── Tools ──────────── tools/task_tools.py
     │   ├── create_task        (in-memory task store)
     │   ├── list_tasks
     │   ├── search_tasks
     │   └── get_task_stats
     │
     ├── Resources ──────── SkillsDirectoryProvider
     │   ├── skills://task-management/SKILL.md
     │   └── skills://code-review/SKILL.md
     │
     └── Bundle ─────────── bundle://{skill_name}
         └── Returns zip of skill directory
```

### Tool Registration

Tools are defined in `tools/task_tools.py` and registered on the FastMCP instance via a `register(mcp)` function. This pattern keeps tool definitions separate from server setup.

The tools use an in-memory dictionary as the task store. Tasks are assigned auto-incrementing IDs (`TASK-0001`, `TASK-0002`, etc.) and stored with priority, status, assignee, and timestamp.

### Skill Provider

`SkillsDirectoryProvider` from FastMCP scans the `skills/` directory for subdirectories containing `SKILL.md` files. Each skill is served as an MCP resource that clients can read.

Skills follow the standard format: YAML frontmatter with metadata, followed by Markdown content with domain knowledge.

### Bundle Resources

The `bundle://{skill_name}` resource endpoint creates a zip archive of an entire skill directory on demand. This allows clients to download a complete skill (including reference files) in a single request.

## Integration Points

### Agent Framework Client

The companion agent-framework-getting-started project connects to this server using:

- **`MCPStreamableHTTPTool`** — discovers and invokes the four task tools.
- **`MCPSkillsClient`** — discovers both tools and skill resources, combining `MCPStreamableHTTPTool` (for tools) and `fastmcp.Client` (for resources).
- **`MCPSkillsChatMiddleware`** — injects discovered skill content as system messages in the agent's LLM calls.

### MCP Inspector

For development and debugging:

```bash
uvx fastmcp inspect server.py
```

This opens a browser-based tool showing all registered tools, resources, and prompts.

## Testing

Tests in `tests/test_server.py` use a `FakeMCP` class that mimics the `@mcp.tool` registration pattern. This allows testing tools without starting the HTTP server. Bundle resource tests import the `skill_bundle` function directly.
