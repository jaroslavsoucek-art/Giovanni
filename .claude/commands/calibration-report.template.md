---
description: Generate monthly calibration report aggregating shadow hypothesis accuracy
allowed-tools: Read, Write, Glob
---

# /calibration-report

<!--
============================================================================
SPEC TEMPLATE — `slash-command-architect` will use this to generate the
runtime implementation.

/calibration-report is the monthly aggregation of shadow hypothesis outcomes
into per-actor + per-tier accuracy scores, bias patterns, and threshold
suggestions.

Cadence: 1st of each month, manual.
============================================================================
-->

Aggregate the previous month's shadow hypothesis accuracy into a calibration report.

## Usage

```
/calibration-report                       # default = previous month
/calibration-report --month <YYYY-MM>     # explicit month
```

## Process

### Step 1 — Identify the cohort

Determine the month being reported on (default: previous month).

Pull all shadow hypotheses with relevant dates falling in the cohort:

- `created` in cohort month: count toward `total_hypotheses_generated`
- `resolved_date` in cohort month (any status): count toward `resolved`
- Status `expired` with horizon_at in cohort month: count toward `expired_without_verdict`
- Status `pending` with horizon_at in next month: count toward `awaiting_resolution`

### Step 2 — Compute volumes

Build the volumes table:

```
| Metric | Count |
| Shadow hypotheses generated this month | <N> |
| Rejected at generation by specificity_gate | <N> |
| With testable outcome (matched + falsified) | <N> |
| Resolved-mixed (partial match) | <N> |
| Expired without ground truth | <N> |
| Awaiting resolution (horizon spills into next month) | <N> |
```

Track triage volume health vs. `memory/triage-heuristic.yaml` thresholds:

- Active branch-out runs this month vs. `branch_out_eligibility.daily_max * days_in_month`
- Shadow generation peak day vs. `shadow_generation_eligibility.daily_max`
- Hard-fail breaches (shadow > `shadow_generation_eligibility.hard_fail_max` in any single day)

### Step 3 — Compute accuracy

**Overall accuracy:**

```
overall_accuracy = matched / (matched + falsified)
```

(Mixed counts as falsified per binding discipline rule.)

**Per-actor accuracy:** for each actor with ≥1 resolved hypothesis this month, compute the same ratio over their resolved cohort.

**Per-tier accuracy:** roll up across all actors:

```
tier_hit_rate_likely = sum(matched where tier=likely) / sum(resolved where tier=likely)
tier_hit_rate_possible_but_surprising = sum(matched where tier=possible-but-surprising) / sum(resolved where tier=possible-but-surprising)
tier_hit_rate_unlikely_but_impactful = sum(matched where tier=unlikely-but-impactful) / sum(resolved where tier=unlikely-but-impactful)
```

### Step 4 — Guard rail check

**If `overall_accuracy > 80%`:** surface the immediate-action callout in the report:

> ⚠ Accuracy > 80% — run /shadow-review immediately. High accuracy is suspect, not celebratory. Either tier labels have drifted, or adversarial-check verdicts are motivated. Quarterly audit cadence should be moved up.

This is governance failure mode #4 from the constitution. Sandbagged predictions look successful but undercut the predictive layer's value.

### Step 5 — Update `actor-scores.yaml`

For each actor in the cohort:

1. Increment `total_hypotheses` by new generations this month
2. Increment `resolved`, `matched`, `falsified`, `expired` by month's deltas
3. Recompute `accuracy_rolling_60d` and `accuracy_rolling_90d` over date-windowed resolved cohort
4. Recompute `accuracy_by_tier` per tier
5. Set `last_calibration: <today>`
6. Update `trend` per hysteresis rule:
   - `improving` if rolling_60d > rolling_90d + 0.05
   - `degrading` if rolling_60d < rolling_90d - 0.05
   - `stable` otherwise
   - `null` if resolved < 3 (insufficient data)
7. Update `bias_watch` array based on observation patterns

**DO NOT modify `triage-heuristic.yaml`** — only surface suggestions in the report.
**DO NOT modify stakeholder profiles** — only surface enrichment recommendations.

### Step 6 — Identify observation patterns

Scan for:

- **Bias patterns:** see catalog in `memory/calibration/README.md` "Bias-watch categories" — over-confidence-on-likely, channel-specificity-miss, actor-direction-flip, tier-label-drift, etc.
- **Profile enrichment recommendations:** actors whose hypotheses repeatedly miss → flag for stakeholder-profiler refresh; top 7 list by missing-pattern count
- **Triage threshold suggestions:** if specificity_gate accepted-but-expired count is climbing → suggest tightening; if hard_fail_max is being approached → suggest evaluating digest triage upstream
- **Notable cases:** 3-5 most instructive hypotheses (matched + falsified) with transferable learning

### Step 7 — Write report

Generate `memory/calibration/monthly/<YYYY-MM>.md` following the template at `memory/templates/calibration-monthly-report.template.md`.

Tell the principal:

> Calibration report for <YYYY-MM> written to `memory/calibration/monthly/<YYYY-MM>.md`. Updated `memory/calibration/actor-scores.yaml`. Review the observation flags and triage threshold suggestions before next month's cycle. Run `/shadow-review` if accuracy callout was flagged.

**DO NOT commit anything.** Principal commits the report + YAML update together.

## Governance

- **Modifies `actor-scores.yaml`** — this is the only command that does. Verdict-recording in /shadow-review writes individual YAMLs; /calibration-report aggregates.
- **Does NOT modify `triage-heuristic.yaml`** — surfaces suggestions only.
- **Does NOT modify stakeholder profiles** — surfaces enrichment recommendations only.
- **Cadence:** 1st of each month (manual). Principal commits the report.

## Anti-patterns

- Cherry-picking which hypotheses to include ("this one wasn't really our prediction") — include the full cohort
- Generous verdict aggregation ("mixed counts as 0.5 matched") — mixed counts as falsified per discipline
- Skipping the accuracy > 80% callout — the guard rail exists for a reason
- Auto-applying triage threshold suggestions — agent suggests, user applies
- Writing the report without updating `actor-scores.yaml` — they must move together for traceability

## Cross-references

- **Templates:**
  - Monthly report: `memory/templates/calibration-monthly-report.template.md`
  - Per-actor record: `memory/templates/calibration-actor-score.template.md`
- **State file schema:** `memory/calibration/actor-scores.template.yaml`
- **Shadow hypothesis schema:** `memory/templates/shadow-hypothesis.template.md`
- **Triage heuristic:** `memory/triage-heuristic.yaml`
- **/shadow-review:** `.claude/commands/shadow-review.template.md`
- **Full predictive layer documentation:** `docs/prediction.md`
