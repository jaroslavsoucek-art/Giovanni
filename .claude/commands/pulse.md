---
description: Weekly read of what is actually getting built or done, per work-block — from the tracker, the code, and the docs. State of the work, not the stream of events. Distinct from the digest, which is signal since the last run.
allowed-tools: Task, Bash, Read, Glob, Grep, Write
---

# /pulse

**The digest answers "what happened since yesterday". Pulse answers "where does each piece of work actually stand".**

Those come apart faster than anyone expects. The digest is an event stream: it is excellent at surprises and blind to silence. A work-block with no messages, no tickets moved and no meetings looks identical in a digest to a work-block that does not exist — and the second-most-common failure in a delivery-shaped domain is discovering that something has been quietly stalled for five weeks, in a channel nobody posts to.

Pulse reads **state**, not events, and reads it from where the work actually leaves traces — which is usually not the tracker.

## Usage

```
/pulse                                 # default — all work-blocks, since last pulse
/pulse since=<YYYY-MM-DD>              # explicit window
/pulse block=<slug>                    # single work-block
/pulse quick                           # counts and deltas only, no narrative
```

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `since=<date>` | parameterized date | last pulse (from `memory/pulse/_state.md`) | Lower bound of the window |
| `block=<slug>` | parameterized string | all | Restrict to one work-block |
| `quick` | boolean flag | off | Deltas only — skip per-block narrative |

## Work-blocks

A **work-block** is a unit of work the principal tracks as one thing: a workstream, an epic, a market, a product area. Defined per fork in the pulse config (`memory/pulse/_blocks.yaml` or equivalent) — slug, owner, where its traces live.

Blocks, not people and not tickets. Tickets are too granular to show a trend; people cut across blocks; and the question being asked is "is this piece of work moving", which is a property of the work.

## Sources — code over tracker

Order matters, and it is the opposite of the intuitive one:

1. **The repository.** Commits, merged changes, and which paths they touch. Code is the only source that cannot be optimistic — a merged change is work that exists.
2. **The tracker.** Status transitions in the window, and their absence. A ticket that moved "in progress" three weeks ago and has not moved since is the signal; the board view hides exactly this.
3. **Documents.** New or materially edited specs, decisions, plans.
4. **Everything else** — only as corroboration.

The tracker is a **claim** about the work. The repository is **evidence** of it. When they disagree, say so explicitly in the output rather than reconciling silently: the disagreement is usually the most useful line in the whole run.

## Pre-flight (STOP on failure)

- Pulse config exists and lists at least one block. Absent → stop and say so; there is nothing to read.
- The repository is fetched, not a stale local clone. **A stale clone reports zero commits, and zero commits from an unfetched clone is indistinguishable from a genuine zero** — it renders as "no activity" for work that shipped. Fetch first, or state that you could not.

## Output

`memory/pulse/<YYYY-MM-DD>.md`, plus a short chat summary. Per block:

- **Moving / slow / stalled / blocked** — with what the verdict rests on
- **Evidence** — commits (with SHAs), transitions, documents. No verdict without evidence.
- **Delta since last pulse** — including blocks that were moving and are not
- **Work found outside the tracked blocks** — the interesting part; work happening in places nobody registered

State to `memory/pulse/_state.md`. Commit as `docs(pulse):`.

## What this is not

- **Not a status report for others.** No audience but the principal. Status reporting is somebody's job and this is not that artifact — writing it as one turns "stalled" into "progressing well".
- **Not delivery management.** Pulse observes; it does not chase, assign, or escalate.
- **Not part of the digest.** Different cadence, different question. Running it daily produces noise: work-state moves on a weekly clock.
