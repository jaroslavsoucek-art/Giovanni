# Pipeline

Six stages, run by the agent roster. Each stage has one job and hands a structured artifact to the next.

```
ingest → extract claims → score → triage → adversarial → HITL
```

---

## 1. Ingest  (`boss-aggregator`)

- For each node in `sources/registry.yaml`, pull **with history** (git log + `decisions/` + memory),
  not a flat snapshot. In public-only mode, read only `[GIOVANNI: public]` regions.
- Defensive against inconsistent quality: a node missing decision records or provenance tags is still
  ingested — it just yields lower-confidence claims downstream.
- Output: per-node raw bundle (knowledge text + decision records + git log of knowledge files).

## 2. Extract claims  (`boss-aggregator`)

- Decompose each node's knowledge into atomic **claims**. A claim =
  `{ statement, anchor, node, domain, visibility, node_confidence }`.
- `anchor` = gen-0 reference (commit SHA / `file:line` / dated statement / permalink). If only node
  prose backs it → `anchor: none` (caps the claim, see §4).
- Drill to changelog when a claim's "how & why" is needed: `git log -p` on the knowledge file gives the
  decision trail. This is the "access down to changelog" requirement, operationalized.
- Output: a flat claim list across all nodes.

## 3. Score  (derived, out-of-the-box — no new ML)

Confidence is **computed from metadata that already exists**, not stored or learned:

```
score(claim) =
      corroboration   # of INDEPENDENT nodes asserting it      (count)
    × anchor_quality  gen-0 = 1.0 | gen-1 (node-canon) = 0.6 | gen-2 (prose) = 0.3
    × authority       domain-owner node weight from authority-matrix.yaml
    × recency         git commit date decay
    − conflict_penalty if another node asserts the opposite
```

Every input is free:
- `corroboration` = matching across node claim lists.
- `anchor_quality` = the anchor's generation level (from §2).
- `authority` = `git blame` author × `governance/authority-matrix.yaml`.
- `recency` = git commit date.

No training, no embeddings required for MVP. Scoring is a deterministic function over git + the matrix.

## 4. Triage  (`boss-triage`)

Bucket each claim. Tiers reuse the node-level branch-out vocabulary — no new slang:

| Tier | Condition | Action |
|---|---|---|
| **canon-ready** | high corroboration **+** gen-0 anchor | → adversarial → canon draft → human approve |
| **likely** | converges, weaker anchor | lives as `[DERIVED]`, circulates, no promotion |
| **contested** | quality nodes assert opposite | → adversarial → **HITL queue** (highest value) |
| **singleton** | one node only | hold as tip, no promotion |

Unanchored claims (§2) are capped at `likely` regardless of corroboration.

## 5. Adversarial  (`boss-adversarial`)  — P7

Every `canon-ready` candidate and every `contested` pair is red-teamed before it goes further:

- For promotion candidates: "what argument says this is NOT canon?" — anchor still valid? corroborating
  nodes truly independent, or copies of one origin (false convergence)? sensitive claim sneaking up via
  low scrutiny?
- For contested pairs: steelman both sides; classify as *genuine strategic divergence* (→ escalate, P5)
  vs *stale claim* (one side has a newer anchor → the other re-opens).
- Verdict per item: PROMOTE / HOLD / ESCALATE / KILL.

## 6. HITL  (`boss-triage` emits; humans resolve)

- Contested + ESCALATE items form a **queue**, each routed to a proposed **oracle** = the domain owner
  from `authority-matrix.yaml` (e.g. CORE → Kácha, pricing → board, rollout → Urban).
- Resolution cadence: **batched** (a periodic "oracle session" — the quarterly-pub model), or
  **trigger-based** when a contested claim blocks something material. Never one-ping-per-claim spam.
- On resolution: re-anchor to the external referent (P4 guard — the oracle's *reasoned* answer, not a
  nod at Giovanni's summary) → draft canon patch → human approves → write to `memory/canon/`.
  **That is the moment canon is born that did not exist before.**

---

## Output of one run

1. **Triage table** — every claim, its tier, score components, anchor.
2. **HITL queue** — contested/escalate items + proposed oracle + what's blocked.
3. **Canon draft** (if any `canon-ready` survived adversarial) — staged for human approval, never auto-written.
