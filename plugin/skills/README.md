# Skills (slash commands)

Giovanni's invokable surface. Each skill is a **thin shell** that runs pre-flight, parses args, then routes to an agent (or to a procedure file beside it). The mechanics live in the agents and procedures; the `SKILL.md` files are the invocation contracts.

Installed as a plugin, every skill is namespaced: `/giovanni:digest`, not `/digest`. The agents are namespaced the same way (`giovanni:source-puller`). Procedure files that used to live in `.claude/workflows/` sit next to the skill that runs them (`digest/procedure.md`, `consistency-review/procedure.md`, `review/procedure.md` — `/giovanni:redline` shares the last one).

Design patterns + argument syntax conventions: see [`docs/slash-commands.md`](../docs/slash-commands.md).

## Registry

| Command | One-liner | Argument syntax | Routes to | Typical cadence |
|---|---|---|---|---|
| [`/giovanni:init`](init/SKILL.md) | Scaffold the memory / knowledge / governance layers in the current repo from the plugin's skeleton. Idempotent. | `[--force]` | `scripts/init-fork.sh` | once per repo |
| [`/giovanni:digest`](digest/SKILL.md) | Daily digest — parallel source pull, drift detection, brief gen, shadow lookback, render | `[--force] [--source <name>]` | `digest/procedure.md` + N × `giovanni:source-puller` (parallel) | daily |
| [`/giovanni:branch-out`](branch-out/SKILL.md) | Active predictive simulation on a situation. Hard-stops on shallow actors. | `<situation-slug> [--from-digest]` | `giovanni:prediction-runtime` (mode: branch-out) | ad hoc (triggered by digest active candidates) |
| [`/giovanni:shadow-review`](shadow-review/SKILL.md) | Quarterly audit of shadow hypotheses with adversarial lookback discipline. COI guard stops self-review of <48h resolutions. | `[--sample N] [--actor <slug>] [--window <YYYY-MM>] [--horizon <YYYY-MM-DD>] [--force-review-now]` | `giovanni:prediction-runtime` (mode: shadow-review) | quarterly |
| [`/giovanni:calibration-report`](calibration-report/SKILL.md) | Monthly per-actor + per-tier accuracy aggregation. Updates `actor-scores.yaml`. | `[--month <YYYY-MM>]` | `giovanni:prediction-runtime` (mode: calibration-report) | monthly (1st of month) |
| [`/giovanni:consistency-check`](consistency-check/SKILL.md) | 8 semantic drift checks — memory + constitution + agent roster + decisions + decided-terms + knowledge↔knowledge + outbound published pages | `[--check <id>] [--since <YYYY-MM-DD>] [--write]` | `giovanni:consistency-checker` | weekly (recommended) |
| [`/giovanni:consistency-review`](consistency-review/SKILL.md) | Per-finding triage of a consistency report — accept-diff / reject / defer / false-positive, precision tally | `[<YYYY-MM-DD>]` | `consistency-review/procedure.md` (interactive main-thread) | after each `/giovanni:consistency-check` during shadow mode |
| [`/giovanni:pulse`](pulse/SKILL.md) | Weekly state-of-the-work read per work-block — code over tracker. Answers "where does each piece stand", not "what happened". | `[since=<YYYY-MM-DD>] [block=<slug>] [quick]` | main thread (+ agents per source) | weekly |
| [`/giovanni:market-radar`](market-radar/SKILL.md) | External competitive / market intelligence scan. Constraint-aware (settled decisions = drift flag). | `[--focus <topic>] [--market <code>] [--competitor <slug>] [--horizon <Nd>] [--depth surface\|deep]` | `giovanni:market-radar` | weekly default; focused ad hoc |
| [`/giovanni:inbox`](inbox/SKILL.md) | Show the one ranked list every loop writes to; act on per-item yes / no / later | `[refresh]` | `scripts/inbox.py` | every session (hook-shown) |
| [`/giovanni:learn`](learn/SKILL.md) | Learning loop: repeated workflows → skill proposals, unused generated skills → retire, repeated corrections → rules; drafts a skill on yes | `[accept <slug> \| reject <slug> \| retire <skill>]` | `scripts/mine-workflows.py` | weekly |
| [`/giovanni:schedule`](schedule/SKILL.md) | Install / inspect / remove headless runs from `schedule:` (launchd, or printed crontab) | `install [--dry-run] \| uninstall \| status \| run <name>` | `scripts/schedule.py` | once per machine |
| [`/giovanni:review`](review/SKILL.md) | Adversarial review of a draft — SHIP / REWRITE / KILL verdict + strongest counter-case | `<draft-path> [--position "..."] [--audience internal\|external\|mixed]` | `giovanni:adversarial-reviewer` via `review/procedure.md` | ad hoc (high-stakes drafts only) |
| [`/giovanni:redline`](redline/SKILL.md) | Adversarial review alias emphasizing verbatim-strike list | `<draft-path> [--position "..."] [--audience internal\|external\|mixed]` | `giovanni:adversarial-reviewer` (emphasis: redline) | ad hoc |

## Conventions

### Argument syntax

