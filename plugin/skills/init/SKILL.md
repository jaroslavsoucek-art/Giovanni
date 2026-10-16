---
description: Scaffold the Giovanni layers into the current repo — memory/, knowledge/, deliverables/, docs/governance.config.yaml, the permission half of .claude/settings.json and the CLAUDE.md operating contract — from the plugin's skeleton. Idempotent; never overwrites a file you have filled.
allowed-tools: Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/init-fork.sh *), Bash(git rev-parse *), Bash(git remote *), Read, Glob
disable-model-invocation: true
argument-hint: "[--force]"
---

# /giovanni:init

Turn the repo you are in into a Giovanni instance. The plugin is the mechanism (skills, agents, hooks, lint); this skill creates the **state** the mechanism operates on, in the project, from `${CLAUDE_PLUGIN_ROOT}/skeleton/` and `${CLAUDE_PLUGIN_ROOT}/templates/`. This skill is a **thin shell** around `${CLAUDE_PLUGIN_ROOT}/scripts/init-fork.sh`; the script is the procedure.

## Usage

```
/giovanni:init            # scaffold the git repo of the cwd; existing files kept
/giovanni:init --force    # re-copy templates over existing runtime files (destructive for filled files — ask first)
```

## Pre-flight (binding — STOP on failure)

1. **Git repo.** `git rev-parse --show-toplevel` succeeds. Otherwise STOP: Giovanni's memory is git-tracked by design; `git init` first.
2. **Not the framework repo.** `git remote get-url origin` does not match `jaroslavsoucek-art/Giovanni`. If it does, STOP and say so — the framework repo is the template, not an instance (the script refuses too; `--force` overrides, which is not something to do on the principal's behalf).
3. **`--force` is explicit.** Only pass it when the principal typed it. It overwrites `knowledge/constitution.md`, `memory/CLAUDE_MEMORY.md` and the other runtime files with blank templates.

## Execution flow

1. Run, from the repo root:
   ```
   bash "${CLAUDE_PLUGIN_ROOT}/scripts/init-fork.sh" --yes --project-root "$(git rev-parse --show-toplevel)" $ARGUMENTS
   ```
2. Relay the script's output verbatim: the `+` / `=` lines say what was created and what was kept, the lint block is the fill-in to-do list (placeholders are expected on a fresh scaffold — do not call them errors), the closing block is the next steps.
3. If the script reported `CLAUDE.md is yours — kept`, tell the principal the one line to add to their `CLAUDE.md` (`@docs/CLAUDE.giovanni.md`) and offer to add it. Do not add it unasked.
4. If the script printed the fork-clone block (`claude plugin marketplace add …`), repeat those two commands — they run outside the session.
5. **No commit.** Show `git status --short` and stop. The principal reviews the scaffold and commits.

## Output behavior

- Writes: `knowledge/`, `memory/`, `deliverables/`, `docs/governance.config.yaml`, `.claude/settings.json`, `CLAUDE.md` (or `docs/CLAUDE.giovanni.md`), the plugin-root marker in `.git/`.
- Never writes outside the project root. Never touches the plugin.
- Idempotent: a second run reports `= … exists — kept` for every file and changes nothing.

## Error handling

- Script exit 2 with `origin looks like the Giovanni framework repo` → relay, stop. Do not retry with `--force`.
- Script exit 2 with `expected template missing` → the plugin install is incomplete; suggest `claude plugin update giovanni@giovanni` and stop.
- Lint findings → informational on a fresh scaffold. Only `[CRITICAL]` lines about files the script just created (not about placeholders) are worth flagging.

## Cross-references

- Procedure: `${CLAUDE_PLUGIN_ROOT}/scripts/init-fork.sh`
- Walkthrough after scaffolding: `${CLAUDE_PLUGIN_ROOT}/docs/setup-guide.md`
- Why settings.json carries the permissions and the plugin carries the hooks: `${CLAUDE_PLUGIN_ROOT}/docs/governance.md` § External write gate
- Git gates (pre-commit regen + lint, pre-push): `${CLAUDE_PLUGIN_ROOT}/scripts/install-hooks.sh`

## Anti-patterns (binding)

- Do not fill the constitution or the L1 memory on the principal's behalf during init. Scaffold, then stop.
- Do not pass `--force` because a file "looks empty". The script keeps it; the principal decides.
- Do not commit. Do not `git add`.
