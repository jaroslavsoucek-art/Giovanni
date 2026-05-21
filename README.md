# Giovanni

> Extended hand and second brain.

Generic AI Chief of Staff methodology — memory architecture, daily digest, predictive layer, governance discipline, custom subagents, slash commands, living constitution, per-stakeholder modeling, adversarial-default review.

Distilled from a working domain-specific implementation, then sanitized into a domain-agnostic framework you can fork and fill with your own context.

## Status

**Setup1 framework complete.** 8/8 specialist architects shipped; all framework layers operational. Hobby project — no commercial support, no roadmap promises. Built part-time by extracting the system layer from a real high-stakes program (expansion of an e-commerce platform into 6 EU markets) and stripping out the domain content.

Next stage (Setup2): fork Giovanni into a clean repo, fill with your own domain content, run actual workflows. See [`docs/setup1-complete.md`](docs/setup1-complete.md) for the bootstrap summary and what to do with this.

## What's in scope

| Layer | Files | Purpose |
|---|---|---|
| **4-layer memory architecture** | `memory/templates/`, `memory/examples/`, `memory/README.md` | MAP → operational shortcut → topic shards → deep storage. Graduation criteria, hard limits, audit cadence. |
| **Living constitution** | `knowledge/constitution.template.md`, `knowledge/README.md`, `knowledge/INDEX.template.md` | Single source of truth, commit-traceable, anchor IDs, supersedes-pointer, auto-INDEX. |
| **Per-stakeholder profiles** | `memory/templates/stakeholder.template.md`, 3 Lattice examples, `docs/stakeholder-profiles.md` | Sentiment trajectory time-series, communication style, predicted reactions, 6-value relationship-type enum. |
| **Daily digest workflow** | `.claude/workflows/daily-digest.md`, `memory/digest-{state,sources}.template.md`, `docs/digest.md` | 12-step procedure, parallel source-puller fan-out, drift detection with 7d ack expiry, brief auto-gen ≤48h, predictive integration. |
| **Predictive layer** | `memory/templates/branch-out.template.md`, `shadow-hypothesis.template.md`, `calibration-actor-score.template.md`, `memory/branch-out/canonical-moves.md`, `docs/prediction.md` | Branch-out simulation (3-tier no-percentages, max t+2, hard-stop shallow actors), shadow hypotheses (invisible at generation, quarterly review, adversarial lookback), calibration scoring (per-actor monthly). |
| **Custom subagents** | `.claude/agents/` (8 architects + 8 workers) | 7 operational worker agents + 8 framework architects. Generic, model-tagged, tool-scoped, isolated context. |
| **Slash commands** | `.claude/commands/` (8 commands + registry + design doc) | `/digest`, `/branch-out`, `/shadow-review`, `/calibration-report`, `/consistency-check`, `/market-radar`, `/review`, `/redline`. |
| **Adversarial-review-as-default** | `.claude/agents/adversarial-reviewer.md`, `.claude/workflows/adversarial-review.md`, `docs/adversarial.md` | SHIP/REWRITE/KILL verdict (no compounds), strongest-counter-case requirement, default-critical, suspend conditions documented. |
| **Governance + lint** | `scripts/lint.{sh,py}`, `scripts/lint_rules/` (11 rules), `scripts/build-{knowledge-index,memory-map}.sh`, `.claude/hooks/` (8 hooks), `docs/governance.md` | Pluggable Python lint framework, INDEX/MAP auto-regen, hard-limit enforcement (300-line, 2% strikethrough), audit cadence (14d light / 35d full), classification rules. |

## What's NOT in scope

- **No domain content.** No stakeholders by name (except Lattice synthetic test domain in examples), no real decision logs, no project specifics.
- **No vendor lock-in.** Works with Claude Code today; designed to migrate to platform-native primitives (Anthropic memory tool, Dreaming, Antigravity SDK) as they ship.
- **No commercial support.** MIT license; fork at your own risk.
- **No automatic value.** Giovanni is templates + workers + workflows + governance. Value comes from filling it with your domain context and running it for months.

## Test domain

`docs/test-domain.md` defines a synthetic 2nd domain (Alex Park / Lattice Finance — Series A B2B treasury automation SaaS) used to validate every template + workflow is genuinely generic. Every architect's output is stress-tested against this domain. See `memory/examples/*.example.md` for filled artifacts.

## Stats (post-Setup1)

- 8 architect agents + 8 operational agents = 16 total
- 8 slash commands + 11 lint rules + 8 hooks + 8 generic scripts
- 13 memory templates + 14 Lattice examples
- 1 living constitution template + 1 INDEX template + 1 governance config template
- 10 workflow/policy/design docs
- ~104 files, ~17K lines, 19 commits

## License

MIT.

## Origin

See [`docs/origin.md`](docs/origin.md). Sanitized clean-room extraction from a private domain-specific implementation; no proprietary content carried over.
