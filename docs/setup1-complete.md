# Setup1 — Bootstrap Complete

> Setup1 = building Giovanni itself from a domain-specific source implementation, via 8 specialist architect agents that each owned one layer of the framework. **Status: 8/8 specialists shipped.**

## What Setup1 produced

The current Giovanni repo is the output. It is a **domain-agnostic AI Chief of Staff methodology framework** ready to be forked into Setup2 (your actual operational instance for whatever domain you operate in).

See `README.md` for the layer-by-layer description.

## What this took

| Specialist | What it owns | Output |
|---|---|---|
| 1. memory-architect | 4-layer memory architecture | 7 templates + 4 Lattice examples + README + classification + graduation criteria + hard limits |
| 2. governance-architect | Constitution pattern + INDEX/MAP auto-regen + lint framework + audit cadence | 4 knowledge files + 10 scripts + 6 hooks + 2 governance docs + 6 ship-default lint rules |
| 3. stakeholder-architect | Per-stakeholder profile schema + sentiment trajectory discipline + 6-value relationship-type enum | 2 templates + 3 Lattice examples + stakeholder-profiles.md + slug-exists lint rule |
| 4. prediction-architect | Branch-out + shadow + calibration triangle + 8 binding principles + canonical-moves registry | 4 templates + canonical-moves (55 generic moves) + 3 Lattice examples + 3 lint rules + 3 slash command stubs + prediction.md |
| 5. subagent-roster-architect | 7 generic worker agents + agent design patterns | 7 agent definitions + README + docs/agents.md |
| 6. adversarial-architect | SHIP/REWRITE/KILL adversarial workflow + default-critical policy | 1 agent + 1 workflow + 1 policy doc + 1 Lattice example + 1 lint rule + constitution patch |
| 7. digest-architect | 12-step daily digest workflow + state/sources templates + session-start hook | 1 workflow + 2 templates + 1 hook + 1 policy doc + 1 Lattice example + 1 lint rule + constitution patch |
| 8. slash-command-architect | 8 finalized slash commands wiring templates + workers + workflows | 8 commands + registry + slash-commands.md + 1 lint rule, plus deletion of 3 superseded stubs |

## Build cadence

Single-session hobby build over a few hours. Each architect: write spec → spawn agent → verify output → commit → push → mark done. Average per architect: ~30-60 min.

## What Setup1 did NOT include

1. **End-to-end runtime test.** All templates + agents + workflows are coherent on paper. The first real test is forking Giovanni to a 2nd domain and running actual `/digest` + `/branch-out` against real signal.

2. **Independent cross-validation.** Same general-purpose agent built schemas and filled Lattice examples — confirmation bias risk remains. Real cross-validation requires an independent agent fork to a 3rd domain.

3. **Slash command runtime parser.** Argument syntax is documented per-command; the actual `$ARGUMENTS` parsing is the Claude Code runtime's job. If forks need a shared parser utility, that's a `scripts/` addition for Setup2.

4. **Setup-guide for fork-to-domain.** `docs/setup-guide.md` is not yet written. Setup2 will write this as it learns what's actually needed to fork cleanly.

5. **CI/CD integration.** `scripts/install-hooks.sh` exists for pre-commit; no GitHub Actions or other CI wiring.

## Known accumulated concerns

1. **Volume = maintenance surface.** ~17K lines for hobby project is substantial. Pruning may be appropriate after Setup2 surfaces what's actually used.

2. **Same-agent confirmation bias on every architect.** See above.

3. **Cross-architect TODOs left as documentation, not blockers.** Each architect's report flagged things for other architects to handle. The architects ran sequentially so most TODOs were absorbed in real-time; remainder are documented in respective specs.

4. **Lint rule overlap.** `check-decision-records.sh` (hook) and `decision_trigger_conditions.py` (lint rule) check the same thing. Intentional redundancy (hook catches at commit time, lint catches in CI), but worth flagging.

5. **Constitution template is structure-only.** Forks fill principles + operating posture + commercial model + compliance + active blockers from their domain. The template demonstrates shape, not content.

## Setup2 path (what comes next, when you want it)

When you decide to actually use Giovanni for a domain:

1. **Fork Giovanni into a new private repo** (`<domain>-cos` or similar)
2. **Fill `knowledge/constitution.md`** with your actual operating principles, strategic posture, stakeholder model, architecture, commercial model, compliance posture
3. **Bootstrap stakeholder profiles** — pick 5-10 key people, run `profile-bootstrap` for each (or write manually)
4. **Configure `memory/digest_sources.md`** with your actual sources (Slack workspace, Outlook calendar, project tracker, etc.)
5. **Wire MCP tools** to source-puller — fork-time mapping from generic `source_type` to actual MCP server identifiers
6. **Run `/digest`** for the first time. Iterate sources config based on signal quality.
7. **Run `/branch-out`** on first high-stakes situation
8. **Wait 30 days**, then `/calibration-report` to see initial accuracy patterns
9. **Wait 90 days**, then `/shadow-review` for first quarterly audit

## Cross-architect TODOs (unresolved, low priority)

These were noted in architect reports but not resolved during Setup1. Address if needed during Setup2:

- **memory-architect ↔ subagent-roster-architect:** `researcher` writes to `memory/intel/` — confirm canonical (vs `memory/research/`)
- **governance-architect:** add `stakeholder_dormant_threshold_days` and `stakeholder_archive_threshold_days` to `docs/governance.config.template.yaml`; consider lint rule for agent frontmatter/body consistency
- **slash-command-architect:** `/consistency-review <YYYY-MM-DD>` workflow referenced in `/consistency-check` but not implemented — likely governance domain
- **stakeholder-architect:** `predicted_reactions` schema may want explicit `prediction_index` for shadow-hypothesis traceability
- **digest-architect:** brief retention policy (auto-archive after N days past event?) — currently no retirement mechanism

## What this is and isn't

**This is:** a thoughtfully-distilled methodology framework with structure, governance, predictive layer, and operational machinery. Lint-clean. Domain-leak-clean. Cross-referenced. Documented.

**This isn't:** validated through external adoption. Tested in production for a 2nd domain. Free of confirmation bias. Marketed. Supported.

If you fork it and find friction, the framework is wrong, not you.
