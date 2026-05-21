---
description: Proactive external competitive / market intelligence scan. Routes to market-radar agent. Default = periodic sweep; focused = topic / market / competitor deep-dive.
allowed-tools: Task, Read, Glob, Grep, Bash
---

# /market-radar

Run an external intelligence scan via the `market-radar` agent. Strictly external sources (PR / LinkedIn / news / public roadmaps / vendor blogs) — **separate from `/digest`'s internal signal pull**. This command is a **thin shell** — scope, source rules, drift-against-settled-decisions logic live in the agent. This file is the invocation contract.

## Usage

```
/market-radar                                       # default — periodic sweep, all markets × all layers
/market-radar --focus <topic>                       # topic-focused, surface depth
/market-radar --market <code>                       # single-market deep-dive
/market-radar --market <code1>,<code2>              # multi-market
/market-radar --competitor <slug>                   # competitor deep-dive
/market-radar --focus <topic> --market <code>       # combined
/market-radar --focus <topic> --horizon 90d         # custom window
/market-radar --focus <topic> --depth deep          # multi-section analysis
```

Examples:
- `/market-radar` — periodic default sweep
- `/market-radar --focus regulatory-shift-X` — cross-market regulatory scan, surface depth
- `/market-radar --focus regulatory-shift-X --market US,EU --horizon 90d --depth deep` — US+EU regulatory deep-dive, 90 days
- `/market-radar --competitor <competitor-slug>` — competitor-specific moves last 7 days

## Argument syntax

| Arg | Type | Default | Allowed values | Meaning |
|---|---|---|---|---|
| `--focus <topic>` | parameterized | none | topic slug (kebab-case) | Topic focus — triggers focused mode if set. |
| `--market <code>` | parameterized | all per scope file | per fork's scope file (comma-separated) | Single or multi-market filter — triggers focused mode if set. |
| `--competitor <slug>` | parameterized | none | per fork's `_scope.md` competitor matrix | Competitor filter — triggers focused mode if set. |
| `--horizon <Nd>` | parameterized | 7d (default mode), 30d (focused) | `7d` / `30d` / `90d` / `<N>d` | Lookback window for signals. |
| `--depth <level>` | parameterized | `surface` | `surface` / `deep` | Surface = ≤10 fetches, 1-page memo. Deep = ≤25 fetches, multi-section analysis. |

**Mode derivation:**
- No `--focus` / `--market` / `--competitor` → **default mode** (periodic sweep)
- Any of `--focus` / `--market` / `--competitor` set → **focused mode**

If `focused` mode but **no** focus/market/competitor → STOP: `ERROR: focused mode requires at least one of --focus / --market / --competitor`.

## Pre-flight (binding — STOP on failure)

Before spawning `market-radar`:

1. **CWD check.** Working directory is a Giovanni repo. Otherwise STOP.
2. **Agent definition present.** `.claude/agents/market-radar.md` exists. Missing → STOP.
3. **Scope file present.** `memory/intel/market-radar/_scope.md` exists. Missing → STOP: `ERROR: memory/intel/market-radar/_scope.md missing. Seed the competitor matrix + settled decisions reference per the template before running /market-radar.`
4. **Scope file freshness (advisory, not STOP).** Parse the scope file's `last_reviewed:` field. If > 90 days ago, surface advisory:
   `⚠ Scope file last reviewed <date> (>90d ago). Consider scope audit before relying on this run.`
   Continue anyway.
5. **Budget readiness (advisory).** If `mode=default` or `depth=deep`, estimated 15-25 fetches / 30 min. Surface advisory before spawn if not in interactive mode:
   `INFO: estimated <N> fetches / <M> min. Proceeding.`
6. **Focused-mode validation.** If `--focus` / `--market` / `--competitor` parsing produced focused mode but no qualifier arg is set → STOP per Mode derivation above.

## Execution flow

1. **Parse args.** Derive mode. Validate per focused-mode constraint.
2. **Run pre-flight.** STOP on any failure.
3. **Spawn `market-radar`** via `Task` with parsed args:
   ```
   subagent_type: market-radar
   mode: default | focused
   focus: <slug or null>
   market: <comma-separated codes or "all">
   competitor: <slug or null>
   horizon_days: <N>
   depth: surface | deep
   ```
