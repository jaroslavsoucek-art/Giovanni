# Stakeholder Profiles — `memory/stakeholders/`

Per-person persistent state for the people whose behavior materially shapes
your work. One file per person, named `<firstname-lastname>.md` (lowercase
ASCII, hyphens, matching the `slug` frontmatter field).

This directory is L3 (deep storage) in the 4-layer memory model. It lazy-loads
on demand — the agent reads a profile when a meeting with that person is upcoming,
when a topic shard cites them in `key_stakeholders`, or when the principal
explicitly asks "what do we know about X?". Profiles do **not** auto-load at
session start.

---

## Purpose

In a single-principal or thin-team context, nobody else holds the model of
each counterparty. Memory + judgment + interaction history → externalized as
a structured file that future-you (or your agent) can read in 30 seconds.

The profile makes four downstream artifacts possible:

1. **Pre-meeting briefs** — counterparty state, hot topics, predicted reactions
   inherited directly from this file.
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
- Explicit user trigger: "bootstrap profile for X"

**Don't create a profile for:**

- One-off contacts (intro emails, single meetings)
- People you don't have direct interactions with (just hear about them)
- Broadcast audiences (mailing list recipients, channel observers)

A profile is overhead. Create it when the relationship is consequential
enough that future-you will benefit from the externalized model.

---

## Schema

Profile structure is documented in `templates/stakeholder.template.md`.
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

See `docs/stakeholder-profiles.md` for workflow detail.

---

## The `relationship_type` enum

The taxonomy matters. The same observation ("she pushed back hard on
pricing") has different operational meaning depending on relationship type:

- **peer** → debate continues; positions argued, not arbitrated
- **asymmetric-power-up** → the pushback is a near-veto; build the case or yield
- **customer** → pushback signals churn risk; relationship needs rescuing
- **counterparty** → the pushback is expected; negotiating position

Pick the framing that's dominant **today**. If it shifts (e.g. a customer
becomes a counterparty when renewal turns adversarial, or an asymmetric-power
peer joins your board and becomes asymmetric-power-up), update the field and
note the shift in Relationship history.

Hybrid framing: if the person genuinely lives across two modes (a major
customer who is also commercially adversarial in negotiations), pick the
dominant mode and name the hybrid in the body's Identity & context section.
Don't pick "counterparty" just because some interactions are negotiation —
pick it only if the whole relationship is adversarial-framed.

---

## Retention

| State | Trigger | What happens |
|---|---|---|
| `active` | Default for current relationships | File lives in `memory/stakeholders/<slug>.md` |
| `dormant` | No interaction in 90+ days but still relevant | Stays in directory; flagged in digests as cooling |
| `archived` | Relationship concluded (person left org, project ended, etc.) | After retention threshold (default 90d dormant), move to `memory/stakeholders/_archived/<slug>.md` |

The retention threshold (90 days) is configurable per
`docs/governance.config.yaml`. Stricter privacy postures may want shorter
(e.g. 30 days for ex-employees). Softer postures may want never-archive.

See `docs/stakeholder-profiles.md` for the full retention workflow including
"what to do when archived person re-engages" (reactivate + back-fill).

---

## Privacy considerations

These files contain **operational notes about real people**, including:

- Predicted reactions (your forecasts of their behavior)
- Pattern observations (their communication tics, allergies, biases)
- Relationship dynamics (where they sit in power gradients)

This is sensitive content. Before committing to a shared repository, decide:

| Approach | Tradeoff |
|---|---|
| **Commit to private repo** | Profiles become organisational asset; team can use them but exposure grows linearly with team size |
| **Personal-only via `.gitignore`** | Profiles stay private to the principal; lose backup + cross-device sync via git |
| **Encrypt at rest** (e.g. `git-crypt` on `memory/stakeholders/`) | Best of both, adds setup friction |

Decide before the first profile is committed. Migrating from public to
private later means scrubbing git history.

The default fork-time recommendation is **private repo, no extra encryption**.
If you're not sure your organization will keep the repo private, treat profile
content as if it could be read by the people profiled — and ask whether
that affects how honestly you can write the patterns down.

---

## Cross-reference contracts

Stakeholder profiles are nodes in a graph. The other nodes:

- **Topic shards** (`memory/topics/<slug>.md`) reference profile slugs in
  `key_stakeholders`. Lint validates that referenced slugs exist
  (`scripts/lint_rules/stakeholder_slug_exists.py`).
- **Decision records** (`memory/decisions/<...>.md`) reference profile slugs in
  their frontmatter `key_stakeholders` field and cite stakeholder positions
  in reasoning.
- **Briefs** (`memory/briefs/<...>.md`) cite the profile as the counterparty
  context source.

When you add a stakeholder to a topic shard, the profile's `related_topics`
should mention the shard back. Bidirectional discipline = audit-able graph.

---

## Anti-patterns

- **Single-line "supportive" snapshots** in sentiment trajectory. Worthless.
  Write the observation that produced the assessment.
- **Predictions without reasoning** in Predicted reactions. Vibes-mode predictions
  contaminate the signal. Force the reasoning line.
- **Profile as flattery** — "great guy, sharp thinker". This is not a tribute
  document. Operational predictions only.
- **Stale `last_touch`** — if you've interacted but didn't update the date, the
  digest can't flag drift correctly.
- **Letting active threads ghost** — if a thread shows no movement >30 days,
  either mark stalled and add to watch points, or close it.

---

## Bootstrap workflow

See `docs/stakeholder-profiles.md` for the step-by-step (signal gathering,
pattern extraction, profile depth heuristic, validation, commit).
