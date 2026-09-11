# Invariants — the contract the repo declares about itself

An invariant is something this repo asserts is always true: a file that must exist, a field that must be filled, a cadence that must not lapse, a channel that must never be written to. They are scattered across `CLAUDE.md`, `docs/governance.md`, the workflows and the hooks. This file is the register that lists them in one place, together with **what enforces each one** — and, just as importantly, which ones nothing enforces.

## Precedence — this file is the contract, code is its implementation

When an implementation and this register disagree, **the implementation is the bug**. Fixing it by editing the register to match the code is how a governance layer quietly becomes a description of whatever the code happens to do.

Changing what an invariant *requires* happens here first, in its own commit, then in code.

Three consequences:

- **An invariant nothing implements is listed as unimplemented**, not assumed covered. Half the value of this file is the honest bottom section.
- **Retired invariants keep their row and a one-line reason.** Identifiers are never reused — a retired id in an old commit message must still resolve to the thing it meant.
- **Waive explicitly or fix.** A knowingly-accepted violation gets a `waived:` note with a reason; silence is not a waiver.

## Identifiers

Invariants are keyed by their **check id** (`l1-size`, `domain-leak`, …), not by a minted number. The check id is already the stable name: it is what `lint.py --check` takes, what the finding prints, and what you grep for. A parallel `INV-nnn` numbering would be a second identifier to keep in sync with the first, and the sync is the part that rots.

Unenforced invariants get an id in the same shape, so promoting one to code is a rename of nothing.

---

## Enforced by lint

`scripts/lint.sh` (bash section — things that need the filesystem or git) and `scripts/lint.py` + `scripts/lint_rules/` (everything else). Run both with `bash scripts/lint.sh`.

| Check id | Invariant | Severity | Where |
|---|---|---|---|
| `index-stale` | `knowledge/INDEX.md` matches what the generator would produce now | high | lint.sh |
| `map-stale` | `memory/MAP.md` matches what the generator would produce now | high | lint.sh |
| `registry-stale` | `deliverables/REGISTRY.md` is fresh against `_registry.yaml` | high | lint.sh |
| `hook-syntax` | every `.claude/hooks/*.sh` parses (`bash -n`) | critical | lint.sh |
| `script-syntax` | every `scripts/*.sh` parses | critical | lint.sh |
| `adversarial-verdict-format` | review output carries a verdict in the declared shape | medium | lint.py |
| `branch-out-no-recommendation` | branch-out artifacts present trade-offs, never a recommended move | high | lint.py |
| `constitution-anchors` | every H2/H3 in the constitution has a stable `{#anchor}` | medium | lint.py |
| `decision-trigger-conditions` | every decision record has non-empty `trigger_conditions` | high | lint.py |
| `deliverables-registry` | every `deliverables/` item has a lifecycle entry | medium | lint.py |
| `digest-state-freshness` | `memory/digest_state.md` is not stale beyond threshold | medium | lint.py |
| `domain-leak` | no prior-domain proper nouns in `memory/`, `knowledge/`, `.claude/` | high | lint.py |
| `hooks-portable-date` | hooks use no single-platform commands | high | lint.py |
| `l1-size` | L1 operational memory within its line budget | high / critical | lint.py |
| `l1-strikethrough-ratio` | strikethrough in L1 below threshold (soft-delete creep) | medium | lint.py |
| `no-percentages-in-predictions` | predictions use tiers, never percentages | high | lint.py |
| `shadow-expired-pending` | no shadow hypothesis sits pending past its horizon | medium | lint.py |
| `slash-command-registry` | commands referenced in docs exist, and vice versa | medium | lint.py |
| `stakeholder-frontmatter` | stakeholder profiles carry the required fields | medium | lint.py |
| `stakeholder-slug-exists` | every referenced stakeholder slug resolves to a profile | medium | lint.py |
| `topic-shard-frontmatter` | topic shards carry the required frontmatter | medium | lint.py |
| `workflow-route-table` | route table ↔ `.claude/workflows` + `.claude/commands`, both directions | medium | lint.py |

