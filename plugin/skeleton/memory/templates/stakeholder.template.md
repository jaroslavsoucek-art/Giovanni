---
# ============================================================================
# Stakeholder profile frontmatter — Layer 3 (memory/stakeholders/<slug>.md)
# ============================================================================
# REQUIRED FIELDS
# ============================================================================

slug: <kebab-case-firstname-lastname>
# Unique slug. Lowercase ASCII, hyphens only. Must match filename
# (`memory/stakeholders/<slug>.md`). Also the join key used by topic shard
# `key_stakeholders`, decision `key_stakeholders`, brief `counterparty` and
# everywhere else a person is referenced. Pick a stable slug — renames break
# every cross-reference.

display_name: <Firstname Lastname>
# Human-readable name as you'd write it in prose. May include diacritics,
# accents, non-ASCII.

org: <Organisation or "independent">
# Primary affiliation. Use "self" only if the profile is the principal
# themselves (rare — usually the principal doesn't profile themselves).

role: <Their job title or functional role>
# How they identify in the room. Use their actual title where stable
# (e.g. "Lead VC partner, Series A") not an abstracted one.

relationship_type: <enum>
# Enum (binding):
#   - peer                    — symmetric authority; co-founder, equal partner,
#                               peer department head. Disagreement is debated,
#                               not arbitrated.
#   - asymmetric-power-up     — they have material authority over you /
#                               your initiative. Board director, VC with
#                               veto rights, regulator. Their preferences
#                               weight more than yours; surprises are costly.
#   - asymmetric-power-down   — you have material authority over them.
#                               Direct report, junior team member you mentor.
#                               You owe them clarity + air-cover; they owe
#                               you execution + early flags.
#   - customer                — they pay you (or you want them to). Relationship
#                               is real but the transaction frames the floor.
#   - vendor                  — you pay them. Service / supplier. Relationship
#                               matters less than reliability + cost.
#   - counterparty            — adversarial or quasi-adversarial. Opposing
#                               counsel, competitor, regulator in enforcement
#                               mode. Profile tracks negotiation patterns,
#                               not warmth.
#
# A person can have hybrid framing — e.g. a major customer who is also
# strategic enough to behave like a counterparty in renewal negotiations.
# In that case, pick the framing dominant TODAY and note the hybrid in
# the body (Identity & context section).

first_touch: YYYY-MM-DD
# Date of first material interaction. Used by:
# - relationship longevity at a glance
# - audit ("how long have we known X before this conflict?")

last_touch: YYYY-MM-DD
# Date of most recent interaction. Used by:
# - retention check (>90d dormant → status:archived consideration)
# - MAP sorting (most recently touched up top)
# - digest staleness flagging ("haven't heard from X in N days — drift signal?")

status: active
# Enum: active | dormant | archived
#   - active: regular interaction (multiple touches per quarter)
#   - dormant: no interaction in 90+ days but relationship still relevant;
#              may reactivate; keep loaded for context
#   - archived: relationship concluded; profile retained for historical
#               record. Auto-moves to `memory/stakeholders/_archived/`
#               after retention threshold (see docs/stakeholder-profiles.md).

related_topics: []
# Slugs of L2 topic shards where this stakeholder is `key_stakeholders`.
# Maintained mostly by hand; lint can flag inconsistency
# (topic shard lists slug X but X's profile doesn't list the topic, or vice-versa).

# ============================================================================
# OPTIONAL FIELDS — use only when relevant
# ============================================================================

# affiliation_secondary: <Secondary org>
# # Use when person sits across two orgs that both matter
# # (e.g. board director who is also CEO of a portfolio company).

# primary_thread: <one-line dominant context>
# # The single dominant topic where you interact. Helpful for grep when
# # many profiles exist. Updates as the relationship's centre of gravity shifts.

# touch_frequency: high | medium | low
# # Subjective freshness label, separate from last_touch date. "Low" with
# # last_touch within 7 days = anomaly worth noting.

# profile_depth: shallow | partial | deep
# # How well you actually know them:
# #   - shallow: <5 touches, can't predict reactions; profile is observational
# #   - partial: 5-20 touches across channels, can predict in-domain reactions
# #   - deep:    20+ touches, 1:1 confirmed, can predict even out-of-domain
# # Lint can warn when relationship_type=asymmetric-power-up but
# # profile_depth=shallow (high-stakes counterparty with thin signal).

