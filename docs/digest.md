# Daily Digest — policy + rationale

The daily digest is the **operational tempo** of Giovanni. Each run pulls from configured sources, detects drift between memory and reality, generates briefs for upcoming high-prep events, and feeds the predictive layer with shadow lookback + new shadow hypotheses. Without the digest, the rest of the framework is a static archive.

This document is the **policy + rationale** for the digest. The 12-step procedure lives in [`.claude/workflows/daily-digest.md`](../.claude/workflows/daily-digest.md). The state file template is at [`memory/digest-state.template.md`](../memory/digest-state.template.md). The sources config template is at [`memory/digest-sources.template.md`](../memory/digest-sources.template.md).

---

## Why daily cadence

The cadence is daily because the **drift surface** is daily — chats, emails, calendar moves, project tracker updates, commits to canonical artifacts. A weekly digest catches stale drift at the cost of letting wrong canonical state stand for up to seven days.

The cost of catching drift late compounds. A chat decision the principal made on Tuesday but never recorded in memory becomes ambient knowledge by Friday — the team behaves as if the decision exists, but it's not auditable, not in the constitution, not in a topic shard. By the time the weekly digest catches it, the documentation gap has metastasized into a culture problem ("we don't write things down").

Daily cadence is calibrated for **one-principal contexts** where the principal is the sole writer of canonical state. Multi-principal contexts may need different mechanics (concurrent edits, conflict resolution) that this framework does not address.

### Cadence override for low-velocity domains

Some domains run on annual cycles — board governance, compliance audits, year-end planning. A daily digest there produces 6 days/week of "nothing happened" + 1 day/week of "the quarterly governance event". The signal-to-noise inverts.

For these domains:

- Configure **weekly cadence** in the slash command runtime (frequency override).
- Tighten the **brief eligibility** criteria to "board-tier events only".
- Extend the **drift detection** window (a knowledge edit one week ago is still recent in a quarterly cycle).

Don't run a daily digest on a quarterly domain — the noise floor destroys trust in the signal that does come through.

---

## Source configuration discipline

**Quality over quantity. 3-5 well-targeted sources beat 10 noisy ones.**

When tuning `memory/digest_sources.md`, the failure mode is **over-inclusion**: adding sources "in case we miss something". Each added source costs:

- Pull latency (parallel mitigates this, but agent fan-out has limits)
- Synthesis cognitive load (more bullets → more clustering work)
- False-positive drift candidates (more inputs → more candidate contradictions, most spurious)
- Brief auto-gen noise (more calendar events → more briefs to skip past)

Tighter source config produces higher-signal digests. When in doubt: omit. A source can always be added later via decision record — that's a feature, not friction.

### Source priority semantics

The `priority` field on each source is a **synthesis hint**, not a strict ordering:

- `priority: high` — always include in render even if volume is low (e.g. DMs to the principal: low volume, high signal)
- `priority: medium` — include if volume warrants
- `priority: low` — include as cluster bullets if relevant, otherwise summarize

Priority is NOT a triage signal for branch-out / shadow eligibility — that's Step 6 (triage classification) which uses different criteria.

### What counts as a "well-targeted" source

A well-targeted source has:

1. **Known signal density** — the principal can name the type of signal that appears here. "Slack #strategy" is targeted; "all of Slack" is not.
2. **Bounded volume** — the source produces ≤50 items per digest window. Above that, narrow the identifier.
3. **Operational relevance** — items here affect a current blocker, a topic shard, or a stakeholder profile.

If a source fails any of those tests, it's noise. Tighten or remove.

---

## Drift detection vs noise

The most common digest-tuning challenge is distinguishing **drift** from **new context**.

**Drift = canonical claim contradicted by reality.** Worth surfacing for the principal to resolve.

**New context = additional information that does not contradict canonical state.** Just goes into the relevant render section, no drift flag.

### Examples

| Signal | Drift? | Why |
|---|---|---|
| Chat: "We decided to push the launch to Q3." Constitution says Q2 launch. | YES | Direct contradiction. Flag #1: confirm or document. |
| Chat: "Sarah seemed less enthusiastic in today's 1:1." Profile says `status: active`, sentiment `supportive`. | YES (sentiment shift) | Sentiment trajectory needs an entry; possibly a profile depth re-read. |
| Email: New competitor X funding round announcement. | NO | New context. Goes into watch list, no canonical contradiction. |
| Calendar: Board meeting moved from Tuesday to Thursday. Topic shard last_touch says Tuesday. | YES (mechanical) | Update topic shard's calendar reference. Low-stakes drift but should be patched. |
| Project tracker: Task "X" moved from "In progress" to "Done". | NO (if X is downstream of canonical state) | Just a status update. Renders as task delta, no drift. |

