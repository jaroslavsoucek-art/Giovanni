# Slash commands — design patterns + conventions

Giovanni's invokable surface is nine slash commands. Each is a **thin shell** that wires pre-flight checks + argument parsing + routing to an agent (or to a workflow procedure). This doc is the **why** companion to [`.claude/commands/README.md`](../.claude/commands/README.md) (the registry).

Two audiences:

1. **Forking principals** customizing Giovanni for a new domain — read the conventions and decide which ones to keep / adapt
2. **Future architects** adding a tenth command — read the patterns and follow them, or document why you're deviating

---

## 1. Commands are thin shells

The single highest-leverage rule in this doc.

**A slash command file contains:**

- One-paragraph description (what + why, with the disclaimer that it's a thin shell)
- Argument syntax (table — arg | type | default | meaning)
- Pre-flight checks (numbered, STOP on failure)
- Execution flow (numbered — pre-flight → spawn agent → wait → relay output → no-commit)
- Output behavior (render target, persistent artifacts, mutation surface)
- Error handling
- Cross-references
- Anti-patterns

**A slash command file does NOT contain:**

- The mechanics of what the agent does
- The full protocol that lives in the agent file or workflow file
- Embedded business logic (e.g. the actual algorithm for calibration aggregation)
- Templates / schemas (those live in `memory/templates/`)

If a command file grows past ~250 lines of body content, that's a smell. The mechanics belong elsewhere. The command file is the **invocation contract**, not the implementation.

### Why this matters

Drift compounds. If the command file embeds 200 lines of business logic, that logic gets out of sync with the agent file's logic — and now there are two sources of truth for "what does `/branch-out` actually do". The thin-shell discipline keeps the agent definition as the single source of truth.

The seven non-workflow commands route to a single agent each. `/digest` and `/consistency-review` are the exceptions — they route to workflow procedures. `/digest` routes to `.claude/workflows/daily-digest.md`, which internally fans out to `source-puller` agents; `/consistency-review` routes to `.claude/workflows/consistency-review.md`, an interactive main-thread triage with no agent spawn. Even there, the command files don't embed the procedures; they point at the workflows.

### Anti-pattern catalogue

- **Embedding the agent's prompt in the command file.** That's how the two sources of truth diverge.
- **Pre-flight that overlaps with agent's internal validation.** Pre-flight is for orchestration prerequisites (CWD, files exist); the agent validates its own inputs.
- **Command file containing tables / templates that are also in `memory/templates/`.** Reference the template, don't duplicate.
- **Command file with a "Process" or "Algorithm" section.** That's agent territory.

---

## 2. Argument syntax conventions

Consistency across the nine commands keeps the muscle memory cheap.

### The three forms

| Form | Use for | Example |
|---|---|---|
| **Positional** | Required primary arg (one per command max) | `/branch-out <situation-slug>` |
| **`--flag`** (boolean) | Switch behavior on/off — no value | `/digest --force` |
| **`--flag value`** or **`--flag=value`** (parameterized) | Pass a value | `/calibration-report --month 2026-04` |

Both `--flag value` and `--flag=value` are supported. Internally the parser handles both. Document either form in usage examples; the principal can use whichever.

### Quoted strings

Multi-word values use quoted strings:

```
/review draft.md --position "we should renew the contract"
```

The parser accepts single or double quotes. Backslash-escape for embedded quotes:

```
/review draft.md --position "the \"strategic\" case for X"
```

### Multi-value

Comma-separated within a single arg:

```
/market-radar --market US,EU
```

Not space-separated (would parse as positional). Not repeated flags (`--market US --market EU`) — unnecessary syntactic variation.

### Required vs optional

- **Required** args go positional (one per command). If absent → STOP with usage hint.
- **Optional** args go as flags. Defaults documented in the command file's argument-syntax table.

If a command has multiple "required-ish" args (e.g. `/branch-out` could in principle require both `--situation-slug` and `--from-digest`), pick **one** as positional and the rest as flags. Two positionals creates ordering ambiguity.

### What we don't use

- **Short flags** (`-f` for `--force`). Inconsistency cost > brevity savings in a low-frequency command set.
- **Subcommands** (`/digest run` vs `/digest configure`). Each subcommand would be its own slash command.
- **Heredocs / multi-line args** at the command level. If a command needs multi-line input, the principal passes a file path (e.g. `/review <path>`).

### Argument parsing implementation

The slash command runtime in Claude Code parses `$ARGUMENTS` as the raw string after the command name. Each command file's pre-flight section interprets that string.

**Bash-style splitter that handles both forms (`--flag value` and `--flag=value`):**

```python
# Conceptual — actual implementation lives in the command runtime
def parse_args(raw):
    tokens = shlex.split(raw)  # handles quotes
    parsed = {"positional": [], "flags": {}, "switches": set()}
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith("--"):
            if "=" in t:
                k, v = t[2:].split("=", 1)
                parsed["flags"][k] = v
            elif i + 1 < len(tokens) and not tokens[i+1].startswith("--"):
                parsed["flags"][t[2:]] = tokens[i+1]
                i += 1
            else:
                parsed["switches"].add(t[2:])
        else:
            parsed["positional"].append(t)
        i += 1
    return parsed
```

A command's pre-flight reads `parsed.positional`, `parsed.flags.get(<name>)`, `parsed.switches`. If a flag was expected and absent, default applies.

---

## 3. Pre-flight pattern

**Every command verifies orchestration prerequisites BEFORE spawning the agent or running the workflow.** Pre-flight is the orchestrator's job; the agent does NOT run pre-flight redundantly.

### Standard pre-flight checks

1. **CWD check.** Working directory is a Giovanni repo. Detection signal: presence of canonical files (`memory/digest_sources.md`, `knowledge/<constitution>.md`, or similar). Failure → STOP with diagnostic.
2. **Agent definition file present.** `.claude/agents/<name>.md` exists. Failure → STOP with the missing path. This catches accidentally-deleted agent files before the `Task` call fails opaquely.
3. **Required state files / config files present.** Per command — e.g. `/branch-out` requires `memory/triage-heuristic.yaml`; `/market-radar` requires `memory/intel/market-radar/_scope.md`.
4. **Cadence guards** (if applicable). E.g. `/digest` has a 4 h cadence guard overridable with `--force`. `/calibration-report` enforces month boundary (no in-progress months).
5. **Empty-cohort short-circuit** (where applicable). E.g. `/shadow-review` STOPs with informational message if no past-horizon pending and filter matches 0 resolved. `/calibration-report` STOPs if no hypotheses match the month.

### Pre-flight failure behavior

- **STOP** with explicit diagnostic. No graceful degradation.
- **No state mutation.** State files are not touched until the agent runs.
- **No agent spawn.** The `Task` call is the expensive step — pre-flight is fast filtering.

If pre-flight is too restrictive, the principal sees a clear "fix this precondition" message. If pre-flight is too lenient, the agent gets bad inputs and fails opaquely.

### What pre-flight does NOT check

- **Domain semantics** — that's the agent's job. E.g. `/branch-out` pre-flight does not verify actor profiles are deep enough; that's `prediction-runtime` Step 2 (the hard-stop logic).
- **Whether the run "should" happen** — e.g. `/market-radar` pre-flight does not pre-decide if a sweep is "worth running". The principal invoked it; the agent runs.
- **Output side effects** — pre-flight is read-only. The orchestrator may create directories (e.g. `memory/audits/consistency/` if missing) but does not write content files until the agent runs.

---

## 4. Agent routing pattern

Seven of the nine commands route to a single agent via `Task`. The exceptions route to workflow procedures: `/digest` (workflow with parallel agent fan-out) and `/consistency-review` (interactive main-thread triage, no agent spawn).

### Single-agent routing (canonical)

```
/<command> <args>
  ↓ pre-flight
  ↓ Task(subagent_type=<agent>, params...)
  ↓ wait for return
  ↓ relay output verbatim
  ↓ no auto-commit
```

The orchestrator passes parsed args as `Task` params. The agent runs in isolated context, returns structured output. The orchestrator relays verbatim.

**Verbatim relay is binding.** The orchestrator does NOT:

- Soften the agent's verdict (especially `/review` / `/redline`)
- Add commentary on the agent's findings
- Suppress findings that seem "harsh"
- Translate output language (the agent matches the draft / source language)

The orchestrator MAY:

- Add a one-line pointer ("Review via `/consistency-review`")
- Surface a related-command suggestion ("Run `/shadow-review` if accuracy callout was flagged")
- Append the file path for written artifacts

### Workflow routing (the `/digest` case)

```
/digest <args>
  ↓ pre-flight
  ↓ run Step 0-3 of workflow inline (read state, determine sources, calc window)
  ↓ Step 4: parallel fan-out — single message, N Task calls to source-puller agents
  ↓ Steps 5-10 inline (synthesis, triage, briefs, shadow lookback, profile signals, drift)
  ↓ Step 12 render
  ↓ Step 11 shadow generation (AFTER render — invisibility is binding)
  ↓ state update
  ↓ no auto-commit
```

The workflow file (`.claude/workflows/daily-digest.md`) defines the 12 steps. The command file points at the workflow and handles orchestration concerns (parallel fan-out, state update, hand-off to drift response sub-flow). The workflow file is the procedural spec; the command file is the runtime contract.

`/consistency-review` follows the same shape minus the fan-out: the command file (`.claude/commands/consistency-review.md`) handles pre-flight + argument resolution, then runs the interactive triage procedure from `.claude/workflows/consistency-review.md` in the main thread — per-finding verdicts come from the principal, so there's no agent to spawn.

### Parallel fan-out (binding pattern in `/digest` Step 4)

**Single message, N agent calls.** All `source-puller` invocations happen in one orchestrator message. Each agent runs in isolated context. Failure isolation: one source failing doesn't block the others.

This pattern is described in [`docs/agents.md`](agents.md) § 3 (Parallel fan-out pattern). The command file doesn't re-document the pattern — it points at the agent doc.

### Sequential chain (where it appears)

Some workflows are sequential: agent A's output feeds agent B. The main thread orchestrates — no auto-handoff between agents.

Example: `researcher` produces a constitution patch proposal → main thread reviews → optional `/review` runs `adversarial-reviewer` on the proposal → main thread applies. The chain is principal-driven, not agent-driven.

Commands do not embed sequential chains. If a workflow requires sequential agent chaining, document it in `.claude/workflows/<name>.md` and have the command point there.

---

## 5. Output behavior pattern

Three output modes:

| Mode | Use for | Examples |
|---|---|---|
| **Chat-only** (ephemeral) | Output that doesn't merit persistence — verdicts, summaries, briefings | `/review`, `/redline`, `/digest` (the digest body itself) |
| **Persistent artifact (unstaged)** | Output that becomes canonical state | `/branch-out` (artifact + decision draft + shadow), `/shadow-review` (audit log + moved YAMLs), `/calibration-report` (report + actor-scores), `/consistency-check` (audit report + state), `/consistency-review` (state update + accepted diffs), `/market-radar` (memo) |
| **Both** | Render summary to chat + write artifact | All persistent-artifact commands also relay a summary |

**No command auto-commits.** This is the binding rule that keeps the git log honest.

### Why no auto-commit

- The principal reviews before committing. Auto-commits bypass review.
- A commit is a decision (the artifact becomes canonical). Decisions belong to the principal, not the orchestrator.
- Auto-commits pollute git history with noise that the principal would have grouped or omitted.

### How "no auto-commit" plays with workflows

Workflows may write multiple files in one run (e.g. `/digest` writes state + briefs + shadow YAMLs). All of these are written **unstaged**. The principal stages and commits in a batch, typically:

- `chore(digest): daily sync <YYYY-MM-DD>` for state + briefs
- `decision: <slug>` for accepted drift patches
- `chore(shadow): generated <N> hypotheses` (if the principal commits the shadow YAMLs separately, which most don't)

The orchestrator surfaces what was written; the principal decides commit groupings.

### Persistent artifact paths (by command)

| Command | Path |
|---|---|
| `/digest` | `memory/digest_state.md`, `memory/briefs/<file>.md`, `memory/shadow/{pending,resolved,expired}/<file>.yaml` |
| `/branch-out` | `memory/branch-out/<today>-<slug>.md`, `memory/decisions/<today>-<slug>.md`, `memory/shadow/pending/<file>.yaml` |
| `/shadow-review` | `memory/calibration/audit-log.md` (append), `memory/shadow/{resolved,expired}/<YYYY-MM>/` (moves) |
| `/calibration-report` | `memory/calibration/monthly/<YYYY-MM>.md`, `memory/calibration/actor-scores.yaml` |
| `/consistency-check` | `memory/audits/consistency/<YYYY-MM-DD>.md`, `memory/audits/consistency/_state.md` (append) |
| `/consistency-review` | `memory/audits/consistency/_state.md` (run entry completed + aggregate precision), accepted diffs applied to target files |
| `/market-radar` | `memory/intel/market-radar/<YYYY-WW>.md` or `memory/intel/market-radar/focused/<YYYY-MM-DD>_<slug>.md` |
| `/review`, `/redline` | none by default (optional `memory/intel/adversarial/` if fork opted in) |

---

## 6. Error handling pattern

Three failure modes:

### Pre-flight failure

**STOP** with explicit diagnostic. No state mutation, no agent spawn.

Examples:

- `ERROR: not in a Giovanni repo (no memory/digest_sources.md). Reinvoke from repo root.`
- `ERROR: prediction-runtime agent definition missing. Cannot run /branch-out.`
- `ERROR: --month <YYYY-MM> is in the future or current. Calibration aggregates completed months only.`

The principal fixes the precondition and reinvokes.

### Agent failure

The agent returns a structured error. The orchestrator surfaces it verbatim.

**No retry from orchestrator.** Retry logic belongs to the principal (re-invoke with adjusted args) or to the agent's internal logic (the agent decides whether to retry an external fetch).

**No graceful degradation that hides failure.** If `/digest` Step 4 has one source fail, that source's section in Step 12 render shows the error explicitly. Honest reporting > coverage theater.

### Cadence guard hit

`/digest` `--force` overrides; `/shadow-review` `--force-review-now` overrides the COI guard (by excluding recent resolutions from the cohort, not by reviewing them); `/calibration-report` and `/consistency-check` don't have hard cadence guards (only advisories).

When a cadence guard is hit:

- **STOP** if it's a hard guard (e.g. `/digest` < 4 h).
- **Advisory** if it's a soft guard (e.g. scope file > 90d stale in `/market-radar`). Continue, but flag.

---

## 7. Cadence guards (per command)

| Command | Guard type | Default | Override |
|---|---|---|---|
| `/digest` | hard | 4 h since last run | `--force` |
| `/branch-out` | soft warning | stale draft for today exists | confirm at prompt (`y/N`) |
| `/shadow-review` | advisory | last run < 60 days ago | continue with advisory |
| `/shadow-review` | hard (COI guard) | any cohort hypothesis `resolved_date` < 48 h ago | `--force-review-now` (excludes recent resolutions from the cohort instead of reviewing them) |
| `/calibration-report` | hard | month boundary (no future / current) | none — can't aggregate incomplete months |
| `/calibration-report` | soft warning | report for `<YYYY-MM>` already exists | confirm at prompt (`y/N`) |
| `/consistency-check` | none (manual cadence) | — | — |
| `/consistency-review` | none (run after each `/consistency-check` during shadow mode) | — | — |
| `/market-radar` | advisory | scope file > 90d stale | continue with advisory |
| `/review`, `/redline` | none | — | — |

The asymmetry reflects domain reality: `/digest` mutates state in non-trivial ways, so a hard cadence guard prevents accidental double-runs. Adversarial review is read-only, so no guard needed. Calibration enforces month boundary because aggregating an in-progress month would produce wrong rolling averages.

---

## 8. Anti-patterns (binding)

What slash commands must NOT do.

### Across all commands

- **Embed business logic.** Mechanics belong in agents or workflows.
- **Auto-commit.** Principal reviews + commits.
- **Soften agent output in relay.** Verbatim relay is binding.
- **Pre-flight that duplicates agent's internal validation.** Pre-flight checks orchestration prerequisites; agents check their own inputs.
- **Swallow errors silently.** STOP with diagnostic; the principal fixes.
- **Auto-spawn follow-up workflows.** E.g. `/market-radar` does not auto-spawn `/branch-out` on a drift candidate. The principal decides.
- **Recurse from another agent's context.** Slash commands always spawn from main thread.
- **Mix internal and external sources.** `/digest` pulls internal (chat, email, calendar, project tracker, version control); `/market-radar` pulls external (PR, LinkedIn, trade press). They do NOT cross.

### Command-specific (highlights — full list in each command file)

- **`/digest`:** no shadow hypotheses in render (binding invisibility); no sequential source pull in main thread
- **`/branch-out`:** no percentages anywhere; no t+3 predictions; no "recommended move"; no caveat-degraded output when actors are shallow
- **`/shadow-review`:** no skipping adversarial-check; no defaulting to matched when uncertain; no auto-modify of `actor-scores.yaml` (that's `/calibration-report`)
- **`/calibration-report`:** no cherry-picking cohort; no generous mixed-verdict aggregation; no auto-applying triage suggestions
- **`/consistency-check`:** no auto-applying proposed diffs; no running on every session-start during shadow mode; no raising the 10-findings cap
- **`/consistency-review`:** no "accept all" without reading findings; no skipping the state-file update; no conflating reject (right finding, wrong diff) with false-positive (wrong finding)
- **`/market-radar`:** no "switch to X" framing for drift candidates; no padding empty memos; no daily cadence
- **`/review`, `/redline`:** no softening verdicts; no RLHF preambles; no language switching in relay

---

## 9. Adding a new slash command

The bar is high. Most work that looks like "I should add a slash command for X" is actually:

- A direct agent invocation (use the `Agent` tool, no shell needed)
- A workflow that runs once a quarter (don't slash-command it, run the workflow ad hoc)
- A script that lives in `scripts/` (e.g. INDEX regen)

Add a slash command only if:

1. **Reusable.** The principal will invoke this enough times that argument-parsing + pre-flight saves measurable friction vs ad-hoc agent spawns.
2. **Orchestration shell adds value.** Pre-flight checks are non-trivial, or the command routes to a multi-step workflow with parallel fan-out.
3. **Thin.** No embedded mechanics. If the command file is ~250 lines, it's not thin.
4. **Discoverable.** Added to `.claude/commands/README.md` registry and to this doc.

Template structure: see `.claude/commands/README.md` § Adding a new slash command.

---

## 10. Lint

`scripts/lint_rules/slash_command_registry.py` validates:

- Every file in `.claude/commands/*.md` (excluding `README.md`) is listed in the README's registry table
- Every entry in the registry table corresponds to a file
- Drift (file added but not registered, file removed but row remains) surfaces as a finding

Severity: low. The lint catches presentation drift, not semantic correctness — semantic correctness is the principal's job at review time.

---

## Cross-references

- **Command registry:** [`.claude/commands/README.md`](../.claude/commands/README.md)
- **Daily digest workflow:** [`.claude/workflows/daily-digest.md`](../.claude/workflows/daily-digest.md)
- **Adversarial review workflow:** [`.claude/workflows/adversarial-review.md`](../.claude/workflows/adversarial-review.md)
- **Agent design patterns:** [`docs/agents.md`](agents.md)
- **Predictive layer doc:** [`docs/prediction.md`](prediction.md)
- **Daily digest policy:** [`docs/digest.md`](digest.md)
- **Adversarial policy:** [`docs/adversarial.md`](adversarial.md)
- **Governance:** [`docs/governance.md`](governance.md)
