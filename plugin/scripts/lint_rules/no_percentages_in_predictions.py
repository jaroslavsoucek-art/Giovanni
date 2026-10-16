"""Lint rule: no percentages in predictive artifacts.

The predictive layer is bound by a three-tier framing rule:
`likely` / `possible-but-surprising` / `unlikely-but-impactful`. Numeric
probabilities create false precision and are unfalsifiable in small-N
stakeholder predictions.

This rule scans the following artifacts for percentage patterns:
- `memory/branch-out/*.md` (branch-out simulations — strict)
- `memory/shadow/**/*.yaml` (shadow hypotheses — strict)
- `memory/stakeholders/*.md` "Predicted reactions" section (strict)

Allowed exceptions (NOT flagged):
- `memory/calibration/**` — calibration reports legitimately quote accuracy
  rates as percentages (matched / resolved). These are MEASUREMENTS, not
  predictions.
- `memory/branch-out/canonical-moves.md` — registry / documentation, not
  prediction.
- `memory/branch-out/README.md` — documentation
- `docs/prediction.md` — documentation (legitimately quotes healthy ranges)
- File body inside an HTML comment block (templates illustrate the rule
  by example).

Severity: high — binding rule violation.
"""

from __future__ import annotations

import re

CHECK_ID = "no-percentages-in-predictions"
SEVERITY = "high"

# Match: digit(s), optional decimal, then % — but not other typographic %
# Patterns matched:
#   70%        ← classic
#   70.5%      ← decimal
#   ~85%       ← approximate
#   80–90%     ← range (also catches single ends)
#   60-80%     ← range
# Not matched (deliberately):
#   100% pure  ← intent could be idiomatic; require '%' is digit-prefixed
#   %COMPLETE  ← non-numeric percent reference
_PERCENT_RE = re.compile(r"(?<![A-Za-z_])(~)?\s*\d+(?:\.\d+)?\s*%")

# HTML comment regex — used to strip template explanation blocks where the
# rule itself is documented.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)

# Frontmatter regex — first --- ... --- block in markdown
_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)

# Predicted reactions section in stakeholder profiles
_PREDICTED_REACTIONS_HEADER_RE = re.compile(
    r"^##\s+Predicted reactions\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _strip_safe_regions(text: str) -> str:
    """Strip HTML comments and frontmatter (rule is about prose, not metadata).

    Frontmatter percentages would be unusual but not the failure mode this
    rule targets. HTML comments often document the rule itself.
    """
    text = _HTML_COMMENT_RE.sub("", text)
    text = _FRONTMATTER_RE.sub("", text)
    return text


def _has_percentage(text: str) -> list[tuple[int, str]]:
    """Return list of (line_number, line_content) hits for percentage patterns."""
    hits = []
    stripped = _strip_safe_regions(text)
    # Re-align line numbers with original by walking original lines
    # Approximation: report on stripped text indices remapped to original.
    # Simpler: scan original line-by-line, but skip lines inside HTML comments.
    in_comment = False
    in_frontmatter = False
    frontmatter_seen = False
    for lineno, ln in enumerate(text.splitlines(), start=1):
        # Frontmatter handling: first occurrence of standalone --- toggles state
        if ln.strip() == "---":
            if not frontmatter_seen:
                in_frontmatter = True
                frontmatter_seen = True
                continue
            elif in_frontmatter:
                in_frontmatter = False
                continue
        if in_frontmatter:
            continue
        # HTML comment handling
        if "<!--" in ln and "-->" not in ln:
            in_comment = True
            continue
        if in_comment:
            if "-->" in ln:
                in_comment = False
            continue
        # Now scan this line
        if _PERCENT_RE.search(ln):
            hits.append((lineno, ln.strip()))
    return hits


def _extract_predicted_reactions_section(text: str) -> tuple[int, str] | None:
    """Return (start_lineno, body) of the 'Predicted reactions' section, or None.

    body excludes the header line. Section ends at next '## ' header.
    """
    lines = text.splitlines()
    capturing = False
    start_lineno = 0
    out: list[str] = []
    for lineno, ln in enumerate(lines, start=1):
        if _PREDICTED_REACTIONS_HEADER_RE.match(ln):
            capturing = True
            start_lineno = lineno
            continue
        if capturing and ln.startswith("## "):
            break
        if capturing:
            out.append(ln)
    if not capturing:
        return None
    return start_lineno, "\n".join(out)


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    memory_dir = ctx.memory_dir()
    if not memory_dir.is_dir():
        return

    # Strict scan: branch-out simulations (skip README + canonical-moves)
    bo_dir = memory_dir / "branch-out"
    if bo_dir.is_dir():
        for path in sorted(bo_dir.rglob("*.md")):
            if path.name in ("README.md", "canonical-moves.md"):
                continue
            if path.name.startswith("_"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            hits = _has_percentage(text)
            for lineno, content in hits:
                ctx.add(
                    SEVERITY,
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}:{lineno}: branch-out artifact "
                    f"contains percentage — three-tier framing required "
                    f"(line: {content[:80]!r})",
                )

    # Strict scan: shadow hypotheses
    shadow_dir = memory_dir / "shadow"
    if shadow_dir.is_dir():
        for path in sorted(shadow_dir.rglob("*.yaml")):
            if path.name.startswith("_") or path.name == ".gitkeep":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            for lineno, ln in enumerate(text.splitlines(), start=1):
                if ln.strip().startswith("#"):
                    continue
                if _PERCENT_RE.search(ln):
                    ctx.add(
                        SEVERITY,
                        CHECK_ID,
                        f"{rel(path, ctx.repo)}:{lineno}: shadow hypothesis "
                        f"contains percentage — three-tier framing required "
                        f"(line: {ln.strip()[:80]!r})",
                    )

    # Strict scan: stakeholder profiles "Predicted reactions" section only
    stakeholders_dir = memory_dir / "stakeholders"
    if stakeholders_dir.is_dir():
        for path in sorted(stakeholders_dir.rglob("*.md")):
            if path.name.startswith("_") or path.name.lower() == "readme.md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            section = _extract_predicted_reactions_section(text)
            if section is None:
                continue
            start_lineno, body = section
            # Strip HTML comments from the section before scanning
            body_no_comments = _HTML_COMMENT_RE.sub("", body)
            # Walk body lines and recompute line numbers relative to file
            for offset, ln in enumerate(body_no_comments.splitlines(), start=0):
                if _PERCENT_RE.search(ln):
                    ctx.add(
                        SEVERITY,
                        CHECK_ID,
                        f"{rel(path, ctx.repo)}:{start_lineno + offset + 1}: "
                        f"stakeholder 'Predicted reactions' section contains "
                        f"percentage — three-tier framing required "
                        f"(line: {ln.strip()[:80]!r})",
                    )