### The "interesting middle"

Some signals are ambiguous — they could be drift or just elaboration. Default posture: **flag and let the principal choose**. The principal's `confirm | ignore Nd | patch` flow exists precisely for these cases. Over-flagging is recoverable (the principal acks); under-flagging is not (canonical state stays wrong).

### Drift definitions per fork

The fork's `memory/digest_sources.md` defines fork-specific drift patterns. The default set:

- (a) Source claim contradicts canonical claim
- (b) Untracked knowledge / constitution edit since last_run (no CHANGELOG entry)
- (c) Profile sentiment shift not yet recorded
- (d) Cross-file inconsistency inside canonical artifacts
- (e) Calendar / scheduling reality contradicts topic shard state

Fork-specific additions are encouraged. The detection runs over named patterns, not arbitrary semantic comparison — the pattern list is the discipline.

---

## Ack flow — principal options

When a drift gets flagged, the principal has three options. Each maps to a state change in `memory/digest_state.md`.

### `confirm`

Principal agrees the drift is real. The digest workflow:

1. Proposes a specific patch (file + line + diff).
2. Waits for the principal's `commit` or refined patch.
3. On `commit`: applies the edit, stages, commits with appropriate prefix (`decision:` or `docs(<canonical>):`), checks whether `CHANGELOG.md` needs an entry.

The commit happens **manually** (the digest workflow proposes; the principal executes). No auto-commits — see § Anti-patterns.

### `ignore Nd`

Principal acknowledges the drift but chooses not to resolve it now. The digest workflow:

1. Appends to `memory/digest_state.md` § Active acks:
   ```
   - [ack YYYY-MM-DD expires YYYY-MM-DD+Nd] <drift summary> | source: digest YYYY-MM-DD #N
   ```
2. Default expiry: 7 days. Principal can specify a different N.
3. Next digest respects the ack — doesn't re-flag the same drift.

After expiry, if the underlying drift still applies, it's re-flagged in the next digest. The principal can ack again, patch, or accept the recurring noise (signal that documentation gap should be patched eventually).

### `patch <text>`

Principal supplies the patch directly. Often used when the principal already knows what the canonical state should be and doesn't want the workflow to propose.

Behaves like `confirm` from step 3 onwards.

### "Permanent" ack — last resort

`expires = 9999-12-31` makes an ack effectively permanent. Use sparingly. Almost always a signal that the **documentation should be patched** to remove the recurring drift — the ack is a workaround for a missing canonical statement.

Example pattern: an automated tool regenerates a navigation file but never gets recorded in CHANGELOG. Permanent ack > documentation patch IF the principal genuinely doesn't want that file class in changelog scope. The ack itself becomes the canonical record of "this class of file is exempt".

### Verbal ack (outside drift flow)

When the principal verbally says "X changed" in chat, the workflow auto-acks for 7 days. This catches the common case where the principal knows about a drift before the digest does and wants to pre-empt the flag.

---

## Brief auto-gen — scope discipline

Briefs are **high-value but bounded**. The digest generates briefs for **high-prep events**, not every calendar entry.

### Default eligibility

Generate a brief for events in the next 48 h that match:

- 1:1 with a stakeholder whose profile has `profile_depth: partial` or deeper
- Decision meeting (board, governance, vote)
- External commercial conversation (customer renewal, vendor negotiation, partnership)
- Board / exec event
- Negotiation / counterparty conversation flagged in an active topic shard

### Default exclusions

Skip:

- Internal stand-ups, daily syncs, recurring blocks ("Place", "Focus time", "Lunch")
- 1:1 entries without a named counterparty
- Mechanical scheduling (interview screening prep, coffee chats with no decision content)
- Events where the principal is host of an open invite (different prep dynamic)

### Eligibility override per fork

The fork's `memory/digest_sources.md` `calendar.brief_eligibility` block can add or remove categories. Common adjustments:

- Add: industry events where the principal speaks
- Remove: recurring 1:1s with a deep-profile stakeholder that don't need new prep each time

### Brief refresh, not recreate

If a brief file already exists for an event, the digest **refreshes** rather than recreates:

- Preserve any manual annotations.
- Append new signal to "Counterparty state" rather than overwriting.
- Update talking points only if a material new signal arrived since last generation.

This protects the principal's edits from being clobbered by automation.

### Why conservative scope

A brief takes ~10-20 minutes to write well (even for the agent). A digest that generates 8 briefs every morning eats the principal's review time and degrades the quality bar — they start skimming and miss the high-signal one in the noise.

