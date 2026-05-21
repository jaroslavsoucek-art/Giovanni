---
description: Manual audit of recent shadow hypotheses (quarterly governance task)
allowed-tools: Read, Glob, Grep, Write
---

# /shadow-review

<!--
============================================================================
SPEC TEMPLATE — `slash-command-architect` will use this to generate the
runtime implementation.

/shadow-review is the quarterly governance audit of the shadow layer.
It surfaces resolved hypotheses for adversarial verdict-recording,
catches motivated-reasoning patterns, and resolves any pending
hypotheses past horizon.

Cadence: quarterly. Hook reminder fires at digest start if last review
> 90d ago.
============================================================================
-->

Quarterly audit of recent shadow hypotheses for governance compliance and adversarial lookback discipline.

## Usage

```
/shadow-review                            # process all unresolved past-horizon + 90d sample
/shadow-review --sample 20                # custom sample size
/shadow-review --actor <slug>             # focus on one actor
/shadow-review --window <YYYY-MM>         # focus on one month
```

## Process

### Step 1 — Identify candidate hypotheses

Two cohorts are reviewed:

**A. Unresolved past-horizon** (operational debt to clear):

- List all files in `memory/shadow/pending/` where `horizon_at` is in the past
- Severity scoring: > 7 days overdue is high priority; ≤ 7 days is medium

**B. Recent resolved sample** (governance audit):

- List all files in `memory/shadow/resolved/<YYYY-MM>/` for last 90 days
- Random sample 10-20 from the cohort (or `--sample` size)

The combined set is the review batch.

### Step 2 — Adversarial lookback per hypothesis

For each hypothesis in the review batch, follow this protocol:

1. **Re-read the prediction** — what specifically was predicted, at what tier, by what horizon, with what expected_signal
2. **Search for ground-truth signal** in the source channels named in `expected_signal.source_channels`, using `expected_signal.search_terms`
3. **Construct the adversarial case** — explicitly prompt:

   > What are the STRONGEST arguments this hypothesis was NOT fulfilled, even if the agent initially read the signal as a match?

4. **Apply the verdict rule:**
   - If the adversarial case is weak and a clean signal matched: `resolved-yes` (matched)
   - If the adversarial case has merit but the signal directionally matched: `resolved-mixed`
   - If no signal observed or the adversarial case is strong: `resolved-no` (falsified)
   - If signal ambiguous and no time for further verification: `resolved-no` (default-skeptical)
   - If horizon passed and reviewer can't verify either way after reasonable effort: `expired`

5. **Fill `adversarial_check` field** in the YAML with the falsification reasoning. **Empty `adversarial_check` field at resolution time is a governance breach.**

6. **Fill `resolved_reasoning` field** with the verdict reasoning (the positive case).

7. **Fill `resolved_date` field** with today's date.

### Step 3 — File movement

Move hypotheses to the appropriate subdirectory:

```bash
# resolved-* → resolved/<YYYY-MM>/
git mv memory/shadow/pending/<id>.yaml memory/shadow/resolved/<YYYY-MM>/<id>.yaml

# expired → expired/<YYYY-MM>/
git mv memory/shadow/pending/<id>.yaml memory/shadow/expired/<YYYY-MM>/<id>.yaml
```

Filename stays stable. Status field reflects the verdict.

### Step 4 — Surface comparison: agent verdict vs user verdict

After processing the sample, build the comparison table:

| ID | Agent verdict (pre-adversarial) | Final verdict (post-adversarial) | User concurs? | Note |
|----|-------------------------------|----------------------------------|---------------|------|
| ... | ... | ... | ... | ... |

The "user concurs" column is filled at /shadow-review time (or by the principal in followup). Discrepancies between adversarial-final verdict and user-judgment surface motivated-reasoning patterns.

### Step 5 — Concerning patterns

Identify discrepancies that suggest systematic bias:

- **Over-calling matched:** if agent's pre-adversarial verdict was matched in ≥3 cases where adversarial flipped to falsified, the adversarial check is doing its job but the agent's initial reads are over-generous → tighten adversarial-check prompt
- **Tier-label drift:** if `likely` tier hits at <40% or `unlikely-but-impactful` hits at >25% in the sample, tier criteria are broken → recalibrate
- **Channel-specificity miss:** if direction is right but channel guess is wrong in ≥30% of sample → tighten `expected_signal.source_channels` per actor
- **Actor-direction-flip:** if predictions about a specific actor's intent are systematically inverted → re-read the profile, sentiment trajectory may be misread

### Step 6 — Audit log

Append to `memory/calibration/audit-log.md` (create if not exists):

```markdown
## Shadow review — <YYYY-MM-DD>

**Sample size:** <N> (resolved) + <N> (past-horizon pending)
**Date range:** <start> to <end>
**Coverage:** <% of resolved hypotheses in window>

### Verdict summary

| Tier | n | Matched | Falsified | Mixed | Expired |
|------|---|---------|-----------|-------|---------|
| likely | <n> | <n> | <n> | <n> | <n> |
| possible-but-surprising | <n> | <n> | <n> | <n> | <n> |
| unlikely-but-impactful | <n> | <n> | <n> | <n> | <n> |

### Discrepancies (agent pre-adversarial vs final verdict)

<count + brief description of patterns>

### Concerning patterns

<actor-specific or framework-wide pattern observations>

### Recommended manual actions for principal

<for principal — manual recalibration suggestions, profile enrichment, triage threshold review>
```

## Governance

- **DO NOT modify `actor-scores.yaml`** in this command. That's `/calibration-report`'s job. /shadow-review records verdicts in individual YAML files; aggregation happens at /calibration-report.
- **Principal CAN dispute** adversarial-check verdicts. The dispute path: principal edits the YAML directly, notes "user override per /shadow-review YYYY-MM-DD" in `resolved_reasoning`, and re-commits. The agent never auto-applies user disputes.
- **Frequency:** quarterly. Hook reminder fires at digest start if last review > 90d ago.
- **Cumulative effect:** at 4 reviews per year, the framework has aggregated 80+ verdict trail across all actors after a year — meaningful calibration data.

## Anti-patterns

- Skipping the adversarial-check step ("the verdict is obvious") — the discipline is the point
- Filling `adversarial_check` with a one-liner ("no, it matched") — must construct the falsification case substantively
- Defaulting to matched when uncertain — discipline rule is default-falsified
- Auto-applying user disputes (agent override of user verdict) — agent never overrides
- Skipping expired hypotheses ("they're not real data") — expired is a discipline signal worth tracking

## Cross-references

- **Shadow hypothesis schema:** `memory/templates/shadow-hypothesis.template.md`
- **Calibration aggregation:** `/calibration-report` (`.claude/commands/calibration-report.template.md`)
- **Triage heuristic:** `memory/triage-heuristic.yaml`
- **Full predictive layer documentation:** `docs/prediction.md`
- **Audit log location:** `memory/calibration/audit-log.md`
