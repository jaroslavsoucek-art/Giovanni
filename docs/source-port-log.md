# Source port log

Giovanni is distilled from a live implementation (`scripts/source-path.sh`). The source keeps learning — mostly from incidents — and the generic half of each lesson belongs here. This file records **where each port started and stopped**, so the next one is a `git log` range instead of an archaeology project.

One row per port. `Source at` is the source HEAD the port was taken against; that is the lower bound of the next window.

| Port date | Source at | Window ported | Giovanni commits | Notes |
|---|---|---|---|---|
| 2026-09-11 | `e270f19` | source `2026-06-22` → `e270f19` (58 apparatus commits, ~24 portable) | `bca721e` → `f724e5c` | First port after the framework ran three months behind a frozen snapshot. Also replaced the snapshot with live read-only access, which is what made the gap visible. |
| 2026-10-16 | `ba21b61` | source `e270f19` → `ba21b61` (160 apparatus commits; ~20 of them a hosted dashboard, out of scope) | see `git log --grep 'source-port 2026-10-16'` | **Partial.** Ported: six defects the framework still carried (digest window gap, cwd-relative hook paths, swallowed lint exit code, `set -u` in the env loader, index regen bypassed by non-editor edits, shadow-review date never written) + read doctrine for working state + rules register + lane honesty. The rest of the window was evaluated and is listed below under *Open*. The next port takes the *Open* list first, then `ba21b61..HEAD`. |

## Open — evaluated, portable, not yet ported

From the 2026-10-16 window. Each row names the source commit to read before porting. Delete a row in the commit that ports it.

| Item | Source | Note |
|---|---|---|
| Calibration integrity: a source that was blind during a hypothesis window cannot turn its silence into "did not happen" (void, condition not met). The source also reversed "matched with caveat counts as matched". | `64a35b6`, `fe86db2` | The caveat reversal contradicts `prediction-runtime.md` today. Read the source decision before porting it: a policy flip made on one principal's calibration data may be taste, not mechanism. |
| Shadow generation cadence as a knob (monthly once daily volume stopped earning; lookback stays per run) | `2beaed8` | Port as a knob with the criterion for turning it, not as a new default. A new fork needs volume to calibrate at all. |
| Adversarial review pass 5: leakage + hidden ask, for drafts that have a recipient | `14e7939` | |
| Stakeholder trajectory cap (10 entries; overflow moves verbatim to `_history/`) | `ff2d498` | Profiles are append-only today with no cap. |
| Rules for an unattended scheduled run (allow-list of reads + named memory paths; commit, push and external writes stay gated) | `1977c1b` | |
| Asks carry state across runs (`## Open asks`: first seen, times asked), so an aging rule has something to age | `b27d728` | |
| Plan-compression drift: start slipped later and further than the end, a gate passed its start date, a dependency is late | `656bf69` | Tracker-specific script in the source; the heuristic is generic. |
| One informed confirmation over an enumerated write set (narrow amendment of the per-action gate), duplicate check before a write that cannot be deleted, and never writing to an artifact another role owns, even when it is assigned to the principal | `518fa01`, `d020b4a` | |
| README ↔ operating surface lint (every workflow, command and skill named in the README) | `b4c532d` | |
| Uncertainty = a question with 2–4 named options and a recommendation; non-trivial ad-hoc work starts with done criteria | `41d2f89`, `a1eeac3` | Two one-line rules + register entries. |
| Context hygiene: MAP lists the N newest briefs + a count; a per-note byte cap inside the digest state; draft deliverables older than 30 d become superseded at light audit (manual, not lint); prompt audit after a model change | `cb2c87d`, `13e042b`, `882a248`, `e2453c8` | |
| Verification routing: before an estimate, query the authoritative knowledge base; content without its own date is cited by index date, never as "current" | `5cfb307` | Mechanism only; the wiring is domain. |
| Interview and respondent data lives outside the repo and its mirrors; only de-identified insights enter | `ba0d219` | |

**Wait before porting** (younger than a month in the source, or not yet evaluated there): principal growth loop (`349e6e3`) · hypothesis register where evidence is appended only by script and status changed only by a human (`93ee9aa`) · tripwire that marks a derived analysis stale when the canon it was computed against changes (`a5c147e`) · one-thought-per-sentence style for asks and drift (`16228ee`, the source's own one-week evaluation pending) · token usage report + session anatomy from local transcripts (`663edcf`, `dd936bd`, `1b54b8c`; harness-specific tooling).

## Why this file exists

The porting rule says "cite the source commit in the commit message", and the commit that introduced that rule did not cite one. That is the honest version of why a log is needed: a convention that lives only in commit messages is one forgotten commit away from being unrecoverable, and the recovery cost is re-deriving three months of history by hand.

## Deliberately not ported

Recorded so the next port does not re-litigate them. These are decisions, not backlog.

| Item | Why not |
|---|---|
| Code-claim anchors (every claim derived from a code repo carries the commit it was verified against, and its age) | Portable in principle, but needs a per-fork registry of anchored claims. That is a feature, not a port — revisit when a fork actually has claims rotting against a codebase. |
| Domain drift checks (roadmap membership audit, wiki discovery ledger, wiki comment layer) | Each is a good idea welded to one organisation's tooling. The generic residue — "watch the layer nobody reads" — is already in the outbound published-pages check. |
| Mirrored upstream skill library + its sync cadence | Entirely specific to a fork that mirrors another repo's skills. |
| Domain content of every kind: markets, vendors, named systems, compliance maps, pricing | Out of scope by construction. See `docs/origin.md`. |
| Private dashboard on a hosted page runtime (queue that starts a session, commit-trailer reconciliation, repo state sync) | Bound to one vendor's page runtime and to the source's domain. The generic residue, "a commit trailer closes the ask it resolves", is worth a line if a fork ever builds a dashboard. |
| A ticket-writing chain on a specific tracker and wiki | Domain tooling. Its generic part (one informed confirmation, duplicate check before an undeletable write) is in *Open*. |
| Session naming and sidebar grouping in a desktop app | Harness-specific. |

## How to run a port

1. `git -C "$(bash scripts/source-path.sh)" log --oneline <last source SHA>..HEAD -- .claude/ scripts/ CLAUDE.md`
2. Split **mechanism** (a rule, a gate, a cadence, a failure mode) from **domain** (a vendor, a market, a named system). Roughly a third is portable.
3. Port the mechanism **with its incident attached**. A rule with no story behind it gets relaxed by the first person who finds it inconvenient.
4. Add a row here, and cite the source SHA in the commit message.
