"""Lint rule: no hardcoded UUID MCP server prefixes.

Some harnesses expose connectors under a generated identifier —
`mcp__3f2a1b7c-....__search` — that is stable for one machine, one account, one
install, and nothing else. Pinning it into an agent definition or a workflow
produces the worst kind of breakage: the tool is simply not found, the agent
reports the source as unavailable, and the digest renders a clean "no signal"
for a connector that was working the whole time.

Use a named server instead (`.mcp.json`, giving `mcp__atlassian__…`), or resolve
by tool name at run time. Both survive a re-install; a UUID does not.

Scanned: the plugin's agents, skills (recursively — procedures sit beside their
skill) and hooks, plus the project's own `.claude/{agents,commands,workflows,hooks}`.
Comment lines are skipped — documenting the anti-pattern is not committing it.
"""

import re

CHECK_ID = "mcp-uuid-pin"
SEVERITY = "high"

_UUID_PREFIX = re.compile(
    r"mcp__[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}__"
)
PROJECT_SCAN_DIRS = (".claude/agents", ".claude/commands", ".claude/workflows", ".claude/hooks")
PLUGIN_SCAN_DIRS = ("agents", "skills", "hooks")
SUFFIXES = {".md", ".sh", ".json"}


def _scan(ctx, root, rel_dir: str, recursive: bool) -> None:
    d = root / rel_dir
    if not d.is_dir():
        return
    paths = sorted(d.rglob("*")) if recursive else sorted(d.iterdir())
    for path in paths:
        if not path.is_file() or path.suffix not in SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        shown = f"{rel_dir}/{path.relative_to(d)}"
        for i, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith(("#", "<!--", "//")):
                continue
            if _UUID_PREFIX.search(line):
                ctx.add(SEVERITY, CHECK_ID,
                        f"{shown}:{i}: hardcoded UUID MCP prefix — it is valid for "
                        "one install only, and when it stops matching the source reports as "
                        "unavailable rather than as broken. Use a named server (.mcp.json) or "
                        "resolve by tool name.")


def run(ctx) -> None:
    plugin = getattr(ctx, "plugin", None)
    if plugin is not None:
        for rel_dir in PLUGIN_SCAN_DIRS:
            _scan(ctx, plugin, rel_dir, recursive=True)
    for rel_dir in PROJECT_SCAN_DIRS:
        _scan(ctx, ctx.repo, rel_dir, recursive=False)
