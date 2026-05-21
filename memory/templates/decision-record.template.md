---
# ============================================================================
# Decision record frontmatter — Layer 3 schema
# ============================================================================
# Filename convention: memory/decisions/YYYY-MM-DD-<slug>.md
# Frontmatter is optional but recommended for status filtering + MAP regen.
# ============================================================================

date: YYYY-MM-DD
# Date the decision was made (not the date this file was written).

situation: <kebab-case-slug>
# Slug matching filename (without date prefix).

status: draft
# Enum: draft | resolved | partially-resolved | superseded | deferred
#   - draft: decision proposed but not committed (e.g. awaiting principal sign-off)
#   - resolved: decided, no open sub-questions
#   - partially-resolved: top-level decided, sub-decisions pending
#   - superseded: replaced by later decision (pointer to successor required)
#   - deferred: explicitly punted; trigger conditions for revisit must be filled

# Optional supporting fields:

# supersedes_blocker: <blocker-slug>
# # If this decision closes out an L1 blocker, name it here so audit can verify
# # the blocker was removed from L1 in the same commit.

# review_path: <open | closed>
# # Whether this decision can be re-opened. Useful when distinguishing
# # tactical commits (review_path: open) from architectural ones (closed).

# effective: YYYY-MM-DD
# # Date the decision takes effect, if different from `date`. Common for
# # role transitions, policy changes, etc.

# related_topics: [<slug>, <slug>]
# # Shards that should reference this decision in their related_decisions.

# related_stakeholders: [<slug>, <slug>]
# # Stakeholders directly party to or affected by the decision.

# related_knowledge: [<repo-relative-path>, ...]
# # Knowledge docs that need patching as a consequence.

# affects_constitution_sections: []
# # If the decision changes a canonical fact, list the constitution sections
# # that need updating. governance-architect's audit verifies these were
# # actually patched.

---

# Decision: <Human-readable title — what was decided>

<!--
Title format: "Decision: <action> — <subject>"
Examples:
- "Decision: HU launch price tactically confirmed at €19.90, future-flexible"
- "Decision: VP Engineering hire deferred to Q3, contractor bridge instead"

Avoid passive ("was decided"); state the decision in active voice.
-->

**Date:** YYYY-MM-DD
**Status:** <status>
**Source:** <how the decision was reached — meeting, async thread, principal solo decision>
**Related:** <pointers to relevant shards / knowledge — repo-relative paths or markdown links>

<!--
"Source" matters for provenance. Examples:
- "Source: Principal + <counterparty> 1:1 (Teams), YYYY-MM-DD HH:MM"
- "Source: Async thread <link>, decided YYYY-MM-DD by principal"
- "Source: Internal review session <date>, attendees: <list>"

This is the audit trail for who was in the room.
-->

## Decision

<!--
The decision itself. 1-3 sentences. State what's being committed to, not why
(reasoning comes next). Use active voice.

If the decision has sub-parts (e.g. "tactical now, review path open"),
state both the commit and the optionality explicitly.
-->

<What was decided.>

## Reasoning

<!--
Why this and not alternatives. 3-8 bullet points.

Each bullet should answer one of:
- What evidence / data drove this?
- What constraint forced this option?
- What was the alternative and why was it rejected?

If reasoning is unknown ("principal decided, didn't explain"), write `[TBD: principal
to fill]` rather than fabricating. A blank reasoning field with `[TBD]` is honest;
invented reasoning is technical debt.
-->

- <Reason / evidence / data point>
- <Reason / evidence / data point>
- <Alternative considered + why rejected>

## Alternatives considered

<!--
Optional but recommended for non-trivial decisions. Each alternative:
- What it was
- Why it was rejected (or deferred)

For tactical / quick decisions, this section can be omitted. For architectural /
commercial decisions, alternatives are mandatory — without them, the decision
can't be revisited intelligently when triggers fire.
-->

- **<Alternative A>:** <description>. Rejected because <reason>.
- **<Alternative B>:** <description>. Deferred because <reason>.

## Implications

<!--
What changes as a result. Group into sub-sections if multi-domain. Common
sub-sections:
- Operational (what we do differently starting now)
- Stakeholder (who needs to be told, who's affected)
- Technical (system changes, dependencies)
- Commercial (contract / pricing / GTM impact)
- Communication (internal vs external)

If implications cross-cut many areas, this section can be the longest in the doc.
That's fine — implications are the executable part of a decision.
-->

### <Sub-section, e.g. "Operational">

- <Implication>
- <Implication>

### <Sub-section, e.g. "Stakeholder">

- <Implication>
- <Implication>

## Trigger conditions (re-evaluate)

<!--
What would cause this decision to be revisited. THIS FIELD MUST NOT BE EMPTY.

Examples:
- Quantitative thresholds: "If churn > X% sustained for 2 months"
- Counterparty moves: "If <competitor> ships <feature>"
- Time-based: "Quarterly review every 90 days"
- Dependency: "If <upstream decision> changes"

A decision without trigger conditions is implicitly forever, which is almost
never the right framing. Even "permanent" decisions can be revisited; the
question is on what signal.

For deferred decisions (status: deferred), this section is doubly important —
it's the only way the deferred item ever surfaces again.
-->

- <Threshold / signal / time>
- <Threshold / signal / time>

## Open follow-ups

<!--
Sub-decisions or actions that fall out of this decision but aren't decided yet.
Each item: what, who owns, by when.

Different from "trigger conditions" — follow-ups are immediate executables;
triggers are watch-for signals.
-->

- **<Action>** — <owner>, by <date>
- **<Action>** — <owner>, by <date>

## Closed follow-ups

<!--
Items previously open that have since closed. Acceptable use of strikethrough
here — decision records are write-once-then-audit-trail; ~~strike~~ marks
closure without losing the audit trail.

Each: ~~item~~ — closed YYYY-MM-DD (reason).
-->

- ~~<Action>~~ — closed YYYY-MM-DD (<reason>)

## Provenance

<!--
Concrete sourcing. Where does this decision live in external systems? Acceptable
sources:
- Verbal report from principal (note date + context)
- Email / Slack message ID
- Meeting recording or notes file
- External doc with version + last-modified

This section makes the record auditable months later when memory has shifted.
-->

- **Source:** <how>
- **Channel:** <where the decision was reached>
- **Attendees / participants:** <who was in the room>
- **External reference:** <doc / link / message ID>