4. **Wait for agent return.** The agent:
   - Loads scope file + settled decisions + last 3 memos
   - Fetches sources per privilege order (official PR → LinkedIn → trade press → public roadmaps)
   - Applies material-event filter
   - Checks drift against settled decisions
   - Writes memo to `memory/intel/market-radar/<YYYY-WW>.md` (default) or `memory/intel/market-radar/focused/<YYYY-MM-DD>_<slug>.md` (focused)
   - Returns summary (default: 5-line top-line; focused: full TL;DR + Material shifts section verbatim)
5. **Relay agent output verbatim** to chat. For focused mode, the principal sees the substantive content immediately (no waiting for next digest delivery).
6. **Do NOT commit.** Memo stays unstaged. Principal reviews drift candidates and decides whether to escalate (`/branch-out` for strategic drift) or batch-commit.

## Drift escalation

If the agent surfaces drift candidates (event contradicts a settled decision), the principal may:

- **Flag for `/branch-out`** — strategic drift warrants active simulation
- **Flag for adversarial review** — the settled decision itself may need redline
- **Monitor only** — context-enriching but not action-forcing

The orchestrator does NOT auto-spawn follow-up workflows. The principal decides.

## Output behavior

- **Render target:** chat (summary for default; verbatim TL;DR + Material shifts for focused)
- **Persistent artifacts (unstaged):**
  - `memory/intel/market-radar/<YYYY-WW>.md` (default mode) — ISO week number
  - `memory/intel/market-radar/focused/<YYYY-MM-DD>_<slug>.md` (focused mode)
- **No mutation outside `memory/intel/market-radar/`.** No edits to constitution, CLAUDE_MEMORY, stakeholder profiles, decisions. Drift candidates flagged in memo, not auto-applied.
- **No auto-commit.**

## Constraint awareness

The agent loads settled decisions from constitution pointers in the scope file and treats them as off-limits for "consider alternative" framing. When a signal contradicts a settled decision, the agent **flags drift**, it does NOT recommend "switch to X". The principal decides whether the drift warrants reopening the decision.

This binding rule reflects that market-radar is intelligence, not strategy. The agent surfaces; the principal decides.

## Cadence guidance

- **Default scan:** weekly (e.g. Monday morning before weekly planning)
- **Focused scan:** ad hoc — typically at strategic decision moments (market entry, regulatory question, competitor announcement)
- **NOT auto-scheduled.** Run manually 4-6 weeks to validate output quality before considering cron — most forks find weekly default cadence sufficient.

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Focused mode with no qualifier** → STOP at arg parsing.
- **Scope file stale > 90d** → advisory only, continue.
- **Agent failure** (web fetch budget exhausted, source unreachable) → agent returns with what it has + coverage note. No retry from orchestrator.
- **Empty result (no material shift)** → agent says so explicitly in memo TL;DR. Do not pad with "5 minor observations".

## Cross-references

- **Agent (executor):** `.claude/agents/market-radar.md`
- **Scope file:** `memory/intel/market-radar/_scope.md` (fork-maintained: competitor matrix, sources, material-event filter, settled decisions reference)
- **Constraint source:** constitution settled decisions (per scope file pointers)
- **Related commands:** `/branch-out` (drift escalation), `/review` (adversarial review of settled decision if reopening)
- **Anti-stylization policy:** `docs/agents.md` § Anti-patterns

## Anti-patterns (binding)

- **Running daily** — cost/value poor, most information repeats. Weekly is the right cadence.
- **Running focused without `--focus` / `--market` / `--competitor`** — produces generic memo.
- **Ignoring scope file staleness warning** — agent reports against a stale competitor map.
- **Auto-committing the memo without review** — drift candidates must surface to the principal before they slip into canonical state.
- **Spawning `/market-radar` + `/digest` in parallel without reason** — wastes tokens, results don't mix anyway (different data sources).
- **Recommending "switch to X" when X contradicts a settled decision** — flag drift, do not recommend reversal.
- **Padding the memo with non-material findings** — if nothing material, the memo says so in one line.
