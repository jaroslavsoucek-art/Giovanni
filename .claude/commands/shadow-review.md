---
description: Quarterly audit of recent shadow hypotheses — routes to prediction-runtime in shadow-review mode. Enforces adversarial lookback discipline.
allowed-tools: Task, Read, Glob, Grep, Write
---

# /shadow-review

Process unresolved past-horizon shadow hypotheses and audit a sample of recently resolved ones for governance compliance. This command is a **thin shell** — the adversarial lookback discipline (binding principle 7) lives in the `prediction-runtime` agent. This file is the invocation contract.

## Usage

```
/shadow-review                          # default — all past-horizon pending + 10-20 resolved sample (90d window)
/shadow-review --sample 20              # custom sample size
/shadow-review --actor <slug>           # focus on hypotheses touching one actor
/shadow-review --window <YYYY-MM>       # focus on one month's resolved cohort
/shadow-review --horizon <YYYY-MM-DD>   # review hypotheses with horizon_at <= date
```

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `--sample <N>` | parameterized int | 10-20 (auto) | Size of the resolved sample to audit. Caller can override for deeper review. |
| `--actor <slug>` | parameterized string | none | Filter the cohort to hypotheses whose `actor` field matches `<slug>`. Useful when calibration-report flagged an actor with concerning patterns. |
| `--window <YYYY-MM>` | parameterized | last 90 days | Focus on a single calendar month's resolved cohort instead of rolling 90-day window. |
| `--horizon <YYYY-MM-DD>` | parameterized date | today | Review hypotheses whose `horizon_at <= <date>`. Default = today. Useful for pre-audit dry runs ("what would shadow-review have closed if I'd run it last week?"). |

All three filter args (`--actor`, `--window`, `--horizon`) can combine.

## Pre-flight (binding — STOP on failure)

Before spawning `prediction-runtime`:

1. **CWD check.** Working directory is a Giovanni repo. Otherwise STOP.
2. **Agent definition present.** `.claude/agents/prediction-runtime.md` exists. Missing → STOP.
3. **Shadow directories present.** `memory/shadow/pending/` exists. (Resolved + expired subdirs are created on first move; not required at pre-flight.) Missing pending dir → STOP: `ERROR: memory/shadow/pending/ missing. The predictive layer hasn't generated any hypotheses yet — nothing to review.`
4. **Cadence reminder (advisory, not STOP).** If the last entry in `memory/calibration/audit-log.md` is < 60 days ago, surface advisory:
   `INFO: Last /shadow-review was <N> days ago. Quarterly cadence is the policy; running this often is fine but inflates the cohort.`
   Continue anyway.
5. **Empty cohort check.** If no past-horizon pending AND no resolved hypotheses match the filter → STOP: `INFO: nothing to review (no past-horizon pending + filter matches 0 resolved). Skip this cycle.`

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Spawn `prediction-runtime`** via `Task` with:
   ```
   subagent_type: prediction-runtime
   mode: shadow-review
   sample: <N or null>
   actor: <slug or null>
   window: <YYYY-MM or null>
   horizon: <YYYY-MM-DD or null>
   ```
3. **Wait for agent return.** The agent processes the cohort: applies adversarial lookback per hypothesis, fills `adversarial_check` + `resolved_reasoning` + `resolved_date` in each YAML, moves files to `resolved/<YYYY-MM>/` or `expired/<YYYY-MM>/`, builds the comparison table, identifies concerning patterns, appends to audit log.
4. **Relay agent output verbatim** to chat. Include the audit log pointer and the principal-action hint.
5. **Do NOT commit.** Principal reviews comparison table + concerning patterns, decides whether to dispute any verdicts, and commits the audit log + moved YAMLs in batch.

## Adversarial lookback enforcement

The `prediction-runtime` agent enforces binding principle 7: each hypothesis gets the explicit adversarial prompt ("What are the STRONGEST arguments this hypothesis was NOT fulfilled?") before verdict-recording. Empty `adversarial_check` field at resolution time is a **governance breach** — the agent surfaces this if it happens (should not, given the agent enforces it).

If the orchestrator detects post-hoc that any moved YAML has an empty `adversarial_check`, it flags the breach in the report output. Lint rule `shadow_expired_pending.py` catches this at commit time.

## Output behavior

- **Render target:** chat (the comparison table + concerning patterns + recommendations summary)
- **Persistent artifacts (unstaged):**
  - `memory/shadow/resolved/<YYYY-MM>/*.yaml` — hypotheses moved from pending with filled verdict fields
  - `memory/shadow/expired/<YYYY-MM>/*.yaml` — hypotheses moved from pending with `status: expired`
  - `memory/calibration/audit-log.md` — audit entry appended
- **No mutation to `actor-scores.yaml`** — that's `/calibration-report`'s job. `/shadow-review` records verdicts in individual YAMLs; aggregation happens at calibration.
- **No auto-commit.** Principal commits in batch.

## Principal dispute path

If the principal disagrees with an adversarial-check verdict, the dispute path is:

1. Principal edits the YAML directly in `memory/shadow/resolved/<YYYY-MM>/`
2. Notes `user override per /shadow-review <YYYY-MM-DD>` in `resolved_reasoning`
3. Re-commits

The agent **never auto-applies** user disputes. Disputes are user-only edits.

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Agent failure** (timeout, crash) → surface structured error. Hypotheses already moved before failure remain moved (no rollback). Principal can re-run with `--horizon` set to before the partial run.
- **Empty cohort** → STOP at pre-flight with informational message.
- **Empty `adversarial_check` post-run** (should not happen, lint enforces) → flag verbatim in report, do not silently fix.

## Cadence guidance

- **Quarterly** is the policy cadence. Running more often is fine but produces small cohorts.
- **Triggered runs:** if `/calibration-report` flags `overall_accuracy > 80%`, the report explicitly recommends running `/shadow-review` immediately. That's a high-accuracy red flag (sandbagging or motivated verdicts), not a celebration.
- **Recovery runs:** after a digest cycle that flagged many past-horizon pending, an off-cycle `/shadow-review` clears operational debt.

## Cross-references

- **Agent (executor):** `.claude/agents/prediction-runtime.md` (mode: shadow-review)
- **Binding principles:** `docs/prediction.md` § 8 binding principles (especially #7 adversarial lookback)
- **Templates:** `memory/templates/shadow-hypothesis.template.md`
- **Calibration aggregation:** `/calibration-report` (`.claude/commands/calibration-report.md`)
- **Lint rules:** `scripts/lint_rules/shadow_expired_pending.py`, `no_percentages_in_predictions.py`

## Anti-patterns (binding)

- **Skipping the adversarial-check step** ("the verdict is obvious") — the discipline is the point.
- **Filling `adversarial_check` with a one-liner** ("no, it matched") — must construct the falsification case substantively.
- **Defaulting to matched when uncertain** — discipline rule is default-skeptical.
- **Auto-applying user disputes** (agent override of user verdict) — agent never overrides.
- **Skipping expired hypotheses** ("they're not real data") — expired is a discipline signal worth tracking.
- **Modifying `actor-scores.yaml` from this command** — that's `/calibration-report`'s job.
- **Auto-committing the audit log + moves** — principal commits in batch.
