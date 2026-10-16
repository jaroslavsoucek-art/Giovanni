---
# ============================================================================
# Branch-out simulation frontmatter — Layer 3 (memory/branch-out/<slug>.md)
# ============================================================================
# A branch-out is a STRUCTURED PREDICTIVE SIMULATION for a high-stakes situation.
# Used when a decision is upcoming, multiple actors are involved, and the user
# wants to see the trade-off landscape laid out before committing.
#
# Filename convention: memory/branch-out/<YYYY-MM-DD>-<situation-slug>.md
#
# BINDING RULES carried by this template:
#   1. No percentages. Three tiers only: likely / possible-but-surprising / unlikely-but-impactful.
#   2. Max horizon t+2 actor turns. Anything beyond requires human strategy session.
#   3. Hard stop on shallow actors — if 2+ key actors have profile_depth: shallow or no profile,
#      /branch-out STOPS. No caveat-degraded output. (Enforced by /branch-out command, not template.)
#   4. No "recommended move". Trade-off matrix is generative, not prescriptive.
#   5. Canonical move names from memory/branch-out/canonical-moves.md. Reuse > coin.
#   6. Shadow hypotheses dropped during/after branch-out are INVISIBLE to user — stored in
#      memory/shadow/pending/ and only surface at /shadow-review.
# ============================================================================

slug: <kebab-case-situation-slug>
# Unique slug. Lowercase ASCII, hyphens only. Matches filename suffix.

created: YYYY-MM-DD
# Date the branch-out was generated.

topic: <one-line topic of the simulation>
# Human-readable summary, e.g. "DP1 renewal call with new CFO Karim".

horizon: t+1
# Enum (binding): t+1 | t+2
# t+1 = one user move + one actor response.
# t+2 = additional actor counter-move OR knock-on by second actor.
# NEVER t+3 or deeper. Beyond t+2 is human strategy session, not agentic prediction.

key_actors: [<slug>, <slug>, ...]
# Stakeholder slugs (matching memory/stakeholders/<slug>.md). Order by salience.
# Each MUST have a profile and profile_depth: deep | partial (NOT shallow / none).

triggering_situation: <one-line situation that triggered this branch-out>
# E.g. "Karim Solanki schedules 2026-05-27 evaluation call after Diane departure".

decision_at_stake: <one-line description of what the user must decide>
# E.g. "How to frame the 2026-05-27 call: relationship-led, ROI-led, or hybrid".

status: draft
# Enum (binding):
#   - draft: simulation generated, not yet used in decision
#   - active: decision pending, simulation referenced in upcoming actions
#   - closed-resolved: decision made, outcome known, retained for calibration
#   - closed-overtaken-by-events: situation changed before decision — superseded

related_stakeholders: []
# Same as key_actors most of the time; may include secondary actors not modeled in the matrix.

related_decisions: []
# Pointers to decision records spawned from this branch-out.

related_shadow_hypotheses: []
# Shadow hypothesis IDs dropped during/after this branch-out. NOT shown to user
# at generation time — listed here for traceability at /shadow-review only.

related_topics: []
# Topic shards this situation touches.

---

# Branch-out: <situation slug>

<!--
This is a PREDICTIVE SIMULATION, not a recommendation. The agent surfaces
consequence space; the user decides.

LENGTH GUIDANCE: 100-250 lines. If under 80, the matrix is shallow. If over
300, you're over-fitting — the simulation should be readable in one screen.

ANTI-PATTERNS that should never appear in this artifact:
- Percentages anywhere ("70% likely", "high confidence ~85%") — three tiers only
- A "Recommended" column in any matrix
- An "Agent suggests..." or "Best path..." callout
- t+3 or deeper predictions
- Predicted moves whose actor lacks a profile (or has profile_depth: shallow)
- Reasoning that says "the agent thinks..." — agent has no opinion; surface trade-offs
-->

**Generated:** <ISO 8601 timestamp>
**Horizon:** t+1 (or t+2 — never t+3+)
**Triggering situation:** <one-line summary>
**Decision at stake:** <one-line decision the user faces>

## Confidence note

