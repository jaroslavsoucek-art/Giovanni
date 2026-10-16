---
description: Monthly calibration report — routes to prediction-runtime in calibration-report mode. Aggregates per-actor + per-tier accuracy, updates actor-scores.yaml.
allowed-tools: Task, Read, Write, Glob
---

# /calibration-report

Aggregate the previous month's shadow hypothesis outcomes into a calibration report. This command is a **thin shell** — the aggregation logic and the > 80% accuracy guard rail live in the `prediction-runtime` agent. This file is the invocation contract.

## Usage

```
/calibration-report                       # default — previous full month
/calibration-report --month <YYYY-MM>     # explicit month
```

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `--month <YYYY-MM>` | parameterized date | previous full calendar month | Explicit month to aggregate. Must be in the past (no in-progress months — cohort would be incomplete). |

If `--month` is in the future or current month → STOP: `ERROR: --month <YYYY-MM> is in the future or current. Calibration aggregates completed months only.`

## Pre-flight (binding — STOP on failure)

Before spawning `prediction-runtime`:

1. **CWD check.** Working directory is a Giovanni repo. Otherwise STOP.
2. **Agent definition present.** `.claude/agents/prediction-runtime.md` exists. Missing → STOP.
3. **Calibration directories present.** `memory/calibration/` exists. (`actor-scores.yaml` is created on first run if missing.) Missing dir → STOP: `ERROR: memory/calibration/ missing. The predictive layer hasn't been initialized.`
4. **Month boundary enforced.** If `--month` is omitted, the default is the **previous full calendar month** (today is 2026-05-21 → default is 2026-04). If today is the 1st-2nd of a month, the previous month's cohort may still have horizon spillover from the month before — surface advisory but continue.
5. **Cohort non-empty.** If no shadow hypotheses match the month → STOP: `INFO: no hypotheses created/resolved/expired in <YYYY-MM>. Nothing to aggregate this month.` Don't write an empty report.
6. **Already-reported guard.** If `memory/calibration/monthly/<YYYY-MM>.md` already exists, surface advisory: `WARN: report for <YYYY-MM> already exists. Re-run will overwrite. Proceed? [y/N]`. Default = abort.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Spawn `prediction-runtime`** via `Task` with:
   ```
   subagent_type: prediction-runtime
   mode: calibration-report
   month: <YYYY-MM>
   ```
3. **Wait for agent return.** The agent:
   - Computes volumes (generated, rejected, matched, falsified, mixed, expired, awaiting)
   - Computes overall + per-actor + per-tier accuracy
   - Checks the > 80% accuracy guard rail (surfaces immediate-action callout if breached)
   - Updates `memory/calibration/actor-scores.yaml` (rolling 60d/90d, trend, bias_watch)
   - Identifies bias patterns + profile enrichment recommendations + triage threshold suggestions
   - Writes `memory/calibration/monthly/<YYYY-MM>.md`
4. **Relay agent output verbatim** to chat. Include the report path + the > 80% callout if present.
5. **Do NOT commit.** Principal commits the report + YAML update together.

## > 80% accuracy guard rail

If `overall_accuracy > 80%`, the agent surfaces:

> ⚠ Accuracy > 80% — run `/shadow-review` immediately. High accuracy is suspect, not celebratory. Either tier labels have drifted, or adversarial-check verdicts are motivated. Quarterly audit cadence should be moved up.

The orchestrator relays this verbatim. The principal decides whether to run `/shadow-review` next.

## Output behavior

- **Render target:** chat (summary + the > 80% callout if present)
- **Persistent artifacts (unstaged):**
  - `memory/calibration/monthly/<YYYY-MM>.md` — the report
  - `memory/calibration/actor-scores.yaml` — updated per-actor + per-tier scores, trend, bias_watch
- **No mutation to `triage-heuristic.yaml`** — the report surfaces suggestions; the principal applies them.
- **No mutation to stakeholder profiles** — the report surfaces enrichment recommendations; the principal decides whether to bootstrap.
- **No auto-commit.** Principal commits report + YAML update in a single commit (atomicity matters).

## Cadence

- **Monthly**, recommended on the 1st of each month for the previous month.
- Triggered runs are fine (e.g. after a `/shadow-review` that flagged systematic patterns and the principal wants the aggregated view).
- Re-runs for the same month require explicit principal confirmation (existing report would be overwritten).

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Agent failure** → surface structured error. `actor-scores.yaml` mutation is the only state at risk; if the agent crashed mid-write, the file may be partial — the principal restores from git.
- **Future month requested** → STOP at pre-flight.
- **Empty cohort** → STOP at pre-flight with informational message. Don't write an empty report.

## Cross-references

- **Agent (executor):** `.claude/agents/prediction-runtime.md` (mode: calibration-report)
- **Binding principles:** `docs/prediction.md` § 8 binding principles
- **State file:** `memory/calibration/actor-scores.yaml`
- **Templates:** `memory/templates/calibration-monthly-report.template.md`, `memory/templates/calibration-actor-score.template.md`
- **Related commands:** `/shadow-review` (triggered when accuracy > 80%)
- **Lint rules:** `scripts/lint_rules/no_percentages_in_predictions.py`, `shadow_expired_pending.py`

## Anti-patterns (binding)

- **Cherry-picking which hypotheses to include** ("this one wasn't really our prediction") — include the full cohort.
- **Generous verdict aggregation** ("mixed counts as 0.5 matched") — mixed counts as falsified per discipline.
- **Skipping the > 80% callout** — the guard rail exists because sandbagged predictions look successful but undercut the predictive layer's value.
- **Auto-applying triage threshold suggestions** — agent suggests, principal applies.
- **Writing the report without updating `actor-scores.yaml`** — they must move together for traceability.
- **Modifying `triage-heuristic.yaml` or stakeholder profiles from this command** — surfaces only.
- **Auto-committing** — principal commits report + YAML update as one commit.
