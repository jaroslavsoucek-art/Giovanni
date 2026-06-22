# Daily Digest — Lattice Finance fork

This fork **inherits the framework's daily-digest policy unchanged**. It does not
re-document the mechanics — read them upstream:

- Policy + rationale: framework `docs/digest.md`
- 12-step procedure: framework `.claude/workflows/daily-digest.md`

## Why this file exists

The `/digest` pre-flight (`.claude/commands/digest.md` § CWD check) verifies it is
running inside a Giovanni repo by checking for **both** `memory/digest_sources.md`
and `docs/digest.md`. This file is the second of those two markers, so the pre-flight
resolves and the dry-run harness (`scripts/run-digest-dryrun.py`) reports green here.

## Fork-specific configuration

- Sources are configured in `../memory/digest_sources.md` (chat, email, calendar,
  project tracker, version control — see `digest_state.md` for last-run state).
- Runtime state lives in `../memory/digest_state.md`.
- A rendered example run is committed at `digest-2026-05-26.example.md` — an
  illustrative transcript, **not** runtime state.

No policy is overridden here. If this fork ever needs a cadence or brief-eligibility
override, document it below; until then, upstream governs.
