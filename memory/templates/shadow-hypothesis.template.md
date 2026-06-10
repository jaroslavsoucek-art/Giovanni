# Shadow hypothesis template

<!--
============================================================================
THIS IS A YAML TEMPLATE. Filename convention:
  memory/shadow/pending/<YYYY-MM-DD>-<actor-slug>-<topic>-<4char-hash>.yaml

Shadow hypotheses are TESTABLE PREDICTIONS about a specific actor's behavior
within a bounded time window. They live in three subdirectories by status:
  memory/shadow/pending/   — generated, awaiting horizon_at
  memory/shadow/resolved/<YYYY-MM>/  — past horizon, verdict recorded
  memory/shadow/expired/<YYYY-MM>/   — past horizon, no signal observed (no verdict)

============================================================================
BINDING RULE — SHADOW INVISIBILITY (carry verbatim across forks)
============================================================================
SHADOW HYPOTHESES ARE NEVER SHOWN TO THE PRINCIPAL AT GENERATION TIME.

Surfacing a prediction to the actor or principal during the prediction window
self-fulfills or self-prevents it (Heisenberg / observer effect). The whole
point of the shadow layer is to track what would have happened WITHOUT the
prediction influencing behavior.

Visibility rule (binding):
- At generation: invisible (stored in memory/shadow/pending/, never surfaced in
  /branch-out output, never quoted in digests, never mentioned in 1:1 prep)
- At horizon_at + 1 day: invisible until /shadow-review reveals as a batch
- At /shadow-review: surfaced for adversarial lookback, then archived
- At /calibration-report: aggregated as anonymized actor-level scores

A shadow hypothesis you discuss with the principal is no longer a shadow
hypothesis. It's an active prediction and belongs in branch-out, not here.

============================================================================
TEMPLATE CONTENT BELOW — copy schema into a new YAML file in pending/.
============================================================================
-->