---

# <Display Name> — <Role @ Org>

<!--
Body sections, in this order. Adapt content but keep the section structure
so cross-profile grep stays predictable. Length target: 80-200 lines.

A profile is a working model, not a tribute. It exists to help future-you
predict behaviour and prepare for interactions. Flattery is anti-pattern.
-->

## Identity & context

<!--
1 paragraph. Who they are in the world (role + org + tenure context),
how the relationship started, what frames your interaction today.

Skip biographical noise. Focus on the operational facts: what they do,
why you care, what they care about that touches you.

If `relationship_type` is hybrid (e.g. customer + counterparty in renewal),
name the hybrid explicitly here and what flips it from one mode to the other.
-->

<One paragraph: who, how you know them, why they matter to your work.>

## Role & decision authority

<!--
What they own / what they don't / what they influence. Critical for
not asking the wrong person for the wrong decision.

Format:
- **Owns:** <decisions they can make unilaterally>
- **Influences:** <decisions where their input weights heavily but they don't decide>
- **Doesn't own:** <decisions they cannot make, even if they sound like they can>
- **Reports to / aligned with:** <upstream stakeholders, where escalation routes>

The "doesn't own" line is often the most useful — it stops you spending
political capital on asks they can't deliver.
-->

- **Owns:** <decisions they decide>
- **Influences:** <decisions they weigh in on>
- **Doesn't own:** <decisions they can't deliver even if you ask>
- **Reports to / aligned with:** <upstream / peer relationships that matter>

## Sentiment trajectory

<!--
APPEND-ONLY TIME-SERIES. Never overwrite. Each entry: date + observation +
signal interpretation.

The discipline is what makes this useful. A single-line "supportive" snapshot
is worthless — you can't see the arc. The arc is the signal.

Format per entry:
- **YYYY-MM-DD — <channel / event>** — <what happened in 1-3 lines> —
  *signal: <warming / cooling / firming / neutral / specific shift>*

Order: reverse chronological (newest at top — easier to scan "what's recent").
Pick one ordering and stay consistent within the file.

Length: keep last ~10-15 entries inline; archive older entries to a
"Relationship history" section below or trim with explicit note
("trajectory pre-YYYY-MM archived in `memory/archive/<...>`").

Anti-pattern: "supportive", "still positive", "good guy", "great convo".
These tell future-you nothing. Force yourself to write the OBSERVATION
that produced the assessment.
-->

- **YYYY-MM-DD — <channel>** — <what happened> — *signal: <interpretation>*
- **YYYY-MM-DD — <channel>** — <what happened> — *signal: <interpretation>*
- **YYYY-MM-DD — <channel>** — <what happened> — *signal: <interpretation>*

## Communication style

<!--
How they actually communicate, not how you wish they would.

Two-sided:
1. How you address them (channel, language, register, tone)
2. How they respond (timing, length, patterns)

The second sub-section is the heads-up layer for future-you: if they
"send silence-then-email when topic matters", that pattern is worth
documenting explicitly so the next silence isn't read as disinterest.
-->

**How I address them:**
- **Channel preference:** <Slack DM / email / in-person / phone>
- **Language:** <EN / CZ / etc>
- **Register:** <formal / casual / technical>
- **Tone notes:** <e.g. "appreciates rigor, allergic to handwaving">

**How they communicate:**
- **Response time:** <typical>
- **Length:** <brief / medium / verbose>
- **Patterns:**
  - <e.g. "writes one-line provocative questions instead of statements">
  - <e.g. "silence-then-unprompted-email when topic matters — not the same as disinterest">
  - <e.g. "structured long-form when escalating, terse when ack'ing">

## Active threads

<!--
Open items between you. Each thread: short name, status, last touch, expected
next move. 3-7 typical.

Active threads have hygiene rules:
- Close threads explicitly when concluded — move to "Relationship history"
- Don't let threads ghost into the past; if no movement >30 days, mark stalled
- "Pending from them" + "Pending from me" split — clarifies who owes what

When a thread concludes, move it to "Relationship history" with the outcome.
-->

