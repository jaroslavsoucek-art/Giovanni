# Giovanni — AI Chief of Staff plugin

Giovanni is the mechanism of an AI Chief of Staff for Claude Code. It gives one principal who runs a high-context, multi-stakeholder program an assistant that still reads the situation correctly in month six: memory that resists drift, stakeholders modelled as sentiment trajectories, predictions that are scored without contaminating themselves, and review that defaults to critical instead of agreeable.

The plugin holds the mechanism. The state it operates on lives in **your** repository, in git, and is scaffolded by `/giovanni:init`.

## What is in the plugin

| Component | Count | What it does |
|---|---|---|
| Skills | 14 | `/giovanni:init`, `/giovanni:digest`, `/giovanni:branch-out`, `/giovanni:shadow-review`, `/giovanni:calibration-report`, `/giovanni:consistency-check`, `/giovanni:consistency-review`, `/giovanni:pulse`, `/giovanni:market-radar`, `/giovanni:review`, `/giovanni:redline`, `/giovanni:inbox`, `/giovanni:learn`, `/giovanni:schedule` — see [`skills/README.md`](skills/README.md) |
| Agents | 8 | `source-puller`, `researcher`, `profile-bootstrap`, `deliverable-reviewer`, `consistency-checker`, `market-radar`, `prediction-runtime`, `adversarial-reviewer` — see [`docs/agent-roster.md`](docs/agent-roster.md) |
| Hooks | 5 events | `SessionStart` (digest and audit cadence reminders, inbox), `PreToolUse` (external write gate on MCP tools, decision-record check on git commits, confirm paths), `PostToolUse` (regenerate indexes after edits to `knowledge/` or `memory/`, constitution-edit reminder), `Stop` (unmerged-branch and uncommitted-work warnings, autocommit, session record), `UserPromptSubmit` (correction capture). The autonomy hooks are no-ops until configured |
| Lint | 26 Python rules + bash checks, plus your project's own | `scripts/lint.sh` + `scripts/lint.py`: hard limits on memory size, strikethrough ratio, shard staleness, decision-record trigger conditions, agent-roster drift, domain leak, and more — see [`docs/invariants.md`](docs/invariants.md) |
| Autonomy layer (opt-in) | — | Switch layers off (`--without predictive,stakeholders,digest`), one inbox every loop writes to, per-path autocommit vs confirm, headless runs on a clock, a learning loop that proposes skills from repetition and rules from corrections — see [`docs/autonomy.md`](docs/autonomy.md) |
| Templates and skeleton | — | Everything `/giovanni:init` copies into your repo: constitution, memory layers, stakeholder profile, decision record, governance config, `CLAUDE.md` operating contract |

## Install

```
/plugin marketplace add jaroslavsoucek-art/Giovanni
/plugin install giovanni@giovanni
/giovanni:init
```

Then fill the constitution, the stakeholder profiles and the digest sources. The multi-hour part is yours; [`docs/setup-guide.md`](docs/setup-guide.md) walks through it step by step.

## What the plugin runs, reads and sends

- **Hooks** are plain shell scripts that run locally. They read the current repository (git status, staged files, the memory state files) and call two Python helpers in `hooks/lib/` for JSON parsing, date arithmetic and the write-gate decision. They need `git` and Python 3 with PyYAML (on Windows also Git for Windows, whose Git Bash runs them). They make no network calls except an opt-in `git push` of automatic commits (`autonomy.auto_push`), and send nothing to the author or any Giovanni service.
- **Skills and agents** read and write files inside the repository the session is open in. `researcher` and `market-radar` use Claude Code's web search and fetch tools when you invoke them. `source-puller` reads whatever MCP connectors you configure yourself (chat, tasks, mail, calendar); the plugin ships none.
- **The external write gate** (`hooks/block-external-writes.sh`) turns every write-type MCP tool call into an explicit per-action confirmation and denies writes to channels you demote to read-only. Reads pass. The permission half of the gate (`permissions.ask` / `permissions.deny`) is written into your project's `.claude/settings.json` by `/giovanni:init`; a plugin cannot ship it.
- **Opt-in autonomy layer** ([`docs/autonomy.md`](docs/autonomy.md)): when configured, a Stop hook commits the paths you list (and pushes to your remote if you say so), and the learning loop keeps a local, gitignored record of each session's generalised tool steps — no prompt text. `/giovanni:schedule install` adds launchd agents only when you run it.
- No credentials, no remote telemetry, no package installs, no `npx`/`uvx` launchers.

## Where it works

macOS, Linux and native Windows. On Windows the hooks run through Git Bash, so [Git for Windows](https://git-scm.com/downloads/win) must be installed, plus Python 3 with PyYAML (`python3`, `python` or `py` all work: `hooks/lib/env.sh` finds the one that runs and forces UTF-8). `bash plugin/scripts/platform-smoke.sh` runs every hook the way Claude Code does and says what fails on the machine it runs on. CI runs it on Linux and Windows.

Hooks, agents and the git gates need Claude Code. Installed from the Claude directory into claude.ai or Cowork, only the skills load; the memory discipline and the review verdict format still apply, the automatic gates do not.

## Repository layout

The plugin is the `plugin/` folder of [jaroslavsoucek-art/Giovanni](https://github.com/jaroslavsoucek-art/Giovanni). The repository root carries the marketplace manifest, the CI, the framework-level docs and a synthetic filled instance under `examples/lattice-finance/` that shows what a running Giovanni looks like.

## Privacy

No server, no telemetry, nothing sent to the author. What the plugin reads, what it writes into your repository (stakeholder profiles are personal data; keep the repository private) and what leaves your machine: [`PRIVACY.md`](PRIVACY.md).

## License

MIT. See the `license` field in `.claude-plugin/plugin.json` and the `LICENSE` file at the repository root.
