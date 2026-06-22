# runs/ — ephemeral run output (git-ignored)

Everything a pipeline run produces **except** the HITL queue: the triage table, per-claim scores,
and the flat claim list. It is **git-ignored on purpose** (see root `.gitignore`) — only this
README is tracked.

## Why ephemeral is a feature, not a shortcut

Scoring is a deterministic function over git + the authority matrix (PIPELINE §3). So a run's
output is **fully reproducible** by re-running against the nodes' current state — there is nothing
to preserve. Recomputing each run means:

- **Stale claims expire by themselves.** A claim that no longer matches any node anchor simply
  isn't regenerated. Nothing accumulates, nothing rots.
- **No second knowledge base.** If triage tables were committed, they'd drift from canon and
  become a competing source of truth — exactly the "memory as dumping ground" failure this layout
  avoids.

The two things that *do* survive a run: `knowledge/canon/` (gated, persisted) and
`memory/hitl-queue/` (async, persisted). Triage output is neither — it lives here and is
overwritten freely.

## Layout (per run)

```
runs/<YYYY-MM-DD-HHMM>/
├── triage-table.md      # every claim, its tier, score components, anchor (PIPELINE §4)
├── scores.yaml          # raw score breakdown per claim
└── claims.jsonl         # flat extracted claim list across all nodes (PIPELINE §2)
```

**Never hand-edit** anything under `runs/` — it is overwritten on the next run.
