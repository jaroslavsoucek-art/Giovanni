# Giovanni Governance — how the discipline layer works

Governance is the half of Giovanni that prevents the memory architecture from decaying into a junk drawer within four weeks. Memory layer alone is just a directory tree. Governance is the rules + automation that keep the layer healthy: classification before append, hard limits with teeth, audit cadence, authority hierarchy, regen scripts, hooks.

This document is the binding reference. The schemas (memory, knowledge) live in their respective `README.md`s. This doc explains how the *system* stays consistent.

---

## Authority hierarchy

When two artifacts disagree, this order wins:

1. **Constitution** (`knowledge/<constitution>.md`) — single source of truth. If memory says "we use per-seat pricing" but the constitution says "platform + per-entity", the constitution wins.
2. **Decision records** (`memory/decisions/`) — audit trail of how the constitution got to its current state. Authoritative for *why*. If the constitution ever drifts from its decision-record back-link, the decision record wins and the constitution gets patched.
3. **Operational memory** (`memory/CLAUDE_MEMORY.md`, `memory/topics/`) — current state, expected to be stale within days. Authoritative for "what am I tracking right now", not for "what's true".
4. **Drafts** (`deliverables/`, working notes) — explicitly non-authoritative. May contradict everything above.

**Test:** if you're about to add a fact to memory that conflicts with the constitution, stop and ask: "is this a transient observation or a change to canon?" If canon, propose a constitution patch first. Then update memory to point at the new constitution section.

---

## Classification rule — where does this belong?

Every piece of content has a target tier. Default is **not** L1. L1 is a restrictive target, not a default landing zone.

