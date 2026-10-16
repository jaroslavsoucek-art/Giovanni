---
description: Run semantic consistency checks across memory, constitution, agent roster, decision records, the decided-terms registry, knowledge↔knowledge cross-doc drift, and externally published pages. Routes to consistency-checker agent. Read-only — proposes diffs, never applies them.
allowed-tools: Agent, Read, Write(./memory/**), Glob, Grep
disable-model-invocation: true
argument-hint: "[--check <id>] [--since <YYYY-MM-DD>]"
---

# /giovanni:consistency-check

Run the 8 semantic invariants that deterministic `${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh` cannot reach (memory↔constitution drift, decisions↔constitution drift, agent roster description mismatch, topic shard cross-reference breakage, optional architecture audit staleness, decided-terms completeness, knowledge↔knowledge cross-doc drift, published-pages outbound drift). This command is a **thin shell** — checks and report format live in the `giovanni:consistency-checker` agent. This file is the invocation contract.

## Usage

```
/giovanni:consistency-check                          # all enabled checks
/giovanni:consistency-check --check <id>             # single check
/giovanni:consistency-check --since <YYYY-MM-DD>     # narrows git-log scan window for staleness checks
/giovanni:consistency-check --write                  # commit findings to file (default = also writes; flag is reserved for future render-only mode)
```

Valid `--check` ids:
- `memory-blockers-vs-constitution`
- `decisions-vs-constitution`
- `agent-roster-semantic`
- `topic-shard-stakeholder-xref`
- `audit-staleness` (optional — only if fork uses architecture tier audits)
- `decided-terms-completeness` (no-op with INFO if `memory/audits/consistency/decided-terms.yaml` is absent)

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `--check <id>` | parameterized | all | Run a single check by ID instead of all enabled checks. |
| `--since <YYYY-MM-DD>` | parameterized date | 30 days ago | For staleness check (`audit-staleness`): limits the git-log window. Ignored by other checks. |
| `--write` | boolean flag | implicit (always writes report) | Reserved for future render-only mode. Default behavior writes the report file. |

## Pre-flight (binding — STOP on failure)

Before spawning `giovanni:consistency-checker`:

1. **CWD check.** Working directory is a Giovanni repo (presence of `memory/CLAUDE_MEMORY.md` + `knowledge/<constitution>.md`). Otherwise STOP.
2. **Agent definition present.** `${CLAUDE_PLUGIN_ROOT}/agents/consistency-checker.md` exists. Missing → STOP.
3. **Audit directory present.** `memory/audits/consistency/` exists. Create if missing (this is the only directory the orchestrator creates pre-spawn).
4. **State file present.** `memory/audits/consistency/_state.md` exists with a non-empty `shadow_mode_start_date` field. If missing or empty:
   - Auto-seed: set `shadow_mode_start_date = today`, `shadow_mode_end_date = today + 28 days`.
   - Surface advisory: `INFO: seeded shadow mode 28d from today. Score precision before promoting to operational warnings.`
5. **Constitution + L1 present.** `knowledge/<constitution_file>.md` (per `docs/governance.config.yaml`) and `memory/CLAUDE_MEMORY.md` exist. Missing → STOP — the checks have no input.

## Execution flow

1. **Run pre-flight.** STOP on any failure. Create `memory/audits/consistency/` if missing. Auto-seed `_state.md` if needed.
2. **Spawn `giovanni:consistency-checker`** via `Agent` with:
   ```
   subagent_type: giovanni:consistency-checker
   check: <id or null>
   since: <YYYY-MM-DD or null>
   ```
3. **Wait for agent return.** The agent:
   - Reads shared context (CLAUDE_MEMORY, constitution, CLAUDE.md, _state.md, INVARIANTS.md if present)
   - Runs the requested checks (all enabled, or single via `--check`)
   - Composes a fixed-format report at `memory/audits/consistency/<YYYY-MM-DD>.md` (if a file for today exists, appends with `## Re-run <HH:MM>Z` subheading)
   - Appends a run entry to `memory/audits/consistency/_state.md`
   - Returns a ≤5-line summary
4. **Relay agent summary verbatim** to chat. Add the pointer: `Review via /giovanni:consistency-review <YYYY-MM-DD>`.
5. **Do NOT commit.** Principal reviews via `/giovanni:consistency-review`, triages findings (accept-diff / reject / defer / false-positive), and commits the audit log + any accepted diffs in batch.

## Shadow mode

The consistency-checker ships in **shadow mode** for the first 28 days from initial seed. During shadow mode:

- The agent runs and writes reports as normal.
- Findings are **not** surfaced in session-start hooks or `/giovanni:digest` output.
- The principal manually reviews each run via `/giovanni:consistency-review` to score precision.

After shadow mode ends (`_state.md` `shadow_mode_end_date` < today), a separate PR integrates findings into operational flow. The orchestrator does NOT auto-promote — that's a governance decision (see `${CLAUDE_PLUGIN_ROOT}/docs/governance.md`).

## Findings cap

The agent caps output at **10 findings per run**, prioritizing by severity (critical > high > medium > low). If more findings exist, the agent notes the truncation count. This cap exists because the principal needs to triage findings manually — 50 findings is operationally hostile.

The orchestrator does NOT raise this cap.

## Output behavior

- **Render target:** chat (≤5-line summary) — the full report lives in the file.
- **Persistent artifacts (unstaged):**
  - `memory/audits/consistency/<YYYY-MM-DD>.md` — full report (or appended re-run section)
  - `memory/audits/consistency/_state.md` — appended run entry
- **No mutation to memory, constitution, CLAUDE.md, agents, decisions, topic shards.** The agent proposes diffs in the report; only the principal applies them via `/giovanni:consistency-review`.
- **No auto-commit.**

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Agent failure** → surface structured error. Partial reports (if any) remain at the file path; the agent's truncation comment reflects what completed.
- **No findings** → write a report with `Findings: 0` and a one-line "no drift detected this run" note. Don't skip writing — the run entry in `_state.md` matters for precision tracking during shadow mode.

## Cadence guidance

- **Recommended cadence:** weekly (e.g. Mondays after `/giovanni:digest`).
- **During shadow mode:** each run is reviewed manually for precision scoring.
- **After shadow mode:** the integration PR may add hook-based scheduling (e.g. weekly cron, session-start advisory). The orchestrator does not auto-schedule.

## Cross-references

- **Agent (executor):** `${CLAUDE_PLUGIN_ROOT}/agents/consistency-checker.md`
- **Triage workflow:** `/giovanni:consistency-review <YYYY-MM-DD>` (`${CLAUDE_PLUGIN_ROOT}/skills/consistency-review/SKILL.md` → `${CLAUDE_PLUGIN_ROOT}/skills/consistency-review/procedure.md`) — per-finding verdicts + precision tally. Run after each check during shadow mode.
- **State file:** `memory/audits/consistency/_state.md`
- **Deterministic lint complement:** `${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh` (this command covers what regex/YAML parsing can't)
- **Governance policy:** `${CLAUDE_PLUGIN_ROOT}/docs/governance.md` § Consistency checks (shadow mode + promotion criteria)

## Anti-patterns (binding)

- **Auto-applying proposed diffs without `/giovanni:consistency-review` triage** — the agent only proposes; the principal applies.
- **Running on every session-start during shadow mode** — defeats the purpose (shadow = manual review per run).
- **Spawning the agent from another agent's context** — always spawn from main thread. Recursive agent spawning produces opaque traces.
- **Treating output as authoritative** — it's a hypothesis stream; precision is unknown until shadow mode resolves.
- **Raising the 10-findings cap** — the cap is operationally calibrated; raising it produces noise.
- **Auto-committing the audit log** — principal commits in batch after `/giovanni:consistency-review`.
