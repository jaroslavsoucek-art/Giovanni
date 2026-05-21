"""Lint rule: topic shard frontmatter must have required fields.

Per memory-architect's binding schema (memory/README.md "Layer 2 — Topic
shards"), every shard needs: slug, status, owner, last_touch,
key_stakeholders. Optional fields tolerated; missing required = medium
finding (won't block CI by default but should be fixed).
"""

CHECK_ID = "topic-shard-frontmatter"

REQUIRED_FIELDS = ["slug", "status", "owner", "last_touch", "key_stakeholders"]
ALLOWED_STATUSES = {"active", "partially-resolved", "resolved", "superseded"}


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    if not HAVE_YAML:
        ctx.add(
            "low",
            CHECK_ID,
            "PyYAML not installed — frontmatter checks skipped",
        )
        return

    topics_dir = ctx.memory_dir() / "topics"
    if not topics_dir.is_dir():
        return

    for shard in sorted(topics_dir.glob("*.md")):
        if shard.name.startswith("_") or shard.name == "README.md":
            continue
        fm = parse_frontmatter(shard)
        if fm is None:
            ctx.add(
                "medium",
                CHECK_ID,
                f"{rel(shard, ctx.repo)}: missing or invalid YAML frontmatter",
            )
            continue
        for field in REQUIRED_FIELDS:
            val = fm.get(field)
            if val is None or val == "" or val == []:
                ctx.add(
                    "medium",
                    CHECK_ID,
                    f"{rel(shard, ctx.repo)}: missing/empty frontmatter field '{field}'",
                )
        status = fm.get("status")
        if status is not None and status not in ALLOWED_STATUSES:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(shard, ctx.repo)}: status='{status}' not in {sorted(ALLOWED_STATUSES)}",
            )

    # Also check _resolved/ shards have status: resolved
    resolved_dir = topics_dir / "_resolved"
    if resolved_dir.is_dir():
        for shard in sorted(resolved_dir.glob("*.md")):
            fm = parse_frontmatter(shard)
            if fm is None:
                continue
            if fm.get("status") != "resolved":
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(shard, ctx.repo)}: in _resolved/ but status='{fm.get('status')}' (expected 'resolved')",
                )
