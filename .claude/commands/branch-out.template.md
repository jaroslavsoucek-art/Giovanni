---
description: Active predictive simulation for a specific situation
allowed-tools: Read, Write, Glob, Grep
---

# /branch-out

<!--
============================================================================
SPEC TEMPLATE — `slash-command-architect` will use this to generate the
runtime implementation. This file defines the contract; not the executable.

The /branch-out command runs an active predictive simulation on a high-stakes
situation. It is THE flagship command of the predictive layer.

Carry the 8 binding principles VERBATIM. They are the IP. If a fork relaxes
any of them, the output becomes hallucination wearing structured-output
costume.
============================================================================
-->

Run an active branch-out simulation on a specific situation surfaced by today's digest, a 1:1 brief, or a topic-shard escalation.

## Usage

```
/branch-out <situation-slug>
```

Example: `/branch-out dp1-renewal-call-2026-05-27`

## Process

Follow these steps strictly. The order matters.

### Step 1 — Load context

Read in this order:

- `memory/branch-out/<today>-<situation-slug>.md` if exists (else create new from digest reference)
- Each `memory/stakeholders/<slug>.md` listed in the situation's key actors
- The source signals referenced in the digest / brief / topic shard
- `memory/triage-heuristic.yaml`
- `memory/branch-out/canonical-moves.md` — reuse existing move names; never coin new variants without user confirmation
- `knowledge/<constitution-file>.md` for any constraints touching this situation

### Step 2 — Actor confidence check (HARD STOP if fails)

For each actor in the situation, classify confidence from the stakeholder profile's `profile_depth` field:

- `deep` — ≥20 touches across channels, sentiment trajectory robust, 1:1 confirmed predictions match
- `partial` — 5-20 touches, sentiment mapped, in-domain reactions predictable
- `shallow` — <5 touches, observational profile only, can't predict reactions
- `none` — actor not in `memory/stakeholders/`

**If 2+ key actors are `shallow` or `none`: STOP.** Output:

```
⚠️ Insufficient actor models for branch-out.

Shallow/missing actors:
- <actor-1>: <reason>
- <actor-2>: <reason>

Recommended next step: bootstrap profile via stakeholder-profiler
agent, or accept that this simulation cannot run.

Branch-out not executed.
```

Do NOT proceed. Do NOT generate caveats and continue. **Hard stop is hard stop.**

### Step 3 — Generate moves (max horizon t+2)

For the principal, generate 3-5 plausible response moves. Each move MUST have:

- **Canonical name** from `memory/branch-out/canonical-moves.md` (reuse > coin)
- **If new pattern**: kebab-case, descriptive of action, NOT actor-specific, NOT situation-specific. Propose to user; do not append to registry without confirmation.
- **One-line descriptor** specific to THIS situation (not generic)

Example formatting:

```
- `request-ROI-justification` — open the 2026-05-27 call by leading
  with quantified ROI summary, invite Karim to test three specific
  numbers
- `escalate-via-exec-sponsor` — activate Sarah's CFO network for
  parallel-track exec-sponsor motion before or during the call
```

### Step 4 — Predict actor responses (t+1, optionally t+2)

For each `user move × key actor`, predict the most plausible response. Use ONLY these tiers:

- `likely` — pattern-matched against actor's observed history; default response
- `possible-but-surprising` — plausible but non-default behavior
- `unlikely-but-impactful` — low probability, high consequence if it happens

**NEVER use percentages.** Violating this is a critical failure caught by `scripts/lint_rules/no_percentages_in_predictions.py`. The three tiers are the entire expressive vocabulary.

Each prediction cell SHOULD include:
- The tier label
- A short response prediction (5-15 words)
- One-line reasoning citing a pattern from the actor's profile

### Step 5 — Trade-off matrix

Generate matrix with rows = user moves, columns = ALL FIVE canonical dimensions:

- `optionality` — does this preserve future options or close them off?
- `speed` — how fast does the consequence resolve?
- `leverage` — does the principal hold framing power, or does the counterparty?
- `trust` — does this build or burn relationship capital?
- `reversibility` — can the principal back out cleanly if signals change?

Each cell: short qualitative assessment (1-2 phrases). Mark `N/A` if dimension doesn't apply.

