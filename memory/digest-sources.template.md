# Digest sources config

<!--
============================================================================
THIS IS A TEMPLATE. Copy to memory/digest_sources.md and edit per fork.

Configures which sources the daily digest pulls each run. Edited without
touching the workflow itself — keeps source mechanics decoupled from
procedure logic.

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
  identifier: <channel ID or DM scope>
  priority: <high | medium | low>
  notes: <why this channel matters>

<!--
DMs: typically `identifier: DMs:all` + `priority: high`.
Mentions: typically a separate entry, `identifier: mentions:@<principal>`.
Channels: one entry per channel ID. Resolve IDs to human-readable names in a
comment for legibility.

Suppression list (recurring stand-ups, automated notifications) lives at the
agent level — see source-puller.md `chat-platform` section.
-->

### email

- source_type: email
  identifier: <mailbox query, e.g. "inbox AND from:domain.com" or "inbox">
  priority: <high | medium | low>
  notes: <relevance filtering criteria — e.g. "filter by topic shard slugs">

<!--
Default: pull the principal's primary inbox since last_run. No filter at pull
time — Step 4 source-puller emits all messages; Step 5 synthesizes; Step 12
renders top-relevant + cluster-other.

The "relevance criteria" lives in the synthesis logic. Reasonable default:
domain-relevant messages (mentioning topic shards, named stakeholders, key
keywords) at top of render; other messages clustered into a single trailing
bullet.
-->

### calendar

- source_type: calendar
  identifier: <account or default>
  priority: high
  notes: <fork-specific suppression patterns>
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
  identifier: <project ID + workspace, or repo for issue-only trackers>
  priority: <high | medium | low>
  notes: <filter at synthesis: assignee=principal OR follower=principal>

<!--
Filter at synthesis (Step 5), not at pull time — the audit trail matters
("why is X showing up?" should be answerable from the bullets).

If the tracker has a CLI script (e.g. `scripts/<tracker>-pull.sh`), prefer
that for stability. Mention the script path in `notes`.
-->

### version-control

- source_type: version-control
  identifier: <repo path or remote URL>
  priority: high
  notes: <which directories matter — typically knowledge/, memory/, deliverables/>
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

### crm (optional)

- source_type: crm
  identifier: <pipeline name or owner=principal>
  priority: medium
  notes: <pipeline-specific filtering>

<!--
Omit entirely if the fork doesn't use a CRM. crm signal tends to be high-noise
unless filtered tightly to the principal's owned accounts.
-->

### documentation-platform (optional)

- source_type: documentation-platform
  identifier: <workspace or specific page tree>
  priority: low
  notes: <substantive edits only, not cosmetic>

<!--
Omit if not relevant. documentation-platform signals tend to be useful for
cross-team coordination but are low-signal for daily ops in a one-principal
context.
-->

## Drift definition (active set)

<!--
Drift = canonical claim contradicted by reality. NOT: new information that
doesn't contradict. Distinguishing these is the most common digest-tuning
challenge.

Definitions appear here so the synthesis step (Step 10) has a fork-specific
checklist. The list below is the source's default — adapt to the fork's
canonical artifacts.
-->

- (a) Source claim X contradicts canonical claim Y (constitution or active topic shard).
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
