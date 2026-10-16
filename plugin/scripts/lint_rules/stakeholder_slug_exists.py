"""Lint rule: stakeholder slug cross-references must resolve.

Per stakeholder-architect's schema (memory/templates/stakeholder.template.md),
profile files live at `memory/stakeholders/<slug>.md` and are referenced by
slug from topic shard `key_stakeholders` arrays (and optionally other
artifacts). This rule validates that every slug referenced in topic shard
`key_stakeholders` resolves to an actual profile file.

Catches:
- Typos in stakeholder slugs (`sarah-vyaas` vs `sarah-vyas`)
- Stale references where a profile was renamed or removed
- Topic shards listing stakeholders before profiles are created

Activation policy:
- Rule activates only once at least one profile file exists in
  `memory/stakeholders/`. Before any profile is created, the rule is a
  no-op — this keeps fork-time activity clean (the user may scaffold
  topic shards before profiles).
- Severity: medium. Broken cross-reference is a maintenance signal, not
  a critical correctness violation.

Future extension hooks (not implemented here):
- Cross-check decision record `key_stakeholders` slugs
- Cross-check brief `counterparty` slugs
- Detect orphan profiles (file exists but no topic shard references it)
- Bidirectional check (topic A lists slug X, but X's profile doesn't
  list topic A in related_topics)
"""

CHECK_ID = "stakeholder-slug-exists"

REQUIRED_FIELDS_OK_TO_SKIP_RULE = []  # noop


def _collect_existing_slugs(stakeholders_dir):
    """Return set of slugs for which profile files exist.

    Slug is derived from filename: `<slug>.md` (without .md extension).
    Skips README, files starting with underscore (e.g. _archived/),
    and the archived subdirectory.
    """
    slugs = set()
    if not stakeholders_dir.is_dir():
        return slugs
    for path in stakeholders_dir.glob("*.md"):
        if path.name.startswith("_") or path.name.lower() == "readme.md":
            continue
        slugs.add(path.stem)
    # Also accept slugs whose files moved to _archived/ — they exist as
    # records, even if archived. A reference to an archived stakeholder
    # is not a broken link.
    archived_dir = stakeholders_dir / "_archived"
    if archived_dir.is_dir():
        for path in archived_dir.glob("*.md"):
            if path.name.startswith("_") or path.name.lower() == "readme.md":
                continue
            slugs.add(path.stem)
    return slugs


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    if not HAVE_YAML:
        ctx.add(
            "low",
            CHECK_ID,
            "PyYAML not installed — stakeholder slug cross-ref check skipped",
        )
        return

    stakeholders_dir = ctx.memory_dir() / "stakeholders"
    existing_slugs = _collect_existing_slugs(stakeholders_dir)

    # Activation policy: if no profiles exist yet, this rule is a no-op.
    # Fork-time scenario: the user may scaffold topic shards listing
    # planned stakeholders before profiles are bootstrapped.
    if not existing_slugs:
        return

    topics_dir = ctx.memory_dir() / "topics"
    if not topics_dir.is_dir():
        return

    for shard in sorted(topics_dir.rglob("*.md")):
        if shard.name.startswith("_") or shard.name.lower() == "readme.md":
            continue
        fm = parse_frontmatter(shard)
        if fm is None:
            # topic_shard_frontmatter.py already complains about missing
            # frontmatter; don't double-report.
            continue
        ks = fm.get("key_stakeholders")
        if not ks:
            # topic_shard_frontmatter.py already complains about empty
            # key_stakeholders.
            continue
        if not isinstance(ks, list):
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(shard, ctx.repo)}: key_stakeholders is not a list "
                f"(type={type(ks).__name__})",
            )
            continue
        for slug in ks:
            if not isinstance(slug, str) or not slug:
                ctx.add(
                    "low",
                    CHECK_ID,
                    f"{rel(shard, ctx.repo)}: key_stakeholders contains "
                    f"non-string entry: {slug!r}",
                )
                continue
            if slug not in existing_slugs:
                ctx.add(
                    "medium",
                    CHECK_ID,
                    f"{rel(shard, ctx.repo)}: key_stakeholders references "
                    f"'{slug}' but no profile at "
                    f"memory/stakeholders/{slug}.md exists",
                )
