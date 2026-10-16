"""Lint rule: slash-command registry must stay in sync with actual command files.

Every file in `.claude/commands/*.md` (excluding README.md and stub
`.template.md` files) must be listed in the registry table inside
`.claude/commands/README.md`. Conversely, every entry in the registry
table must correspond to a file. Catches presentation drift:

- Command added but not registered (forgot to update the table)
- Command removed but row remains (stale row)
- Command renamed but registry row still points at old name

Activation policy:
- Rule activates only if `.claude/commands/README.md` exists. Forks that
  haven't initialized the slash command surface yet (no README) are a
  no-op.
- Severity: low. Registry drift is a maintenance signal, not a
  correctness violation — commands still work even if the registry is
  stale.

The registry table is detected by the row format `| [/<command>](<file>.md) |`
inside the README's `## Command registry` section (or anywhere a row
matching this shape appears). The first column's path between
`[](` and `)` is the command file reference. Either backtick-wrapped
or plain Markdown link is accepted.

What this rule does NOT check:
- Whether the command file's frontmatter `description:` matches the
  registry's "One-liner" column (semantic drift — that's a different
  problem, would need NLP-style matching)
- Whether the argument syntax column matches the command file's
  argument-syntax table
- Whether the agent / workflow the command routes to actually exists
  (covered indirectly by the command's own pre-flight checks at
  runtime — lint doesn't validate runtime behavior)
"""

from __future__ import annotations

import re

CHECK_ID = "slash-command-registry"

# Match a Markdown link of the form [/foo](foo.md) or [`/foo`](foo.md)
# anywhere in a line. Captures the path inside (). Restricts the link
# text to start with `/` (optionally backtick-wrapped) so we don't match
# arbitrary repo links — the registry rows always have the slash prefix
# on the command name.
_REGISTRY_LINK_RE = re.compile(r"\[`?/[\w-]+`?\]\(([\w./-]+\.md)\)")


def _collect_command_files(commands_dir):
    """Return set of filenames in .claude/commands/*.md, excluding README and stubs."""
    files = set()
    if not commands_dir.is_dir():
        return files
    for path in commands_dir.glob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        # Skip stub `.template.md` files (prediction-architect intermediate
        # artifacts that should be finalized into runtime commands by the
        # slash-command-architect; if a fork still has them, that's a
        # separate cleanup issue not this rule's concern).
        if path.name.endswith(".template.md"):
            continue
        files.add(path.name)
    return files


def _collect_registered_files(readme_path):
    """Parse the registry README, return set of referenced command filenames."""
    referenced = set()
    try:
        text = readme_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return referenced
    for line in text.splitlines():
        for m in _REGISTRY_LINK_RE.finditer(line):
            ref = m.group(1)
            # Normalize to filename only (drop any leading path components).
            # Registry uses relative links like "branch-out.md" — already a
            # filename — but defensive normalization is cheap.
            referenced.add(ref.rsplit("/", 1)[-1])
    return referenced


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    commands_dir = ctx.repo / ".claude" / "commands"
    readme_path = commands_dir / "README.md"

    # Activation policy: if README doesn't exist, the fork hasn't
    # initialized the slash command surface. No-op.
    if not readme_path.is_file():
        return

    actual = _collect_command_files(commands_dir)
    registered = _collect_registered_files(readme_path)

    # Files present but not registered (command added without README update)
    unregistered = sorted(actual - registered)
    for fname in unregistered:
        ctx.add(
            "low",
            CHECK_ID,
            f"{rel(commands_dir / fname, ctx.repo)}: command file present but "
            f"not listed in .claude/commands/README.md registry table",
        )

    # Files registered but not present (stale row pointing at deleted command)
    missing = sorted(registered - actual)
    for fname in missing:
        ctx.add(
            "low",
            CHECK_ID,
            f"{rel(readme_path, ctx.repo)}: registry table references "
            f"'{fname}' but no such file exists in .claude/commands/",
        )
