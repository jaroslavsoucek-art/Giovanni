#!/usr/bin/env python3
"""scripts/lint.py — Giovanni Python lint dispatcher.

Discovers and runs rule plugins from scripts/lint_rules/. Each plugin is one
Python file that exposes:

  CHECK_ID: str         # unique id, used by --check
  SEVERITY: str         # default severity (critical/high/medium/low)
  def run(ctx) -> list[Finding]

Where Finding = (severity, check_id, message).

Configuration is loaded from docs/governance.config.yaml if present (PyYAML
required), then overridden by env vars (GIOVANNI_*). Defaults are sensible
for a small / mid-sized fork.

Usage:
    python3 scripts/lint.py [--repo-root <path>] [--check <id>] [--list]

Exit codes:
    0 — no findings
    1 — one or more findings
    2 — internal error (missing dependency, bad config)
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    import yaml  # type: ignore[import-not-found]
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


# ---------------------------------------------------------------------------
# Finding type + emitter

@dataclass
class Finding:
    severity: str
    check_id: str
    message: str


FINDINGS_COUNT = 0


def emit(f: Finding) -> None:
    global FINDINGS_COUNT
    print(f"[{f.severity.upper()}] [{f.check_id}] {f.message}")
    FINDINGS_COUNT += 1


# ---------------------------------------------------------------------------
# Config

DEFAULT_CONFIG: dict[str, Any] = {
    # Layer paths
    "knowledge_dir": "knowledge",
    "memory_dir": "memory",
    "constitution_file": "constitution.md",
    "l1_file": "CLAUDE_MEMORY.md",
    # Size pressure
    "l1_limit": 300,
    "l1_limit_critical": 400,
    # Bytes, not lines. A file can sit well under the line cap and still be
    # expensive: 200 lines of 290-char paragraphs is 58 KB of session start.
    # Whichever cap trips first, trips.
    "l1_limit_bytes": 32768,
    "strike_ratio_max": 0.02,
    "digest_state_limit_bytes": 32768,
    # Cadence (days)
    "audit_full_cadence_days": 35,
    "audit_light_cadence_days": 14,
    "resolved_shard_retirement_days": 60,
    # An ACTIVE shard that nobody has touched in this long is either stale or
    # finished. Either way it needs a human decision — refresh or retire.
    "shard_stale_days": 45,
    # A "N days of silence" claim in L1 / an active shard must carry a
    # `[verified YYYY-MM-DD]` stamp no older than this (silence-counter-verified).
    "silence_stamp_max_days": 7,
    # Extra silence keywords for the fork's working language. The English
    # defaults in the rule always apply.
    "silence_keywords": [],
    # Constitution / structural
    "require_anchor_ids": True,
    # Deliverables lifecycle registry (opt-in — checks activate only when
    # <deliverables_dir>/_registry.yaml exists)
    "deliverables_dir": "deliverables",
    # Reference date for every time-based check. Empty = the real today.
    # A frozen reference fork (a bundled example, a captured audit state) sets
    # this to the date it was captured, so cadence checks measure the snapshot's
    # own age rather than how long ago it was committed. Without it, any example
    # with dates in it goes red on a clock, not on a defect.
    "snapshot_date": "",
    # Domain-leak guard — list of strings forbidden in memory + knowledge.
    # Fork-time: populate with prior-domain proper nouns to catch carry-over
    # during template filling. Default empty = no check.
    "domain_leak_denylist": [],
    # Optional layers. A layer set to false is switched off: its lint rules
    # no-op (rules declare LAYER = "<name>"), init does not scaffold it, its
    # skills refuse to run. Absent = on. Known layers: predictive, stakeholders,
    # digest. See docs/autonomy.md § Layers.
    "layers": {},
    # Project-owned lint rules, discovered next to the plugin's own. Same
    # contract as scripts/lint_rules/*.py in the plugin (CHECK_ID + run(ctx)).
    # A project rule whose CHECK_ID collides with a plugin rule is skipped.
    "project_lint_rules_dir": "scripts/lint_rules",
    # Autonomy profile, inbox and learning loop — read by scripts/inbox.py,
    # hooks/lib/autonomy.py, hooks/lib/learning.py. Empty = off. Schema in
    # templates/governance.config.template.yaml; mechanism in docs/autonomy.md.
    "inbox": {},
    "autonomy": {},
    "learning": {},
    "schedule": [],
}

ENV_PREFIX = "GIOVANNI_"


def load_config(repo: Path) -> dict[str, Any]:
    cfg = dict(DEFAULT_CONFIG)
    cfg_path = repo / "docs" / "governance.config.yaml"
    if cfg_path.is_file() and HAVE_YAML:
        try:
            file_cfg = yaml.safe_load(cfg_path.read_text())
            if isinstance(file_cfg, dict):
                cfg.update({k: v for k, v in file_cfg.items() if v is not None})
        except yaml.YAMLError as e:
            print(f"WARNING: governance.config.yaml parse error — {e}", file=sys.stderr)
    elif cfg_path.is_file() and not HAVE_YAML:
        print("WARNING: governance.config.yaml present but PyYAML missing — using defaults", file=sys.stderr)
    # Env overrides (string-typed, coerced lightly)
    for key in list(cfg.keys()):
        env_key = f"{ENV_PREFIX}{key.upper()}"
        raw = os.environ.get(env_key)
        if raw is None:
            continue
        # Coerce based on default type
        default = DEFAULT_CONFIG[key]
        if isinstance(default, dict):
            continue  # structured blocks are file-only
        try:
            if isinstance(default, bool):
                cfg[key] = raw.lower() in {"1", "true", "yes", "on"}
            elif isinstance(default, int):
                cfg[key] = int(raw)
            elif isinstance(default, float):
                cfg[key] = float(raw)
            elif isinstance(default, list):
                cfg[key] = [s.strip() for s in raw.split(",") if s.strip()]
            else:
                cfg[key] = raw
        except ValueError:
            print(f"WARNING: env {env_key}={raw!r} invalid for type {type(default).__name__}", file=sys.stderr)
    return cfg


# ---------------------------------------------------------------------------
# Context

@dataclass
class LintContext:
    """Two roots, deliberately.

    `repo` is the project under lint — the fork's memory, knowledge, its own
    .claude/ additions. `plugin` is the Giovanni plugin this lint ships in:
    skills, agents, hooks, mechanism docs. They were one directory while
    Giovanni was a fork template; as a plugin they are not, and a rule that
    looks for `.claude/agents` in the project finds the fork's own agents (if
    any), never Giovanni's. Rules that govern the plugin surface read
    `ctx.plugin`; rules that govern state read `ctx.repo`.
    """
    repo: Path
    config: dict[str, Any]
    plugin: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    findings: list[Finding] = field(default_factory=list)

    def add(self, severity: str, check_id: str, message: str) -> None:
        self.findings.append(Finding(severity, check_id, message))

    def knowledge_dir(self) -> Path:
        return self.repo / self.config["knowledge_dir"]

    def memory_dir(self) -> Path:
        return self.repo / self.config["memory_dir"]

    def constitution_path(self) -> Path:
        return self.knowledge_dir() / self.config["constitution_file"]

    def l1_path(self) -> Path:
        return self.memory_dir() / self.config["l1_file"]

    def deliverables_dir(self) -> Path:
        return self.repo / self.config["deliverables_dir"]

    def layer_enabled(self, name: str) -> bool:
        """A layer is on unless `layers.<name>` is explicitly false."""
        layers = self.config.get("layers") or {}
        return not (isinstance(layers, dict) and layers.get(name) is False)

    def today(self):
        """Reference date for time-based checks — `snapshot_date` if set, else today.

        Every cadence rule must use this rather than date.today(), or a frozen
        fixture becomes a failing build the moment enough time passes.
        """
        import datetime as _dt
        raw = str(self.config.get("snapshot_date") or "").strip()
        if raw:
            try:
                return _dt.date.fromisoformat(raw)
            except ValueError:
                pass
        return _dt.date.today()

    def now(self):
        """Reference timestamp (UTC) for time-based checks. See today()."""
        import datetime as _dt
        raw = str(self.config.get("snapshot_date") or "").strip()
        if raw:
            try:
                d = _dt.date.fromisoformat(raw)
                return _dt.datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=_dt.timezone.utc)
            except ValueError:
                pass
        return _dt.datetime.now(_dt.timezone.utc)


# ---------------------------------------------------------------------------
# Plugin discovery

RULES_DIR_NAME = "lint_rules"


def _load_rules_from(rules_dir: Path, namespace: str) -> list[tuple[str, Callable[[LintContext], None], str | None]]:
    rules: list[tuple[str, Callable[[LintContext], None], str | None]] = []
    if not rules_dir.is_dir():
        return rules
    for path in sorted(rules_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(f"{namespace}.{path.stem}", path)
        if spec is None or spec.loader is None:
            print(f"WARNING: cannot load rule {path.name}", file=sys.stderr)
            continue
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"WARNING: rule {path.name} failed to import — {e}", file=sys.stderr)
            continue
        check_id = getattr(mod, "CHECK_ID", None)
        run_fn = getattr(mod, "run", None)
        if not check_id or not callable(run_fn):
            print(f"WARNING: rule {path.name} missing CHECK_ID or run()", file=sys.stderr)
            continue
        rules.append((check_id, run_fn, getattr(mod, "LAYER", None)))
    return rules


def discover_rules(scripts_dir: Path, project_rules_dir: Path | None = None
                   ) -> list[tuple[str, Callable[[LintContext], None], str | None]]:
    """Discover rule plugins: the plugin's scripts/lint_rules/*.py, then the
    project's own (`project_lint_rules_dir`). Returns (check_id, run_fn, layer)
    triples, plugin rules first, each set in filename-sort order. A rule's
    optional module-level LAYER names the layer it governs; the runner skips it
    when that layer is switched off in the project config.
    """
    rules = _load_rules_from(scripts_dir / RULES_DIR_NAME, "lint_rules")
    if project_rules_dir is not None and project_rules_dir.resolve() != (scripts_dir / RULES_DIR_NAME).resolve():
        seen = {cid for cid, _fn, _layer in rules}
        for cid, fn, layer in _load_rules_from(project_rules_dir, "project_lint_rules"):
            if cid in seen:
                print(f"WARNING: project rule {cid} collides with a plugin rule — skipped", file=sys.stderr)
                continue
            rules.append((cid, fn, layer))
            seen.add(cid)
    return rules


# ---------------------------------------------------------------------------
# Frontmatter helper (re-exported for rules to use via shared utilities)

_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(path: Path) -> dict | None:
    """Parse YAML frontmatter from a markdown file. Returns dict or None."""
    if not HAVE_YAML:
        return None
    try:
        text = path.read_text()
    except OSError:
        return None
    m = _FM_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def rel(path: Path, repo: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


# Make these importable from rules
sys.modules[__name__].parse_frontmatter = parse_frontmatter  # type: ignore[attr-defined]
sys.modules[__name__].rel = rel  # type: ignore[attr-defined]
sys.modules[__name__].Finding = Finding  # type: ignore[attr-defined]
sys.modules[__name__].HAVE_YAML = HAVE_YAML  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Main

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--check", help="single check id")
    parser.add_argument("--list", action="store_true", help="list check ids and exit")
    args = parser.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    if not repo.is_dir():
        print(f"ERROR: repo root not found: {repo}", file=sys.stderr)
        return 2

    scripts_dir = Path(__file__).parent
    cfg = load_config(repo)
    project_rules = repo / str(cfg.get("project_lint_rules_dir") or "scripts/lint_rules")
    rules = discover_rules(scripts_dir, project_rules)

    if args.list:
        if not rules:
            print("  (no rules found in scripts/lint_rules/)")
        for check_id, _fn, layer in rules:
            print(f"  {check_id}" + (f"  [layer: {layer}]" if layer else ""))
        return 0

    if args.check and args.check not in {cid for cid, _fn, _l in rules}:
        print(f"ERROR: unknown check id: {args.check} (see --list)", file=sys.stderr)
        return 2

    ctx = LintContext(repo=repo, config=cfg, plugin=scripts_dir.resolve().parent)

    for check_id, run_fn, layer in rules:
        if args.check and args.check != check_id:
            continue
        if layer and not ctx.layer_enabled(layer):
            continue
        try:
            run_fn(ctx)
        except Exception as e:
            ctx.add("critical", f"{check_id}-crash", f"rule crashed: {e!r}")

    for f in ctx.findings:
        emit(f)

    return 1 if FINDINGS_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
