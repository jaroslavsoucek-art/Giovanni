"""Lint rule: the workflow route table and the files on disk agree, both ways.

An agentic repo grows runs by accretion: a command here, a workflow there, each
one added in the session that needed it. Nothing records the shape of the whole,
so nobody can answer the two questions that matter at 2am — *what can start
without me, and where does it stop?*

The route table answers both, in one table, with one row per run: trigger, file,
what it writes, where it stops, autonomy. This rule keeps it honest in both
directions:

  * every `.claude/workflows/*.md` and `.claude/commands/*.md` has a row
    (a run nobody listed is a run nobody governs)
  * every `.claude/…` path in the table exists
    (a row pointing at a deleted file is a promise the repo can't keep)

Target file: `CLAUDE.md` when it carries the table (a fork), otherwise
`CLAUDE.template.md` (the framework repo, checking its own template against its
own runs). Neither → one medium finding, not silence.
"""

import re

CHECK_ID = "workflow-route-table"
SEVERITY = "medium"

_TABLE_HEADING = re.compile(r"(?mi)^#{1,3}\s+.*workflows?\b.*$")
_PATH_RE = re.compile(r"`(\.claude/(?:workflows|commands)/[A-Za-z0-9._-]+\.md)`")
SKIP_FILENAMES = {"README.md"}


def _target(ctx):
    for name in ("CLAUDE.md", "CLAUDE.template.md"):
        path = ctx.repo / name
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _TABLE_HEADING.search(body)
        if m and "|" in body[m.end():]:
            return name, body[m.end():]
    return None, None


def run(ctx) -> None:
    on_disk = set()
    for sub in ("workflows", "commands"):
        d = ctx.repo / ".claude" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name in SKIP_FILENAMES:
                continue
            on_disk.add(f".claude/{sub}/{f.name}")

    name, section = _target(ctx)
    if section is None:
        if on_disk:
            ctx.add(SEVERITY, CHECK_ID,
                    "no workflow route table found in CLAUDE.md or CLAUDE.template.md — "
                    f"{len(on_disk)} run file(s) in .claude/ are ungoverned "
                    "(no recorded trigger, stop point, or autonomy level)")
        return

    # Stop at the next H2 so a later section's backticked path isn't read as a row.
    end = re.search(r"(?m)^##\s+", section)
    if end:
        section = section[:end.start()]

    listed = set(_PATH_RE.findall(section))

    for missing in sorted(on_disk - listed):
        ctx.add(SEVERITY, CHECK_ID,
                f"{missing} has no row in the {name} route table — "
                "add trigger / writes / stop point / autonomy, or delete the file")

    for ghost in sorted(listed - on_disk):
        ctx.add(SEVERITY, CHECK_ID,
                f"{name} route table points at {ghost}, which does not exist")
