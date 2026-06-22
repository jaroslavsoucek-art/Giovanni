# Digest sources config

<!--
============================================================================
Lattice Finance fork — configures which sources the daily digest pulls each run.
Edited without touching the workflow itself — keeps source mechanics decoupled
from procedure logic.

The digest workflow (.claude/workflows/daily-digest.md) reads this file at
Step 2 and spawns one source-puller agent per entry in Step 4.

============================================================================
SOURCE DISCIPLINE
============================================================================
Quality > quantity. 3-5 well-targeted sources beat 10 noisy ones.

When in doubt: omit. A digest with too many low-signal sources buries the
signal in raw bullets. Sources can always be added later via decision record.

Anti-patterns:
- Adding a chat channel because "we might miss something there" → unspecific
  use case = noise.
- Adding every project tracker board → too many low-signal task moves.
- Adding global "all mentions" filters → unbounded scope, no retention rules.

============================================================================
-->

## Source entries

<!--
Schema per entry:

- source_type: <enum>
  identifier: <platform-specific identifier>
  time_window_override: <optional ISO 8601 duration, e.g. "P7D" — overrides
                        default digest window for this source only>
  priority: <high | medium | low>  — triage hint for synthesis, NOT a strict
                                     ordering. high = always include even if
                                     volume low.
  notes: <one-line context — why this source matters, what to watch for>
  feeds: <optional, project-tracker only — multi-feed list, see that section>

source_type enum (matches source-puller agent):
  chat-platform           — Slack, Teams, Discord, Mattermost
  email                   — Outlook, Gmail, IMAP
  calendar                — Outlook Calendar, Google Calendar
  project-tracker         — Asana, Linear, Jira, GitHub Issues
  version-control         — Git, GitHub, GitLab
  crm                     — Salesforce, HubSpot, Pipedrive
  documentation-platform  — Notion, Confluence, Google Drive
-->

### chat-platform

- source_type: chat-platform
  identifier: #strategy-private        # Alex + Morgan co-founder channel
  priority: high
  notes: Primary co-founder decision channel; pricing-v2, dp1 renewal, VP Eng candor lives here.

- source_type: chat-platform
  identifier: #board-async             # board updates + async board commentary
  priority: high
  notes: Sarah / David / Marcus async board signal — Series B narrative reactions, burn scrutiny.

- source_type: chat-platform
  identifier: DMs:all
  priority: high
  notes: Direct messages to Alex — Priya pipeline pings, Morgan side-threads, recruiter updates.

<!--
DMs: `identifier: DMs:all` + `priority: high`.
Channels: one entry per channel. Standups / automated notifications are
suppressed at the agent level — see source-puller.md `chat-platform` section.
-->

### email

- source_type: email
  identifier: inbox (alex@lattice.io)
  priority: high
  notes: Relevance filtering at synthesis — surface messages touching topic shard slugs (dp1-renewal, vp-eng-hire, pricing-v2, series-b-prep) or profiled stakeholders; cluster the rest.

<!--
Default: pull Alex's primary inbox since last_run. No filter at pull time —
Step 4 source-puller emits all messages; Step 5 synthesizes; Step 12 renders
top-relevant + cluster-other.
-->

### calendar

- source_type: calendar
  identifier: Outlook (alex@lattice.io)
  priority: high
  notes: Suppress internal standups / focus blocks at pull time; brief eligibility applied at Step 7.
  brief_eligibility:
    include:
      - 1:1 with profiled stakeholder
      - decision meeting
      - external commercial conversation
      - board / exec event
      - negotiation
    exclude:
      - internal stand-ups
      - recurring blocks (focus time, lunch)
      - mechanical scheduling
  suppress_title_matching:
    - 1:1 <-- without named counterparty
    - Standup
    - Daily
    - Place
    - Focus
    - Lunch
    - Cancelled

<!--
suppress_title_matching: applied at pull time (source-puller hides matches).
brief_eligibility: applied at digest Step 7 (which events get briefs).

isCancelled events: suppress from main calendar list, emit separately so drift
detection can see them (an unexpected cancellation IS a signal).
-->

