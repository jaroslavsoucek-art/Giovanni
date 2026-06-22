# Lattice Finance Memory — live operational state

> **Last update:** 2026-05-21 — Design partner 1 renewal call set for 2026-06-04; new champion identified (CFO direct, not the operations contact who left).
> For recent context (last 7 days of changes) → `git log memory/CLAUDE_MEMORY.md`

---

## Purpose & context

Alex Park (co-founder & CEO) owns Lattice Finance end-to-end — treasury automation SaaS for €10–100M mid-market companies. AI CoS supports commercial, product strategy, fundraising, and board management.

- **Stage:** Series A (€5M raised 14 months ago), 15 employees, ARR €1.2M, 18 months net runway.
- **Series B narrative target:** €3M ARR + Net Retention >115% by month 24 post-Series-A.
- **Decision cadence:** weekly co-founder sync (Morgan), monthly Sarah Vyas 1:1, quarterly board.

### Key stakeholders

**Internal:** morgan-chen (co-founder & CTO), priya-shah (head of sales)
**Board:** sarah-vyas (lead VC, Series A), david-tannen (independent director), marcus-liu (board observer)
**Customers:** lattice-design-partner-1 (€180K ARR, churn risk), lattice-design-partner-2, lattice-design-partner-3
**Vendors:** compliance-vendor-x (SOC 2 audit), recruiter-firm-y (VP Eng search)

### Communication style

- Internal: direct, structured, decisions over discussion
- Board / VC: written async preferred (pre-reads before meetings); meeting time for debate not status
- Customer: warm but uncomplicated; Alex personally owns top 3 accounts

---

## Active blockers (May 2026)

1. **VP Engineering hire** — Morgan stretched across eng + product + design partner 1 tech ask; 4 months active search, 1 finalist (Alina Crisan) in final round, offer prep needed. → `topics/vp-eng-hire.md`
2. **SOC 2 Type II audit** — mid-audit with compliance-vendor-x; 2 design partners gate seat expansion on completion. Surprise findings possible.
3. **Design partner 1 renewal** — €180K ARR account, primary champion left for new role 2026-04-12; new buyer (CFO, identified 2026-05-19) reviewing renewal Q3. → `topics/dp1-renewal.md`
4. **Pricing model rework** — current per-seat doesn't fit treasury-team buyer pattern; needs platform fee + per-entity layer. Draft v1 ready, board input pending. → `topics/pricing-v2.md`
5. **Series B narrative gap** — need €3M ARR + NR >115% inflection story; current ARR trajectory €1.2M → €1.8M projected by Series B prep. Story-stretching candidates pending validation. → `topics/series-b-prep.md`

> Archived 2026-05-13: blocker #2 "DPA template for EU customers" (RESOLVED, → `memory/archive/2026-05.md`). Archived 2026-05-08: blocker #4 "Series A 12-month review with Sarah" (DONE, no action items, → `memory/archive/2026-05.md`).

---

## Canonical facts (pointer to constitution)

Detail in `knowledge/constitution.md`. Top-of-mind facts:

- **Pricing principle:** platform fee + per-entity, never per-seat. Codified 2026-03-04 after pricing-v2 first-pass debate.
- **ICP:** companies with dedicated finance team (CFO + ≥1 treasury/AP analyst). No self-serve sub-€20K ACV.
- **Compliance posture:** SOC 2 Type II is non-negotiable for >€100K ACV deals. ISO 27001 deferred Series B.
- **Data residency:** EU customers on EU AWS region (Frankfurt). No cross-region by default.
- **Hiring filter:** all senior hires (E5+ / lead+) go through Morgan AND Alex; junior IC hires Morgan solo.

---

## This week (2026-05-21 to 2026-05-27)

