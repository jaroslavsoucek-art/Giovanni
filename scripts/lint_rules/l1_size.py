"""Lint rule: L1 operational memory line count.

Warn at config.l1_limit (default 300), critical at config.l1_limit_critical
(default 400). The cap exists to keep session-start cheap — at ~80 tokens
per line, 300 lines ≈ 24k tokens ≈ 12% of a 200k-token context.

Above 400 lines means L1 has stopped being a "cheap session start" and
needs aggressive shard graduation. See memory/README.md.
"""

CHECK_ID = "l1-size"


def run(ctx) -> None:
    l1 = ctx.l1_path()
    if not l1.is_file():
        return
    try:
        lines = sum(1 for _ in l1.open(encoding="utf-8"))
    except OSError:
        return

    warn = ctx.config["l1_limit"]
    crit = ctx.config["l1_limit_critical"]

    if lines > crit:
        ctx.add(
            "critical",
            CHECK_ID,
            f"{ctx.config['memory_dir']}/{ctx.config['l1_file']} = {lines} lines "
            f"(>{crit} hard limit — STOP adding, audit first per memory/README.md)",
        )
    elif lines > warn:
        ctx.add(
            "high",
            CHECK_ID,
            f"{ctx.config['memory_dir']}/{ctx.config['l1_file']} = {lines} lines "
            f"(>{warn} soft limit — classify before append, consider shard graduation)",
        )
