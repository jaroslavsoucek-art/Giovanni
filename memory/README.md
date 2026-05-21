# Giovanni Memory Layer — schema explanation

Memory is **operational state** — what an AI Chief of Staff needs to load to act usefully *today* on behalf of its principal. It is not a knowledge base (`knowledge/` owns that), not a chat log (git history owns that), not a CRM (deep storage owns per-person profiles).

Memory's job is to make session start cheap. Layer 0 + Layer 1 auto-load in every session and must stay small. Everything else lazy-loads on demand.

This document explains the 4-layer model, when each layer applies, and how items move between layers. Fork this file when adapting Giovanni to a new domain — almost everything below stays the same. Only the test-domain examples need replacement.

---

## The 4-layer model

| Layer | Files | Purpose | Loaded |
|---|---|---|---|
| **L0 — MAP** | `memory/MAP.md` (auto-regenerated) | Navigation index of every memory + knowledge artifact. Single grep target. | Every session start |
| **L1 — Operational** | `memory/CLAUDE_MEMORY.md` (or rename for your domain) | Active blockers, this week, on the horizon, watch list, open questions. Hard cap 300 lines. | Every session start |
| **L2 — Topic shards** | `memory/topics/<slug>.md` | Per-topic deep state with YAML frontmatter. One shard per ongoing initiative. | Lazy load on relevance (grep MAP first) |
| **L3 — Deep storage** | `decisions/`, `briefs/`, `stakeholders/`, `archive/`, plus optional `branch-out/`, `shadow/`, `calibration/`, `audits/`, `watch/`, `intel/` | Per-decision audit trail, per-event prep, per-person profile, retired items, plus optional predictive / governance / intel layers. | Follow pointers from L1 / L2 |

The contract between layers is **pointers, not duplication**. L1 says "blocker #4: pricing migration — `→ topics/pricing-v2.md`". The shard owns the detail. L1 owns the fact that it's an active blocker today.

### What auto-loads at session start

L0 (MAP) + L1 (CLAUDE_MEMORY) only. If you find yourself reading every shard on every turn, the L1/L2 split has collapsed and you need to re-prune L1.

### Navigation pattern

1. **Topic-specific query:** grep MAP for slug / stakeholder slug / topic keywords → identify L2 shard → read shard → follow `related_*` frontmatter pointers as needed.
2. **History query:** follow pointers into L3 (`archive/`, `briefs/`, `decisions/`). If the index doesn't have it, `git log memory/`.
3. **Canonical fact query:** memory is **never** canonical. Canon lives in `knowledge/` (constitution + indexed docs). If you need to assert a fact, check `knowledge/` first; memory may be stale.

---

## Layer 0 — MAP (navigation index)

Single auto-regenerated file. Lists every active shard, decision record, brief, stakeholder profile, archive, and peripheral L3 directory with one-line description.

- **Auto-regen trigger:** hook fires on every Edit/Write to `memory/topics/`, `memory/decisions/`, `memory/briefs/`, `memory/stakeholders/`, `memory/archive/`. Hook implementation is `governance-architect` domain — see `TODO: governance-architect` notes in template.
- **Never edit by hand.** Manual edits get overwritten. If you want to change MAP format, edit the regen script, not the output.
- **Template:** `templates/MAP.template.md` — describes the target shape the regen script must produce.

---

## Layer 1 — Operational memory

The one file an agent always reads. Strict shape:

- **Active blockers** — things that, if not resolved, stop progress this week. Numbered list, one line per blocker, pointer to shard if deep.
- **This week** — concrete actions / meetings / deliverables due in current 7-day window.
- **On the horizon** — things due in next ~2-4 weeks. Light touch — re-promote to "this week" when they get closer.
- **Watch list** — no action yet, just monitor. Things that *could* escalate.
- **Open questions** — explicit `[TBD]` items needing a human to decide.

**Hard limits (binding):**

