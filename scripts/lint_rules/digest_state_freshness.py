"""Lint rule: digest state file last-run freshness.

Flags `memory/digest_state.md` (or the configured equivalent) when the
`last_run_timestamp` field is older than the configured threshold.

Rationale: the digest is the operational tempo of Giovanni. A stale digest
state is an operational drift signal — the principal hasn't been running
the digest, which means drift catches are not happening, briefs are not
generating, shadow lookback is accumulating un-resolved hypotheses.

Severity is **low** by default. This is a soft operational signal, not a
structural problem with the framework — the principal may have legitimate
reasons to skip (PTO, deep focus week, fork in standby). Severity should
not block CI.

Activation:
- Rule activates only if the state file exists. Fresh fork (no state file
  yet) is a no-op.
- If state file exists but has the empty / template placeholder timestamp
  (`<YYYY-MM-DDTHH:MM:SSZ>`), report a one-time low finding pointing the
  principal at first-run seeding.

Config (env overrides):
- GIOVANNI_DIGEST_STATE_FILE          default "digest_state.md"
- GIOVANNI_DIGEST_FRESHNESS_HOURS     default 48 (warn threshold)
- GIOVANNI_DIGEST_FRESHNESS_HOURS_CRITICAL  default 168 (escalate to medium)

The thresholds map to:
- 48 h  — one missed daily digest; everyone misses occasionally
- 168 h — one full week; cadence is broken, principal needs prompt
"""

from __future__ import annotations

import datetime as dt
import os
import re

CHECK_ID = "digest-state-freshness"
SEVERITY_DEFAULT = "low"

# Match the timestamp line per memory/digest-state.template.md schema:
#   - timestamp: 2026-05-26T06:30:00Z
# Allow optional surrounding whitespace; YAML-ish but not full YAML parse.
_TIMESTAMP_RE = re.compile(
    r"^\s*-\s*timestamp\s*:\s*(\S+)\s*$",
    re.MULTILINE,
)

# Placeholder in the template — not a real timestamp.
_PLACEHOLDER_PATTERN = re.compile(r"<YYYY-MM-DDTHH:MM:SSZ>")


def _parse_iso(ts: str) -> dt.datetime | None:
    """Parse an ISO 8601 UTC timestamp ending in Z to a datetime.

    Returns None for malformed input. Standard library only — no PyYAML
    dependency.
    """
    # Python's datetime.fromisoformat rejects trailing Z in <3.11; normalize.
    candidate = ts.strip().strip("'\"")
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return None
    # Ensure UTC-aware (template enforces Z; reject naive timestamps).
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(dt.timezone.utc)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
        if value <= 0:
            return default
        return value
    except ValueError:
        return default


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    state_filename = os.environ.get("GIOVANNI_DIGEST_STATE_FILE", "digest_state.md")
    state_path = ctx.memory_dir() / state_filename

    if not state_path.is_file():
        # Fresh fork — no digest state to check. Silent.
        return

    try:
        text = state_path.read_text(encoding="utf-8")
    except OSError:
        return

    # Template placeholder = first-run seeding gap; flag once at low severity.
    if _PLACEHOLDER_PATTERN.search(text):
        ctx.add(
            "low",
            CHECK_ID,
            f"{rel(state_path, ctx.repo)}: contains template placeholder "
            "<YYYY-MM-DDTHH:MM:SSZ> — first digest hasn't run yet. Run "
            "`/digest` (or seed timestamp manually) to bootstrap state.",
        )
        return

    match = _TIMESTAMP_RE.search(text)
    if not match:
        ctx.add(
            "low",
            CHECK_ID,
            f"{rel(state_path, ctx.repo)}: no `- timestamp:` line found — "
            "state file structure may not match the template.",
        )
        return

    parsed = _parse_iso(match.group(1))
    if parsed is None:
        ctx.add(
            "low",
            CHECK_ID,
            f"{rel(state_path, ctx.repo)}: `- timestamp:` value "
            f"{match.group(1)!r} is not a parseable ISO 8601 UTC timestamp.",
        )
        return

    threshold_hours = _env_int("GIOVANNI_DIGEST_FRESHNESS_HOURS", 48)
    critical_hours = _env_int("GIOVANNI_DIGEST_FRESHNESS_HOURS_CRITICAL", 168)

    now = dt.datetime.now(dt.timezone.utc)
    age_seconds = (now - parsed).total_seconds()
    age_hours = age_seconds / 3600.0

    if age_hours < threshold_hours:
        return

    severity = "medium" if age_hours >= critical_hours else SEVERITY_DEFAULT
    age_display = f"{int(age_hours)}h" if age_hours < 96 else f"{int(age_hours / 24)}d"

    ctx.add(
        severity,
        CHECK_ID,
        f"{rel(state_path, ctx.repo)}: last digest run was {age_display} ago "
        f"(threshold {threshold_hours}h, critical {critical_hours}h). "
        "Operational tempo signal — drift may be accumulating un-caught. "
        "Run `/digest` or document the standby reason.",
    )
