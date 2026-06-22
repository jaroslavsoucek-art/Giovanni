# Source Contract

What a node (a colleague's AI setup) must expose to be a valid Giovanni source.

The point of this contract is **normalization despite inconsistent quality**. Nodes will differ wildly
in how mature their knowledge/ústava/memory is. Giovanni does not demand they be good — it demands they
be **declared, anchored, and classified**, so the scorer can do the rest.

A node does *not* rewrite how it works. It adds one manifest + follows three rules.

---

## 1. The manifest (`manifest.yaml`)

Each node publishes a `manifest.yaml` (template in `_template/`). It declares:

```yaml
node: <slug>                      # unique, e.g. shoptet-neo
owner: <person>                   # accountable human
read:
  type: git                       # git | api | export
  url: <repo or endpoint>         # must expose HISTORY, not just a snapshot
  ref: main                       # default branch to read
visibility_default: restricted    # restricted | public  — see rule R2
layout:                           # where Giovanni finds each layer (paths are node-relative)
  knowledge: knowledge/           # canonical docs
  decisions: memory/decisions/    # decision records (the "how & why")
  memory:    memory/              # operational + topic memory
  changelog: CHANGELOG.md         # optional but recommended
  workflows: .claude/workflows/   # workflow definitions (separate layer)
domains: [expansion, pricing]     # which authority-matrix domains this node speaks to
anchor_resolvable_externally: false  # true only if anchors verify without origin-system access
```

## 2. Three rules a node must follow

**R1 — History is preserved.** Giovanni reads *into* the changelog and decision records to learn how &
why a decision was made. A node that squashes/rewrites history or only emits a flat snapshot is **not a
valid source** — it is a dead end. (Shallow clones must be `--unshallow`-able.)

**R2 — Visibility is opt-IN to sharing, declared at the claim level where it matters.**
Default is `restricted`. A node marks something `public` *actively*. This is the inverse of "export
what feels important" — that is opt-out of sensitivity and it leaks. For granular control, a claim may
carry an inline marker:

```
[GIOVANNI: public]      ← this line/section is shareable
[GIOVANNI: restricted]  ← default; Giovanni in public-only mode will not read it
```

**R3 — Claims carry anchors.** A node's canonical/decision content should already tag provenance
(NEO does: `[ODHAD]`, `[DERIVED]`, primary anchors). Giovanni reuses whatever exists. Unanchored
claims are ingestable but capped at `singleton`/`likely` — they can never reach `canon-ready`.

## 3. What Giovanni reads, per layer

| Layer | Source path | Used for | Aggregation |
|---|---|---|---|
| **Facts / knowledge** | `layout.knowledge` | claim extraction + scoring | convergence |
| **Decisions (how & why)** | `layout.decisions` + git log of knowledge files | provenance drill-down | linked, not merged |
| **Workflows** | `layout.workflows` | fitness assessment | meritocracy (separate) |
| **Operational memory** | `layout.memory` (live state) | **NOT aggregated** — context only during drill-down | none |

## 4. The minimum a colleague has to do to onboard

1. Copy `_template/manifest.yaml`, fill it in, commit to their repo root.
2. Make sure their repo history is intact and readable by Giovanni's reader.
3. Mark at least their shareable knowledge sections `[GIOVANNI: public]`.
4. Add an entry to Giovanni's `sources/registry.yaml` (PR).

That's it. No rewrite of their setup. A weak node still works — it just scores low until it improves,
which is exactly the incentive you want.

## 5. Handling inconsistent quality (the explicit requirement)

- **Missing decision records?** Claims fall back to git-log anchors; confidence is lower but non-zero.
- **No provenance tags?** Claims are capped below `canon-ready` (R3).
- **Messy/contradictory memory?** Operational layer is not aggregated anyway (P3); only knowledge +
  decisions feed canon.
- **A node lies or drifts?** Conflict penalty + adversarial pass catch it; persistent divergence
  becomes a P5 escalation, not silent corruption of canon.

Quality is never a gate to *being a source*. It is only a gate to *promotion*. Bad input cannot poison
canon because it cannot earn the score.
