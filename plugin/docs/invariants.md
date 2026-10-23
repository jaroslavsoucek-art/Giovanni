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
| `hook-syntax` | every `hooks/*.sh` parses (`bash -n`) | critical | lint.sh |
| `script-syntax` | every `scripts/*.sh` and `scripts/git-hooks/*` parses | critical | lint.sh |
| `adversarial-verdict-format` | review output carries a verdict in the declared shape | medium | lint.py |
| `branch-out-no-recommendation` | branch-out artifacts present trade-offs, never a recommended move | high | lint.py |
| `constitution-anchors` | every H2/H3 in the constitution has a stable `{#anchor}` | medium | lint.py |
| `decision-trigger-conditions` | every decision record has non-empty `trigger_conditions` | high | lint.py |
| `deliverables-registry` | every `deliverables/` item has a lifecycle entry | medium | lint.py |
| `digest-state-freshness` | `memory/digest_state.md` is not stale beyond threshold | medium | lint.py |
| `domain-leak` | no prior-domain proper nouns in the project's `memory/`, `knowledge/`, `.claude/` | high | lint.py |
| `hooks-portable-date` | hooks use no single-platform commands | high | lint.py |
| `l1-size` | L1 operational memory within its line budget | high / critical | lint.py |
| `l1-strikethrough-ratio` | strikethrough in L1 below threshold (soft-delete creep) | medium | lint.py |
| `no-percentages-in-predictions` | predictions use tiers, never percentages | high | lint.py |
| `shadow-expired-pending` | no shadow hypothesis sits pending past its horizon | medium | lint.py |
| `slash-command-registry` | commands referenced in docs exist, and vice versa | medium | lint.py |
| `stakeholder-frontmatter` | stakeholder profiles carry the required fields | medium | lint.py |
| `stakeholder-slug-exists` | every referenced stakeholder slug resolves to a profile | medium | lint.py |
| `topic-shard-frontmatter` | topic shards carry the required frontmatter | medium | lint.py |
| `workflow-route-table` | route table ↔ `skills/*/procedure.md` + `skills/`, both directions | medium | lint.py |
| `l1-byte-size` | L1 within its byte budget (the cap line count is blind to) | high | lint.py |
| `digest-state-size` | `digest_state.md` is a state file, not a journal | medium | lint.py |
| `topic-shard-stale` | an active shard must not freeze — refresh or retire | medium | lint.py |
| `resolved-shard-status` | `_resolved/` holds only resolved shards; resolved shards get filed | medium | lint.py |
| `agent-roster-match` | agent files ↔ roster rows ↔ declared model | medium | lint.py |
| `mcp-uuid-pin` | no install-specific MCP server ids in the plugin's agents / skills / hooks or the project's `.claude/` | high | lint.py |
| `silence-counter-verified` | a "N days of silence" claim in L1 / an active shard carries a fresh `[verified YYYY-MM-DD]` stamp, or is written as a past fact without a counter | high / medium | lint.py |
| `rules-register-pointers` | every `docs/invariants.md#<id>` pointer in `CLAUDE.md` / `templates/CLAUDE.template.md` resolves to a Behavioral rules entry | medium | lint.py |
| `inbox-health` | the inbox file is valid (required fields, dates, no closed items, unique keys) and holds ≤ `inbox.max_open` open items | medium / high | lint.py |

## Enforced by hook

Hooks warn or gate in the moment. They are **additive** to lint, never a substitute: a hook only fires if the session is running and the plugin is enabled, and a plugin is something a user can disable. Lint stays the check of record.

