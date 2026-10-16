"""Lint rule: every rule pointer in CLAUDE.md resolves to a register entry.

CLAUDE.md keeps each rule to one line plus a pointer into
`docs/invariants.md` § Behavioral rules, where the reason and the incident
live (see the `rules-register` entry there). That split only works while the
pointers resolve. A rule whose pointer dangles has quietly lost its reason, and
a rule without its reason is the one that gets relaxed first.

Two sources, each resolved against the register nearest to it:

  * the project's `CLAUDE.md` against the project's `docs/invariants.md` when it
    keeps one, otherwise against the plugin's — the mechanism docs ship with the
    plugin, and a fork's CLAUDE.md points at them by the short name
  * the plugin's `templates/CLAUDE.template.md` against the plugin's
    `docs/invariants.md`

A pointer is `docs/invariants.md#<id>`; it resolves when the register has a
heading that renders to that anchor: "### `<id>`" (an entry) or an explicit
`{#<id>}`.
"""

import re

CHECK_ID = "rules-register-pointers"
SEVERITY = "medium"

POINTER_RE = re.compile(r"docs/invariants\.md#([a-z0-9][a-z0-9-]*)")
ENTRY_RE = re.compile(r"^#{2,4}\s+`([a-z0-9][a-z0-9-]*)`\s*$", re.M)
EXPLICIT_RE = re.compile(r"\{#([a-z0-9][a-z0-9-]*)\}")


def _pointers(src):
    out = []
    for n, line in enumerate(src.read_text(encoding="utf-8").splitlines(), 1):
        for m in POINTER_RE.finditer(line):
            out.append((n, m.group(1)))
    return out


def _anchors(register):
    text = register.read_text(encoding="utf-8")
    return set(ENTRY_RE.findall(text)) | set(EXPLICIT_RE.findall(text))


def _check(ctx, src, register, shown_src: str) -> None:
    if not src.is_file():
        return
    pointers = _pointers(src)
    if not pointers:
        return
    if register is None or not register.is_file():
        ctx.add(SEVERITY, CHECK_ID,
                f"{shown_src}: {len(pointers)} rule pointer(s) into docs/invariants.md, "
                "but no register exists (neither the project's nor the plugin's)")
        return
    anchors = _anchors(register)
    for n, anchor in pointers:
        if anchor not in anchors:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{shown_src}:{n}: pointer `docs/invariants.md#{anchor}` has no entry in "
                    f"{register.name} — add \"### `{anchor}`\" under § Behavioral rules, or fix the pointer")


def run(ctx) -> None:
    plugin = getattr(ctx, "plugin", None)
    plugin_register = (plugin / "docs" / "invariants.md") if plugin is not None else None

    project_register = ctx.repo / "docs" / "invariants.md"
    if not project_register.is_file():
        project_register = plugin_register
    _check(ctx, ctx.repo / "CLAUDE.md", project_register, "CLAUDE.md")

    # Legacy fork layout kept a CLAUDE.template.md at the project root.
    _check(ctx, ctx.repo / "CLAUDE.template.md", project_register, "CLAUDE.template.md")

    if plugin is not None:
        _check(ctx, plugin / "templates" / "CLAUDE.template.md", plugin_register,
               "plugin templates/CLAUDE.template.md")
