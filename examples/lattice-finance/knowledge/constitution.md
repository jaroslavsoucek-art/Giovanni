# Lattice Finance — Living Constitution

<!--
This is the canonical single-source-of-truth document for Lattice Finance.
When this file disagrees with anything else in the repo (memory, briefs,
drafts), this file wins.

‼ Editing rules (binding — see knowledge/README.md "How to amend safely"):

  1. Every amendment uses commit prefix `docs(constitution):` or
     `decision: <slug>` (when the amendment is the artifact of a recorded
     decision).
  2. Supersessions never delete prior content — rename the section header
     to `<old> (SUPERSEDED → §<new-anchor>)` and leave a one-paragraph stub.
  3. Cite the decision record (`Source: memory/decisions/<file>`) at the
     bottom of any section established by a decision.
  4. Update the section's last-touch date.
  5. Update the table of contents if section IDs changed.
  6. Sections state CURRENT truth only — no inline "[changed YYYY-MM-DD per
     decision X]" trails. History lives in git, the decision record, and the
     Superseded-positions stub.

The `post-constitution-edit-check.sh` hook flags missing supersedes-pointers,
missing commit-message prefix, and detected domain-leak patterns.
-->

> **Version:** v1.0
> **Last review:** 2026-06-22
> **Status:** LIVING

## Document status legend

| Badge | Meaning |
|---|---|
| `RESOLVED` | Position settled; should hold unless a `trigger condition` from the decision record fires. |
| `OPEN` | Active question; section captures the current best understanding, expected to change. |
| `SUPERSEDED → §<anchor>` | Position retired; follow the pointer to the active section. |
| `DRAFT` | Section under construction; not yet authoritative. |

---

## Table of contents

<!--
Hand-maintained list of section anchors. If you rename a section, update
the anchor here.
-->

