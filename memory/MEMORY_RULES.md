# Memory Rules (one level up)

Boss's own memory will drift and bloat over time **unless** it is more disciplined than a node's,
because it sits over many nodes. These rules are the long-term-survival contract. They are the
meta-level analogue of NEO's memory authoring rules + read-doctrine.

---

## What META_MEMORY may contain (and what it must NOT)

| Layer | Aggregate into META_MEMORY? |
|---|---|
| Facts / canon (post-HITL, approved) | **Yes** → `memory/canon/` |
| Decisions (how & why, as links) | **Yes, as back-pointers** — not copied prose |
| Workflow fitness verdicts | **Yes** (summary only) |
| Node operational / live state (blockers, "this week") | **NO — never.** This is the #1 bloat vector. |

Aggregating the operational layer of dozens of nodes = thousands of lines of noise + a leak surface.
META_MEMORY is a **thin layer over canon**, not "every node's setup stacked up."

## Anti-drift rules (binding)

1. **Read-doctrine, one level up.** META_MEMORY is navigation, not evidence. Boss never re-reads its
   own prior synthesis as a source. A run reads *node anchors since last run*, not Boss's last digest.
   Generational depth stays ≤1 by construction.

2. **No synthesis of synthesis.** A canon entry cites the **node's original anchor verbatim**, never
   "as Boss summarized last cycle." Courier is never cited as source.

3. **Size pressure.** `memory/canon/` is indexed, not narrated. META_MEMORY.md (the live operational
   shortcut) has a hard ceiling — warn >300 lines, stop-and-audit >400. Canon scales by adding indexed
   entries with pointers, not by growing one file.

4. **Provenance is permanent (P8).** Every canon entry stores `{ nodes, anchors, last_grounded, tier }`.
   When a node commits a change to a cited anchor, the entry is auto-re-opened — drift is detected, not
   accumulated.

5. **Two re-grounding gates.** (a) promotion into canon (`update-canon`), (b) shipping anything outward.
   At a gate: every FACT in the diff has a primary anchor verified this cycle; DERIVED traces to an
   anchor or degrades to ODHAD. Outside the gates nothing is continuously re-verified (no token burn on
   claims nobody reads).

6. **Principal-as-oracle guard (P4).** A human's nod at Boss's own summary is not grounding. Only
   confirmation referencing an external referent re-grounds a claim.

## Cadence

- **Light audit** every 14 days — prune, size check, no full re-read.
- **Full audit** every 35 days — section by section + provenance spot-check on canon entries.
- **Stale canon** (cited anchor gone / node retired) → entry marked `unverified`, dropped from
  `canon-ready` until re-grounded.
