# Autonomy — layers, inbox, autocommit, schedule, learning

> **Status:** opt-in mechanism, 0.2.0. Every piece is a no-op until a project configures it in `docs/governance.config.yaml`. Built for an instance whose principal does not maintain the system and does not read diffs — the opposite of the principal Giovanni was distilled from. If your principal *is* the maintainer, you may want none of this.

Giovanni's default contract is: the agent proposes, the principal reviews, the principal commits. It assumes someone who reads diffs, runs audits on a cadence and remembers to say "remember this". Hand the same system to someone who does not, and it fails in a predictable order: state is never committed, audits never run, the cadence hooks nag into a void, and in month three the repo describes a world that ended in month one.

The autonomy layer replaces "the principal maintains it" with four mechanisms and one rule:

| Mechanism | Replaces | Where |
|---|---|---|
| **Inbox** | hook warnings, digest asks, audit reminders scattered across places | `scripts/inbox.py`, hook `session-start-inbox.sh`, skill `/giovanni:inbox` |
| **Autonomy profile** | "commit only when asked" | hooks `pre-edit-confirm.sh`, `stop-autocommit.sh` → `hooks/lib/autonomy.py` |
| **Schedule** | the principal remembering to run things | `scripts/schedule.py`, skill `/giovanni:schedule` |
| **Learning loop** | the maintainer writing skills and rules | hooks `stop-session-record.sh`, `prompt-correction.sh` → `hooks/lib/learning.py`; `scripts/mine-workflows.py`, skill `/giovanni:learn` |

**The rule:** anything reversible inside the repo outside canon happens on its own. Canon, deletion, and anything that leaves the machine waits for a one-word yes. Nothing outside the repo is ever done on a yes that has not been asked for item by item.

---

## Layers {#layers}

