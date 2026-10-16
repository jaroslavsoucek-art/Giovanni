# <Project / role name> Memory — live operational state

<!--
Layer 1 operational shortcut. Read by the agent at every session start.
Hard cap: 300 lines. Warn at 80 % (240 lines), stop adding above 300 — audit first.
Strikethrough ratio cap: 2 % of lines. Anything struck through must be archived
or restored within one session.

This file is NOT:
- a knowledge base (canon lives in `knowledge/`)
- a decision log (per-decision audit trail lives in `memory/decisions/`)
- a chat log (git history is the chat log)
- an archive (resolved items move to `memory/archive/<YYYY-MM>.md`)

This file IS:
- active blockers (what's stopping progress this week)
- this week (concrete deliverables / meetings / actions in current 7 days)
- on the horizon (next ~2-4 weeks, light touch)
- watch list (no action yet, just monitor)
- open questions (explicit [TBD] items needing a decision)

For canonical definitions → `knowledge/<constitution-file>.md`
For change history → `git log memory/<this-file>.md`
For archived items → `memory/archive/<YYYY-MM>.md`
-->

> **Last update:** YYYY-MM-DD — <1-line summary of most recent material change>
> For recent context (last 7 days of changes) → `git log memory/<this-file>.md`

---

## Purpose & context

<!--
2-4 sentences. Who owns this initiative, what is it, what role does memory play.
Identify:
- Principal (whose CoS this is — name + role)
- Scope of the initiative
- Anchor decisions / sequencing if relevant
- Time horizon

This section changes rarely. If it's changing every audit, move the volatile parts
to a constitution patch instead.
-->

<Principal name> owns <initiative scope>. <Role description>.

- **<Key fact 1>** — <brief>
- **<Key fact 2>** — <brief>
- **<Key fact 3>** — <brief>

### Key stakeholders

<!--
2-4 lines max. Just slugs + 1-line role.
Detail belongs in `memory/stakeholders/<slug>.md`.
If this section grows beyond 4 lines, that's a signal: graduate to stakeholder profiles.
-->

**Internal:** <slug> (<role>), <slug> (<role>), <slug> (<role>)
**External:** <slug> (<role>), <slug> (<role>)

### Communication style

<!--
1-3 bullets. How does the principal communicate, what tone is expected internally
vs externally. This is also low-volatility and a good candidate to live in the
constitution if it stabilises.
-->

- <Tone preference>
- <Internal vs external split>

---

## Active blockers (<current month / quarter>)

<!--
Numbered list. One line per blocker, with a pointer to a topic shard if it has
its own dedicated state. If a blocker has >5 sub-items, it should already be
a shard — replace the detail with a 1-2 line summary + pointer.

Resolution / archive workflow:
- When a blocker resolves: move to `memory/archive/<YYYY-MM>.md` with verbatim
  original wording + "Why archived" reasoning. Remove from this list in the
  same commit.
- Do NOT strikethrough as soft-delete. Strikethrough is acceptable for one
  session as a "verify before archive" marker.

Aim for 3-7 blockers. Above 7 indicates the field has lost its filter (too many
"important things" tagged blocker; pick the actual top 5 that gate this week).
-->

1. **<Blocker name>** — <one-line state>. → `topics/<slug>.md` *(if it has a shard)*
2. **<Blocker name>** — <one-line state>.
3. **<Blocker name>** — <one-line state>.

> Archived <date>: <blocker> (<why>, → `memory/archive/<YYYY-MM>.md` or `memory/decisions/<...>`).

---

## Canonical facts (pointer to constitution)

<!--
Memory NEVER owns canonical facts. This section is a *pointer* to where canon
lives, plus a handful of the most-referenced facts a session-start agent needs
immediately.

If a fact gets disputed or revised → patch the constitution, not this section.
Keep this list to <15 lines. Anything longer = the agent should read the
constitution directly.
-->

Detail in `knowledge/<constitution>.md`. Top-of-mind facts:

- **<Fact category>:** <one-line claim>
- **<Fact category>:** <one-line claim>
- **<Fact category>:** <one-line claim>

---

## This week (<date range>)

<!--
Concrete deliverables, meetings, actions due in current 7-day window. Each item:
- What
- When (date if known, "by end of week" otherwise)
- Status (pending / in-progress / done-pending-archive)
- Pointer to brief / decision / shard if relevant

When an item completes: move to archive in same commit (or move to "Done this
week" sub-section if you want a roll-up for the next digest).

Typical size: 5-10 items.
-->

- **<Action / meeting>** (<date>) — <state>. → `briefs/<...>` *(if a brief exists)*
- **<Action / meeting>** (<date>) — <state>.
- **<Action / meeting>** (<date>) — <state>.

---

## On the horizon (next 2-4 weeks)

<!--
Lighter touch than "this week" — keep each item to one line. As items get
closer (within 7 days), promote to "this week". As they slip beyond 4 weeks,
either re-promote with a real date or drop to "watch list".

Typical size: 3-7 items.
-->

### t+1 to t+2 weeks

- **<Item>** — <state>
- **<Item>** — <state>

### Stakeholder profile bootstrap pending

<!--
Names that came up but don't have a profile yet. Quick triage:
- New role unclear → flag for next stakeholder session
- Active counterparty without profile → bootstrap before next interaction
-->

- **<Name>** (<context — where they appeared, likely role>)
- **<Name>** (<context>)

### Active sub-actions (no hard deadline)

<!--
Things that are progressing but not gated by a specific date. Pointers to shards.
-->

- **<Topic>** — → `topics/<slug>.md`
- **<Topic>** — → `topics/<slug>.md`

---

## Watch list (monitor, no action yet)

<!--
Things that COULD escalate. Re-evaluate each weekly. Re-evaluation triggers
(what would move this to active) should be in the relevant shard, not duplicated
here.

Typical size: 3-8 items.
-->

- **<External signal / dependency>** — <what would trigger action>
- **<External signal / dependency>** — <what would trigger action>

---

## Open questions ([TBD])

<!--
Explicit decisions waiting on a human. Each one should have:
- The question
- Who can answer it
- Why it's blocked (waiting on what)

If a question has been [TBD] for >30 days, it's not actually waiting — it's
deprioritised. Either escalate or remove.
-->

- **[TBD: <topic>]** — needs <owner> input. Blocked on <reason>.
- **[TBD: <topic>]** — needs <owner> input. Blocked on <reason>.

---

## Architectural / operating principles

<!--
Short list of binding principles for how this initiative operates. NOT canonical
(constitution owns canon), just operational reminders for the agent.

If this grows beyond ~10 items, move to constitution.
-->

- **<Principle>** — <one-line>
- **<Principle>** — <one-line>

---

## Tools & resources

<!--
Stable references — system IDs, API endpoints, tool quirks. This section is
high-utility but low-volatility. Update when something material changes (new
ID, deprecated tool), otherwise leave alone.

If a tool's quirks need >5 lines of explanation, write a separate doc in
`knowledge/tools/` and link to it from here.
-->

- **<Tool name>:** <key ID / endpoint / quirk in one line>
- **<Tool name>:** <key ID / endpoint / quirk in one line>

---

## System hygiene

<!--
Memory audit + watch scan cadence reminders. These are auto-updated by the
audit hooks (see `governance-architect` for hook implementation).

Format: last-run date + cadence + next-due date.
-->

- **Monthly memory audit** — last: YYYY-MM-DD. Next due ~YYYY-MM-DD (cadence 35d).
- **Light prune** — last: YYYY-MM-DD. Next due ~YYYY-MM-DD (cadence 14d).
- **Watch scan** — last: YYYY-MM-DD. Next due ~YYYY-MM-DD (cadence 7d).
