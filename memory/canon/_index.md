# Canon Index

Emergent, confidence-ranked canon. **Empty until the first HITL resolution** — this is correct (P0).

Each entry is created only after: adversarial pass → HITL oracle resolution → human approval of a
canon patch. Entries are indexed here with pointers; full text lives in per-entry files.

## Entry schema

```yaml
id: <slug>
statement: <the canonical claim>
tier: canon-ready
domain: <authority-matrix domain>
nodes: [<node>, ...]          # which nodes asserted it
anchors: [<commit|file:line|permalink>, ...]   # gen-0, verbatim from origin
oracle: <who resolved it, if it came via HITL>
last_grounded: YYYY-MM-DD
status: live | unverified | superseded
```

## Entries

_(none yet)_
