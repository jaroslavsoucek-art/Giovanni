---
description: Manual per-finding triage of a /giovanni:consistency-check report — accept-diff / reject / defer / false-positive verdicts, precision tally update. Interactive main-thread workflow, no agent spawn.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
disable-model-invocation: true
argument-hint: "[<YYYY-MM-DD>]"
---

# /giovanni:consistency-review

Triage the findings of a `/giovanni:consistency-check` run, one by one, with the principal as decision-maker. This command is a **thin shell** — the triage procedure lives in `${CLAUDE_PLUGIN_ROOT}/skills/consistency-review/procedure.md`. This file is the invocation contract.

Like `/giovanni:digest`, this command routes to a workflow procedure rather than an agent: triage is interactive (per-finding verdicts from the principal), so it runs in the main thread.

## Usage

```
/giovanni:consistency-review <YYYY-MM-DD>    # triage the report for that date
/giovanni:consistency-review                 # defaults to the most recent report
```

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `<YYYY-MM-DD>` | positional date | most recent report | Which report in `memory/audits/consistency/` to triage. |

## Pre-flight (binding — STOP on failure)

1. **CWD check.** Working directory is a Giovanni repo (presence of `memory/CLAUDE_MEMORY.md` + `knowledge/<constitution>.md`). Otherwise STOP.
2. **Report file present.** `memory/audits/consistency/<YYYY-MM-DD>.md` exists (after resolving the default). Missing → STOP:
   `ERROR: no consistency report for <YYYY-MM-DD>. Run /giovanni:consistency-check first.`
3. **State file present.** `memory/audits/consistency/_state.md` exists. If missing → seed per the `/giovanni:consistency-check` auto-seed rules (shadow window starts today, 28 days) and surface an advisory — a review without a state file can't record precision.
4. **Run entry present.** `_state.md` contains a `## Run <YYYY-MM-DD>` entry for the report being reviewed. Missing → STOP with diagnostic (report and state are written together by the agent; a missing entry means a corrupted run).
5. **Not already reviewed.** If the run entry has `review_status: complete`, warn and confirm at prompt (`y/N`) before re-reviewing — a re-review overwrites the prior verdict counts.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Run the workflow procedure** per `${CLAUDE_PLUGIN_ROOT}/skills/consistency-review/procedure.md`:
   - Step 1: open the report, print summary + findings
   - Step 2: per-finding interactive triage (accept / reject / defer / false-positive)
   - Step 3: apply accepted diffs (bottom-to-top within a file)
   - Step 4: update the run entry + aggregate precision metrics in `_state.md`
   - Step 5: propose the batch commit — **wait for the principal's explicit go**
   - Step 6: shadow-mode promotion gate check (only after `shadow_mode_end_date`)
3. **No auto-commit.** The commit in Step 5 happens only on the principal's confirmation.

## Output behavior

- **Render target:** chat (per-finding prompts + final verdict summary).
- **Persistent artifacts (unstaged until the Step 5 commit):**
  - `memory/audits/consistency/_state.md` — run entry completed + aggregates updated
  - Target files touched by accepted diffs (constitution, memory, agents, decisions — whatever the findings pointed at)
- **No mutation without a verdict.** Diffs are applied only on explicit `accept` / `accept-with-modification`.

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Principal abandons mid-review** → findings triaged so far keep their verdicts; the run entry stays `review_status: pending` with a partial-review note. Re-invoking resumes at the first unverdicted finding.
- **Accepted diff no longer applies** (target file changed since the check ran) → surface the mismatch, ask the principal to re-verdict against the current file state. Never force-apply a stale diff.

## Cadence guidance

- **During shadow mode:** run after **each** `/giovanni:consistency-check` — every run needs a precision score or the shadow-mode gate has no evidence.
- **After shadow mode:** run when a check surfaces findings; unreviewed reports accumulate as operational debt.

## Cross-references

- **Workflow procedure:** `${CLAUDE_PLUGIN_ROOT}/skills/consistency-review/procedure.md`
- **Producer command:** `${CLAUDE_PLUGIN_ROOT}/skills/consistency-check/SKILL.md`
- **Agent that writes the reports:** `${CLAUDE_PLUGIN_ROOT}/agents/consistency-checker.md`
- **State file:** `memory/audits/consistency/_state.md`
- **Governance policy:** `${CLAUDE_PLUGIN_ROOT}/docs/governance.md` § Consistency checks (shadow mode + promotion criteria)

## Anti-patterns (binding)

- **"Accept all" without reading findings** — defeats the precision metric the whole shadow mode hinges on.
- **Skipping the state-file update** — an unrecorded review is a wasted review.
- **Auto-committing** — the Step 5 commit is principal-gated, always.
- **Conflating reject and false-positive** — reject = real finding, wrong diff; false-positive = wrong finding. The distinction is the signal.
- **Reviewing from an agent context** — this is a main-thread interactive workflow; spawning it inside an agent hides the verdicts from the principal.
