# Boss Knowledge Layer — the earned org canon

Knowledge is Boss's **canonical state**: the emergent, confidence-ranked org canon, and the one
thing Boss treats as authoritative when memory and knowledge disagree. It is the node-level
`knowledge/` rule applied one level up — *knowledge is the source of truth; memory is volatile;
memory is never canonical.*

But there is one inversion from the node, and it is the entire reason a human gate exists:

> **A node's principal writes `knowledge/` directly — that is their authority.**
> **Boss writes `knowledge/canon/` NEVER directly.** Canon is an *output*, not an input (P0);
> Boss *proposes*, a human *decides* (P4). On a node, the canonical layer is freely authored;
> on Boss, it is the one layer where every write is gated. The split mirrors the node; the
> write-authority is its opposite.

So Boss's knowledge layer is **write-only-through-the-gate**. There is no "just add a fact" path.

---

## Layer contract

| Path | Status | Written by |
|---|---|---|
| `knowledge/canon/_index.md` | Index of every canon entry. Indexed, not narrated. | the `update-canon` gate (regen on approval) |
| `knowledge/canon/<entry>.md` | One canonical claim + permanent provenance. | the `update-canon` gate only |

Note `CONSTITUTION.md` lives at the repo root, **not** here. That is deliberate: the constitution
is Boss's *self-governance* (how Boss operates — P0–P8), whereas `knowledge/canon/` is the
*derived org canon* (what the org actually believes, earned from node convergence). A node folds
its constitution into `knowledge/`; Boss keeps the two apart because one is authored and one is
earned.

## The write gate (`update-canon`) — binding sequence

A claim reaches `knowledge/canon/` only after **all** of:

1. **Triage** marks it `canon-ready` (high corroboration **+** gen-0 anchor) — PIPELINE §4.
2. **Adversarial pass** returns PROMOTE, not HOLD/ESCALATE/KILL — PIPELINE §5 (P7).
3. **Oracle resolution** by the domain owner from `governance/authority-matrix.yaml`, grounded on
   an **external referent** — *not* a nod at Boss's own summary (P4 principal-as-oracle guard).
4. **Human approves the canon patch.** Boss drafts; it never auto-commits (P4).

> **That is the moment canon is born that did not exist before.** Before that moment a claim is
> at most `likely`/`contested` and lives in `runs/` (ephemeral) or `memory/hitl-queue/` (awaiting
> an oracle) — never here.

## Entry schema

```yaml
id: <slug>
statement: <the canonical claim>
tier: canon-ready
domain: <authority-matrix domain>
nodes: [<node>, ...]          # which nodes asserted it
anchors: [<commit|file:line|permalink>, ...]   # gen-0, verbatim from origin
oracle: <who resolved it, if it came via HITL>
last_grounded: YYYY-MM-DD
status: live | unverified | superseded
```

## Provenance is permanent and live (P8)

Every entry keeps back-pointers to the nodes + anchors it came from. When a node later commits a
change to a cited anchor, Boss **re-opens** the dependent entry (marks it `unverified`, drops it
from `canon-ready` until re-grounded). Canon is living, not frozen — drift is detected, not
accumulated.

## What does NOT belong here

| Not canon | Lives in |
|---|---|
| Contested/escalate item awaiting an oracle | `memory/hitl-queue/` |
| Triage table / scores / claim list from a run | `runs/` (git-ignored) |
| Boss's own run-state, cadence, last digest | `memory/` |
| Any node's live operational state | the node (P3 — never aggregated) |

See [`../memory/README.md`](../memory/README.md) for the read/write doctrine and the full
classification rule.
