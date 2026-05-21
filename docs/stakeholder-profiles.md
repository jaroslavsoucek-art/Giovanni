# Stakeholder Profiles — Workflow

This document describes when to create a stakeholder profile, how to refresh
it, when to retire it, and which disciplines keep the data useful over time.

The **schema** is in `memory/templates/stakeholder.template.md` (template
file with inline field documentation) and `memory/templates/stakeholders-README.template.md`
(directory README explaining the contract). This document is the **workflow**:
when, why, how often, with what hygiene rules.

---

## Why profiles exist

A stakeholder profile is **operational externalized memory of a person**.
It exists to:

1. Lift session-entry context when a meeting with that person is upcoming
2. Give adversarial review a recipient-context source
3. Surface drift signals (sentiment trajectory shifts the digest can flag)
4. Match tone in drafted messages (their communication style is part of the file)
5. Seed predicted reactions for the predictive layer (branch-out)

It does **not** exist to:

- Be a tribute / favourable assessment
- Be a CRM record of every interaction
- Replace the principal's own judgment in the moment

A useful profile makes a future-you faster. A useless one makes future-you
distrust the file.

---

## Bootstrap trigger criteria

Create a profile when **any** of the following is true:

| Trigger | Why it matters |
|---|---|
| Person appears in ≥2 decision records as `key_stakeholders` | Their behavior is shaping decisions; future-you needs the model |
| Person attends ≥3 standing meetings (1:1, working group, board) | Recurring touchpoints justify the upfront cost |
| Person has a named active thread that's lived >14 days | Persistent engagement = persistent profile worth |
| Person is named in `key_stakeholders` of any topic shard | The cross-reference contract needs the profile to exist |
| Explicit user trigger: "bootstrap profile for X" | Principal judgment overrides the heuristic |

**Don't profile:**

- One-off contacts (intro emails, single meetings, conference contacts)
- Broadcast audiences (mailing list recipients, channel observers, signal-takers)
- People you only hear about from others (no direct interaction yet)

A profile is overhead. The break-even is roughly **5-10 future interactions
where you'd otherwise reconstruct context from memory** — below that, no
profile pays for itself.

---

## Bootstrap procedure

For each person crossing the criteria above:

### Step 1 — Identify primary channels

- Slack / Teams / Discord ID (whichever your org uses)
- Email address (from existing threads or directory)
- Project tracker user (Asana / Jira / Linear)
- Calendar attendee normalized form (sometimes display name varies)

### Step 2 — Signal gathering (6-month window for bootstrap)

Pull from each channel where this person interacts with the principal:

- **DM history** — all direct exchanges
- **Channel mentions** — where they speak, where they're mentioned
- **Email exchanges** — both directions
- **Calendar shared meetings** — recurrence pattern + attendance discipline
- **Project tracker activity** — tasks they assign / own / follow
- **Git commit references** — historical evolution of this profile if it exists

Cap the pull at ~200 messages per source. Beyond that, you have a CRM problem
not a profile problem.

### Step 3 — Pattern extraction

For each source stream:

- **Topics** — top 5 things they engage with (manual clustering, not LLM
  summarization — manual gives sharper edges)
- **Sentiment trajectory** — date-anchored entries. Each entry = one
  observation + one signal interpretation. Don't aggregate; the observation
  granularity is what makes the trajectory useful.
- **Position statements** — verbatim quotes where they explicitly say what
  they want or won't accept
- **Communication style** — message length distribution, response timing,
  channel preferences, register

### Step 4 — Profile depth heuristic

Set `profile_depth` honestly:

- **shallow** — <5 touches in 90d, mostly observational; cannot predict
  reactions. Profile is preliminary; flag with `‼ Low signal warning` in
  body if signals are thin.
- **partial** — 5-20 touches across channels, some 1:1 evidence, can
  predict reactions to in-domain asks
- **deep** — 20+ touches across multiple channels, 1:1 + email + Slack
  confirmed, can predict reactions even out-of-domain

A `relationship_type: asymmetric-power-up` with `profile_depth: shallow`
is a red flag — high-stakes counterparty with thin signal. Plan a
targeted bootstrap session.

### Step 5 — Draft + assumption flagging

Fill the template. For any claim not directly supported by observed
signal, flag with an explicit inference marker:

