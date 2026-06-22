<!-- ILLUSTRATIVE REVIEW TRANSCRIPT — demonstration artifact, not a live review run. This is the
adversarial-reviewer output for the deliverable at ../deliverables/2026-05-30_series-b-narrative-v0.3.md. -->

# Adversarial Review Example — Series B Narrative v0.3

<!--
EXAMPLE STATUS — not a live deliverable.

This file demonstrates the output format of the adversarial-reviewer agent.
The scenario: Alex Park (Lattice CEO) drafts Series B narrative v0.3, references
the €1.8M ARR projection. The repo state (memory/topics/dp1-renewal.md) shows
the design-partner-1 €180K ARR account is at material churn risk after champion
departure.

The example deliberately surfaces the highest-leverage adversarial finding:
the projection assumes 100% retention on a customer base where the largest
account is in active churn risk. A sharp B-stage VC will model the haircut
in 30 seconds. The narrative ducks the contradiction.

Purpose of this file:
1. Demonstrate the verdict format
2. Show what "strongest counter-case" construction looks like
3. Show the difference from deliverable-reviewer (content QA) output
4. Test the workflow against a real-shaped scenario

The draft being reviewed (deliverables/2026-05-30_series-b-narrative-v0.3.md) is
referenced but does not need to exist as a separate file for this example — the
review output below references its content inline.
-->

## File: `deliverables/2026-05-30_series-b-narrative-v0.3.md`

### Position the draft is defending

Lattice is ready for Series B now, anchored on €1.8M ARR projection by year-end and a platform-fee unit economics narrative that justifies a step-up valuation.

### Verdict

**REWRITE**

### Strongest counter-case

The €1.8M ARR projection assumes 100% retention on the design partner cohort. The largest account in that cohort (€180K ARR, 15% of total) is in active churn risk — champion departed 2026-04-12, new CFO is reassessing the treasury stack, first call set for 2026-05-27. A B-stage VC will pattern-match this in under five minutes (departed champion + CFO-led re-evaluation is a textbook churn signal) and model a haircut: €1.8M projection → €1.62M effective, ARR growth narrative drops from 50% YoY to 35%. **Verdict: the draft ducks this counter-case entirely. The phrase "design partner cohort retention assumed at trajectory" does not survive contact with Sarah Vyas's diligence model, let alone a less-friendly Series B partner.**

### Issues

**Fatal (blocks send — KILL territory if not addressed):**

- **The €1.8M projection contradicts the active state in `memory/topics/dp1-renewal.md`.** The topic shard documents DP1 as Risk A (active churn risk) with renewal probability 40-60% and a first call set 2026-05-27 — i.e. unresolved at draft time. The narrative cannot project DP1 at full ARR contribution while the canonical record says it's at-risk. This isn't a hedge to add; it's a contradiction to resolve before the draft can ship.
  - **Why it matters:** Sarah Vyas (the lead VC the narrative is targeting) is on the board and has seen the DP1 shard items added to the 2026-05-26 1:1 agenda. She will know the projection is structurally inconsistent with what we've told her two days earlier. Sending the narrative with the contradiction unresolved costs more trust than acknowledging the risk would have cost.
  - **What would fix it:** Two paths. (a) Wait for the 2026-05-27 call outcome, then reproject with the actual renewal probability. (b) Ship the narrative with explicit risk-adjusted ARR ("€1.62M base case, €1.8M if DP1 renews" or similar) and own the contradiction directly. Choose (a) if the call is the better signal source; choose (b) if timing pressure dominates.

- **"Platform-fee unit economics improvement" is unsourced.** The draft asserts the platform-fee transition (per pricing-v2) improves unit economics, but the pricing-v2 board vote is 2026-06-09 — i.e. unresolved at draft time. Per `memory/topics/dp1-renewal.md` and the topic shard for DP1, the new model moves DP1 from €15K/mo per-seat to ~€11K/mo platform + per-entity, which is a Lattice-side reduction in the short term. Net positive only at month 12 in the model.
  - **Why it matters:** B-stage VCs read "platform-fee improvement" as gross margin expansion + ACV expansion. The actual mechanic is a 4-month revenue dip followed by expansion-revenue compensation. The unit-economics framing is misleading without the dip disclosure.
  - **What would fix it:** Replace the un-numbered "improvement" claim with the actual model — short-term per-customer ARR dip (~€32K/mo across 8 customers for ~4 months), expansion-revenue compensation by month 12, net positive thereafter. Owns the trough; the curve is more credible than the hand-wave.

**Major (blocks send — REWRITE territory):**

- **"Net Retention >115% trajectory" is asserted but not yet reported.** Sarah committed in 2026-04-29 1:1 to add NRR to the monthly board report; per the topic shard, this is still pending (target: June 2026 monthly cycle). The narrative cites the metric as if it's a tracked KPI; it's currently a projection, not an observed series.
  - **Why it matters:** B-stage diligence will request the NRR series and find it doesn't exist. The narrative claim then degrades from "tracked KPI" to "founder estimate" mid-call.
  - **What would fix it:** Either present NRR as a forward projection with explicit methodology, or hold the claim until the June report ships and lock the methodology in advance.

