# Agents

Custom subagents for Giovanni. Each lives at `.claude/agents/<name>.md` and is spawned via the `Agent` tool (or via slash commands that route through `prediction-runtime`).

Two populations live in this directory:

1. **Architect agents** — framework-builders. Spawned during Giovanni bootstrap to produce templates / docs / scripts. **Frozen after bootstrap** — they don't run in daily operations. (memory-architect, governance-architect, stakeholder-architect, prediction-architect, subagent-roster-architect, adversarial-architect, digest-architect, slash-command-architect)

2. **Operational agents** — worker agents. Spawned by the fork's user during daily operations. **This is what the rest of this README is about.**

Design philosophy + invocation patterns: see [`docs/agents.md`](../../docs/agents.md).

## Operational agent roster

| Agent | One-liner | Model | When to spawn |
|---|---|---|---|
| [`source-puller`](source-puller.md) | Pull a single source (chat / email / calendar / project tracker / version control / CRM / docs) for a time window — return structured bullets, no synthesis | sonnet | Parallel fan-out in daily digest workflows; any time you need raw signal from one source isolated from main thread context |
| [`researcher`](researcher.md) | External research via web search + fetch — return structured memory note (FACT / ANALOGY / ESTIMATE) + optional constitution patch proposal | opus | "Investigate X", "research X", "verify claim about Y" — anything requiring sources outside the repo |
| [`profile-bootstrap`](profile-bootstrap.md) | Bootstrap a new stakeholder profile OR refresh an existing one in `memory/stakeholders/<slug>.md` | opus | "Bootstrap stakeholder X", "refresh profile X", "who is X" (when not yet profiled) |
| [`deliverable-reviewer`](deliverable-reviewer.md) | Pre-share content QA pass — consistency, diff vs prior, provenance, voice match. SHIP / REWRITE / KILL verdict. Read-only. | opus | After writing any deliverable in `deliverables/`; before sharing externally |
| [`consistency-checker`](consistency-checker.md) | Semantic drift checks across memory + constitution + agent roster + decision records. Surfaces contradictions that deterministic lint can't catch. | sonnet | Via `/consistency-check` slash command — NOT auto. Cadence is configurable per fork. |
| [`market-radar`](market-radar.md) | Proactive external competitive / market intelligence scan. Default = periodic sweep; focused = topic / market / competitor deep-dive | opus | Via `/market-radar` slash command. Manual cadence; weekly default. |
| [`prediction-runtime`](prediction-runtime.md) | Executes `/branch-out` (active simulation), `/shadow-review` (quarterly verdict pass), `/calibration-report` (monthly aggregation). Carries the 8 binding principles. | opus | Via slash commands — never invoked directly by user. |
| [`adversarial-reviewer`](adversarial-reviewer.md) | Adversarial review of strategic drafts — SHIP / REWRITE / KILL verdict with strongest counter-case construction. Default-critical mode, no flattery. | sonnet | Via `/review` or `/redline` slash commands; or when draft contains `[REVIEW]` tag or message starts with `review:` / `redline:` / `before send:` |

## When to spawn (rules of thumb)

- **Bounded specialized work that pollutes main thread context** if done inline → spawn
- **Parallel work that's source-independent** (e.g. 5 sources to pull) → fan-out spawn (one message, N agent calls)
- **Tool scope materially different from main** (e.g. heavy web-fetch budget, repo-wide grep) → spawn to isolate
- **Trivial work** (single grep, single read, single bullet response) → do it inline, don't spawn

Detailed criteria in [`docs/agents.md`](../../docs/agents.md).

## Architect agents (reference — not spawned in daily ops)

These ran during Giovanni bootstrap. They produced the templates, docs, scripts, and operational agent definitions. Frozen unless framework needs structural revision.

| Agent | Owned subsystem | Status |
|---|---|---|
| [`memory-architect`](memory-architect.md) | 4-layer memory system (operational-memory, topic-shards, decisions, briefs, archive, MAP) | done |
| [`governance-architect`](governance-architect.md) | Constitution pattern, INDEX/MAP regen scripts, lint framework, hooks, audit cadence | done |
| [`stakeholder-architect`](stakeholder-architect.md) | Per-stakeholder profile schema, relationship_type enum, sentiment trajectory discipline | done |
| [`prediction-architect`](prediction-architect.md) | Predictive layer (branch-out / shadow / calibration), 8 binding principles, canonical-moves registry | done |
| [`subagent-roster-architect`](subagent-roster-architect.md) | Operational agent definitions (this directory's worker agents) | done |
| [`adversarial-architect`](adversarial-architect.md) | Adversarial review workflow + adversarial-reviewer operational agent + SHIP/REWRITE/KILL verdict enum + default-critical-mode policy | done |
| [`digest-architect`](digest-architect.md) | Daily digest workflow (12 steps), state + sources templates, drift ack flow, briefs auto-gen, predictive integration (shadow gen + lookback) | done |
| [`slash-command-architect`](slash-command-architect.md) | All 8 slash command implementations (/digest, /branch-out, /shadow-review, /calibration-report, /consistency-check, /market-radar, /review, /redline) | done |

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

Bar for adding a new agent: the work is genuinely bounded, parallelizable OR pollution-prone, and reused across enough scenarios to justify the overhead. **If you're tempted to add an agent for a single use case, do the work inline first and revisit after 3 occurrences.**