<!--
Open with the confidence-bounding note. This is the agent's accountability for
the simulation it just produced — what it modeled, what it could not model,
where predictions are higher / lower confidence.

Structure (binding):
- Actor model depth per actor (deep / partial — anything shallow or missing
  triggered /branch-out STOP, so by construction this list only has deep/partial)
- Confidence at t+1 vs t+2 (t+1 is pattern-matched against actor history;
  t+2 is structurally derived and inherently speculative)
- What the matrix does NOT capture (3-5 bullets — political context, second-
  order effects, things requiring human judgment)
-->

- **Actor model depth:** <actor-1> `deep` · <actor-2> `partial` · <actor-3> `deep`
- **Predictions at t+1 are higher confidence; at t+2 are inherently speculative.**
- **What this matrix does NOT capture:**
  - <Factor 1 — e.g. political context outside the modeled actors>
  - <Factor 2 — e.g. second-order effects on related stakeholders not in the matrix>
  - <Factor 3 — e.g. signals requiring human judgment of tone / register>

## Situation

<!--
3-5 sentences. What's happening. Who, what's at stake, what time horizon.
Cite source signals (DMs, emails, decision records) with dates.

Anti-pattern: narrative essay. Be operationally precise.
-->

<3-5 sentence situation summary citing source signals.>

## Actors involved

