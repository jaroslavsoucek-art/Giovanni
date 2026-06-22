# Boss

**An organization-level knowledge aggregator that treats each colleague's *Giovanni* as a *source*, not as truth.**

Boss sits one level above individual **Giovanni** nodes — each person's own AI Chief
of Staff (see the [`main`](https://github.com/jaroslavsoucek-art/Giovanni/tree/main)
branch). It reads their knowledge, decisions, and memory as raw sources, applies a
governance layer (scoring → triage → adversarial → HITL), and **produces** an emergent,
confidence-ranked org canon — rather than assuming one exists.

> **Giovanni is the node; Boss is the network.** `main` is Giovanni (the generic,
> per-person assistant anyone can run); this `Giovanni-Boss` branch is Boss (the
> aggregator over many Giovanni nodes). The two are deliberately separate layers.

---

## The core insight

Two things aggregate by **opposite logic**, so Boss keeps them in separate layers:

| | Facts / Knowledge | Workflows |
|---|---|---|
| Validated by | **convergence** (many Giovanni nodes agree → higher confidence) | **fitness** (does it produce good outcomes, is it wired to the whole?) |
| Aggregation | democracy of sources | meritocracy of results — *one* node can hold the best workflow |
| Danger if mixed | — | averaging workflows yields mediocrity, not best practice |

Operational/live memory (current state, blockers) **does not aggregate at all** — it stays in the node's Giovanni.

## What Boss is NOT

- **Not a meta-assistant that swallows other assistants' output.** It reads *anchors* (gen-0:
  commit / explicit statement / code), not other nodes' prose. Reading synthesis as fact is the
  generational-telephone trap (one level up from the node's own read-doctrine).
- **Not a single brain over everything.** Sensitivity is mixed; see `CONSTITUTION.md` §3 access model.
- **Not an auto-writer.** Boss *proposes*; humans *decide*. Canon promotion is gated.

## MVP scope (what the first build actually does)

Three Giovanni nodes, **public layer only**. Boss does exactly two things:

1. **Ingest → extract claims with anchors → score → triage** into a single table:
   `canon-ready / likely / contested / singleton`.
2. **Emit a HITL queue** of contested claims, each routed to a proposed oracle (domain owner).

Success test: if the first run surfaces **one** contested claim where two teams unknowingly
contradict each other → proof of value. If it surfaces nothing interesting → you saved yourself a platform.

Explicitly **out** of MVP: auto-write to canon, org-constitution, ACL machinery, workflow fitness
scoring (that is its own discovery branch — see `workflows/WORKFLOW_FITNESS.md`).

## Layout

```
boss/  (this branch)
├── README.md                      ← this file
├── CONSTITUTION.md                ← binding meta-principles (read-only, propose-not-write, access model)
├── governance/
│   └── authority-matrix.yaml      ← domain → owner (drives authority weight + HITL routing)
├── sources/
│   ├── SOURCE_CONTRACT.md         ← what a Giovanni node must expose to be a valid source
│   ├── _template/manifest.yaml    ← copy-and-fill template for a colleague's node
│   └── registry.yaml              ← registered Giovanni nodes
├── pipeline/
│   └── PIPELINE.md                ← the 6 stages: ingest → extract → score → triage → adversarial → HITL
├── knowledge/                     ← Boss's CANONICAL layer — the earned org canon (peer of memory/)
│   ├── README.md                  ← layer contract + update-canon write gate
│   └── canon/_index.md            ← emergent canon index (written only through the gate)
├── memory/                        ← Boss's own VOLATILE run-state — never canonical
│   ├── README.md                  ← read + write doctrine, storage rules, anti-drift
│   ├── STATE.md                   ← run-state shortcut (thin pointer to canon)
│   ├── hitl-queue/                ← open contested/escalate items awaiting an oracle (persists)
│   └── audit_state.md             ← memory-hygiene cadence
├── runs/                          ← ephemeral triage output (git-ignored; recomputed each run)
├── workflows/
│   └── WORKFLOW_FITNESS.md        ← how workflows are judged (fitness, not convergence) — open discovery branch
└── .claude/agents/ROSTER.md       ← boss-aggregator / boss-adversarial / boss-triage
```

## How a run works (operator's view)

1. `sources/registry.yaml` lists Giovanni nodes + their public read endpoints.
2. `boss-aggregator` pulls each node **with history** (git log + decision records + memory),
   not a flat snapshot — so it can drill to the changelog to learn *how & why* a decision was made.
3. Claims are extracted with their anchor; confidence is **derived** from git metadata + the
   authority matrix (no new ML — see `pipeline/PIPELINE.md` §3).
4. `boss-triage` buckets claims into tiers.
5. `boss-adversarial` red-teams every promotion candidate and every contested pair.
6. Output: a triage table + a HITL queue. Humans resolve; only then does anything reach canon.

---

> **Naming note:** the aggregator is called **Boss** consistently across this
> branch's own docs (`CONSTITUTION.md`, `pipeline/PIPELINE.md`, `sources/*`,
> `knowledge/README.md`, `memory/{README,STATE}.md`, the agent roster). The branch *also*
> carries the **node-level Giovanni framework** files — it was scaffolded on top of
> them — and there "Giovanni" correctly means the individual per-person assistant
> that Boss aggregates, so it is left unchanged.
