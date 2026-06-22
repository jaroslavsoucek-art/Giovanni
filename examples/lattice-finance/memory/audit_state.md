# Audit state — memory-hygiene cadence

<!--
============================================================================
Lattice Finance fork — memory-hygiene cadence tracker.

Seeds the recurring memory-maintenance loop. The session-start hook reads the
"next due" dates here and surfaces a reminder when a cadence is overdue. Each
audit / prune / scan updates its "last" date (and recomputes "next due") when
it runs.

Cadences (defaults from docs/governance.config.yaml):
- Monthly memory audit  — full L1/L2 review, archive resolved shards.  35d
- Light prune           — trim stale "this week" / watch-list entries.  14d
- Watch scan            — re-check watch-list items for movement.        7d

Same shape as the "System hygiene" section of an operational-memory L1.
============================================================================
-->

## System hygiene

- **Monthly memory audit** — last: 2026-06-08. Next due ~2026-07-13 (cadence 35d).
- **Light prune** — last: 2026-06-16. Next due ~2026-06-30 (cadence 14d).
- **Watch scan** — last: 2026-06-15. Next due ~2026-06-22 (cadence 7d).
