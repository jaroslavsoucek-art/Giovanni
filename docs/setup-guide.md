# Setup Guide — Fork Giovanni for Your Domain

> **Status:** WIP stub. This guide iterates as Setup2 (first real fork) surfaces actual fork-and-fill friction. Treat each section as "best current intent" — if your experience diverges, flag it and we'll update.

Giovanni is a **methodology framework**, not a working AI Chief of Staff. To get value from it, you fork the repo, fill it with your own domain content (constitution, stakeholder profiles, source configurations), and run the workflows.

This guide walks through the fork-and-fill process. Expect 4-8 hours of focused work to reach "first useful `/digest` run", and several weeks of iteration before the predictive layer (branch-out / shadow / calibration) starts producing accuracy signals.

## Prerequisites

- Claude Code installed (or Antigravity SDK — Giovanni is harness-agnostic in principle, but currently tested only on Claude Code)
- Git + GitHub account (or equivalent private repo host)
- PyYAML installed (`pip install pyyaml`) for governance lint
- A domain you operate in with: ≥5 named stakeholders, ≥1 multi-month strategic horizon, ≥3 configurable signal sources (chat / email / calendar / project tracker / etc.)
- ~4-8 hours initial setup time

## Step 1 — Fork the repo

```bash
# Clone Giovanni
git clone https://github.com/jaroslavsoucek-art/Giovanni.git <your-domain>-cos
cd <your-domain>-cos

# Set your own remote
git remote remove origin
git remote add origin <your-private-repo-url>
```

**Recommendation:** make this a private repo. Stakeholder profiles contain operational predictions and pattern observations about real people. See [`docs/stakeholder-profiles.md`](stakeholder-profiles.md) § Privacy considerations.

## Step 2 — Fill the constitution

Open `knowledge/constitution.template.md`, rename to `knowledge/constitution.md` (or `<domain>_constitution.md`), and replace placeholders with your domain content:

- **Identity & scope** — what initiative this constitution governs
- **Operating principles** — non-negotiable rules (e.g. "we don't sell to companies without a finance team", "platform + entity pricing, never per-seat")
- **Strategic posture** — competitive / differentiating sequencing
- **Stakeholder model** — high-level org map (specific profiles live in `memory/stakeholders/`)
- **Architecture** — how the work works (config layer vs core, integration model, etc.)
- **Commercial model** — pricing, contracts, revenue dynamics
- **Compliance posture** — regulatory, legal, audit requirements
- **Active blockers** — top 3-5 things currently blocking progress (graduates to `memory/topics/<slug>.md` once they have >5 sub-items)

**Discipline:** every section needs an anchor ID (`{#section-name}`). Section status badge (`RESOLVED` / `OPEN` / `SUPERSEDED`). Decision back-pointers where applicable.

**Time:** 1-2 hours to draft initial constitution. Expect to revise weekly for first month as gaps surface.

## Step 3 — Bootstrap stakeholder profiles

Pick **5-10 most-frequently-interacted-with people** in your domain. For each, create `memory/stakeholders/<slug>.md` from `memory/templates/stakeholder.template.md`.

Required frontmatter fields (lint catches if missing):
- `slug` — must match filename (lowercase, hyphens)
- `display_name`, `org`, `role`
- `relationship_type` — one of: `peer` | `asymmetric-power-up` | `asymmetric-power-down` | `customer` | `vendor` | `counterparty`
- `status`, `profile_depth`, `touch_frequency`, `last_touch`
- `primary_thread`, `related_topics`

Required body sections (workflow stress-tested):
- Identity & context · Role & decision authority · Sentiment trajectory (append-only time-series) · Communication style · Active threads · Hot topics in their head · Predicted reactions · Watch points · Relationship history · Reasoning / source links

**Time:** ~30 min per profile for first-pass depth (`partial`). Deepen iteratively as interactions accumulate.

**Tool:** invoke `profile-bootstrap` agent for any stakeholder you want auto-populated from chat/email/calendar/project-tracker signal. See [`.claude/agents/profile-bootstrap.md`](../.claude/agents/profile-bootstrap.md).

## Step 4 — Configure signal sources

Open `memory/digest-sources.template.md`, rename to `memory/digest-sources.md`, configure your actual sources.

`source_type` enum (generic) maps to your actual tools:
- `chat-platform` → Slack / Teams / Discord / etc.
- `email` → Gmail / Outlook / etc.
- `calendar` → Google Cal / Outlook / etc.
- `project-tracker` → Asana / Linear / Jira / etc.
- `version-control` → GitHub / GitLab / etc.
- `crm` → Salesforce / HubSpot / etc.
- `documentation-platform` → Confluence / Notion / SharePoint / etc.

**Discipline:** quality > quantity. 3-5 well-targeted sources beat 10 noisy ones. First-pass: configure 2-3 most-trafficked, iterate based on digest signal quality.

**Time:** ~30 min initial config + tuning over first 2 weeks.

## Step 5 — Wire MCP tools to source-puller

`source-puller` agent is generic — it doesn't know your actual MCP server identifiers. Fork-time wiring:

1. Edit `.claude/agents/source-puller.md` frontmatter `tools:` list, append your MCP tool identifiers (e.g. `mcp__<your-slack-id>__slack_read_channel`, etc.)
2. Update body's "Tool routing per source_type" section to map your `source_type` enum values to actual MCP tool calls

