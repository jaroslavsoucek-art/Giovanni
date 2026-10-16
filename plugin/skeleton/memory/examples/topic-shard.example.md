---
slug: dp1-renewal
status: active
owner: self
last_touch: 2026-05-21
key_stakeholders: [lattice-design-partner-1, sarah-vyas, priya-shah, morgan-chen]
related_decisions:
  - memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md
related_briefs:
  - memory/briefs/2026-05-27_dp1-cfo-intro.md
  - memory/briefs/2026-05-26_sarah-monthly.md
related_knowledge:
  - knowledge/lattice_operating_principles.md
related_artifacts:
  - deliverables/dp1-renewal-proposal-draft-v0.2.docx
related_topics: [pricing-v2, vp-eng-hire]
---

# Design Partner 1 — Q3 renewal at risk

## Status & current state

**€180K ARR account at material churn risk after primary champion (VP Finance Operations) departed 2026-04-12.** New champion identified 2026-05-19 as their CFO (Karim Solanki) — bypasses the operations layer where the previous relationship lived. First direct call set 2026-05-27. Renewal decision expected late Q3 (renewal date 2026-09-30).

Risk profile shifted from "rebuild relationship with operations-level successor" (3 weeks ago) to "land CEO-level value story with CFO who has no prior context". Materially harder, materially shorter timeline.

Morgan's bandwidth on the design partner 1 technical ask (custom multi-entity reporting view) is now also a bandwidth lever — if we ship the ask by 2026-08 we have a concrete value demonstration; if we slip past renewal, churn probability rises.

## Risk profile shift (timeline)

| Date | State | Implications |
|---|---|---|
| 2026-03-15 | Champion fully engaged, renewal trajectory positive | Default-renew assumption |
| 2026-04-12 | Champion (VP Fin Ops) announces departure | Risk B (relationship dependency) materializes |
| 2026-04-26 | Champion's last day; no warm-handoff to successor at ops level | Search for new champion begins |
| 2026-05-19 | Discovery: account in transition — ops layer thin, CFO (Karim) re-evaluating treasury stack | Pivot to CFO-level conversation |
| 2026-05-27 | First Karim Solanki call (Alex + Priya) | First-impression weight high |

## Strategic framing

### Why this account matters disproportionately

- €180K ARR = 15% of total ARR. Loss would drop ARR to €1.02M, materially affecting Series B narrative.
- Design partner 1 is the **largest treasury-stack reference** Lattice has. Cohort 2 prospects (3 in pipeline) reference-check against it.
- Karim's CFO peer network includes 2 prospects currently in Priya's pipeline — relationship outcome here ripples downstream.

### What Karim likely needs to hear

- **Quantified ROI** since contract start: Lattice consolidated 7 bank connections, eliminated ~12 hours/week manual cash forecasting effort, caught one €40K FX exposure prior to settlement.
- **Roadmap fit** with his Q4 priorities: multi-entity reporting (in progress), bank-fee analysis (Q4 build), audit-trail export (existing feature he may not have seen).
- **Pricing fairness** under platform-fee model (pricing-v2): under new model, account moves from €15K/mo per-seat to roughly €12K/mo platform + per-entity — Lattice-side reduction signaling partnership posture. (Validate with pricing-v2 board first; do not commit pre-vote.)

### What NOT to lead with

- Series B narrative — Karim has no incentive to support a fundraise; framing renewal as "we need this for our raise" is anti-pattern.
- VP Eng hire — internal team change doesn't reassure CFO of stability; arguably the opposite.
- Pricing-v2 details before board vote 2026-06-09 — committing prematurely creates board-side friction.

## Timeline & history

