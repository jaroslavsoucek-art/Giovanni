---
description: Active predictive simulation for a specific situation — routes to prediction-runtime in branch-out mode. Hard-stops on shallow actors.
allowed-tools: Task, Read, Write, Glob, Grep
---

# /branch-out

Run an active predictive simulation on a high-stakes situation surfaced by today's digest, a 1:1 brief, or a topic-shard escalation. This command is a **thin shell** — the 8 binding principles (no percentages, max horizon t+2, hard stop on shallow actors, no recommended move, canonical names from registry, invisible shadow hypotheses, adversarial lookback, decision records draft only) live in the `prediction-runtime` agent. This file is the invocation contract.

## Usage

```
/branch-out <situation-slug>            # required positional
/branch-out <situation-slug> --from-digest    # use today's digest as triage source
```

Example: `/branch-out fundraise-followup-call-2026-05-27`

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `<situation-slug>` | positional, required | — | Kebab-case identifier for the situation. Must match the slug surfaced in today's `/digest` "Active branch-out candidates", a brief reference, or a topic shard escalation. Used as primary key in `memory/branch-out/<today>-<slug>.md` and the decision record draft. |
| `--from-digest` | boolean flag | off | Pull triage context from today's `/digest` rendered output (must have run earlier today). Without this flag, the orchestrator infers situation context from existing files or asks the principal. |

If `<situation-slug>` missing → STOP: `ERROR: /branch-out requires <situation-slug>. Usage: /branch-out <kebab-case-slug>`.

## Pre-flight (binding — STOP on failure)

Before spawning `prediction-runtime`:

1. **CWD check.** Working directory is a Giovanni repo (presence of `memory/triage-heuristic.yaml` + `knowledge/<constitution>.md`). Otherwise STOP with diagnostic.
2. **Agent definition present.** `.claude/agents/prediction-runtime.md` exists. Missing → STOP: `ERROR: prediction-runtime agent definition missing. Cannot run /branch-out.`
3. **Triage heuristic present.** `memory/triage-heuristic.yaml` parses. Missing or malformed → STOP: `ERROR: memory/triage-heuristic.yaml missing or unparseable. Predictive layer is not configured.`
4. **Canonical moves registry present.** `memory/branch-out/canonical-moves.md` exists. Missing → STOP: `ERROR: memory/branch-out/canonical-moves.md missing. Register canonical move names per docs/prediction.md before running /branch-out.`
5. **No stale draft for today.** If `memory/decisions/<today>-<situation-slug>.md` already exists with `status: draft`, surface a warning (not a STOP): `WARN: Decision draft for <slug> already exists from earlier run. The new run will overwrite. Proceed? [y/N]`. Default = abort.

The hard stop for shallow actors lives **inside** `prediction-runtime` (Step 2), not at pre-flight — the agent needs to read each profile to make that determination. The orchestrator does not pre-check.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Spawn `prediction-runtime`** via `Task` with:
   ```
   subagent_type: prediction-runtime
   mode: branch-out
   situation_slug: <slug>
   from_digest: true | false
   ```
3. **Wait for agent return.** The agent produces either:
   - **Successful run:** branch-out artifact at `memory/branch-out/<today>-<slug>.md` + decision record draft at `memory/decisions/<today>-<slug>.md` + (silently) shadow hypothesis YAMLs in `memory/shadow/pending/`.
   - **Hard stop (shallow actors):** structured stop message — no artifacts written, no shadow hypotheses generated. See `prediction-runtime` Step 2.
4. **Relay agent output verbatim** to chat. For successful runs, include the principal-action hint: "Fill `chosen_move`, `reasoning`, and `trigger_conditions` in the decision draft, then commit when ready."
5. **Do NOT commit.** Principal commits via git workflow.

## Hard-stop behavior

If `prediction-runtime` returns the shallow-actor stop, the orchestrator:

- Relays the stop message verbatim
- Does NOT auto-spawn `profile-bootstrap` to enrich actors (principal decides)
- Does NOT generate caveats and continue
- Does NOT write a partial artifact

Hard stop is hard stop. Binding principle 3 from `prediction-runtime`.

## Output behavior

- **Render target:** chat (the pass-back structured output)
- **Persistent artifacts (unstaged):**
  - `memory/branch-out/<today>-<situation-slug>.md` — historical record
  - `memory/decisions/<today>-<situation-slug>.md` — decision record draft with empty `chosen_move`, `reasoning`, `trigger_conditions`
  - `memory/shadow/pending/<YYYY-MM-DD>-<actor>-<topic>-<hash>.yaml` × 1-3 — invisible to principal, surfaces at `/shadow-review`
- **No auto-commit.** Principal reviews + commits in batch.

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Agent failure** (timeout, crash, malformed return) → surface structured error to chat. Do NOT retry automatically. Principal decides.
- **Stale draft warning** (decision record exists for today) → ask principal; abort by default.
- **Shallow actor hard stop** → relay verbatim, do not soften.

## Cross-references

- **Agent (executor):** `.claude/agents/prediction-runtime.md` (mode: branch-out)
- **Binding principles:** `docs/prediction.md` § 8 binding principles
- **Canonical moves registry:** `memory/branch-out/canonical-moves.md`
- **Triage heuristic:** `memory/triage-heuristic.yaml`
- **Templates:** `memory/templates/branch-out.template.md`, `memory/templates/shadow-hypothesis.template.md`, `memory/templates/decision-record.template.md`
- **Lint rules:** `scripts/lint_rules/no_percentages_in_predictions.py`, `branch_out_no_recommendation.py`, `decision_trigger_conditions.py`

## Anti-patterns (binding)

- **Generating percentages anywhere** — three tiers only (`likely` / `possible-but-surprising` / `unlikely-but-impactful`). Lint catches this.
- **Predicting beyond t+2** — beyond two turns is human strategy session, not agentic prediction.
- **Adding "recommended move" column or section** to the trade-off matrix. Lint catches this.
- **Proceeding with caveats when 2+ actors are shallow / none** — hard stop is hard stop.
- **Coining new canonical move names without registry update** — propose to principal, do not silently append.
- **Surfacing shadow hypotheses in branch-out output** — invisibility is binding (anti-self-fulfilling prophecy).
- **Auto-committing the decision record** — principal fills `trigger_conditions` and commits.
- **Filling `trigger_conditions` on principal's behalf** — that's the principal's call; lint catches empty values at commit time.
