"""Lint rule: L1 strikethrough ratio.

Strikethrough (`~~text~~`) is acceptable for ≤1 session as a "verify before
archive" marker. Persistent strikethrough = soft delete = drift. Above
config.strike_ratio_max (default 2 %) signals cleanup overdue. Above 2.5×
that → critical.

See memory/README.md "No strikethrough as soft-delete".
"""

CHECK_ID = "l1-strikethrough-ratio"


def run(ctx) -> None:
    l1 = ctx.l1_path()
    if not l1.is_file():
        return
    try:
        text = l1.read_text(encoding="utf-8")
    except OSError:
        return

    lines_all = text.splitlines()
    total_lines = len(lines_all)
    if total_lines == 0:
        return

    strike_lines = sum(1 for ln in lines_all if "~~" in ln)
    if strike_lines == 0:
        return

    ratio = strike_lines / total_lines
    max_ratio = float(ctx.config["strike_ratio_max"])
    critical_ratio = max_ratio * 2.5

    pct = ratio * 100
    max_pct = max_ratio * 100

    if ratio > critical_ratio:
        ctx.add(
            "critical",
            CHECK_ID,
            f"{ctx.config['memory_dir']}/{ctx.config['l1_file']} strikethrough "
            f"{strike_lines}/{total_lines} ({pct:.1f}% > {max_pct * 2.5:.1f}% hard limit) — "
            "archive resolved items in same commit per memory/README.md",
        )
    elif ratio > max_ratio:
        ctx.add(
            "medium",
            CHECK_ID,
            f"{ctx.config['memory_dir']}/{ctx.config['l1_file']} strikethrough "
            f"{strike_lines}/{total_lines} ({pct:.1f}% > {max_pct:.1f}%) — "
            "archive resolved items instead",
        )
