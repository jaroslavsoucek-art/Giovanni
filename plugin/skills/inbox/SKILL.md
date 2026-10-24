---
description: Show the inbox — the one ranked list every Giovanni loop writes to — and act on the principal's one-word answers (yes / no / later). Headless-safe.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py *), Read, Edit, Write, Skill
disable-model-invocation: false
argument-hint: "[refresh]"
---

# /giovanni:inbox

The inbox is the interface between the loops and the principal: deadlines from
project refreshers, lint findings, a scheduled run that did not happen, a skill
the learning loop could write, a canon change waiting for an OK. This skill is a
**thin shell** over `${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py`; the mechanism is
in `${CLAUDE_PLUGIN_ROOT}/docs/autonomy.md` § Inbox.

The session-start hook already shows the list when it is non-empty. Run this
skill when the principal asks for it again ("what's on today?"), or with
`refresh` to re-run the producers first.

## Usage

```
/giovanni:inbox            # render the open items
/giovanni:inbox refresh    # run refreshers + lint→inbox + scheduler check, then render
```

## Pre-flight (binding — STOP on failure)

1. The project has an inbox: an `inbox:` block in `docs/governance.config.yaml` or an existing `memory/inbox.yaml`. Otherwise STOP: "No inbox configured — see docs/autonomy.md § Inbox."

## Execution flow

1. `refresh` given → `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py refresh`.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py render` → show it to the principal verbatim.
3. For the actions, read `inbox.py list --json` (it carries `on_yes`, `ref`, `key`).
4. Act on the answers, item by item:
   - **yes** → do exactly the item's `on_yes` (a command, a skill, or a one-line instruction), within this session's normal permission rules — an `on_yes` never widens them. Then `inbox.py resolve <id>`.
   - **no** → `inbox.py resolve <id> --status dismissed`.
   - **later Nd** → `inbox.py snooze <id> --days N`.
   - no answer → leave the item; do not chase.
5. Report in one line per item what was done.

## Headless (GIOVANNI_HEADLESS=1)

Run step 1, then stop: nobody is there to answer. Do not resolve anything.

## Output behavior

- Writes: `memory/inbox.yaml`, `memory/archive/inbox-YYYY-MM.md` (closed items). Whatever an approved `on_yes` writes.
- Commits nothing itself; the autocommit Stop hook (when configured) picks up `memory/`.

## Anti-patterns (binding)

- Do not run an `on_yes` without the principal's yes for that item. "Do everything" is a yes to each item **listed in the reply you answered**, not to items added since.
- Do not add items to make the list look complete; producers add items, this skill answers them.
- Do not edit `memory/inbox.yaml` by hand; use the script (it locks, dedupes and archives).
- An item whose `on_yes` reaches an external system still goes through the external write gate.
