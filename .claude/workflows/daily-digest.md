# Workflow: Daily Digest

**Trigger:** `/digest` (slash command). Runs the procedure below.
**Companion docs:** [`docs/digest.md`](../../docs/digest.md) (policy + rationale), [`docs/prediction.md`](../../docs/prediction.md) (binding rules the predictive steps enforce), [`docs/governance.md`](../../docs/governance.md) (cadence + ack mechanics).
**State file:** `memory/digest_state.md` (per `memory/digest-state.template.md`).
**Sources config:** `memory/digest_sources.md` (per `memory/digest-sources.template.md`).

---

## What this workflow is

The daily digest is the **operational tempo** of Giovanni. Each run pulls from configured sources, detects drift between memory and reality, generates briefs for upcoming high-prep events, and feeds the predictive layer with shadow hypotheses + shadow lookback. Without the digest, the rest of the framework is a static archive.

The 12 steps are sanitized from the source AI Chief of Staff implementation. Step ordering matters — drift detection precedes triage so drift signals don't get re-classified as predictive content; brief gen precedes shadow lookback so brief context can include resolved hypotheses; shadow generation runs **after** render so the principal never sees it at generation time.

---

## Step 0 — Pre-flight checks

1. **CWD check.** Verify the working directory is the Giovanni repo root (presence of `memory/digest_sources.md` + `docs/digest.md`). If neither exists, STOP with one-line error: `ERROR: not in a Giovanni repo (no memory/digest_sources.md). Reinvoke from repo root.`
2. **State file readable.** `memory/digest_state.md` exists and `last_run_timestamp` parses as ISO 8601. If missing or empty:
   - **First run ever:** ASK the principal for a manual seed timestamp (e.g. "start window 7 days ago"). Do NOT default — operating window is meaningful.
   - **Corrupt / missing field:** STOP with diagnostic line pointing at the template.
