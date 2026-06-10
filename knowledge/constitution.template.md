# <DOMAIN_NAME> — Living Constitution

<!--
This is the canonical single-source-of-truth document for the <DOMAIN_NAME>
initiative / company / engagement. When this file disagrees with anything
else in the repo (memory, briefs, drafts), this file wins.

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
     decision X]" trails. When a decision changes canon, rewrite the section
     to current state; history lives in git, the decision record, and the
     Superseded-positions stub (see knowledge/README.md "Current-state only").

The `post-constitution-edit-check.sh` hook flags missing supersedes-pointers,
missing commit-message prefix, and detected domain-leak patterns.
-->

> **Version:** v0.1 (draft)
> **Last review:** YYYY-MM-DD
> **Status:** DRAFT — promote to LIVING after first full pass

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
the anchor here. Sections cited by other sections must have stable anchor
IDs even if their headers evolve.
-->

1. [Operating principles](#operating-principles) — `RESOLVED`
2. [Strategic posture](#strategic-posture) — `OPEN` / `RESOLVED` per section
3. [Stakeholder model](#stakeholder-model) — `RESOLVED`
4. [Architecture / how the work works](#architecture) — mix of `RESOLVED` + `OPEN`
5. [Commercial model](#commercial-model) — `RESOLVED` / `OPEN`
6. [Compliance & legal posture](#compliance-legal-posture) — `RESOLVED` / `OPEN`
7. [Active blockers (canonical)](#active-blockers-canonical) — `OPEN`
8. [Superseded positions](#superseded-positions) — historical record

---

## Operating principles {#operating-principles}

> **Status:** `RESOLVED`
> **Last updated:** YYYY-MM-DD
> _Operating principles are the load-bearing values the initiative is built on. They are durable across quarters. They are amended sparingly — typically only when a fundamental assumption is challenged._

<!--
EXAMPLE FORMAT (replace with your domain's principles):

### Principle 1 — <one-line principle>

**FACT (source: <citation>):** <The concrete claim — what is true.>

**REASONING:** <Why this principle was adopted. What it costs. What it
buys.> Cite back-link `Source: memory/decisions/<file>` if established by
a recorded decision.

**IMPLIES:** <Operational consequences — what follows from this principle
when applied. Bullet-style, terse.>

- <consequence 1>
- <consequence 2>

**ANTI-PATTERNS:** <What this principle forbids. The "do not" list.>

- <forbidden behaviour 1>
- <forbidden behaviour 2>
-->

### Principle 1 — `<principle_one_name>`

**FACT (source: `<citation_or_decision_record>`):** `<the concrete claim>`

**REASONING:** `<why this was adopted, trade-offs, what's bought>` — Source: `memory/decisions/<YYYY-MM-DD>-<slug>.md`

**IMPLIES:**

- `<consequence_1>`
- `<consequence_2>`

**ANTI-PATTERNS:**

- `<forbidden_behaviour_1>`

### Principle 2 — `<principle_two_name>`

**FACT (source: `<citation>`):** `<claim>`

**REASONING:** `<rationale>`

**IMPLIES:**

- `<consequence>`

### Principle 3 — `<principle_three_name>`

`<and so on>`

---

## Adversarial review {#adversarial-review}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** YYYY-MM-DD

Adversarial review is the default mode for any draft that touches strategic position, external communication, or commitment. RLHF training optimizes the underlying model for agreeable; without explicit policy reversal, review becomes validation theater. The framework reverses the bias at three layers: prompt, verdict enum, and counter-case requirement.

### Binding triggers

Any of the following invokes adversarial review on a draft:

- `[REVIEW]` tag anywhere in draft text
- Message starts with `review:` / `redline:` / `adversarial:` / `before send:`
- Explicit phrasing: "review this", "redline this", "before sending", "tear this apart", "challenge this position", "what's wrong with this", "stress-test this"
- Slash commands `/review` or `/redline`

If a draft is pasted without trigger, the agent asks before auto-running.

### Verdict format (fixed enum)

Three tiers — no compounds, no softening:

- **SHIP** — position defensible, evidence supports, no fatal counter-case
- **REWRITE** — position has merit but execution has material issues blocking send
- **KILL** — position wrong, evidence weak, or counter-case fatal — do not send

Forbidden: `MOSTLY SHIP`, `SHIP-WITH-CAVEATS`, `MILD REWRITE`, `STRONG REWRITE`, `SOFT KILL`. The three-tier vocabulary is exhaustive.

### Strongest counter-case requirement

Adversarial review constructs the **explicit strongest counter-argument** to the draft's position. Default-skeptical lookback, mirroring the predictive layer's adversarial-check discipline:

> What are the strongest arguments this position is WRONG, even if the draft initially makes it sound right?

A draft that doesn't acknowledge its strongest counter-case is REWRITE-or-KILL territory — independent of prose polish.

### Anti-patterns

- RLHF-style softening preambles ("Overall solid, just one concern…")
- Symmetric pro/con balance when one side clearly wins
- Validation theater (verdict that confirms what the user already drafted)
- Recommending the user's own position back at them
- Hedge-language without actionable issue ("could be better", "consider tightening")
- Compound verdicts ("MOSTLY SHIP")
- Personally critical language (attacks on the writer, not the work)

### Suspend conditions

Adversarial review is suspended in three contexts (workflow doc `.claude/workflows/adversarial-review.md` carries the executable rules):

1. Brainstorming / early-stage exploration — adversarial pushback suppresses generative work
2. Moments of distress — review is not crisis support
3. Mechanical execution tasks — content QA, not strategic challenge → route to `deliverable-reviewer`

### Override mechanism (strongly discouraged)

Forks may disable adversarial-as-default by editing this section and the corresponding agent description. **This reverses the framework's core IP design choice.** See `docs/adversarial.md §4` for the recommended alternative path (suspend per-draft via trigger semantics; keep policy at default-adversarial).

**Source:** `.claude/agents/adversarial-reviewer.md` + `.claude/workflows/adversarial-review.md` + `docs/adversarial.md`

---

## Daily digest — operational tempo {#daily-digest}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** YYYY-MM-DD

### Cadence (binding)

The daily digest is the **operational tempo** of this framework. The principal runs `/digest` once per business day. Cadence override (weekly for low-velocity domains) requires a decision record at `memory/decisions/<date>-digest-cadence-override.md`.

The digest pulls from configured sources (`memory/digest_sources.md`), detects drift between canonical state and reality, auto-generates briefs for high-prep events within 48 h, and feeds the predictive layer with shadow lookback + new shadow hypotheses. Without daily cadence, drift accumulates uncaught and the predictive loop breaks.

### Drift ack flow (binding)

Drift flags surface as numbered items in the digest output. The principal responds with `confirm | ignore Nd | patch <text>`:

- **`confirm`** → workflow proposes patch → principal commits manually with `decision:` or `docs(<canonical>):` prefix
- **`ignore Nd`** → ack stored in `memory/digest_state.md` with `today + Nd` expiry (default 7 days)
- **`patch <text>`** → principal supplies patch directly, behaves like `confirm` from step 3

Permanent acks (`9999-12-31`) require explicit rationale in the ack source line — they're effectively a documentation gap acknowledgment, not a workaround.

### Brief auto-gen scope (binding)

Briefs auto-generate ONLY for high-prep events in the next 48 h:

- 1:1 with a stakeholder whose profile has `profile_depth: partial` or deeper
- Decision meetings (board, governance, vote)
- External commercial conversations (renewal, negotiation)
- Board / exec events
- Counterparty conversations flagged in active topic shards

NOT for internal stand-ups, daily syncs, recurring blocks, or 1:1 entries without a named counterparty. The fork's `memory/digest_sources.md` `calendar.brief_eligibility` tunes the boundary.

### Anti-patterns (binding)

The digest workflow MUST NOT:

1. **Auto-commit.** State updates and brief files remain unstaged. Principal reviews + commits in batch.
2. **Auto-spawn `profile-bootstrap`.** Digest flags refresh candidates; principal invokes.
3. **Render shadow hypothesis content.** Shadow hypotheses are invisible at generation time (anti-self-fulfilling — see § Predictive layer governance).
4. **Run more than once per 4 h** without explicit `--force` override.

### Pre-flight (binding)

Every `/digest` invocation verifies CWD is the Giovanni repo root, state file exists and is parseable, source config is non-empty, and cadence guard is not violated. Failure on any check STOPS with diagnostic — no graceful degradation.

### Cross-references

- Workflow: `.claude/workflows/daily-digest.md`
- Policy: `docs/digest.md`
- State template: `memory/digest-state.template.md`
- Sources template: `memory/digest-sources.template.md`
- Session-start hook: `.claude/hooks/session-start-digest.sh`
- Lint rule: `scripts/lint_rules/digest_state_freshness.py`
- Example: `memory/examples/digest.example.md`

---

## External write gate {#external-write-gate}

> **Status:** `RESOLVED` — binding policy
> **Last updated:** YYYY-MM-DD

**FACT (source: `docs/governance.md` § External write gate):** Reads of external / shared systems are free. Writes (create / update / delete / post / send / publish) to any destination other people see — `documentation-platform`, `chat-platform`, `project-tracker`, email, calendar — require explicit confirmation of the specific write action. A generic task instruction ("process X", "do item 1") is not publish authorization.

**REASONING:** The cost asymmetry is extreme: a wrong external write leaks confidential content or makes a commitment in the principal's name; a deferred write costs one confirmation round-trip. Typical adoption trigger: an ambiguous instruction read as publish authorization, or a "confirm it" read as a send when a draft was wanted. — Source: `memory/decisions/<YYYY-MM-DD>-external-write-gate.md` <!-- TODO: create this decision record when adopting the gate, or back-link your own incident -->

**IMPLIES:**

- Draft-first: agent output destined for an external system lands in `deliverables/` (or chat as copy-paste text), then the principal confirms the specific action: "publish to `<documentation-platform>` page `<name>`", "send to `<stakeholder_slug>`".
- The confirmation names destination + action. Approving "the task" is not approving the write.
- Channels with repeated misfires get demoted to **absolute read-only** — agent emits copy-paste text only, even when the instruction sounds like a send ("reply to him", "confirm it"). Re-promotion requires a decision record.

**GATED DESTINATIONS:** <!-- TODO for fork: enumerate your own. One line each: destination, gate level (per-action confirm | absolute read-only), provenance. -->

| Destination | Gate level | Provenance |
|---|---|---|
| `<documentation-platform>` | per-action confirm | `memory/decisions/<file>` |
| `<chat-platform>` | `<per-action confirm \| absolute read-only>` | `memory/decisions/<file>` |
| `<project-tracker>` | per-action confirm | `memory/decisions/<file>` |

**ANTI-PATTERNS:**

- Treating "handle this" / "process X" as authorization to publish or send.
- Writing to a demoted channel because *this particular* instruction sounded explicit.
- Relaxing the gate without a decision record superseding the one that created it.

---

## Strategic posture {#strategic-posture}

> **Status:** mix — see per-section badges
> **Last updated:** YYYY-MM-DD
> _Strategic posture covers how the initiative competes / differentiates / sequences. More volatile than operating principles. Sections graduate to `RESOLVED` once a decision record locks them in._

### Market / scope {#strategic-posture-market}

> **Status:** `RESOLVED` / `OPEN` — `<which>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<what market(s) / scope is in or out>`

**REASONING:** `<why this scope was chosen>`

**IMPLIES:**

- `<scope_consequence_1>`
- `<scope_consequence_2>`

### Differentiation {#strategic-posture-differentiation}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<how we differentiate from incumbents / alternatives>`

**REASONING:** `<rationale>`

### Sequence / phasing {#strategic-posture-sequence}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<the planned sequence — what gets done before what>`

**REASONING:** `<dependencies and capacity constraints driving the sequence>`

---

## Stakeholder model {#stakeholder-model}

> **Status:** `RESOLVED`
> **Last updated:** YYYY-MM-DD
> _Authoritative roster of who matters and what each person's role is. Detailed per-person profiles live in `memory/stakeholders/<slug>.md`. This section just declares the official structure._

### Decision-making authority

| Role | Who | Scope |
|---|---|---|
| `<role_1>` | `<stakeholder_slug>` | `<scope>` |
| `<role_2>` | `<stakeholder_slug>` | `<scope>` |

### Coalition map

- **Primary advocates:** `<slug>`, `<slug>` — supportive, unblock or amplify.
- **Sceptics / counterweights:** `<slug>`, `<slug>` — challenge from named positions.
- **Veto-holders:** `<slug>`, `<slug>` — can block; must be aligned for major moves.
- **External counterparties:** `<slug>` — customers, vendors, regulators.

### Engagement cadence

| Stakeholder | Cadence | Format |
|---|---|---|
| `<slug>` | Weekly | 30-min 1:1 |
| `<slug>` | Monthly | Board session |
| `<slug>` | Ad-hoc | As triggered |

### Operating model / role boundaries (OPTIONAL)

<!--
Use this block when the initiative has a formal operating model with
separate seats (sponsor/board, principal, project manager, engineering,
commercial). Solo-founder forks: delete the block — the lane-separation
rules only bind where the seats actually exist.
Pattern reference: docs/governance.md § "Role boundaries".
-->

**Role matrix** <!-- TODO for fork: fill seats; leave out seats your domain doesn't have -->

| Seat | Who | Owns |
|---|---|---|
| Sponsor / board | `<stakeholder_slug(s)>` | Final scope, budget, go/no-go, sequencing; escalation arbitration |
| Principal (product / strategy owner) | `<principal>` | Vision, roadmap, launch scope, acceptance criteria, product outcome |
| Project manager | `<stakeholder_slug>` | Integrated plan, cross-functional coordination, RAID + decision log, status reporting, change control |
| Engineering lead | `<stakeholder_slug>` | Build, architecture, technical feasibility |
| Commercial lead | `<stakeholder_slug>` | GTM, pricing execution, revenue |

**Behavioral rules (binding once seats are filled):**

1. **Lane separation.** Delivery / status / RAID / scheduling / cross-team coordination work belongs to the project-manager seat. The agent flags it as such — it never maps it onto the principal.
2. **Shared status forums:** generate only the principal's slice (e.g. the product slide), never the full project status — that is the PM's artifact.
3. **Escalation routing:** cross-functional blocker → project manager; strategic / scope / budget / go-no-go / pricing → sponsor/board.
4. **Two-way artifact flow:** the PM's agendas, minutes, decision log, and RAID are digest inputs; the principal's decisions and product-side risks feed back into the PM's log.
5. **Open comment threads ≠ settled canon.** A governance doc with unresolved comments is not `RESOLVED` — track the open threads explicitly.

---

## Architecture / how the work works {#architecture}

> **Status:** mix
> **Last updated:** YYYY-MM-DD
> _What the system / org / product actually does and the load-bearing facts about how it does it. Heavily cited (FACT lines). Architecture decisions get their own subsection with `RESOLVED` / `OPEN` status._

### Core components {#architecture-core}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT (source: `<citation>`):** `<the structural reality>`

`<diagram or table of components and how they relate>`

### `<architecture_decision_one>` {#architecture-decision-one}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD
> Source: `memory/decisions/<YYYY-MM-DD>-<slug>.md`

**FACT:** `<the chosen architecture>`

**REASONING:** `<why this over alternatives>`

**ALTERNATIVES REJECTED:**

- `<alternative_1>` — rejected because `<reason>`
- `<alternative_2>` — rejected because `<reason>`

**TRIGGER CONDITIONS for re-evaluation:** see decision record back-link.

### `<architecture_decision_two>` {#architecture-decision-two}

`<same shape>`

---

## Commercial model {#commercial-model}

> **Status:** mix
> **Last updated:** YYYY-MM-DD
> _Pricing, packaging, contracting, revenue model. Decisions here have direct business-case impact — every change requires a BC-impact note._

### Pricing {#commercial-pricing}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<the pricing model>`

**REASONING:** `<why this model>`

**BC impact:** `<headline metric — ARR, ACV, take-rate — that this model produces>`

### Packaging {#commercial-packaging}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<how the offering is bundled>`

### Contracting {#commercial-contracting}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT:** `<contract structure — terms, parties, MoR, etc.>`

---

## Compliance & legal posture {#compliance-legal-posture}

> **Status:** mix
> **Last updated:** YYYY-MM-DD
> _Regulatory, legal, accessibility, data-protection posture. High-stakes section — changes here typically trigger external counsel review._

### `<compliance_domain_one>` {#compliance-one}

> **Status:** `<RESOLVED | OPEN>`
> **Last updated:** YYYY-MM-DD

**FACT (source: `<regulation_or_counsel_citation>`):** `<what is required>`

**OUR POSTURE:** `<how we comply>`

**OPEN ITEMS:** `<gaps still to be closed>`

### `<compliance_domain_two>` {#compliance-two}

`<same shape>`

---

## Active blockers (canonical) {#active-blockers-canonical}

> **Status:** `OPEN`
> **Last updated:** YYYY-MM-DD
> _The constitution's view of what is blocking the initiative right now. This is the authoritative list — `memory/CLAUDE_MEMORY.md` may have additional transient items but the canonical blockers live here._

<!--
Blockers in the constitution are deeper / longer-lived than memory's
operational "active blockers". A constitution blocker has been escalated
to "this is a known structural problem that requires a decision".
-->

1. **B1 — `<blocker_name>`** — `<one-line description>`. Owner: `<slug>`. Tracking: `memory/topics/<slug>.md`.
2. **B2 — `<blocker_name>`** — `<one-liner>`. Owner: `<slug>`. Tracking: `memory/topics/<slug>.md`.

---

## Superseded positions {#superseded-positions}

> **Status:** historical record — read-rarely
> _When a section is superseded, the old version lands here as a stub with a pointer to the new section. Do not delete; future readers need the trail._

### `<old_position_name>` (SUPERSEDED → §`<new-anchor>`)

> **Superseded:** YYYY-MM-DD
> **Reason:** `<one paragraph — what changed, what new information forced the change>`
> **Replacement:** [`<new-anchor>`](#`<new-anchor>`)

`<one-paragraph stub of the old position>`

---

## Appendices

### A. Glossary

| Term | Definition |
|---|---|
| `<term_1>` | `<definition>` |
| `<term_2>` | `<definition>` |

### B. External references

- `<reference_1>` — `<URL or citation>`
- `<reference_2>` — `<URL or citation>`

### C. Decision record index

<!--
Auto-discoverable from `memory/decisions/`. This is an optional inline
reverse-index — if your domain has many decision records, list the ones
that established or amended sections of this constitution.
-->

- `memory/decisions/<YYYY-MM-DD>-<slug>.md` — established §`<anchor>`
- `memory/decisions/<YYYY-MM-DD>-<slug>.md` — amended §`<anchor>`

---

_End of constitution. To amend, see `knowledge/README.md` "How to amend safely"._
