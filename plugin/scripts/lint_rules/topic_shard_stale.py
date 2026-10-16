"""Lint rule: an active topic shard must not freeze.

Shards graduate out of L1 to keep session start cheap. The side effect is that
a shard, once written, is read only when someone goes looking for it — so a
topic that quietly ended leaves behind a file that still says `status: active`
and still shows up as live context to every future reader.

The retirement rule (60 days after `status: resolved`) never fires for these,
because nobody set the status. This check catches the other direction: a shard
still claiming to be active that nobody has touched in `shard_stale_days`.

Two valid answers, both requiring a human: refresh it (the topic is alive and
the shard is behind), or set `status: resolved` (it is done). Bumping
`last_touch` without reading the shard is the third answer and it is a lie.
"""

import datetime

CHECK_ID = "topic-shard-stale"
SEVERITY = "medium"
LIVE_STATUSES = {"active", "partially-resolved"}


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    if not HAVE_YAML:
        return

    topics_dir = ctx.memory_dir() / "topics"
    if not topics_dir.is_dir():
        return

    max_age = int(ctx.config["shard_stale_days"])
    today = ctx.today()

    for shard in sorted(topics_dir.glob("*.md")):
        if shard.name.startswith("_") or shard.name == "README.md":
            continue
        fm = parse_frontmatter(shard)
        if not fm:
            continue  # topic-shard-frontmatter owns that finding
        if str(fm.get("status", "")).strip() not in LIVE_STATUSES:
            continue
        raw = fm.get("last_touch")
        if isinstance(raw, datetime.date):
            touched = raw
        else:
            try:
                touched = datetime.date.fromisoformat(str(raw).strip())
            except (TypeError, ValueError):
                continue  # frontmatter rule owns malformed values
        age = (today - touched).days
        if age > max_age:
            ctx.add(SEVERITY, CHECK_ID,
                    f"{rel(shard, ctx.repo)}: status `{fm.get('status')}` but untouched {age} d "
                    f"(max {max_age}) — refresh it or set `status: resolved`. "
                    "Do not bump last_touch without reading it.")