**Pending from them:**
- **<Thread name>** — waiting since YYYY-MM-DD on <what>. Expected next move: <what>.

**Pending from me:**
- **<Thread name>** — owe them <what> by YYYY-MM-DD. Current state: <state>.

## Hot topics in their head

<!--
3-5 things currently occupying THEIR attention. Not what you wish they
cared about — what they actually do.

Derived from: their recent communications, their other responsibilities,
external pressure on their role, their boss's asks.

This section directly feeds brief generation — when prepping a meeting with
this person, the brief inherits this list.

Updates: revisit monthly for active relationships, quarterly otherwise.
-->

1. **<Topic>** — <what's at stake for them, what they're tracking>
2. **<Topic>** — <what's at stake for them>
3. **<Topic>** — <what's at stake for them>

## Predicted reactions

<!--
THE DIFFERENTIATION SECTION. No competitor / off-the-shelf CoS tool has this.

For high-stakes scenarios — the ones that could materially affect your
relationship or your work — your best guess at their response.

Format (binding):
- **If <specific event>, <name> will likely <specific action>.**
  Reasoning: <observed pattern from sentiment trajectory or relationship history>.

Force specificity. "Sarah will probably be supportive" is worthless.
"If we surface dp1 churn risk in next 1:1 before quarterly numbers, Sarah
will likely add it as standing agenda item rather than escalate it to
board — pattern: she prefers calibrated awareness over discovery surprises
(see 2026-04-29 entry)" is useful.

Anti-pattern detection: if the prediction doesn't have a reasoning line
tied to specific past behavior, it's vibes. Strip it and re-write or delete.

This section pairs with the predictive layer (branch-out) if you run one —
shadow hypotheses about how a counterparty will move can be seeded from
here and tracked over time for calibration.
-->

- **If <event A>, <name> will likely <action>.** Reasoning: <pattern observed from sentiment trajectory / past behavior>.
- **If <event B>, <name> will likely <action>.** Reasoning: <pattern>.
- **If <event C>, <name> will likely <action>.** Reasoning: <pattern>.

## Watch points

<!--
Early signals to monitor. What patterns would indicate sentiment change?
Different from "Predicted reactions" — those are forecasts of specific events;
these are leading indicators.

Format:
- **<Signal>** — <what it would mean> — <where to look for it>

Examples:
- "Response time on DMs >24h after pattern of same-day" — disengagement signal
- "Public channel governance posts disappear" — signals they're routing around you
- "Forwarding articles without commentary" — silent "what's your take?" pattern

Watch points feed into governance scans (governance-architect's domain) and
digest drift detection.
-->

- **<Signal>** — <what it would mean> — <where to look>
- **<Signal>** — <what it would mean> — <where to look>

## Relationship history

<!--
Major events: introduction, conflicts, resolutions, escalations, key
decisions where they took a position.

Format per entry:
- **YYYY-MM-DD — <event>** — <what happened, what was decided, where the
  artifact lives if it became a decision record>

When an active thread concludes, it migrates here with the outcome line
appended. This makes the file the single source of relationship history.

Pre-relationship-start entries (e.g. "their public reputation before we
met" or "what their previous portfolio companies say") can go here too,
clearly labelled as second-hand.

Length: trim with year-block summaries when individual entries exceed
~25. Cite the archive location if you do.
-->

- **YYYY-MM-DD — <event>** — <what happened> — <pointer if any>
- **YYYY-MM-DD — <event>** — <what happened>

## Reasoning / source links

<!--
Back-pointers to artifacts where this stakeholder's behavior shaped the
outcome. Decision records they influenced, briefs prepped for them,
threads where their position is documented.

Format: repo-relative paths or markdown links.

Bidirectional discipline: when a decision record cites this stakeholder
in its reasoning, the decision should appear here. When a brief is
generated for an event with them, the brief should appear here.

Lint can catch some of this — see `scripts/lint_rules/stakeholder_slug_exists.py`.
-->

- `memory/decisions/<YYYY-MM-DD>-<slug>.md` — <what was decided, their role>
- `memory/briefs/<YYYY-MM-DD>_<event>.md` — <when this stakeholder was the counterparty>
- `memory/topics/<slug>.md` — <topic shard where they appear in `key_stakeholders`>
