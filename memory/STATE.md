# STATE — Boss run-state shortcut

> Boss's own volatile run-state — NOT canon. Thin pointer **to** the knowledge layer, never a
> copy of it. Node operational state does NOT belong here (see [README §"what NOT"](README.md)).
> Hard ceiling: warn >300 lines, stop-and-audit >400.

## Status
- Phase: **scaffold / pre-MVP**. Canon is empty — correct initial state (P0).
- Registered sources: 0 (see `sources/registry.yaml`).

## This cycle
- Awaiting first 3 nodes to onboard via SOURCE_CONTRACT.

## Pointers
- Canon (the knowledge layer) → `../knowledge/canon/_index.md` (empty until first HITL resolution)
- HITL queue (open items awaiting an oracle) → `hitl-queue/` (empty)
- Cadence / audit state → `audit_state.md`
- Last run's ephemeral output → `runs/` (git-ignored; recomputed each run)

## Open discovery branches
- Workflow fitness signal still undefined → `workflows/WORKFLOW_FITNESS.md`.
- Authority matrix seeded from NEO only → needs org-wide extension as nodes join.
