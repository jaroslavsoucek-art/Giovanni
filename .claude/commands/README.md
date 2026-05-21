# Slash commands

Giovanni's invokable surface. Each command is a **thin shell** that runs pre-flight, parses args, then routes to an agent (or to a workflow procedure). The mechanics live in the agents and workflows; these files are the invocation contracts.

Design patterns + argument syntax conventions: see [`docs/slash-commands.md`](../../docs/slash-commands.md).

## Command registry

| Command | One-liner | Argument syntax | Routes to | Typical cadence |
|---|---|---|---|---|
| [`/digest`](digest.md) | Daily digest — parallel source pull, drift detection, brief gen, shadow lookback, render | `[--force] [--source <name>]` | `.claude/workflows/daily-digest.md` + N × `source-puller` (parallel) | daily |
| [`/branch-out`](branch-out.md) | Active predictive simulation on a situation. Hard-stops on shallow actors. | `<situation-slug> [--from-digest]` | `prediction-runtime` (mode: branch-out) | ad hoc (triggered by digest active candidates) |
| [`/shadow-review`](shadow-review.md) | Quarterly audit of shadow hypotheses with adversarial lookback discipline | `[--sample N] [--actor <slug>] [--window <YYYY-MM>] [--horizon <YYYY-MM-DD>]` | `prediction-runtime` (mode: shadow-review) | quarterly |
| [`/calibration-report`](calibration-report.md) | Monthly per-actor + per-tier accuracy aggregation. Updates `actor-scores.yaml`. | `[--month <YYYY-MM>]` | `prediction-runtime` (mode: calibration-report) | monthly (1st of month) |
| [`/consistency-check`](consistency-check.md) | Semantic drift checks across memory + constitution + agent roster + decisions | `[--check <id>] [--since <YYYY-MM-DD>] [--write]` | `consistency-checker` | weekly (recommended) |
| [`/market-radar`](market-radar.md) | External competitive / market intelligence scan. Constraint-aware (settled decisions = drift flag). | `[--focus <topic>] [--market <code>] [--competitor <slug>] [--horizon <Nd>] [--depth surface\|deep]` | `market-radar` | weekly default; focused ad hoc |
| [`/review`](review.md) | Adversarial review of a draft — SHIP / REWRITE / KILL verdict + strongest counter-case | `<draft-path> [--position "..."] [--audience internal\|external\|mixed]` | `adversarial-reviewer` | ad hoc (high-stakes drafts only) |
| [`/redline`](redline.md) | Adversarial review alias emphasizing verbatim-strike list | `<draft-path> [--position "..."] [--audience internal\|external\|mixed]` | `adversarial-reviewer` (emphasis: redline) | ad hoc |

## Conventions

### Argument syntax

- **Positional** for required primary arg (e.g. `<situation-slug>`, `<draft-path>`)
- **`--flag`** for boolean (e.g. `--force`, `--from-digest`)
- **`--flag value`** or **`--flag=value`** for parameterized (e.g. `--month 2026-04`, `--check=memory-blockers-vs-constitution`)
- Quoted strings supported for multi-word values (e.g. `--position "we should renew"`)
- Comma-separated for multi-value (e.g. `--market US,EU`)

Detailed parsing rules: [`docs/slash-commands.md`](../../docs/slash-commands.md) § Argument parsing implementation.

### Pre-flight

Every command verifies prerequisites BEFORE spawning the agent or running the workflow:

- CWD check (in a Giovanni repo)
- Required agent definition file present
- Required state files / config files present
- Cadence guards where applicable

Pre-flight failure → STOP with explicit diagnostic. No graceful degradation.

### Output behavior

| Behavior | Commands |
|---|---|
| Render to chat only (no persistent artifact) | `/digest` (the digest body), `/review`, `/redline` |
| Render to chat + write persistent artifact | `/digest` (state + briefs + shadow), `/branch-out` (branch-out artifact + decision draft + shadow), `/shadow-review` (audit log + moved YAMLs), `/calibration-report` (report + actor-scores), `/consistency-check` (audit report + state), `/market-radar` (memo) |
| Mutate `actor-scores.yaml` | only `/calibration-report` |

**No command auto-commits.** Principal reviews + commits in batch. This is the binding rule that keeps the git log audit-trail honest.

### Routing

Commands route to either:

- **A single agent** via `Task` (`/branch-out`, `/shadow-review`, `/calibration-report`, `/consistency-check`, `/market-radar`, `/review`, `/redline`)
- **A workflow procedure** with embedded parallel agent fan-out (`/digest`)

No command embeds business logic. If a command file grows past ~250 lines of body content, that's a smell — the mechanics belong in the agent or workflow, not the invocation shell.

## What's NOT here

- **Daily-use agent invocations that are NOT slash commands.** Agents like `researcher`, `profile-bootstrap`, `deliverable-reviewer` are invoked via the `Agent` tool directly, not via slash. They don't need an orchestration shell — the principal spawns them with explicit params.
- **Hook-based automation.** Pre-commit hooks, session-start hooks, post-tool-use hooks live in `.claude/hooks/`. They don't go through slash commands.
- **Knowledge index / memory map regeneration.** These are scripts (`scripts/build-knowledge-index.sh`, `scripts/build-memory-map.sh`) invoked by hooks or lint, not slash commands.

## Adding a new slash command

Bar for adding a new slash command:

1. **The work is reusable.** A one-off task doesn't warrant a command — just invoke the agent directly.
2. **The orchestration shell adds value.** Pre-flight checks, argument parsing, or workflow procedure routing must be non-trivial. If the command is `→ spawn agent with args` and nothing else, the principal can spawn the agent directly.
3. **The command is thin.** No embedded business logic. If you find yourself writing 200 lines of mechanics in the command file, refactor: mechanics belong in the agent or workflow.
4. **It's discoverable.** Add it to the registry table above and to `docs/slash-commands.md` so principals know it exists.

Template structure for a new command:

```markdown
---
description: <one-liner — appears in /<command> listings>
allowed-tools: <comma-separated minimal tool list>
---

# /<command-name>

<One-paragraph what + why. State that this is a thin shell.>

## Usage

<canonical invocation forms>

## Argument syntax

<table — arg | type | default | meaning>

## Pre-flight (binding — STOP on failure)

<numbered checks>

## Execution flow

<numbered steps — pre-flight → spawn → wait → relay → no-commit>

## Output behavior

<render target, persistent artifacts, mutation surface>

## Error handling

<per-failure-mode behavior>

## Cross-references

<agent, workflow, templates, lint rules>

## Anti-patterns (binding)

<bullet list of what the command must not do>
```

## Lint

`scripts/lint_rules/slash_command_registry.py` validates that the registry table in this README stays in sync with the actual files in `.claude/commands/*.md`. Catches drift: command added but not listed, command listed but file removed.
