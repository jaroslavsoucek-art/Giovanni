# Workflow Fitness  — OPEN DISCOVERY BRANCH

> This layer is deliberately **not** solved in MVP. Solving it by analogy to the facts layer would be
> the central mistake (P3). Documented here so it is scoped, not silently dropped.

## Why workflows are a separate layer

A workflow (a colleague's `/command`, a repeatable procedure, an agent pattern) does **not** validate by
convergence. The best workflow in the org might run on exactly one node. Counting adopters rewards the
*most common* practice, not the *best* one. So:

- Facts → aggregated by **convergence** (democracy of sources).
- Workflows → aggregated by **fitness** (meritocracy of results).
- Same machine for both = mediocrity by averaging.

Workflows have a *link* to how facts are created (a good decision-workflow produces well-anchored
decisions) but are **decoupled** from fact content. Boss judges the procedure, not what it produced once.

## The open question (to be discovered, not guessed)

How does Boss tell a *functional workflow wired to the whole* from a *local hack*? Candidate fitness
signals — to be validated, not assumed:

- **Reuse across nodes** — adopted/forked by another node (weak signal; popularity ≠ quality, but non-zero).
- **Gate pass rate** — does its output clear a real gate (review, deliverable QA, merged PR)?
- **Wiring to shared artifacts** — does it have explicit input/output edges to org-shared things, or is
  it self-contained and local?
- **Outcome traceability** — can you trace a good outcome back to this workflow running?

## What MVP does instead

Nothing automated. Boss **catalogs** declared workflows per node (`layout.workflows`) into
`workflows/registry.yaml` with their declared purpose and observed reuse — a directory, not a ranking.
Fitness scoring is the next discovery branch after the facts pipeline proves out.

## Registry

→ `workflows/registry.yaml` (catalog only; no fitness score in MVP)
