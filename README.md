# Giovanni

**An organization-level knowledge aggregator that treats each colleague's AI setup as a *source*, not as truth.**

Giovanni sits one level above individual "node" repos (like Shoptet NEO). It reads
their knowledge, decisions, and memory as raw sources, applies a governance layer
(scoring → triage → adversarial → HITL), and **produces** an emergent, confidence-ranked
canon — rather than assuming one exists.

> The contents of this directory are the **root of the Giovanni repo**. They live on the
> `giovanni` branch of the shoptet-neo repo only as a scaffold/proposal. When promoted,
> copy this directory into its own repository.

---

## The core insight

Two things aggregate by **opposite logic**, so Giovanni keeps them in separate layers:

| | Facts / Knowledge | Workflows |
|---|---|---|
| Validated by | **convergence** (many nodes agree → higher confidence) | **fitness** (does it produce good outcomes, is it wired to the whole?) |
| Aggregation | democracy of sources | meritocracy of results — *one* node can hold the best workflow |
| Danger if mixed | — | averaging workflows yields mediocrity, not best practice |

Operational/live memory (current state, blockers) **does not aggregate at all** — it stays in the node.

## What Giovanni is NOT

- **Not a meta-assistant that swallows other assistants' output.** It reads *anchors* (gen-0:
  commit / explicit statement / code), not other nodes' prose. Reading synthesis as fact is the
  generational-telephone trap (NEO read-doctrine, one level up).
- **Not a single brain over everything.** Sensitivity is mixed; see `CONSTITUTION.md` §3 access model.
- **Not an auto-writer.** Giovanni *proposes*; humans *decide*. Canon promotion is gated.

## MVP scope (what the first build actually does)

Three nodes, **public layer only**. Giovanni does exactly two things:

1. **Ingest → extract claims with anchors → score → triage** into a single table:
   `canon-ready / likely / contested / singleton`.
2. **Emit a HITL queue** of contested claims, each routed to a proposed oracle (domain owner).

Success test: if the first run surfaces **one** contested claim where two teams unknowingly
contradict each other → proof of value. If it surfaces nothing interesting → you saved yourself a platform.

Explicitly **out** of MVP: auto-write to canon, org-constitution, ACL machinery, workflow fitness
scoring (that is its own discovery branch — see `workflows/WORKFLOW_FITNESS.md`).

## Layout

```
giovanni/
├── README.md                      ← this file
├── CONSTITUTION.md                ← binding meta-principles (read-only, propose-not-write, access model)
├── governance/
│   └── authority-matrix.yaml      ← domain → owner (drives authority weight + HITL routing)
├── sources/
│   ├── SOURCE_CONTRACT.md         ← what a node must expose to be a valid source
│   ├── _template/manifest.yaml    ← copy-and-fill template for a colleague
│   └── registry.yaml              ← registered nodes
├── pipeline/
│   └── PIPELINE.md                ← the 6 stages: ingest → extract → score → triage → adversarial → HITL
├── memory/
│   ├── META_MEMORY.md             ← aggregated canon/decision/fitness ONLY (anti-drift)
│   ├── MEMORY_RULES.md            ← read-doctrine + size pressure, one level up
│   └── canon/_index.md            ← emergent canon index
├── workflows/
│   └── WORKFLOW_FITNESS.md        ← how workflows are judged (fitness, not convergence) — open discovery branch
└── .claude/agents/ROSTER.md       ← giovanni-aggregator / giovanni-adversarial / giovanni-triage
```

## How a run works (operator's view)

1. `sources/registry.yaml` lists nodes + their public read endpoints.
2. `giovanni-aggregator` pulls each node **with history** (git log + decision records + memory),
   not a flat snapshot — so it can drill to the changelog to learn *how & why* a decision was made.
3. Claims are extracted with their anchor; confidence is **derived** from git metadata + the
   authority matrix (no new ML — see `pipeline/PIPELINE.md` §3).
4. `giovanni-triage` buckets claims into tiers.
5. `giovanni-adversarial` red-teams every promotion candidate and every contested pair.
6. Output: a triage table + a HITL queue. Humans resolve; only then does anything reach canon.
