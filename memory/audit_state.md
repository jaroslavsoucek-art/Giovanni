# Audit state — Boss memory hygiene cadence

Canonical record of when Boss last audited its own memory + canon. The (future) session-start
hook reads this and warns when an audit is overdue. See [README §Cadence](README.md).

```yaml
light_audit:           # prune memory/, size-check STATE.md, no full re-read
  interval_days: 14
  last_run: null       # never run — scaffold stage
full_audit:            # section-by-section + provenance spot-check on canon entries
  interval_days: 35
  last_run: null
canon_reground:        # re-verify cited anchors still live; mark stale entries unverified
  trigger: node_commit_to_cited_anchor   # event-driven (P8), not a fixed interval
  last_run: null
```

## Thresholds (mirror [README](README.md))

| Target | Warn | Stop-and-audit |
|---|---|---|
| `memory/STATE.md` length | >300 lines | >400 lines |

_Last updated 2026-06-22 — scaffold seed, no audit has run yet._