3. **Cadence guard.** If `last_run_timestamp` < 4h ago, STOP with `INFO: last digest <Nm> ago — re-running this fast pollutes state. Override with --force.` (Override mechanism is the slash command's responsibility; see slash-command-architect.)
4. **Source config presence.** `memory/digest_sources.md` parsed. If empty or no sources listed, STOP with diagnostic. A digest with zero configured sources is a config error, not a "quiet day".

---

## Step 1 — Read state

Parse `memory/digest_state.md` for:

- `last_run_timestamp` — start of pull window (ISO 8601 UTC)
- `last_run_sha` — git rev at last run (for version-control source delta)
- `active_acks[]` — drift flags the principal hasn't resolved yet, with expiry dates
- `last_shadow_review_date` — for cadence flag in Step 12 render
- `shadow_generation_stats` — running counts for monthly calibration aggregation

Hold these in working memory for Steps 5, 8, 10, 11, 12.

---

## Step 2 — Determine sources

Parse `memory/digest_sources.md`:

- One entry per source. Schema in `memory/digest-sources.template.md`:
  - `source_type` — from the generic enum (`chat-platform | email | calendar | project-tracker | version-control | crm | documentation-platform`)
  - `identifier` — channel ID / folder / project ID / repo path
  - `time_window_override` — optional override of default digest window
  - `priority` — `high | medium | low` (triage hint, not strict ordering)
  - `notes` — fork-specific context

If a source's underlying tool is unavailable (e.g. an MCP connector is down), do NOT skip silently — flag it in Step 12's "System hygiene" section.

---

## Step 3 — Window calculation

- `window_start = last_run_timestamp`
- `window_end = now()` (ISO 8601 UTC)
- **Weekend / holiday extension:** if today is Monday AND `window_start` is more than 48 h ago, mark this run as "weekend recap + week-ahead" — calendar pull extends to upcoming Friday EOD.
- **Per-source override:** if a source has `time_window_override`, use that for that source only.

---

## Step 4 — Parallel source pull

### 4a. Connector health gate — probe before trust

Read the `source_health:` block in `digest_state.md` (per-source consecutive-failure counter, maintained in Step 12).

**The carry is a token-saving heuristic, not ground truth.** Before skipping a source on the strength of its counter, run one cheap liveness probe *this run*. Only a failed probe means dead.

This rule exists because the counter is systematically pessimistic. Observed: three sources written off from carry in a single run — all three were alive. A connector that needed re-auth last week does not stay broken out of loyalty, and "the session can't do interactive auth" is not the same claim as "the connector has no token".

Probe shape, per source type:

- **Cheapest identity call the connector has** (`whoami`, current user, account info). An identity response means a live token, whatever the session-start banner says.
- **Point-read on a known id** for chat platforms — never a search. A search returning zero is ambiguous: dead connector, wrong workspace, or a genuinely quiet channel look identical. A point-read on an id you know exists is unambiguous.
- **Tool availability** for connectors that vanish entirely when deauthorised: zero tools = account-level outage, go to fallback.
- **Fallback probe** (browser automation, if the fork uses it): does an authenticated session exist? If yes, fallback is viable this run.

After the probe:

| Carry | Probe | Action |
|---|---|---|
| `< threshold` | — | Pull normally |
| `>= threshold` | fails | **Do not spawn the agent.** A doomed spawn costs a full agent context for an instant error. Activate fallback, report `skipped (dead N runs, probe failed)` in hygiene |
| `>= threshold` | succeeds | Pull normally, reset counter to 0 (recovery) |

Probe **every run**. The probe is cheap; a missed signal is not.

A probe-confirmed outage lasting many runs is an **infrastructure problem, not a daily operating cost** — surface it as an action item ("reconnect X"), not as a recurring hygiene line the principal learns to scroll past.

### 4b. Connector budgets (binding — applies to agents and to main-thread calls alike)

- **Retry cap = 1.** One repeat, only for a transient failure (auth, timeout, 5xx, mismatched payload). A 404, an empty result, or a schema mismatch after a clean retry is a *result*, not a reason to try again.
- **Two identical errors = stop.** Same tool, same error text, twice in one run → that source ends as `ERROR`. No third attempt, no "let me try a different query and see". Hygiene gets `⚠ <source> stopped after 2 identical errors: <error>`; `source_health` increments. The fallback channel is a different lane and may be used once.
- **Bounded queries, always.** Every list/search call carries an explicit cap and a field projection — never default all-fields. At most ~3 pages per source per run; past that, `[... +N more — narrow the window]`. **An unbounded call is a defect of the run regardless of what it returned.** Observed cost of ignoring this: three unbounded queries on the main thread, ~350 KB of result each, in a run whose useful output was a dozen bullets.
- **Result size.** A single tool result over ~50 KB does not belong on the main thread. It belongs in an agent with a narrower query.

### 4c. Spawn — one source per agent

**Single message, N agent calls.** Spawn `source-puller` agents in parallel — one per live source — as one message with N `Agent` tool calls.

Each invocation gets exactly:

- `source_type` — **exactly one value.** Two sources sharing a backend (mail and calendar on the same account) are still two sources. The agent contract rejects a multi-source request and returns `ERROR` without making a single tool call — the whole spawn is wasted, and the run pays for it twice.
- `source_identifier`, `window_start`, `window_end`
- Optional `extra_context` (e.g. `last_run_sha` for version control)

Agents return structured markdown bullets per `.claude/agents/source-puller.md`. They do not synthesize, prioritize, or recommend — the main thread does that in Step 5.

### 4d. Shared-backend serialization

**Two agents hitting the same backend concurrently can cross-wire their responses.** Observed on a connector serving two products behind one gateway: three concurrent consumers, and one agent received the *other product's* data in response to its own query, while point-reads returned pages nobody asked for. The sequential re-pull was clean — so the bug was concurrency, not auth, and nothing about the payload said "wrong".

Rules:

- Group sources by **backend**, not by product name. Different backends → parallel. Same backend → serialize.
- Within a shared backend, either one dedicated agent does its sources in sequence, or the main thread does them one call per message.
- Do not make main-thread calls to a backend while an agent is in flight against it.
- **Guard:** verify the response answers the request — asked for id X, got id X; asked for issues, got issue schema. A mismatch is retried sequentially, never trusted.

### Why parallel

- Sequential pull pollutes main-thread context with raw tool output before synthesis. Parallel keeps each pull isolated in its own agent context.
- Wall time drops from N × per-source latency to max(per-source latency).
- Failure isolation — one failed source does not block the others.

### Failure handling

- Each agent returns bullets or `ERROR: <reason>` as a single bullet. The main thread aggregates errors into Step 12's "System hygiene" section.
- A single failed source does NOT abort the digest — render what arrived.
- Do not fabricate data for failed sources. Honest reporting > coverage theater.
- **Never read a running or finished agent's raw transcript** to find out what it did. The result is the final notification. A task's raw output is the full transcript, and reading it back dumps every raw tool result into the main thread — which is precisely the cost the agent existed to avoid.

### Fallback (degraded mode)

If agent infrastructure is unavailable, the orchestrator MAY fall back to sequential pull on the main thread. This is explicitly degraded — log a system-hygiene flag. Where the fork uses browser automation as a fallback channel: **read navigation only** (direct URL, scroll, read). Never type into a composer, search box, or reply field; the external write gate does not watch that path.

---

## Step 5 — Synthesize

Merge bullets across sources. Deduplicate. Group by topic / stakeholder / decision.

Synthesis rules:

- **Topic clustering** — items mentioning the same topic shard slug or canonical entity collapse into one cluster with multiple source references.
- **Stakeholder clustering** — items where the principal interacts with a profiled stakeholder collapse, with a `signals: <N>` count.
- **Dedup heuristic** — same event surfacing across multiple sources (e.g. an email confirming a calendar event) collapses into the most-source-rich representation.
- **No re-ordering by importance yet** — triage happens in Step 6.

Output of this step is the working set fed to Steps 6, 7, 8, 9, 10.

---

## Step 6 — Triage classification

For each new signal / situation from Step 5 (post-synthesis, pre-drift):

1. Load `memory/triage-heuristic.yaml`.
2. Classify into one of three buckets:

   - **Active branch-out candidate** — satisfies ALL of `active_branch_out.required_all`:
     - Touches ≥2 actors with mapped profile (`memory/stakeholders/<slug>.md`)
     - All actors have `profile_depth: partial` or deeper (no shallow / missing)
     - Situation unresolved (open question, pending decision, contested timeline)
     - Time-bound (deadline / scheduled event / expiring opportunity within `time_bound_horizon_days_max`, default 14 days)

   - **Shadow-only** — satisfies ANY of `shadow_only.required_any`:
     - Single-actor reactive event with downstream effects
     - Multi-actor situation but no time-bound element
     - Passive signal with predictable follow-up behavior

   - **Passive** (default when uncertain — `passive_default: true`). Standard bullet in the relevant render section, no special handling.

3. **Volume caps** (from `triage-heuristic.yaml`):

   - Active candidates: max 3/day (`active_branch_out.daily_max`). If >3 qualify, raise the effective bar this cycle and log `triage threshold raised — active candidates exceeded daily_max` to Step 12 system hygiene.
   - Shadow-only: soft cap 15/day; **hard fail at 25** (`shadow_only.hard_fail_max`). If hard-fail triggered in Step 11, ABORT shadow generation and flag.
   - Passive: no cap.

4. **Slugging** — assign `kebab-case` slug (max 6 words, descriptive) for each active candidate. Stored alongside the situation reference for Step 11 cross-linking.

5. **Output to Step 12 render:**

   - Active candidates: numbered list with launch hint `/branch-out <slug>`
   - Shadow-only: **NEVER rendered.** Silent (binding rule from `docs/prediction.md` § Shadow invisibility).
   - Passive: standard bullets in relevant sections (chat / email / project-tracker lines).

---

## Step 7 — Brief auto-gen for ≤48 h events

For each calendar event from Step 4 within next 48 h, where the event matches **brief-eligible criteria** (configurable, but default = high-prep events):

**Eligible (default):**
- 1:1 with a stakeholder whose profile has `profile_depth: partial` or deeper
- Decision meeting (board, governance, vote)
- External commercial conversation (customer renewal, vendor negotiation)
- Board / exec event
- Negotiation / counterparty conversation flagged in topic shard active threads

**Ineligible (default — skip):**
- Internal stand-ups, daily syncs, recurring blocks ("Place", "Focus time")
- Calendar entries titled `1:1` without a named counterparty
- Mechanical scheduling (interview screening, coffee chats with no decision content)
- Events the principal organized as host (different prep dynamic)

The fork's `digest_sources.md` `calendar.suppress_title_matching` and `digest_sources.md` `brief.eligibility_overrides` tune the boundary.

**For each eligible event:**

1. **File path:** `memory/briefs/YYYY-MM-DD_<event-slug>.md`. Slug = lowercase ASCII, hyphenated, max 50 chars.
2. **Idempotency:** if the file already exists for this event, **refresh** (don't recreate). Preserve any manual annotations. Append new signal to "Counterparty state" rather than overwriting.
3. **Pull context:**
   - Per counterparty: `memory/stakeholders/<slug>.md` (if profile exists; if not, flag "profile: shallow / missing — signals proxy-only")
   - Topic shards referenced in counterparty's `related_topics`
   - Recent chat / email signals with counterparty from Step 4
   - Constitution-level decisions relevant to topic
4. **Generate brief per `memory/templates/brief.template.md`:**
   - Counterparty state (last touch, sentiment trajectory, pattern observation, active threads)
   - Hot topics in their head
   - Talking points (3-5)
   - Fallback positions + red line
   - Expected pushback
   - Open from last meeting
   - Asks / decisions needed today
   - What would be a win
   - Predictive layer (if any) — branch-out artifacts, decision drafts pending the meeting

5. **Do NOT auto-commit.** Leave the brief file unstaged. Principal reviews + commits in batch (see Step 12 and `docs/digest.md` § Anti-patterns).

---

## Step 8 — Shadow lookback

Read all files in `memory/shadow/pending/`.

For each pending shadow hypothesis:

1. Check whether `horizon_at` < today.

2. **If horizon not yet passed:** leave in `pending/`. (No action.)

3. **If past horizon:** classify into exactly ONE of three buckets based on signal evidence in today's Step 4/5 output (plus prior 24 h if helpful):

   **Bucket A — `expected_signal` MATCHED** (positive evidence for prediction):
      - `description` semantic match, OR
      - `search_terms` keyword hit in any source bullet, AND
      - `source_channels` matched — or mismatched while the substance matched (a substance match on the wrong channel stays in Bucket A and resolves as `matched-with-caveat` below; it does not fall out of the bucket)

      Apply adversarial evaluation (binding rule from `docs/prediction.md` § Adversarial lookback):

      > "What are the STRONGEST arguments this hypothesis was NOT actually fulfilled by this signal? Consider: coincidence (signal would have appeared anyway), partial match (signal exists but lacks predicted specifics), alternative interpretations (signal could mean something else entirely), base rate (how often does this signal appear regardless of prediction)."

      Score `matched` (strict) ONLY if adversarial arguments are weak AND the substantive direction matched AND the channel/timing matched.

      Score `matched-with-caveat` if the **substantive direction matched but the channel or timing missed** (e.g. predicted that `morgan-chen` would raise the VP Eng finalist concern on the chat platform, and the concern arrived in a meeting instead; predicted email arrived 1 day past horizon). Status stays `resolved-yes` and it **counts as matched** for scoring — record the miss in the optional `caveat:` field of the resolution block (per `memory/templates/shadow-hypothesis.template.md`) and note it in `adversarial_check`, so calibration can distinguish strict from caveat matches. **A channel/timing miss alone is NOT grounds for `falsified`** — the substantive prediction takes precedence.

      Score `falsified` only if the adversarial arguments are strong — the apparent match was coincidence, content-shallow, mis-interpreted, or noise. Default to `falsified` if uncertain **on substance**, not on channel/timing pedantry.

      **Symmetry principle (binding):** generosity on substance corrupts calibration one way (motivated reasoning inflates accuracy); strictness on channel/timing corrupts it the other (false negatives deflate it). Default-skeptical applies to substance; channel/timing misses are caveats, not falsifications.

      → Record the verdict in the hypothesis file (`status`, `resolved_date`, `resolved_reasoning`, `adversarial_check`, optional `caveat:`). Move file to `memory/shadow/resolved/<YYYY-MM>/<file>.yaml`. **Do NOT touch `actor-scores.yaml`** — aggregation happens exclusively in `/calibration-report`.

   **Bucket B — CONTRADICTING signal present** (active negative evidence):
      - Counterparty observably took the opposite action (e.g. prediction was "Karim signals openness", reality was "Karim explicitly declined"), OR
      - Third-party / market signal directly contradicts predicted outcome

      → Score `falsified`. Record the verdict in the hypothesis file. Move file to `memory/shadow/resolved/<YYYY-MM>/<file>.yaml`. (`actor-scores.yaml` mutation stays in `/calibration-report`.)

   **Bucket C — SILENT (no positive match, no contradicting signal):**
      - No expected_signal match AND no observable contradicting action
      - True absence of ground truth (the predicted event neither happened nor demonstrably didn't happen)

      → Move file to `memory/shadow/expired/<YYYY-MM>/<file>.yaml`. **Do NOT count toward accuracy** (no ground truth observable). Flag in Step 12 render: `⚠ <N> shadow hypotheses expired without ground truth — specificity gate may need tightening`.

**Critical distinction (P1 fix 2026-05-21):** Bucket B (active contradiction) ≠ Bucket C (silence). Counting Bucket C as falsified would corrupt calibration by penalizing the framework for unfalsifiable predictions. Tighten specificity gate via `triage-heuristic.yaml` if Bucket C rate exceeds ~40% / month.

4. Apply frontmatter updates to moved files per schema (`memory/templates/shadow-hypothesis.template.md` + `prediction-runtime.md` § Step 2c rule "empty `adversarial_check` at resolution is a governance breach"):

   | Bucket | Destination | `status` | `resolved_date` | `resolved_reasoning` | `adversarial_check` |
   |---|---|---|---|---|---|
   | **A — match** | `resolved/<YYYY-MM>/` | `resolved-yes` or `resolved-no` (per adversarial verdict) | today | required — verdict reasoning citing observed signal | required — "could match be coincidence/partial/wrong-interpretation?" reasoning; for matched-with-caveat MUST note the channel/timing miss (also recorded in the optional `caveat:` field) |
   | **B — contradiction** | `resolved/<YYYY-MM>/` | `resolved-no` (falsified) | today | required — verdict reasoning citing contradicting signal | required — "could contradicting signal be misread/partial/alternative-interpretation?" reasoning |
   | **C — silent** | `expired/<YYYY-MM>/` | `expired` | today | required — "no signal observed in either direction by horizon" | optional/empty — no signal to audit (expired ≠ verdict resolution) |

   **Binding:** Bucket B MUST populate `adversarial_check` same as A. Apparent contradictions can be misread (e.g. counterparty's negative action was about different topic, third-party signal was unrelated). Skipping adversarial discipline on falsified verdicts produces overconfident calibration in the opposite direction (under-counting matches that were actually right).

   **Lint enforces:** `scripts/lint_rules/shadow_expired_pending.py` flags empty `adversarial_check` on files under `resolved/` (medium severity), alongside its pending-past-horizon check. Files under `expired/` are exempt.

**Lookback runs silently.** Verdicts live in the hypothesis files; `actor-scores.yaml` aggregation happens exclusively in monthly `/calibration-report`, and results surface there — not in the rendered digest output.

---

## Step 9 — Profile refresh signals

For each stakeholder with new signal in this window's Step 4/5 output:

1. **If `memory/stakeholders/<slug>.md` exists:**
   - Note the signal for inclusion in Step 12 render ("Stakeholder updates" section).
   - If sentiment shift detected (warming→cooling or vice versa) → mark as extra drift candidate for Step 10.
   - **Do NOT auto-edit the profile.** Flag the stakeholder as refresh-candidate. Principal invokes `profile-bootstrap` (refresh mode) manually if they want the update applied — see `docs/digest.md` § Profile refresh trigger.

2. **If profile missing AND stakeholder appears in any Step 4/5 bullet ≥3 times:**
   - Flag "Profile bootstrap pending: `<name>`" in Step 12 render.
   - The principal decides whether to bootstrap.

3. **If profile exists but stakeholder has no signal for >30 days:**
   - Flag "Cooling: `<name>`" in Step 12 render.
   - Useful for retention / governance — silence is itself a signal.

---

## Step 10 — Drift detection

For each new fact / decision from Step 4/5 (post-synthesis):

1. **Search canonical memory** for related claims:
   - Constitution (`knowledge/<constitution>.md`)
   - L1 operational memory (`memory/CLAUDE_MEMORY.md`)
   - Active topic shards (`memory/topics/`)
   - Active blockers list

2. **Apply drift definitions** from `digest_sources.md`:
   - (a) Source claim X contradicts canonical claim Y
   - (b) Untracked knowledge / constitution edit since last_run
   - (c) Decision record exists but knowledge / constitution not updated to reflect
   - (d) Cross-file contradiction inside `knowledge/`
   - (e) Profile sentiment shift unprocessed in canonical state
   - (f) Other domain-specific drift definitions configured in fork

3. **Filter through `active_acks`:** if a drift candidate matches an active ack, suppress it (the principal has already chosen to ignore for N days).

4. **Re-evaluate expired acks:** if an ack from `digest_state.md` has expired AND the underlying drift still applies, re-flag.

5. **Output to Step 12 render:** numbered drift flags with actionable choices (`confirm` / `ignore Nd` / `patch <file>:<change>`). See `docs/digest.md` § Ack flow for the full state machine.

---

## Step 11 — Shadow generation

**Runs AFTER Step 12 render. Invisibly. Per binding rule from `docs/prediction.md` § Shadow invisibility.**

For each item classified as `shadow-only` in Step 6:

1. **Specificity gate check** (per `memory/triage-heuristic.yaml` `specificity_gate.required_for_generation`):
   - Prediction must be one sentence, specific (not "X will happen at some point").
   - `expected_signal.search_terms` ≥ 2 keywords.
   - `expected_signal.source_channels` ≥ 1.
   - **If ANY fails → DO NOT generate.** Skip silently. Log rejected count to `digest_state.md` (`shadow_generation_stats.rejected_specificity_today`) for monthly calibration tracking.

2. **Hard fail check:** if running count of this-cycle generated hypotheses reaches `shadow_only.hard_fail_max` (25), STOP generation immediately. Flag `⚠ Shadow volume hard-fail (>25) — triage heuristics need review.` in `digest_state.md` system hygiene.

3. **If both gates pass, generate the hypothesis YAML** per `memory/templates/shadow-hypothesis.template.md` schema. File path:

   ```
   memory/shadow/pending/<YYYY-MM-DD>-<actor-slug>-<topic-slug>-<4char-hash>.yaml
   ```

4. **The hypothesis is invisible.** Never reference it in the rendered digest. Never quote it in 1:1 briefs. Never surface to the principal until `/shadow-review` reveals as a batch.

5. **Update `digest_state.md`:**
   - `shadow_generation_stats.generated_today++`
   - `shadow_generation_stats.last_generated` — append `<id>` for audit trail

---

## Step 12 — Render output + update state

### Render order (digest output to chat — NOT a file)

The rendered digest is the principal's morning briefing. It is **not committed** as a file — committing daily digests pollutes git history without value. State updates DO get committed (see below).

Render structure (sections appear only when they have content):

```
Daily digest — <YYYY-MM-DD> <weekday>

Recap (since <last_run_timestamp>)
  Version control: <CHANGELOG match status + N commits to knowledge/>
  Chat: <3-5 key bullets from chat-platform sources>
  Email (relevant): <3-5 bullets — explicit relevance criteria from digest_sources.md>
  Email (other): <count> messages (<top sender clusters>)
  Project tracker: <task / issue deltas>
  CRM / docs (if configured): <key signals>

Today (<weekday>)
  HH:MM <event> — context from <topic-shard or canonical doc> or [no context]
                  brief: memory/briefs/<file> (if generated this cycle)

Week ahead (through <Friday date>)
  <date HH:MM> <event / deadline> — 1-line context
                brief: <file> (if ≤48h) or "brief due in N days"

Active blockers — delta since last run
  New: <…>
  Resolved: <…>
  No change: <count> (<names>)

Asks (things only the principal can unblock)
  #A1 <question — one sentence, decidable as written>
      proposed: <the answer you would give if it were yours to give>
      unblocks: <what moves the moment it is answered>
      tier: now | this week | when convenient
  #A2 …

Stakeholder updates
  Touched this window: <names with new signal>
  ‼ Sentiment shift: <name> <direction> — <trigger summary>
  ‼ Cooling >30d: <names with no signal>
  Profile bootstrap pending: <names with ≥3 signals but no profile>

‼ Drift flags
  #1 [source: <source>] claims <X>
       <canonical-file>:<line> says <Y>
       action? confirm | ignore Nd | patch <file>:<change>
  #2 …

‼ Active branch-out candidates (max 3, per Step 6 triage)
  - <situation-slug> — <1-line context> · actors: <list> · horizon: <days>
    launch: /branch-out <situation-slug>
  - …

Briefs generated this cycle (≤48 h events)
  <event-slug> — memory/briefs/<file> — TLDR: <talking point #1 + hot topic #1>

Open follow-ups / awaiting reply
  <Awaiting from <person> — <thing> due <date>>

Active acks
  <expires YYYY-MM-DD> <ack summary> | acked YYYY-MM-DD

System hygiene (flags only when applicable)
  ⚠ /shadow-review due (last <date> > <cadence> days ago)
  ⚠ <N> shadow hypotheses expired without ground truth (specificity gate review needed)
  ⚠ Shadow volume hard-fail (>25) — triage heuristics need review
  ⚠ Source pull failed: <source> — <error>
  ⚠ Degraded mode: source-puller fallback used (sequential pull)
  ⚠ Mirrored external tool/skill library sync >7d stale (optional — only if the fork mirrors one)
```

Drift items are numbered so the principal can reference `#N` in their response; asks are numbered `#A<N>` for the same reason.

**Every ask carries a proposed answer.** A question on its own moves work from the assistant to the principal — which is backwards, and it is how a digest turns into a list of homework. A question plus the answer you would have given turns the ask into a yes/no: the principal corrects it or waves it through, and either way it took them ten seconds. If you cannot propose an answer, say what you would need in order to have one; an ask with neither is not ready to be asked.

`unblocks` is the anti-padding field. If nothing moves when the question is answered, it is not an ask — it is curiosity, and it belongs nowhere in the digest.

### Update `memory/digest_state.md`

- `last_run_timestamp = now()` (ISO 8601 UTC)
- `last_run_sha = <git rev-parse HEAD>`
- `source_health` — per source: consecutive failure count, and **one terse sentence** on the last failure. Reset to 0 on any successful pull, including a recovery after a passed probe.
- Move expired acks (from Step 1) to `## Expired acks` section
- Update `shadow_generation_stats`:
  - `generated_today` — total this cycle
  - `rejected_specificity_today` — count from Step 11 specificity gate rejections
  - `expired_no_ground_truth_today` — count from Step 8 expired moves
  - `hard_fail_triggered_today` — boolean
  - `last_generated` — IDs of hypotheses generated this cycle

### Keep the state file a state file

`digest_state.md` is **state, not a journal**. Every run rewrites it; nothing accumulates. The failure mode is gradual and quiet: each run appends one more note about a connector that misbehaved, none of them ever expire, and a year later session start is reading a 68 KB file to learn one timestamp. (Measured, in the implementation this framework came from: 68.5 KB, cut to 24 KB once rotation existed.)

Rules:

- One line per fact. A source's health is a counter plus one sentence — not a history of what it did.
- Durable lessons about a connector's quirks belong in `memory/digest_sources.md` (the playbook, which is *meant* to accumulate). Per-run numbers belong in this run's state and nowhere else.
- Expired acks move to their section, then out. Shadow stats are counters, not logs.
- Soft cap: **32 KB**. Over that, the file is a journal and needs rotating, not a bigger cap.

### Do NOT auto-commit

The digest workflow makes file changes (state update, brief files written). It does NOT commit them. The principal reviews + commits in batch.

This is the binding rule that prevents the digest from silently churning the git log. See `docs/digest.md` § Anti-patterns.

---

## Drift response sub-flow

After the digest renders, the principal responds to flagged drifts.

**`drift #N confirm`:**
1. Propose specific patch (file + line + diff).
2. Wait for `commit` or principal-supplied refinement.
3. On `commit`: Edit + `git add` + `git commit` with appropriate prefix (`decision:` or `docs(<canonical>):`) + check whether `CHANGELOG.md` needs update.

**`drift #N ignore Nd`** (where N is days):
1. Append to `memory/digest_state.md` § Active acks:
   ```
   - [ack <today> expires <today+Nd>] <drift summary> | source: digest <today> #N
   ```
2. No git commit (state file is committed separately, in batch).

**`drift #N patch <text>`:**
1. Use principal-supplied text as the patch.
2. Otherwise behaves like `confirm` flow.

---

## Memory ack flow (outside drift)

If the principal verbally says "X changed" in chat:

1. Acknowledge — confirm understanding.
2. Append to `digest_state.md` § Active acks with 7-day expiry:
   ```
   - [ack <today> expires <today+7d>] X changed | source: chat <today> | trigger: divergence with <where>
   ```
3. Next digest respects the ack — doesn't re-flag the same divergence.

---

## Branch-out launch flow (outside digest)

After digest render, the principal sees active candidates in "Active branch-out candidates". To execute:

1. Principal runs `/branch-out <situation-slug>`.
2. The `/branch-out` command runs per `.claude/commands/branch-out.md`.
3. Output: branch-out artifact in `memory/branch-out/` + decision record draft in `memory/decisions/`.
4. Principal fills the decision record (`chosen_move`, `reasoning`, `trigger_conditions`) and commits with `decision:` prefix.

---

## Cross-architect boundaries

This workflow depends on the following deliverables owned by other architects:

- **`source-puller` agent spec** — `subagent-roster-architect` (done; `.claude/agents/source-puller.md`)
- **`profile-bootstrap` agent spec** — `subagent-roster-architect` (done; `.claude/agents/profile-bootstrap.md`)
- **Triage heuristic + shadow generation + shadow lookback bindings** — `prediction-architect` (done; `docs/prediction.md` + `memory/triage-heuristic.template.yaml`)
- **Brief template** — `memory-architect` (done; `memory/templates/brief.template.md`)
- **Shadow hypothesis template** — `prediction-architect` (done; `memory/templates/shadow-hypothesis.template.md`)
- **Slash command `/digest` implementation + drift ack CLI flow** — `slash-command-architect` (PENDING — see open items below)
- **Constitution patch (digest as binding daily cadence)** — `governance-architect` (PENDING — patch text in this architect's report)

---

## Open items for downstream architects

- **`slash-command-architect`:** Build `/digest` slash command that orchestrates Step 4 parallel fan-out (single message, N agent calls). Build `--force` flag for cadence guard override. Build drift response CLI mini-grammar (`drift #N confirm | ignore Nd | patch <text>`).
- **`governance-architect`:** Add the digest cadence as binding section to the constitution template. See this architect's report for proposed section text.
