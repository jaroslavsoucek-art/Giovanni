"""Lint rule: the resolved-shard folder and the status field agree.

`memory/topics/_resolved/` is where finished topics go so that MAP and every
future reader can tell live context from history at a glance. Two ways that
breaks, both silent:

  * a shard sits in `_resolved/` still marked active — history that reads as live
  * a shard marked `resolved` sits in `topics/` past the retirement window —
    live context that is actually history

Neither is caught by the frontmatter rule, which only checks that the field
exists and holds an allowed value.
"""

import datetime

CHECK_ID = "resolved-shard-status"
SEVERITY = "medium"


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    if not HAVE_YAML:
        return

    topics_dir = ctx.memory_dir() / "topics"
    if not topics_dir.is_dir():
        return

    # 1. Everything filed as resolved must say so.
    resolved_dir = topics_dir / "_resolved"
    if resolved_dir.is_dir():
        for shard in sorted(resolved_dir.glob("*.md")):
            if shard.name == "README.md":
                continue
            fm = parse_frontmatter(shard)
            if not fm:
                continue
            status = str(fm.get("status", "")).strip()
            if status not in {"resolved", "superseded"}:
                ctx.add(SEVERITY, CHECK_ID,
                        f"{rel(shard, ctx.repo)}: filed under _resolved/ but `status: {status or 'missing'}` "
                        "— history that reads as live context. Set the status or move it back.")

    # 2. Anything resolved long enough should have been filed.
    window = int(ctx.config["resolved_shard_retirement_days"])
    today = ctx.today()
    for shard in sorted(topics_dir.glob("*.md")):
        if shard.name.startswith("_") or shard.name == "README.md":
            continue
        fm = parse_frontmatter(shard)
        if not fm or str(fm.get("status", "")).strip() != "resolved":
            continue
        raw = fm.get("resolved_date") or fm.get("last_touch")
        if isinstance(raw, datetime.date):
            since = raw
        else:
            try:
                since = datetime.date.fromisoformat(str(raw).strip())
            except (TypeError, ValueError):
                continue
        age = (today - since).days
        if age > window:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{rel(shard, ctx.repo)}: resolved {age} d ago (window {window}) — "
                    f"move to {ctx.config['memory_dir']}/topics/_resolved/ and regenerate MAP.")