| Hook | Invariant | Kind |
|---|---|---|
| `post-knowledge-edit.sh` | `knowledge/INDEX.md` never drifts from `knowledge/` | regenerates |
| `post-memory-edit.sh` | `memory/MAP.md` never drifts from `memory/` | regenerates |
| `post-constitution-edit-check.sh` | constitution amendments follow the supersede + changelog convention | reminds |
| `session-start-audit-check.sh` | audit cadence, L1 size, strikethrough creep, consistency-check cadence + pending triage | warns |
| `session-start-digest.sh` | digest cadence, expired drift acks, shadow-review cadence | warns |
| `check-decision-records.sh` | no commit with an empty `trigger_conditions` | blocks |
| `check-unmerged-claude-branches.sh` | no forgotten unmerged `claude/*` branches | warns |
| `block-external-writes.sh` | external writes gated per action; demoted channels denied | gates |
| `stop-ephemeral-commit-guard.sh` | no unsaved work at the end of an ephemeral session | warns |
| `pre-edit-confirm.sh` | `autonomy.confirm_paths` are edited only with the principal's OK (ask), never in a headless run (deny) | gates |
| `stop-autocommit.sh` | `autonomy.auto_commit_paths` are committed at every Stop through the git pre-commit gate; confirm paths never — they become inbox items | commits |
| `session-start-inbox.sh` | the inbox is refreshed (refreshers, lint→inbox, scheduler health, expiry) and shown first | shows |
| `stop-session-record.sh` | the session's generalised shape (no prompt text) is recorded for the learning loop | records |
| `prompt-correction.sh` | a correction is classified (skill-fix / rule / one-off) and logged before work continues | reminds |

## Enforced by cadence (a human runs it)

| Id | Invariant | Cadence | Trigger |
|---|---|---|---|
| `audit-light` | L1 reconciled against reality (dates, statuses) | 14 d | hook warns |
| `audit-full` | section-by-section L1 review, shard graduation, archival | 35 d | hook warns |
| `shard-retirement` | resolved shards move to `topics/_resolved/` | 60 d | full audit |
| `shadow-review` | shadow hypotheses audited for calibration | 90 d | hook warns |
| `calibration-report` | actor-score calibration written up | monthly | `/giovanni:calibration-report` |
| `consistency-check` | 8 semantic drift checks the linter cannot reach, incl. knowledge↔knowledge and outbound published pages | weekly | `/giovanni:consistency-check` |
| `re-grounding` | every FACT promoted to canon or shipped in a deliverable has a primary anchor verified this cycle | at the two gates | constitution amendment · deliverable ship |

---

## Declared but unenforced

These are real rules — stated in `CLAUDE.md` or `docs/governance.md`, binding on the agent — that **no code checks**. Listing them is the point: an unenforced rule is one bad session away from being a former rule, and the register is where that risk is visible instead of implied.

| Id | Invariant | Why unenforced | Path to enforcement |
|---|---|---|---|
| `shard-first-write` | updates to a sharded topic go in the shard, not L1 | requires judgement about topic identity | none planned — audit-time review |
| `no-strikethrough-soft-delete` | resolved items are archived in the same commit, not struck through | ratio check catches accumulation, not the individual act | partial: `l1-strikethrough-ratio` |
| `read-doctrine` | synthetic outputs are not inputs; claims carry their original anchor | needs to read meaning, not shape | `consistency-checker` agent, partially |
| `browser-read-only` | UI fallback never types into a composer | the harness cannot distinguish a search box from a composer | none possible — stated in the workflow, held by the agent |
| `subagent-transcript-ban` | never read a subagent's raw transcript | no hook sees the read | none planned |
| `external-write-per-action` | the confirmation names the destination and the action | the gate can force a prompt, not judge the answer | partial: `block-external-writes.sh` |
| `thread-supersession` | a cited thread message comes with the thread's last message and a supersedes verdict | needs to read meaning | partial: puller contract emits `→ tail:` on every thread bullet |
| `asymmetric-test` | ranked output is checked for corrections that only ever raise urgency | judgement about direction of a correction | partial: digest renders `⚠ asymmetry: N↑ / 0↓` |

---

## Behavioral rules — why each one-line rule exists {#behavioral-rules}

