# Memory archive — YYYY-MM

<!--
Monthly archive aggregation. Items moved out of L1 (CLAUDE_MEMORY.md) and
optionally L2 (resolved sub-blockers) during the month, with their original
wording preserved for audit trail + reasoning for why they were archived.

Filename: memory/archive/YYYY-MM.md (one per calendar month).

This file is APPEND-ONLY. Never edit existing entries — archives are
write-once. If a fact in an archive entry turns out to be wrong, write a
correction at the bottom rather than rewriting history.

Retention: forever. Archives are the audit trail for "what did we think then,
how did it actually play out".
-->

> Archived from `memory/CLAUDE_MEMORY.md` during monthly audit **YYYY-MM-DD** (commit: `<hash>`).
> Items below were DONE / superseded / OBSOLETE but still occupied space in live memory.
> For provenance: `git log memory/CLAUDE_MEMORY.md` before the audit commit.

---

## A. Resolved blockers

<!--
Blockers that were active in L1 during the month and resolved. One sub-section
per blocker.

For each:
- Original wording (verbatim quote from L1 at time of archival)
- Why archived (1-3 sentences — what changed, where the canonical record now
  lives)
- Pointer to the decision record or knowledge doc that contains the resolution
  (when applicable)

The verbatim quote matters. Months later, "what was the exact wording when
we still thought X was a problem" is a real question.
-->

### Blocker #<N> — <Original blocker name> (<RESOLUTION TYPE> YYYY-MM-DD)

> Original wording in live memory:

> <Verbatim original line(s) from L1>

**Why archived:** <reason>. <Where canonical record now lives — pointer.>

---

### Blocker #<N> — <Original blocker name> (<RESOLUTION TYPE> YYYY-MM-DD)

> Original wording:

> <Verbatim original>

**Why archived:** <reason>.

---

## B. Done meetings / chases (from "On the horizon" / "This week")

<!--
This-week / on-the-horizon items that completed. Lower-rigor than blockers —
typically just the original wording + a DONE timestamp + outcome.
-->

### <Item description> → DONE YYYY-MM-DD

> Original wording:

> <Verbatim>

<Optional 1-2 line outcome summary if material.>

---

### <Item description> → DONE YYYY-MM-DD

> Original wording:

> <Verbatim>

---

## C. Graduated to topic shards

<!--
Items that grew large enough during the month to graduate from L1 to L2 shards.
For each: when graduated, where the shard now lives.

This section is for traceability — letting future audits find when a topic
went from "1 line in L1" to "100-line shard".
-->

- **<Topic name>** graduated YYYY-MM-DD → `memory/topics/<slug>.md`
- **<Topic name>** graduated YYYY-MM-DD → `memory/topics/<slug>.md`

---

## D. Extracted to decision records

<!--
L1 items that were extracted into formal `memory/decisions/<...>.md` records
during the month. Different from "resolved blockers" — these may still be
active but with their detail moved out of L1.
-->

- **<Decision>** extracted YYYY-MM-DD → `memory/decisions/<date>-<slug>.md`
- **<Decision>** extracted YYYY-MM-DD → `memory/decisions/<date>-<slug>.md`

---

## E. Verbatim transcripts / large artifacts

<!--
Optional. If a long meeting transcript, threaded-comment dump, or other
verbatim artifact was previously sitting in L1 / L2 and got moved here during
audit, it goes in this section.

Use sub-headings per artifact (e.g. "## E1. <Meeting name> YYYY-MM-DD transcript").

Length: this section can be long — verbatim transcripts are often hundreds of
lines. That's fine, archives are read-rarely. If a single transcript is
>500 lines, consider moving it out of memory entirely to `deliverables/` or
a separate `archive/transcripts/` subdirectory.
-->

### E1. <Event / artifact name> — YYYY-MM-DD

<!-- Verbatim content here. -->

<Verbatim transcript / comments / dump>

---

## F. Corrections to prior archive entries

<!--
If a previously archived item turns out to have been wrong, correct it here
rather than editing the historical entry. Format:

### Correction to <section> / <item> (archived YYYY-MM-DD)

Original entry claimed: <what>.
Actual: <what>.
Discovered: YYYY-MM-DD via <source>.

This preserves the original (showing what was believed at the time) while
making the correction discoverable.
-->

<None unless needed.>
