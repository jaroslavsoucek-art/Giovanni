# Learning from chat history — `/giovanni:learn-history`

An instance usually starts empty and learns from use. Most principals, though, arrive with months of chat-app history in which they already did their recurring work: the same ask, the same corrections, the same output shape, many times. That history is a better first set of skills than anything a builder would guess, and it encodes the one thing a builder never knows — **the format the principal actually accepts**.

This mechanism reads that history once (and again after each re-export), proposes skills, and converts only what the principal approves. It is built around one constraint: the history is full of other people's data, and the repo must never hold any of it.

## The three steps

| Step | What runs | Reads | Writes | Stops |
|---|---|---|---|---|
| 1 Extract | `scripts/history/extract.py` | the official data export (zip or dir) | workspace: `raw/` transcripts, projects, artifacts, memories; `index.jsonl`; `manifest.json` | — |
| 2a Triage | `scripts/history/pii.py harvest`, `scripts/history/triage.py` | `index.jsonl`, `raw/` | workspace: `denylist.txt`, `triage/{clusters.json,workplan.json,triage.md}` | asks once: split right? which clusters? |
| 2b Analyse | `giovanni:history-analyst` × clusters (parallel) | sampled transcripts + project instructions | workspace: `specs/<id>.yaml` | — |
| 2c Review | `scripts/history/convert.py review` | specs | workspace: `review/{review.md,decisions.yaml}` | **stops for the principal** |
| 3 Convert | `scripts/history/convert.py apply` | specs + decisions | staging → PII gate → repo: skills, house style, references, `CLAUDE.md` block, `memory/learning/` | no commit |

`convert.py package` additionally zips learned skills for upload back into the chat app, renamed `<slug>-web` so the uploaded copy and the repo copy do not collide when the chat app syncs skills into Claude Code.

## Why each step is shaped the way it is

- **The export, not scraping.** It is the only complete, supported copy. Its JSON is not a published schema, so `extract.py` counts unknown keys into `manifest.json` and fails loudly when `conversations.json` is missing or reshaped. `--inspect` shows what an export contains before anything is written.
- **The workspace lives inside the project, gitignored.** The principal reviews the triage and the proposals in the same app the assistant runs in, and the app's file pane opens project files only. `init` puts `.history/` in `.gitignore`; the `pii-scan` lint rule fails CRITICAL for any tracked file under it.
- **Deterministic triage before any model reads.** A year of history is hundreds of conversations. Clustering by project and TF-IDF over the principal's own messages is free, and it is what decides which few transcripts a model reads. Personal conversations are counted and never read — not clustered, not sampled, not summarised.
- **One analyst per cluster, a sample, never the main thread.** The main thread reads specs, never transcripts. A transcript quoted into chat is personal data in a place it can be copied from.
- **Accepted ≠ produced; corrections are rules.** The analyst describes the output the principal kept, and turns every "no, …" into a generalised rule with evidence. That is where the instance's house style comes from.
- **A project's templates travel with the skill.** A cluster seeded by a chat-app project copies that project's instructions and knowledge docs into the skill's `references/` — they are usually the principal's own templates, the output format in its purest form, and in Claude Code there is no project around the skill to supply them. They pass the same PII gate.
- **The principal decides; a script converts.** Specs are YAML so the review is about content, and the conversion is deterministic so the same decision always produces the same files. `apply` never overwrites: a changed proposal for an existing skill lands as `SKILL.md.proposed`.
- **Three PII layers.** Shape patterns (built-in + `pii_patterns`), a denylist of names harvested from the export (stored in the workspace; it is personal data itself), and the principal's review. `apply` stages, scans the staging tree, and copies nothing if anything matches.

## Configuration (`docs/governance.config.yaml`)

The skill refuses to run without this block; it is also what activates the `pii-scan` lint rule.

```yaml
learning:
  history:
    workspace: .history            # MUST be in .gitignore
    language: en                   # review page + generated skills: en | cs
    domain_hint: >                 # one paragraph the analysts read
      <who the principal is, what they produce, for whom>
    work_projects: null            # chat-app project names that are work; null = every project
    work_keywords: []              # a hit marks a conversation as work
    personal_keywords: []          # a hit (and no work hit) marks it personal: counted, never read
    name_cues: []                  # extra role words that precede a name ("debtor", "client")
    pii_patterns:                  # identifiers with a shape, beyond e-mail / phone / IBAN / card
      - {name: national-id, regex: '\b\d{6}/?\d{3,4}\b'}
    house_style: knowledge/house-style.md
    pii_scan_paths: []             # extra repo paths for the pii-scan rule
```

`CLAUDE.md` may carry a block the conversion maintains — a table of learned skills:

```markdown
<!-- giovanni:learned-skills -->
<!-- /giovanni:learned-skills -->
```

## What the workspace keeps between runs

`overrides.yaml` (the principal's work/personal corrections), `denylist.txt` (harvested names plus lines marked `# manual`), and `review/decisions.yaml`. A re-export therefore only asks about what is new. Deleting the workspace is the principal's call; the skill offers it, never does it.

## Limits, stated

- The export format is observed, not specified. The self-test (`scripts/history/selftest.py`) runs against a synthetic export shaped like a real one; the first real export is the real test, which is why `--inspect` exists.
- Name detection is cue-based. A name that never follows a role word or honorific, and is not in the denylist, is caught only by the principal's review.
- The analysts see a sample (default 5 per cluster). A rule that appears only in an unsampled conversation is missed until a re-run samples it.
