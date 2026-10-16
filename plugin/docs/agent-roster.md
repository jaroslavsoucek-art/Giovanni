# Agent roster

Giovanni's operational subagents. Each lives at `agents/<name>.md` in the plugin (this roster sits in `docs/` because a plugin's `agents/` directory may hold nothing but agent definitions) and is spawned via the `Agent` tool as **`giovanni:<name>`** — the plugin namespaces every agent, so `subagent_type: giovanni:prediction-runtime`, never the bare name. The roster below keeps the bare names because that is what the files are called; prefix when you spawn.

The framework-building **architect agents** (memory-architect, governance-architect, …) are not here. They ran once, during Giovanni's own bootstrap, and live in the framework repo's `agents/`; a fork or a plugin install never needs them.

Design philosophy + invocation patterns: see [`docs/agents.md`](agents.md).

## Operational agent roster

| Agent | One-liner | Model | When to spawn |
|---|---|---|---|
| [`source-puller`](../agents/source-puller.md) | Pull a single source (chat / email / calendar / project tracker / version control / CRM / docs) for a time window — return structured bullets, no synthesis | sonnet | Parallel fan-out in daily digest workflows; any time you need raw signal from one source isolated from main thread context |
| [`researcher`](../agents/researcher.md) | External research via web search + fetch — return structured memory note (FACT / ANALOGY / ESTIMATE) + optional constitution patch proposal | opus | "Investigate X", "research X", "verify claim about Y" — anything requiring sources outside the repo |
| [`profile-bootstrap`](../agents/profile-bootstrap.md) | Bootstrap a new stakeholder profile OR refresh an existing one in `memory/stakeholders/<slug>.md` | opus | "Bootstrap stakeholder X", "refresh profile X", "who is X" (when not yet profiled) |
| [`deliverable-reviewer`](../agents/deliverable-reviewer.md) | Pre-share content QA pass — consistency, diff vs prior, provenance, voice match. SHIP / REWRITE / KILL verdict. Read-only. | opus | After writing any deliverable in `deliverables/`; before sharing externally |
| [`consistency-checker`](../agents/consistency-checker.md) | Semantic drift checks across memory + constitution + agent roster + decision records. Surfaces contradictions that deterministic lint can't catch. | sonnet | Via `/giovanni:consistency-check` — NOT auto. Cadence is configurable per fork. |
| [`market-radar`](../agents/market-radar.md) | Proactive external competitive / market intelligence scan. Default = periodic sweep; focused = topic / market / competitor deep-dive | opus | Via `/giovanni:market-radar`. Manual cadence; weekly default. |
| [`prediction-runtime`](../agents/prediction-runtime.md) | Executes `/giovanni:branch-out` (active simulation), `/giovanni:shadow-review` (quarterly verdict pass), `/giovanni:calibration-report` (monthly aggregation). Carries the 8 binding principles. | opus | Via slash commands — never invoked directly by user. |
| [`adversarial-reviewer`](../agents/adversarial-reviewer.md) | Adversarial review of strategic drafts — SHIP / REWRITE / KILL verdict with strongest counter-case construction. Default-critical mode, no flattery. | opus | Via `/giovanni:review` or `/giovanni:redline`; or when draft contains `[REVIEW]` tag or message starts with `review:` / `redline:` / `before send:` |

## When to spawn (rules of thumb)

- **Bounded specialized work that pollutes main thread context** if done inline → spawn
- **Parallel work that's source-independent** (e.g. 5 sources to pull) → fan-out spawn (one message, N agent calls)
- **Tool scope materially different from main** (e.g. heavy web-fetch budget, repo-wide grep) → spawn to isolate
- **Trivial work** (single grep, single read, single bullet response) → do it inline, don't spawn

Detailed criteria in [`docs/agents.md`](agents.md).

## Hook-gap rule (binding)

**PostToolUse hooks fire only for main-thread writes.** The `post-memory-edit` hook that regenerates `memory/MAP.md` does NOT fire when a subagent writes a file. Consequence:

> Any agent that writes under `memory/` MUST run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/build-memory-map.sh"` as its final step before reporting, or the map-stale lint check fails on the next commit.

Currently applies to: `profile-bootstrap` (stakeholder profiles), `consistency-checker` (audit reports + state), `market-radar` (intel memos), `prediction-runtime` (branch-out artifacts, shadow YAMLs, decision drafts, calibration reports). Each of these agents carries a one-line post-write step referencing this rule. When adding a new writing agent, add the step — don't rediscover the gap.

## Frontmatter convention (all agents)

```yaml
---
name: <kebab-case-name>
description: <one paragraph — when to spawn, what it returns. Include trigger phrases for natural-language invocation.>
tools: <comma-separated tool list — minimal scope>
model: opus | sonnet | haiku
---
```

After the frontmatter:

- One-line headline
- **Inputs the caller MUST provide** (named params)
- **Protocol** (numbered steps)
- **Reporting format** (what the agent returns to main thread)
- **Hard rules** (binding constraints)
- **What you do NOT own** (scope boundaries — critical for preventing recommendation creep)

## Don't add agents lightly

Each new agent adds:

- Cognitive overhead (one more thing to remember to spawn)
- A maintenance burden (description has to stay in sync with body)
- Surface area for scope creep (agents tend to grow capabilities over time)

Bar for adding a new agent: the work is genuinely bounded, parallelizable OR pollution-prone, and reused across enough scenarios to justify the overhead. **If you're tempted to add an agent for a single use case, do the work inline first and revisit after 3 occurrences.** A new agent also needs a line in `.claude-plugin/plugin.json` (`agents` is an explicit list) and a row here (lint: `agent-roster-match`).
