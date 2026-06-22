# Digest state

<!--
============================================================================
Lattice Finance fork — operational state for the daily digest workflow
(.claude/workflows/daily-digest.md). The session-start hook
(.claude/hooks/session-start-digest.sh) reads from this file to compute cadence
reminders. The digest workflow reads + writes it each run.

Persistence: this file IS committed to git. State changes commit in batch with
related principal action (drift confirms, ack additions, shadow lookback
resolutions). Do NOT commit on every digest run — only when the principal acts.

============================================================================
-->

## Last run

- timestamp: 2026-06-22T08:00:00Z
- sha: 00e98e1

<!--
The timestamp is the upper bound of the LAST run's window. The next run uses
it as the lower bound — so the window is `[timestamp, now]`.
-->

## Shadow review cadence

- last_shadow_review_date: null
- review_cadence_days: 90

<!--
last_shadow_review_date is null until /shadow-review runs the first time.
The digest workflow flags `⚠ /shadow-review due` in render output if
(today - last_shadow_review_date) > review_cadence_days, or if the field is
null AND the framework has been running > review_cadence_days.
-->

## Shadow generation stats

<!--
Rolling counts. Reset by /calibration-report at month boundary. Used by
prediction-architect's calibration aggregation + triage threshold review.
-->

- generated_today: 0
- rejected_specificity_today: 0
- expired_no_ground_truth_today: 0
- hard_fail_triggered_today: false
- last_generated: null
- lookback_resolved_today: null

## Brief generation stats

<!--
Counts how many briefs were generated / refreshed this cycle. Useful for
detecting brief-spam (cadence too loose) or brief-drought (eligibility
criteria too tight). Surfaced in monthly calibration report.
-->

- generated_today: 0
- refreshed_today: 0
- skipped_ineligible_today: 0

## Active acks

<!--
Format:
- [ack <YYYY-MM-DD> expires <YYYY-MM-DD>] <one-line description> | source: <chat <date> | digest <date> #N> | trigger: <why this ack was added>

Expiry rules:
- Default ack duration: 7 days. Override with explicit "ignore Nd" or "natrvalo".
- "Permanent" ack: set expires to 9999-12-31. Use sparingly — usually the
  underlying drift signals a documentation gap that should be patched, not
  permanently silenced.
- Expired acks auto-move to "## Expired acks" at next digest run.
- Re-evaluation: if drift still applies after expiry, re-flag (Step 10).
-->

- [ack 2026-06-20 expires 2026-06-27] SOC 2 mid-audit draft findings not yet reflected in pricing-v2 shard — known, awaiting compliance-vendor-x final report (~2026-06-13 slipped, now expected this week). | source: digest 2026-06-20 #3 | trigger: drift (a) — pricing-v2 shard assumes clean SOC 2 close; findings pending could shift seat-expansion timing.

## Expired acks (audit trail)

<!--
Append-only audit trail. Useful for:
- /calibration-report (which drifts kept resurfacing → documentation gap)
- Pattern analysis (drift category vs ack frequency)

Format same as active acks but marked expired.
-->

(none yet)
