# Test Domain — Synthetic 2nd Domain for Pseudo-Fork Validation

> Used to validate that Giovanni's schemas are genuinely generic, not implicitly shaped by the source domain. When a specialist architect produces a template, the next step is filling it for this domain. If the template forces source-domain-shaped thinking, the schema needs redesign.

## Profile

**Founder:** Alex Park (synthetic — not a real person)

**Company:** Lattice Finance — B2B treasury automation SaaS, helping mid-market companies (€10–100M revenue) consolidate cash forecasting, bank connectivity, and FX exposure across multiple bank accounts and entities.

**Stage:**
- Series A, raised €5M 14 months ago
- 15 employees (8 eng, 2 product, 2 sales, 2 ops, 1 design)
- ARR €1.2M (ramped from €200K at Series A)
- 18 months net runway at current burn

**Alex's role:** Co-founder & CEO. Owns commercial, product strategy, fundraising, board.

## Key stakeholders

| Slug | Role | Relationship |
|---|---|---|
| `morgan-chen` | Co-founder & CTO | 50/50 split, six years working together, decision peer |
| `sarah-vyas` | Lead VC partner (Series A) | Series A lead, board director, monthly 1:1 |
| `david-tannen` | Independent board director | Industry vet, ex-CFO public fintech, quarterly board |
| `marcus-liu` | Board observer (smaller fund) | Quarterly board, occasional intros |
| `priya-shah` | Head of Sales (hired 6 months ago) | First commercial leader, direct report |
| `lattice-design-partner-1` | Design partner (one of 3) | Largest customer, €180K ARR, churn risk |
| `lattice-design-partner-2` | Design partner | €120K ARR, healthy |
| `lattice-design-partner-3` | Design partner | €60K ARR, scaling slowly |
| `compliance-vendor-x` | SOC 2 audit firm | Active engagement, mid-audit |
| `recruiter-firm-y` | Eng recruiter retained | Active for VP Eng search |

## Active blockers (real domain-shaped pressure)

1. **Series B prep** — 12 months out, need to ship €3M ARR + Net Retention >115% to be fundable
2. **SOC 2 Type II compliance** — required by 2 of 3 design partners to expand seat count; mid-audit, surprises possible
3. **VP Engineering hire** — Morgan stretched, need senior eng leader; 4 months active search, 1 finalist
4. **Design partner 1 churn risk** — €180K ARR account, primary champion left for new role; new buyer reviewing renewal Q3
5. **Pricing model rework** — current per-seat doesn't fit treasury-team buyer pattern; needs platform fee + per-entity layer
6. **Co-founder bandwidth** — Morgan running both eng + product, design partner 1's tech ask is consuming his cycles, not scalable

## Horizon

- **t+1 quarter:** SOC 2 Type II completion, VP Eng signed, design partner 1 renewal confirmed or churned, pricing v2 ready
- **t+2 quarters:** Pricing v2 rolled, 2 new design partners signed, ARR €1.8M trajectory, Series B narrative starts forming
- **t+12 months:** Series B raise targeting €15–25M at €80–150M valuation

## What this domain exercises in Giovanni schemas

- **Memory layering:** active blockers (L1), per-blocker shards (L2), decision records (L3)
- **Stakeholder profiles:** co-founder (peer), VC partners (asymmetric power), customers (transactional with relationship overlay), vendor (transactional only)
- **Decision logs:** pricing model decisions, hiring decisions, fundraise timing decisions
- **Briefs:** board meetings, VC 1:1s, design partner renewals, candidate finals
- **Predictive layer:** what does Sarah (VC) do if SOC 2 slips? What does Morgan do if VP Eng hire fails to close?
- **Calibration:** Alex's prediction track record on board reactions, customer renewals
- **Adversarial review:** every fundraise narrative draft, every pricing change announcement
- **Ústava equivalent:** Lattice's own operating principles (e.g. "we don't sell to companies without finance team", "we charge platform + entity, never per-seat")

## How to use this doc

When a Giovanni specialist architect produces a template:
1. Read the template.
2. Fill it for Alex / Lattice Finance using the context above.
3. Note where the template forces source-domain-shaped thinking (e.g. assumes "country-specific config" as core concept when it's not generic).
4. Iterate the architect prompt and re-generate.

The synthetic domain is intentionally **different in shape** from the source (different industry, different stakeholder dynamics, different time horizon, different stage) to stress-test genericity.
