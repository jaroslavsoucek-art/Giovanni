# HITL queue — open contested/escalate items awaiting an oracle

The **one** run artifact that persists in `memory/`. Everything else a run produces (triage
tables, scores, claim lists) is ephemeral and recomputed (`runs/`, git-ignored). This queue
persists because resolution is **asynchronous** — a contested claim waits days or weeks for a
batched oracle session (PIPELINE §6), so it cannot live in a per-run scratch.

## What lands here

- `contested` claims (two quality nodes assert the opposite) — the highest-value output (P5).
- `ESCALATE` verdicts from the adversarial pass (PIPELINE §5).

Each item is routed to a proposed **oracle** = the domain owner from
`governance/authority-matrix.yaml`.

## Item shape

One file per item, `hitl-queue/<YYYY-MM-DD>-<slug>.md`:

```yaml
id: <slug>
opened: YYYY-MM-DD
domain: <authority-matrix domain>
oracle: <proposed owner from authority-matrix.yaml>
blocks: <what material decision this is holding up, if any>
sides:                      # for a contested pair, steelman each
  - node: <node>
    claim: <statement>
    anchor: <gen-0 ref>
  - node: <node>
    claim: <opposite statement>
    anchor: <gen-0 ref>
status: open | resolved | dropped
```

## Lifecycle

- **open** → waits for an oracle session.
- **resolved** → if the oracle PROMOTEs (grounded on an external referent, not a nod at Boss's
  summary — P4), a canon patch is drafted, a human approves, and the entry is born in
  `knowledge/canon/`. The queue item is then removed (its outcome lives in canon + git history).
- **dropped** → oracle rejects or the claim goes stale; removed, no canon entry.

A resolved/dropped item leaves no residue here — the queue holds *open* work only. Its history is
in git.

_(empty — no registered sources yet)_
