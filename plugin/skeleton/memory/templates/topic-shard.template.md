---
# ============================================================================
# Topic shard frontmatter — Layer 2 schema
# ============================================================================
# REQUIRED FIELDS
# ============================================================================

slug: <kebab-case-unique-identifier>
# Unique slug. Must match filename (`memory/topics/<slug>.md`).

status: active
# Enum: active | partially-resolved | resolved | superseded
#   - active: work ongoing, blockers open
#   - partially-resolved: some sub-decisions made, others pending
#   - resolved: nothing more to do; auto-retired to _resolved/ after 60d untouched
#   - superseded: replaced by a different topic; pointer to successor required

owner: <stakeholder-slug or "self">
# Who's accountable for moving this forward. Usually the principal ("self"),
# but can be delegated to a specific stakeholder.

last_touch: YYYY-MM-DD
# Date of most recent material change. Used by:
# - retirement check (60d untouched + status:resolved → move to _resolved/)
# - MAP regen (sorting + freshness flag)
# - audit cadence (stale shards flagged)

key_stakeholders: [<slug>, <slug>, <slug>]
# Slugs of the people most active in this topic. Used by:
# - cross-reference (stakeholder profile mentions this topic in active threads)
# - brief generation (when a meeting touches this topic, profiles get loaded)
# 3-8 typical; >10 = topic too broad, consider splitting.

# ============================================================================
# RELATED ARTIFACTS — use [] (empty array) when none
# ============================================================================

related_decisions: []
# Paths to `memory/decisions/<...>.md` records spawned from this topic.
# Repo-relative paths.

related_briefs: []
# Paths to `memory/briefs/<...>.md` records where this topic was discussed.

related_knowledge: []
# Paths to canonical knowledge docs (`knowledge/<...>.md`) this topic
# either depends on or proposes patching.

related_artifacts: []
# Paths to deliverables produced under this topic. Outside `memory/` —
# e.g. `deliverables/<file>.xlsx`.

related_topics: []
# Slugs of other shards this topic cross-cuts. Mutual — if topic A
# references topic B in `related_topics`, B should reference A too.

# ============================================================================
# OPTIONAL FIELDS — uncomment only if the corresponding L3 layer is in use
# ============================================================================

# related_branch_outs: []
# # Paths to predictive simulations (see prediction-architect).
# # Omit if no predictive layer.

# related_shadows: []
# # Paths to shadow hypotheses tracking this topic (see prediction-architect).
# # Omit if no shadow layer.

# affects_gates: []
# # Milestone gate IDs this topic blocks/unblocks (e.g. ["G09", "G15"]).
# # Omit if no formal gate system.

---

# <Human-readable topic title>

<!--
The body is freeform Markdown. Recommended sections below, in this order.
Adapt to topic shape but keep the core four (Status, Active threads,
Trigger conditions, Risk register) for any non-trivial shard.

Length target: 80-150 lines. Above 200 lines, consider splitting into two
sub-topics or extracting a section into a separate decision record.
-->

## Status & current state

<!--
What is true today. 2-5 paragraphs. Include:
- One-line summary at the top ("** ... **" bold) suitable for L1 promotion
- Current blockers / waiting state
- Recent material change with date

If this section is changing every session, the topic is too volatile to be a
shard — keep it in L1 until it stabilises.
-->

**<One-line current state, bold>**

<Paragraph: detailed current state>

<Paragraph: what's blocked, on whom, why>

## <Section relevant to topic — e.g. "Strategic framing" or "Architecture" or "Per-stream analysis">

<!--
Domain-specific section. Use as many as the topic needs. Keep each section
focused on one dimension. Examples:
- "Strategic framing" — for negotiations
- "Architecture decisions" — for technical topics
- "Per-market analysis" — for expansion topics
- "Stakeholder positions" — for multi-party topics
-->

<Content>

## Timeline & history

<!--
Dated entries, chronological order (oldest first or newest first — pick one
and stay consistent across shards). Use this section as a local audit trail
BEFORE graduating an entry to a `memory/decisions/<...>.md` record.

Format per entry:
- **YYYY-MM-DD** — what happened, in 1-3 lines. Pointer to source (email,
  Slack thread, doc) for provenance.

When an entry becomes a real decision (multi-party, with reasoning + alternatives),
graduate it to `memory/decisions/<YYYY-MM-DD>-<slug>.md` and add a pointer here.
-->

- **YYYY-MM-DD** — <event>
- **YYYY-MM-DD** — <event>

## Active threads

<!--
Open sub-actions. Each thread: who owns, what's pending, expected next move.
3-7 threads typical.
-->

**Pending from <stakeholder>:** <what>

**Pending from <stakeholder>:** <what>

## Trigger conditions

<!--
What would cause this topic to advance, branch, or close. These are the
"watch for X" signals that the principal should be alert to.

Use this section as input to:
- watch-list scans (governance-architect)
- branch-out predictive simulations (prediction-architect)
- decision record `trigger_conditions` fields (when graduating a sub-decision)
-->

- **<Signal>** — <what it would mean / what to do>
- **<Signal>** — <what it would mean / what to do>

## Open questions

<!--
Explicit [TBD] items. Each question: what's unknown, who can answer, why blocked.
Different from "Active threads" — threads are work-in-flight; questions are
gating decisions waiting on input.
-->

- **<Question>** — needs <owner>. Blocked on <reason>.
- **<Question>** — needs <owner>. Blocked on <reason>.

## Risk register

<!--
Known failure modes + mitigations. Format:
- **Risk <letter>:** <description>. Mitigation: <plan>.
- ~~Risk <letter>~~ — CLOSED <date> (<reason>). [strikethrough OK here because risks
  are archived in-place; the shard IS the record]

Risks that materialise should graduate to active blockers in L1 (with pointer
back here) and the corresponding mitigation should become an active thread.
-->

- **Risk A:** <description>. Mitigation: <plan>.
- **Risk B:** <description>. Mitigation: <plan>.

## Deliverables

<!--
Pointers to artifacts produced under this topic. These should also appear in
`related_artifacts` frontmatter — this section gives them human context.
-->

- `deliverables/<file>` — <what it is>
- `memory/decisions/<date>-<slug>.md` — <what was decided>
- `memory/briefs/<date>_<event>.md` — <when this topic was prepped>
