"""Lint rule: domain-leak denylist.

Configurable allowlist/denylist for catching prior-domain content carry-over
during a fork. Set `domain_leak_denylist` in `docs/governance.config.yaml`
to a list of strings (proper nouns from the prior domain). Each occurrence
across `memory/` + `knowledge/` is flagged.

Default denylist is empty — fork-time activity.

Match is case-insensitive substring against the file body. Hits are
reported per-file with line numbers. Allowed contexts (a configurable
list of file paths via `domain_leak_allowlist`) are skipped — useful for
e.g. `docs/origin.md` which legitimately references the source domain.
"""

CHECK_ID = "domain-leak"


def run(ctx) -> None:
    from lint import rel  # type: ignore[import-not-found]

    denylist = ctx.config.get("domain_leak_denylist") or []
    if not denylist:
        return
    if not isinstance(denylist, list):
        return

    allowlist = ctx.config.get("domain_leak_allowlist") or []
    if not isinstance(allowlist, list):
        allowlist = []
    allow_set = set(allowlist)

    # Scan memory + knowledge + .claude (hooks / agents)
    scan_roots = [
        ctx.memory_dir(),
        ctx.knowledge_dir(),
        ctx.repo / ".claude",
    ]
    # Also scan top-level CLAUDE.md / README.md
    for top in ("CLAUDE.md", "README.md"):
        p = ctx.repo / top
        if p.is_file():
            scan_roots.append(p)

    needles = [(n.lower(), n) for n in denylist if isinstance(n, str) and n]
    if not needles:
        return

    for root in scan_roots:
        if root.is_file():
            paths = [root]
        elif root.is_dir():
            paths = list(root.rglob("*.md")) + list(root.rglob("*.sh")) + list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))
        else:
            continue
        for path in paths:
            rel_path = rel(path, ctx.repo)
            if rel_path in allow_set:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            lower = text.lower()
            for needle_lc, needle_orig in needles:
                if needle_lc not in lower:
                    continue
                # Find first line number for context
                first_line = None
                for lineno, ln in enumerate(text.splitlines(), start=1):
                    if needle_lc in ln.lower():
                        first_line = lineno
                        break
                ctx.add(
                    "high",
                    CHECK_ID,
                    f"{rel_path}:{first_line or '?'}: prior-domain term "
                    f"'{needle_orig}' present — sanitize for generic fork",
                )
