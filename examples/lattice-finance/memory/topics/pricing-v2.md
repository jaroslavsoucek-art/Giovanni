---
slug: pricing-v2
status: partially-resolved
owner: self
last_touch: 2026-06-09
key_stakeholders: [morgan-chen, sarah-vyas, priya-shah]
related_decisions:
  - memory/decisions/2026-05-18-pricing-v2-platform-fee.md
related_briefs: []
related_knowledge:
  - knowledge/constitution.md
related_artifacts: []
related_topics: [dp1-renewal, series-b-prep]
---

# Pricing v2 — per-seat to platform fee + per-entity

## Status & current state

**The model decision is made — moving off per-seat to a platform fee plus per-entity charge — but rollout mechanics (migration path, grandfathering, list pricing) are still open, hence partially-resolved.** The per-seat model never fit the buyer: treasury teams are small and the value scales with entities and bank connections consolidated, not headcount. The 2026-05-18 board decision ratified platform + per-entity as the canonical structure and aligns with the constitution principle "we charge platform + entity, never per-seat" (knowledge/constitution.md).

Resolved: the pricing shape. Open: how existing accounts migrate without a churn shock, what the published list looks like, and how Priya's in-flight pipeline gets repriced mid-cycle. dp1's renewal (see dp1-renewal) is the first live test of the new model — its proposal v0.2 already prices on platform + per-entity, ahead of a general rollout.

Blocked on: a migration playbook for existing accounts and a decision on grandfathering windows, both of which need Priya's pipeline data and Morgan's input on metering (per-entity billing requires entity-count instrumentation that isn't fully built).

## Model rationale

- **Buyer pattern:** the buyer is a finance/treasury lead, not a per-seat SaaS admin. Adding seats is friction; the value is entities and bank connections under management.
- **Expansion alignment:** per-entity revenue grows as the customer onboards more legal entities — the natural expansion vector — which is exactly the Net Retention motion Series B needs (see series-b-prep).
- **Partnership signal:** for an account like dp1, the platform-fee structure reads as a lower, fairer base, framing the renewal as principle rather than discount.

## Open rollout questions

- **Migration path:** do existing per-seat accounts move at renewal, on a fixed cutover date, or opt-in? Renewal-aligned is least disruptive but slowest to fully transition the book.
- **Grandfathering:** how long do legacy accounts keep per-seat economics if the new model would raise their cost? A window protects relationships but complicates revenue reporting for diligence.
- **List pricing:** what published platform fee and per-entity rate anchor new-logo deals so Priya isn't negotiating from scratch each time.
- **Metering:** per-entity billing needs reliable entity-count instrumentation — a build dependency on Morgan's team.

## Timeline & history

- **2026-04** — Per-seat friction surfaced across the pipeline; treasury buyers pushing back on seat-based quotes.
- **2026-05-09** — pricing-v2 added to the board agenda for the 2026-06-09 cycle; model options drafted (platform + per-entity vs. usage-based vs. tiered).
- **2026-05-18** — Board decision: adopt platform fee + per-entity as the canonical model. → `memory/decisions/2026-05-18-pricing-v2-platform-fee.md`
- **2026-06-04** — dp1 renewal proposal v0.2 priced on the new model (first live application, ahead of general rollout).
- **2026-06-09** — Board cycle reviewed rollout mechanics; model reaffirmed, migration/grandfathering left open pending Priya's pipeline analysis and Morgan's metering estimate.

## Active threads

**Pending from Priya:** pipeline repricing analysis — which in-flight deals shift under the new model, and the revenue delta — input to the migration playbook.

**Pending from Morgan:** estimate for per-entity metering instrumentation; gates how soon per-entity billing can go live for new accounts.

**Pending from Sarah Vyas:** view on how a mid-cycle pricing change reads in Series B diligence — does it strengthen the Net Retention story or raise a "revenue isn't stable" flag.

**Pending from self (Alex):** decide migration approach (renewal-aligned vs. cutover) and grandfathering window once Priya's and Morgan's inputs land.

## Trigger conditions

- **dp1 accepts the platform-fee proposal:** validates the model in the field; use it as the reference case to firm up list pricing and accelerate the general rollout.
- **Priya's repricing shows material revenue dip on migration:** revisit grandfathering length and cutover sequencing before any general announcement.
- **Morgan's metering estimate exceeds one quarter:** decouple new-logo platform pricing (shippable now) from per-entity automation (deferred), so Priya isn't blocked.
- **A second renewal lands before the playbook exists:** treat it like dp1 — bespoke proposal on the new model — but flag that ad-hoc repricing doesn't scale and forces the playbook decision.

## Open questions

- **Renewal-aligned migration or fixed cutover?** Needs Alex, informed by Priya's revenue delta. Blocked on the repricing analysis.
- **How long is the grandfathering window?** Needs Alex + Sarah. Blocked on the diligence-read and revenue impact.
- **Can per-entity billing be metered reliably at launch?** Needs Morgan. Blocked on the instrumentation estimate.

## Risk register

- **Risk A (active):** Mid-cycle migration triggers churn among legacy accounts whose cost rises. Mitigation: renewal-aligned migration plus a grandfathering window; never force a re-paper that worsens an account's economics without a value story.
- **Risk B (active):** Per-entity metering isn't built, so the model can't be billed accurately at rollout. Mitigation: ship platform-fee pricing for new logos first; defer per-entity automation until Morgan's instrumentation lands.
- **Risk C:** A mid-cycle pricing change reads as revenue instability in Series B diligence. Mitigation: frame it as deliberate Net-Retention engineering; have Sarah pressure-test the narrative before the raise.
- ~~Risk D (closed):~~ Board rejects platform + per-entity in favour of usage-based — model never settles. CLOSED 2026-05-18 (board adopted platform + per-entity).

## Deliverables

- `memory/decisions/2026-05-18-pricing-v2-platform-fee.md` — board decision adopting platform fee + per-entity
