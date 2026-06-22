---
slug: series-b-prep
status: active
owner: self
last_touch: 2026-06-15
key_stakeholders: [sarah-vyas, morgan-chen]
related_decisions: []
related_briefs: []
related_knowledge:
  - knowledge/constitution.md
related_artifacts: []
related_topics: [dp1-renewal, vp-eng-hire, pricing-v2]
---

# Series B prep — closing the €3M ARR + NR>115% narrative gap

## Status & current state

**The fundable bar is €3M ARR and Net Retention >115% by month 24; today ARR is ~€1.2M with NR not yet instrumented to prove >115%, so the gap is both an absolute-growth gap and a metric-evidence gap.** The raise is roughly 12 months out. Sarah Vyas (Series A lead, board director) is the inside-track signal on what her firm and the broader market will underwrite, and the narrative has to cohere across the other three live topics rather than be assembled at the last minute.

The honest read: the ARR gap is large but on-trajectory if expansion and new logos land; the more fragile piece is the Net Retention story. NR>115% has to come from existing accounts expanding — which is exactly what the pricing-v2 per-entity model is designed to produce — and it has to be measurable and clean enough to survive diligence. Right now it's a narrative, not yet a substantiated metric.

Blocked on: instrumenting Net Retention properly (depends on the pricing-v2 metering work and Morgan's data tooling), and on the dependent topics resolving favourably — dp1 not churning, a VP Eng in seat for technical diligence, pricing-v2 producing demonstrable expansion.

## The narrative gap, decomposed

- **ARR €1.2M → €3M:** roughly 2.5x in ~18 months. Needs both new-logo growth (Priya's pipeline, cohort 2) and expansion within existing accounts. Losing dp1 (~15% of ARR) would set this back materially — the single largest single-point risk to the absolute number.
- **Net Retention >115%:** must be driven by expansion, not just retention. The per-entity pricing model (pricing-v2) is the mechanism — customers adding entities grows revenue per account. But NR isn't yet instrumented as a board-grade metric; a number we can't defend in diligence is worse than no number.
- **Team credibility:** technical diligence expects a stable senior engineering leader. The VP Eng hire (vp-eng-hire) is therefore not just an ops fix but a fundability input.

## How the dependent topics feed the raise

- **dp1-renewal:** retaining €180K ARR protects both the absolute ARR number and the reference-customer story; churning it damages both.
- **pricing-v2:** the per-entity model is the engine of the Net Retention claim; without it the >115% narrative has no mechanism.
- **vp-eng-hire:** a VP Eng in seat de-risks technical diligence and signals the team can scale post-raise.

## Timeline & history

- **2026-05** — Series B readiness framed against the €3M ARR + NR>115% bar in board prep; gap acknowledged as primarily a Net-Retention-evidence problem.
- **2026-05-26** — Sarah monthly 1:1: she flagged that her firm will want a defensible NR metric, not a projection, and that the expansion mechanism (pricing-v2) needs to be visibly working before kickoff.
- **2026-06-09** — pricing-v2 board cycle reaffirmed the per-entity model — the expansion engine the NR story depends on.
- **2026-06-15** — Series B narrative draft started; surfaced that NR instrumentation is the long pole and that the raise timing should follow proof, not precede it.

## Active threads

**Pending from Sarah Vyas:** a target investor shortlist and her read on what NR evidence and ARR trajectory the market will underwrite for a treasury-SaaS Series B in this window.

**Pending from Morgan:** Net Retention instrumentation — a board-grade, diligence-defensible expansion metric, dependent on the pricing-v2 metering work.

**Pending from self (Alex):** sequence the raise relative to proof points — set a kickoff backstop that follows a clean NR metric and a VP Eng in seat, not an arbitrary calendar date.

## Trigger conditions

- **dp1 churns:** ARR drops ~15% and the reference story weakens — re-baseline the entire raise narrative and the timing before approaching investors.
- **NR instrumentation confirms the trajectory is below >115%:** the raise narrative needs a different angle (e.g. logo growth or efficiency) rather than the expansion story; surface this to Sarah immediately.
- **pricing-v2 rollout stalls:** the expansion mechanism behind the NR claim is delayed — push the raise timing rather than pitch a mechanism that isn't live.
- **VP Eng hire fails to close before kickoff (see vp-eng-hire):** technical diligence weakens; either delay kickoff or pre-brief Sarah on the interim eng-leadership story.
- **Sarah signals her firm's appetite shifts:** the inside-track read changes the target list and timing — treat as a material input, not a footnote.

## Open questions

- **Can we instrument a defensible NR>115% metric before kickoff?** Needs Morgan (tooling) + pricing-v2 (per-entity expansion live). Blocked on the metering build.
- **What's the realistic ARR trajectory to €3M, and how much depends on retaining dp1 vs. new logos?** Needs Priya's pipeline view fed into the model; flagged here for the raise narrative.
- **What kickoff date follows the proof points rather than forcing them?** Needs Alex + Sarah, once NR evidence and the VP Eng hire firm up.

## Risk register

- **Risk A (active):** Net Retention can't be substantiated as a clean, diligence-grade metric in time — the central narrative claim is unprovable. Mitigation: prioritise NR instrumentation now; gate kickoff on a defensible metric, not a projection.
- **Risk B (active):** dp1 churn removes ~15% of ARR and the flagship reference simultaneously. Mitigation: see dp1-renewal; treat retention as a fundraise-critical objective, not just an account save.
- **Risk C:** Raise timing gets driven by runway pressure (18mo) rather than by proof points, forcing a pitch before the story coheres. Mitigation: monitor burn against the proof-point timeline; if they converge, raise a bridge conversation with Sarah early rather than pitching weak.
- **Risk D:** The three dependent topics resolve out of sequence (e.g. pricing live but dp1 churned), leaving an incoherent narrative. Mitigation: track all three against the raise timeline as one portfolio, not independently.
- ~~Risk E (closed):~~ Pricing model unsettled, leaving no expansion mechanism for the NR story. CLOSED 2026-05-18 (board adopted platform + per-entity; see pricing-v2).

## Deliverables

- (none yet — Series B narrative draft and investor materials to be produced under this topic as proof points firm up)
