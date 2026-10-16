---
# ============================================================================
# Per-actor calibration record — Layer 3 (memory/calibration/actors/<slug>.md)
# ============================================================================
# OPTIONAL artifact: a per-actor narrative calibration record that supplements
# the rolled-up YAML state file memory/calibration/actor-scores.yaml.
#
# The YAML file is the canonical numerical state (single source of truth for
# per-tier counts and accuracy rolling-window). This markdown record is a
# NARRATIVE LAYER on top — it captures bias patterns, hit/miss notable cases,
# trend interpretation that doesn't reduce cleanly to a number.
#
# WHEN TO USE THIS RECORD
# Use the per-actor markdown record when:
#   - Total resolved hypotheses for the actor ≥ 5 (less = no narrative pattern)
#   - You want to capture qualitative observations about WHY the agent's
#     prediction tier was right or wrong
#   - Trend is degrading or surprising — the YAML alone won't explain why
#
# Skip this record when:
#   - Actor has <5 resolved hypotheses — patterns are not yet visible
#   - Trend is stable and uninteresting — the YAML is enough
# ============================================================================

actor_slug: <stakeholder-slug>
# Matches memory/stakeholders/<slug>.md. Same actor whose YAML stats roll up here.

last_updated: <YYYY-MM-DD>
# Date of most recent update. Light touch — update at /shadow-review or
# /calibration-report time, not on every hypothesis resolution.

total_predictions: <integer>
# Cumulative count of shadow hypotheses for this actor (pending + resolved + expired).

resolved_predictions: <integer>
# Cumulative count of shadow hypotheses with a verdict (matched + falsified).
# Excludes expired-without-verdict.

accuracy_by_tier:
  likely:
    n: <integer>
    matched: <integer>
    rate: <float between 0.0 and 1.0>
    # Example: likely: { n: 10, matched: 7, rate: 0.70 }
  possible-but-surprising:
    n: <integer>
    matched: <integer>
    rate: <float between 0.0 and 1.0>
  unlikely-but-impactful:
    n: <integer>
    matched: <integer>
    rate: <float between 0.0 and 1.0>
# Per-tier hit rate over resolved hypotheses.
# Healthy calibration:
#   - likely: 60-80% (if higher, agent is sandbagging; if lower, agent is over-confident)
#   - possible-but-surprising: 20-40% (the name says it — they should mostly NOT happen)
#   - unlikely-but-impactful: 5-15% (the name says it — they should rarely happen)
# Deviation from these ranges signals tier-label drift.

trend: <improving | stable | degrading | insufficient-data>
# Qualitative read on accuracy direction. "Insufficient data" if <3 monthly
# data points in /calibration-report aggregation.

bias_watch: []
# List of identified biases (filled at /shadow-review when patterns emerge).
# Examples:
#   - over-confidence-on-likely  (agent predicts "likely" and actor doesn't act — too many false positives in top tier)
#   - under-confidence-on-unlikely  (agent predicts "unlikely" and actor does act — top-tier framing under-reflects upside surprises)
#   - channel-specificity-miss  (agent predicts right outcome but wrong channel — common at /shadow-review)
#   - actor-direction-flip  (agent's reading of actor's intent is systematically inverted — re-read profile)
# Lint can warn if bias_watch grows beyond 3 items without resolution.

---

# Calibration record — <Display Name> (`<slug>`)

<!--
This narrative record supplements memory/calibration/actor-scores.yaml.
Read the YAML for numbers; read this for patterns.

Length: 50-150 lines. If shorter, the patterns aren't visible yet.
If longer, you're recording too much — calibration is a thin layer
on top of shadow review, not its own essay.
-->

**Last updated:** YYYY-MM-DD
**Total predictions:** <N> · **Resolved:** <N> · **Accuracy by tier:** likely <hit/total> · possible-but-surprising <hit/total> · unlikely-but-impactful <hit/total>

## Recent prediction patterns

