# Stakeholder Profiles — `memory/stakeholders/`

Per-person persistent state for the people whose behavior materially shapes
Alex's work at Lattice Finance. One file per person, named
`<firstname-lastname>.md` (lowercase ASCII, hyphens, matching the `slug`
frontmatter field).

This directory is L3 (deep storage) in the 4-layer memory model. It lazy-loads
on demand — the agent reads a profile when a meeting with that person is upcoming,
when a topic shard cites them in `key_stakeholders`, or when Alex explicitly
asks "what do we know about X?". Profiles do **not** auto-load at session start.

> **The principal is not profiled.** Alex Park (co-founder & CEO) is the owner
> of this memory, referenced as `owner: self` in topic-shard frontmatter. There
> is no `alex-park.md`, and `alex-park` never appears in any `key_stakeholders`
> or `related_topics` list. You don't profile yourself.

---

## Current profiles

| Slug | Name | Role / Org | `relationship_type` | Depth | Related topics |
|---|---|---|---|---|---|
| `morgan-chen` | Morgan Chen | Co-founder & CTO, Lattice Finance | `peer` | deep | dp1-renewal, vp-eng-hire, pricing-v2 |
| `sarah-vyas` | Sarah Vyas | Lead VC partner (Series A) & board director, Meridian Ventures | `asymmetric-power-up` | deep | dp1-renewal, pricing-v2, vp-eng-hire, series-b-prep |
| `lattice-design-partner-1` | Design Partner 1 (Helios Holdings) | Largest customer, €180K ARR, renewal Q3 2026 | `customer` | partial | dp1-renewal, pricing-v2 |
| `priya-shah` | Priya Shah | Head of Sales, Lattice Finance | `asymmetric-power-down` | partial | dp1-renewal, pricing-v2, series-b-prep |

Notes:

- **`lattice-design-partner-1`** is a *customer* tipping toward *counterparty*
  for the renewal cycle. The new buyer-of-record, **Karim Solanki** (Helios
  CFO), is tracked **inside** this profile — there is no separate `karim-solanki`
  file. The original champion, Diane Martens, departed 2026-04-12; the profile
  documents the rebuild of the relationship at CFO level.

---

## Named, not yet profiled

These people are referenced in prose across memory but do not (yet) meet the
bootstrap bar. Mention them by name; do **not** put them in any
`key_stakeholders` list until a profile exists.

| Name | Why named | Why not profiled yet |
|---|---|---|
| `david-tannen` | Independent board director (ex-CFO public fintech); quarterly board | Interaction is quarterly + mediated through Sarah; thin direct signal |
| `marcus-liu` | Board observer (smaller fund); quarterly board, occasional intros | Observer seat; low direct interaction |
| `lattice-design-partner-2` | Design partner, €120K ARR, healthy | Stable account, no active decision pressure |
| `lattice-design-partner-3` | Design partner, €60K ARR, scaling slowly | Low touch, no active thread |
| `compliance-vendor-x` | SOC 2 audit firm, mid-audit | `vendor` — reliability matters more than a behavioral model; engagement is bounded |
| `recruiter-firm-y` | Retained eng recruiter (VP Eng search) | `vendor` — transactional; no per-person model needed |
| `alina-crisan` | VP Eng finalist (candidate) | Pre-hire; profile only if she signs and becomes a colleague |

Promotion rule: when one of these crosses a bootstrap criterion (see below),
create the profile and add the slug to the relevant topic shard's
`key_stakeholders`.

---

## Purpose

In a single-principal or thin-team context, nobody else holds the model of
each counterparty. Memory + judgment + interaction history → externalized as
a structured file that future-Alex (or the agent) can read in 30 seconds.

The profile makes four downstream artifacts possible:

1. **Pre-meeting briefs** — counterparty state, hot topics, predicted reactions
   inherited directly from this file (e.g. the 2026-05-27 dp1 CFO intro brief).
2. **Adversarial review** — drafts get reviewed with recipient context loaded
   ("would Sarah read this as supportive or condescending?").
3. **Drift detection** — sentiment trajectory changes flagged in digests.
4. **Tone matching** — communication style section guides drafted messages.

---

## When to create a profile

Bootstrap criteria — **any** of:

- Person appears in ≥2 decision records as a stakeholder
- Person attends ≥3 standing meetings (recurring 1:1, working group, board)
- Person has a named active thread that has lived >14 days
- Person is named in `key_stakeholders` of any topic shard
- Explicit trigger: "bootstrap profile for X"

**Don't create a profile for:**

- One-off contacts (intro emails, single meetings)
- People you don't have direct interactions with (just hear about them)
- Broadcast audiences (mailing list recipients, channel observers)