- `[INFERRED: <basis for the inference>]` — for behavioural patterns
- `[TBD: <what's needed to verify>]` — for fields you genuinely don't know yet
- `[OBSERVED YYYY-MM-DD]` — implicit for any claim with a date reference

The inference markers stay in the file. Future-you will thank present-you
for being honest about what's known vs guessed.

### Step 6 — Validation

Submit one profile to the principal for accuracy review before
batch-generating more. The first one calibrates your inference; if your
draft is consistently off, the heuristic needs tuning before you spend
time on the next nine.

### Step 7 — Commit

```
git add memory/stakeholders/<slug>.md
git commit -m "feat(stakeholders): profile <slug> — bootstrap"
```

Never auto-commit. The principal batches profile commits.

---

## Refresh cadence

Refresh patterns vary by relationship type:

| Relationship type | Passive refresh trigger | Active refresh cadence |
|---|---|---|
| `peer` | Any meaningful interaction | Quarterly full review |
| `asymmetric-power-up` | Any meaningful interaction | Monthly full review |
| `asymmetric-power-down` | Any meaningful interaction | Monthly for direct reports; quarterly otherwise |
| `customer` | Any commercial signal | Quarterly + pre-renewal |
| `vendor` | Any contract / SLA event | Annual + pre-renewal |
| `counterparty` | Any negotiation move | Pre-engagement always |

### Passive refresh (in digest)

If you run a daily digest agent (see `digest-architect`), wire it to
append to `Sentiment trajectory` whenever a signal is detected:

- New DM exchange — append entry
- Calendar event with them — append entry post-event (with outcome if known)
- Email exchange — append entry
- Mention in their channel — append entry

Each appended entry must have: date, channel, observation, signal
interpretation. Don't append entries without the interpretation line —
the agent is supposed to do the work of interpreting, not just logging.

If sentiment shifts (warming → cooling or vice versa), the digest flags
explicitly to the principal.

### Active refresh (scheduled)

The full review goes deeper than appending trajectory entries:

1. Re-read the full file
2. Update `Hot topics in their head` — what's actually occupying them now?
3. Update `Active threads` — close concluded ones, add new ones, flag stalled
4. Update `Predicted reactions` — are predictions from last month verified
   or falsified? (Falsified predictions are signal; preserve a few in
   `Relationship history` as "predicted X, actually Y" — calibration
   evidence for the predictive layer.)
5. Update `Watch points` — are watch signals firing? If yes, add to
   sentiment trajectory.
6. Update `Role & decision authority` — has anything shifted in their
   position?

Then commit: `docs(stakeholders): refresh <slug> — <YYYY-MM>`.

---

## Sentiment trajectory discipline

This is the **single most-important hygiene rule** in the profile system.

### Format (binding)

```markdown
- **YYYY-MM-DD — <channel / event>** — <what happened in 1-3 lines> — *signal: <interpretation>*
```

Three required parts:

1. **Date + channel** — locates the observation in time and context
2. **What happened** — the observable behaviour (verbatim where useful)
3. **Signal interpretation** — your read on what the behaviour means

### Append-only, never overwrite

- New observations append
- Old observations stay
- If an interpretation turns out to be wrong, **add a new entry** noting
  the correction; don't edit the original
- The arc is the value — overwriting destroys the arc

### Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| `2026-05-12 — supportive` | No observation, no signal, no value |
| `2026-05-12 — meeting went well` | No specific behavior, no interpretation |
| Removing entries you don't like the look of | Destroys the audit trail |
| Aggregating "this month: cooling" without dated observations | Loses the trigger event |
| Predictions written into the trajectory ("she'll probably push back") | Predictions go in `Predicted reactions`, not trajectory |

### Trimming

When the inline trajectory exceeds ~15 entries, archive older entries:

1. Move pre-cutoff entries to `memory/archive/<YYYY-MM>.md` under a
   "<slug> trajectory pre-<cutoff>" section
2. Note the trim in the profile: `(Older entries archived in
   memory/archive/<YYYY-MM>.md under "<slug> trajectory pre-<cutoff>")`

Never delete trajectory entries without archiving — the lost context will
bite you later.

### Counter-example: how source went wrong

A bad source-profile pattern looks like this:

