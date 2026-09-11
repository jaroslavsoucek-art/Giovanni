"""Lint rule: L1 operational memory byte size.

The line-count cap (`l1-size`) measures the wrong thing on its own. Lines are a
proxy for reading cost, and the proxy breaks the moment the file contains long
paragraphs instead of short bullets — which is exactly what happens as a fork
matures and L1 starts carrying narrative instead of state.

Measured in the implementation this framework came from: 201 lines (comfortably
under the 300-line cap) and 58 KB — nearly twice the byte budget, paid at every
session start, with no check firing.

Two caps, two failure modes. Whichever trips first, trips.
"""

CHECK_ID = "l1-byte-size"
SEVERITY = "high"


def run(ctx) -> None:
    l1 = ctx.l1_path()
    if not l1.is_file():
        return
    try:
        size = l1.stat().st_size
    except OSError:
        return

    limit = int(ctx.config["l1_limit_bytes"])
    if size <= limit:
        return

    try:
        lines = sum(1 for _ in l1.open(encoding="utf-8")) or 1
    except OSError:
        lines = 1

    ctx.add(SEVERITY, CHECK_ID,
            f"{ctx.config['memory_dir']}/{ctx.config['l1_file']} = {size // 1024} KB "
            f"(max {limit // 1024} KB; ~{size // lines} chars/line). Long paragraphs in L1 are a "
            "graduation signal, not a formatting problem — move the topic to "
            "memory/topics/<slug>.md and leave 1-3 lines plus a pointer.")
