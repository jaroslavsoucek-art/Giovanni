"""Lint rule: hooks must not use commands that exist on only one platform.

Hooks run wherever the fork runs — a laptop today, an ephemeral Linux container
tomorrow. A platform-only command does not fail loudly. It either skips the check
it was guarding (BSD `date -j` on Linux: every freshness warning silently no-ops)
or aborts the hook outright (GNU `timeout` on stock macOS: command not found).
Both directions are silent enough to survive months.

Portable spellings:
  dates             -> python3 datetime (see .claude/hooks/session-start-digest.sh)
  bounded network   -> `command -v timeout || command -v gtimeout` with a fallback,
                       or the tool's own timeout knobs

Comment lines are skipped: quoting a forbidden command while documenting the rule
is not a use of it.
"""

import re

CHECK_ID = "hooks-portable-date"
SEVERITY = "high"

NONPORTABLE = [
    (re.compile(r"(^|[^\w-])date\s+-j\b"),
     "BSD-only `date -j` — on Linux the check it guards silently no-ops. Use python3 datetime."),
    (re.compile(r"(^|[;&|(]\s*)timeout\s+\d"),
     "GNU-only `timeout` in command position — absent on stock macOS, the hook dies. "
     "Probe with `command -v timeout` and fall back."),
    (re.compile(r"(^|[^\w-])(stat\s+-f|readlink\s+-f)\b"),
     "Platform-divergent flag (`stat -f` is BSD, `readlink -f` is GNU). Use python3 os.path."),
]


def run(ctx) -> None:
    hooks_dir = ctx.repo / ".claude" / "hooks"
    if not hooks_dir.is_dir():
        return
    for path in sorted(hooks_dir.glob("*.sh")):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("#"):
                continue
            for pattern, message in NONPORTABLE:
                if pattern.search(line):
                    ctx.add(SEVERITY, CHECK_ID,
                            f".claude/hooks/{path.name}:{i}: {message}")
