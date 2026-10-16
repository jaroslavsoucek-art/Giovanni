"""Lint rule: adversarial-review records must use the SHIP/REWRITE/KILL enum.

Forks that persist adversarial-review records under memory/intel/adversarial/
must use the fixed three-tier verdict. Compound verdicts ("MOSTLY SHIP",
"STRONG REWRITE", "SOFT KILL") are softening creep and violate the binding
policy documented in docs/adversarial.md.

This rule is OPTIONAL — many forks don't persist adversarial reviews
(the verdict is delivered in-conversation and the user acts on it). If
memory/intel/adversarial/ doesn't exist, the rule is a no-op.

When the directory exists, every *.md file (excluding README.md and files
starting with _) is checked for:
  - YAML frontmatter present
  - verdict field present + matches SHIP | REWRITE | KILL exactly (case-insensitive
    on input; normalized to uppercase in finding messages)
  - issue_count present + integer >= 1 (a review with zero issues is a
    discipline-drift signal per workflow doc)
  - severity counts (fatal_count, major_count, minor_count) if present
    must be non-negative integers

Severity: low — adversarial reviews may not be logged systematically; the
rule is advisory unless the fork has opted into persistent logging.
"""

from __future__ import annotations

CHECK_ID = "adversarial-verdict-format"

ALLOWED_VERDICTS = {"SHIP", "REWRITE", "KILL"}
REQUIRED_FIELDS = ["verdict", "issue_count"]
OPTIONAL_INT_FIELDS = ["fatal_count", "major_count", "minor_count"]


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    adv_dir = ctx.memory_dir() / "intel" / "adversarial"
    if not adv_dir.is_dir():
        # No persistent log — rule is a no-op for this fork.
        return

    if not HAVE_YAML:
        ctx.add(
            "low",
            CHECK_ID,
            "PyYAML not installed — adversarial-review frontmatter checks skipped",
        )
        return

    for path in sorted(adv_dir.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md":
            continue

        fm = parse_frontmatter(path)
        if fm is None:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: missing or invalid YAML frontmatter "
                f"(expected verdict + issue_count fields)",
            )
            continue

        # Required: verdict
        verdict = fm.get("verdict")
        if verdict is None or verdict == "":
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: missing/empty 'verdict' field "
                f"(must be SHIP, REWRITE, or KILL)",
            )
        else:
            verdict_upper = str(verdict).strip().upper()
            if verdict_upper not in ALLOWED_VERDICTS:
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}: verdict='{verdict}' not in "
                    f"{sorted(ALLOWED_VERDICTS)} — compound verdicts "
                    f"('MOSTLY SHIP', 'STRONG REWRITE', etc.) violate the "
                    f"three-tier enum",
                )

        # Required: issue_count >= 1
        ic = fm.get("issue_count")
        if ic is None:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: missing 'issue_count' field "
                f"(zero-issue reviews are a discipline-drift signal — see "
                f"docs/adversarial.md §7)",
            )
        elif not isinstance(ic, int) or ic < 1:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: issue_count={ic!r} invalid — must be "
                f"integer >= 1",
            )

        # Optional: severity-bucket counts must be non-negative ints if present
        for field in OPTIONAL_INT_FIELDS:
            val = fm.get(field)
            if val is None:
                continue
            if not isinstance(val, int) or val < 0:
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}: {field}={val!r} invalid — must be "
                    f"non-negative integer if present",
                )

        # Optional consistency check: if all three severity counts present and
        # issue_count present, they should sum equal to issue_count (otherwise
        # the reviewer is mis-bucketing).
        if (
            isinstance(ic, int)
            and all(isinstance(fm.get(f), int) for f in OPTIONAL_INT_FIELDS)
        ):
            severity_sum = sum(fm[f] for f in OPTIONAL_INT_FIELDS)
            if severity_sum != ic:
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}: severity counts sum to "
                    f"{severity_sum} but issue_count={ic} — bucketing mismatch",
                )

        # Optional: strongest_counter_case_addressed enum check
        scc = fm.get("strongest_counter_case_addressed")
        if scc is not None:
            scc_str = str(scc).strip().lower()
            if scc_str not in {"addressed", "ducked", "partially"}:
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}: "
                    f"strongest_counter_case_addressed='{scc}' not in "
                    f"['addressed', 'ducked', 'partially']",
                )