```yaml
# ============================================================================
# Shadow hypothesis schema (binding)
# ============================================================================

id: <YYYY-MM-DD>-<actor-slug>-<short-topic>-<4-char-hash>
# Unique ID. Matches filename. Hash is to avoid collision when multiple
# hypotheses get generated for the same actor on the same day on the same
# topic (rare but possible).

created: <YYYY-MM-DD>
# Date the hypothesis was generated.

generated_by: <"branch-out:<slug>" | "digest:<date>" | "freestanding">
# Provenance — which workflow dropped this hypothesis. Branch-out hypotheses
# are linked back to the simulation; digest hypotheses are dropped during
# the daily-digest workflow on passive-signal items; freestanding are user-
# generated for explicit calibration tests.

topic: <one-line topic description>
# E.g. "Karim renewal posture", "Sarah burn-rate framing", "Morgan VP Eng confidence".

actor: <stakeholder-slug>
# References memory/stakeholders/<slug>.md. Actor MUST have a profile.
# Lint can verify this slug resolves.

source_signal: >-
  <Multi-line description of what was observed that triggered the
  hypothesis. Be specific — dates, channels, exact quotes if possible.
  This is the OBSERVATION that the hypothesis is predicting a follow-up to.>

prediction: >-
  <Single specific testable claim about what actor will do by horizon_at.
  MUST be falsifiable — if you can't say "this either happened or didn't"
  by horizon_at, the prediction is too vague.

  Anti-pattern: "Karim will be cooperative" — unfalsifiable.
  Better: "Karim will respond to Priya's 2026-05-22 email within 48h with
  either a meeting confirm or a meeting decline" — falsifiable.>

prediction_tier: <likely | possible-but-surprising | unlikely-but-impactful>
# BINDING ENUM — three tiers only. No percentages.
#   - likely: pattern-matched against actor history; default expectation
#   - possible-but-surprising: plausible but non-default behavior
#   - unlikely-but-impactful: low probability, high consequence

expected_signal:
  description: >-
    <How will you know the prediction was met or falsified?
    Be operational: name the channel, the search terms, the structural
    features of the expected observation.

    The lint rule scripts/lint_rules/shadow_expired_pending.py uses
    horizon_at; verification is human at /shadow-review time. This
    description is what the human reads to decide matched/falsified.>
  search_terms: [<keyword>, <keyword>, ...]
  source_channels: [<channel-1>, <channel-2>, ...]
  # Channels are operational, not abstract. Use whatever channels the
  # principal's tooling indexes (slack, email, calendar, asana, github, etc.).

horizon_days: <integer 1-14>
# Number of days from `created` until the prediction is testable.
# Hard cap: 14 days (beyond is not testable — actor will have moved through
# multiple unrelated cycles).
# Soft preference: 2-7 days for digest-generated shadow; 7-14 for branch-out-
# generated shadow.

horizon_at: <YYYY-MM-DD>
# Calendar date = created + horizon_days. Lint rule
# scripts/lint_rules/shadow_expired_pending.py flags pending hypotheses
# past this date.

source: <"freestanding" | "branch-out:<branch-out-slug>" | "digest:<YYYY-MM-DD>">
# Provenance. If source == "branch-out:...", that branch-out's
# related_shadow_hypotheses field should list this ID for cross-reference.

status: pending
# Enum (binding):
#   - pending: awaiting horizon_at
#   - resolved-yes: signal observed, verdict = matched
#   - resolved-no: signal not observed, verdict = falsified
#   - resolved-mixed: partial match (counts as falsified in calibration aggregation
#                     but the verdict reasoning notes the partial nature)
#   - expired: past horizon_at with no signal observed AND no human verdict —
#              ambiguous outcome. Counts toward "expired without ground truth"
#              metric in /calibration-report.

# ============================================================================
# FIELDS BELOW are filled at /shadow-review or by ground-truth observation,
# NOT at generation time. Leave empty / null when creating the hypothesis.
# ============================================================================

resolved_date: <YYYY-MM-DD or null>
# Date the verdict was recorded. Null while status=pending.

resolved_reasoning: >-
  <Multi-line. WHY the verdict went the way it did. Cite the observed
  signal (or its absence). Be operationally specific.

  This field is the audit trail. Calibration aggregation depends on it
  being honest, not motivated.>

adversarial_check: >-
  <ADVERSARIAL LOOKBACK — filled at /shadow-review time.

  Binding prompt (do not soften): "What are the STRONGEST arguments
  this hypothesis was NOT fulfilled, even if the agent initially
  read the signal as a match?"

  This counterweights LLM overconfidence. Default posture is skeptical,
  not confirming. If on adversarial-check the verdict shifts from
  matched to falsified, that's the system working.

  Default rule: "if uncertain, falsified". Generosity in verdict =
  motivated reasoning = calibration corruption.>

caveat: >-
  <OPTIONAL — matched-with-caveat marker. Filled at /shadow-review time;
  leave null at generation and for strict matches or falsified verdicts.

  Use when the SUBSTANCE of the prediction matched but the channel or
  timing missed — e.g. predicted "morgan-chen confirms the VP Eng finalist
  on the chat-platform within 48h", and Morgan confirmed the finalist, but
  in the weekly 1:1 and two days late. Status stays resolved-yes and the
  hypothesis counts as matched in actor scores — but calibration reports
  split strict vs caveat matches, so the caveat MUST be recorded here,
  not buried in resolved_reasoning.

  Symmetry principle (binding): generosity on substance corrupts
  calibration one way; strictness on channel/timing corrupts it the
  other. A channel/timing miss alone is NOT grounds for falsified —
  but an undocumented caveat is motivated reasoning by omission.>
```

<!--
============================================================================
TEMPLATE USAGE NOTES (not part of the YAML)
============================================================================

WHEN TO GENERATE A SHADOW HYPOTHESIS

A shadow hypothesis should ONLY be generated when:
1. The actor has a profile in memory/stakeholders/ (profile_depth: partial
   or deeper — shallow profiles produce noise, not signal)
2. There is a specific testable expected_signal (not a vibes prediction)
3. horizon_days is within 1-14 day window
4. The hypothesis would NOT change behavior if it were known to the
   principal at generation time (if it would, it belongs in /branch-out,
   not in shadow)

memory/triage-heuristic.yaml `shadow_generation_eligibility` formalizes
this — its specificity_gate rejects vague hypotheses.

WHEN NOT TO GENERATE

- Single-actor reactive decisions with no clear time window
- Actor has shallow / no profile (noise)
- Prediction would require the agent to act differently to "fairly test" it
- Outcome is already determined by external constraints (calendar, contract,
  decided plan)
- Horizon would exceed 14 days
- The prediction is so vague that "matched / falsified" is a coin flip

DIRECTORY STRUCTURE

memory/shadow/
  pending/                              → currently active hypotheses
  resolved/
    <YYYY-MM>/                          → resolved within that month
  expired/
    <YYYY-MM>/                          → expired within that month
                                          (status=expired, no human verdict)

Movement between subdirectories happens at /shadow-review or via the
post-horizon expiration sweep — both are HUMAN-INITIATED. No auto-promotion.

============================================================================
-->
