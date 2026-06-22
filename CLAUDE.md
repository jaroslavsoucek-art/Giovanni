# Boss — Claude Code Instructions

**Boss is an organization-level knowledge aggregator.** It sits above many
individual **Giovanni** nodes (each person's own AI Chief of Staff) and treats
each node as a *source, not as truth* — reading their knowledge, decisions, and
memory, scoring where the org converges vs contradicts, and producing an
emergent, confidence-ranked org canon rather than assuming one exists.

This branch (`Giovanni-Boss`) is **Boss**. The `main` branch is **Giovanni**
(the generic, per-person assistant). They are separate layers — do not mix
them. "Giovanni is the node; Boss is the network."

## Binding principles (full text in `CONSTITUTION.md`)

- **Read-only over nodes (P4).** Boss never writes back into a node. Node autonomy is absolute.
- **Propose, don't write.** Boss drafts canon patches; a human owner approves. No auto-commit to canon.
- **Anchors, not prose.** Read gen-0 anchors (commit / explicit statement / code), never another node's synthesis as fact — that is the generational-telephone trap.
- **Disagreement is the product (P5).** Surfacing a contested claim two teams didn't know they had is the value, not noise.
- **Adversarial by default (P7).** Every promotion candidate and contested pair gets red-teamed.
- **Access model (P6).** Public-only by default; restricted material only via an explicitly scoped instance.

## Layout

- `CONSTITUTION.md` — binding meta-principles
- `pipeline/PIPELINE.md` — the 6 stages: ingest → extract → score → triage → adversarial → HITL
- `sources/` — `SOURCE_CONTRACT.md` (what a node must expose) + `registry.yaml` (registered nodes) + `_template/manifest.yaml`
- `governance/authority-matrix.yaml` — domain → owner (authority weight + HITL routing)
- `memory/` — `META_MEMORY.md` (aggregated canon/decisions only) + `MEMORY_RULES.md` + `canon/`
- `workflows/` — `WORKFLOW_FITNESS.md` (fitness, not convergence) + `registry.yaml`
- `.claude/agents/ROSTER.md` — `boss-aggregator` / `boss-triage` / `boss-adversarial`

## Working mode

Critical by default — no flattery, pushback expected. Boss's whole job is to
catch contradiction, so an aggregator that agrees with everything is broken.

## Status

Early scaffold / proposal. MVP = ingest a few Giovanni nodes (public layer) →
a triage table + a HITL queue of contested claims. Not built out.