```
- 2026-05-12 — DM — sentiment: supportive
- 2026-04-29 — 1:1 — sentiment: neutral
- 2026-04-08 — 1:1 — sentiment: warming
```

This tells you nothing. What happened on those dates? What did they say?
Why did the interpretation shift? Future-you can't act on this.

A good pattern:

```
- **2026-05-12 — email forward** — forwarded TechCrunch article on competitor X, no commentary attached — *signal: cooling. Pattern: silence-then-forward = "what's your take?" probe.*
- **2026-04-29 — monthly 1:1** — raised Net Retention as a metric we don't yet report; asked to add to monthly board pack — *signal: firming. Standing agenda growing in governance direction.*
- **2026-04-08 — monthly 1:1** — added burn-rate to standing agenda — *signal: shifting from supportive to governing. First institutionalized scrutiny vector.*
```

The good pattern has observations + interpretations + a coherent arc. It
predicts what to expect 2026-05-26.

---

## Predicted reactions discipline

This section is **the differentiation** of this schema. No off-the-shelf
tool does it. The discipline that makes it useful:

### Format (binding)

```markdown
- **If <specific event>, <name> will likely <specific action>.** Reasoning: <observed pattern from sentiment trajectory or relationship history>.
```

Three required parts:

1. **Specific conditional** — the event that triggers, not a vague situation
2. **Specific predicted action** — what they'll actually do, not a vibe
3. **Reasoning anchored in observation** — cite the date/event that gave you this pattern

### Counter-examples

| Bad | Why |
|---|---|
| "Sarah will probably be supportive on Series B" | No event trigger; no specific action; no reasoning |
| "If asked about pricing, she'll push back" | Vague event ("asked"); vague action ("push back"); no reasoning |
| "She always supports the team" | Not a prediction, not falsifiable, not useful |

### Good

> If we surface dp1 churn risk in next 1:1 (before quarterly numbers reveal it),
> Sarah will likely add it as standing agenda item rather than escalate it to
> board. Reasoning: pattern from 2026-04-08 (burn rate) and 2026-04-29 (Net
> Retention) — she institutionalizes scrutiny through cadence, not ad-hoc
> alarms. Escalation to board is reserved for >50% materialized risk.

This is testable. After the 2026-05-26 1:1, future-you can check: did Sarah
add it as standing agenda, or did she escalate? Outcome feeds the
calibration loop.

### Tracking accuracy (optional)

If you run the predictive layer (`prediction-architect`), each predicted
reaction can be tracked as a shadow hypothesis. The pattern:

1. Predicted reaction is written 2026-05-21
2. Event happens 2026-05-26 (1:1)
3. Outcome captured in trajectory entry
4. Shadow hypothesis marked verified / falsified
5. Aggregate accuracy by predictor (the human or the agent) over time

Without the predictive layer, the section is still useful — it just isn't
formally calibrated. Most forks should start without the layer; add it
once predictions are routinely written.

---

## Active threads hygiene

Active threads have three states:

- **Open** — work in flight, expected next move identified
- **Stalled** — no movement >30 days; flag in watch points, surface in digest
- **Closed** — concluded; migrate to `Relationship history` with outcome

Don't let threads ghost into the past. If a thread shows no movement and
no expected next move, either close it explicitly or mark it stalled.
The middle state — "thread that's just hanging around" — corrodes the
trust that the file reflects reality.

### Migration to history

When a thread concludes:

1. Cut from `Active threads`
2. Paste in `Relationship history` with date + outcome
3. Add a one-liner to `Sentiment trajectory` capturing the closure

Example:

```
Active threads → Pending from her: "Series B narrative v0.2 response"

(after she redlines v0.3)

Relationship history: "2026-05-31 — Series B narrative v0.3 redlined; concerns on Net Retention framing addressed; v0.4 in draft."
Sentiment trajectory: "**2026-05-31 — email redline** — returned 14 specific edits on v0.3, mostly tone-focused — *signal: engaged, willing to invest in the framing. Stronger than expected.*"
```

---

## Retention policy

