"""Lint rule: branch-out artifacts must not contain recommendations.

Branch-out output is generative (surfaces consequence space), not prescriptive
(recommends a move). Recommendation creep is a binding-rule violation —
the trade-off matrix is the agent's contribution; the principal weighs.

Patterns flagged:
- "we recommend", "agent recommends", "I recommend"
- "best move is", "the best path", "best choice"
- "should do X", "you should X" (when not in a watch-points / monitoring context)
- "Recommended" as a table column header (matrix structure violation)
- "Recommendation:" as a section header
- "Agent suggests" / "agent's suggestion"

Allowed exceptions:
- `memory/branch-out/canonical-moves.md` — registry / documentation
- `memory/branch-out/README.md` — documentation explaining the rule
- File body inside HTML comment blocks (templates document the rule)

Severity: medium — recommendation creep is a discipline drift signal.
Critical at the structural level (Recommended column header), medium at
the prose level.
"""

from __future__ import annotations

import re

CHECK_ID = "branch-out-no-recommendation"

# Patterns scanned in branch-out artifact prose
_PROSE_PATTERNS = [
    (
        re.compile(r"\b(we|I|agent|the agent)\s+recommend(s|ed)?\b", re.IGNORECASE),
        "recommendation prose ('recommend')",
    ),
    (
        re.compile(r"\bagent('s)?\s+(suggestion|suggests|recommendation|recommends)\b", re.IGNORECASE),
        "agent recommendation prose",
    ),
    (
        re.compile(r"\bbest\s+(move|path|choice|option|action)\b", re.IGNORECASE),
        "ranking prose ('best move/path/choice')",
    ),
    (
        re.compile(r"\b(you|principal)\s+should\b", re.IGNORECASE),
        "prescriptive prose ('should')",
    ),
    (
        re.compile(r"^##+\s+Recommendation", re.IGNORECASE | re.MULTILINE),
        "section header 'Recommendation' (structural violation)",
    ),
    (
        re.compile(r"\|\s*Recommended\s*\|", re.IGNORECASE),
        "table column header 'Recommended' (structural violation)",
    ),
]

# HTML comment regex — used to strip template explanation blocks
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _strip_comments(text: str) -> str:
    """Remove HTML comment blocks from text, preserving line numbering.

    Replaces comment text with same-line-count blank lines so downstream
    line numbers stay accurate.
    """
    def _replace(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")

    return _HTML_COMMENT_RE.sub(_replace, text)


def _is_structural(label: str) -> bool:
    """Return True if this is a structural-level violation (critical-adjacent)."""
    return "structural violation" in label


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    bo_dir = ctx.memory_dir() / "branch-out"
    if not bo_dir.is_dir():
        return

    for path in sorted(bo_dir.rglob("*.md")):
        if path.name in ("README.md", "canonical-moves.md"):
            continue
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue

        # Strip HTML comments first (the "No recommended move" explanatory
        # block contains discussion of the rule itself)
        scanned_text = _strip_comments(text)

        # "No recommended move" callout is the SPEC; we should not catch it.
        # The callout uses the literal phrase "does not recommend" / "no
        # recommended move" — we explicitly exclude lines containing the
        # SPEC phrase from triggering the rule.
        spec_phrases = (
            "does not recommend",
            "no recommended move",
            "no recommendation",
            "intentionally does not recommend",
            "no recommended",
        )

        for lineno, ln in enumerate(scanned_text.splitlines(), start=1):
            lower = ln.lower()
            if any(p in lower for p in spec_phrases):
                continue
            # Skip line that says "No recommended move" header itself
            if "no recommended move" in lower:
                continue

            for pattern, label in _PROSE_PATTERNS:
                if pattern.search(ln):
                    severity = "critical" if _is_structural(label) else "medium"
                    ctx.add(
                        severity,
                        CHECK_ID,
                        f"{rel(path, ctx.repo)}:{lineno}: branch-out artifact "
                        f"contains {label} — trade-off matrix is generative, "
                        f"not prescriptive (line: {ln.strip()[:80]!r})",
                    )
                    break  # one finding per line is enough