- **Alina Crisan (VP Eng finalist) reference call 1** (2026-05-23) — Alex + Morgan, ex-CTO at `<former-employer>`. → `briefs/2026-05-23_alina-reference-1.md`
- **Sarah Vyas monthly 1:1** (2026-05-26) — Series B narrative draft v0.3 review + design partner 1 status sync. → `briefs/2026-05-26_sarah-monthly.md`
- **Design partner 1 CFO intro call** (2026-05-27) — Alex + Priya, first contact with new champion since predecessor departure. → `briefs/2026-05-27_dp1-cfo-intro.md`
- **Pricing v2 board pre-read** — distribute by 2026-05-26, asynchronous feedback before next board.
- **SOC 2 mid-audit findings review** — compliance-vendor-x to send draft findings by 2026-05-25.

---

## On the horizon (next 2-4 weeks)

### t+1 to t+2 weeks

- **VP Eng offer extension** — assuming reference calls go well, target offer 2026-06-02.
- **Design partner 1 renewal proposal** — pricing + terms draft due to CFO by 2026-06-04.
- **Pricing v2 board review** (2026-06-09 board meeting) — formal vote on platform-fee model.
- **SOC 2 final report** — expected 2026-06-13, gates 2 design partner seat expansions.

### Stakeholder profile bootstrap pending

- **Alina Crisan** (VP Eng finalist) — bootstrap before offer extension if she signs
- **Design partner 1 new CFO contact** (Karim Solanki, tracked inside `stakeholders/lattice-design-partner-1.md`) — deepen after 2026-05-27 intro
- **Cohort 2 prospects** — Priya pipeline has 3 design-partner-tier prospects warming; flag for profile after first call

### Active sub-actions (no hard deadline)

- **Series B target list research** — → `topics/series-b-prep.md`
- **Pricing migration plan for existing customers** — → `topics/pricing-v2.md`
- **Morgan bandwidth recovery** — VP Eng hire is the unlock; secondary lever is contractor for design partner 1 tech ask

---

## Watch list (monitor, no action yet)

- **Treasury automation competitor X funding round** — rumored late-stage Series C (>$50M). Would expand their sales motion downmarket. Confirm via TechCrunch/Pitchbook by end of month.
- **EU AI Act enforcement guidance** — Lattice uses LLM for cash flow categorization; if model risk classification tightens, may need compliance review.
- **Bank API consolidation (Open Banking 2.0)** — UK FCA consultation paper Q3 2026. Could change connector cost structure.
- **Sarah's fund Q2 LP letter** — annually her LP relations affect her bandwidth; if Q2 letter shows pressure, expect more board scrutiny on burn.

---

## Open questions ([TBD])

- **[TBD: Series B target valuation range]** — needs Alex + Morgan alignment. Blocked on pricing-v2 board outcome (changes ARR multiple defensibility).
- **[TBD: DK/SE expansion timing]** — needs Priya pipeline data. Blocked on cohort 2 prospect signal (3 warming, need conversion confirmation).
- **[TBD: VP Eng comp package ceiling]** — needs board comp committee input. Sarah signaled flexibility but no number.

---

## Architectural / operating principles

- **Decision-log before execute:** any decision changing pricing, hiring filter, or product scope gets a `memory/decisions/<...>.md` record before execution.
- **Adversarial review on customer-facing comms:** all renewal proposals, pricing announcements, board updates go through `/review` before send.
- **No silent customer escalations:** if a customer touches Sarah or any board member directly, Alex flagged within 24h.
- **Bandwidth budget:** Morgan max 60% on customer-facing tech work; above 60% triggers VP Eng or contractor decision.

---

## Tools & resources

- **Asana:** Project ID `1209876543210000` ("Lattice 2026"), workspace gid `412345678901234`.
- **Slack:** primary channel `#strategy-private` for Alex + Morgan; `#board-async` for board updates.
- **HubSpot:** Priya's pipeline source. CRM export weekly Mondays via webhook.
- **Mercury Bank API:** payments / payouts integration. Rate limit 1000 req/min.
- **GitHub:** `lattice-finance/` org, main monorepo `lattice-monorepo`.

---

## System hygiene

- **Monthly memory audit** — last: 2026-06-08. Next due ~2026-07-13 (cadence 35d).
- **Light prune** — last: 2026-06-16. Next due ~2026-06-30 (cadence 14d).
- **Watch scan** — last: 2026-06-15. Next due ~2026-06-22 (cadence 7d).