| Limit | Threshold | Rationale |
|---|---|---|
| **Total length** | 300 lines | Above this, an agent spends meaningful tokens loading L1 every session. The whole point of L1 is cheap session start. |
| **Strikethrough ratio** | 2% of lines | Strikethrough is acceptable for ≤1 session as "done but not yet archived". Persistent strikethrough = soft delete = drift. Above 2% means cleanup is overdue. |

**Why these numbers, not others?**

300 was chosen empirically — at ~80 tokens per line, that's ~24k tokens, roughly 12% of a 200k-token context window. Acceptable session-start overhead. If your agent has a much smaller context (e.g. 32k), drop to ~100 lines. If much larger, the limit doesn't change much — token-cheap session starts are still desirable.

2% strikethrough is a drift signal, not an absolute count. Below 2% it's noise. Above 2% it indicates the writer is using strikethrough as "I'll archive this later" — and "later" never comes. The fix is archive immediately or delete.

**Templates and worked examples:** `templates/operational-memory.template.md`, `examples/operational-memory.example.md`.

---

## Layer 2 — Topic shards

One file per ongoing initiative. YAML frontmatter + free-form body.

### Frontmatter schema (binding fields)

```yaml
slug: <kebab-case unique identifier>
status: active | partially-resolved | resolved | superseded
owner: <stakeholder_slug or "self">
last_touch: YYYY-MM-DD
key_stakeholders: [<slug>, <slug>, ...]
related_decisions: [<repo-relative-path>, ...]
related_briefs: [<repo-relative-path>, ...]
related_knowledge: [<repo-relative-path>, ...]
related_artifacts: [<repo-relative-path>, ...]
related_topics: [<slug>, <slug>, ...]
```

### Optional fields (use only when meaningful)

```yaml
related_branch_outs: [...]   # only if predictive layer in use → see prediction-architect
related_shadows: [...]       # only if predictive layer in use → see prediction-architect
affects_gates: [<gate_id>]   # only if you have a milestone gating system
```

### Body structure (recommended sections)

- **Status & current state** — what's true today
- **Active threads** — open sub-actions and who owns them
- **Timeline & history** — dated entries; this is where decisions get audit-trailed locally before graduating to L3 decision records
- **Trigger conditions** — what would cause this topic to advance, branch, or close
- **Open questions** — explicit `[TBD]` items
- **Risk register** — known failure modes + mitigations
- **Deliverables** — pointers to artifacts produced under this topic

### When to create a shard (graduation criteria)

Item in L1 graduates to L2 when **ANY** of:

1. **>5 active sub-items** (sub-decisions, sub-actions, open questions, related stakeholders)
2. **>14 days of continuous activity** across sessions
3. **Cross-cuts ≥3 stakeholders** (multi-actor coordination)
4. **Has its own decision record** in `memory/decisions/`
5. **Has its own predictive artifact** (branch-out, shadow hypothesis)

When graduating:

1. Create `memory/topics/<slug>.md` with frontmatter.
2. In L1, replace the detail with a 1-2 line summary + pointer `→ topics/<slug>.md`.
3. MAP auto-regen on next save adds the entry.
4. Commit with `feat(memory): graduate <slug> to topic shard`.

### When to retire a shard

When the topic resolves:

1. Set `status: resolved` in frontmatter.
2. Last-touch date stays as final resolution date.
3. After **60 days without touch**, move to `memory/topics/_resolved/<slug>.md`.
4. MAP regen lists resolved shards in a separate section.
5. Cross-references from other shards may still point into `_resolved/` — link rot is tolerated for historical pointers.

**Templates and worked examples:** `templates/topic-shard.template.md`, `examples/topic-shard.example.md`.

---

## Layer 3 — Deep storage

