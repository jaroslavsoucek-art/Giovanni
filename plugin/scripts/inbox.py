#!/usr/bin/env python3
"""scripts/inbox.py — the one list every loop writes to and the principal answers.

Why one list. An assistant that maintains itself produces a stream of small
asks: a deadline to verify, a lint finding, a skill it could write, a scheduled
run that did not happen. Scattered across hook messages, digests and files they
are noise; nobody acts on noise. Collected into one ranked list, shown at
session start and answerable with one word per item, they are a morning
routine. The list is the whole interface between the loops and the principal.

State: <memory_dir>/<inbox.file> (default memory/inbox.yaml) — open and snoozed
items only. Closed items (done / dismissed / expired) leave the file and land as
one line in <memory_dir>/archive/inbox-YYYY-MM.md, so the live file never turns
into a journal.

Item fields: id, kind, priority (high|normal|low), text, key (dedupe), source,
created, expires, status (open|snoozed); optional ref, on_yes, due, snooze_until.
`on_yes` is the action the agent runs when the principal answers yes — a command,
a skill invocation, or a one-line instruction.

A "no" (`resolve --status dismissed`) on an undated item suppresses its key for
`inbox.dismiss_days` (default 30): without that, a producer that still sees the
cause would put the same ask back at the next session start, and "no" would mean
nothing. A dated item cannot be dismissed away — only its producer closes it
(a deadline is closed by recording what happened to it, not by ignoring it).

Usage:
  inbox.py [--repo R] add --kind K --text T [--key K] [--source S] [--priority P]
                          [--ref R] [--on-yes A] [--due YYYY-MM-DD] [--expires-days N]
  inbox.py [--repo R] list [--json]
  inbox.py [--repo R] render [--max N]
  inbox.py [--repo R] resolve ID|KEY [--status done|dismissed] [--note N]
  inbox.py [--repo R] snooze ID|KEY --days N
  inbox.py [--repo R] sync-source SOURCE [--keep KEY ...]   close SOURCE's open items not in --keep
  inbox.py [--repo R] refresh          refreshers + lint→inbox + scheduler health + expiry
  inbox.py [--repo R] session-start    refresh, then print the SessionStart hook JSON
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gconfig  # noqa: E402
import filelock  # noqa: E402

try:
    import yaml  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    print("inbox.py needs PyYAML (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

PRIORITY_ORDER = {"high": 0, "normal": 1, "low": 2}
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
FINDING_RE = re.compile(r"^\[(CRITICAL|HIGH|MEDIUM|LOW)\] \[([\w.-]+)\] (.+)$")


def today() -> dt.date:
    raw = os.environ.get("GIOVANNI_SNAPSHOT_DATE", "").strip()
    if raw:
        try:
            return dt.date.fromisoformat(raw)
        except ValueError:
            pass
    return dt.date.today()


class Inbox:
    def __init__(self, repo: Path):
        self.repo = repo
        self.cfg = gconfig.config(repo)
        self.icfg = self.cfg["inbox"]
        self.memory = repo / self.cfg["memory_dir"]
        self.path = self.memory / self.icfg["file"]
        self.lock_path = self.memory / ".inbox.lock"
        self.items: list[dict] = []
        self.suppressed: dict[str, str] = {}

    def active(self) -> bool:
        """The inbox exists for a project that configured it or already has the file.
        Everywhere else every entry point is a no-op, so installing the plugin never
        creates files a project did not ask for."""
        raw = gconfig.load_config(self.repo).get("inbox") if hasattr(gconfig, "load_config") else None
        return bool(raw) or self.path.is_file()

    # ----- persistence -------------------------------------------------------
    @contextlib.contextmanager
    def locked(self):
        self.memory.mkdir(parents=True, exist_ok=True)
        with open(self.lock_path, "a+") as lock:
            filelock.lock(lock)
            try:
                self.load()
                yield self
                self.save()
            finally:
                filelock.unlock(lock)

    def load(self) -> None:
        if not self.path.is_file():
            self.items, self.suppressed = [], {}
            return
        data = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
        items = data.get("items") if isinstance(data, dict) else None
        self.items = [i for i in (items or []) if isinstance(i, dict)]
        sup = data.get("suppressed") if isinstance(data, dict) else None
        self.suppressed = {str(k): str(v) for k, v in (sup or {}).items()} if isinstance(sup, dict) else {}

    def save(self) -> None:
        header = ("# Generated and consumed by the Giovanni inbox (scripts/inbox.py).\n"
                  "# Open items only; closed ones are archived to memory/archive/inbox-YYYY-MM.md.\n"
                  "# Edit through the script or the agent, not by hand.\n")
        doc = {"version": 1, "items": self.items}
        if self.suppressed:
            doc["suppressed"] = dict(sorted(self.suppressed.items()))
        body = yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000)
        self.path.write_text(header + body, encoding="utf-8")

    def archive(self, item: dict, status: str, note: str = "") -> None:
        arch = self.memory / "archive"
        arch.mkdir(parents=True, exist_ok=True)
        f = arch / f"inbox-{today():%Y-%m}.md"
        if not f.exists():
            f.write_text(f"# Inbox archive {today():%Y-%m}\n\n"
                         "> Closed inbox items, one line each. Written by scripts/inbox.py.\n\n",
                         encoding="utf-8")
        line = (f"- {today().isoformat()} · {status} · {item.get('kind')} · {item.get('text')}"
                + (f" · {note}" if note else "") + f" · `{item.get('key')}`\n")
        with open(f, "a", encoding="utf-8") as fh:
            fh.write(line)

    # ----- operations --------------------------------------------------------
    def find(self, ref: str) -> dict | None:
        for it in self.items:
            if it.get("id") == ref or it.get("key") == ref:
                return it
        return None

    def add(self, kind: str, text: str, key: str | None = None, source: str = "manual",
            priority: str = "normal", ref: str | None = None, on_yes: str | None = None,
            due: str | None = None, expires_days: int | None = None) -> dict:
        key = key or f"{source}:{hashlib.sha1(text.encode()).hexdigest()[:10]}"
        until = self.suppressed.get(key)
        if until and not due:
            if until >= today().isoformat():
                # The principal said no to this ask; its producer does not get to ask again
                # until the suppression runs out. Dated items are never suppressed.
                return {"id": None, "key": key, "suppressed_until": until}
            self.suppressed.pop(key, None)
        existing = self.find(key)
        if existing is not None:
            # Same ask again: refresh what may have changed, keep its age and snooze.
            existing.update({k: v for k, v in {"text": text, "priority": priority, "ref": ref,
                                                "on_yes": on_yes, "due": due}.items() if v})
            return existing
        days = expires_days if expires_days is not None else int(self.icfg["default_expiry_days"])
        item = {
            "id": f"i-{today():%Y%m%d}-{hashlib.sha1(key.encode()).hexdigest()[:4]}",
            "kind": kind,
            "priority": priority if priority in PRIORITY_ORDER else "normal",
            "text": text,
            "key": key,
            "source": source,
            "created": today().isoformat(),
            "expires": (today() + dt.timedelta(days=days)).isoformat(),
            "status": "open",
        }
        for k, v in (("ref", ref), ("on_yes", on_yes), ("due", due)):
            if v:
                item[k] = v
        self.items.append(item)
        return item

    def close(self, ref: str, status: str = "done", note: str = "") -> bool:
        it = self.find(ref)
        if it is None:
            return False
        self.items.remove(it)
        if status == "dismissed" and not it.get("due"):
            days = int(self.icfg.get("dismiss_days", 30))
            self.suppressed[it["key"]] = (today() + dt.timedelta(days=days)).isoformat()
            note = (note + " · " if note else "") + f"suppressed {days} d"
        self.archive(it, status, note)
        return True

    def snooze(self, ref: str, days: int) -> bool:
        it = self.find(ref)
        if it is None:
            return False
        it["status"] = "snoozed"
        it["snooze_until"] = (today() + dt.timedelta(days=days)).isoformat()
        exp = dt.date.fromisoformat(it["expires"])
        if exp <= today() + dt.timedelta(days=days):
            it["expires"] = (today() + dt.timedelta(days=days + 7)).isoformat()
        return True

    def sync_source(self, source: str, keep: set[str], note: str = "no longer reported") -> int:
        closed = 0
        for it in list(self.items):
            if it.get("source") == source and it.get("key") not in keep:
                self.items.remove(it)
                self.archive(it, "done", note)
                closed += 1
        return closed

    def expire(self) -> None:
        t = today()
        self.suppressed = {k: v for k, v in self.suppressed.items() if v >= t.isoformat()}
        for it in list(self.items):
            if it.get("status") == "snoozed" and it.get("snooze_until") and \
                    dt.date.fromisoformat(it["snooze_until"]) <= t:
                it["status"] = "open"
                it.pop("snooze_until", None)
            if it.get("due"):
                # A dated item (a deadline) never expires: past its date it escalates, and
                # only its producer closes it. A silently expired deadline is the one
                # failure this list exists to prevent.
                try:
                    if dt.date.fromisoformat(str(it["due"])) < t:
                        it["priority"] = "high"
                        it["overdue"] = True
                except ValueError:
                    pass
                continue
            try:
                exp = dt.date.fromisoformat(str(it.get("expires")))
            except ValueError:
                continue
            if exp < t:
                self.items.remove(it)
                self.archive(it, "expired")

    def open_sorted(self) -> list[dict]:
        def k(it):
            due = it.get("due") or "9999-12-31"
            return (PRIORITY_ORDER.get(it.get("priority"), 1), str(due), str(it.get("created")))
        return sorted((i for i in self.items if i.get("status") == "open"), key=k)

    def render(self, max_items: int | None = None) -> str:
        items = self.open_sorted()
        if not items:
            return ""
        cap = max_items or int(self.icfg["max_open"])
        lines = [f"## {self.icfg['title']} — {today().isoformat()}", ""]
        for n, it in enumerate(items[:cap], 1):
            due = f" — **{it['due']}**" if it.get("due") else ""
            if it.get("overdue"):
                due += f" **{self.icfg['overdue_label']}**"
            prio = "❗ " if it.get("priority") == "high" else ""
            ref = f" (`{it['ref']}`)" if it.get("ref") else ""
            lines.append(f"{n}. {prio}{it['text']}{due}{ref}  ·  `{it['id']}`")
        if len(items) > cap:
            lines.append(f"\n_+{len(items) - cap} more. More than {cap} open items means the loops "
                         "produce more than one person can answer — prune, raise thresholds, or fix the source._")
        lines += ["", self.icfg["answer_hint"]]
        return "\n".join(lines)


# ----- refresh sources ---------------------------------------------------------

def _plugin_scripts() -> Path:
    return Path(__file__).resolve().parent


def refresh(repo: Path) -> list[str]:
    """Run every producer that can run cheaply at session start. Returns warnings
    for producers that failed (they also land in the inbox)."""
    warnings: list[str] = []
    box = Inbox(repo)
    if not box.active():
        return warnings
    # 1. project refreshers (they call inbox.py add/sync-source themselves)
    for cmd in box.icfg.get("refreshers") or []:
        try:
            r = subprocess.run(shlex.split(cmd), cwd=repo, capture_output=True, text=True, timeout=60,
                               env={**os.environ, "GIOVANNI_REPO_ROOT": str(repo)})
            ok = r.returncode == 0
            err = (r.stderr or r.stdout).strip().splitlines()[-1:] if not ok else []
        except Exception as e:  # noqa: BLE001
            ok, err = False, [repr(e)]
        with Inbox(repo).locked() as b:
            key = f"refresher:{hashlib.sha1(cmd.encode()).hexdigest()[:8]}"
            if ok:
                b.close(key, "done", "refresher recovered")
            else:
                b.add("warning", f"Refresher failed: `{cmd}` — {' '.join(err)[:200]}", key=key,
                      source="refresher", priority="high")
                warnings.append(cmd)
    # 2. lint → inbox
    if box.icfg.get("lint_to_inbox"):
        threshold = SEVERITY_ORDER.get(str(box.icfg.get("lint_min_severity", "medium")).lower(), 2)
        r = subprocess.run([sys.executable, str(_plugin_scripts() / "lint.py"), "--repo-root", str(repo)],
                           capture_output=True, text=True, timeout=120)
        keep: set[str] = set()
        with Inbox(repo).locked() as b:
            for line in r.stdout.splitlines():
                m = FINDING_RE.match(line.strip())
                if not m:
                    continue
                sev, check, msg = m.group(1).lower(), m.group(2), m.group(3)
                if SEVERITY_ORDER.get(sev, 3) > threshold:
                    continue
                key = f"lint:{check}:{hashlib.sha1(msg.encode()).hexdigest()[:10]}"
                keep.add(key)
                b.add("hygiene", f"[{check}] {msg}", key=key, source="lint",
                      priority="high" if sev in ("critical", "high") else "normal",
                      on_yes="fix it (lint rule " + check + "), then re-run lint", expires_days=60)
            b.sync_source("lint", keep, "lint finding resolved")
    # 3. scheduler health
    if box.cfg.get("schedule"):
        subprocess.run([sys.executable, str(_plugin_scripts() / "schedule.py"), "--repo", str(repo), "check"],
                       capture_output=True, text=True, timeout=30)
    # 4. expiry
    with Inbox(repo).locked() as b:
        b.expire()
    return warnings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--kind", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--key")
    a.add_argument("--source", default="manual")
    a.add_argument("--priority", default="normal")
    a.add_argument("--ref")
    a.add_argument("--on-yes")
    a.add_argument("--due")
    a.add_argument("--expires-days", type=int)
    ls = sub.add_parser("list")
    ls.add_argument("--json", action="store_true")
    rd = sub.add_parser("render")
    rd.add_argument("--max", type=int)
    rs = sub.add_parser("resolve")
    rs.add_argument("ref")
    rs.add_argument("--status", default="done", choices=["done", "dismissed"])
    rs.add_argument("--note", default="")
    sz = sub.add_parser("snooze")
    sz.add_argument("ref")
    sz.add_argument("--days", type=int, required=True)
    ss = sub.add_parser("sync-source")
    ss.add_argument("source")
    ss.add_argument("--keep", nargs="*", default=[])
    sub.add_parser("refresh")
    sub.add_parser("session-start")
    args = ap.parse_args(argv)
    repo = gconfig.repo_root(args.repo)

    if args.cmd == "add":
        with Inbox(repo).locked() as b:
            it = b.add(args.kind, args.text, key=args.key, source=args.source, priority=args.priority,
                       ref=args.ref, on_yes=args.on_yes, due=args.due, expires_days=args.expires_days)
        print(it["id"] or f"suppressed until {it.get('suppressed_until')}")
        return 0
    if args.cmd == "list":
        b = Inbox(repo)
        b.load()
        if args.json:
            print(json.dumps(b.items, ensure_ascii=False, indent=2))
        else:
            for it in b.open_sorted():
                print(f"{it['id']}  {it['priority']:<6} {it['kind']:<16} {it['text']}")
        return 0
    if args.cmd == "render":
        b = Inbox(repo)
        b.load()
        print(b.render(args.max))
        return 0
    if args.cmd == "resolve":
        with Inbox(repo).locked() as b:
            ok = b.close(args.ref, args.status, args.note)
        if not ok:
            print(f"no inbox item {args.ref}", file=sys.stderr)
        return 0 if ok else 1
    if args.cmd == "snooze":
        with Inbox(repo).locked() as b:
            ok = b.snooze(args.ref, args.days)
        return 0 if ok else 1
    if args.cmd == "sync-source":
        with Inbox(repo).locked() as b:
            print(b.sync_source(args.source, set(args.keep)))
        return 0
    if args.cmd == "refresh":
        refresh(repo)
        return 0
    if args.cmd == "session-start":
        try:
            refresh(repo)
        except Exception as e:  # noqa: BLE001 — a hook never blocks a session
            print(f"inbox refresh failed: {e!r}", file=sys.stderr)
        b = Inbox(repo)
        b.load()
        text = b.render()
        if text:
            msg = ("INBOX — show this list to the principal first, as-is, before anything else, then "
                   "act on their one-word answers: yes → run the item's on_yes and resolve it; "
                   "no → resolve --status dismissed; later Nd → snooze (scripts/inbox.py in the "
                   "Giovanni plugin; see `inbox.py list --json` for on_yes).\n\n" + text)
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                                     "additionalContext": msg}}, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
