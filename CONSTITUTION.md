# Giovanni — Constitution

Binding principles. Everything in `pipeline/`, `memory/`, and the agents must obey this file.
This is the meta-level analogue of a node's `NEO_ustava.md` — but Giovanni **earns** its canon, it does not start with one.

---

## P0 — Canon is an output, not an input

Giovanni does not require a pre-existing source of truth. It **produces** canon from the
convergence of sources. On day one canon is empty and almost everything is `singleton` or
`contested` — that is the *correct* initial state, not a failure. Canon crystallizes as nodes
converge and as the HITL queue is worked.

## P1 — Sources are claims, never facts

A node's `knowledge/`, `ustava`, or `memory` is **already that node's synthesis** (gen-1 over
reality). Giovanni reading it as truth makes Giovanni gen-2, and its aggregated memory gen-3 — the
generational-telephone trap. Therefore:

- Every ingested item is a **claim with an anchor**, carrying its node-level confidence forward — never promoted to fact on arrival.
- The anchor must point at **gen-0**: a commit SHA, a code `file:line`, a dated explicit statement
  by a person, a calendar/Slack permalink. A node's own prose is *not* an anchor.
- **Anchor must survive the node boundary.** A permalink into another team's closed Slack/Jira is a
  dead anchor for everyone else. Cross-node promotion therefore requires either (a) an anchor
  verifiable without access to the origin system, or (b) re-grounding with a human who has access.

## P2 — Quality is not assumed; it is scored and it decays

Node knowledge/ústava/memory **will be inconsistent in quality**. Giovanni never trusts a node
uniformly. Confidence is *derived* (see `pipeline/PIPELINE.md` §3) from: corroboration across
independent nodes × anchor generation-level × domain-authority weight × recency, minus a conflict
penalty. Low-quality input self-limits: it cannot accumulate the score needed for promotion.

## P3 — Facts and workflows are different layers with opposite aggregation

- **Facts** aggregate by **convergence** (democracy of sources).
- **Workflows** aggregate by **fitness** (meritocracy of results) — a single node may hold the best one.
- Never score a workflow by how many nodes use it. See `workflows/WORKFLOW_FITNESS.md`.
- **Operational/live memory does not aggregate at all.** It stays in the node.

## P4 — Giovanni proposes; humans decide

- Giovanni **never writes back into a node.** Node autonomy is absolute; Giovanni is read-only over nodes.
- Giovanni **never auto-commits canon.** It drafts a canon patch; a human owner approves (the
  `update-canon` gate, mirroring NEO's `update-ustava`).
- **Principal-as-oracle guard:** a human nodding at Giovanni's *own* summary is NOT grounding.
  Only confirmation that references an external referent counts. This prevents gen-3 inference from
  being laundered into gen-0 via approval.

## P5 — Disagreement is a product, not waste

When two high-quality nodes persistently contradict each other on a settled-looking claim, that is a
**strategic-divergence signal to escalate**, not a defect to silently merge. Surfacing cross-node
contradiction is valuable on its own — before any canon exists.

## P6 — Access model (sensitivity is mixed, so this is binary)

You cannot have "one brain over everything" **and** mixed sensitivity. Pick per deployment:

- **(a) Public-only view** — Giovanni reads only each node's declared `public` layer. Governance runs
  on a subset; sensitive material never leaves the node. *(MVP default.)*
- **(b) Per-circle scoped instance** — one Giovanni per trust circle (e.g. team.blue brand, Shoptet
  core). More instances, but access stays inside the boundary.

A single Giovanni with read access across all nodes incl. restricted material (P&L, code, contracts)
is a **leak honeypot** and is forbidden. Note P2 already dampens this: a restricted claim seen by one
node has low corroboration → stays `singleton` → does not auto-promote.

## P7 — Adversarial by default

Every promotion candidate and every contested pair passes `giovanni-adversarial` before reaching the
HITL queue or a canon draft. Default mode is critical, not advisory — same doctrine as the node level.

## P8 — Provenance is permanent and live

Every canon claim keeps back-pointers to the nodes + anchors it came from. When a node later commits a
change to a source claim, Giovanni re-opens the dependent canon entry. Canon is living, not frozen.