- **2025-08-12** — Initial contract signed, 18-month term, €180K ARR, primary contact = Diane Martens (VP Finance Operations).
- **2026-03-15** — Q1 business review with Diane. Trajectory positive, NPS 9, expansion conversation initiated for Q4 (3 additional entities).
- **2026-04-12** — Diane announces departure to <new-role>. Lattice flagged immediately as Risk B in topic shard.
- **2026-04-26** — Diane's last day. No designated successor at ops level. Account temporarily owned by Karim (CFO) directly.
- **2026-05-08** — Priya's outbound to Karim returned with auto-reply "evaluating treasury vendors Q3". Risk B escalated to Risk A (active churn risk).
- **2026-05-15** — Decision: cap Morgan's bandwidth on the dp1 multi-entity reporting ask at 30% to avoid Morgan-burnout-driven churn elsewhere. → `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md`
- **2026-05-19** — Discovery (via Priya's outbound to Karim's EA): Karim open to renewal conversation but "wants to understand the stack value before continuing". Translation: he's evaluating churning. First call set 2026-05-27.
- **2026-05-21** — Sarah Vyas flagged in monthly 1:1 prep: "dp1 status sync" added as agenda item.

## Active threads

**Pending from Karim Solanki:** acknowledgment of 2026-05-27 call brief (Priya sent agenda 2026-05-22).

**Pending from Morgan:** multi-entity reporting feature MVP demo-ready by 2026-06-15 (capped at 30% bandwidth per 2026-05-15 decision).

**Pending from Priya:** account health diagnostic (usage data, login frequency, support ticket trend Q1-Q2 2026) by 2026-05-25 — input to 2026-05-27 call narrative.

**Pending from self (Alex):** renewal proposal draft v1 by 2026-06-04 — needs Sarah feedback on pricing positioning (2026-05-26 1:1) + pricing-v2 board outcome (2026-06-09).

## Trigger conditions

- **Karim signals churn intent (any form):** escalate to Sarah for board-level warm intro to her network for parallel exec sponsor. Decision threshold: ≤30 days before renewal date with no concrete renewal motion.
- **Morgan slips multi-entity reporting MVP date:** re-evaluate contractor (decision 2026-05-15 deferred but available). Trigger: 2026-06-15 demo not ready or quality below internal bar.
- **Pricing-v2 board vote fails / delays:** dp1 proposal stays on per-seat pricing for this renewal cycle. Materially weaker negotiation lever.
- **Cohort 2 prospect reference-checks dp1:** Karim's response shapes 2 active sales opportunities. Coordinate Priya outreach so reference timing doesn't precede the 2026-05-27 first call.

## Open questions

- **What is Karim's actual treasury stack evaluation framework?** Needs discovery during 2026-05-27 call. Blocked on call happening.
- **Are there other Lattice users inside dp1 we haven't engaged?** Needs Priya audit of account user logins — sometimes mid-level analysts are champions in waiting.
- **What did Diane tell Karim about Lattice during transition?** Unknowable directly; proxy = call posture. Adjust based on observed warmth/coolness 2026-05-27.

## Risk register

- **Risk A (active):** Karim decides Lattice doesn't justify €180K/year and churns. Mitigation: 2026-05-27 call lands quantified ROI; renewal proposal under pricing-v2 reduces effective cost.
- **Risk B (active):** Morgan can't ship multi-entity reporting by 2026-06-15 demo target. Mitigation: contractor-bridge decision available (deferred 2026-05-15); re-evaluate weekly.
- **Risk C:** Karim asks for pricing-v2 details before board vote 2026-06-09. Mitigation: hold position "we're updating pricing model, can share specifics post-board mid-June"; do not pre-commit.
- **Risk D:** Cohort 2 prospect reference-checks dp1 and Karim gives lukewarm response. Mitigation: time outreach so first call (2026-05-27) precedes any reference call; brief Priya to delay any reference asks until 2026-06-15+.
- ~~Risk E (closed):~~ Diane returns to dp1 — unlikely-but-impactful per branch-out 2026-05-12. CLOSED 2026-05-19 (confirmed she started new role).

## Deliverables

- `deliverables/dp1-renewal-proposal-draft-v0.2.docx` — pricing options, ROI summary, roadmap fit
- `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md` — Morgan bandwidth cap rationale
- `memory/briefs/2026-05-27_dp1-cfo-intro.md` — first Karim call brief
- `memory/briefs/2026-05-26_sarah-monthly.md` — Sarah 1:1 brief (dp1 status sync item)
