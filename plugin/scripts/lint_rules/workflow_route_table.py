"""Lint rule: the workflow route table and the runs that exist agree, both ways.

An agentic repo grows runs by accretion: a command here, a workflow there, each
one added in the session that needed it. Nothing records the shape of the whole,
so nobody can answer the two questions that matter at 2am — *what can start
without me, and where does it stop?*

The route table answers both, in one table, with one row per run: trigger, file,
what it writes, where it stops, autonomy. This rule keeps it honest in both
directions, on two surfaces:

  * the plugin's skills against the plugin's own template
    (`<plugin>/templates/CLAUDE.template.md`): every `skills/<name>/SKILL.md`
    has a `/giovanni:<name>` row, and every `/giovanni:<x>` in the table is a
    skill that exists. This is the framework checking itself; a fork may trim
    rows from its own CLAUDE.md, the template may not.
  * the project's own runs against the project's `CLAUDE.md`: every
    `.claude/workflows/*.md` and `.claude/commands/*.md` has a row, every
    `.claude/…` path in the table exists, and every `/giovanni:<x>` the table
    names is a skill the plugin ships (a row pointing at a skill that was
    renamed is a promise the repo can't keep).

A project with run files but no route table gets one medium finding, not
silence. When the project is the framework repo itself (its CLAUDE.md is the
meta-builder contract, no table), the template stands in for it.
"""

import re

CHECK_ID = "workflow-route-table"
SEVERITY = "medium"

_TABLE_HEADING = re.compile(r"(?mi)^#{1,3}\s+.*workflows?\b.*$")
_PATH_RE = re.compile(r"`(\.claude/(?:workflows|commands)/[A-Za-z0-9._-]+\.md)`")
_SKILL_RE = re.compile(r"`/giovanni:([a-z0-9-]+)")
SKIP_FILENAMES = {"README.md"}


def _table_section(path):
    if not path.is_file():
        return None
    try:
        body = path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _TABLE_HEADING.search(body)
    if not (m and "|" in body[m.end():]):
        return None
    section = body[m.end():]
    # Stop at the next H2 so a later section's backticked path isn't read as a row.
    end = re.search(r"(?m)^##\s+", section)
    return section[:end.start()] if end else section


def _plugin_skills(plugin) -> set[str]:
    skills_dir = plugin / "skills"
    if not skills_dir.is_dir():
        return set()
    return {d.name for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}


def run(ctx) -> None:
    plugin = getattr(ctx, "plugin", None)
    skills = _plugin_skills(plugin) if plugin is not None else set()

    # --- plugin surface: skills ↔ the shipped template -------------------------
    if plugin is not None and skills:
        template = plugin / "templates" / "CLAUDE.template.md"
        section = _table_section(template)
        if section is None:
            ctx.add(SEVERITY, CHECK_ID,
                    f"plugin: no workflow route table in templates/CLAUDE.template.md — "
                    f"{len(skills)} skill(s) are ungoverned")
        else:
            listed = set(_SKILL_RE.findall(section))
            for missing in sorted(skills - listed):
                ctx.add(SEVERITY, CHECK_ID,
                        f"plugin: skills/{missing}/SKILL.md has no `/giovanni:{missing}` row in "
                        "templates/CLAUDE.template.md — add trigger / writes / stop point / autonomy, "
                        "or delete the skill")
            for ghost in sorted(listed - skills):
                ctx.add(SEVERITY, CHECK_ID,
                        f"plugin: templates/CLAUDE.template.md route table names `/giovanni:{ghost}`, "
                        "which is not a skill the plugin ships")

    # --- project surface: its own runs ↔ its CLAUDE.md -------------------------
    on_disk = set()
    for sub in ("workflows", "commands"):
        d = ctx.repo / ".claude" / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.name in SKIP_FILENAMES:
                continue
            on_disk.add(f".claude/{sub}/{f.name}")

    name = "CLAUDE.md"
    section = _table_section(ctx.repo / "CLAUDE.md")
    if section is None and plugin is not None and ctx.repo == plugin.parent:
        # The framework repo: its CLAUDE.md is the meta-builder contract. The
        # template is the table it ships, and it was checked above.
        return
    if section is None:
        if on_disk:
            ctx.add(SEVERITY, CHECK_ID,
                    "no workflow route table found in CLAUDE.md — "
                    f"{len(on_disk)} run file(s) in .claude/ are ungoverned "
                    "(no recorded trigger, stop point, or autonomy level)")
        return

    listed = set(_PATH_RE.findall(section))
    for missing in sorted(on_disk - listed):
        ctx.add(SEVERITY, CHECK_ID,
                f"{missing} has no row in the {name} route table — "
                "add trigger / writes / stop point / autonomy, or delete the file")
    for ghost in sorted(listed - on_disk):
        ctx.add(SEVERITY, CHECK_ID,
                f"{name} route table points at {ghost}, which does not exist")
    if skills:
        for ghost in sorted(set(_SKILL_RE.findall(section)) - skills):
            ctx.add(SEVERITY, CHECK_ID,
                    f"{name} route table names `/giovanni:{ghost}`, which is not a skill the plugin ships")