**NO "recommended" column. NO ranking. NO "best move first" ordering.** Catched by `scripts/lint_rules/branch_out_no_recommendation.py`.

### Step 6 — Generate shadow hypotheses (INVISIBLE)

Identify 1-3 testable predictions about actor follow-up behavior in the t+1 to t+14 window. For each:

- Verify it passes the `specificity_gate` in `memory/triage-heuristic.yaml`
- Create a YAML file at `memory/shadow/pending/<YYYY-MM-DD>-<actor-slug>-<topic>-<4char-hash>.yaml`
- Use the schema from `memory/templates/shadow-hypothesis.template.md`
- Include `generated_by: branch-out:<situation-slug>` for traceability

**These hypotheses are INVISIBLE to the principal at generation time.** Do NOT mention them in the branch-out output. Do NOT discuss them with the principal. They surface only at `/shadow-review`. This is the binding anti-self-fulfilling-prophecy rule.

### Step 7 — Pass-back output

Output structure (use the branch-out template):

```markdown
# Branch-out: <situation-slug>

**Generated:** <ISO 8601 timestamp>
**Horizon:** t+1 (or t+2)
**Triggering situation:** <one-line>
**Decision at stake:** <one-line>

## Confidence note
<actor depths, t+1 vs t+2 confidence, what the matrix doesn't capture>

## Situation
<3-5 sentence summary>

## Actors involved
<each actor with slug + relationship_type + profile_depth + profile pointer>

## User's possible moves
<3-5 moves with canonical names and situation-specific descriptors>

## Predicted actor responses
<table: rows = moves, columns = actors, cells = tier + prediction + reasoning>

## Trade-off matrix
<table: rows = moves, columns = 5 canonical dimensions>

## No recommended move
<explicit callout that the absence is intentional>

## Watch points
<3-5 leading indicators between now and decision moment>

## Key question to ask yourself
<one question whose answer reframes the situation — unanswerable by agent>

## Related artifacts
<decision record draft pointer, topic shards, source brief>
```

### Step 8 — Draft decision record

After pass-back, generate `memory/decisions/<today>-<situation-slug>.md`:

```markdown
---
date: <today>
situation: <situation-slug>
status: draft
branch_out_ref: memory/branch-out/<today>-<situation-slug>.md
trigger_conditions:
---

# Decision: <situation-slug>

**Date:** <today>
**Status:** draft
**Source:** /branch-out simulation
**Related:** <branch-out artifact>

## Context
<auto-filled from branch-out situation section>

## Options considered
<auto-filled from moves section with canonical names>

## Chosen move
<EMPTY — principal fills>

## Reasoning
<EMPTY — principal fills>

## Trigger conditions for re-evaluation
<EMPTY — principal fills with concrete signals that would cause reconsidering>

## Related shadow hypotheses
<auto-filled with IDs of any shadow hypotheses touching same actors>
```

Tell the principal:

> Decision draft created at `memory/decisions/<today>-<situation-slug>.md`. Fill `chosen_move`, `reasoning`, and **`trigger_conditions`** (not optional — lint catches empty values), then commit when ready.

**DO NOT commit anything yourself.**

### Step 9 — Save branch-out artifact

Write the pass-back output (Step 7) verbatim to `memory/branch-out/<today>-<situation-slug>.md`. This is the historical record — referenced by the decision record and future shadow lookback.

## Anti-patterns (critical failures)

- Generating percentages anywhere ("70% likely") — use three tiers only
- Generating t+3 or deeper predictions — beyond t+2 is human strategy session
- Adding "recommended move" column or section to trade-off matrix
- Proceeding with caveats when 2+ actors are shallow / none
- Coining new canonical move names without registry update (decision record + user confirm)
- Surfacing shadow hypotheses in the output
- Committing decision records autonomously
- Filling `trigger_conditions` for the principal (must be principal's call)

## Cross-references

- **Template:** `memory/templates/branch-out.template.md`
- **Canonical moves:** `memory/branch-out/canonical-moves.md`
- **Triage heuristic:** `memory/triage-heuristic.yaml`
- **Shadow hypothesis template:** `memory/templates/shadow-hypothesis.template.md`
- **Full predictive layer documentation:** `docs/prediction.md`
- **Constitution section:** `knowledge/<constitution-file>.md` § "Predictive layer governance"
