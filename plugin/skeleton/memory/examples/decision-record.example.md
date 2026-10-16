---
date: 2026-05-15
situation: dp1-tech-ask-scope-cap
status: resolved
review_path: open
related_topics: [dp1-renewal, vp-eng-hire]
related_stakeholders: [morgan-chen, lattice-design-partner-1]
---

# Decision: Cap Morgan's bandwidth on design partner 1 technical ask at 30%

**Date:** 2026-05-15
**Status:** resolved (tactical) · review-cadence-open
**Source:** Alex + Morgan co-founder sync (in-person, office), 2026-05-15 14:00
**Related:** [topics/dp1-renewal.md](../topics/dp1-renewal.md), [topics/vp-eng-hire.md](../topics/vp-eng-hire.md)

## Decision

Cap Morgan's direct engineering time on the design partner 1 multi-entity reporting feature at **30% of his weekly capacity**, no more, until the VP Eng hire closes. Any work beyond 30% gets explicitly deferred or contracted out. Existing 2026-06-15 demo target stays but is now conditional on staying within the cap; if cap binds, slip the demo, do not stretch Morgan.

## Reasoning

- Morgan currently sits at ~70% on dp1 tech ask (per his own time log 2026-05-12 retro). At 70%, he is materially absent from the rest of the eng org — three other deliverables (Stripe webhook hardening, audit-log export, EU AWS region migration) are slipping.
- Other engineers (8 total) report Morgan-blocked on architecture decisions ≥2x per week. Each Morgan-blocked engineer-day costs ~€600. At current rate this is ~€36K/quarter in soft cost, not counting morale.
- VP Eng hire (Alina Crisan finalist) targeted offer 2026-06-02. Cap holds until VP Eng signs and is onboarded (target effective date 2026-07-15). After that, dp1 tech ask gets reassigned to the new VP's team.
- Risk of NOT capping: Morgan ships dp1 demo on time, but other deliverables slip → dp2 / dp3 churn risk emerges → no net improvement, just shifted exposure.
- Risk of capping: dp1 demo slips past 2026-06-15 target → dp1 renewal proposal has weaker concrete value demonstration → renewal probability drops. This is the explicit trade-off being accepted.

## Alternatives considered

- **Don't cap (status quo):** rejected. Pattern is unsustainable for 6+ more weeks until VP Eng onboarded; eng org degrading.
- **Contractor bridge for dp1 work specifically:** deferred, not rejected. Contractor with multi-entity reporting domain expertise is hard to source on 4-6 week timeline (recruiter-firm-y estimate: 8-10 weeks for senior contract eng). If Morgan misses the 2026-06-15 demo target despite cap, escalate this path.
- **Push dp1 renewal date out:** rejected. Renewal date is contractual (2026-09-30); cannot unilaterally move it.
- **Tell dp1 the feature slips and propose alternative value demonstration:** holds as fallback if 2026-06-15 demo materially misses. Requires Karim Solanki relationship maturity, which we don't have yet pre-2026-05-27 first call.

## Implications

### Operational

- Morgan publishes his weekly capacity budget in `#eng-leads` every Monday. Above 30% on dp1 tech ask = immediate Alex+Morgan triage.
- dp1 multi-entity reporting MVP demo-ready 2026-06-15 stays as soft target; deferred to 2026-06-29 if cap binds.
- Other deliverables (Stripe webhook, audit-log export, EU AWS migration) reclaim Morgan's attention on the freed 40% capacity. Audit-log export is critical-path for SOC 2 Type II audit — un-blocking this is the highest-leverage win from the cap.

### Stakeholder

- **Morgan:** sign-off received in 2026-05-15 sync ("I'd been hoping you'd push this earlier"). Co-founder alignment confirmed.
- **dp1 / Karim Solanki:** NOT informed of internal capacity decision. He sees feature timeline as committed; we adjust internally without altering external commitment unless cap binds at 2026-06-15.
- **VP Eng candidate (Alina Crisan):** mentioned during 2026-05-23 reference call that dp1 multi-entity work is "high priority for new VP from day one" — sets expectation honestly.

### Technical

- No architecture changes triggered by this decision. Pure capacity allocation.
- Multi-entity reporting feature design (Morgan's spec doc 2026-04-30) stays as-is. Cap affects build velocity, not direction.

### Commercial

- dp1 renewal probability shifts modestly — pricing-v2 board outcome 2026-06-09 is a larger lever than this cap.
- No commitment changes to dp1 contract; existing 2025-08-12 SOW unchanged.

## Trigger conditions (re-evaluate)

- **2026-06-15 demo missed by >2 weeks:** escalate contractor bridge path; re-evaluate cap (raise to 40%? or accept slip and find alternative dp1 value demonstration?).
- **VP Eng hire closes or fails:** if signs, cap auto-removes effective VP onboarding date. If hire falls through, cap stays but contractor bridge becomes priority-1.
- **Morgan reports >50% time on dp1 across two consecutive weeks:** cap is being violated; reset enforcement (this is the cap-leakage failure mode).
- **dp1 churn signal accelerates (Karim cools post-2026-05-27 call):** reopens trade-off — may need to break cap to ship demo earlier as save-the-account move.

## Open follow-ups

- **Morgan weekly capacity report in `#eng-leads`** — starts 2026-05-19.
- **Contractor sourcing exploration with recruiter-firm-y** — Priya owns first contact, by 2026-05-29 (parallel to VP Eng search, lighter touch).
- **dp1 demo content review** — Alex + Morgan to confirm 2026-06-15 scope is actually a sufficient value demonstration, not just feature presence. By 2026-06-01.

## Closed follow-ups

- ~~Discuss with Morgan whether to inform dp1 of capacity constraint~~ — closed 2026-05-15 (Morgan + Alex agree: do not inform; manage internally).
- ~~Sarah Vyas pre-notification~~ — closed 2026-05-15 (not material enough; cover in 2026-05-26 monthly 1:1 if relevant).

## Provenance

- **Source:** Co-founder sync (Alex + Morgan), 2026-05-15 14:00–14:45, Lattice office (in-person).
- **Channel:** Verbal decision, Alex documented post-sync.
- **Attendees / participants:** Alex Park, Morgan Chen.
- **External reference:** Morgan's time log 2026-05-12 retro (private Notion doc `lattice/eng-leads/morgan-time-2026-05-12`).