| State | Trigger | Action |
|---|---|---|
| `active` | Default for current relationships | File lives at `memory/stakeholders/<slug>.md` |
| `dormant` | No interaction in 90+ days but still relevant | Stays in directory; digest flags as cooling |
| `archived` | Relationship concluded (org change, project ended, etc.) | After retention threshold (default 90 days dormant), move to `memory/stakeholders/_archived/<slug>.md` |

### Configurable threshold

The 90-day threshold is the default. Configurable via
`docs/governance.config.yaml`:

```yaml
stakeholder_dormant_threshold_days: 90
stakeholder_archive_threshold_days: 180  # 90 dormant + 90 grace
```

Stricter privacy postures may want shorter (e.g. 30/60 for ex-employees).
Softer ones may want never-archive.

### Reactivation

If an archived person re-engages:

1. Move file back from `_archived/` to `stakeholders/`
2. Set `status: active`, update `last_touch`
3. Add a trajectory entry capturing the re-engagement
4. Add a Relationship history entry covering the dormancy gap
5. Refresh `Hot topics in their head` and `Active threads` — old assumptions
   are stale

Don't pretend the gap didn't happen — the gap itself is signal.

### Final retirement

If a person fully leaves the relevant context (e.g. retired, moved sectors,
relationship genuinely ended):

- Set `status: archived`
- Keep file in `_archived/` indefinitely — it's historical record
- Don't delete; future you may need the context if they reappear

---

## Privacy considerations

Profiles contain **operational notes about real people**:

- Predicted reactions (your forecasts of their behavior)
- Pattern observations (their tics, allergies, biases)
- Relationship dynamics (power gradients, hidden incentives)

This is sensitive. Decide **before** committing the first profile:

### Option 1 — Private repo

- Commit profiles to the same git repo as everything else
- Repo must stay private (no public mirror, no employee directory access)
- Team can use them; exposure grows linearly with team size

### Option 2 — Personal-only via `.gitignore`

- Add `memory/stakeholders/` to `.gitignore`
- Profiles stay on the principal's machine only
- Lose backup + cross-device sync via git; consider encrypted personal backup

### Option 3 — Encrypted at rest

- `git-crypt` or similar on `memory/stakeholders/`
- Repo can be wider-shared; profiles only readable by key-holders
- Setup friction; key management is a real ongoing cost

### Default fork-time recommendation

**Private repo, no extra encryption.** Most forks have a small team, and
the operational benefit of profiles is too high to leave them on one
machine.

### The honesty test

If you can't write the profile as honestly as you'd think about the person
in private, the file is going to drift toward sanitized uselessness.
Either:

- Increase privacy (Option 2 or 3) so honesty is safe, or
- Acknowledge that profiles will be lightweight and shift the operational
  intelligence somewhere else

The middle ground — profiles that exist but are too sanitized to predict
behavior — is the worst of both worlds.

---

## Anti-patterns (summary)

| Anti-pattern | What to do instead |
|---|---|
| Single-line "supportive" entries | Write the observation that produced the assessment |
| Predictions without reasoning lines | Cite the trajectory date that gave you the pattern |
| Profile as flattery / tribute | Operational predictions only; no warmth budget |
| Stale `last_touch` | Update on every interaction; staleness corrupts drift detection |
| Active threads hanging open >30 days untouched | Close, stall, or escalate |
| Overwriting trajectory entries | Append-only — corrections add a new entry |
| `profile_depth: shallow` + `relationship_type: asymmetric-power-up` | Flag as urgent; high-stakes counterparty needs targeted bootstrap |
| Sentiment shift without trajectory entry explaining the trigger | The trigger event is the signal; capture it |
| `last_touch` updated but no new trajectory entry | Update both or neither |

---

## Quick-reference: lifecycle

```
Bootstrap criteria met
         ↓
Bootstrap profile (Step 1-7)
         ↓
Active relationship
   ↑          ↓
Refresh ←── Passive append on interactions
   ↑          ↓
Active refresh (cadence by relationship_type)
         ↓
No interaction 90+ days?
         ↓ yes
   status: dormant
         ↓
Re-engagement?  →  yes  →  Reactivate (status: active)
         ↓ no
   90 more days dormant?
         ↓ yes
   status: archived → move to _archived/
         ↓
   Person re-engages?
         ↓ yes
   Move back, capture gap in Relationship history
         ↓ no
   Stay in _archived/ as historical record
```
