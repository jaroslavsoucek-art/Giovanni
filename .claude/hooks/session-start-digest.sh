#!/usr/bin/env bash
# Giovanni SessionStart hook: surface digest cadence + ack expiry reminders.
#
# Reads memory/digest_state.md and emits soft warnings (additionalContext)
# when:
#   1. last_run_timestamp is older than $GIOVANNI_DIGEST_THRESHOLD_HOURS
#      (default 12h) → digest reminder
#   2. one or more active acks are past expires_at → expired-drift flag
#   3. last_shadow_review_date is older than its review_cadence_days OR null
#      while the framework has been active > cadence days → shadow review
#      reminder
#
# All warnings are SOFT — the hook never blocks the session start. It exits 0
# in all paths.
#
# Silent when:
#   - State file missing (fresh fork, no signal to give yet)
#   - State file malformed (don't pretend; let lint catch the malformation)
#   - All checks pass (a clean state should produce no noise)
#
# Env overrides:
#   GIOVANNI_MEMORY_DIR                  default "memory"
#   GIOVANNI_DIGEST_STATE_FILE           default "digest_state.md"
#   GIOVANNI_DIGEST_THRESHOLD_HOURS      default 12
#   GIOVANNI_SHADOW_REVIEW_CADENCE_DAYS  default 90

set +e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"

MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"
STATE_FILENAME="${GIOVANNI_DIGEST_STATE_FILE:-digest_state.md}"
STATE_FILE="${REPO_ROOT}/${MEMORY_DIR}/${STATE_FILENAME}"

THRESHOLD_HOURS=${GIOVANNI_DIGEST_THRESHOLD_HOURS:-12}
THRESHOLD_SECONDS=$((THRESHOLD_HOURS * 3600))

SHADOW_CADENCE_DAYS=${GIOVANNI_SHADOW_REVIEW_CADENCE_DAYS:-90}

# Silent if state file missing — fresh fork has no signal.
[ -f "${STATE_FILE}" ] || exit 0

WARNINGS=""

# ----- Helper: parse ISO 8601 (UTC, with trailing Z) to epoch seconds -----
iso_to_epoch() {
    local ts="$1"
    [ -z "${ts}" ] && return 1
    # macOS first (Darwin), then GNU coreutils fallback.
    date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "${ts}" +%s 2>/dev/null \
        || date -u -d "${ts}" +%s 2>/dev/null \
        || return 1
}

# ----- Helper: parse YYYY-MM-DD to epoch seconds (UTC midnight) -----
date_to_epoch() {
    local d="$1"
    [ -z "${d}" ] && return 1
    date -j -u -f "%Y-%m-%d" "${d}" +%s 2>/dev/null \
        || date -u -d "${d}" +%s 2>/dev/null \
        || return 1
}

NOW_EPOCH=$(date -u +%s)

# ----- 1. Digest cadence -----

TS=$(grep -E '^- timestamp:' "${STATE_FILE}" | head -1 | awk '{print $3}')

if [ -n "${TS}" ]; then
    if TS_EPOCH=$(iso_to_epoch "${TS}"); then
        AGE=$((NOW_EPOCH - TS_EPOCH))
        if [ "${AGE}" -ge "${THRESHOLD_SECONDS}" ]; then
            AGE_HOURS=$((AGE / 3600))
            WARNINGS="${WARNINGS}🔄 Digest stale: last run ${AGE_HOURS}h ago (cutoff ${THRESHOLD_HOURS}h). Consider running \`/digest\` — pulls sources, drift detection, briefs for ≤48h events, predictive lookback. Workflow: \`.claude/workflows/daily-digest.md\`. Skip with one word if you're already mid-task.\n"
        fi
    fi
fi

# ----- 2. Expired active acks -----
#
# An active ack format:
#   - [ack YYYY-MM-DD expires YYYY-MM-DD] <desc> | source: <…> | trigger: <…>
#
# We extract the second date (expires) and count rows where it's < today.
# "Permanent" acks (9999-12-31) never trip this check.

EXPIRED_COUNT=0
if grep -qE '^- \[ack ' "${STATE_FILE}" 2>/dev/null; then
    TODAY_EPOCH=$(date_to_epoch "$(date -u +%Y-%m-%d)")
    while IFS= read -r line; do
        # Extract date inside `expires YYYY-MM-DD`
        EXP_DATE=$(echo "${line}" | sed -nE 's/.*expires ([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/p')
        [ -z "${EXP_DATE}" ] && continue
        [ "${EXP_DATE}" = "9999-12-31" ] && continue
        EXP_EPOCH=$(date_to_epoch "${EXP_DATE}") || continue
        if [ "${EXP_EPOCH}" -lt "${TODAY_EPOCH}" ]; then
            EXPIRED_COUNT=$((EXPIRED_COUNT + 1))
        fi
    done < <(grep -E '^- \[ack ' "${STATE_FILE}")
fi

if [ "${EXPIRED_COUNT}" -gt 0 ]; then
    WARNINGS="${WARNINGS}⚠ ${EXPIRED_COUNT} active ack(s) past expiry in ${MEMORY_DIR}/${STATE_FILENAME}. Next \`/digest\` will re-evaluate the underlying drift; either patch canonical state or extend the ack consciously.\n"
fi

# ----- 3. Shadow review cadence -----
#
# last_shadow_review_date is null until /shadow-review runs the first time.
# We only nag if either:
#   (a) date present AND > cadence days old, OR
#   (b) date null AND framework has been running > cadence days
#       (proxy: last_run_timestamp older than cadence days)

LAST_SR=$(grep -E '^- last_shadow_review_date:' "${STATE_FILE}" | head -1 | awk '{print $3}')

case "${LAST_SR}" in
    null|"")
        # Use last_run as proxy for "framework age"
        if [ -n "${TS}" ]; then
            if TS_EPOCH=$(iso_to_epoch "${TS}"); then
                AGE_DAYS=$(( (NOW_EPOCH - TS_EPOCH) / 86400 ))
                if [ "${AGE_DAYS}" -gt "${SHADOW_CADENCE_DAYS}" ]; then
                    WARNINGS="${WARNINGS}⚠ /shadow-review has never run; framework active >${SHADOW_CADENCE_DAYS}d. Pending shadow hypotheses are accumulating without verdict. Run \`/shadow-review\` at next convenience.\n"
                fi
            fi
        fi
        ;;
    *)
        if SR_EPOCH=$(date_to_epoch "${LAST_SR}"); then
            AGE_DAYS=$(( (NOW_EPOCH - SR_EPOCH) / 86400 ))
            if [ "${AGE_DAYS}" -gt "${SHADOW_CADENCE_DAYS}" ]; then
                WARNINGS="${WARNINGS}⚠ /shadow-review overdue: ${AGE_DAYS}d since ${LAST_SR} (cadence ${SHADOW_CADENCE_DAYS}d). Resolved-but-unverified shadow hypotheses are skewing calibration.\n"
            fi
        fi
        ;;
esac

# ----- Emit -----

[ -z "${WARNINGS}" ] && exit 0

if command -v jq >/dev/null 2>&1; then
    jq -nc --arg msg "${WARNINGS}" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $msg}}'
else
    # Manual JSON escape — newlines + quotes + backslashes.
    escaped=$(printf '%s' "${WARNINGS}" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')
    printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "${escaped}"
fi

exit 0