<!--
What kinds of predictions hit, what kinds missed. Be specific:
- "Predictions about channel choice land; predictions about timing miss by 1-2 days"
- "Predictions about technical objections match; predictions about commercial pushback under-predict frequency"
- "Predictions on tier 'likely' for this actor are at 0.5 — agent is over-confident here"

If the pattern is "no pattern yet, sample too small", say that.
-->

### Notable hits

- **<YYYY-MM-DD>: <hypothesis topic>** — predicted <tier> that <prediction>; matched because <reason>. Resolved-yes per `memory/shadow/resolved/<YYYY-MM>/<id>.yaml`.
- **<YYYY-MM-DD>: <hypothesis topic>** — predicted <tier> that <prediction>; matched in the time window. The channel guess was exact.

### Notable misses

- **<YYYY-MM-DD>: <hypothesis topic>** — predicted `likely` that <prediction>; falsified per adversarial check. Direction was right but channel guess was wrong (specificity miss — see bias-watch).
- **<YYYY-MM-DD>: <hypothesis topic>** — predicted `unlikely-but-impactful` that <prediction>; matched, but it actually happened. Indicates the tier was wrong (tier underestimated; pattern check needed).

## Calibration trend

<!--
Trend over the last 60-90 days. Use the rolling-window accuracy field from
the YAML state file. Single value isn't trend; sequence is.

Anti-pattern: "calibration is improving" with no evidence. Cite the
rolling-window numbers and how they moved.
-->

<Multi-paragraph trend assessment citing rolling-window accuracy from
actor-scores.yaml. Mention sample size — calibration is meaningless at
n=2.>

## Bias watch

<!--
Identified systematic biases in predictions for this actor. Each bias:
- Name
- Pattern observed (with date/case citations)
- Mitigation hypothesis (what should change for next prediction)
- Status (open / mitigated)

Bias-watch entries are MOVED to "Mitigated" subsection when accuracy has
stabilized in the post-mitigation cohort (rule of thumb: 5 predictions
post-mitigation showing no recurrence).
-->

### Active

- **<bias name>** — <pattern observed with citations>. Mitigation: <what should change>. Status: open since YYYY-MM-DD.
- **<bias name>** — <pattern>. Mitigation: <what>. Status: open since YYYY-MM-DD.

### Mitigated

- ~~**<bias name>**~~ — mitigated YYYY-MM-DD after <N> predictions showing no recurrence. Original entry: <date and pattern>.

## Anti-patterns to watch

<!--
For THIS actor specifically — what kind of predictions should not be made
because the pattern keeps failing. Different from "bias-watch" — those are
in-progress diagnostics; this is settled wisdom.

Examples:
- "Don't predict response time below 24h — actor has a deliberate-processing pattern"
- "Don't predict actor will speak in group forum when topic is sensitive — pattern is 1:1 first, group second"
- "Avoid likely-tier predictions for actor's commercial-strategy moves; calibration here is consistently weak"
-->

- <Anti-pattern observation>
- <Anti-pattern observation>

## Re-read profile recommendation

<!--
If calibration is degrading or bias-watch is growing without resolution,
re-reading and updating the stakeholder profile is the structural fix.

Note any specific sections of the profile that the calibration evidence
suggests should be revised:
- "Sentiment trajectory entries between Mar-Apr should be revisited — agent's
   reading of warming signal was inverted (actor was cooling)"
- "Predicted reactions section has 3 predictions whose calibration is <30%;
   those reactions should be archived as stale and re-derived"

This is the connective tissue between calibration discipline and stakeholder
profile maintenance.
-->

- <Profile section to revisit> — <reason>
- <Profile section to revisit> — <reason>

## Related artifacts

- **Stakeholder profile:** `memory/stakeholders/<slug>.md`
- **Aggregated YAML state:** `memory/calibration/actor-scores.yaml` (canonical numerical record)
- **Recent shadow hypotheses (resolved):** `memory/shadow/resolved/<YYYY-MM>/<id>.yaml` (list 3-5 most recent)
- **Recent monthly report:** `memory/calibration/monthly/<YYYY-MM>.md`
