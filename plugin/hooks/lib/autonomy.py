#!/usr/bin/env python3
"""Autonomy profile — the decision half of pre-edit-confirm.sh and stop-autocommit.sh.

Giovanni's default is "never commit unless asked": the principal reviews and
commits. That default assumes the principal reads diffs. An instance run by
someone who does not — or one that runs headless every morning — loses its
state between sessions or never commits at all. The autonomy profile makes the
split explicit, per path, in docs/governance.config.yaml:

  autonomy.auto_commit_paths  globs the Stop hook commits on its own (working state)
  autonomy.confirm_paths      globs that are canon: an Edit/Write there asks first,
                              a headless run may not touch them at all, and the
                              Stop hook never commits them — it puts them in the inbox
  autonomy.auto_push          push after an automatic commit (a private backup remote)

Globs use fnmatch on the repo-relative POSIX path: `*` crosses directories, so
`cases/*` and `cases/**` mean the same. Empty profile = both hooks are no-ops.

Subcommands:
  confirm-gate   stdin PreToolUse JSON → permissionDecision ask (interactive) or
                 deny (headless) for a confirm path; nothing otherwise
  autocommit     commit the auto paths now (the Stop hook runs this in the background)
"""
from __future__ import annotations

import fnmatch
import json
import os
import subprocess
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN / "scripts"))
import gconfig  # noqa: E402


def _rel(repo: Path, path: str) -> str | None:
    p = Path(path)
    if not p.is_absolute():
        p = repo / p
    try:
        return p.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return None


def matches(rel: str, globs) -> bool:
    return any(fnmatch.fnmatchcase(rel, g) or fnmatch.fnmatchcase(rel, g.rstrip("/*") + "/*")
               or rel == g.rstrip("/*") for g in (globs or []))


def confirm_gate() -> int:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0
    ti = d.get("tool_input") or {}
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if not path:
        return 0
    repo = gconfig.repo_root()
    rel = _rel(repo, path)
    if rel is None:
        return 0
    cfg = gconfig.config(repo)["autonomy"]
    if not matches(rel, cfg["confirm_paths"]):
        return 0
    if gconfig.headless():
        decision, reason = "deny", (
            f"{rel} is a confirm path (autonomy.confirm_paths) and this is a headless run: "
            "nobody is here to confirm. Put the proposed change in the inbox "
            "(scripts/inbox.py add --kind canon-patch …) instead.")
    else:
        decision, reason = "ask", (
            f"{rel} is a confirm path (autonomy.confirm_paths): canon changes only with the "
            "principal's explicit OK for this edit.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                             "permissionDecision": decision,
                                             "permissionDecisionReason": reason}}))
    return 0


def _git(repo: Path, *args, check=False, env=None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=check, env=env)


def _busy(repo: Path) -> bool:
    gd = Path(_git(repo, "rev-parse", "--absolute-git-dir").stdout.strip() or ".git")
    return any((gd / m).exists() for m in ("MERGE_HEAD", "rebase-merge", "rebase-apply",
                                            "CHERRY_PICK_HEAD", "REVERT_HEAD", "BISECT_LOG"))


def _changed(repo: Path) -> list[str]:
    out = _git(repo, "status", "--porcelain", "-z", "--untracked-files=all").stdout
    files, parts, i = [], out.split("\0"), 0
    while i < len(parts):
        entry = parts[i]
        if not entry:
            i += 1
            continue
        code, path = entry[:2], entry[3:]
        files.append(path)
        if code[0] in "RC":  # rename/copy: the next field is the source path
            i += 1
        i += 1
    return files


def autocommit() -> int:
    repo = gconfig.repo_root()
    cfg_all = gconfig.config(repo)
    cfg = cfg_all["autonomy"]
    if not cfg["auto_commit_paths"] and not cfg["confirm_paths"]:
        return 0
    if _git(repo, "rev-parse", "--verify", "-q", "HEAD").returncode != 0 and not _changed(repo):
        return 0
    if _busy(repo):
        return 0
    import fcntl
    mem = repo / cfg_all["memory_dir"]
    mem.mkdir(parents=True, exist_ok=True)
    lock = open(mem / ".autocommit.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return 0  # another turn's backup is running; it will pick these files up
    from inbox import Inbox  # noqa: E402

    changed = _changed(repo)
    confirm = sorted(f for f in changed if matches(f, cfg["confirm_paths"]))
    auto = sorted(f for f in changed if f not in confirm and matches(f, cfg["auto_commit_paths"]))

    with Inbox(repo).locked() as box:
        keep = set()
        for f in confirm:
            key = f"autocommit:confirm:{f}"
            keep.add(key)
            box.add("canon-change", f"Uncommitted change in `{f}` (a confirm path) waits for your OK.",
                    key=key, source="autocommit-confirm", ref=f,
                    on_yes=f"show `git diff -- {f}`, then commit it with a docs: message")
        box.sync_source("autocommit-confirm", keep, "committed or reverted")

    if not auto:
        return 0
    staged_other = [f for f in _git(repo, "diff", "--cached", "--name-only").stdout.splitlines()
                    if f and f not in auto]
    if staged_other:
        with Inbox(repo).locked() as box:
            box.add("warning", f"Automatic backup skipped: {len(staged_other)} file(s) staged by hand "
                    f"({staged_other[0]}…). Commit or unstage them.", key="autocommit:staged",
                    source="autocommit", priority="high")
        return 0

    _git(repo, "add", "-A", "--", *auto)
    groups = sorted({f.split("/")[0] + ("/" if "/" in f else "") for f in auto})
    msg = f"{cfg['commit_prefix']} session state — {', '.join(groups)} ({len(auto)} files)"
    r = _git(repo, "commit", "-q", "-m", msg)
    with Inbox(repo).locked() as box:
        if r.returncode != 0:
            _git(repo, "reset", "-q", "--", *auto)
            first = next((ln for ln in (r.stdout + r.stderr).splitlines()
                          if ln.startswith("[") or "ERROR" in ln or "error" in ln), "commit failed")
            box.add("warning", f"Automatic backup commit blocked: {first.strip()[:220]}",
                    key="autocommit:blocked", source="autocommit", priority="high",
                    on_yes="run the lint, fix the finding, let the next turn commit")
            return 0
        box.close("autocommit:blocked", "done", "backup commit went through")
        box.close("autocommit:staged", "done", "backup commit went through")
    if cfg["auto_push"]:
        if _git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}").returncode == 0:
            p = _git(repo, "push", "-q")
            with Inbox(repo).locked() as box:
                if p.returncode != 0:
                    box.add("warning", f"Backup push failed: {(p.stderr or '').strip()[:200]}",
                            key="autocommit:push", source="autocommit", priority="high")
                else:
                    box.close("autocommit:push", "done", "push went through")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "confirm-gate":
        sys.exit(confirm_gate())
    if cmd == "autocommit":
        try:
            sys.exit(autocommit())
        except Exception as e:  # noqa: BLE001 — never break a session over a backup
            print(f"autocommit: {e!r}", file=sys.stderr)
            sys.exit(0)
    sys.stderr.write(__doc__)
    sys.exit(2)