- **Positional** for required primary arg (e.g. `<situation-slug>`, `<draft-path>`)
- **`--flag`** for boolean (e.g. `--force`, `--from-digest`)
- **`--flag value`** or **`--flag=value`** for parameterized (e.g. `--month 2026-04`, `--check=memory-blockers-vs-constitution`)
- Quoted strings supported for multi-word values (e.g. `--position "we should renew"`)
- Comma-separated for multi-value (e.g. `--market US,EU`)

Detailed parsing rules: [`docs/slash-commands.md`](../docs/slash-commands.md) § Argument parsing implementation.

### Pre-flight

Every skill verifies prerequisites BEFORE spawning the agent or running the procedure:

- Project check (the cwd is a repo that `/giovanni:init` has scaffolded — `memory/`, `knowledge/` present)
- Required agent definition present under `${CLAUDE_PLUGIN_ROOT}/agents/`
- Required state files / config files present in the project
- Cadence guards where applicable

Pre-flight failure → STOP with explicit diagnostic. No graceful degradation.

### Output behavior

| Behavior | Commands |
|---|---|
| Render to chat only (no persistent artifact) | `/giovanni:digest` (the digest body), `/giovanni:review`, `/giovanni:redline` |
| Render to chat + write persistent artifact | `/giovanni:digest` (state + briefs + shadow), `/giovanni:branch-out` (branch-out artifact + decision draft + shadow), `/giovanni:shadow-review` (audit log + moved YAMLs), `/giovanni:calibration-report` (report + actor-scores), `/giovanni:consistency-check` (audit report + state), `/giovanni:consistency-review` (state update + accepted diffs), `/giovanni:market-radar` (memo) |
| Mutate `actor-scores.yaml` | only `/giovanni:calibration-report` |
| Write project scaffolding | only `/giovanni:init` |

**No skill auto-commits.** Principal reviews + commits in batch. This is the binding rule that keeps the git log audit-trail honest. The one opt-in exception is the autonomy profile (`docs/autonomy.md`): a Stop *hook*, not a skill, commits the paths a project lists under `autonomy.auto_commit_paths`, and never its `confirm_paths`.

### Routing

Skills route to either:

- **A single agent** via `Agent` (`/giovanni:branch-out`, `/giovanni:shadow-review`, `/giovanni:calibration-report`, `/giovanni:consistency-check`, `/giovanni:market-radar`, `/giovanni:review`, `/giovanni:redline`)
- **A procedure file** — with embedded parallel agent fan-out (`/giovanni:digest`), or interactive main-thread triage with no agent spawn (`/giovanni:consistency-review`)
- **A script** (`/giovanni:init`)

No skill embeds business logic. If a `SKILL.md` grows past ~250 lines of body content, that's a smell — the mechanics belong in the agent or procedure, not the invocation shell.

### Paths

`${CLAUDE_PLUGIN_ROOT}` in a `SKILL.md`, procedure or agent body is substituted by Claude Code when the plugin loads, so a skill can name its own procedure or a lint rule by absolute path. Project files (`memory/…`, `knowledge/…`, `docs/governance.config.yaml`) stay relative: they belong to the repo the session runs in, not to the plugin.

## What's NOT here

- **Daily-use agent invocations that are NOT slash commands.** Agents like `giovanni:researcher`, `giovanni:profile-bootstrap`, `giovanni:deliverable-reviewer` are invoked via the `Agent` tool directly, not via slash. They don't need an orchestration shell — the principal spawns them with explicit params.
- **Hook-based automation.** Session-start, pre-tool-use and post-tool-use hooks live in `../hooks/` and are wired by `../hooks/hooks.json`. The git pre-commit hook lives in `../scripts/git-hooks/`. None of them go through slash commands.
- **Knowledge index / memory map regeneration.** These are scripts (`../scripts/build-knowledge-index.sh`, `../scripts/build-memory-map.sh`) invoked by hooks or lint, not slash commands.

## Adding a new skill

Bar for adding a new skill:

1. **The work is reusable.** A one-off task doesn't warrant a skill — just invoke the agent directly.
2. **The orchestration shell adds value.** Pre-flight checks, argument parsing, or procedure routing must be non-trivial. If the skill is `→ spawn agent with args` and nothing else, the principal can spawn the agent directly.
3. **The skill is thin.** No embedded business logic. If you find yourself writing 200 lines of mechanics in `SKILL.md`, refactor: mechanics belong in the agent or procedure.
4. **It's discoverable.** Add it to the registry table above, to `docs/slash-commands.md`, and to the route table in `templates/CLAUDE.template.md` so principals know it exists (lint: `slash-command-registry`, `workflow-route-table`).

Template structure for a new skill (`skills/<name>/SKILL.md`):

```markdown
---
description: <one-liner — appears in the / menu>
allowed-tools: <comma-separated minimal tool list>
disable-model-invocation: true
argument-hint: "<canonical args>"
---

# /giovanni:<name>

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

<agent, procedure, templates, lint rules>

## Anti-patterns (binding)

<bullet list of what the skill must not do>
```

`disable-model-invocation: true` is the default here on purpose: every Giovanni skill has an explicit trigger (a slash command, a cadence, a hook that *reminds*), and none of them should start because the model decided the moment looked right.

## Lint

`../scripts/lint_rules/slash_command_registry.py` validates that the registry table in this README stays in sync with the actual `skills/*/SKILL.md` files. Catches drift: skill added but not listed, skill listed but directory removed.
