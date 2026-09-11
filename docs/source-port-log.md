# Source port log

Giovanni is distilled from a live implementation (`scripts/source-path.sh`). The source keeps learning — mostly from incidents — and the generic half of each lesson belongs here. This file records **where each port started and stopped**, so the next one is a `git log` range instead of an archaeology project.

One row per port. `Source at` is the source HEAD the port was taken against; that is the lower bound of the next window.

| Port date | Source at | Window ported | Giovanni commits | Notes |
|---|---|---|---|---|
| 2026-09-11 | `e270f19` | source `2026-06-22` → `e270f19` (58 apparatus commits, ~24 portable) | `bca721e` → `f724e5c` | First port after the framework ran three months behind a frozen snapshot. Also replaced the snapshot with live read-only access, which is what made the gap visible. |

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

## How to run a port

1. `git -C "$(bash scripts/source-path.sh)" log --oneline <last source SHA>..HEAD -- .claude/ scripts/ CLAUDE.md`
2. Split **mechanism** (a rule, a gate, a cadence, a failure mode) from **domain** (a vendor, a market, a named system). Roughly a third is portable.
3. Port the mechanism **with its incident attached**. A rule with no story behind it gets relaxed by the first person who finds it inconvenient.
4. Add a row here, and cite the source SHA in the commit message.