<!--
List each key actor with:
- Slug + display name
- Relationship type (asymmetric-power-up / peer / customer / vendor / counterparty)
- Profile depth (deep / partial — must NOT be shallow or none per binding rule #3)
- Pointer to profile

Format:
- **<display-name> (`<slug>`)** — <relationship_type>, `profile_depth: <depth>` — `memory/stakeholders/<slug>.md`
-->

- **<Display Name> (`<slug>`)** — <relationship_type>, `profile_depth: <depth>` — `memory/stakeholders/<slug>.md`
- **<Display Name> (`<slug>`)** — <relationship_type>, `profile_depth: <depth>` — `memory/stakeholders/<slug>.md`

## User's possible moves

<!--
3-5 plausible response moves the principal might take. Each move MUST:
- Use canonical name from memory/branch-out/canonical-moves.md (reuse > coin)
- Have a one-line descriptor specific to THIS situation (not generic)
- Be operationally distinct from the others (not three variations of the same move)

Format:
- `<canonical-move-name>` — <situation-specific descriptor in one line>

Example:
- `request-ROI-justification` — open the 2026-05-27 call by leading with
  quantified ROI summary; ask Karim to test the numbers
-->

- `<canonical-move-name>` — <situation-specific descriptor>
- `<canonical-move-name>` — <situation-specific descriptor>
- `<canonical-move-name>` — <situation-specific descriptor>
- `<canonical-move-name>` — <situation-specific descriptor>

## Predicted actor responses

<!--
THIS IS THE CORE OF THE SIMULATION.

Rows = user moves (from section above).
Columns = key actors (from "Actors involved").
Each cell = predicted response WITH tier label.

Tier labels are BINDING:
- likely — pattern-matched against actor's history; default response
- possible-but-surprising — plausible but non-default; would not be the
  first prediction
- unlikely-but-impactful — low probability, high consequence if it happens

NEVER use percentages. NEVER hedge with "70% likely", "high confidence", etc.
The three tiers are the entire expressive vocabulary.

Each cell SHOULD include:
- The tier label
- A short response prediction (5-15 words)
- Optional: one-line reasoning citing a pattern from the actor's profile

The reasoning citation is what makes this auditable later (shadow lookback
and calibration both depend on it).
-->

| User move | <Actor 1> (<depth>) | <Actor 2> (<depth>) | <Actor 3> (<depth>) |
|-----------|---------------------|---------------------|---------------------|
| `<move-1>` | likely — <response> (pattern: <citation>) | possible-but-surprising — <response> | likely — <response> |
| `<move-2>` | possible-but-surprising — <response> | likely — <response> | unlikely-but-impactful — <response> |
| `<move-3>` | likely — <response> | possible-but-surprising — <response> | likely — <response> |
| `<move-4>` | unlikely-but-impactful — <response> | likely — <response> | possible-but-surprising — <response> |

## Trade-off matrix

<!--
Rows = user moves.
Columns = FIVE canonical dimensions (binding — these five, no more, no less):
- optionality (does this preserve future options or close them off?)
- speed (how fast does the consequence resolve?)
- leverage (does the principal hold framing power, or does the counterparty?)
- trust (does this build or burn relationship capital with key actors?)
- reversibility (can the principal back out cleanly if signals change?)

Each cell: short qualitative assessment (1-2 phrases). Mark N/A if the
dimension doesn't apply to a particular move.

NO "recommended" column. NO ranking. NO "best move first" ordering.
This is GENERATIVE — surfacing consequence space, not prescribing.

If you find yourself wanting to add a "recommendation" column: stop.
That column violates a binding rule. The principal decides; the agent
surfaces structure.
-->

| User move | optionality | speed | leverage | trust | reversibility |
|-----------|-------------|-------|----------|-------|---------------|
| `<move-1>` | high — <why> | medium — <why> | high — <why> | medium — <why> | high — <why> |
| `<move-2>` | low — <why> | high — <why> | medium — <why> | low — <why> | low — <why> |
| `<move-3>` | medium — <why> | low — <why> | low — <why> | high — <why> | medium — <why> |
| `<move-4>` | high — <why> | medium — <why> | medium — <why> | medium — <why> | high — <why> |

## No recommended move

<!--
EXPLICIT CALLOUT. Always include this section.

The absence of a "recommended move" is intentional. The trade-off matrix
surfaces consequences; the principal weighs them against context the
agent cannot see (political weight, gut, prior commitments, the long
shadow of relationship history).

If a reader of this artifact ever wonders "but which move does the agent
recommend?" — the answer is "the agent has no recommendation, by design".

The callout below is the contract.
-->

This branch-out intentionally does not recommend a move. The trade-off matrix is generative, not prescriptive. The principal weighs the dimensions against context not present in the matrix — political weight, gut judgment, prior commitments, long-running relationship history. The agent's role ends at surfacing the consequence space.

## Watch points

<!--
3-5 leading indicators the principal should monitor between now and the
decision moment. Different from "predicted responses" — those are forecasts
of explicit moves; these are early signals that would update the prediction.

Format:
- **<Signal>** — <what it would mean> — <where to look for it>

Example:
- **Karim's EA Mira's scheduling tone shift** — if scheduling friction goes
  up (cancellations, narrow windows), Karim is deprioritizing — look in
  EA email threads, Mira's tone on confirmation
-->

- **<Signal>** — <what it would mean> — <where to look>
- **<Signal>** — <what it would mean> — <where to look>
- **<Signal>** — <what it would mean> — <where to look>

## Key question to ask yourself

<!--
ONE targeted question that surfaces what the matrix cannot decide for the
principal. Not "which move?" — that's the recommendation creep the matrix
explicitly refuses. Rather, a question whose answer reframes the situation.

Examples:
- "Is the relationship recoverable, or is this already a counterparty negotiation?"
- "Are you optimizing for renewal signature, or for the cohort 2 reference call
  that depends on it?"

The question should be unanswerable by the agent (requires principal judgment).
That's what makes it useful.
-->

<One question whose answer reframes the situation. Unanswerable by agent.>

## Related artifacts

<!--
Cross-references for traceability:
- Decision record this simulation feeds (created by /branch-out Step 7, EMPTY
  until principal fills)
- Shadow hypotheses dropped (HIDDEN from user at generation — referenced here
  for /shadow-review traceability)
- Topic shard(s) this situation belongs to
- Source briefs / source signals
-->

- **Decision record (draft):** `memory/decisions/<YYYY-MM-DD>-<situation-slug>.md` (created by /branch-out — principal fills `chosen_move`, `reasoning`, `trigger_conditions`)
- **Shadow hypotheses:** `<list IDs — these are INVISIBLE to principal at generation; only revealed at /shadow-review>`
- **Topic shards:** `memory/topics/<slug>.md`
- **Source brief:** `memory/briefs/<YYYY-MM-DD>_<event>.md`
- **Source signals:** <chat / email / decision-record citations>

<!--
DO NOT add a "summary" or "agent recommendation" or "agent notes" section
below this point. The artifact ends here.
-->
