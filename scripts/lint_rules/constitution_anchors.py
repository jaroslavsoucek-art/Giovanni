"""Lint rule: constitution sections must have anchor IDs.

Sections without anchor IDs cannot be cross-referenced from other constitution
sections or from decision records. The `{#anchor-id}` suffix convention is
required for every H2 / H3 in the constitution.

Disabled by setting `require_anchor_ids: false` in governance.config.yaml.
"""

import re

CHECK_ID = "constitution-anchors"

_HEADER_RE = re.compile(r"^(##+)\s+([^\n]+)$")
_ANCHOR_RE = re.compile(r"\{#[a-z0-9][a-z0-9-]*\}\s*$")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# Skip sections that are explicitly meta / structural
_SKIP_HEADERS = {
    "table of contents",
    "appendices",
    "document status legend",
    "superseded positions",
}


def run(ctx) -> None:
    if not ctx.config.get("require_anchor_ids", True):
        return
    from lint import rel  # type: ignore[import-not-found]

    const = ctx.constitution_path()
    if not const.is_file():
        return

    try:
        text = const.read_text(encoding="utf-8")
    except OSError:
        return

    # Mask HTML comment spans to blanks (preserving newlines for line-number
    # alignment) so example headers inside <!-- ... --> are not flagged — the
    # same treatment no_percentages / branch_out_no_recommendation apply.
    text = _HTML_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)

    # Skip H1 (document title); only check H2/H3
    in_code = False
    for lineno, ln in enumerate(text.splitlines(), start=1):
        if ln.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = _HEADER_RE.match(ln)
        if not m:
            continue
        hashes, title = m.group(1), m.group(2).strip()
        if len(hashes) < 2:  # H1 = document title
            continue
        # Strip trailing `(SUPERSEDED → §x)` decoration if present
        title_normalized = re.sub(r"\(SUPERSEDED.*?\)\s*$", "", title).strip().lower()
        if title_normalized in _SKIP_HEADERS:
            continue
        if not _ANCHOR_RE.search(title):
            ctx.add(
                "medium",
                CHECK_ID,
                f"{rel(const, ctx.repo)}:{lineno}: header '{title}' missing "
                "anchor ID `{#kebab-case}` — required for cross-references",
            )
