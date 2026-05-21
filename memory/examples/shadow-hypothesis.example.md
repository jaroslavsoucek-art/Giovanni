# Shadow hypothesis example — Karim renewal prediction

<!--
This is the EXAMPLE counterpart to memory/templates/shadow-hypothesis.template.md.
It shows what a properly-formed shadow hypothesis looks like for the Lattice
domain.

The corresponding actual hypothesis file (if generated in production) would
live at:
    memory/shadow/pending/2026-05-21-lattice-design-partner-1-roi-pricing-concession-a9b2.yaml

Per binding rule: this hypothesis is INVISIBLE to Alex at generation time.
It is shown here as illustration of the schema, not as a hypothesis that
would be surfaced. In production, Alex would see the /branch-out output
above but would NOT see this prediction during the 2026-05-22 → 2026-06-15
window.
-->

```yaml
id: 2026-05-21-lattice-design-partner-1-roi-pricing-concession-a9b2

created: 2026-05-21

generated_by: branch-out:dp1-renewal-call-2026-05-27
# Provenance — this hypothesis was dropped during the /branch-out simulation
# for the DP1 renewal call. Cross-referenced from the branch-out artifact's
# related_shadow_hypotheses field for /shadow-review traceability.

topic: Karim renewal posture — ROI conversation followed by pricing concession ask

actor: lattice-design-partner-1
# References memory/stakeholders/lattice-design-partner-1.md (Karim is the
# new buyer-of-record there). The profile_depth is `partial` per the
# stakeholder profile — partial is the threshold; below this we'd refuse to
# generate.

source_signal: >-
  Karim Solanki signals openness to renewal conversation via EA Mira
  exchange 2026-05-19, framing as "wants to understand the stack value
  before continuing". Call scheduled 2026-05-27 with quantified ROI
  framing planned by Alex. The 2026-05-19 EA tone is CFO-evaluation
  posture, not relationship-mode. Historical pattern from stakeholder
  profile: new buyer-of-record after champion departure typically
  follows ROI conversation with pricing pressure before committing to
  renewal terms (predicted-reactions section, third entry).

prediction: >-
  By 2026-06-15, Karim Solanki (or his EA Mira on his behalf) will send
  an outbound email or Teams message to Alex / Priya that explicitly
  requests a pricing concession on the DP1 renewal — either a discount
  (e.g. retention rebate, list-price reduction), a tier change (move
  from current bundle to a lower tier), or a renewal-term restructure
  (shorter term, more flexibility) — citing the ROI evaluation as
  justification.

prediction_tier: possible-but-surprising
# Tier reasoning: pricing-concession ask from a new CFO buyer is plausible
# but not default. Default expectation (likely) is extending the evaluation
# window without explicit pricing ask. The concession-with-ROI-justification
# pattern is non-default but observed across similar enterprise-customer
# renewal motions.

expected_signal:
  description: >-
    Inbound message from Karim Solanki, Karim's EA Mira, or Helios
    procurement to Alex Park, Priya Shah, or Lattice general inbox.
    Match criteria (operational — auditable at /shadow-review):
    (a) Mentions DP1 renewal AND
    (b) Mentions pricing in explicit terms — discount percentage, tier
        name change, term-length adjustment, or renewal-pricing
        restructure language AND
    (c) References the 2026-05-27 ROI discussion or the broader value
        evaluation as justification.
    Partial match (counts as resolved-mixed): only (a) and (b) without
    (c) — pricing pressure without ROI-justification framing.
  search_terms: ["discount", "renewal", "pricing", "concession", "terms", "Karim", "Mira", "Solanki"]
  source_channels: [email, slack]

horizon_days: 25
horizon_at: 2026-06-15
# Horizon = call date + 19 days. Standard pattern: CFOs in evaluation mode
# typically push pricing within 2-4 weeks of the value conversation. 14-day
# horizon was too short; 30+ was too long. 25 days balances testability
# against horizon-cap discipline.

source: branch-out:dp1-renewal-call-2026-05-27

status: pending

# Fields below filled at /shadow-review or post-horizon resolution

resolved_date: null

resolved_reasoning: null
# Filled at /shadow-review with adversarial reasoning citing observed
# signal (or its absence).

adversarial_check: null
# Filled at /shadow-review. Required prompt: "What are the STRONGEST
# arguments this hypothesis was NOT fulfilled, even if the agent
# initially read the signal as a match?"
```

<!--
============================================================================
COMMENTARY (not part of the YAML — illustrative)
============================================================================

### Why this hypothesis qualifies

1. ✅ Actor has a profile (lattice-design-partner-1) with profile_depth: partial — above the shallow threshold.
2. ✅ Specific testable expected_signal — concrete channels, search terms, and structural match criteria.
3. ✅ Horizon within 1-14 day soft cap (extended to 25d per the 30-day enterprise-renewal observation pattern; still within the 30-day hard cap).
4. ✅ Knowing the prediction would NOT change Alex's behavior — Alex would walk into 2026-05-27 with the ROI framing regardless of whether the agent predicted a follow-up concession ask. The prediction is about the t+2 follow-up move, not the t+1 in-call dynamic.

### Why this hypothesis is INVISIBLE to Alex at generation

If Alex saw this prediction before 2026-05-27, he would walk into the call:
- Anticipating the concession ask
- Possibly pre-emptively framing pricing as non-negotiable to head it off
- Reading post-call Karim signals through the lens of "did he push for the concession?"

Each of those is a behavioral change that contaminates the test. The hypothesis must be hidden until 2026-06-15 + verdict time.

### Verdict pathway

At 2026-06-15:
- **If pricing-concession ask landed** in the window (matching criteria a + b + c): verdict = matched
- **If pricing pressure surfaced without ROI-justification framing** (matching a + b only): verdict = resolved-mixed (counts as falsified in calibration; nuance retained in adversarial_check)
- **If no pricing pressure surfaced at all**: verdict = falsified
- **If Karim went silent / no signal at all by horizon**: 
  - Run adversarial-check: did Alex's pre-emptive moves prevent the signal? If yes, hypothesis is structurally invalidated (Alex saw the prediction or accidentally hedged).
  - Default to falsified if no clear answer.
- **If horizon passed and no /shadow-review by horizon + 30d**: status = expired (no verdict)

### What the adversarial_check might say (hypothetical)

If at /shadow-review the signal looks like a match, the adversarial prompt asks:
> "What are the STRONGEST arguments Karim did NOT in fact request a pricing concession as defined?"

Possible answers:
- The mentioned 'pricing' was about contract term renewal, not discount — terminology overlap, not actual concession ask
- The concession ask was generic (industry standard CFO negotiation move) rather than ROI-tied — failing criterion (c)
- The message was from procurement, not Karim/Mira directly — actor was structurally different
- The message arrived 1 day after horizon (2026-06-16) — out of window

If the adversarial case has any of these merits, verdict = falsified (or mixed).

============================================================================
-->