L3 is a set of sibling directories, each with its own purpose. Memory-architect owns the storage taxonomy (where things live, how they're named, what the contract is). Per-folder content schemas are owned by specialist architects where flagged.

| Directory | Purpose | One file per | Owner |
|---|---|---|---|
| `decisions/` | Per-decision audit trail. Reasoning, alternatives, trigger conditions for revisit. | Decision (`YYYY-MM-DD-<slug>.md`) | memory-architect (schema) |
| `briefs/` | Pre-event briefings — counterparty state, talking points, fallback positions, expected pushback. | Event (`YYYY-MM-DD_<event-slug>.md`) | memory-architect (schema) |
| `stakeholders/` | Per-person persistent profile. Sentiment trajectory, communication style, active threads. | Person (`<firstname-lastname>.md`) | **stakeholder-architect** — field schema; memory-architect only owns "stakeholder profiles live here" |
| `archive/` | Monthly retirement target for items archived from L1 / L2. Verbatim original text + "why archived" reasoning. | Month (`YYYY-MM.md`) | memory-architect (schema) |
| `branch-out/` | Predictive simulations — t+1 / t+2 scenarios for high-stakes situations. | Situation (`YYYY-MM-DD-<slug>.md`) | **prediction-architect** — content schema |
| `shadow/` | Shadow hypotheses (invisible to user at generation time) tracking agent prediction accuracy. Subdirs `pending/`, `resolved/`, `expired/`. | Hypothesis (`YYYY-MM-DD-<slug>-<hash>.yaml`) | **prediction-architect** — content schema |
| `calibration/` | Actor / agent prediction track records, monthly accuracy aggregations. | Various — actor scores, monthly reports | **prediction-architect** — content schema |
| `audits/` | Per-audit findings (memory consistency, dataflow staleness, etc.). | Audit run (`YYYY-MM-DD-<audit-type>.md`) | **governance-architect** — audit definitions |
| `watch/` | Weekly external scan outputs (overdue items, stakeholder cooling, etc.). | Scan (`YYYY-MM-DD.md`) | **governance-architect** — scan definitions |
| `intel/` | External market intelligence — competitor moves, market-radar outputs. | Topic or scan output | **governance-architect** (or dedicated intel-architect if added) |

**Mandatory minimum:** `decisions/`, `briefs/`, `stakeholders/`, `archive/`. Everything else is opt-in based on whether your domain needs that layer.

**Templates owned by memory-architect:**

- `templates/decision-record.template.md` + `examples/decision-record.example.md`
- `templates/brief.template.md` + `examples/brief.example.md`
- `templates/archive.template.md`

Stakeholder profile template lives in `templates/` but is owned by `stakeholder-architect`. Memory-architect only enforces the file-naming convention and the placement (`memory/stakeholders/<slug>.md`).

---

## Pointer format convention

Three forms, used consistently across all memory files:

1. **From L1 (CLAUDE_MEMORY) to L2 shard:** `→ topics/<slug>.md` — relative, grep-friendly, arrow signal makes "this is a pointer, not prose" obvious at a glance.
2. **From shard to L3 (decision / brief / archive):** repo-relative path, e.g. `memory/decisions/2026-05-04-d9-order-workflow-presets.md`. Always full path from repo root so grep across the tree finds back-references.
3. **Between shards or to knowledge:** Markdown link `[<slug>](path)` when the pointer appears inline in prose, or repo-relative path in a list.

**Why repo-relative everywhere except L1→L2?**

L1→L2 traffic is high frequency. `→ topics/<slug>.md` is shorter to type and read than `→ memory/topics/<slug>.md`. Acceptable because L1 only ever points into `memory/topics/`. Other directions are lower-frequency, and full repo-relative paths grep cleanly.

---

## Classification rule — where does this belong?

Before adding content to memory, classify. **Default is NOT L1.** L1 is a restrictive target, not a default landing zone.

| Content type | Goes to |
|---|---|
| **Decision** (architecture, product, commercial, contract — anything with reasoning + alternatives + trigger conditions) | `memory/decisions/<YYYY-MM-DD>-<slug>.md`. Add 1-line pointer to L1 only if it's a *current* blocker; otherwise the decision lives alone. |
| **Historical artifact** (meeting transcript, threaded comments verbatim, superseded version of a doc) | `memory/archive/<YYYY-MM>.md` if small-ish; `deliverables/` (outside memory) if a real document. |
| **Canonical fact** (platform constraint, decided architecture, operating principle) | Constitution patch proposal — see `governance-architect`. Not memory. |
| **Operational current state** (what I'm doing now, status of active blockers, what's on horizon) | L1 (`CLAUDE_MEMORY.md`) — but only the minimum. Move to L2 shard as soon as it gets detailed. |
| **Per-person notes** | `memory/stakeholders/<slug>.md` — owned by stakeholder-architect schema. |
| **Per-event prep** | `memory/briefs/<YYYY-MM-DD>_<event>.md`. |

**The "remember X" trap:** when a user (or you) says "remember X", classify before appending. If it's not operational-current-state, it doesn't go in L1. Append to the right L3 file and add a pointer if needed.

---

## Cadence rules

| Cadence | What | Trigger |
|---|---|---|
| **Session start** | L0 + L1 auto-load | Every session |
| **Per-edit** | MAP regen | Hook on any `memory/topics|decisions|briefs|stakeholders|archive` Edit/Write |
| **14 days** | L1 light prune | Strip strikethroughs, check size; ~5 min, no full re-read |
| **35 days** | L1 full audit | Section-by-section review; archive resolved items; graduate hot items to shards |
| **60 days** | Resolved shard retirement | Move `topics/<slug>.md` to `topics/_resolved/<slug>.md` if `status: resolved` and untouched |

Cadence state lives in `memory/audit_state.md` (one canonical file with last-run dates + thresholds). Session-start hook warns when overdue.

---

## Optional state files

Some domains need lightweight state outside the main layers:

- `memory/audit_state.md` — memory hygiene cadence + last-run dates (recommended; referenced by session-start hook)
- `memory/digest_state.md` — if you run a daily digest agent (see `digest-architect`)
- `memory/triage-heuristic.yaml` — if you have a predictive layer that needs triage rules (see `prediction-architect`)

Memory-architect provides the **placement convention** (these live at `memory/<name>.md` or `<name>.yaml`, not nested) but not their content schema.

---

## Design tradeoffs

Architectural decisions where memory-architect chose one path and the alternatives are worth knowing.

### 1. 4 layers is one more than minimum

A 3-layer model (operational / shards / archive) is simpler and works for most domains. The 4th layer (MAP) earns its place only when:

- You expect more than ~10 active L2 shards (grep is then helpful)
- Multiple agents need a single navigation entry point
- Session-start cost matters (MAP gives you the index for free)

**If you fork Giovanni for a domain with <5 expected shards and a single agent:** consider dropping MAP and grepping `memory/topics/` directly. Less infra to maintain.

### 2. Hard 300-line cap on L1 — source ran double that

The source implementation routinely sits at 600-900 lines despite the stated 300-line limit. This is a discipline problem, not a schema problem — the writer accumulated context faster than they archived. Giovanni keeps 300 lines as the hard cap and treats violation as a real warning, not advisory.

**If the cap consistently fires for you:** the right fix is more aggressive shard graduation, not raising the cap. Above ~400 lines, an L1 stops being a "cheap session start" and starts being a second knowledge base.

### 3. Topic shard frontmatter is heavy

The schema has ~10 fields. Most shards use 5-7. The unused fields stay empty (`[]`).

**Why keep them?** Consistent shape across shards means grep / agent-side scanning is reliable. If `related_decisions` is sometimes missing and sometimes empty, agents have to handle both cases. Always empty-list is cheaper.

**Lean alternative:** drop `related_branch_outs`, `related_shadows`, `affects_gates` if you don't have those layers. Keep the core 7 (slug / status / owner / last_touch / key_stakeholders / related_decisions / related_briefs / related_knowledge / related_artifacts / related_topics).

### 4. Per-month archive granularity

`memory/archive/YYYY-MM.md` aggregates everything archived in a month into one file. This is intentional — archives are read-rarely, write-once-then-frozen.

**Alternative:** one file per archived item. Higher cardinality, harder to scan retrospectively ("what got archived in May?").

**When to switch to per-item:** if your archive ratio is high (>5 archived items per week) and any single archived item is large (>200 lines verbatim), the monthly file gets unwieldy. Per-item with month subdirectory (`archive/YYYY-MM/<slug>.md`) scales better.

### 5. L3 has 10 possible subdirectories but only 4 are mandatory

`decisions/`, `briefs/`, `stakeholders/`, `archive/` are baseline. The rest (`branch-out/`, `shadow/`, `calibration/`, `audits/`, `watch/`, `intel/`) are opt-in.

**Source has all 10.** That's a sophisticated CoS setup with a predictive layer + governance hooks + external intel scanning. For most fork targets (solo founder, head of legal, head of ops), the baseline four is enough. Adding peripheral L3 subdirs without the agents to populate them creates empty folders that look broken.

### 6. Source's MAP includes a "Predictive layer" section even when shadow/branch-out are empty

This is over-design. Sections only earn their place when populated. Giovanni's MAP template generates predictive-layer rows only when those directories have content.

### 7. Strikethrough-as-soft-delete is forbidden

Source's L1 frequently uses `~~text~~` to mark items as done without actually archiving them. The result: visual chaos, archive backlog, and the writer's mental model thinking the work is cleaner than the file shows.

Giovanni's rule: strikethrough is acceptable for ≤1 session as a "verify before archive" marker. By the next session, the item is archived (moved out) or restored (unstruck). Persistent strikethrough is a drift signal flagged by the cadence hook.

### 8. No separate "person-tied notes" file

Some CoS systems give each stakeholder a journal as well as a profile. Giovanni keeps profile + journal merged into the single `stakeholders/<slug>.md` file. Sentiment trajectory and recent-interaction notes live in the same file as static profile.

**Why:** access pattern. When you load a stakeholder, you almost always want both static (role, communication style) and recent (last touch, sentiment shift). Splitting forces two reads.

---

## Cross-architect dependencies

Memory-architect produces the file-system taxonomy and storage contracts. The following live in other architects' templates:

- **Stakeholder profile field schema** (sentiment trajectory, active threads, communication style) → `stakeholder-architect`
- **Constitution pattern** (single source-of-truth document) → `governance-architect`
- **Daily digest mechanics** (what runs, when, what gets generated) → `digest-architect`
- **Predictive layer internals** (branch-out / shadow / calibration content schemas) → `prediction-architect`
- **Adversarial review workflow** (how a draft is critiqued before sending) → `adversarial-architect`
- **Hook scripts** (MAP regen, audit cadence warnings, session-start checks) → `governance-architect`
- **Slash commands** (`/digest`, `/branch-out`, `/audit`) → `slash-command-architect`

When forking Giovanni for a new domain, the memory layer alone is incomplete — you'll want at least `governance-architect` (constitution + audits) and `stakeholder-architect` (per-person schema) deployed alongside.

---

## Quick-reference: where do I put...?

| ...this thing? | ...goes here. |
|---|---|
| A decision I just made with reasoning | `memory/decisions/<YYYY-MM-DD>-<slug>.md` |
| Notes for a meeting tomorrow | `memory/briefs/<YYYY-MM-DD>_<event>.md` |
| A new active blocker | L1 (`CLAUDE_MEMORY.md`) — 1 line + pointer to shard if deep |
| Detailed state of an ongoing initiative | `memory/topics/<slug>.md` (L2 shard) |
| Verbatim meeting transcript | `memory/archive/<YYYY-MM>.md` |
| Updated profile for someone I just met with | `memory/stakeholders/<slug>.md` |
| A canonical fact about how the business works | `knowledge/` constitution patch — not memory |
| A simulation of what might happen next week | `memory/branch-out/<YYYY-MM-DD>-<slug>.md` (if predictive layer in use) |
| A "remember to check X next week" reminder | L1 "Watch list" |
