# Giovanni Agent Roster

Three agents, mirroring the node-level pattern (isolated context, main thread orchestrates). Each maps
to pipeline stages and obeys the Constitution.

| Agent | Stages | Job | Must obey |
|---|---|---|---|
| `giovanni-aggregator` | 1–2 ingest + extract | Pull each node WITH history, decompose into anchored claims. Read-only over nodes (P4). Public-only unless scoped (P6). | P1 anchors, P6 access |
| `giovanni-triage` | 4, 6 | Bucket claims into tiers; emit HITL queue routed via authority-matrix. | P3 layer split, P5 disagreement-as-product |
| `giovanni-adversarial` | 5 | Red-team every promotion candidate + contested pair. PROMOTE/HOLD/ESCALATE/KILL. Critical by default. | P7 adversarial, P1 false-convergence check |

Scoring (stage 3) is deterministic (git + matrix) — a script, not an agent.

## Orchestration

```
aggregator (per node, parallel fan-out)  →  scorer (deterministic)  →  triage  →  adversarial  →  HITL queue
```

- **Parallel fan-out:** one `giovanni-aggregator` per node in a single batch (mirrors NEO digest Step 4).
- **No auto-handoff between agents.** Main thread orchestrates; no agent writes canon (P4).
- **No agent writes back into a node, ever** (P4). Canon drafts are human-approved at the `update-canon` gate.

## Not yet built
- Workflow fitness agent — blocked on `workflows/WORKFLOW_FITNESS.md` discovery.
