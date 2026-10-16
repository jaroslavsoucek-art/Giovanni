"""Lint rule: the agent roster and the agent files agree, including models.

`.claude/agents/README.md` carries the operational roster — what each agent is
for, which model it runs on, when to spawn it. It is the file a person reads
before deciding to delegate, and the file nobody updates when an agent is added
in the middle of some other task.

Two drifts, both quiet:

  * an agent file with no roster row — capability nobody knows exists, spawned
    by whoever happened to write it and by nobody else
  * a roster row whose Model column disagrees with the agent's frontmatter —
    the roster says opus, the file says sonnet, and the cost model in someone's
    head is wrong by a factor

Architect agents (`*-architect.md`) are exempt: they are framework-build
scaffolding, frozen after bootstrap, and the README documents them as prose.
"""

import re

CHECK_ID = "agent-roster-match"
SEVERITY = "medium"

_ROW = re.compile(r"^\|\s*\[`(?P<name>[a-z0-9-]+)`\]\([^)]+\)\s*\|(?P<rest>.*)\|\s*$", re.MULTILINE)
_FM_MODEL = re.compile(r"(?m)^model:\s*(\S+)\s*$")


def run(ctx) -> None:
    agents_dir = ctx.repo / ".claude" / "agents"
    readme = agents_dir / "README.md"
    if not agents_dir.is_dir():
        return

    on_disk = {
        f.stem: f for f in sorted(agents_dir.glob("*.md"))
        if f.name != "README.md" and not f.stem.endswith("-architect")
    }

    if not readme.is_file():
        if on_disk:
            ctx.add(SEVERITY, CHECK_ID,
                    f".claude/agents/README.md missing — {len(on_disk)} operational agent(s) with no roster")
        return

    body = readme.read_text(encoding="utf-8")
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
                f".claude/agents/{name}.md has no row in the agent roster (.claude/agents/README.md) "
                "— an undocumented agent is one only its author will ever spawn")

    for name in sorted(set(listed) - set(on_disk)):
        ctx.add(SEVERITY, CHECK_ID,
                f"agent roster lists `{name}`, but .claude/agents/{name}.md does not exist")

    for name in sorted(set(listed) & set(on_disk)):
        declared = listed[name].strip("` ")
        head = on_disk[name].read_text(encoding="utf-8")[:2000]
        m = _FM_MODEL.search(head)
        if not m:
            ctx.add(SEVERITY, CHECK_ID,
                    f".claude/agents/{name}.md: no `model:` in frontmatter, roster says `{declared}`")
            continue
        actual = m.group(1).strip("`\"'")
        if declared and actual != declared:
            ctx.add(SEVERITY, CHECK_ID,
                    f".claude/agents/{name}.md runs `{actual}`, roster says `{declared}`")
