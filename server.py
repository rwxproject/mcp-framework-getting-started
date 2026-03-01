"""TaskFlow MCP Server — serves task tools and skill resources."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

SKILLS_DIR = Path(__file__).parent / "skills"

mcp = FastMCP(
    "taskflow-mcp",
    providers=[SkillsDirectoryProvider(str(SKILLS_DIR))],
)

# Register task tools
from tools.task_tools import register  # noqa: E402

register(mcp)


@mcp.resource("bundle://{skill_name}")
async def skill_bundle(skill_name: str) -> bytes:
    """Serve a skill directory as a zip bundle.

    Args:
        skill_name: Name of the skill directory to bundle.
    """
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.is_dir():
        return b""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(skill_dir.rglob("*")):
            if file_path.is_file():
                arcname = str(file_path.relative_to(skill_dir))
                zf.write(file_path, arcname)
    return buf.getvalue()


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