**Time:** ~15-30 min if your MCP tools are already configured. Hours if not.

## Step 6 — Install hooks + verify lint

```bash
bash scripts/install-hooks.sh
bash scripts/lint.sh
```

Expected: lint clean (your fork starts with empty `memory/topics/`, `memory/decisions/`, etc. — only constitution + stakeholders + sources populated).

If lint fails, see [`docs/governance.md`](governance.md) § "Lint framework" for rule-by-rule debugging.

## Step 7 — First `/digest` run

```
/digest --force
```

(`--force` overrides the 4 h cadence guard on first run.)

Expected output sections:
- **Top of mind** — synthesized signal across sources
- **Briefs ready** — auto-generated for any high-prep events in next 48 h
- **Drift flags** — contradictions between memory/constitution and reality (likely thin on first run)
- **Triage** — branch-out candidates / shadow-only / declined
- **Watch** — expiring acks, expired shadow hypotheses (none yet)

**First run is exploratory.** Iterate sources config based on signal quality. Within 1-2 weeks, signal-to-noise should stabilize.

## Step 8 — First `/branch-out`

When you have a high-stakes decision coming up with ≥2 deep-profile stakeholders:

```
/branch-out <situation-slug>
```

The simulation produces a per-actor moves table + trade-off matrix. **No "recommended move"** — the matrix is generative, you decide. See [`docs/prediction.md`](prediction.md) § "8 binding principles".

**Critical:** if `/branch-out` hard-stops because ≥2 actors are shallow, **deepen profiles first**. Don't override.

## Step 9 — Monthly `/calibration-report`

After 30 days of digest runs (shadow hypotheses accumulating):

```
/calibration-report
```

Produces per-actor accuracy aggregation. Initial reports are noisy due to small N — useful patterns emerge after 60-90 days.

## Step 10 — Quarterly `/shadow-review`

After 90 days:

```
/shadow-review
```

Manual audit of resolved shadow hypotheses with adversarial lookback. **Default to skeptical** — see [`docs/prediction.md`](prediction.md) § "Adversarial lookback".

## What to expect month-by-month

| Month | Realistic state |
|---|---|
| 1 | Constitution drafted but revising weekly; 5-10 profiles bootstrapped; first digest runs noisy; first branch-out maybe |
| 2 | Sources config stabilized; signal-to-noise improving; first shadow hypotheses resolving; 10-15 profiles |
| 3 | First /calibration-report (noisy but useful); first /shadow-review (small N); constitution stable |
| 6 | Predictive layer producing actionable accuracy patterns; calibration noticing per-actor bias; routine drift detection working |
| 12 | Framework is operational tempo; minimum viable maintenance |

## Failure modes

- **Constitution bloat** — if you exceed 1500 lines, you're putting decision content where it should be in `memory/decisions/`. Graduate sections out.
- **Profile shallow-stuck** — if a key stakeholder's profile stays `shallow` for >30 days, something is broken in your signal access. Investigate before next /branch-out involving them.
- **Triage volume explosion** — if active branch-outs >3/day OR shadow >25/day, threshold creep. Don't silently raise thresholds; force re-evaluation per [`memory/triage-heuristic.template.yaml`](../memory/triage-heuristic.template.yaml).
- **Calibration overconfidence** — if monthly overall accuracy >80%, suspect motivated reasoning, not victory. Run `/shadow-review` immediately.
- **Drift flag noise** — if 80% of digest drift flags are noise (false positives), tighten source configs and constitution scope.

## What to do when this guide is wrong

This guide is WIP — written from the architect-side, not from a real fork. If your fork experience diverges:

1. **Document the friction** in a notes file alongside your work
2. **Flag it** by opening a discussion or issue in your Giovanni fork's tracker (or upstream if patching)
3. **Patch this guide** — Setup2 iterations are the canonical truth. Architect-side intent is just hypothesis.

## Cross-references

- [`docs/setup1-complete.md`](setup1-complete.md) — what Setup1 actually shipped, what it didn't include
- [`docs/governance.md`](governance.md) — discipline rules, hard limits, audit cadence
- [`docs/prediction.md`](prediction.md) — 8 binding principles for predictive layer
- [`docs/stakeholder-profiles.md`](stakeholder-profiles.md) — bootstrap criteria, refresh cadence, privacy
- [`docs/adversarial.md`](adversarial.md) — adversarial-review-as-default policy
- [`docs/digest.md`](digest.md) — daily digest policy + workflow rationale
- [`docs/agents.md`](agents.md) — agent design patterns, when to spawn
- [`docs/slash-commands.md`](slash-commands.md) — slash command argument conventions

## Open questions (await Setup2 to resolve)

- Real fork-time wiring time for MCP tools per source_type — is "15-30 min" realistic?
- Real first-month constitution revision cadence — is weekly the right rhythm?
- Real shadow hypothesis volume per day — does the default triage heuristic hold up?
- Real adversarial-reviewer adoption — do principals actually invoke `/review` before sending?
- Real calibration utility — does the monthly report change behavior or just gather dust?

These get answered in Setup2 retrospectives. This guide updates accordingly.
