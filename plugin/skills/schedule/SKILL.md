---
description: Install, inspect or remove the headless runs listed under `schedule:` in docs/governance.config.yaml (launchd on macOS, printed crontab lines elsewhere).
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/schedule.py *)
disable-model-invocation: true
argument-hint: "install [--dry-run] | uninstall | status | run <name>"
---

# /giovanni:schedule

A self-maintaining instance needs something to wake it. This turns the
`schedule:` list into OS jobs that run `claude -p "<prompt>"` headless in this
repo (GIOVANNI_HEADLESS=1, `--permission-mode dontAsk`, `--permission-prompts none`),
and reports a job that failed or silently stopped through the inbox. Thin shell
over `${CLAUDE_PLUGIN_ROOT}/scripts/schedule.py`; mechanism in
`${CLAUDE_PLUGIN_ROOT}/docs/autonomy.md` § Schedule.

## Usage

```
/giovanni:schedule status
/giovanni:schedule install --dry-run    # print the launchd plists / crontab lines, change nothing
/giovanni:schedule install              # macOS: write ~/Library/LaunchAgents/*.plist and load them
/giovanni:schedule uninstall
/giovanni:schedule run <name>           # run one job now, the way the clock would
```

## Pre-flight (binding — STOP on failure)

1. `schedule:` has at least one valid job (`schedule.py status` lists it).
2. `install` / `uninstall` change the principal's machine. Run them only when the principal typed this command with that argument; show the `--dry-run` output first if they have not seen it.
3. Headless runs can only do what `.claude/settings.json` allows. Before the first install, check that every tool the scheduled prompts need is in `permissions.allow` — a denied tool fails the run quietly into the log (and the inbox).

## Execution flow

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/schedule.py <args>` and relay the output.

## Anti-patterns (binding)

- Never add `--dangerously-skip-permissions` or `bypassPermissions` to a scheduled run.
- Never edit the principal's crontab; print the lines.
