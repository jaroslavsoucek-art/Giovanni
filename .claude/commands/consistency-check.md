---
description: Run semantic consistency checks across memory, constitution, agent roster, and decision records. Routes to consistency-checker agent. Read-only — proposes diffs, never applies them.
allowed-tools: Task, Read, Write, Bash
---

# /consistency-check

Run the semantic invariants that deterministic `scripts/lint.sh` cannot reach (memory↔constitution drift, decisions↔constitution drift, agent roster description mismatch, topic shard cross-reference breakage, optional architecture audit staleness). This command is a **thin shell** — checks and report format live in the `consistency-checker` agent. This file is the invocation contract.

## Usage

```
/consistency-check                          # all enabled checks
/consistency-check --check <id>             # single check
/consistency-check --since <YYYY-MM-DD>     # narrows git-log scan window for staleness checks
/consistency-check --write                  # commit findings to file (default = also writes; flag is reserved for future render-only mode)
```

Valid `--check` ids:
- `memory-blockers-vs-constitution`
- `decisions-vs-constitution`
- `agent-roster-semantic`
- `topic-shard-stakeholder-xref`
- `audit-staleness` (optional — only if fork uses architecture tier audits)

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `--check <id>` | parameterized | all | Run a single check by ID instead of all enabled checks. |
| `--since <YYYY-MM-DD>` | parameterized date | 30 days ago | For staleness check (`audit-staleness`): limits the git-log window. Ignored by other checks. |
| `--write` | boolean flag | implicit (always writes report) | Reserved for future render-only mode. Default behavior writes the report file. |

## Pre-flight (binding — STOP on failure)

Before spawning `consistency-checker`:

1. **CWD check.** Working directory is a Giovanni repo (presence of `memory/CLAUDE_MEMORY.md` + `knowledge/<constitution>.md`). Otherwise STOP.
2. **Agent definition present.** `.claude/agents/consistency-checker.md` exists. Missing → STOP.
3. **Audit directory present.** `memory/audits/consistency/` exists. Create if missing (this is the only directory the orchestrator creates pre-spawn).
4. **State file present.** `memory/audits/consistency/_state.md` exists with a non-empty `shadow_mode_start_date` field. If missing or empty:
   - Auto-seed: set `shadow_mode_start_date = today`, `shadow_mode_end_date = today + 28 days`.
   - Surface advisory: `INFO: seeded shadow mode 28d from today. Score precision before promoting to operational warnings.`
5. **Constitution + L1 present.** `knowledge/<constitution_file>.md` (per `docs/governance.config.yaml`) and `memory/CLAUDE_MEMORY.md` exist. Missing → STOP — the checks have no input.

## Execution flow

1. **Run pre-flight.** STOP on any failure. Create `memory/audits/consistency/` if missing. Auto-seed `_state.md` if needed.
2. **Spawn `consistency-checker`** via `Task` with:
   ```
   subagent_type: consistency-checker
   check: <id or null>
   since: <YYYY-MM-DD or null>
   ```
3. **Wait for agent return.** The agent:
   - Reads shared context (CLAUDE_MEMORY, constitution, CLAUDE.md, _state.md, INVARIANTS.md if present)
   - Runs the requested checks (all enabled, or single via `--check`)
   - Composes a fixed-format report at `memory/audits/consistency/<YYYY-MM-DD>.md` (if a file for today exists, appends with `## Re-run <HH:MM>Z` subheading)
   - Appends a run entry to `memory/audits/consistency/_state.md`
   - Returns a ≤5-line summary
4. **Relay agent summary verbatim** to chat. Add the pointer: `Review via /consistency-review <YYYY-MM-DD>`.
5. **Do NOT commit.** Principal reviews via `/consistency-review`, triages findings (accept-diff / reject / defer / false-positive), and commits the audit log + any accepted diffs in batch.

## Shadow mode

The consistency-checker ships in **shadow mode** for the first 28 days from initial seed. During shadow mode:

- The agent runs and writes reports as normal.
- Findings are **not** surfaced in session-start hooks or `/digest` output.
- The principal manually reviews each run via `/consistency-review` to score precision.

After shadow mode ends (`_state.md` `shadow_mode_end_date` < today), a separate PR integrates findings into operational flow. The orchestrator does NOT auto-promote — that's a governance decision (see `docs/governance.md`).

## Findings cap

The agent caps output at **10 findings per run**, prioritizing by severity (critical > high > medium > low). If more findings exist, the agent notes the truncation count. This cap exists because the principal needs to triage findings manually — 50 findings is operationally hostile.

The orchestrator does NOT raise this cap.

## Output behavior

- **Render target:** chat (≤5-line summary) — the full report lives in the file.
- **Persistent artifacts (unstaged):**
  - `memory/audits/consistency/<YYYY-MM-DD>.md` — full report (or appended re-run section)
  - `memory/audits/consistency/_state.md` — appended run entry
- **No mutation to memory, constitution, CLAUDE.md, agents, decisions, topic shards.** The agent proposes diffs in the report; only the principal applies them via `/consistency-review`.
- **No auto-commit.**

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Agent failure** → surface structured error. Partial reports (if any) remain at the file path; the agent's truncation comment reflects what completed.
- **No findings** → write a report with `Findings: 0` and a one-line "no drift detected this run" note. Don't skip writing — the run entry in `_state.md` matters for precision tracking during shadow mode.

## Cadence guidance

- **Recommended cadence:** weekly (e.g. Mondays after `/digest`).
- **During shadow mode:** each run is reviewed manually for precision scoring.
- **After shadow mode:** the integration PR may add hook-based scheduling (e.g. weekly cron, session-start advisory). The orchestrator does not auto-schedule.

## Cross-references

- **Agent (executor):** `.claude/agents/consistency-checker.md`
- **Triage workflow:** `/consistency-review <YYYY-MM-DD>` — **out of scope for Setup1**, owned by `governance-architect`'s domain. Defer to Setup2 when first real-world findings need triage. See `docs/setup1-complete.md` § "Cross-architect TODOs (unresolved, low priority)".
- **State file:** `memory/audits/consistency/_state.md`
- **Deterministic lint complement:** `scripts/lint.sh` (this command covers what regex/YAML parsing can't)
- **Governance policy:** `docs/governance.md` § Consistency checks (shadow mode + promotion criteria)

## Anti-patterns (binding)

- **Auto-applying proposed diffs without `/consistency-review` triage** — the agent only proposes; the principal applies.
- **Running on every session-start during shadow mode** — defeats the purpose (shadow = manual review per run).
- **Spawning the agent from another agent's context** — always spawn from main thread. Recursive agent spawning produces opaque traces.
- **Treating output as authoritative** — it's a hypothesis stream; precision is unknown until shadow mode resolves.
- **Raising the 10-findings cap** — the cap is operationally calibrated; raising it produces noise.
- **Auto-committing the audit log** — principal commits in batch after `/consistency-review`.
