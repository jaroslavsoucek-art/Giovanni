"""Lint rule: the inbox stays a list one person can answer.

The inbox (scripts/inbox.py, docs/autonomy.md § Inbox) is where every loop asks
the principal something. Two ways it fails, both silent:

  * schema rot — an item without a key cannot be deduplicated, so the next run of
    its producer adds it again; an item without `expires` never leaves; a bad date
    makes the expiry pass skip it. Hand edits are the usual cause.
  * overflow — more open items than `inbox.max_open`. At that point the list has
    stopped being a morning routine and become a backlog nobody reads, and the
    real fix is upstream: a producer that fires too often, a threshold too low.

No-op when the project has no inbox file. Overdue dated items are NOT a finding
here: the inbox itself escalates them, and a lint finding about them would be
fed back into the same inbox as a duplicate.
"""

from __future__ import annotations

import datetime as dt

CHECK_ID = "inbox-health"
SEVERITY = "medium"
REQUIRED = ("id", "kind", "text", "key", "source", "created", "expires", "status")


def run(ctx) -> None:
    from lint import HAVE_YAML, rel  # type: ignore[import-not-found]

    icfg = ctx.config.get("inbox") or {}
    path = ctx.memory_dir() / str(icfg.get("file") or "inbox.yaml")
    if not path.is_file() or not HAVE_YAML:
        return
    import yaml  # type: ignore[import-not-found]

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        ctx.add("high", CHECK_ID, f"{rel(path, ctx.repo)}: not valid YAML — {e}")
        return
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        ctx.add("high", CHECK_ID, f"{rel(path, ctx.repo)}: no `items:` list")
        return
    keys: set[str] = set()
    open_count = 0
    for n, it in enumerate(items, 1):
        if not isinstance(it, dict):
            ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: item {n} is not a mapping")
            continue
        missing = [f for f in REQUIRED if not it.get(f)]
        if missing:
            ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: item {it.get('id', n)} missing {', '.join(missing)}")
        for f in ("created", "expires", "due", "snooze_until"):
            if it.get(f):
                try:
                    dt.date.fromisoformat(str(it[f]))
                except ValueError:
                    ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: item {it.get('id', n)} has invalid {f}: {it[f]!r}")
        if it.get("status") not in ("open", "snoozed"):
            ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: item {it.get('id', n)} status {it.get('status')!r} — "
                    "closed items belong in the archive, not the live file")
        k = it.get("key")
        if k in keys:
            ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: duplicate key {k!r}")
        keys.add(k)
        if it.get("status") == "open":
            open_count += 1
    cap = int(icfg.get("max_open") or 10)
    if open_count > cap:
        ctx.add(SEVERITY, CHECK_ID, f"{rel(path, ctx.repo)}: {open_count} open items (max_open {cap}) — the loops "
                "produce more than one person can answer; fix the noisiest producer, do not raise the cap")