Not every domain needs every layer. A principal working on unconnected cases (a lawyer's matters, an administrator's insolvencies, a consultant's engagements) has no use for a sentiment-trajectory profile of a counterparty they meet once, and no basis for calibrated predictions about them. Carrying those layers anyway costs context on every turn and produces lint findings about files nobody should fill.

```yaml
layers:
  predictive: false     # branch-out, shadow hypotheses, calibration
  stakeholders: false   # per-person trajectory profiles
  digest: false         # multi-source daily digest
```

A layer set to `false`: init does not scaffold its files or directories (`init-fork.sh --without predictive,stakeholders,digest` sets the flags on a fresh project); its lint rules no-op (a rule declares `LAYER = "<name>"`); its skills STOP in pre-flight. Absent = on, so existing instances do not change.

**Project lint rules.** A domain that drops layers usually adds its own invariants (a case file has a phase; a deadline has a source). `project_lint_rules_dir` (default `scripts/lint_rules`) is discovered next to the plugin's rules, same contract — `CHECK_ID`, `run(ctx)`, optional `LAYER`. A project rule cannot shadow a plugin rule (same `CHECK_ID` → skipped with a warning).

---

## Inbox {#inbox}

**Why one list.** A self-maintaining assistant generates a steady trickle of small asks: verify a computed deadline, fix a lint finding, the morning run did not happen, a skill could be written. Spread across hook messages they are noise, and noise is ignored. In one ranked list, shown first, answerable with one word per item, they are a two-minute morning routine.

State: `memory/inbox.yaml` — open and snoozed items only. Closed items leave the file and land as one line in `memory/archive/inbox-YYYY-MM.md`. (The same lesson as `digest-state-size`: a file rewritten every run must not accumulate.)

| Field | Meaning |
|---|---|
| `key` | dedupe key. A producer that reports the same thing again updates the item instead of adding a twin. |
| `source` | the producer. `sync-source <source> --keep …` closes that producer's items it no longer reports, so items close themselves when the cause goes away. |
| `on_yes` | what the agent does when the principal says yes. A command, a skill, or one instruction. It never widens permissions; an external write still hits the write gate. |
| `due` | a date the item is about. **Dated items never expire**: past `due` they escalate to high priority with an overdue label, and only their producer closes them. A deadline that silently ages out of a to-do list is the failure this list exists to prevent. |
| `expires` | undated items leave after `default_expiry_days` unanswered. An ask nobody answered in two weeks was not worth asking. |
| *(no)* | a "no" to an undated item mutes its key for `dismiss_days` (default 30). Otherwise a producer that still sees the cause asks again at the next session start, and "no" means nothing. Dated items cannot be dismissed away: the answer to a deadline is what happened to it, recorded by its producer. |

**Producers** at session start (`inbox.py refresh`): the project's `refreshers` (commands that call `inbox.py add` / `sync-source` themselves), `lint_to_inbox` (findings ≥ `lint_min_severity`; they close themselves when the lint goes clean), the scheduler check, expiry. Producers elsewhere: the autocommit hook, scheduled runs, the learning loop.

**Overflow is a finding.** More than `max_open` open items (default 10) means the loops produce more than one person answers. Lint `inbox-health` flags it. The fix is upstream — the noisiest producer — never a higher cap.

---

## Autonomy profile {#autonomy-profile}

```yaml
autonomy:
  auto_commit_paths: ["cases/*", "memory/*"]
  confirm_paths: ["knowledge/*", "CLAUDE.md", ".claude/*", "docs/governance.config.yaml"]
  auto_push: true
```

Globs are `fnmatch` on the repo-relative path; `*` crosses directories.

- **Confirm paths are canon.** An `Edit`/`Write` there gets `permissionDecision: ask` with the reason; in a headless run it is **denied** (nobody is there to answer — the run must put the proposal in the inbox instead). Shell edits walk past this hook, which is why the second layer exists:
- **Autocommit** (Stop hook, backgrounded so a turn never waits): changes under `auto_commit_paths` and not under `confirm_paths` are committed through the normal git pre-commit gate (regen + lint). A blocked commit is unstaged and becomes a high-priority inbox item with the first lint line; the next turn retries. Uncommitted changes under `confirm_paths` become one inbox item per file ("waits for your OK"). Hand-staged files outside the set → skip + inbox item; the hook never commits what someone else staged. Mid-merge / rebase / cherry-pick → skip.
- **Auto-push** only for a private backup remote. A failed push is an inbox item, not a retry loop.

Why not "commit everything at the end of the session": sessions do not end cleanly (a closed laptop is not a SessionEnd), and a Stop-per-turn commit is the only cadence that survives that. Why the lint gate stays on: an autocommit that bypasses lint turns the lint into a suggestion within a week.

---

## Schedule {#schedule}

```yaml
schedule:
  - name: morning
    prompt: "/<your-sync-skill> all"
    at: "07:30"
    weekdays: [1, 2, 3, 4, 5]
```

`/giovanni:schedule install` writes one launchd agent per job on macOS. On Linux it prints crontab lines and edits nothing. On Windows it writes a small runner per job into `memory/.runs/` and prints the `schtasks` commands that call it through Git Bash; the Claude Desktop app's own scheduled tasks are the better choice there, because they use the app's login. The job resolves the plugin path at run time from `.git/giovanni-plugin-root` — the plugin cache path changes with every version, so a baked-in path would break on the first update.

A run is `claude -p "<prompt>" --permission-mode dontAsk --permission-prompts none` with `GIOVANNI_HEADLESS=1`: anything not pre-allowed in `.claude/settings.json` is denied rather than waited on. **That is the headless safety model**: the allow list is the whole capability set of an unattended run. Review it before installing.

Health: each run's log goes to `memory/.runs/<name>-<date>.log` (last 14 kept); `state.json` keeps the last success. A failed run, a job without a success within its period + 1 day (machine asleep or off at run time), and jobs configured but not installed on this machine all become inbox items. A scheduler that stopped silently is worse than none, because everyone believes it runs.

---

## Learning loop {#learning}

"Learns by itself" means two things here, both as files in the repo, both proposal-only:

1. **Repetition → skill.** The Stop hook records each session's *shape* — the ordered tool steps, generalised: paths under `learning.unit_dirs` masked to `*`, digits to `#`, shell reads collapsed to `read`; no prompt text, no file contents — in `memory/.telemetry/sessions.jsonl` (gitignored, machine-local, capped at 500 sessions). `mine-workflows.py` (weekly, via `/giovanni:learn`) finds contiguous 3–6-step sequences that recur in ≥ `min_sessions` distinct sessions, contain at least one effectful step and no step that is already a skill, keeps the maximal ones, and proposes the top few through the inbox. On yes, `/giovanni:learn accept <slug>` drafts a project skill (`generated_from:` in its frontmatter) and a route-table row, in an interactive session — `.claude/` is a confirm path, so the write itself asks.
2. **Correction → rule.** A `UserPromptSubmit` hook matches `learning.correction_markers` (regexes; set them in the principal's working language). On a match the agent is told to classify before continuing: **skill-fix** (fix the procedure now, say which file), **rule** (a standing preference → canon patch proposed through the inbox), **one-off** — and log one line to `memory/learning/corrections.md`. The weekly run proposes one-offs whose target repeats as rules.
3. **Pruning.** A generated skill unused for `retire_after_days` is proposed for retirement (`.claude/skills/_retired/`, one level deeper, no longer discovered). Hand-written skills are never proposed for retirement.

What the loop does **not** do: change domain knowledge on its own (law, regulation, prices — a wrong rule is worse than a stale one; changes there are flags plus drafts), activate anything without a yes, or learn from prompt text.

---

## What stays human {#what-stays-human}

Being explicit about this is the difference between "self-maintaining" and "unattended":

- **The yes.** Canon changes, new skills, deletion, anything that leaves the machine.
- **Tuning in the first month.** Thresholds (`min_sessions`, `max_open`, `lint_min_severity`, markers) are guesses until the instance has run against real work. Expect the first proposals to be bad.
- **Domain truth.** The loop can notice that something changed; it cannot decide that the new reading of a statute is right.

---

## Failure modes this layer is built against {#failure-modes}

| Failure | Mechanism |
|---|---|
| State never committed because the principal does not commit | autocommit of `auto_commit_paths` |
| Canon edited quietly by an over-eager session | confirm-gate (ask / headless deny) + autocommit never commits confirm paths |
| A deadline ages out of the to-do list | dated inbox items never expire; they escalate |
| Morning run silently stopped (machine off, auth expired) | scheduler check → inbox |
| Inbox becomes a backlog | `max_open` + lint `inbox-health`; fix the producer |
| Learning loop writes skills nobody asked for | proposals only; accept is interactive and asks |
| Skill sprawl | usage-based retirement proposals |
| Telemetry leaks case data | generalised steps only, masked unit dirs, gitignored |