## Enforced by hook

Hooks warn or gate in the moment. They are **additive** to lint, never a substitute: a hook only fires if the session is running, and `.claude/settings.json` is a file a user can edit. Lint stays the check of record.

| Hook | Invariant | Kind |
|---|---|---|
| `post-knowledge-edit.sh` | `knowledge/INDEX.md` never drifts from `knowledge/` | regenerates |
| `post-memory-edit.sh` | `memory/MAP.md` never drifts from `memory/` | regenerates |
| `post-constitution-edit-check.sh` | constitution amendments follow the supersede + changelog convention | reminds |
| `session-start-audit-check.sh` | audit cadence, L1 size, strikethrough creep | warns |
| `session-start-digest.sh` | digest cadence, expired drift acks, shadow-review cadence | warns |
| `check-decision-records.sh` | no commit with an empty `trigger_conditions` | blocks |
| `check-unmerged-claude-branches.sh` | no forgotten unmerged `claude/*` branches | warns |
| `block-external-writes.sh` | external writes gated per action; demoted channels denied | gates |

## Enforced by cadence (a human runs it)

| Id | Invariant | Cadence | Trigger |
|---|---|---|---|
| `audit-light` | L1 reconciled against reality (dates, statuses) | 14 d | hook warns |
| `audit-full` | section-by-section L1 review, shard graduation, archival | 35 d | hook warns |
| `shard-retirement` | resolved shards move to `topics/_resolved/` | 60 d | full audit |
| `shadow-review` | shadow hypotheses audited for calibration | 90 d | hook warns |
| `calibration-report` | actor-score calibration written up | monthly | `/calibration-report` |
| `consistency-check` | semantic drift checks the linter cannot reach | weekly | `/consistency-check` |
| `re-grounding` | every FACT promoted to canon or shipped in a deliverable has a primary anchor verified this cycle | at the two gates | constitution amendment · deliverable ship |

---

## Declared but unenforced

These are real rules — stated in `CLAUDE.md` or `docs/governance.md`, binding on the agent — that **no code checks**. Listing them is the point: an unenforced rule is one bad session away from being a former rule, and the register is where that risk is visible instead of implied.

| Id | Invariant | Why unenforced | Path to enforcement |
|---|---|---|---|
| `l1-byte-size` | L1 within a byte budget, not just a line budget | not implemented yet | lint rule alongside `l1-size` — a 200-line file can still be 58 KB |
| `topic-shard-stale` | an active shard must not freeze (refresh or retire) | not implemented yet | lint rule over `last_touch` frontmatter |
| `resolved-shard-status` | `topics/_resolved/` holds only `status: resolved` shards | not implemented yet | lint rule over frontmatter |
| `agent-roster-match` | agents on disk ↔ agents listed in docs, with matching models | not implemented yet | lint rule, same shape as `workflow-route-table` |
| `digest-state-size` | `digest_state.md` is a state file, not a journal | not implemented yet | byte cap in lint |
| `shard-first-write` | updates to a sharded topic go in the shard, not L1 | requires judgement about topic identity | none planned — audit-time review |
| `no-strikethrough-soft-delete` | resolved items are archived in the same commit, not struck through | ratio check catches accumulation, not the individual act | partial: `l1-strikethrough-ratio` |
| `read-doctrine` | synthetic outputs are not inputs; claims carry their original anchor | needs to read meaning, not shape | `consistency-checker` agent, partially |
| `browser-read-only` | UI fallback never types into a composer | the harness cannot distinguish a search box from a composer | none possible — stated in the workflow, held by the agent |
| `subagent-transcript-ban` | never read a subagent's raw transcript | no hook sees the read | none planned |
| `external-write-per-action` | the confirmation names the destination and the action | the gate can force a prompt, not judge the answer | partial: `block-external-writes.sh` |

## Retired

| Id | Retired | Reason |
|---|---|---|
| — | — | Nothing retired yet. When something is, its row stays here forever and its id is never reused. |