- **VP Engineering hire framed as locked.** The narrative implies the VP Eng hire is closing; per the topic shard / Sarah brief, Alina Crisan is in final round with target offer 2026-06-02, comp committee path unresolved, hire-close confidence 50-70% range.
  - **Why it matters:** B-stage VCs will ask the close date and confidence directly. Framing a 50-70% hire as locked is a precision mismatch that erodes confidence in everything else cited at high confidence.
  - **What would fix it:** "VP Eng search in final round; target offer 2026-06-02; hire-close milestone material for B closing timeline." Doesn't weaken the narrative; calibrates the confidence.

**Minor (should fix; doesn't block):**

- The phrase "platform-fee inflection" recurs three times. Once is framing; three times is a slogan. Cut to one usage.
- "ARR €1.2M → €1.8M" appears in two places with different surrounding language; consistency reads as drafting carelessness in a document that's nominally locked.

### What's missing entirely

- **No acknowledgment of competitor X.** Sarah forwarded the TechCrunch article on competitor X's rumored Series C on 2026-05-12. The narrative's defensibility section talks about Lattice's mid-market treasury depth but does not mention competitor X. A B-stage VC reading the narrative who knows competitor X exists will read the omission as either ignorance or avoidance. Differentiation needs to engage with the specific competitor, not the abstract category.
- **No exit framing.** The narrative is built around the next round; B-stage VCs model the exit at the next round, not just the current one. Silence on the exit thesis is read as "founders haven't thought about it" — usually a worse signal than a wrong exit thesis.
- **No mention of EU compliance posture.** Lattice's geographic positioning includes EU AWS region + SOC 2; for a B-stage round targeting US and EU VCs, this is a differentiation lever. The narrative omits it.

### Verbatim strikes (delete these)

- "We're confident in our trajectory" — "we're confident" is unsupported assertion; either show the data that produces confidence or cut.
- "Platform-fee economics open up a new chapter" — chapter-language is deck-flavored, not narrative-flavored; Sarah explicitly asked in 2026-04-29 1:1 for "a narrative thesis paragraph that doesn't sound like a deck slide". This is the deck slide.
- "Best-in-class retention" — unsupported and category-creep. The metric is NRR, currently unreported. Strike.
- "Our momentum is undeniable" — RLHF-style framing dressed up as narrative voice. The reader will deny it (B-stage VCs deny everything by default); the sentence creates an opening rather than closing one.

### Recommended next action

Hold the narrative at v0.3 until after the 2026-05-27 DP1 call. Reproject ARR with the actual renewal signal (or risk-adjusted band), then issue v0.4 with explicit DP1 disclosure + competitor X engagement. Sending v0.3 to Sarah at the 2026-05-26 1:1 risks a credibility hit that costs more than the timing delay.

---

<!--
============================================================================
NOTES ON THIS EXAMPLE (for adversarial-architect verification)
============================================================================

WHY THIS IS A SHARP REVIEW (test against the workflow's quality gates):

1. The fatal finding is the load-bearing contradiction — €1.8M ARR projection
   vs DP1 churn risk per topic shard. The review surfaces it explicitly,
   cites both sources, and proposes two concrete fix paths. This is the
   strongest-counter-case construction in action.

2. The strongest counter-case is constructed, not skipped. It runs three
   sentences, names the specific B-stage diligence pattern (departed
   champion + CFO re-evaluation = textbook churn signal), and assesses
   the draft's handling: "ducks this counter-case entirely". Not "could be
   stronger" — ducks.

3. Severity categorization is honest. Two fatals (genuine ship-blockers
   linked to repo contradictions), two majors (fixable issues that block
   send), two minors. Not one fatal hidden among ten minors; not ten majors
   diluting the fatal signal.

4. Issues cite repo state. Topic shard `memory/topics/dp1-renewal.md` is
   referenced four times; Sarah's brief is referenced twice; specific dates
   (2026-04-12, 2026-05-19, 2026-05-27, 2026-06-09, etc.) anchor every
   factual claim. This is what "cross-checked against repo" looks like in
   output.

5. No softening preambles. Opens with verdict line. The "Recommended next
   action" section is one sentence + one specific action (hold v0.3, ship
   v0.4 after the call), not three paragraphs of options.

6. Voice matches the draft (English, business-formal-but-direct). Per the
   workflow's "match draft language" rule.

CONTRAST WITH deliverable-reviewer.example.md (content QA):

The deliverable-reviewer on the same draft would flag:
- Provenance: which decision records back the projection?
- Voice match: internal vs external mix?
- Diff vs v0.2: what changed?
- Mirror status: is the file in deliverables/ and ~/Desktop/.../deliverables/?

Different layer, different findings. Same draft can fail one and pass the
other. Both reviewers can run.

DRIFT WATCH: if this example ever reads as "the position is mostly fine
but here are a few concerns", the schema is too soft and needs tightening.
The €1.8M-vs-DP1 contradiction is fatal-tier; if the example softens it,
the workflow softens with it.
-->