| Content type | Goes to | Authority tier |
|---|---|---|
| **Decision** (with reasoning + alternatives + trigger conditions) | `memory/decisions/<YYYY-MM-DD>-<slug>.md` + optional 1-line pointer in L1 | Decision record |
| **Historical artifact** (meeting transcript, threaded comments verbatim, superseded version) | `memory/archive/<YYYY-MM>.md` or `deliverables/` | Archive |
| **Canonical fact** (operating principle, decided architecture) | Constitution patch — `knowledge/<constitution>.md` | Constitution |
| **Operational current state** (what I'm doing now, status of blockers) | L1 (`memory/CLAUDE_MEMORY.md`) — minimum, then graduate to shard | Memory |
| **Per-person notes** | `memory/stakeholders/<slug>.md` | Memory L3 |
| **Per-event prep** | `memory/briefs/<YYYY-MM-DD>_<event>.md` | Memory L3 |
| **Per-topic deep state** | `memory/topics/<slug>.md` (L2 shard) | Memory L2 |
| **Predictive simulation** | `memory/branch-out/` (only if predictive layer in use) | Memory L3 — see `prediction-architect` |
| **External market intel** | `memory/intel/` (only if intel layer in use) | Memory L3 |
| **Audit findings** | `memory/audits/` (only if audit layer in use) | Memory L3 |

### The "remember X" trap

When a user (or you) says "remember X", **classify before appending**. If it's not operational-current-state, it doesn't go in L1. Append to the right L3 file and add a pointer if useful.

Concretely, on encountering "remember X":

1. **Is it a decision?** → New file in `memory/decisions/`, then optional L1 pointer.
2. **Is it a fact about how the domain works?** → Constitution patch proposal, not memory.
3. **Is it a fact about a person?** → `memory/stakeholders/<slug>.md`.
4. **Is it transient (resolves in <30 days)?** → L1, but only if it's a current blocker. Otherwise it goes nowhere — just remember it for the session.

---

## Hard limits + rationale

Limits exist because they have teeth. Soft conventions get ignored. Hard limits with hooks flagging breach get respected.

| Limit | Threshold | Hook / lint behaviour | Why this number |
|---|---|---|---|
| **L1 line count** | 300 (warn), 400 (critical) | `lint.sh --check l1-size` + `session-start-audit-check.sh` warn at warn level, critical means STOP-and-audit | At ~80 tokens/line, 300 ≈ 24k tokens ≈ 12 % of a 200k-token context. Acceptable session-start overhead. Above 400, L1 stops being "cheap session start" and becomes a second knowledge base. |
| **L1 strikethrough ratio** | 2 % (warn), 5 % (critical) | `lint.sh --check l1-strikethrough-ratio` + `session-start-audit-check.sh` warn | Strikethrough is acceptable for ≤1 session as "verify before archive". Persistent strikethrough = soft delete = drift signal. Above 2 % means cleanup overdue. |
| **Decision record `trigger_conditions`** | Must be non-empty | `lint.sh --check decision-trigger-conditions` + `check-decision-records.sh` pre-commit | Decision without trigger conditions is decision theatre. There's no way to know when to revisit. |
| **Topic shard required frontmatter** | 5 fields: `slug`, `status`, `owner`, `last_touch`, `key_stakeholders` | `lint.sh --check topic-shard-frontmatter` | Consistent shape across shards means grep / agent-side scanning is reliable. Always-empty-list ≪ sometimes-missing. |
| **Constitution section anchors** | Every H2/H3 has `{#kebab-case}` | `lint.sh --check constitution-anchors` | Anchors enable inbound pointers from memory and other constitution sections. No anchor = unlinkable = lost. |

### What changes the numbers?

- **Smaller agent context** (e.g. 32k): drop `l1_limit` to ~100 lines. Configure via `governance.config.yaml`.
- **Larger context** (1M+): leave at 300. The point isn't token budget — it's that L1 should remain reviewable in one screen.
- **High-velocity domains** (week-by-week pivots): strikethrough ratio can sit higher, but only if your `audit_light_cadence_days` is also lower (7d). Otherwise drift compounds.

---

## Audit cadence

Two cadences. Both tracked in `memory/audit_state.md` (flat, see "State file placement" below).

### Light prune — every 14 days

Strip strikethroughs, archive resolved items, scan for soft-delete patterns. ~5 minutes, no full re-read. Updates `last_audit_light:` in state file.

### Full audit — every 35 days

Section-by-section L1 review. Archive resolved items. Graduate hot items to shards. Re-classify items that drifted into the wrong tier (e.g. canonical fact accidentally in L1). Updates `last_audit_full:` in state file.

The session-start hook (`session-start-audit-check.sh`) warns when either cadence is overdue.

### Resolved-shard retirement — every 60 days (configurable)

Shards in `memory/topics/` with `status: resolved` and untouched for >60 days move to `memory/topics/_resolved/<slug>.md`. The MAP regenerates with a separate "Resolved" section.

**Configurable per-domain.** See [Resolved shard retirement window](#resolved-shard-retirement-window) below.

---

## Commit prefix conventions

Conventional Commits with Giovanni-specific scopes. Pre-commit lint enforces some of these implicitly (e.g. `decision-trigger-conditions` is checked when `memory/decisions/` is staged regardless of prefix; the prefix just helps reviewers).

| Prefix | When to use | Example |
|---|---|---|
| `feat:` | New capability (new agent, new hook, new template) | `feat(memory): graduate <slug> to topic shard` |
| `fix:` | Bug fix in a script / hook / template | `fix(scripts): build-memory-map crashed on missing frontmatter` |
| `docs:` | Documentation-only change | `docs(memory): clarify retirement window` |
| `docs(constitution):` | Constitution amendment | `docs(constitution): <slug> — supersede §<old>` |
| `docs(memory):` | Memory layer update other than a decision | `docs(memory): add Q3 watch items` |
| `decision:` | New decision recorded in `memory/decisions/` (often paired with constitution patch) | `decision: <slug> — switch to platform pricing` |
| `chore:` | Maintenance, non-functional | `chore: regen INDEX after rename` |
| `chore(archive):` | Move content from L1/L2 into `archive/` | `chore(archive): retire <slug> shard to _resolved/` |
| `refactor:` | Code/template restructure with no behaviour change | `refactor(scripts): split lint rules into plugins` |

**Hard rule:** every constitution amendment uses `docs(constitution):` or `decision:`. The `post-constitution-edit-check.sh` hook reminds the agent. The pre-commit lint can be configured to enforce, but defaults to advisory (false positives on legitimate non-constitution edits to the file are too easy).

---

## State file placement (resolved memory-architect open question #1)

**Decision: flat at `memory/<name>_state.md`.**

Memory-architect raised the question whether state files should be flat (`memory/audit_state.md`) or nested (`memory/state/audit.md`). Verdict: flat.

**Rationale:**

1. **Grep simplicity.** State files are rare — typically `audit_state.md`, `digest_state.md`, maybe `watch_state.md`. Three to five files in the memory root. Adding a `memory/state/` subdirectory creates more typing for no gain.
2. **Visibility.** When you `ls memory/`, you see state files inline with the action artifacts. They're not separated like infrastructure.
3. **No collision risk.** State file names are agent-controlled, not user-controlled. We can guarantee no name collisions.
4. **Reverse case is forced.** If the fork has >5 state files, that's a smell — most should be in `audits/` or `intel/`.

If your fork ever exceeds 5 state files, revisit and consolidate. Don't preemptively nest.

---

## MAP regeneration on archive/ writes (resolved memory-architect open question #2)

**Decision: yes, archive/ writes DO fire MAP regen.**

The performance argument (regen is fast, ~100-200ms) outweighs the alternative (archive lands but MAP doesn't reflect it until next non-archive memory edit, leading to confusing stale MAP for an unbounded period).

The post-memory-edit hook (`.claude/hooks/post-memory-edit.sh`) explicitly includes `memory/archive/*` in its trigger paths.

**If regen becomes slow** (>1s on a large repo): the regen script's `find` operations are the hot path. Profile, optimize, but don't drop the archive trigger.

---

## Resolved shard retirement window (resolved memory-architect open question #3)

**Decision: configurable per-domain via `governance.config.yaml`, default 60 days.**

The default value (60 days) is the source-implementation observation: shards that stay `status: resolved` untouched for ~2 months are no longer being referenced even occasionally. The exact number is calibrated to the source's working cadence.

For other domains, the right value depends on the principal's working cycle:

- **High-velocity domains** (week-by-week pivots, fast-moving startup, sales lifecycle): 30 days. Resolved-but-recent shards stop being relevant fast.
- **Quarterly domains** (board cycles, fundraising, treasury): 90 days. A shard "resolved" in March may legitimately get re-opened in June board prep.
- **Annual-cycle domains** (compliance, audit, year-end planning): 120-180 days.

For Lattice Finance (test domain): **90 days** is the right default. Quarterly board cadence + ~Q3 board prep referencing Q1-resolved items + the SOC 2 / fundraise prep with quarter-spanning effects. Set in `docs/governance.config.yaml`:

```yaml
resolved_shard_retirement_days: 90
```

**Why configurable, not derived:** Giovanni doesn't introspect business cadence. The fork-er knows their own cycle better than any heuristic.

**Override mechanism:** environment variable `GIOVANNI_RESOLVED_SHARD_RETIREMENT_DAYS` overrides config file. Useful for one-off audits ("what would 30d retirement give me?") without committing the change.

---

## What the hooks do (in plain English)

| Hook | Fires when | What it does |
|---|---|---|
| `.claude/hooks/post-knowledge-edit.sh` | After Edit/Write to `knowledge/<anything>.md` (except INDEX.md) | Regenerates `knowledge/INDEX.md` via `scripts/build-knowledge-index.sh`. Inline echo confirms refresh. |
| `.claude/hooks/post-memory-edit.sh` | After Edit/Write to `memory/{topics,decisions,briefs,stakeholders,archive}/*` (except MAP.md) | Regenerates `memory/MAP.md` via `scripts/build-memory-map.sh`. Inline echo confirms refresh. |
| `.claude/hooks/post-constitution-edit-check.sh` | After Edit/Write to `knowledge/<constitution>.md` | Surfaces amendment checklist: supersedes-pointer convention, commit prefix expectation, decision-record back-link reminder. Detects unattached "SUPERSEDED" headers. |
| `.claude/hooks/session-start-audit-check.sh` | At Claude Code session start | Warns if cadence overdue, L1 over size, strikethrough creep. Silent if state file missing (fresh fork). |
| `.claude/hooks/check-decision-records.sh` | Pre-tool-use of `git commit` (configure in `.claude/settings.json`) | Blocks commit if any staged `memory/decisions/*.md` has empty `trigger_conditions`. Override: `GIOVANNI_SKIP_DECISION_CHECK=1`. |
| `.claude/hooks/check-unmerged-claude-branches.sh` | Session start / stop | Warns if `claude/*` branches exist that aren't merged to `main`. Threshold configurable via `GIOVANNI_BRANCH_WARN_THRESHOLD` (default 1). |

**Trigger configuration** lives in `.claude/settings.json` (or `.claude/settings.local.json`). Giovanni doesn't provide a default `settings.json` because the fork chooses which hooks to enable. See `scripts/install-hooks.sh` for the chmod step + git pre-commit install — the Claude Code hook *trigger* is wired separately in `settings.json`.

---

## Lint framework

Two-layer lint (`scripts/lint.sh` + `scripts/lint.py` + `scripts/lint_rules/`):

- **Bash side** (`scripts/lint.sh`): INDEX/MAP staleness checks (cheap diff against `--dry` output) + `bash -n` syntax checks for hooks + scripts.
- **Python side** (`scripts/lint.py`): pluggable rules in `scripts/lint_rules/*.py`. One rule per file. Each rule exposes `CHECK_ID` constant + `run(ctx)` function.

### Built-in rules

| Rule | Severity | What it checks |
|---|---|---|
| `index-stale` | critical | `knowledge/INDEX.md` matches `build-knowledge-index.sh --dry` |
| `map-stale` | critical | `memory/MAP.md` matches `build-memory-map.sh --dry` |
| `hook-syntax` | critical | All `.claude/hooks/*.sh` pass `bash -n` |
| `script-syntax` | critical | All `scripts/*.sh` pass `bash -n` |
| `l1-size` | high / critical | L1 line count vs warn/critical thresholds |
| `l1-strikethrough-ratio` | medium / critical | Strikethrough ratio vs threshold |
| `decision-trigger-conditions` | critical | Decision records have non-empty trigger conditions |
| `topic-shard-frontmatter` | medium | Required fields present |
| `constitution-anchors` | medium | Every H2/H3 has `{#anchor-id}` |
| `domain-leak` | high | Configurable denylist matches caught (fork-time activity) |

### Adding a rule

Create `scripts/lint_rules/<rule_name>.py`:

```python
"""One-line description."""

CHECK_ID = "kebab-case-id"

def run(ctx):
    # ctx.repo, ctx.config, ctx.memory_dir(), etc.
    # Emit findings via ctx.add(severity, CHECK_ID, message)
    pass
```

See `scripts/lint_rules/README.md` for the helper API.

### Running

```bash
bash scripts/lint.sh                       # all checks
bash scripts/lint.sh --list                # list check ids
bash scripts/lint.sh --check l1-size       # one check
```

### Pre-commit integration

`scripts/install-hooks.sh` installs `.git/hooks/pre-commit` that runs `scripts/lint.sh`. Override: `GIOVANNI_SKIP_LINT=1 git commit ...`.

---

## Anti-patterns (CO NIKDY)

**Never:**

1. **Edit `knowledge/INDEX.md` or `memory/MAP.md` by hand.** They are auto-generated. Hand-edits get overwritten on the next regen. Want to change format? Edit the regen script.

2. **Delete superseded constitution sections.** Always preserve the old section as a `(SUPERSEDED → §<new-anchor>)` stub with a pointer. Future readers need the trail.

3. **Use strikethrough as soft-delete in L1.** Persistent strikethrough = drift signal. Archive in same commit or unstrike.

4. **Combine memory updates and architectural changes in one commit.** Conventional commits + one logical decision per commit. A decision-record commit doesn't bundle in a memory shard graduation.

5. **Add a knowledge doc without re-running the INDEX regen.** The hook should fire automatically, but if you edit via a non-hook-aware tool, manually run `bash scripts/build-knowledge-index.sh`.

6. **Bypass the pre-commit lint without an override flag.** If lint fails, fix the finding. If the finding is wrong, fix the rule. `--no-verify` should be the exception, not the habit.

7. **Add a section without anchor ID.** No anchor = unlinkable.

8. **Skip the classification step** when adding content to memory. Memory authoring rules are binding for a reason — they prevent the four-week decay pattern.

---

## How to fork governance for a new domain

1. **Copy** `docs/governance.config.template.yaml` to `docs/governance.config.yaml`.
2. **Edit** the values for your domain:
   - `constitution_file`: rename if your domain uses a different name (e.g. `lattice_principles.md`)
   - `l1_limit`: match your context-window economics
   - `resolved_shard_retirement_days`: match your business cadence
   - `domain_leak_denylist`: populate with proper nouns from the prior domain (company / project codenames, stakeholder full names, region codes, partner brands)
3. **Run** `bash scripts/install-hooks.sh` to chmod hooks + install pre-commit.
4. **Wire** Claude Code hooks in `.claude/settings.json` (PostToolUse / SessionStart / PreToolUse mappings → the `.claude/hooks/*.sh` files).
5. **Generate** initial INDEX + MAP:
   ```bash
   bash scripts/build-knowledge-index.sh
   bash scripts/build-memory-map.sh
   ```
6. **Verify** lint clean:
   ```bash
   bash scripts/lint.sh
   ```
7. **Fill** the constitution from `knowledge/constitution.template.md`.

---

## Cross-architect coordination

- **Memory templates + L1/L2/L3 schema** → `memory-architect` (already done).
- **Stakeholder profile schema** → `stakeholder-architect`. Governance enforces file placement (`memory/stakeholders/<slug>.md`) but not the field schema.
- **Predictive layer file types** (branch-out / shadow / calibration) → `prediction-architect`. Governance lint enforces placement only.
- **Daily digest mechanics** → `digest-architect`. Governance provides `digest_state.md` placement convention; content schema belongs to digest-architect.
- **Adversarial review workflow** → `adversarial-architect`.

When forking Giovanni for a new domain, memory + governance + at least `stakeholder-architect` should be deployed together. Without all three, the memory layer is incomplete (no profile schema), the canonical layer has no audit cadence, and the discipline fails.