1. [Operating principles](#operating-principles) — `RESOLVED`
2. [Adversarial review](#adversarial-review) — `RESOLVED` (binding policy)
3. [Daily digest — operational tempo](#daily-digest) — `RESOLVED` (binding policy)
4. [External write gate](#external-write-gate) — `RESOLVED` (binding policy)
5. [Strategic posture](#strategic-posture) — `OPEN` / `RESOLVED` per section
6. [Stakeholder model](#stakeholder-model) — `RESOLVED`
7. [Architecture / how the work works](#architecture) — mix of `RESOLVED` + `OPEN`
8. [Commercial model](#commercial-model) — `RESOLVED` / `OPEN`
9. [Compliance & legal posture](#compliance-legal-posture) — `RESOLVED` / `OPEN`
10. [Active blockers (canonical)](#active-blockers-canonical) — `OPEN`
11. [Superseded positions](#superseded-positions) — historical record

---

## Operating principles {#operating-principles}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22
> _Operating principles are the load-bearing values Lattice is built on. They are durable across quarters and amended sparingly — typically only when a fundamental assumption is challenged._

### Principle 1 — pricing is platform + entity, never per-seat {#principle-pricing-shape}

**FACT (source: `memory/decisions/2026-05-18-pricing-v2-platform-fee.md`):** Lattice prices on a platform fee plus a per-entity layer. Per-seat pricing is forbidden for all new deals; existing design partners are grandfathered until renewal.

**REASONING:** The buyer is a treasury team, not a seat-growth org. Seat count stays flat while entity count grows with the customer's legal structure — so per-seat pricing decouples our revenue from the value we deliver and caps expansion. Platform + entity ties revenue to the dimension that actually scales (entities, bank connections, FX exposure), which is the Net-Retention engine the Series B narrative depends on. — Source: `memory/decisions/2026-05-18-pricing-v2-platform-fee.md`

**IMPLIES:**

- Quotes lead with a platform fee + per-entity rate. Seat counts never appear on a price line.
- Expansion revenue is modeled on entity growth and connection growth, not headcount.
- Renewal proposals migrate grandfathered per-seat customers onto platform + entity at the renewal boundary, not mid-term.

**ANTI-PATTERNS:**

- Quoting or discounting on a per-seat basis to close a deal faster.
- Introducing a "per-user add-on" that re-creates seat pricing under another name.
- Migrating a grandfathered customer mid-contract instead of at renewal.

### Principle 2 — ICP requires a finance team; no self-serve sub-€20K ACV {#principle-icp}

**FACT:** Lattice sells only to companies with a dedicated finance team (CFO plus at least one treasury/AP analyst). There is no self-serve motion and no deal below €20K ACV.

**REASONING:** Treasury automation requires a buyer who owns cash forecasting, bank connectivity, and FX exposure as a job. Without a finance team there is no one to operate the product, so those accounts churn and consume support out of proportion to revenue. The €20K ACV floor keeps CAC payback defensible and protects sales capacity for accounts that can expand.

**IMPLIES:**

- Inbound without an identifiable finance team is disqualified at first call, not nurtured.
- No self-serve signup or free tier is built — engineering does not invest in self-serve onboarding.
- Pipeline is qualified on finance-team presence and entity count before it reaches Priya's forecast.

**ANTI-PATTERNS:**

- Taking a sub-€20K deal "to land and expand" with no finance team in place.
- Building self-serve flows to chase volume at the bottom of the market.

### Principle 3 — EU data residency on AWS Frankfurt by default {#principle-data-residency}

**FACT:** EU customer data lives in the EU AWS region (Frankfurt, `eu-central-1`). No cross-region processing or storage by default.

**REASONING:** Treasury data is among the most sensitive a customer holds (bank balances, payment instructions, FX positions). EU mid-market finance buyers treat data residency as a procurement gate, and SOC 2 / GDPR diligence both probe it. Defaulting to Frankfurt removes a recurring objection and keeps the compliance posture simple.

**IMPLIES:**

- New infrastructure provisions in `eu-central-1` unless a signed exception exists.
- Any cross-region service (analytics, logging, LLM inference) is reviewed for data egress before adoption.
- Sub-processors must support EU-region processing or are not adopted.

**ANTI-PATTERNS:**

- Spinning up convenience infrastructure in a US region "just for staging" with production data.
- Routing customer data through a non-EU LLM endpoint without a residency review.

### Principle 4 — senior hires pass through Morgan AND Alex {#principle-hiring-filter}

**FACT:** Every senior hire (lead / E5+) is approved jointly by morgan-chen and the principal. Junior IC hires are Morgan's call alone.

**REASONING:** Senior hires set the technical and cultural ceiling and are the hardest mistakes to reverse at 15 people. Dual approval keeps the co-founders aligned on the leadership bar and prevents a single founder's blind spot from compounding. Pushing junior IC decisions to Morgan alone keeps velocity where the reversibility cost is low.

**IMPLIES:**

- VP Eng and any lead-level offer requires both co-founders' explicit sign-off before extension.
- Junior IC offers do not wait on the principal.
- Comp packages above the band escalate to the board comp committee (Sarah signals flexibility; no fixed number yet).

**ANTI-PATTERNS:**

- Extending a lead-level offer on one co-founder's authority to move faster.
- Routing a junior IC hire through both founders and slowing the pipeline.

---

## Adversarial review {#adversarial-review}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** 2026-06-22

Adversarial review is the default mode for any draft that touches strategic position, external communication, or commitment. RLHF training optimizes the underlying model for agreeable; without explicit policy reversal, review becomes validation theater. The framework reverses the bias at three layers: prompt, verdict enum, and counter-case requirement. For Lattice this binds every fundraise narrative draft, every pricing-change announcement, and every design-partner renewal proposal.

### Binding triggers {#adversarial-triggers}

Any of the following invokes adversarial review on a draft:

- `[REVIEW]` tag anywhere in draft text
- Message starts with `review:` / `redline:` / `adversarial:` / `before send:`
- Explicit phrasing: "review this", "redline this", "before sending", "tear this apart", "challenge this position", "what's wrong with this", "stress-test this"
- Slash commands `/review` or `/redline`

If a draft is pasted without trigger, the agent asks before auto-running.

### Verdict format (fixed enum) {#adversarial-verdict}

Three tiers — no compounds, no softening:

- **SHIP** — position defensible, evidence supports, no fatal counter-case
- **REWRITE** — position has merit but execution has material issues blocking send
- **KILL** — position wrong, evidence weak, or counter-case fatal — do not send

Forbidden: `MOSTLY SHIP`, `SHIP-WITH-CAVEATS`, `MILD REWRITE`, `STRONG REWRITE`, `SOFT KILL`. The three-tier vocabulary is exhaustive.

### Strongest counter-case requirement {#adversarial-counter-case}

Adversarial review constructs the **explicit strongest counter-argument** to the draft's position, mirroring the predictive layer's adversarial-check discipline:

> What are the strongest arguments this position is WRONG, even if the draft initially makes it sound right?

A draft that doesn't acknowledge its strongest counter-case is REWRITE-or-KILL territory — independent of prose polish.

### Anti-patterns {#adversarial-anti-patterns}

- RLHF-style softening preambles ("Overall solid, just one concern…")
- Symmetric pro/con balance when one side clearly wins
- Validation theater (verdict that confirms what the user already drafted)
- Recommending the user's own position back at them
- Hedge-language without actionable issue ("could be better", "consider tightening")
- Compound verdicts ("MOSTLY SHIP")
- Personally critical language (attacks on the writer, not the work)

### Suspend conditions {#adversarial-suspend}

Adversarial review is suspended in three contexts (workflow doc `.claude/workflows/adversarial-review.md` carries the executable rules):

1. Brainstorming / early-stage exploration — adversarial pushback suppresses generative work
2. Moments of distress — review is not crisis support
3. Mechanical execution tasks — content QA, not strategic challenge → route to `deliverable-reviewer`

**Source:** `.claude/agents/adversarial-reviewer.md` + `.claude/workflows/adversarial-review.md` + `docs/adversarial.md`

---

## Daily digest — operational tempo {#daily-digest}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** 2026-06-22

### Cadence (binding) {#digest-cadence}

The daily digest is the **operational tempo** of this framework. Alex runs `/digest` once per business day. Cadence override (weekly for low-velocity domains) requires a decision record at `memory/decisions/<date>-digest-cadence-override.md`.

The digest pulls from configured sources (`memory/digest_sources.md`), detects drift between canonical state and reality, auto-generates briefs for high-prep events within 48 h, and feeds the predictive layer with shadow lookback + new shadow hypotheses. Without daily cadence, drift accumulates uncaught and the predictive loop breaks.

### Drift ack flow (binding) {#digest-drift-ack}

Drift flags surface as numbered items in the digest output. Alex responds with `confirm | ignore Nd | patch <text>`:

- **`confirm`** → workflow proposes patch → principal commits manually with `decision:` or `docs(<canonical>):` prefix
- **`ignore Nd`** → ack stored in `memory/digest_state.md` with `today + Nd` expiry (default 7 days)
- **`patch <text>`** → principal supplies patch directly, behaves like `confirm` from step 3

Permanent acks (`9999-12-31`) require explicit rationale in the ack source line — they are a documentation-gap acknowledgment, not a workaround.

### Brief auto-gen scope (binding) {#digest-brief-scope}

Briefs auto-generate ONLY for high-prep events in the next 48 h:

- 1:1 with a stakeholder whose profile has `profile_depth: partial` or deeper (e.g. sarah-vyas monthly, priya-shah sales sync)
- Decision meetings (board, governance, vote — e.g. pricing-v2 board review)
- External commercial conversations (design-partner renewal, negotiation)
- Board / exec events
- Counterparty conversations flagged in active topic shards

NOT for internal stand-ups, daily syncs, recurring blocks, or 1:1 entries without a named counterparty. The fork's `memory/digest_sources.md` `calendar.brief_eligibility` tunes the boundary.

### Anti-patterns (binding) {#digest-anti-patterns}

The digest workflow MUST NOT:

1. **Auto-commit.** State updates and brief files remain unstaged. Alex reviews + commits in batch.
2. **Auto-spawn `profile-bootstrap`.** Digest flags refresh candidates; principal invokes.
3. **Render shadow hypothesis content.** Shadow hypotheses are invisible at generation time (anti-self-fulfilling — see § Predictive layer governance).
4. **Run more than once per 4 h** without explicit `--force` override.

### Pre-flight (binding) {#digest-preflight}

Every `/digest` invocation verifies CWD is the repo root, state file exists and is parseable, source config is non-empty, and the cadence guard is not violated. Failure on any check STOPS with a diagnostic — no graceful degradation.

### Cross-references {#digest-cross-references}

- Workflow: `.claude/workflows/daily-digest.md`
- Policy: `docs/digest.md`
- State file: `memory/digest_state.md`
- Sources: `memory/digest_sources.md`
- Lint rule: `scripts/lint_rules/digest_state_freshness.py`

---

## External write gate {#external-write-gate}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** 2026-06-22

**FACT (source: `docs/governance.md` § External write gate):** Reads of external / shared systems are free. Writes (create / update / delete / post / send / publish) to any destination other people see — documentation platform, chat platform, project tracker, email, calendar — require explicit confirmation of the specific write action. A generic task instruction ("process X", "do item 1") is not publish authorization.

**REASONING:** The cost asymmetry is extreme: a wrong external write leaks confidential treasury data or makes a commitment in Alex's name to a board member or customer; a deferred write costs one confirmation round-trip. Typical adoption trigger: an ambiguous instruction read as publish authorization, or a "confirm it" read as a send when a draft was wanted.

**IMPLIES:**

- Draft-first: agent output destined for an external system lands in `deliverables/` (or chat as copy-paste text), then Alex confirms the specific action: "publish to Confluence page `<name>`", "send to sarah-vyas".
- The confirmation names destination + action. Approving "the task" is not approving the write.
- Channels with repeated misfires get demoted to **absolute read-only** — agent emits copy-paste text only, even when the instruction sounds like a send ("reply to him", "confirm it"). Re-promotion requires a decision record.

**GATED DESTINATIONS:**

| Destination | Gate level | Provenance |
|---|---|---|
| Confluence (documentation platform) | per-action confirm | `docs/governance.md` § External write gate |
| Slack `#board-async` / `#strategy-private` (chat platform) | absolute read-only | `docs/governance.md` § External write gate |
| Asana "Lattice 2026" (project tracker) | per-action confirm | `docs/governance.md` § External write gate |

**ANTI-PATTERNS:**

- Treating "handle this" / "process X" as authorization to publish or send.
- Writing to a demoted channel (Slack board/strategy) because *this particular* instruction sounded explicit.
- Relaxing the gate without a decision record superseding the one that created it.

---

## Strategic posture {#strategic-posture}

> **Status:** mix — see per-section badges
> **Last updated:** 2026-06-22
> _Strategic posture covers how Lattice competes / differentiates / sequences. More volatile than operating principles. Sections graduate to `RESOLVED` once a decision record locks them in._

### Market / scope {#strategic-posture-market}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22

**FACT:** Lattice serves mid-market companies (€10–100M revenue) needing treasury automation — cash forecasting, bank connectivity, and FX exposure consolidation across multiple accounts and entities. Out of scope: enterprise treasury (>€100M, served by incumbents with implementation teams) and SMB / self-serve (no finance team, sub-€20K ACV).

**REASONING:** Mid-market is underserved — too complex for spreadsheets, too small for enterprise TMS vendors that require six-figure implementations. These companies have a real finance team (the ICP gate) but lack a dedicated treasury platform, so the wedge is clear and the buyer is identifiable.

**IMPLIES:**

- GTM targets companies with a CFO + treasury/AP analyst and multiple bank accounts or entities.
- We do not build down to self-serve SMB or up to enterprise-implementation-heavy deals.
- Multi-entity / multi-bank complexity is a qualifier, not a deal-breaker — it is where the product wins.

### Differentiation {#strategic-posture-differentiation}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** Lattice differentiates on time-to-value (live bank connectivity in days, not a multi-month implementation) and on automated cash-flow categorization that incumbents do manually. Against spreadsheets we win on multi-entity consolidation and FX visibility; against enterprise TMS we win on price and onboarding speed.

**REASONING:** Mid-market buyers will not tolerate enterprise implementation cycles and cannot afford enterprise pricing. Fast connectivity and automated categorization are the two pains that pull them off spreadsheets. This is `OPEN` because a well-funded competitor moving downmarket (see watch list) could compress the price/speed gap.

### Sequence / phasing {#strategic-posture-sequence}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** Series B is the organizing sequence. Target: €3M ARR + Net Retention >115% by month 24 post-Series-A (~12 months out), funding a €15–25M raise. The unblocking sequence is: (1) close VP Eng to recover Morgan's bandwidth; (2) complete SOC 2 Type II to unlock design-partner seat expansion; (3) confirm the design partner 1 renewal; (4) ship pricing v2 to make the NR engine real; (5) form the Series B narrative.

**REASONING:** ARR trajectory (€1.2M → €1.8M projected) does not yet reach €3M, so Net Retention is the load-bearing metric — which depends on pricing v2 (entity-based expansion) and retaining the largest accounts (design partner 1). The hires and compliance work are prerequisites that gate expansion, so they sequence first.

---

## Stakeholder model {#stakeholder-model}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22
> _Authoritative roster of who matters and what each person's role is. Detailed per-person profiles live in `memory/stakeholders/<slug>.md`. This section declares the official structure. Alex (principal) is the owner of the system and has no profile file._

### Decision-making authority {#stakeholder-authority}

| Role | Who | Scope |
|---|---|---|
| CEO / principal | Alex (self) | Commercial, product strategy, fundraising, board; final call on go-to-market and pricing |
| Co-founder & CTO | `morgan-chen` | Engineering, architecture, technical feasibility; junior IC hiring; joint sign-off on senior hires |
| Lead VC / board director | `sarah-vyas` | Board vote, comp-committee input, Series B sponsorship; veto weight on major strategic moves |
| Head of Sales | `priya-shah` | Pipeline, sales execution, forecast; owns deal qualification under the ICP gate |
| Largest customer (buyer-of-record) | `lattice-design-partner-1` | Renewal decision on the €180K account; new buyer-of-record Karim Solanki (CFO) tracked inside this profile |

### Coalition map {#stakeholder-coalition}

- **Primary advocates:** `morgan-chen` (co-founder, fully aligned), `sarah-vyas` (lead VC, Series B sponsor) — supportive, unblock or amplify.
- **Sceptics / counterweights:** `priya-shah` — challenges pricing v2 from the sales-friction angle; a healthy counterweight on go-to-market.
- **Veto-holders:** `sarah-vyas` — board weight on Series B timing, comp ceiling, and major scope; must be aligned for major moves.
- **External counterparties:** `lattice-design-partner-1` — largest customer, churn risk, renewal under review. Named-but-unprofiled counterparties (prose only): david-tannen and marcus-liu (board), lattice-design-partner-2 and lattice-design-partner-3 (healthy accounts), compliance-vendor-x (SOC 2 audit), recruiter-firm-y (VP Eng search), alina-crisan (VP Eng finalist).

### Engagement cadence {#stakeholder-cadence}

| Stakeholder | Cadence | Format |
|---|---|---|
| `morgan-chen` | Weekly | Co-founder sync |
| `sarah-vyas` | Monthly | 30-min 1:1 + quarterly board |
| `priya-shah` | Weekly | Sales / pipeline review |
| `lattice-design-partner-1` | Ad-hoc | Renewal track; Alex + Priya own the account |

---

## Architecture / how the work works {#architecture}

> **Status:** mix
> **Last updated:** 2026-06-22
> _What the product actually does and the load-bearing facts about how it does it. Heavily cited (FACT lines). Architecture decisions get their own subsection with `RESOLVED` / `OPEN` status._

### Core components {#architecture-core}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22

**FACT:** Lattice is a single monorepo (`lattice-monorepo`) deployed in `eu-central-1`. Three load-bearing subsystems:

| Component | Role |
|---|---|
| Bank connectivity layer | Pulls balances and transactions across customer bank accounts and entities; payment/payout integration via Mercury Bank API (rate limit 1000 req/min). |
| Cash-flow engine | Consolidates positions across accounts/entities, forecasts cash, computes FX exposure. |
| LLM categorization service | Classifies transactions into cash-flow categories automatically (the incumbent-manual task we automate). |

### Config-vs-core boundary {#architecture-config-vs-core}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22

**FACT:** Customer-specific behavior is configuration (per-entity setup, bank-connector selection, categorization rules, residency region). Shared product logic is core. Per-customer asks that would require a core branch are escalated, not silently forked.

**REASONING:** At 15 people, per-customer core forks are unaffordable to maintain. Holding the config/core line is what keeps a small eng team serving multiple design partners — and it is exactly the line design partner 1's tech ask is testing.

**ALTERNATIVES REJECTED:**

- Per-customer core branches — rejected because maintenance cost compounds and blocks the shared roadmap.
- Fully generic config-only product with no escalation path — rejected because some genuinely strategic asks justify core investment; the point is a deliberate decision, not a default.

**TRIGGER CONDITIONS for re-evaluation:** see the design partner 1 tech-ask scope cap — `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md`.

### Bank connectivity {#architecture-bank-connectivity}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** Connectivity is built on direct bank APIs (Mercury today) plus an aggregation layer. Open Banking 2.0 (UK FCA consultation, Q3 2026) could change connector cost structure.

**REASONING:** Direct APIs give the best data fidelity for treasury use but each connector is bespoke. Aggregation broadens coverage at the cost of latency and data quality. This is `OPEN` because the Open Banking regulatory shift may change the build-vs-aggregate economics.

### LLM cash-flow categorization {#architecture-llm-categorization}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** Transaction categorization uses an LLM. Inference must respect EU data residency (§ `#principle-data-residency`). The EU AI Act risk classification is on the watch list — if model-risk rules tighten, this service needs a compliance review.

**REASONING:** Categorization is the automation wedge against incumbents who do it manually, but it processes the most sensitive customer data, so residency and AI-Act exposure are first-order constraints, not afterthoughts.

**TRIGGER CONDITIONS for re-evaluation:** EU AI Act enforcement guidance lands and classifies financial-categorization models as higher-risk; or a residency-incompatible inference dependency is proposed.

---

## Commercial model {#commercial-model}

> **Status:** mix
> **Last updated:** 2026-06-22
> _Pricing, packaging, contracting, revenue model. Decisions here have direct business-case impact — every change requires a BC-impact note._

### Pricing {#commercial-pricing}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22
> Source: `memory/decisions/2026-05-18-pricing-v2-platform-fee.md`

**FACT:** Platform fee + per-entity layer for all new deals. No per-seat pricing (see § `#principle-pricing-shape`). Existing design partners are grandfathered to per-seat until renewal, then migrated.

**REASONING:** Entity count is the dimension that grows with the customer and is the basis for Net-Retention expansion; per-seat decoupled revenue from delivered value.

**BC impact:** Entity-based expansion is the engine for the Series B target of Net Retention >115%. Migration of grandfathered design partners at renewal converts flat per-seat accounts into expanding per-entity accounts.

### Packaging {#commercial-packaging}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** A single platform tier (no per-seat tiers) with usage scaling on entities and bank connections. Add-on scope (FX module, advanced forecasting) is still being defined as part of pricing v2 rollout. Tracking: `memory/topics/pricing-v2.md`.

### Contracting {#commercial-contracting}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22

**FACT:** Annual contracts, EU entity as contracting party, EU data residency clause standard. Deals >€100K ACV require SOC 2 Type II evidence in the contract diligence package (see § `#compliance-soc2`). Renewals are the migration point for grandfathered per-seat customers.

---

## Compliance & legal posture {#compliance-legal-posture}

> **Status:** mix
> **Last updated:** 2026-06-22
> _Regulatory, legal, data-protection posture. High-stakes section — changes here typically trigger external counsel review._

### SOC 2 Type II {#compliance-soc2}

> **Status:** `RESOLVED` (posture) / `OPEN` (audit in progress)
> **Last updated:** 2026-06-22

**FACT (source: design partner procurement requirements + `compliance-vendor-x` engagement):** SOC 2 Type II is non-negotiable for any deal >€100K ACV. Two of three design partners gate seat / entity expansion on completion. The audit is mid-flight with `compliance-vendor-x`; surprise findings are possible.

**OUR POSTURE:** Complete SOC 2 Type II before expansion deals close. The final report gates two design-partner expansions, so it sits on the critical path to the Series B Net-Retention number.

**OPEN ITEMS:** Mid-audit findings still outstanding; remediation scope unknown until the draft findings land.

### ISO 27001 {#compliance-iso27001}

> **Status:** `RESOLVED` (deferred)
> **Last updated:** 2026-06-22

**FACT:** ISO 27001 is deferred to Series B. SOC 2 Type II covers current procurement gates; ISO adds cost without unblocking present deals.

**OUR POSTURE:** Do not start ISO 27001 work pre-Series-B. Revisit when enterprise-leaning prospects or post-B scale make it a procurement gate.

### EU data residency & GDPR {#compliance-data-residency}

> **Status:** `RESOLVED`
> **Last updated:** 2026-06-22

**FACT:** EU customer data is processed and stored in `eu-central-1` (Frankfurt) by default (see § `#principle-data-residency`). Standard DPA in place for EU customers.

**OUR POSTURE:** Residency-by-default removes a recurring procurement objection and keeps sub-processor selection constrained to EU-region-capable vendors.

### EU AI Act watch {#compliance-ai-act}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22

**FACT:** Lattice uses an LLM for cash-flow categorization (§ `#architecture-llm-categorization`). EU AI Act enforcement guidance is pending; a tightening of model-risk classification for financial use could require a compliance review.

**OPEN ITEMS:** Monitor EU AI Act enforcement guidance; assess whether the categorization model falls into a regulated risk tier and what documentation that would demand.

---

## Active blockers (canonical) {#active-blockers-canonical}

> **Status:** `OPEN`
> **Last updated:** 2026-06-22
> _The constitution's view of what is blocking Lattice right now. This is the authoritative list — `memory/CLAUDE_MEMORY.md` may carry additional transient items, but the canonical blockers live here._

1. **B1 — Design partner 1 renewal** — €180K ARR account; original champion departed, new buyer-of-record (CFO Karim Solanki) reviewing renewal. Owner: `lattice-design-partner-1`. Tracking: `memory/topics/dp1-renewal.md`.
2. **B2 — VP Engineering hire** — Morgan stretched across eng + product + the design partner 1 tech ask; senior search active with one finalist. Owner: `morgan-chen`. Tracking: `memory/topics/vp-eng-hire.md`.
3. **B3 — SOC 2 Type II audit** — mid-audit with `compliance-vendor-x`; gates two design-partner expansions and all >€100K ACV deals. Owner: Alex (self). Tracking: `memory/topics/dp1-renewal.md` (expansion dependency) and § `#compliance-soc2`.
4. **B4 — Pricing v2 rollout** — platform + per-entity decided; packaging/add-on scope and customer migration plan still open. Owner: `priya-shah`. Tracking: `memory/topics/pricing-v2.md`.
5. **B5 — Series B narrative gap** — need a €3M ARR + Net Retention >115% inflection story; current trajectory €1.2M → €1.8M. Owner: Alex (self). Tracking: `memory/topics/series-b-prep.md`.
6. **B6 — Co-founder bandwidth** — Morgan running both eng and product; the design partner 1 tech ask is consuming his cycles above the 60% customer-facing budget. Owner: `morgan-chen`. Tracking: `memory/topics/vp-eng-hire.md`.

---

## Superseded positions {#superseded-positions}

> **Status:** historical record — read-rarely
> _When a section is superseded, the old version lands here as a stub with a pointer to the new section. Do not delete; future readers need the trail._

_None yet. The first supersession will land here as a stub with a pointer to its replacement section._

---

## Appendices

### A. Glossary {#appendix-glossary}

| Term | Definition |
|---|---|
| ACV | Annual Contract Value. |
| ICP | Ideal Customer Profile — here, a mid-market company with a dedicated finance team. |
| NR / Net Retention | Net revenue retention across the existing customer base; Series B target >115%. |
| Entity | A legal entity (subsidiary / account grouping) — the per-entity pricing unit. |
| TMS | Treasury Management System — the enterprise category Lattice undercuts on price/speed. |
| Buyer-of-record | The person who owns the purchase/renewal decision at a customer. |

### B. External references {#appendix-references}

- Mercury Bank API — payments / payouts integration, rate limit 1000 req/min.
- UK FCA Open Banking 2.0 consultation — Q3 2026, may change connector cost structure.
- EU AI Act — enforcement guidance pending; relevant to LLM categorization.

### C. Decision record index {#appendix-decision-index}

- `memory/decisions/2026-05-15-dp1-tech-ask-scope-cap.md` — established § `#architecture-config-vs-core`
- `memory/decisions/2026-05-18-pricing-v2-platform-fee.md` — established § `#principle-pricing-shape` and § `#commercial-pricing`
- `memory/decisions/2026-05-21-dp1-renewal-call-2026-05-27.md` — informs § `#active-blockers-canonical` B1

---

_End of constitution. To amend, see `knowledge/README.md` "How to amend safely"._
