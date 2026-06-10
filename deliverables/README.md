# Deliverables — outbound artifacts + lifecycle registry

`deliverables/` is the landing zone for **outbound artifacts**: drafts in progress, decks, one-pagers, exports, generated documents — anything produced *for* someone outside the repo. Per the authority hierarchy ([`docs/governance.md`](../docs/governance.md) § Authority hierarchy), everything here is explicitly **non-authoritative**: a deliverable may contradict the constitution and memory, because it is a draft or a frozen snapshot, not canon.

This directory also hosts the **opt-in lifecycle registry** that keeps the directory navigable once it grows.

---

## Directory contract

| Path | What it is |
|---|---|
| `deliverables/<file>` | An outbound artifact (any format — md, html, pdf, xlsx, generator scripts). |
| `deliverables/_registry.yaml` | Lifecycle registry — single source of truth for each artifact's status. Opt-in; see "When to activate". |
| `deliverables/_registry.template.yaml` | Template for the registry (this repo ships it; copy to `_registry.yaml` at activation). |
| `deliverables/REGISTRY.md` | Auto-generated, human-readable view of the registry. Built by `scripts/build-deliverables-registry.py`. **Never hand-edit.** |
| `deliverables/_archive/` | Superseded artifacts with zero inbound references. Outside the registry. |

The external write gate applies here: deliverables are the **draft-first** destination. The agent drafts into `deliverables/`, the principal confirms the specific publish/send action. See [`docs/governance.md`](../docs/governance.md) § External write gate.

---

## Registry schema

`_registry.yaml` holds one entry per file:

```yaml
entries:
  - file: <filename or folder name, relative to deliverables/>
    status: <live | draft | sent | superseded>
    type: <document | artifact | generator | infra | ...>   # free vocabulary, keep it small
    date: 'YYYY-MM-DD'    # creation/send date of the artifact — NOT last edit
    note: <one line — what it is, where it went, what supersedes it>
```

**Status enum (binding):**

| Status | Meaning |
|---|---|
| `live` | Maintained artifact / valid reference — changes as the project changes. |
| `draft` | In preparation / not yet sent (send queue, pending review). |
| `sent` | Delivered / presented / published — **FROZEN**, do not edit. |
| `superseded` | Replaced by a newer version or decision — candidate for `_archive/` once zero-referenced. |

---

## Binding rules

1. **New file in `deliverables/` ⇒ entry in `_registry.yaml`.** The `deliverables-registry` lint rule enforces bidirectional completeness: every file has an entry, every entry points at an existing file. Exempt: `_archive/`, dotfiles, `README.md`, `REGISTRY.md`, `*.template.yaml`.
2. **Status flip = edit the yaml. NEVER rename or move the file.** Status lives in metadata, not in the path. This is the **anti-link-rot rule**: memory shards, decision records, and knowledge docs hold pointers to deliverable paths. Renaming `pricing-deck.md` to `pricing-deck-FINAL-sent.md` breaks every inbound reference for zero information gain — the registry already knows it was sent.
3. **After any yaml edit, regenerate:** `python3 scripts/build-deliverables-registry.py`. `REGISTRY.md` is deterministic output (grouped by status, date-descending within group); lint flags it as stale when it doesn't match a `--dry` regeneration.
4. **`date` is the artifact's creation/send date**, not its last-edit date. It answers "when did this enter the world", which is what you need when triaging what is stale.
5. **Archive sweep at full-audit cadence.** At each full memory audit (`audit_full_cadence_days`, default 35 — see [`docs/governance.md`](../docs/governance.md) § Audit cadence), sweep `superseded` entries whose files have zero inbound references into `_archive/` and remove their registry entries. Until the sweep, superseded files stay in place so existing pointers keep resolving.
6. **`sent` artifacts are frozen.** If a sent document needs changes, that's a new draft entry — the sent version is the historical record of what the counterparty actually received.

---

## When to activate

The registry is **deferred by default** — both lint checks (`deliverables-registry` schema/orphan check, `registry-stale` freshness check) no-op while `_registry.yaml` is absent. New forks should not start with it.

**Activation trigger: your flat deliverables directory exceeds ~50 files.** Below that, you can still eyeball the directory and the maintenance cost outweighs the link-rot risk. Above it, "which version did we actually send?" starts costing real time.

To activate:

1. `cp deliverables/_registry.template.yaml deliverables/_registry.yaml`
2. Replace the example entries with one entry per existing file (one backfill commit).
3. `python3 scripts/build-deliverables-registry.py`
4. `bash scripts/lint.sh --check deliverables-registry` — must be clean.

Config: `deliverables_dir` in `docs/governance.config.yaml` (default `deliverables`, env override `GIOVANNI_DELIVERABLES_DIR`).

---

## Worked example (Lattice Finance test domain)

Alex drafts the Series B narrative as `2026-05-30_series-b-narrative-v0.3.md` (`status: draft`). After Sarah's redline, v0.4 goes out — v0.4's entry flips to `sent` (frozen), v0.3 flips to `superseded`. **Neither file is renamed or moved.** The topic shard `memory/topics/series-b-prep.md` keeps pointing at both paths and both pointers still resolve. At the next full audit, v0.3 has zero inbound references left and sweeps to `_archive/`.
