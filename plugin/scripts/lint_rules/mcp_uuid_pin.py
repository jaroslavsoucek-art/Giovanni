"""Lint rule: no hardcoded UUID MCP server prefixes.

Some harnesses expose connectors under a generated identifier —
`mcp__3f2a1b7c-....__search` — that is stable for one machine, one account, one
install, and nothing else. Pinning it into an agent definition or a workflow
produces the worst kind of breakage: the tool is simply not found, the agent
reports the source as unavailable, and the digest renders a clean "no signal"
for a connector that was working the whole time.

Use a named server instead (`.mcp.json`, giving `mcp__atlassian__…`), or resolve
by tool name at run time. Both survive a re-install; a UUID does not.

Comment lines are skipped — documenting the anti-pattern is not committing it.
"""

import re

CHECK_ID = "mcp-uuid-pin"
SEVERITY = "high"

_UUID_PREFIX = re.compile(
    r"mcp__[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}__"
)
SCAN_DIRS = (".claude/agents", ".claude/commands", ".claude/workflows", ".claude/hooks")


def run(ctx) -> None:
    for rel_dir in SCAN_DIRS:
        d = ctx.repo / rel_dir
        if not d.is_dir():
            continue
        for path in sorted(d.iterdir()):
            if not path.is_file() or path.suffix not in {".md", ".sh", ".json"}:
                continue
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                stripped = line.lstrip()
                if stripped.startswith(("#", "<!--", "//")):
                    continue
                if _UUID_PREFIX.search(line):
                    ctx.add(SEVERITY, CHECK_ID,
                            f"{rel_dir}/{path.name}:{i}: hardcoded UUID MCP prefix — it is valid for "
                            "one install only, and when it stops matching the source reports as "
                            "unavailable rather than as broken. Use a named server (.mcp.json) or "
                            "resolve by tool name.")
