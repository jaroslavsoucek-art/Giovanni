"""Lint rule: digest state is a state file, not a journal.

Every digest run rewrites `digest_state.md`. Nothing should accumulate in it.
The failure is gradual and quiet: each run appends one more note about a
connector that misbehaved, none of them expire, and eventually session start
reads tens of kilobytes to learn one timestamp. Measured elsewhere: 68.5 KB,
cut to 24 KB once rotation existed — and none of the deleted text had been
read by anyone in months.

Durable connector lessons belong in `digest_sources.md`, which is meant to
accumulate. This file holds timestamps, counters, one sentence per source.
"""

CHECK_ID = "digest-state-size"
SEVERITY = "medium"


def run(ctx) -> None:
    state = ctx.memory_dir() / "digest_state.md"
    if not state.is_file():
        return
    try:
        size = state.stat().st_size
    except OSError:
        return
    limit = int(ctx.config["digest_state_limit_bytes"])
    if size > limit:
        ctx.add(SEVERITY, CHECK_ID,
                f"{ctx.config['memory_dir']}/digest_state.md = {size // 1024} KB "
                f"(max {limit // 1024} KB) — state file has turned into a journal. Rotate it: "
                "counters and one-sentence source health stay, per-run notes go, durable "
                "connector lessons move to digest_sources.md.")
