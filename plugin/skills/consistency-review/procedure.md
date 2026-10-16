# Workflow: Consistency-check review (manual triage)

**Trigger:** `/consistency-review <YYYY-MM-DD>` slash invocation by the principal after a `/consistency-check` run, or "review consistency report" in chat.

**Why:** the `consistency-checker` agent surfaces semantic findings but never applies them. Each finding needs a principal decision: accept proposed diff / reject / defer / mark as false-positive. Verdicts feed back into shadow-mode precision metrics in `memory/audits/consistency/_state.md` — that tally is the evidence base for the shadow-mode promotion decision (see `docs/governance.md`).

This workflow runs **interactively in the main thread** (like `/digest`'s drift response sub-flow) — no agent spawn. The principal is the decision-maker; the orchestrator presents findings, applies accepted diffs, and keeps the bookkeeping honest.

## Inputs

- `<YYYY-MM-DD>` — the report date to triage. Defaults to the most recent report in `memory/audits/consistency/` if omitted.

## Procedure

### Step 1 — Open the report

Read `memory/audits/consistency/<YYYY-MM-DD>.md`. Print the summary + each finding in turn. If the report contains `## Re-run <HH:MM>Z` sections, triage the latest run's findings (earlier sections are superseded unless the principal asks otherwise).

### Step 2 — Per-finding triage

For each finding F1..F10 in order, present to the principal:

```
F<n> [SEVERITY] [check-id]
File: <path>
Section: <heading>
Claim: <quote>
Conflict: <quote>
Proposed diff:
  - <old>
  + <new>

Verdict? (accept | reject | defer | false-positive)
```

Wait for the principal's verdict. Optional: the principal answers "accept-with-modification" — they paste the modified diff.

**Verdict meanings:**

- **accept** — finding is correct, proposed diff is correct, apply it
- **reject** — finding is correct, but the proposed diff is wrong / scope is wrong — the principal will edit manually
- **defer** — finding is correct but not actionable now (e.g. the drift is real but the canonical update needs separate stakeholder confirmation)
- **false-positive** — finding is incorrect (agent misread the source, or claim/conflict don't actually contradict). Record the `check-id` — FP clustering drives check tightening (see feedback loop below).

### Step 3 — Apply accepted diffs

For each `accept` verdict:

1. Edit the target file with the proposed diff. **If multiple accepted diffs touch the same file, apply them bottom-to-top** (highest line number first) so earlier edits don't shift the line numbers of later diffs. Context-based patching (the `Edit` tool's `old_string` carries context) makes this caveat mainly relevant to manual line-numbered patches.
2. If the diff touches a file covered by a post-edit hook (constitution, `memory/topics/`, decisions, stakeholders, archive), the hook regenerates INDEX / MAP automatically — these edits run in the main thread, so hooks fire.
3. **Don't commit yet** — accepted diffs batch into one commit at the end of the review.

For `accept-with-modification`, apply the principal's edited version, not the agent's proposal.

### Step 4 — Update the run entry in state

In `memory/audits/consistency/_state.md`, find the run entry for this date and fill in:

```markdown
## Run <YYYY-MM-DD>

- run_id: <preserve>
- commit: <preserve>
- checks_run: <preserve>
- findings_total: <preserve>
- findings_by_severity: <preserve>
- truncated: <preserve>
- review_status: complete
- accepted: <count>
- rejected: <count>
- deferred: <count>
- false_positives: <count>
- precision_this_run: <accepted / (accepted + rejected + false_positives), 2 decimals; "N/A" if denominator is 0 — i.e. only deferred or no actionable findings>
- reviewed_at: <YYYY-MM-DD>T<HH:MM>Z
```

Also update the aggregate metrics at the top of the state file:

- `runs_reviewed`: +1
- `findings_lifetime_total`: += findings_total
- `accepted_lifetime` / `rejected_lifetime` / `deferred_lifetime` / `false_positives_lifetime`: += respective counts
- `precision_rolling`: recompute over lifetime totals (accepted / (accepted + rejected + false_positives))

If the aggregate block doesn't exist yet (first review), seed it with the fields above plus the promotion-gate defaults: `promotion_gate_precision_min: 0.70`, `promotion_gate_min_reviewed_runs: 3`.

### Step 5 — Propose the batch commit

**No auto-commit** — propose the commit and wait for the principal's explicit go (consistent with the binding no-auto-commit rule in `.claude/commands/README.md`).

If accepted diffs were applied:

```bash
git add <touched files including state>
git commit -m "fix(consistency): apply <N> accepted findings from <YYYY-MM-DD> review"
```

If the review produced **only** rejected / deferred / false-positives:

```bash
git add memory/audits/consistency/_state.md
git commit -m "docs(consistency): <YYYY-MM-DD> review — 0 accepted (<N> rejected, <M> deferred, <K> FP)"
```

### Step 6 — Shadow-mode promotion gate check

If today's date is **after** `shadow_mode_end_date` in `_state.md`:

1. Compare `precision_rolling` to `promotion_gate_precision_min` (default 0.70).
2. Compare `runs_reviewed` to `promotion_gate_min_reviewed_runs` (default 3).
3. If both gates pass → propose the integration PR: surface unreviewed high-severity findings via the session-start hook (the promotion path described in `docs/governance.md`). **Don't auto-implement** — propose to the principal; promotion is a governance decision.
4. If the precision gate fails → propose scope narrowing or a check-prompt retune in a separate decision record. Don't promote a noisy signal.

## False-positive feedback loop

False-positives are the most informative verdicts — they reveal where a check's prompt or scope is too aggressive. At the end of the shadow-mode window:

- Cluster false-positives by `check-id`.
- If one check-id dominates → narrow that check's scope in `.claude/agents/consistency-checker.md`.
- For `decided-terms-completeness` FPs specifically → tighten the corresponding registry entries in `memory/audits/consistency/decided-terms.yaml` (`ok_framing` whitelist, exemption regexes) rather than the agent prompt.
- If false-positives are evenly distributed → general prompt retune.

## What NOT to do

- Don't apply diffs without per-finding triage.
- Don't skip the state-file update — the precision tally is the only thing that makes shadow mode meaningful.
- Don't extend the shadow-mode window without explicit reason (anti-pattern — defeats the gate).
- Don't run `/consistency-review` on a date with no report — verify the file exists first (the command pre-flight enforces this).

## Anti-patterns

- "Accept all" without reading findings.
- "Reject all" without distinguishing which proposed diffs were wrong vs which findings were FP — the distinction is what the precision metric measures.
- Mixing this workflow's commits with unrelated work in the same commit.
- Reviewing before the `/consistency-check` run finishes — the agent must complete first.

## Cross-references

- **Command (invocation contract):** `.claude/commands/consistency-review.md`
- **Producer:** `/consistency-check` → `.claude/agents/consistency-checker.md`
- **State file:** `memory/audits/consistency/_state.md`
- **Decided-terms registry:** `memory/audits/consistency/decided-terms.yaml` (template: `memory/templates/decided-terms.template.yaml`)
- **Governance policy:** `docs/governance.md` § Consistency checks (shadow mode + promotion criteria)
