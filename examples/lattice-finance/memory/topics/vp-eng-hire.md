---
slug: vp-eng-hire
status: active
owner: self
last_touch: 2026-06-12
key_stakeholders: [morgan-chen, sarah-vyas]
related_decisions:
  - memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md
related_briefs: []
related_knowledge:
  - knowledge/constitution.md
related_artifacts: []
related_topics: [dp1-renewal, series-b-prep]
---

# VP Engineering hire — relieving Morgan's bandwidth

## Status & current state

**Search is in finals: one credible finalist (Alina Crisan) after ~4 months, with Morgan running both eng and product and now also carrying the dp1 technical ask — the structural reason this hire exists.** Search opened February 2026 via a retained recruiter; the pipeline thinned through spring and the role now hangs on a single candidate.

The bottleneck is real and compounding: Morgan owns engineering, owns product direction, and is the only person who can scope the dp1 multi-entity reporting ask. The 2026-05-15 decision capped his dp1 bandwidth at 30% precisely because the other 70% can't safely move to anyone else yet. A VP Eng is the structural fix; until one signs, every other topic competes for the same person.

Current blocker: converting Alina from finalist to signed offer. She is strong on platform scaling and team-building but lighter on the regulated-fintech context Lattice operates in, which is the open question Morgan and Alex are working through before extending.

## Candidate state

Alina Crisan is the sole active finalist. Profile: scaled a payments-infra team from ~10 to ~40 engineers, strong on reliability and hiring, comfortable owning a roadmap alongside a CTO. Gaps under examination: depth in treasury/FX domain and in the compliance posture Lattice's customers demand. The deliberate question is whether that gap is coachable inside two quarters or a structural mismatch with the role's near-term load (SOC 2, multi-entity reporting, Series B technical diligence).

No second finalist is warm. Re-opening the search would add an estimated two-to-three months — directly material to Series B readiness, since technical diligence wants a stable senior eng leader in seat.

## Timeline & history

- **2026-02** — Search opened; retained recruiter engaged for VP Engineering.
- **2026-03 to 2026-04** — Pipeline built and narrowed; several candidates fell out on level or fit.
- **2026-05-15** — Morgan's dp1 bandwidth capped at 30% to protect core eng delivery — explicit acknowledgment the hire can't come soon enough. → `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md`
- **2026-06-12** — Alina Crisan confirmed as the lead finalist after final-round panel; domain-depth question flagged as the gate before an offer.

## Active threads

**Pending from Morgan:** technical deep-dive with Alina to assess whether the treasury/FX and compliance gap is coachable; verdict feeds the offer go/no-go.

**Pending from Sarah Vyas:** a reference call into her network on Alina (one shared connection from her payments-infra portfolio); also a read on how Series B investors weight a recent senior-eng hire in diligence.

**Pending from self (Alex):** decide offer scope (level, equity band, start ramp) and the fallback plan if the domain-depth verdict is negative.

## Trigger conditions

- **Morgan's deep-dive returns "gap not coachable":** do not extend; re-open the search and accept the Series B timing hit. Pre-stage the recruiter to restart within a week.
- **Alina receives a competing offer:** compress the decision to days; lean on Sarah's reference to de-risk fast rather than let the process lapse.
- **dp1 demo slips (2026-06-15) while the hire is unsigned:** Morgan's bandwidth crunch worsens — escalates the urgency of the offer decision, not the deliberation.
- **Series B kickoff date firms (see series-b-prep):** sets a hard backstop for having a VP Eng in seat before technical diligence.

## Open questions

- **Is Alina's domain gap coachable in two quarters?** Needs Morgan's deep-dive. Blocked on scheduling it.
- **What equity band closes her without breaking the option-pool model going into Series B?** Needs Alex + Sarah. Blocked on the offer-scope decision.
- **If we pass on Alina, what's the realistic re-open timeline?** Needs the recruiter. Blocked on whether we actually pass.

## Risk register

- **Risk A (active):** Single-candidate dependency — if Alina falls through, the search resets with material Series B timing cost. Mitigation: keep the recruiter warm; ask Sarah for one parallel intro now rather than after a no.
- **Risk B (active):** Domain-depth gap means a slow first two quarters exactly when SOC 2, dp1, and Series B diligence all land. Mitigation: scope a 90-day ramp with Morgan owning domain handoff; gate the offer on the deep-dive verdict.
- **Risk C:** Hiring to relieve Morgan but loading the new VP with the dp1 ask immediately just relocates the bottleneck. Mitigation: hold the dp1 ask on Morgan through the ramp; transition it only after the VP is established.
- ~~Risk D (closed):~~ Two finalists creating a bidding/sequencing problem — moot; only one finalist remains. CLOSED 2026-06-12.

## Deliverables

- `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md` — why Morgan's dp1 time is capped, the bandwidth case for this hire
