---
description: Bootstrap or refresh an instance's skills from the principal's chat-app history — extract a claude.ai data export into a private gitignored workspace, triage it, have analysts write de-identified workflow specs per recurring job, and after the principal's review convert the approved ones into skills, house style and provenance behind a PII gate.
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/history/*), Bash(git status *), Bash(git diff *), Bash(bash ${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh *), Read, Write, Edit, Glob, Grep, Agent
disable-model-invocation: true
argument-hint: "<export.zip|dir> | review | apply [--only c01,c02] | package"
---

# /giovanni:learn-history

Someone who has used the chat app for months already has their workflows: the same kind of ask, the same corrections, the same output shape, many times over. This skill turns that history into the instance's first skills instead of a builder's guess. It is a **thin shell** over three scripts and one agent; the procedure is [`procedure.md`](procedure.md).

1. **Extract** — `scripts/history/extract.py`: the official data export → normalised transcripts, projects, artifacts, memories in a workspace that never enters git.
2. **Analyse** — `scripts/history/triage.py` (deterministic: work/personal, clusters, sample) → `giovanni:history-analyst` per cluster (parallel) → `scripts/history/convert.py review` (one review page + decisions file). **Stops for the principal.**
3. **Convert** — `scripts/history/convert.py apply`: approved specs → `.claude/skills/<slug>/`, house style, merge-into references, provenance — staged, PII-scanned, then copied. **No commit.**

## Usage

```
/giovanni:learn-history ~/Downloads/data-2026-10-23.zip   # steps 1–2, stops at review
/giovanni:learn-history review                            # rebuild the review page after spec edits
/giovanni:learn-history apply                             # step 3 for every decided item
/giovanni:learn-history apply --only c01,c04              # step 3 for some
/giovanni:learn-history package                           # zips for upload to the chat app
```

## Pre-flight (binding — STOP on failure)

1. The project has a `learning.history` block in `docs/governance.config.yaml` (workspace, language, keywords, PII patterns). Without it there is no PII gate — STOP and say what to add (template: `${CLAUDE_PLUGIN_ROOT}/templates/governance.config.template.yaml` § learning.history).
2. The workspace (default `.history/`) is in `.gitignore`. Check with `git check-ignore -q .history/x`. Not ignored → STOP; add it first. This is the line between a private analysis and personal data in a git history.
3. PyYAML importable (`python3 -c "import yaml"` via the scripts' own error). Missing → STOP.
4. For `apply`: `review/decisions.yaml` exists and at least one decision is not `pending`.

## Output behavior

- Writes inside the workspace: everything in steps 1–2, staging for step 3, packages.
- Writes in the repo, step 3 only: `.claude/skills/<slug>/{SKILL.md,format.md}`, `.claude/skills/<existing>/references/learned-<slug>.md` + one pointer line, the house-style doc, the learned-skills block in `CLAUDE.md`, `memory/learning/history-<date>.md`. Never overwrites an existing file (writes `<name>.proposed` beside it), except appending to the house-style doc.
- Never commits. Never uploads anything — `package` makes zips; the principal uploads them.

## Anti-patterns (binding)

- Reading transcripts in the main thread. The analysts read them; the main thread reads specs, triage and review pages. Quoting a transcript into chat puts personal data where it can be copied anywhere.
- Analysing conversations triage classed `personal`, or summarising them in any form.
- Running `apply` on decisions the principal did not make. `pending` stays pending; a headless run never applies.
- Deleting the workspace on the principal's behalf. Offer it at the end; it is theirs.
- Copying a PII hit "with a note to fix later". The gate exists so the repo never holds it.

## Cross-references

- Procedure: [`procedure.md`](procedure.md)
- Agent: `${CLAUDE_PLUGIN_ROOT}/agents/history-analyst.md`
- Scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/history/{extract,triage,convert,pii}.py`
- Lint: `pii-scan` (workspace never tracked; learned files carry no identifiers)
- Mechanism doc: `${CLAUDE_PLUGIN_ROOT}/docs/history-bootstrap.md`
