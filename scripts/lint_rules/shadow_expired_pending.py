"""Lint rule: shadow hypothesis lifecycle hygiene (pending + resolved).

Two checks under one CHECK_ID:

1. Pending past horizon — a shadow hypothesis in pending/ past its
   horizon_at without a verdict is operational drift: either /shadow-review
   cadence is slow, or the specificity_gate is too loose and the hypothesis
   was untestable from the start.

   Two thresholds:
   - Past horizon_at by ≤ 7 days: medium (overdue, but inside normal cadence
     variability)
   - Past horizon_at by > 7 days: high (cadence is broken, or specificity gate
     let through an untestable hypothesis)

2. Resolved without adversarial lookback — a file in resolved/ with an empty
   (or missing) `adversarial_check` field is a verdict recorded without the
   mandatory adversarial lookback ("what are the strongest arguments this
   hypothesis was NOT fulfilled?"). Generous verdicts without that
   counterweight corrupt calibration. Severity: medium.

   expired/ is exempt — expired files carry no verdict, so there is nothing
   to adversarially check.

Activation:
- Each check activates only if its directory (memory/shadow/pending/ or
  memory/shadow/resolved/) exists and contains hypothesis YAML files.
  Before any hypothesis is generated, the rule is a no-op (clean fork-time
  activity).
- Filenames matching .gitkeep, README.md, or starting with _ are skipped.
- Both checks use cheap regex parses (no PyYAML dependency) — they cover
  the standard schema in memory/templates/shadow-hypothesis.template.md.
"""

from __future__ import annotations

import datetime as dt
import re

CHECK_ID = "shadow-expired-pending"
SEVERITY_DEFAULT = "medium"
SEVERITY_HIGH_DAYS = 7

# horizon_at: YYYY-MM-DD pattern (with optional spaces/quotes)
_HORIZON_RE = re.compile(
    r"^\s*horizon_at\s*:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?\s*(?:#.*)?$",
    re.MULTILINE,
)

# adversarial_check: <inline value or block scalar indicator>
_ADV_LINE_RE = re.compile(r"^adversarial_check\s*:\s*(.*)$", re.MULTILINE)

_BLOCK_INDICATORS = {">", ">-", ">+", "|", "|-", "|+"}
_EMPTY_VALUES = {"", "null", "~", '""', "''"}


def _parse_horizon(text: str) -> dt.date | None:
    """Extract horizon_at date from YAML text without full YAML parse.

    Cheap regex parse; covers the standard schema. Returns None if not present
    or malformed.
    """
    m = _HORIZON_RE.search(text)
    if not m:
        return None
    try:
        return dt.date.fromisoformat(m.group(1))
    except ValueError:
        return None


def _adversarial_check_filled(text: str) -> bool:
    """Return True if the adversarial_check field has non-empty content.

    Handles inline scalars (`adversarial_check: verdict stands ...`) and
    block scalars (`adversarial_check: >-` followed by indented lines).
    Cheap regex parse, consistent with _parse_horizon — no PyYAML needed.
    """
    m = _ADV_LINE_RE.search(text)
    if not m:
        return False
    inline = re.sub(r"#.*$", "", m.group(1)).strip()
    if inline not in _BLOCK_INDICATORS and inline not in _EMPTY_VALUES:
        return True  # inline scalar with content
    # Block scalar (or bare key) — look for indented continuation content.
    for ln in text[m.end():].splitlines():
        if not ln.strip():
            continue
        if ln[0] in (" ", "\t"):
            return True
        break  # next top-level key — field ended without content
    return False


def _shadow_files(directory, recursive=False):
    glob = directory.rglob if recursive else directory.glob
    return sorted(
        p for p in glob("*.yaml")
        if not p.name.startswith("_") and p.name != ".gitkeep"
    )


def _check_pending(ctx, rel) -> None:
    pending_dir = ctx.memory_dir() / "shadow" / "pending"
    if not pending_dir.is_dir():
        return

    candidates = _shadow_files(pending_dir)
    if not candidates:
        return

    today = dt.date.today()

    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue

        horizon = _parse_horizon(text)
        if horizon is None:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: pending shadow hypothesis has no "
                "parseable horizon_at field — schema check needed",
            )
            continue

        if horizon >= today:
            continue  # not yet at horizon, no finding

        days_overdue = (today - horizon).days
        if days_overdue > SEVERITY_HIGH_DAYS:
            severity = "high"
            comment = (
                f"past horizon by {days_overdue} days — /shadow-review cadence "
                "broken, or specificity_gate too loose"
            )
        else:
            severity = SEVERITY_DEFAULT
            comment = (
                f"past horizon by {days_overdue} days — schedule /shadow-review "
                "to resolve"
            )

        ctx.add(
            severity,
            CHECK_ID,
            f"{rel(path, ctx.repo)}: {comment} (horizon_at={horizon.isoformat()})",
        )


def _check_resolved_adversarial(ctx, rel) -> None:
    # resolved/ uses monthly subdirectories (resolved/<YYYY-MM>/) — recurse.
    # expired/ is exempt: no verdict was recorded, nothing to adversarially
    # check.
    resolved_dir = ctx.memory_dir() / "shadow" / "resolved"
    if not resolved_dir.is_dir():
        return

    for path in _shadow_files(resolved_dir, recursive=True):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not _adversarial_check_filled(text):
            ctx.add(
                "medium",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: resolved shadow hypothesis has empty "
                "adversarial_check — the adversarial lookback is mandatory "
                "before a verdict counts (expired/ files are exempt)",
            )


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    _check_pending(ctx, rel)
    _check_resolved_adversarial(ctx, rel)
