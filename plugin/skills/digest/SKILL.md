---
description: Run the daily digest — parallel source pull, synthesis, drift detection, brief generation, shadow lookback, render to chat.
allowed-tools: Agent, Read, Write(./memory/**), Edit(./memory/**), Glob, Grep, Bash(git log *), Bash(git diff *), Bash(git status *), Bash(git add *), Bash(git commit *)
disable-model-invocation: true
argument-hint: "[--force] [--source <name>]"
---

# /giovanni:digest

Orchestrate the daily digest per `${CLAUDE_PLUGIN_ROOT}/skills/digest/procedure.md`. This command is a **thin shell** — it sets up pre-flight, parses args, fans out `giovanni:source-puller` agents in parallel, then hands off to the workflow procedure. The mechanics live in the workflow doc and the agents; this file is the invocation contract.

## Usage

```
/giovanni:digest                            # default — full 12-step procedure
/giovanni:digest --force                    # override 4 h cadence guard
/giovanni:digest --source <name>            # debug mode — run a single source pull only
/giovanni:digest --source <name> --force    # both
```

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `--force` | boolean flag | off | Skip the 4 h cadence guard (Workflow Step 0.3). Use after correcting a botched run or rerunning intentionally. |
| `--source <name>` | parameterized | none | Run only the named source pull and render its bullets — bypasses synthesis, drift, briefs, shadow. Debug aid for source config tuning. `<name>` must match an entry in `memory/digest_sources.md`. |

Quoted strings supported. `--flag=value` and `--flag value` both work.

## Pre-flight (binding — STOP on failure)

Before spawning any agent, the orchestrator verifies:

1. **CWD check.** Working directory contains both `memory/digest_sources.md` and `${CLAUDE_PLUGIN_ROOT}/docs/digest.md`. Otherwise STOP:
   `ERROR: not in a Giovanni repo (no memory/digest_sources.md). Reinvoke from repo root.`
2. **State file readable.** `memory/digest_state.md` exists and parses `last_run_timestamp` as ISO 8601. If missing or empty:
   - First run ever → ASK the principal for a manual seed timestamp (e.g. "start window 7 days ago"). Do NOT default.
   - Corrupt / missing field → STOP with a diagnostic line pointing at `memory/digest-state.template.md`.
3. **Cadence guard.** If `last_run_timestamp` is less than 4 h ago AND `--force` is not set, STOP:
   `INFO: last digest <Nm> ago — re-running this fast pollutes state. Override with --force.`
4. **Source config presence.** `memory/digest_sources.md` parses and lists ≥1 source. Empty config is a setup error, not a "quiet day". STOP:
   `ERROR: memory/digest_sources.md has no configured sources. Seed it per memory/digest-sources.template.md.`
5. **Required agent files present.** `${CLAUDE_PLUGIN_ROOT}/agents/source-puller.md` (parallel pull) and — if Step 9/10 will reach them — `profile-bootstrap.md`. Missing agent file → STOP with which file is absent.

If any pre-flight fails, the orchestrator does NOT proceed and does NOT update state. The principal fixes the precondition and reinvokes.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Step 0-3 of `${CLAUDE_PLUGIN_ROOT}/skills/digest/procedure.md`** inline — read state, determine sources, calculate window.
3. **Step 4 parallel fan-out.** Single message, N `Agent` calls to `giovanni:source-puller` agents (one per configured source). Each gets the source-specific identifier, `window_start`, `window_end`, and any `extra_context` (e.g. `last_run_sha` for version-control). If `--source <name>` was passed, fan-out reduces to a single agent for that source.
4. **Steps 5-10** inline — synthesis, triage, brief auto-gen, shadow lookback, profile refresh signals, drift detection — per workflow doc.
5. **Step 12 render** to chat. Then **Step 11 shadow generation** (runs AFTER render — invisibility is binding, see `${CLAUDE_PLUGIN_ROOT}/docs/prediction.md`).
6. **State update** — write `memory/digest_state.md` with `last_run_timestamp = window_end` (from Step 3, never the time of writing), `last_run_sha`, shadow stats. **Do NOT auto-commit.**
7. **Hand off** to drift response sub-flow per workflow doc (principal reacts with `confirm` / `ignore Nd` / `patch ...`).

## Debug mode (`--source <name>`)

When `--source <name>` is set:

- Pre-flight runs as normal.
- Step 4 spawns a single `giovanni:source-puller` for the named source only.
- Output is the raw bullets returned by the agent — no synthesis, no drift detection, no briefs, no shadow.
- State file is NOT updated (this run is not a "real" digest).
- Use for tuning source identifiers / suppression patterns / volume caps. Then re-run the full digest.

## Output behavior

- **Render target:** chat (ephemeral). The digest body itself is not committed — committing daily digests pollutes git history without value. See `${CLAUDE_PLUGIN_ROOT}/docs/digest.md` § Anti-patterns.
- **Persistent artifacts:** `memory/digest_state.md` (overwritten), `memory/briefs/<file>.md` (one per eligible event, idempotent refresh), `memory/shadow/pending/<file>.yaml` (any new hypotheses), `memory/shadow/resolved/<YYYY-MM>/` (lookback movements), `memory/shadow/expired/<YYYY-MM>/` (expired horizon movements). All written **unstaged**.
- **No auto-commit.** Principal reviews + commits in batch.

## Error handling

- **Pre-flight failure** → STOP, no state mutation, principal fixes precondition.
- **Source-puller failure** (one or more agents return `ERROR: ...`) → continue. Failed sources surface in Step 12 render's `System hygiene` section. Do not fabricate data for failed sources.
- **All sources fail** → render the digest with empty sections + system hygiene flagging the systemic failure. Don't abort — the principal needs to see that everything broke.
- **Cadence guard hit** without `--force` → STOP. Principal decides whether to override.
- **Brief generation failure** (template missing, slug collision) → flag in render, do not abort the digest.

No graceful degradation that hides failure. Honest reporting > coverage theater.

## Cadence guard rationale

The 4 h cadence guard exists because Step 8 (shadow lookback) and Step 11 (shadow generation) mutate state in ways that are awkward to reverse if run twice in a tight window. Running twice an hour apart produces duplicate shadow generation, double-counted lookback, and a corrupted `digest_state.md`. The `--force` flag exists for the rare case where the principal genuinely needs to rerun (e.g. recovering from a botched cycle).

Default cadence is implicit "approximately daily" — the workflow's design is around daily-ish runs, not hard daily. A 16 h or 30 h gap is fine. A 30 min gap is not.

## Cross-references

- **Workflow procedure:** `${CLAUDE_PLUGIN_ROOT}/skills/digest/procedure.md` (the 12 steps)
- **Policy / rationale:** `${CLAUDE_PLUGIN_ROOT}/docs/digest.md` (why daily, anti-patterns, multi-domain calibration)
- **State template:** `memory/digest-state.template.md`
- **Sources config template:** `memory/digest-sources.template.md`
- **Source-puller agent:** `${CLAUDE_PLUGIN_ROOT}/agents/source-puller.md`
- **Predictive layer dependencies:** `${CLAUDE_PLUGIN_ROOT}/docs/prediction.md` (shadow invisibility, adversarial lookback)
- **Drift ack flow:** `${CLAUDE_PLUGIN_ROOT}/docs/digest.md` § Ack flow

## Anti-patterns (binding)

- **Skipping pre-flight to "save time"** — the four checks exist because each has caught a real failure mode. Skip = corrupted state.
- **Auto-committing the state file update** — the principal commits in batch. Auto-commit pollutes git log.
- **Surfacing shadow hypotheses in render** — they are invisible at generation time per `${CLAUDE_PLUGIN_ROOT}/docs/prediction.md` § Shadow invisibility. Lint catches this.
- **Sequential source pull** in main thread context — pollutes main with raw tool output. Always fan-out, even for one source.
- **Adding "recommended action" to drift flags** — the principal chooses `confirm | ignore | patch`. The orchestrator surfaces the choice, does not pre-select.
