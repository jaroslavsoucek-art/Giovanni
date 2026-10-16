"""Lint rule: every rule pointer in CLAUDE.md resolves to a register entry.

CLAUDE.md keeps each rule to one line plus a pointer into
`docs/invariants.md` § Behavioral rules, where the reason and the incident
live (see the `rules-register` entry there). That split only works while the
pointers resolve. A rule whose pointer dangles has quietly lost its reason, and
a rule without its reason is the one that gets relaxed first.

Checks `CLAUDE.md` and `CLAUDE.template.md` at the repo root for
`docs/invariants.md#<id>` and requires a heading in `docs/invariants.md` that
renders to that anchor: "### `<id>`" (an entry) or an explicit `{#<id>}`.
"""

import re

CHECK_ID = "rules-register-pointers"
SEVERITY = "medium"

POINTER_RE = re.compile(r"docs/invariants\.md#([a-z0-9][a-z0-9-]*)")
ENTRY_RE = re.compile(r"^#{2,4}\s+`([a-z0-9][a-z0-9-]*)`\s*$", re.M)
EXPLICIT_RE = re.compile(r"\{#([a-z0-9][a-z0-9-]*)\}")


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    sources = [p for p in (ctx.repo / "CLAUDE.md", ctx.repo / "CLAUDE.template.md") if p.is_file()]
    pointers = []
    for src in sources:
        for n, line in enumerate(src.read_text(encoding="utf-8").splitlines(), 1):
            for m in POINTER_RE.finditer(line):
                pointers.append((src, n, m.group(1)))
    if not pointers:
        return

    register = ctx.repo / "docs" / "invariants.md"
    if not register.is_file():
        ctx.add(SEVERITY, CHECK_ID,
                f"{len(pointers)} rule pointer(s) into docs/invariants.md, but the file does not exist")
        return
    text = register.read_text(encoding="utf-8")
    anchors = set(ENTRY_RE.findall(text)) | set(EXPLICIT_RE.findall(text))

    for src, n, anchor in pointers:
        if anchor not in anchors:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{rel(src, ctx.repo)}:{n}: pointer `docs/invariants.md#{anchor}` has no entry — "
                    f"add \"### `{anchor}`\" under § Behavioral rules, or fix the pointer")
