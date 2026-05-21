"""Lint rule: shadow hypotheses in pending/ must not be past horizon_at.

A shadow hypothesis past its horizon_at without a verdict is operational
drift — either /shadow-review cadence is slow, or the specificity_gate is
too loose and the hypothesis was untestable from the start.

Two thresholds:
- Past horizon_at by ≤ 7 days: medium (overdue, but inside normal cadence
  variability)
- Past horizon_at by > 7 days: high (cadence is broken, or specificity gate
  let through an untestable hypothesis)

Activation:
- Rule activates only if memory/shadow/pending/ exists AND contains
  hypothesis YAML files. Before any hypothesis is generated, the rule is
  a no-op (clean fork-time activity).
- Filenames matching .gitkeep, README.md, or starting with _ are skipped.
- Requires PyYAML to parse horizon_at — if PyYAML missing, rule reports a
  low-severity finding and exits.
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


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    pending_dir = ctx.memory_dir() / "shadow" / "pending"
    if not pending_dir.is_dir():
        return

    candidates = [
        p for p in pending_dir.glob("*.yaml")
        if not p.name.startswith("_") and p.name != ".gitkeep"
    ]
    if not candidates:
        return

    today = dt.date.today()

    for path in sorted(candidates):
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
