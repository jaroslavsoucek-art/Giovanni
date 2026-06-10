# scripts/lint_rules/

Pluggable lint rules for `scripts/lint.py`. Each `.py` file in this directory is one rule. Files starting with `_` are skipped (use for shared helpers).

## Adding a rule

Create `scripts/lint_rules/<rule_name>.py`:

```python
"""One-line description of what the rule checks."""

CHECK_ID = "kebab-case-identifier"

def run(ctx) -> None:
    """ctx is LintContext (see scripts/lint.py).

    Access:
      ctx.repo                  pathlib.Path of repo root
      ctx.config                dict of governance config (see governance.config.template.yaml)
      ctx.memory_dir()          memory dir path
      ctx.knowledge_dir()       knowledge dir path
      ctx.constitution_path()   constitution file path
      ctx.l1_path()             L1 operational memory path

    Emit findings via:
      ctx.add(severity, CHECK_ID, message)

    Severity: 'critical' | 'high' | 'medium' | 'low'.
    """
    # ...
```

Optional helpers from `lint.py`:

```python
from lint import parse_frontmatter, rel, HAVE_YAML
```

## Conventions

- One rule per file; one `CHECK_ID` per file.
- Description in module docstring (top of file). The docstring is documentation, not used by the runner.
- Default severity in the rule itself — caller cannot override.
- Rules should be **idempotent and side-effect-free**. No writes, no network, no env mutation.
- Rules should **degrade gracefully** when their target doesn't exist (no constitution file → return cleanly, don't crash).
- Rules should **respect config** — if a behaviour is toggled by `governance.config.yaml`, read `ctx.config["<key>"]`.

## Listing rules

```
bash scripts/lint.sh --list
```

## Running one rule

```
bash scripts/lint.sh --check <CHECK_ID>
```

## Built-in rules

| CHECK_ID | Severity (default) | Purpose |
|---|---|---|
| `adversarial-verdict-format` | low | Persisted adversarial reviews use the SHIP/REWRITE/KILL enum + count fields (no-op without `memory/intel/adversarial/`) |
| `branch-out-no-recommendation` | medium / critical | Branch-out artifacts stay generative — no recommendation prose or structure |
| `constitution-anchors` | medium | Constitution headers have `{#anchor-id}` |
| `decision-trigger-conditions` | critical | Decision records have non-empty `trigger_conditions` |
| `deliverables-registry` | high | Deliverables ↔ `_registry.yaml` bidirectional completeness, schema + status enum (no-op without `_registry.yaml`) |
| `digest-state-freshness` | low / medium | Digest state `last_run_timestamp` is recent (operational tempo signal) |
| `domain-leak` | high | Configurable denylist for prior-domain content carry-over |
| `l1-size` | high / critical | L1 operational memory line count (warn 300, fail 400) |
| `l1-strikethrough-ratio` | medium / critical | Strikethrough ratio in L1 (warn 2 %, fail 5 %) |
| `no-percentages-in-predictions` | high | Predictive artifacts use the three-tier enum, never numeric probabilities |
| `shadow-expired-pending` | medium / high | Pending shadow hypotheses not past `horizon_at`; resolved ones carry a filled `adversarial_check` |
| `slash-command-registry` | low | `.claude/commands/README.md` registry table in sync with command files |
| `stakeholder-frontmatter` | medium | Stakeholder profiles match the documented frontmatter schema (required fields, enums, slug ↔ filename) |
| `stakeholder-slug-exists` | medium | `key_stakeholders` slugs resolve to profile files |
| `topic-shard-frontmatter` | medium | Topic shards have required frontmatter fields |

Plus bash-side checks (in `scripts/lint.sh`, not Python plugins):

| CHECK_ID | Purpose |
|---|---|
| `index-stale` | `knowledge/INDEX.md` matches `build-knowledge-index.sh --dry` ([SKIP] on shallow clones) |
| `map-stale` | `memory/MAP.md` matches `build-memory-map.sh --dry` ([SKIP] on shallow clones) |
| `registry-stale` | `deliverables/REGISTRY.md` matches `build-deliverables-registry.py --dry` (opt-in — only when `_registry.yaml` exists) |
| `hook-syntax` | Every `.claude/hooks/*.sh` passes `bash -n` |
| `script-syntax` | Every `scripts/*.sh` passes `bash -n` |

## Self-test fixtures

New rule ⇒ new fixture suite in `scripts/lint-fixtures/<check-id>/{pass,fail}/`
(see `scripts/lint-fixtures/README.md`). Run the harness:

```
bash scripts/run-lint-fixtures.sh
```