### project-tracker

- source_type: project-tracker
  identifier: Asana project 1209876543210000 (workspace 412345678901234)
  priority: medium
  notes: "Lattice 2026" project. Filter at synthesis: assignee=Alex OR follower=Alex.

<!--
Filter at synthesis (Step 5), not at pull time — the audit trail matters
("why is X showing up?" should be answerable from the bullets).

Single-feed behavior (no `feeds:` block) — all relevant task moves come from
the one "Lattice 2026" project; no externally-owned risk/decision log to
aggregate yet.
-->

### version-control

- source_type: version-control
  identifier: lattice-finance/lattice-monorepo
  priority: high
  notes: Drift-detection backbone — watch knowledge/, memory/, deliverables/ for unrecorded canonical edits.
  extra_context:
    - track_changelog: true
    - watch_paths: [knowledge/, memory/, deliverables/]

<!--
The version-control source is the drift-detection backbone. It catches:
- Knowledge / constitution edits since last_run that haven't been recorded
- CHANGELOG.md edits matched against commits
- Untracked decisions

The `extra_context.watch_paths` narrows the diff to paths that matter for
drift. Code-only commits typically don't trigger drift; knowledge / decision
commits do.
-->

<!--
crm + documentation-platform sources omitted for this fork:
- HubSpot pipeline signal is high-noise; Priya surfaces pipeline material via
  #strategy-private and DMs. Add later via decision record if Series B prep
  needs systematic pipeline ingestion.
- No documentation-platform (Notion/Confluence) in the stack — knowledge lives
  in the repo, caught by version-control.
-->

## Drift definition (active set)

<!--
Drift = canonical claim contradicted by reality. NOT: new information that
doesn't contradict. Distinguishing these is the most common digest-tuning
challenge.

Definitions appear here so the synthesis step (Step 10) has a fork-specific
checklist.
-->

- (a) Source claim X contradicts canonical claim Y (`knowledge/constitution.md` or an active topic shard).
- (b) Commits to canonical directories (`knowledge/`, `memory/decisions/`) since `last_run` not reflected in `CHANGELOG.md`. **Exempt:** auto-generated navigation files (`knowledge/INDEX.md`, `memory/MAP.md`) — they regenerate from the underlying content, not authored independently.
- (c) Profile sentiment trajectory shift detected by digest but not reflected in stakeholder profile.
- (d) Cross-file inconsistency inside `knowledge/` (decision record contradicts constitution).
- (e) Calendar / scheduling reality contradicts state recorded in topic shards.

## Branch-out integration (Step 6 / 8 / 11 inputs)

<!--
The predictive layer hooks into the digest at three steps. Pointers to the
canonical state for each step:
-->

- Triage thresholds: `memory/triage-heuristic.yaml`
- Canonical move names: `memory/branch-out/canonical-moves.md`
- Pending shadow hypotheses: `memory/shadow/pending/`
- Actor calibration scores: `memory/calibration/actor-scores.yaml`

## Memory ack policy

<!--
Governs the ack flow (Step 10 drift response + verbal ack).
-->

- Default expiry: 7 days
- "Permanent" ack: `expires = 9999-12-31` — use sparingly, signals documentation gap
- Auto-archive: expired acks → `## Expired acks` in `digest_state.md` at next digest run
- Re-flag: if drift still applies after expiry, re-flag at next drift detection

## Source pull failure handling

<!--
Source failures are common (auth expires, MCP connector down, rate limits).
The digest must degrade gracefully without fabricating data.

Rules:
1. Failed sources surface as system-hygiene flags, not silent drops.
2. One failed source does NOT abort the digest.
3. Failed source bullets MAY be retried by the principal manually (re-run the
   specific source-puller agent with same params); the digest itself doesn't
   auto-retry.
-->

- On source failure: emit `ERROR: <source-type>:<identifier> — <error>` bullet, flag in Step 12 system hygiene, continue with other sources.
- No fabricated data. Honest "source unavailable" > coverage theater.
