# lint-fixtures

Test fixtures for `scripts/lint.sh` and `scripts/lint.py`. Each fixture is a minimal mock repo subset that exercises one check in either passing or failing state. All fixture content uses the synthetic test domain (Lattice Finance — see `docs/test-domain.md`); never real domain content.

## Layout

```
<check-id>/
├── pass/                  # files that should NOT trigger the check
│   └── <minimal repo subset>
└── fail/                  # files that SHOULD trigger the check
    └── <minimal repo subset>
```

The fixture's directory is treated as `LINT_REPO_ROOT` — so a fixture at `l1-size/fail/memory/CLAUDE_MEMORY.md` is picked up by the `l1-size` check when lint runs with `LINT_REPO_ROOT=scripts/lint-fixtures/l1-size/fail`.

## Test runner

`scripts/run-lint-fixtures.sh` iterates every `<check-id>/{pass,fail}/` directory, runs `scripts/lint.sh --check <check-id>` against it, and asserts:

- `pass/` → lint exits 0
- `fail/` → lint exits 1

Some checks run with `GIOVANNI_*` env overrides so fixtures stay compact (e.g. `l1-size` runs with a 7-line warn limit) — see the override table in `run-lint-fixtures.sh`.

## Adding fixtures

New rule ⇒ new fixture suite. When adding a check to `scripts/lint_rules/` or `scripts/lint.sh`:

1. Create `scripts/lint-fixtures/<check-id>/pass/` with files that satisfy the invariant
2. Create `scripts/lint-fixtures/<check-id>/fail/` with files that violate it
3. Run `bash scripts/run-lint-fixtures.sh` and confirm both behave as expected

Fixture content rules: synthetic test domain only (Lattice Finance cast), English only, minimal — just enough structure to trip or satisfy the one check under test.

## Current fixtures

- `l1-size` — pass: short L1; fail: L1 over the (overridden) critical limit
- `l1-strikethrough-ratio` — pass: no strikethrough; fail: ratio over the (overridden) max
- `decision-trigger-conditions` — pass: filled trigger section; fail: empty section
- `topic-shard-frontmatter` — pass: complete frontmatter; fail: missing fields + bad status
- `shadow-expired-pending` — pass: pending inside horizon + resolved with adversarial_check; fail: pending past horizon + resolved with empty adversarial_check
- `branch-out-no-recommendation` — pass: generative trade-off matrix; fail: recommendation prose + section
- `stakeholder-frontmatter` — pass: schema-complete profile; fail: missing fields, bad enums, slug↔filename mismatch
- `deliverables-registry` — pass: registry ↔ files consistent; fail: invalid status, orphan entry, unregistered file
- `registry-stale` — pass: REGISTRY.md matches regen; fail: REGISTRY.md stale vs `_registry.yaml`

Checks without fixtures (covered by lint runs against the real repo for now): `index-stale`, `map-stale`, `hook-syntax`, `script-syntax` (need a git repo / scripts tree inside the fixture), `digest-state-freshness` (needs date manipulation), `constitution-anchors`, `domain-leak`, `adversarial-verdict-format`, `no-percentages-in-predictions`, `slash-command-registry`, `stakeholder-slug-exists`. Follow-up can extend.
