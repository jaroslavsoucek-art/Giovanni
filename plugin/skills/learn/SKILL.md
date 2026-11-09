---
description: The learning loop — mine repeated workflows into skill proposals, prune unused generated skills, promote repeated corrections to rules; and, on the principal's yes, draft or retire a skill. Weekly; the mining half is headless-safe.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mine-workflows.py *), Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py *), Bash(git mv *), Read, Edit, Write, Glob, Grep
disable-model-invocation: true
argument-hint: "[accept <slug> | reject <slug> | retire <skill>]"
---

# /giovanni:learn

How an instance gets better without anyone maintaining it: repetition becomes a
skill, a repeated correction becomes a rule, a skill nobody uses goes away. All
three only as **proposals in the inbox**; nothing activates itself. Thin shell
over `${CLAUDE_PLUGIN_ROOT}/scripts/mine-workflows.py`; mechanism in
`${CLAUDE_PLUGIN_ROOT}/docs/autonomy.md` § Learning.

## Usage

```
/giovanni:learn                  # weekly: mine + usage + corrections → inbox (headless-safe)
/giovanni:learn accept <slug>    # draft a project skill from memory/learning/candidates/<slug>.md
/giovanni:learn reject <slug>    # mark a candidate rejected; it is never proposed again
/giovanni:learn retire <skill>   # move a generated skill out of the active set
```

## Pre-flight (binding — STOP on failure)

1. `learning:` is configured and on (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gconfig.py get learning.enabled` → `true`). Otherwise STOP.
2. `accept` / `retire` in a headless run (GIOVANNI_HEADLESS=1) → STOP: writing a skill needs the principal.

## Execution flow — weekly (no argument)

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mine-workflows.py all`
2. Relay the three counts. Proposals are in the inbox; do not draft anything.

## Execution flow — `accept <slug>`

1. Read `memory/learning/candidates/<slug>.md` (the generalised step sequence and when it was seen).
2. Find what the sequence *does* in this project: the files and scripts its steps name, the route table in `CLAUDE.md`, existing skills in `.claude/skills/` (do not duplicate one — extend it instead and say so).
3. Ask the principal for a name and one sentence of what the routine is for, unless the candidate makes it obvious; offer 2–3 names.
4. Draft `.claude/skills/<name>/SKILL.md` in the project (never in the plugin), thin-shell format (`${CLAUDE_PLUGIN_ROOT}/skills/README.md` § Adding a new skill), in the principal's working language, with frontmatter:
   ```yaml
   name: <name>
   description: <one line — when to use it>
   generated_from: memory/learning/candidates/<slug>.md
   generated_on: <YYYY-MM-DD>
   disable-model-invocation: true
   ```
   Steps that write outside the repo keep their gates; a skill never grants itself permissions.
5. Add a row for it to the route table in `CLAUDE.md` (trigger · file · writes · stops at · autonomy).
6. Show the draft. `.claude/` is normally a confirm path, so the write itself asks; that ask is the principal's yes.
7. Set `status: accepted` in the candidate file; `inbox.py resolve mining:<slug>`.

## Execution flow — `reject <slug>` / `retire <skill>`

- reject: `status: rejected` in the candidate file; `inbox.py resolve mining:<slug> --status dismissed`.
- retire: `git mv .claude/skills/<skill> .claude/skills/_retired/<skill>` (one level deeper = no longer discovered), remove its route-table row, `inbox.py resolve usage:<skill>`.

## Output behavior

- Weekly: `memory/learning/candidates/*.md`, `memory/inbox.yaml`.
- accept / retire: `.claude/skills/…`, `CLAUDE.md` route table, the candidate file, the inbox.
- Commits nothing itself.

## Anti-patterns (binding)

- Never write a skill without the principal's yes on that candidate.
- Never write into `${CLAUDE_PLUGIN_ROOT}`. Generated skills belong to the project.
- Never copy prompt text, names or case data from telemetry or corrections into a skill; the telemetry holds only generalised steps by design.
- Do not lower `min_sessions` to produce proposals. An empty week is a valid result.
