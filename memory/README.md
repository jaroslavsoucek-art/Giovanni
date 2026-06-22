# Boss Memory Layer — Boss's own volatile run-state (NOT canon)

Memory is **operational state Boss needs to do a run today** — the HITL queue waiting on
oracles, cadence/audit dates, the pointer to the last digest. It is **not** the canon.

> Canon is **not** memory. Boss's earned, confidence-ranked canon lives one layer up in
> [`knowledge/canon/`](../knowledge/canon/_index.md). Memory **points at** canon; it never
> **contains** it. This is the node-level rule (`knowledge/` is canonical, `memory/` is
> volatile, *memory is never canonical*) applied one level up. Putting canon under memory
> was the original sin this layout fixes.

Boss sits over many nodes, so its memory will drift and bloat **faster** than a node's unless
it is *more* disciplined. These rules are the long-term-survival contract — the meta-level
analogue of a node's memory authoring rules + read-doctrine.

---

## The three stores (and the one that does not exist)

Boss writes to exactly three places. Knowing which is which is the whole discipline.

| Store | Path | Persisted? | Canonical? | Who writes |
|---|---|---|---|---|
| **Knowledge / canon** | `knowledge/canon/` | yes | **yes** | **only the HITL gate** (see Write doctrine) |
| **Memory / run-state** | `memory/` (this dir) | yes, but volatile | no | Boss freely, bounded by caps + cadence |
| **Ephemeral run output** | `runs/` (git-ignored) | no — recomputed each run | no | Boss; never hand-edited |
| ~~Node operational state~~ | — | **never aggregated** | — | **nobody** — it stays in the node (P3) |

**Why this split kills the "dumping ground" failure mode:** the only write that becomes
*truth* (canon) is the only write a human gates. Everything Boss writes by itself is
structurally non-canonical and disposable. As long as canon lives **outside** memory, "Boss
writes to memory freely" and "memory is never truth" stop contradicting each other.

## What `memory/` may contain (and what it must NOT)

| Content | Goes to | Note |
|---|---|---|
| Open contested/escalate items awaiting an oracle | `memory/hitl-queue/` | **persists** — resolution is async (batched oracle sessions, PIPELINE §6) |
| Cadence / audit run dates | `memory/audit_state.md` | run-state |
| Pointer to the last run's digest + canon index | `memory/STATE.md` | thin shortcut, navigation only |
| Approved canonical claim (post-HITL) | `knowledge/canon/<entry>.md` | **NOT here** — it's knowledge |
| Triage table, claim list, scores from a run | `runs/` (git-ignored) | **NOT here** — ephemeral, recomputed |
| Node operational/live state (blockers, "this week") | **NOWHERE** — stays in the node | the #1 bloat vector (P3) |

Aggregating the operational layer of dozens of nodes = thousands of lines of noise + a leak
surface. `memory/STATE.md` is a **thin pointer to canon**, not "every node's setup stacked up."

## Read doctrine (one level up) — evidence vs navigation vs bookkeeping

Boss never re-reads its own synthesis as a source. State it as a strict hierarchy of *what is
read as what*:

| Read as… | Source | Rule |
|---|---|---|
| **Evidence (gen-0)** | node anchors only: commit SHA / `file:line` / dated human statement / permalink | the *only* legitimate ground for a claim |
| **Navigation (NOT evidence)** | Boss's own `knowledge/canon/_index`, the HITL queue, the last digest | tells Boss *where it is*; never re-grounds a claim |
| **Bookkeeping (not even navigation-to-truth)** | Boss's own `memory/` run-state | never cited as a source for anything |

Consequences (binding):

1. **A run reads node anchors *since last run*, not Boss's last digest.** Generational depth
   stays ≤1 by construction.
2. **No synthesis of synthesis.** A canon entry cites the node's original anchor verbatim,
   never "as Boss summarized last cycle." The courier is never cited as the source.
3. **Principal-as-oracle guard (P4).** A human's nod at Boss's *own* summary is not grounding.
   Only confirmation referencing an **external referent** re-grounds a claim. This is the
   single rule that is both read-doctrine and write-doctrine — it stops gen-3 inference from
   being laundered into gen-0 via approval.

## Write doctrine — where writes are allowed, gated, or forbidden

The most important table in the repo for anyone validating write rights.

| Target | Who may write | Gate |
|---|---|---|
| `knowledge/canon/` | **only the HITL flow** | adversarial pass → oracle resolution (external referent) → human approves the canon patch. **Boss never auto-commits canon** (P4). |
| `memory/` (HITL queue, run-state) | Boss (aggregator) | no gate — Boss's own scratch; bounded by caps + cadence below |
| `runs/` (triage / claims / scores) | Boss | recomputed every run; **hand-editing is forbidden** |
| any node repo | **NOBODY** (P4) | read-only over nodes is absolute; forbidden, full stop |

Two re-grounding gates exist (and only these two): **(a)** promotion into canon, **(b)** shipping
anything outward. At a gate: every FACT in the diff has a primary anchor verified this cycle;
DERIVED traces to an anchor or degrades to ODHAD. Outside the gates nothing is continuously
re-verified — no token burn on claims nobody reads.

## Anti-drift rules (binding)

1. **Size pressure.** `knowledge/canon/` is indexed, not narrated — it scales by adding indexed
   entries with pointers, not by growing one file. `memory/STATE.md` has a hard ceiling — warn
   **>300 lines**, stop-and-audit **>400**.
2. **Provenance is permanent (P8).** Every canon entry stores `{ nodes, anchors, last_grounded,
   tier }`. When a node commits a change to a cited anchor, the entry auto-re-opens — drift is
   detected, not accumulated.
3. **Ephemeral by design.** Because scoring is a deterministic function over git + the authority
   matrix (PIPELINE §3), triage output is **recomputed each run**, never stored. Stale claims
   expire by themselves; nothing accumulates. The HITL queue is the *only* run artifact that
   persists, because its resolution is asynchronous.

## Classification rule — "where does this go?"

Before writing anything, classify. **Default is NOT canon, and default is NOT `memory/STATE.md`.**

| You have… | It goes to… |
|---|---|
| An approved canonical claim (survived adversarial + oracle + human approval) | `knowledge/canon/<entry>.md` |
| A contested/escalate item waiting on an oracle | `memory/hitl-queue/<id>.md` |
| A triage table / scores / claim list from this run | `runs/` (git-ignored) |
| A cadence/audit timestamp | `memory/audit_state.md` |
| Anything about a *node's* live operational state | **back off** — it stays in the node (P3) |

The "remember X" trap, one level up: when something looks worth keeping, classify before
appending. If it is not Boss's own run-state and has not passed the canon gate, it does not
belong in `memory/` **or** in `knowledge/`.

## Cadence

- **Light audit** every 14 days — prune `memory/`, size-check `STATE.md`, no full re-read.
- **Full audit** every 35 days — section by section + provenance spot-check on canon entries.
- **Stale canon** (cited anchor gone / node retired) → entry marked `unverified`, dropped from
  `canon-ready` until re-grounded.

Cadence state lives in `memory/audit_state.md` (last-run dates + thresholds).

> **Enforcement note (scaffold).** On a node, these rules are backed by hooks + lint
> (size caps, classification, MAP regen). This Boss branch has **no hooks/lint yet** —
> enforcement is currently documentary only. That is an accepted scaffold-stage debt, not a
> design choice; the rules above are written to be mechanically checkable when the hooks land.
