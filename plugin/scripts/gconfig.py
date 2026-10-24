#!/usr/bin/env python3
"""scripts/gconfig.py — one reader for docs/governance.config.yaml.

The lint has always parsed the governance config; the autonomy layer (inbox,
autocommit, scheduler, learning loop) needs the same values from hooks and
scripts that are not the lint. Two parsers drift, so everything goes through
lint.load_config and this module only adds the structured-block defaults.

CLI:
  gconfig.py [--repo R] get <dotted.key> [default]   value (JSON for lists/dicts)
  gconfig.py [--repo R] layer <name>                 exit 0 if the layer is on, 1 if off
  gconfig.py [--repo R] set-layer <name> true|false  edit `layers:` in place, comments kept
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lint import load_config  # noqa: E402

INBOX_DEFAULTS = {
    "file": "inbox.yaml",
    "title": "Today",
    "answer_hint": "Answer per item: `<n> yes` · `<n> no` · `<n> later 7d`.",
    "overdue_label": "OVERDUE",
    "max_open": 10,
    "default_expiry_days": 14,
    "dismiss_days": 30,
    "lint_to_inbox": False,
    "lint_min_severity": "medium",
    "refreshers": [],
}
AUTONOMY_DEFAULTS = {
    "auto_commit_paths": [],
    "confirm_paths": [],
    "auto_push": False,
    "commit_prefix": "chore(auto):",
}
LEARNING_DEFAULTS = {
    "enabled": False,
    "unit_dirs": [],
    "min_sessions": 3,
    "window_days": 90,
    "max_candidates": 3,
    "retire_after_days": 60,
    "correction_markers": [
        r"^\s*no[,.!]",
        r"\bthat'?s (wrong|not right)\b",
        r"\bnot like that\b",
        r"\bnext time\b",
        r"\bfrom now on\b",
        r"\balways\b",
        r"\bnever\b",
    ],
}


def repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("GIOVANNI_REPO_ROOT") or os.environ.get("CLAUDE_PROJECT_DIR")
    if not raw:
        try:
            raw = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                                 text=True, check=True).stdout.strip()
        except Exception:
            raw = os.getcwd()
    return Path(raw).resolve()


def _merged(defaults: dict, value) -> dict:
    out = dict(defaults)
    if isinstance(value, dict):
        out.update({k: v for k, v in value.items() if v is not None})
    return out


def config(repo: Path) -> dict:
    cfg = load_config(repo)
    cfg["inbox"] = _merged(INBOX_DEFAULTS, cfg.get("inbox"))
    cfg["autonomy"] = _merged(AUTONOMY_DEFAULTS, cfg.get("autonomy"))
    learning = cfg.get("learning")
    cfg["learning"] = _merged(LEARNING_DEFAULTS, learning)
    # A learning block that says anything at all, without enabled: false, means on.
    if isinstance(learning, dict) and learning and "enabled" not in learning:
        cfg["learning"]["enabled"] = True
    if not isinstance(cfg.get("schedule"), list):
        cfg["schedule"] = []
    if not isinstance(cfg.get("layers"), dict):
        cfg["layers"] = {}
    return cfg


def layer_enabled(cfg: dict, name: str) -> bool:
    return cfg.get("layers", {}).get(name) is not False


def headless() -> bool:
    return os.environ.get("GIOVANNI_HEADLESS") == "1"


def set_layer(repo: Path, name: str, on: bool) -> None:
    """Edit the `layers:` block of docs/governance.config.yaml as text, so the
    file's comments survive (a YAML round-trip would drop them)."""
    path = repo / "docs" / "governance.config.yaml"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    val = "true" if on else "false"
    m = re.search(r"(?m)^layers:[ \t]*(\{\})?[ \t]*$", text)
    if not m:
        text = text.rstrip("\n") + f"\n\nlayers:\n  {name}: {val}\n"
    else:
        block_start = m.end()
        rest = text[block_start:]
        end = re.search(r"(?m)^\S", rest)
        block = rest[:end.start()] if end else rest
        line_re = re.compile(rf"(?m)^([ \t]+){re.escape(name)}:[ \t]*\S*")
        if line_re.search(block):
            block = line_re.sub(lambda mm: f"{mm.group(1)}{name}: {val}", block, count=1)
        else:
            block = f"\n  {name}: {val}" + block if not block.strip() else block.rstrip("\n") + f"\n  {name}: {val}\n"
        head = text[:m.start()] + "layers:"
        text = head + block + (rest[end.start():] if end else "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _get(cfg, dotted: str):
    cur = cfg
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("get")
    g.add_argument("key")
    g.add_argument("default", nargs="?")
    lay = sub.add_parser("layer")
    lay.add_argument("name")
    sl = sub.add_parser("set-layer")
    sl.add_argument("name")
    sl.add_argument("value", choices=["true", "false"])
    args = ap.parse_args(argv)
    if args.cmd == "set-layer":
        set_layer(repo_root(args.repo), args.name, args.value == "true")
        return 0
    cfg = config(repo_root(args.repo))
    if args.cmd == "layer":
        return 0 if layer_enabled(cfg, args.name) else 1
    val = _get(cfg, args.key)
    if val is None:
        val = args.default
    if isinstance(val, bool):
        print("true" if val else "false")
    elif isinstance(val, (list, dict)):
        print(json.dumps(val, ensure_ascii=False))
    elif val is not None:
        print(val)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
