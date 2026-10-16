"""Lint rule: the agent roster and the agent files agree, including models.

A roster carries the operational list — what each agent is for, which model it
runs on, when to spawn it. It is the file a person reads before deciding to
delegate, and the file nobody updates when an agent is added in the middle of
some other task.

Two drifts, both quiet:

  * an agent file with no roster row — capability nobody knows exists, spawned
    by whoever happened to write it and by nobody else
  * a roster row whose Model column disagrees with the agent's frontmatter —
    the roster says opus, the file says sonnet, and the cost model in someone's
    head is wrong by a factor

Two surfaces, checked the same way:

  * the plugin: `<plugin>/agents/*.md` against `<plugin>/docs/agent-roster.md`
    (the roster lives in docs/ because a plugin's agents/ directory may hold
    nothing but agent definitions)
  * the project: `<repo>/.claude/agents/*.md` against its own `README.md`, for
    a fork's own additions. Architect agents (`*-architect.md`) are exempt:
    framework-build scaffolding, documented as prose.
"""

import re

CHECK_ID = "agent-roster-match"
SEVERITY = "medium"

_ROW = re.compile(r"^\|\s*\[`(?P<name>[a-z0-9-]+)`\]\([^)]+\)\s*\|(?P<rest>.*)\|\s*$", re.MULTILINE)
_FM_MODEL = re.compile(r"(?m)^model:\s*(\S+)\s*$")


def _check(ctx, agents_dir, roster, label: str) -> None:
    if not agents_dir.is_dir():
        return

    on_disk = {
        f.stem: f for f in sorted(agents_dir.glob("*.md"))
        if f.name != "README.md" and not f.stem.endswith("-architect")
    }

    if not roster.is_file():
        if on_disk:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{label}: roster {roster.name} missing — {len(on_disk)} operational agent(s) with no roster")
        return

    body = roster.read_text(encoding="utf-8")
    listed: dict[str, str] = {}
    for m in _ROW.finditer(body):
        cells = [c.strip() for c in m.group("rest").split("|")]
        # roster shape: | agent | one-liner | model | when to spawn |
        model = cells[1] if len(cells) > 1 else ""
        name = m.group("name")
        if name.endswith("-architect"):
            continue  # frozen bootstrap population, documented separately
        listed[name] = model

    for name in sorted(set(on_disk) - set(listed)):
        ctx.add(SEVERITY, CHECK_ID,
                f"{label}: {name}.md has no row in the agent roster ({roster.name}) "
                "— an undocumented agent is one only its author will ever spawn")

    for name in sorted(set(listed) - set(on_disk)):
        ctx.add(SEVERITY, CHECK_ID,
                f"{label}: roster lists `{name}`, but {name}.md does not exist")

    for name in sorted(set(listed) & set(on_disk)):
        declared = listed[name].strip("` ")
        head = on_disk[name].read_text(encoding="utf-8")[:2000]
        m = _FM_MODEL.search(head)
        if not m:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{label}: {name}.md has no `model:` in frontmatter, roster says `{declared}`")
            continue
        actual = m.group(1).strip("`\"'")
        if declared and actual != declared:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{label}: {name}.md runs `{actual}`, roster says `{declared}`")


def run(ctx) -> None:
    plugin = getattr(ctx, "plugin", None)
    if plugin is not None:
        _check(ctx, plugin / "agents", plugin / "docs" / "agent-roster.md", "plugin agents/")
    project_agents = ctx.repo / ".claude" / "agents"
    _check(ctx, project_agents, project_agents / "README.md", ".claude/agents/")