Tight eligibility = each brief gets the principal's full attention = the brief actually changes meeting outcomes.

---

## Shadow generation discipline

The digest is **not** the primary place to generate shadow hypotheses. The primary place is `/branch-out` (active simulation surfaces multiple hypotheses per simulation). The digest's role is:

1. **Catch passive signals** that don't warrant active simulation but have predictable follow-ups
2. **Feed shadow lookback** at horizon dates (Step 8 = resolve, Step 11 = generate new)
3. **Maintain the shadow pending pool** between branch-out runs

### Specificity gate, not coverage

Shadow generation is gated by `memory/triage-heuristic.yaml` `specificity_gate`:

- Prediction must be one sentence, specific
- `expected_signal.search_terms` ≥ 2 keywords
- `expected_signal.source_channels` ≥ 1

**Fewer-but-testable beats many-but-vague.** A vague shadow hypothesis is calibration noise — it resolves ambiguously either way and corrupts the per-actor accuracy score. The gate refuses to generate vague hypotheses; rejected counts feed monthly calibration tracking as a discipline-health metric.

### Volume caps

- Soft cap: 15/day (`shadow_only.daily_max`). Above this, calibration becomes noisy.
- Hard fail: 25/day (`shadow_only.hard_fail_max`). If exceeded, the digest **aborts shadow generation** and flags `⚠ Shadow volume hard-fail` for triage heuristic review.

Hard fail is NOT silent threshold creep. It signals that the digest's triage is too generous AND should be tightened.

### Invisibility is binding

Shadow hypotheses are **invisible** to the principal at generation time. They appear in `memory/shadow/pending/` but are not surfaced in the digest output, brief content, or any other principal-facing channel until `/shadow-review` reveals as a batch.

This is the **anti-self-fulfilling prophecy** rule — the single most important constraint in the predictive layer. See [`docs/prediction.md`](prediction.md) § Shadow invisibility for the full rationale.

If a digest output mentions any pending shadow hypothesis, that's a bug. Lint cannot catch this directly (free text), but human review at fork bootstrap should verify the workflow output template never includes shadow content.

---

## Shadow lookback discipline

Step 8 (shadow lookback) runs through `memory/shadow/pending/` and resolves hypotheses past their `horizon_at`. Two rules govern lookback quality:

### Adversarial default

When a signal looks like it matches a prediction, the agent applies the adversarial prompt:

> What are the STRONGEST arguments this hypothesis was NOT actually fulfilled, even if the agent initially read the signal as a match?

Default verdict on uncertainty: `falsified`. Generosity = motivated reasoning = calibration corruption. See [`docs/prediction.md`](prediction.md) § Adversarial lookback.

### No auto-promote of expired → resolved

If a hypothesis passes its horizon with **no matching signal and no contradicting signal**, the verdict is `expired`, NOT `resolved-no`. Expired hypotheses do NOT count toward accuracy — there's no ground truth.

Auto-promoting expired to falsified inflates the falsification count, biases the calibration, and makes the agent look more accurate at "calling things won't happen" than it actually is. Expired is a separate bucket for a reason.

Step 8 moves expired hypotheses to `memory/shadow/expired/<YYYY-MM>/`. A high expired count is itself a signal — the specificity gate may be too loose (predictions are untestable as written).

---

## Profile refresh trigger — NOT auto-spawn

The digest flags stakeholders with new signal in the window (Step 9). It does **not** auto-spawn the `profile-bootstrap` agent.

### Why no auto-spawn

Three reasons:

1. **Privacy + cadence are principal-controlled.** The principal decides when a profile gets updated, what gets recorded, whether the update applies to a permission-restricted profile (e.g. board members, customers with sensitive context).
2. **Refresh is not free.** It costs agent time + token budget. Automating it on every signal creates churn — most refreshes don't materially change the profile.
3. **Sentiment shifts deserve principal judgment.** A "cooling" signal can be a meeting bad day, a project frustration, or a real relationship deterioration. The principal interprets; the agent should not pre-decide.

### What the digest does

- Lists "Stakeholder updates" with names + signal counts in the render
- Flags sentiment shifts as drift candidates (Step 10)
- Flags `profile bootstrap pending` for stakeholders with ≥3 signals but no profile
- Flags `cooling: <name>` for profiles with no signal in >30 days

The principal then chooses: invoke `profile-bootstrap` (refresh mode), invoke for bootstrap, ignore for now. The decision authority stays with the principal.

---

## Anti-patterns

Patterns to recognize and refuse.

### Running the digest >1×/day

Symptom: principal triggers `/digest` multiple times in the same day. Each run pollutes state (window calculation shifts), eats agent budget, and surfaces the same drift candidates redundantly.