`CLAUDE.md` is loaded into every turn, so every byte in it is paid for again on every message. The reason behind a rule is read only when somebody questions the rule. So the two live apart. `CLAUDE.md` holds the rule, one line, with a pointer here. This section holds why the rule exists, what happened when it did not, and what enforces it.

Rules whose full reasoning already lives in another doc (`docs/governance.md` for the write gate, role boundaries and classification) point there directly and are not duplicated here. Lint-enforced rules keep their story in the rule's docstring.

### `rules-register`

- **Rule:** each rule in `CLAUDE.md` is one line plus a pointer. A new rule is one line there and one entry here, in the same commit. `CLAUDE.md` stays under ~200 lines.
- **Why:** in the source implementation the operating file had grown to 402 lines and 41 KB, most of it incident narrative appended after each failure. Moving the narrative into a register cut it to 155 lines and 22 KB, and no rule was dropped. The opposite failure is a rule with no reason attached: the first person who finds it inconvenient relaxes it. The register keeps the reason without making every turn pay for it.
- **Enforced by:** lint `rules-register-pointers` (no dangling pointer). File size: audit cadence.

### `thread-supersession`

- **Rule:** citing message N of a thread? Name the thread's last message too (author + time) and say whether it supersedes N. The newest relevant statement wins.
- **Why:** in the source, a position was cited as current a week after its own author had retracted it in the same thread. Both messages were in one tool result, and the later one had been quoted correctly twenty minutes earlier. Memory was not the failure, because the whole thread was in context. It was motivated retrieval: the item was already ranked high, the thread was searched for support for the rank rather than for its current state, and reading stopped at the most useful sentence.
- **Enforced by:** puller contract (`→ tail: <author> <ts>` on every thread bullet, `agents/source-puller.md`) and digest Step 5. No lint: it needs to read meaning.

### `asymmetric-test`

- **Rule:** before any ranked output, check whether any correction this cycle lowered an item's stakes. If every correction raised urgency, say so.
- **Why:** both errors from the same morning in the source (a rotted silence counter, see `silence-counter-verified`, and the retracted position above) raised urgency. Neither lowered it. Random retrieval noise points both ways. A system whose job is ranking priorities pulls toward overstating stakes, because stakes are what justify a rank.
- **Enforced by:** digest Step 10.6 renders `⚠ asymmetry: <N>↑ / 0↓`. The same flag three runs in a row means the bias belongs to the render step and needs a structural fix, not another reminder.

### `subagent-transcript-ban`

- **Rule:** never read a subagent's raw transcript. Consume its result from the final notification only.
- **Why:** a task's output file is not a log. It is the full raw transcript, and reading it pours every raw tool result back into the main thread. That destroys the one reason the agent ran in isolation.
- **Enforced by:** nothing. No hook sees the read.

### `agent-lane-discipline`

- **Rule:** while an agent runs, work a different lane. Do not redo its source on the main thread. An agent that keeps overrunning gets a cap in its own definition.
- **Why:** redoing the source gives two versions of one fact and throws away the isolation. A main-thread workaround for a slow agent hides the problem the cap would fix, and it comes back next run.
- **Enforced by:** nothing.

### `shared-backend-serialise`

- **Rule:** parallelise across backends, serialise within one. Verify that a response answers the request before trusting it.
- **Why:** concurrent agents on one connector gateway cross-wired their responses. One received another product's data for its own query, and nothing in the payload said "wrong". The full story is in `skills/digest/procedure.md` § 4d.
- **Enforced by:** puller hard rule (verify the response answers the request).

### `branch-landing`

- **Rule:** if the fork adopts branches, it adopts the step that lands them too.
- **Why:** an apparatus can lint, commit and push into a branch for days while the main branch stays frozen, and every workflow will report success.
- **Enforced by:** hook `check-unmerged-claude-branches.sh` (warns).

## Retired

| Id | Retired | Reason |
|---|---|---|
| — | — | Nothing retired yet. When something is, its row stays here forever and its id is never reused. |
