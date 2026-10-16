# Architect agents (framework-build scaffolding)

The agents in this directory built Giovanni. They ran during bootstrap to produce the templates, docs, scripts and operational agent definitions, and they run again only when the framework itself needs a structural revision — a port from the source implementation, a new layer. **They are not part of the product.** The operational agents a fork actually spawns live in [`plugin/agents/`](../../plugin/docs/agent-roster.md) and ship with the plugin as `giovanni:<name>`.

Each architect reads the live source implementation (`bash scripts/source-path.sh`) read-only and writes sanitised generic artifacts into `plugin/`. The no-leak rule in the root `CLAUDE.md` applies to every one of them.

| Agent | Owned subsystem | Status |
|---|---|---|
| [`memory-architect`](memory-architect.md) | 4-layer memory system (operational-memory, topic-shards, decisions, briefs, archive, MAP) | done |
| [`governance-architect`](governance-architect.md) | Constitution pattern, INDEX/MAP regen scripts, lint framework, hooks, audit cadence | done |
| [`stakeholder-architect`](stakeholder-architect.md) | Per-stakeholder profile schema, relationship_type enum, sentiment trajectory discipline | done |
| [`prediction-architect`](prediction-architect.md) | Predictive layer (branch-out / shadow / calibration), 8 binding principles, canonical-moves registry | done |
| [`subagent-roster-architect`](subagent-roster-architect.md) | Operational agent definitions (`plugin/agents/`) | done |
| [`adversarial-architect`](adversarial-architect.md) | Adversarial review procedure + adversarial-reviewer operational agent + SHIP/REWRITE/KILL verdict enum + default-critical-mode policy | done |
| [`digest-architect`](digest-architect.md) | Daily digest procedure (12 steps), state + sources templates, drift ack flow, briefs auto-gen, predictive integration (shadow gen + lookback) | done |
| [`slash-command-architect`](slash-command-architect.md) | The bootstrap slash command implementations, now `plugin/skills/*/SKILL.md` — `/consistency-review` and `/pulse` were added post-bootstrap | done |

Frontmatter convention and the bar for adding an agent are the same as for the operational roster — see [`plugin/docs/agent-roster.md`](../../plugin/docs/agent-roster.md).
