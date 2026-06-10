"""Lint rule: deliverables lifecycle registry completeness.

Forks that opt into the deliverables registry track every output file in
`<deliverables_dir>/_registry.yaml` (entries: {file, status, type, date,
note}). Status lives in metadata, not in the file path — a status flip is
a YAML edit, never a rename/move (anti-link-rot).

This rule is OPT-IN — it is a no-op when `<deliverables_dir>/_registry.yaml`
does not exist (same scaffold-tolerance pattern as adversarial_verdict_format).
The registry only pays for itself once a flat output directory exceeds
roughly 50 files.

When the registry exists, the rule checks (severity high):
  - every entry has the required fields: file, status, type, date
  - status is in the enum {live, draft, sent, superseded}
  - every entry points to an existing file (no orphan entries)
  - every top-level file in <deliverables_dir>/ has a registry entry
    (no unregistered files)
  - no duplicate entries for the same file

Out of registry scope (skipped when scanning the directory):
  - `_archive/` and any other name starting with `_` (incl. _registry.yaml)
  - dotfiles (.gitkeep, .DS_Store, ...)
  - README.md, REGISTRY.md (the generated view itself)
  - `*.template.yaml` scaffolding

Freshness of the generated REGISTRY.md vs a `--dry` regen is the bash-side
`registry-stale` check in scripts/lint.sh (same pattern as index-stale /
map-stale), not this rule.
"""

from __future__ import annotations

CHECK_ID = "deliverables-registry"
SEVERITY = "high"

ALLOWED_STATUSES = {"live", "draft", "sent", "superseded"}
REQUIRED_FIELDS = ("file", "status", "type", "date")
SKIP_NAMES = {"README.md", "REGISTRY.md", ".gitkeep"}


def run(ctx) -> None:
    from lint import rel, HAVE_YAML  # type: ignore[import-not-found]

    deliv = ctx.deliverables_dir()
    registry_yaml = deliv / "_registry.yaml"
    if not deliv.is_dir() or not registry_yaml.is_file():
        # Registry not adopted by this fork — rule is a no-op.
        return

    if not HAVE_YAML:
        ctx.add(
            "low",
            CHECK_ID,
            "PyYAML not installed — deliverables registry checks skipped",
        )
        return

    import yaml  # type: ignore[import-not-found]

    try:
        data = yaml.safe_load(registry_yaml.read_text())
        entries = (data or {}).get("entries") or []
    except Exception as exc:
        ctx.add(
            "critical",
            CHECK_ID,
            f"{rel(registry_yaml, ctx.repo)}: unparseable — {exc}",
        )
        return

    registered: set[str] = set()
    for e in entries:
        if not isinstance(e, dict):
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(registry_yaml, ctx.repo)}: entry is not a mapping: {e!r}",
            )
            continue
        fname = e.get("file")
        missing = [f for f in REQUIRED_FIELDS if not e.get(f)]
        if missing:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(registry_yaml, ctx.repo)}: entry "
                f"{fname or '(no file field)'}: missing required field(s) "
                f"{', '.join(missing)}",
            )
        if not fname:
            continue
        if fname in registered:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(registry_yaml, ctx.repo)}: duplicate entry for '{fname}'",
            )
        registered.add(fname)
        status = e.get("status")
        if status and status not in ALLOWED_STATUSES:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(registry_yaml, ctx.repo)}: '{fname}' has invalid "
                f"status '{status}' (allowed: {sorted(ALLOWED_STATUSES)})",
            )
        if not (deliv / fname).exists():
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(registry_yaml, ctx.repo)}: entry points to missing "
                f"file: {rel(deliv / fname, ctx.repo)} — remove the entry or "
                f"restore the file (files are never renamed/moved on status flip)",
            )

    # Every top-level file must be registered.
    for item in sorted(deliv.iterdir()):
        if item.name.startswith("_") or item.name.startswith("."):
            continue
        if item.name in SKIP_NAMES or item.name.endswith(".template.yaml"):
            continue
        if not item.is_file():
            continue
        if item.name not in registered:
            ctx.add(
                SEVERITY,
                CHECK_ID,
                f"{rel(item, ctx.repo)}: missing registry entry — add to "
                f"{rel(registry_yaml, ctx.repo)} (status: draft is the default "
                f"for new files), then regenerate REGISTRY.md",
            )