Fix: the workflow's Step 0 cadence guard refuses to run if `last_run_timestamp` is < 4h ago. Override exists (`--force`) for the rare case of "I changed source config, want to verify it works" — but the override should never become routine.

### Auto-committing digest output

Symptom: the workflow stages and commits files (briefs, state updates, profile edits) without principal review.

Fix: NEVER auto-commit. The principal reviews + commits in batch. Briefs sit unstaged. State updates sit unstaged. The principal's commit is the audit trail — the agent's edits are proposals.

Lint can partially detect this (a brief committed by the agent rather than the principal would show up in `git log --author`), but the discipline is fundamentally procedural.

### Auto-spawning profile-bootstrap

Symptom: the digest detects a sentiment shift and spawns `profile-bootstrap` (refresh mode) without asking.

Fix: never. The digest **flags** candidates. The principal **invokes**. See § Profile refresh trigger.

### Shadow generation without specificity gate

Symptom: shadow hypotheses generated with one-keyword `search_terms`, no `source_channels`, or vague `prediction`.

Fix: the specificity gate refuses these. Rejected count goes into `digest_state.md` for calibration tracking. Bypassing the gate destroys per-actor accuracy.

### Source config bloat

Symptom: `memory/digest_sources.md` grows to 10+ sources over time. Each source individually defensible; collectively the digest becomes noise.

Fix: quarterly source-config audit. Drop any source whose recent contributions are <10% of the digest's flagged signals. Tightening is reversible; bloat compounds.

### Drift ignore-then-forget

Symptom: principal acks "ignore 7d", forgets, drift recurs, acks again, repeats. Drift becomes permanent ambient state.

Fix: the digest re-flags after ack expiry. If the same drift is acked >2 times, the agent SHOULD propose a documentation patch ("this drift keeps recurring — should we add to constitution / topic shard?") rather than just re-ack. This proposal is part of the drift response flow's escalation.

### Brief over-generation

Symptom: digest generates briefs for every calendar entry including low-prep events. Principal stops reading briefs in detail.

Fix: tighten `calendar.brief_eligibility`. Better: fewer high-signal briefs than many low-signal ones.

### Render shadow leakage

Symptom: digest output mentions a pending shadow hypothesis ("we predict X will happen by Y date").

Fix: the rendered output template explicitly omits shadow content. If shadow text leaks, it's a workflow bug. Bootstrap-time human review should verify the render template.

---

## Constitution integration

The constitution should include a binding section on digest cadence + drift handling. The proposed section text is owned by `governance-architect` (see this architect's report for proposed wording).

Key bindings to encode in constitution:

- Daily digest is the operational tempo (cadence override only via decision record)
- Drift acks have default 7-day expiry; permanent acks (`9999-12-31`) require explicit rationale
- Briefs auto-generate for ≤48 h high-prep events, NOT all calendar entries
- Shadow hypotheses are invisible at generation time (binding rule from `docs/prediction.md`)
- Profile refresh is principal-invoked, never auto-spawned by digest
- Digest output is NEVER auto-committed; principal reviews state changes in batch

---

## Cross-references

- **Workflow:** [`.claude/workflows/daily-digest.md`](../.claude/workflows/daily-digest.md)
- **State template:** [`memory/digest-state.template.md`](../memory/digest-state.template.md)
- **Sources template:** [`memory/digest-sources.template.md`](../memory/digest-sources.template.md)
- **Session-start hook:** [`.claude/hooks/session-start-digest.sh`](../.claude/hooks/session-start-digest.sh)
- **Source-puller agent:** [`.claude/agents/source-puller.md`](../.claude/agents/source-puller.md)
- **Profile-bootstrap agent:** [`.claude/agents/profile-bootstrap.md`](../.claude/agents/profile-bootstrap.md)
- **Brief template:** [`memory/templates/brief.template.md`](../memory/templates/brief.template.md)
- **Shadow hypothesis template:** [`memory/templates/shadow-hypothesis.template.md`](../memory/templates/shadow-hypothesis.template.md)
- **Triage heuristic:** [`memory/triage-heuristic.template.yaml`](../memory/triage-heuristic.template.yaml)
- **Predictive layer rationale:** [`docs/prediction.md`](prediction.md)
- **Governance:** [`docs/governance.md`](governance.md)
- **Lint rule (state freshness):** [`scripts/lint_rules/digest_state_freshness.py`](../scripts/lint_rules/digest_state_freshness.py)
- **Example output (Lattice):** [`memory/examples/digest.example.md`](../memory/examples/digest.example.md)
