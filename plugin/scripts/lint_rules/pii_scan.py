"""Lint rule: what was learned from chat history carries no identifiers, and the
raw history never enters git.

/giovanni:learn-history reads the principal's past conversations — other
people's names, case numbers, whatever was pasted into a chat — from a
workspace inside the project (default `.history/`, gitignored). Two ways that
goes wrong, both silent until the repo is shared or pushed:

  * the workspace gets tracked (a `git add -f`, a .gitignore edit, a copy under
    another name) → CRITICAL for every tracked file under it;
  * a learned artifact quotes an identifier the analyst should have replaced
    with a placeholder → HIGH per hit, value masked in the message.

What is scanned: every skill directory whose SKILL.md says
`generated_from: chat-history`, the house-style doc (`learning.history.house_style`),
`memory/learning/`, plus any extra paths in `learning.history.pii_scan_paths`.
Patterns: the built-ins in scripts/history/pii.py plus
`learning.history.pii_patterns`. Names: the denylist harvested into the
workspace — absent on a machine without the export (CI, a second laptop), in
which case only the patterns run.

No-op unless the project config has a `learning.history` block.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECK_ID = "pii-scan"


def run(ctx) -> None:
    hist = (ctx.config.get("learning") or {}).get("history") if isinstance(ctx.config.get("learning"), dict) else None
    if not isinstance(hist, dict) or not hist:
        return
    sys.path.insert(0, str(ctx.plugin / "scripts" / "history"))
    sys.path.insert(0, str(ctx.plugin / "scripts"))
    import pii  # type: ignore[import-not-found]

    repo = ctx.repo
    ws = pii.workspace(repo)
    try:
        ws_rel = ws.resolve().relative_to(repo.resolve())
    except ValueError:
        ws_rel = None
    if ws_rel is not None:
        try:
            tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--", str(ws_rel)],
                                     capture_output=True, text=True, timeout=20).stdout.split()
        except Exception:
            tracked = []
        for f in tracked:
            ctx.add("critical", CHECK_ID, f"{f}: chat-history workspace file is tracked by git — "
                    "`git rm --cached` it and keep the workspace in .gitignore")

    targets: list[Path] = []
    skills = repo / ".claude" / "skills"
    if skills.is_dir():
        for sk in sorted(skills.glob("*/SKILL.md")):
            try:
                if "generated_from: chat-history" in sk.read_text(encoding="utf-8"):
                    targets.append(sk.parent)
            except OSError:
                pass
        targets += sorted(skills.glob("*/references/learned-*.md"))
    for rel in [hist.get("house_style") or "knowledge/house-style.md", "memory/learning"] + list(hist.get("pii_scan_paths") or []):
        p = repo / rel
        if p.exists():
            targets.append(p)
    if not targets:
        return
    for line in pii.scan_paths(repo, targets, pii.denylist_path(repo)):
        path, _, rest = line.partition(":")
        try:
            path = str(Path(path).resolve().relative_to(repo.resolve()))
        except ValueError:
            pass
        ctx.add("high", CHECK_ID, f"{path}:{rest.strip()} — replace with a placeholder")
