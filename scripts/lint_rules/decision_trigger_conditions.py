"""Lint rule: decision records must have non-empty `Trigger conditions`.

A decision record without trigger conditions is decision theatre — there's
no way to know when to revisit. Empty / TBD / TODO placeholders are
treated as violations.

Two-track validation:
  1. Frontmatter `trigger_conditions:` field if present must be non-empty.
  2. Markdown `## Trigger conditions for re-evaluation` section if present
     must have non-whitespace content beyond comments.

If neither exists, the record is missing trigger conditions entirely
(critical — see memory/templates/decision-record.template.md).
"""

from __future__ import annotations

import re

CHECK_ID = "decision-trigger-conditions"

_SECTION_HEADER_RE = re.compile(
    r"^##\s+Trigger conditions(?:\s+for\s+re-?evaluation)?",
    re.IGNORECASE,
)
_PLACEHOLDER_RE = re.compile(r"<EMPTY|<TBD|<TODO|^\s*TBD\s*$|^\s*TODO\s*$", re.MULTILINE)
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _extract_section(text: str) -> str | None:
    """Extract content of '## Trigger conditions ...' section, or None if absent."""
    lines = text.splitlines()
    capturing = False
    out: list[str] = []
    for ln in lines:
        if _SECTION_HEADER_RE.match(ln):
            capturing = True
            continue
        if capturing and ln.startswith("## "):
            break
        if capturing:
            out.append(ln)
    if not capturing and not out:
        return None
    return "\n".join(out)


def run(ctx) -> None:
    from lint import parse_frontmatter, rel  # type: ignore[import-not-found]

    decisions_dir = ctx.memory_dir() / "decisions"
    if not decisions_dir.is_dir():
        return

    for rec in sorted(decisions_dir.glob("*.md")):
        if rec.name.startswith("_") or rec.name == "README.md":
            continue
        try:
            text = rec.read_text(encoding="utf-8")
        except OSError:
            continue

        fm = parse_frontmatter(rec)
        fm_trigger = (fm or {}).get("trigger_conditions")
        section = _extract_section(text)

        # Both absent → critical
        if fm_trigger in (None, "", []) and section is None:
            ctx.add(
                "critical",
                CHECK_ID,
                f"{rel(rec, ctx.repo)}: missing trigger conditions "
                "(neither frontmatter field nor '## Trigger conditions' section)",
            )
            continue

        # Frontmatter present but empty
        if fm_trigger is not None and fm_trigger in ("", [], None):
            ctx.add(
                "critical",
                CHECK_ID,
                f"{rel(rec, ctx.repo)}: frontmatter trigger_conditions is empty",
            )

        # Section present — verify non-empty after stripping comments
        if section is not None:
            stripped = _COMMENT_RE.sub("", section).strip()
            if not stripped or _PLACEHOLDER_RE.search(stripped):
                # If frontmatter has content, treat as warning only
                if fm_trigger:
                    ctx.add(
                        "medium",
                        CHECK_ID,
                        f"{rel(rec, ctx.repo)}: section '## Trigger conditions' is empty / "
                        "placeholder (frontmatter has content — promote section body)",
                    )
                else:
                    ctx.add(
                        "critical",
                        CHECK_ID,
                        f"{rel(rec, ctx.repo)}: section '## Trigger conditions' is empty / placeholder "
                        "and no frontmatter trigger_conditions",
                    )
