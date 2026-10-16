"""Lint rule: the slash-command registry stays in sync with the files that exist.

Two surfaces:

  * the plugin: every `<plugin>/skills/<name>/SKILL.md` has a row in
    `<plugin>/skills/README.md`, and every row points at a skill directory
    that exists
  * the project: every `<repo>/.claude/commands/*.md` (excluding README.md
    and stub `.template.md` files) is listed in `.claude/commands/README.md`,
    and vice versa — a fork's own commands

Catches presentation drift: command added but not registered, command removed
but row remains, command renamed but the row still points at the old name.

Activation policy: a surface is checked only when its README exists. A fork
that has not opened its own command surface (no `.claude/commands/README.md`)
is a no-op on that half. Severity low: registry drift is a maintenance signal,
not a correctness violation — the commands still work.

A registry row is a Markdown link whose text is the command (`/digest`,
`/giovanni:digest`, backticks optional) and whose target is the file:
`[`/giovanni:digest`](digest/SKILL.md)`. Only the target is compared.

What this rule does NOT check: whether a row's one-liner matches the file's
`description:` (semantic drift), whether the argument column matches the file's
own table, or whether the agent / procedure the command routes to exists.
"""

from __future__ import annotations

import re

CHECK_ID = "slash-command-registry"

# [/foo](foo.md), [`/foo`](foo.md), [`/giovanni:foo`](foo/SKILL.md)
_REGISTRY_LINK_RE = re.compile(r"\[`?/[\w:-]+`?\]\(([\w./-]+\.md)\)")


def _registered(readme_path) -> set[str]:
    referenced: set[str] = set()
    try:
        text = readme_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return referenced
    for line in text.splitlines():
        for m in _REGISTRY_LINK_RE.finditer(line):
            referenced.add(m.group(1))
    return referenced


def _check_skills(ctx, skills_dir) -> None:
    from lint import rel  # type: ignore[import-not-found]

    readme = skills_dir / "README.md"
    if not readme.is_file():
        return
    actual = {
        f"{d.name}/SKILL.md"
        for d in skills_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    }
    registered = {r for r in _registered(readme) if r.endswith("/SKILL.md")}
    for ref in sorted(actual - registered):
        ctx.add("low", CHECK_ID,
                f"{rel(skills_dir / ref, ctx.repo)}: skill present but not listed in the "
                f"registry table ({rel(readme, ctx.repo)})")
    for ref in sorted(registered - actual):
        ctx.add("low", CHECK_ID,
                f"{rel(readme, ctx.repo)}: registry table references '{ref}' but no such skill exists")


def _check_commands(ctx, commands_dir) -> None:
    from lint import rel  # type: ignore[import-not-found]

    readme = commands_dir / "README.md"
    if not readme.is_file():
        return
    actual = {
        p.name for p in commands_dir.glob("*.md")
        if p.name.lower() != "readme.md" and not p.name.endswith(".template.md")
    }
    registered = {r.rsplit("/", 1)[-1] for r in _registered(readme) if not r.endswith("/SKILL.md")}
    for fname in sorted(actual - registered):
        ctx.add("low", CHECK_ID,
                f"{rel(commands_dir / fname, ctx.repo)}: command file present but "
                f"not listed in {rel(readme, ctx.repo)} registry table")
    for fname in sorted(registered - actual):
        ctx.add("low", CHECK_ID,
                f"{rel(readme, ctx.repo)}: registry table references '{fname}' but no such file exists")


def run(ctx) -> None:
    plugin = getattr(ctx, "plugin", None)
    if plugin is not None and (plugin / "skills").is_dir():
        _check_skills(ctx, plugin / "skills")
    _check_commands(ctx, ctx.repo / ".claude" / "commands")