A profile is overhead. Create it when the relationship is consequential
enough that future-Alex will benefit from the externalized model. The
"named, not yet profiled" list above is the holding pen for people who
matter but haven't crossed the bar.

---

## Schema

Profile structure is documented in `../templates/stakeholder.template.md`.
Required frontmatter fields:

- `slug` — kebab-case unique identifier (matches filename)
- `display_name` — human-readable name
- `org` — primary affiliation
- `role` — their functional role
- `relationship_type` — enum: `peer` | `asymmetric-power-up` | `asymmetric-power-down` | `customer` | `vendor` | `counterparty`
- `first_touch` — date of first material interaction
- `last_touch` — date of most recent
- `status` — `active` | `dormant` | `archived`
- `related_topics` — slugs of L2 shards referencing this person

Required body sections:

1. Identity & context
2. Role & decision authority
3. **Sentiment trajectory** — append-only time-series (binding discipline)
4. Communication style
5. Active threads
6. Hot topics in their head
7. **Predicted reactions** — specific forecasts with reasoning (THE differentiation)
8. Watch points
9. Relationship history
10. Reasoning / source links

Note: the **Predicted reactions** section must not use numeric percentages —
the predictive layer uses `likely` / `possible-but-surprising` /
`unlikely-but-impactful` framing (enforced by
`scripts/lint_rules/no_percentages_in_predictions.py`).

---

## The `relationship_type` enum

The taxonomy matters. The same observation ("she pushed back hard on
pricing") has different operational meaning depending on relationship type:

- **peer** → debate continues; positions argued, not arbitrated (Morgan)
- **asymmetric-power-up** → the pushback is a near-veto; build the case or yield (Sarah)
- **asymmetric-power-down** → you owe clarity + air-cover; they owe execution + early flags (Priya)
- **customer** → pushback signals churn risk; relationship needs rescuing (Helios / dp1)
- **counterparty** → the pushback is expected; negotiating position

Pick the framing that's dominant **today**. If it shifts (e.g. dp1's renewal
turns fully adversarial and the account becomes a `counterparty`), update the
field and note the shift in Relationship history. dp1 is the live example of a
`customer` carrying a counterparty overlay for one cycle — the hybrid is named
in that profile's Identity & context.

---

## Retention

| State | Trigger | What happens |
|---|---|---|
| `active` | Default for current relationships | File lives in `memory/stakeholders/<slug>.md` |
| `dormant` | No interaction in 90+ days but still relevant | Stays in directory; flagged in digests as cooling |
| `archived` | Relationship concluded (person left org, project ended, etc.) | After retention threshold (default 90d dormant), move to `memory/stakeholders/_archived/<slug>.md` |

The retention threshold (90 days) is configurable per
`docs/governance.config.yaml`.

---

## Privacy considerations

These files contain **operational notes about real people** — predicted
reactions, pattern observations, and relationship dynamics. This is sensitive
content; the Lattice fork is a **private repo, no extra encryption** by
default. If you can't guarantee the repo stays private, treat profile content
as if it could be read by the people profiled — and ask whether that affects
how honestly you can write the patterns down.

---

## Cross-reference contracts

Stakeholder profiles are nodes in a graph. The other nodes:

- **Topic shards** (`memory/topics/<slug>.md`) reference profile slugs in
  `key_stakeholders`. Lint validates that referenced slugs exist
  (`scripts/lint_rules/stakeholder_slug_exists.py`). The only slugs allowed in
  any shard's `key_stakeholders` are the four above.
- **Decision records** (`memory/decisions/<...>.md`) reference profile slugs
  and cite stakeholder positions in reasoning.
- **Briefs** (`memory/briefs/<...>.md`) cite the profile as the counterparty
  context source.

When you add a stakeholder to a topic shard, the profile's `related_topics`
should mention the shard back. Bidirectional discipline = audit-able graph.

---

## Anti-patterns

- **Single-line "supportive" snapshots** in sentiment trajectory. Worthless.
  Write the observation that produced the assessment.
- **Predictions without reasoning** in Predicted reactions. Force the reasoning line.
- **Profile as flattery** — "great guy, sharp thinker". Operational predictions only.
- **Stale `last_touch`** — if you've interacted but didn't update the date, the
  digest can't flag drift correctly.
- **Letting active threads ghost** — if a thread shows no movement >30 days,
  either mark stalled and add to watch points, or close it.
- **Profiling the principal or a sub-account contact** — no `alex-park.md`;
  Karim lives inside `lattice-design-partner-1`, not a file of his own.
