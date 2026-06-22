---
slug: dp1-renewal
status: active
owner: self
last_touch: 2026-06-04
key_stakeholders: [lattice-design-partner-1, sarah-vyas, priya-shah, morgan-chen]
related_decisions:
  - memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md
related_briefs:
  - memory/briefs/2026-05-27_dp1-cfo-intro.md
  - memory/briefs/2026-05-26_sarah-monthly.md
related_knowledge:
  - knowledge/constitution.md
related_artifacts:
  - deliverables/dp1-renewal-proposal-draft-v0.2.docx
related_topics: [pricing-v2, vp-eng-hire, series-b-prep]
---

# Design Partner 1 — Q3 renewal at risk

## Status & current state

**€180K ARR account at material churn risk after primary champion (VP Finance Operations) departed 2026-04-12.** New buyer-of-record is the design partner's CFO, Karim Solanki — identified 2026-05-19, bypassing the operations layer where the previous relationship lived. First direct call held 2026-05-27. Renewal decision expected late Q3 (renewal date 2026-09-30).

Post-call (2026-05-27) read: Karim is transactional but not hostile — he asked for a quantified value case and roadmap alignment, not a discount. Risk profile is now "land CFO-level value story" rather than "rebuild an operations relationship". Renewal proposal v0.2 went out 2026-06-04 incorporating his asks; awaiting his finance team's review.

Morgan's bandwidth on the design partner's technical ask (custom multi-entity reporting view) remains a renewal lever — MVP demo target is 2026-06-15, capped at 30% of Morgan's time per the 2026-05-15 decision. If we ship a credible demo before the proposal is decided, we have a concrete value demonstration; if it slips, the proposal leans entirely on the historical ROI narrative.

## Strategic framing

### Why this account matters disproportionately

- €180K ARR ≈ 15% of total ARR. Loss would drop ARR to ~€1.02M, materially weakening the Series B narrative (see series-b-prep).
- Largest treasury-stack reference Lattice has. Cohort 2 prospects (3 in pipeline) reference-check against it.
- Karim's CFO peer network overlaps 2 prospects currently in Priya's pipeline — the relationship outcome ripples downstream.

### What Karim needs to hear (validated on 2026-05-27 call)

- **Quantified ROI** since contract start: consolidated 7 bank connections, eliminated ~12 hours/week of manual cash forecasting, caught one €40K FX exposure before settlement.
- **Roadmap fit** with his Q4 priorities: multi-entity reporting (in progress), bank-fee analysis (Q4 build), audit-trail export (existing, he hadn't seen it).
- **Pricing fairness** under the platform-fee model (pricing-v2): per the 2026-05-18 board decision, the account moves off per-seat toward platform + per-entity. Net effect is a Lattice-side reduction signalling partnership posture — now shareable post-vote.

### What NOT to lead with

- Series B narrative — Karim has no incentive to support a fundraise; framing the renewal as "we need this for our raise" is an anti-pattern.
- VP Eng hire — an internal team change doesn't reassure a CFO of stability.
- Anything that reads as desperation. The constitution principle "we charge platform + entity, never per-seat" frames the pricing shift as principle, not concession (see knowledge/constitution.md).

## Timeline & history

- **2025-08-12** — Initial contract signed, 18-month term, €180K ARR, primary contact = VP Finance Operations.
- **2026-03-15** — Q1 business review. Trajectory positive, NPS 9, Q4 expansion conversation (3 additional entities) initiated.
- **2026-04-12** — Champion announces departure. Flagged immediately as Risk B (relationship dependency).
- **2026-04-26** — Champion's last day. No designated successor at ops level; account owned by Karim (CFO) directly.
- **2026-05-08** — Priya's outbound to Karim returns "evaluating treasury vendors Q3". Risk B escalated to Risk A (active churn risk).
- **2026-05-15** — Decision: cap Morgan's bandwidth on the multi-entity reporting ask at 30%. → `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md`
- **2026-05-19** — Discovery via Karim's EA: open to a renewal conversation but "wants to understand the stack value first". First call set 2026-05-27.
- **2026-05-26** — Sarah Vyas monthly 1:1: dp1 status sync; she offered a board-network exec intro if churn signals harden.
- **2026-05-27** — First Karim Solanki call (Alex + Priya). Posture neutral-to-warm; asked for quantified value case + roadmap. → `memory/briefs/2026-05-27_dp1-cfo-intro.md`
- **2026-06-04** — Renewal proposal v0.2 sent (ROI summary, roadmap fit, platform-fee pricing). Awaiting Karim's finance-team review.

## Active threads

**Pending from Karim Solanki:** finance-team review of proposal v0.2 (sent 2026-06-04); expected response window 2–3 weeks.

**Pending from Morgan:** multi-entity reporting MVP demo-ready by 2026-06-15 (30% bandwidth cap per 2026-05-15 decision).

**Pending from Priya:** schedule a roadmap-walkthrough working session with Karim's team contingent on proposal traction; hold any cohort-2 reference asks until the demo lands.

**Pending from self (Alex):** confirm with Sarah whether to pre-position a board-network exec intro now or hold it as a churn-trigger lever.

## Trigger conditions

- **Karim signals churn intent (any form):** escalate to Sarah for a board-level warm intro to a parallel exec sponsor. Threshold: ≤30 days before renewal with no concrete renewal motion.
- **Morgan slips the multi-entity reporting MVP:** re-open the contractor-bridge option (deferred 2026-05-15). Trigger: 2026-06-15 demo not ready or below internal quality bar.
- **Proposal v0.2 gets a price-only counter:** treat as a signal Karim doesn't yet value the stack; re-anchor on ROI before negotiating number.
- **Cohort 2 prospect reference-checks dp1:** Karim's response shapes 2 active opportunities. Sequence outreach so no reference call precedes the 2026-06-15 demo.

## Open questions

- **What is Karim's actual treasury-stack evaluation framework?** Partly surfaced on 2026-05-27; needs confirmation in the roadmap working session. Needs Priya.
- **Are there other Lattice users inside dp1 we haven't engaged?** Needs Priya's audit of account user logins — mid-level analysts are sometimes champions-in-waiting.
- **Will the platform-fee proposal clear Karim's procurement without re-papering the contract?** Needs legal review of the existing term against the new pricing structure.

## Risk register

- **Risk A (active):** Karim decides Lattice doesn't justify €180K/year and churns. Mitigation: proposal v0.2 lands quantified ROI; platform-fee pricing reduces effective cost.
- **Risk B (active):** Morgan can't ship the multi-entity reporting demo by 2026-06-15. Mitigation: contractor-bridge option available (deferred 2026-05-15); re-evaluate weekly.
- **Risk C:** Proposal stalls in Karim's procurement over re-papering. Mitigation: pre-empt with legal review of the existing term; offer an addendum rather than a new MSA.
- **Risk D:** Cohort 2 prospect reference-checks dp1 before the demo and gets a lukewarm read. Mitigation: hold reference asks until 2026-06-15+; brief Priya.
- ~~Risk E (closed):~~ Departed champion returns to dp1 — unlikely-but-impactful per branch-out 2026-05-12. CLOSED 2026-05-19 (confirmed she started a new role).

## Deliverables

- `deliverables/dp1-renewal-proposal-draft-v0.2.docx` — pricing options, ROI summary, roadmap fit
- `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md` — Morgan bandwidth cap rationale
- `memory/briefs/2026-05-27_dp1-cfo-intro.md` — first Karim call brief
- `memory/briefs/2026-05-26_sarah-monthly.md` — Sarah 1:1 brief (dp1 status sync item)
