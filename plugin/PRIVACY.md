# Privacy

Giovanni is a Claude Code plugin. It runs on your machine, inside your Claude Code session, against a git repository you own. There is no Giovanni server, account or analytics. Nothing the plugin reads is sent to the plugin's author or to any service the plugin operates.

## What the plugin reads

- Files in the repository the session is open in: `memory/`, `knowledge/`, `deliverables/`, `docs/governance.config.yaml`, `CLAUDE.md`, and git metadata (status, staged files, log).
- When you run `/giovanni:digest`, the `source-puller` agent reads the MCP connectors **you** have configured in Claude Code (chat, mail, calendar, task tracker). The plugin ships no connectors and holds no credentials for them.
- When you run `/giovanni:market-radar` or the `researcher` agent, they use Claude Code's own web search and fetch tools on public pages.

## What the plugin stores, and where

Everything the plugin writes lands in your repository, in plain text, under your control:

- Stakeholder profiles (`memory/stakeholders/`): names, roles, observed sentiment over time, predicted reactions. These are personal data about the people you work with. Keep the repository private.
- Digest state, briefs, decision records, shadow hypotheses and calibration scores (`memory/`).
- Regenerated indexes (`knowledge/INDEX.md`, `memory/MAP.md`).

- **Only if you enable the learning loop** (`learning:` in `docs/governance.config.yaml`): a local record of each session's *shape* — the ordered tool steps, generalised (paths under the directories you name are masked, digits replaced, no prompt text, no file contents) — in `memory/.telemetry/sessions.jsonl`. It is machine-local, gitignored by `/giovanni:init`, capped at 500 sessions, and read only by `scripts/mine-workflows.py` on the same machine.
- **Only if you enable the autonomy layer**: the inbox (`memory/inbox.yaml`, closed items in `memory/archive/`), the corrections log (`memory/learning/corrections.md`), scheduled-run logs (`memory/.runs/`, gitignored).

Retention is yours to decide: the data lives in your git history until you remove it. The plugin never deletes repository content.

## What leaves your machine

Nothing goes to the plugin's author. Data leaves your machine only through channels you already use: Claude itself (your conversation, under Anthropic's terms for your plan), the MCP connectors you configured, and git pushes you make. The plugin's hooks make no network calls, with one opt-in exception: with `autonomy.auto_push: true` the Stop hook pushes automatic commits to the git remote **you** configured. `/giovanni:schedule install` writes launchd agents into `~/Library/LaunchAgents/` that run Claude Code headless on the schedule you set; it does nothing until you run it. The external write gate (`hooks/block-external-writes.sh`) turns every write-type call to an external connector into an explicit confirmation.

## Contact

Questions or concerns: open an issue at https://github.com/jaroslavsoucek-art/Giovanni/issues.
