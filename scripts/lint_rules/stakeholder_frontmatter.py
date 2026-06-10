"""Lint rule: stakeholder profile frontmatter must match the documented schema.

Deterministic enforcement of the schema documented in
`memory/templates/stakeholder.template.md` and `docs/stakeholder-profiles.md`.
Complements `stakeholder_slug_exists` (cross-reference resolution) — this rule
validates the profiles themselves.

Required fields (per the template's REQUIRED FIELDS block):
  slug, display_name, org, role, relationship_type, first_touch, last_touch,
  status, related_topics

`related_topics` must be present and be a list — an empty list is valid
(the template ships `related_topics: []` as the starting value).

Enums (binding):
  relationship_type ∈ {peer, asymmetric-power-up, asymmetric-power-down,
                       customer, vendor, counterparty}
  status            ∈ {active, dormant, archived}

Optional fields are validated only when present:
  profile_depth   ∈ {shallow, partial, deep}
  touch_frequency ∈ {high, medium, low}

Additional checks:
  - slug must match the filename (`memory/stakeholders/<slug>.md`) — the slug
    is the join key for every cross-reference; a mismatch breaks them all.
  - profiles in `_archived/` should carry `status: archived` (low severity
    if not — archival without the status flip is a soft inconsistency).

Activation policy:
  - No-op until at least one profile exists (in `memory/stakeholders/` or
    `_archived/`) — consistent with stakeholder_slug_exists scaffold-tolerance.
  - README.md and `_`-prefixed files are skipped.

Severity: medium for missing required fields, slug mismatch, and binding-enum
violations; low for optional-enum violations and archived-status mismatch.
"""

from __future__ import annotations

CHECK_ID = "stakeholder-frontmatter"
SEVERITY = "medium"

REQUIRED_FIELDS = [
    "slug",
    "display_name",
    "org",
    "role",
    "relationship_type",
    "first_touch",
    "last_touch",
    "status",
]
RELATIONSHIP_TYPES = {
    "peer",
    "asymmetric-power-up",
    "asymmetric-power-down",
    "customer",
    "vendor",
    "counterparty",
}
STATUSES = {"active", "dormant", "archived"}
PROFILE_DEPTHS = {"shallow", "partial", "deep"}
TOUCH_FREQUENCIES = {"high", "medium", "low"}


def _profile_files(stakeholders_dir):
    """Yield (path, in_archived) for every profile file."""
    if stakeholders_dir.is_dir():
        for path in sorted(stakeholders_dir.glob("*.md")):
            if path.name.startswith("_") or path.name.lower() == "readme.md":
                continue
            yield path, False
    archived_dir = stakeholders_dir / "_archived"
    if archived_dir.is_dir():
        for path in sorted(archived_dir.glob("*.md")):
            if path.name.startswith("_") or path.name.lower() == "readme.md":
                continue
            yield path, True


def run(ctx) -> None:
    from lint import parse_frontmatter, rel, HAVE_YAML  # type: ignore[import-not-found]

    stakeholders_dir = ctx.memory_dir() / "stakeholders"
    profiles = list(_profile_files(stakeholders_dir))

    # Activation policy: no profiles yet → no-op (clean fork-time activity).
    if not profiles:
        return

    if not HAVE_YAML:
        ctx.add(
            "low",
            CHECK_ID,
            "PyYAML not installed — stakeholder frontmatter checks skipped",
        )
        return

    for path, in_archived in profiles:
        fm = parse_frontmatter(path)
        if fm is None:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: missing or invalid YAML frontmatter "
                f"(see memory/templates/stakeholder.template.md)",
            )
            continue

        for field in REQUIRED_FIELDS:
            val = fm.get(field)
            if val is None or val == "":
                ctx.add(
                    SEVERITY,
                    CHECK_ID,
                    f"{rel(path, ctx.repo)}: missing/empty required "
                    f"frontmatter field '{field}'",
                )

        # related_topics: required presence; must be a list (empty allowed —
        # template default is `related_topics: []`).
        if "related_topics" not in fm:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: missing required frontmatter field "
                f"'related_topics' (use [] when none yet)",
            )
        elif not isinstance(fm.get("related_topics"), list):
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: related_topics must be a list "
                f"(got {type(fm.get('related_topics')).__name__})",
            )

        # Binding enums.
        rt = fm.get("relationship_type")
        if rt is not None and rt != "" and rt not in RELATIONSHIP_TYPES:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: relationship_type='{rt}' not in "
                f"{sorted(RELATIONSHIP_TYPES)}",
            )
        status = fm.get("status")
        if status is not None and status != "" and status not in STATUSES:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: status='{status}' not in "
                f"{sorted(STATUSES)}",
            )

        # Optional enums — validated only when present.
        pd = fm.get("profile_depth")
        if pd is not None and pd not in PROFILE_DEPTHS:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: profile_depth='{pd}' not in "
                f"{sorted(PROFILE_DEPTHS)} (optional field, but enum is fixed)",
            )
        tf = fm.get("touch_frequency")
        if tf is not None and tf not in TOUCH_FREQUENCIES:
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: touch_frequency='{tf}' not in "
                f"{sorted(TOUCH_FREQUENCIES)} (optional field, but enum is fixed)",
            )

        # Slug must match filename — slug is the join key everywhere.
        slug = fm.get("slug")
        if slug and f"{slug}.md" != path.name:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(path, ctx.repo)}: slug='{slug}' does not match "
                f"filename '{path.name}' — slug is the cross-reference join key",
            )

        # Archived profiles should carry status: archived.
        if in_archived and status != "archived":
            ctx.add(
                "low",
                CHECK_ID,
                f"{rel(path, ctx.repo)}: in _archived/ but "
                f"status='{status}' (expected 'archived')",
            )
