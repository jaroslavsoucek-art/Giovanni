"""Lint rule: a "N days of silence" claim in live working state carries a fresh verification stamp.

The failure this exists for: a claim like "counter-proposal unanswered, 25 d" is
written once from one layer of a thread. Every later digest takes the claim as
input and adds the days since — 25 becomes 32 — and the growing number reads
as measurement. Nothing about it was measured. In the source implementation,
re-reading eight such claims against the actual threads found four rotten: one
thread had continued twice since the "unanswered" message, one question had been
answered within 27 hours two messages further down the same thread, one person
had replied a week earlier. Every one of them had raised the urgency of an item
in the principal's priority list.

None of the other checks could see it. Lint and semantic consistency checks
compare the repo against the repo; a consistent falsehood passes all of them.
The read doctrine's re-grounding gates (constitution promotion, deliverable
ship) never fire for L1 and topic shards — the layers that auto-load and where
claims live longest. This check is the gate for those layers.

Rule: a line that carries a silence keyword AND a duration counter must also
carry `[verified YYYY-MM-DD]` (optionally with the channel:
`[verified chat 2026-05-20]`), no older than `silence_stamp_max_days`.
There are exactly two legitimate forms:

  (a) re-read the source (the thread, not memory) and stamp it:
      "no reply for 26 d [verified chat 2026-05-20]"
  (b) rewrite it as a fact about the past, with no counter:
      "last documented message 2026-04-24 17:04 (from <person>)"
      — the reader does the subtraction, and this form cannot rot.

A stamp without a re-read is worse than none: it turns an unverified claim into
a certified one. Only the run that read the thread may stamp it.

Scope: the L1 file and active topic shards. Stakeholder profiles are out of
scope — their trajectory entries carry a date header, so they are past-fact by
construction. Extend the scope when rot shows up there.

Config (docs/governance.config.yaml or GIOVANNI_* env):
  silence_stamp_max_days  default 7
  silence_keywords        extra keywords for the fork's working language
                          (the English defaults below always apply)
"""

import datetime
import re

CHECK_ID = "silence-counter-verified"
SEVERITY = "high"

DEFAULT_KEYWORDS = [
    "silence", "silent", "unanswered", "no reply", "no replies", "no response",
    "no answer", "no reaction", "not answered", "not replied", "hasn't replied",
    "has not replied", "hasn't answered", "has not answered", "never replied",
    "still waiting", "ghosted",
]

COUNTER_RE = re.compile(r"\b\d+\s*(?:d|days?|wks?|weeks?|months?)\b|\b\d+\s*(?:×|x)(?![\w-])", re.I)
STAMP_RE = re.compile(r"\[verified(?: [A-Za-z0-9_-]+)? (\d{4}-\d{2}-\d{2})\]")


def _keyword_re(extra) -> "re.Pattern[str]":
    words = list(DEFAULT_KEYWORDS)
    if isinstance(extra, list):
        words += [str(w).strip() for w in extra if str(w).strip()]
    alternation = "|".join(re.escape(w) for w in sorted(set(words), key=len, reverse=True))
    return re.compile(rf"(?<!\w)(?:{alternation})(?!\w)", re.I)


def run(ctx) -> None:
    from lint import parse_frontmatter, rel  # type: ignore[import-not-found]

    max_days = int(ctx.config.get("silence_stamp_max_days", 7))
    silence_re = _keyword_re(ctx.config.get("silence_keywords"))
    today = ctx.today()

    targets = []
    l1 = ctx.l1_path()
    if l1.is_file():
        targets.append(l1)
    topics_dir = ctx.memory_dir() / "topics"
    if topics_dir.is_dir():
        for shard in sorted(topics_dir.glob("*.md")):
            if shard.name == "README.md":
                continue
            fm = parse_frontmatter(shard)
            if fm is not None and str(fm.get("status", "")).strip() == "resolved":
                continue
            targets.append(shard)

    for path in targets:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            if line.strip().startswith("<!--"):
                continue
            if not (silence_re.search(line) and COUNTER_RE.search(line)):
                continue
            m = STAMP_RE.search(line)
            where = f"{rel(path, ctx.repo)}:{n}"
            if not m:
                ctx.add("high", CHECK_ID,
                        f"{where}: silence counter without a verification stamp — re-read the thread "
                        f"and add `[verified YYYY-MM-DD]`, or rewrite as a past fact "
                        f"(\"last documented message <date>\") with no counter")
                continue
            try:
                stamp = datetime.date.fromisoformat(m.group(1))
            except ValueError:
                ctx.add("high", CHECK_ID, f"{where}: unparseable verification stamp `{m.group(0)}`")
                continue
            age = (today - stamp).days
            if age > max_days:
                ctx.add("medium", CHECK_ID,
                        f"{where}: verification stamp {stamp} is {age} d old (max {max_days}) — "
                        f"re-read the thread, or rewrite as a past fact")
