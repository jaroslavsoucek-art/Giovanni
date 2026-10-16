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
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
# Record where the plugin lives so the git gates (which run outside any Claude
# session) can find lint.sh and the generators again.
GIT_DIR_PATH=$(git -C "${REPO_ROOT}" rev-parse --git-common-dir 2>/dev/null)
if [ -n "${GIT_DIR_PATH}" ]; then
    case "${GIT_DIR_PATH}" in /*) ;; *) GIT_DIR_PATH="${REPO_ROOT}/${GIT_DIR_PATH}" ;; esac
    printf '%s\n' "${CLAUDE_PLUGIN_ROOT}" > "${GIT_DIR_PATH}/giovanni-plugin-root" 2>/dev/null || true
fi

MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"
STATE_FILENAME="${GIOVANNI_DIGEST_STATE_FILE:-digest_state.md}"
STATE_FILE="${REPO_ROOT}/${MEMORY_DIR}/${STATE_FILENAME}"
THRESHOLD_HOURS=${GIOVANNI_DIGEST_THRESHOLD_HOURS:-12}
THRESHOLD_SECONDS=$((THRESHOLD_HOURS * 3600))
SHADOW_CADENCE_DAYS=${GIOVANNI_SHADOW_REVIEW_CADENCE_DAYS:-90}
[ -f "${STATE_FILE}" ] || exit 0
WARNINGS=""

iso_to_epoch() {
    [ -z "$1" ] && return 1
    python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" epoch iso "$1" 2>/dev/null || return 1
}
date_to_epoch() {
    [ -z "$1" ] && return 1
    python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" epoch date "$1" 2>/dev/null || return 1
}

NOW_EPOCH=$(date -u +%s)
TS=$(python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${STATE_FILE}" '^- timestamp:' first)
if [ -n "${TS}" ]; then
    if TS_EPOCH=$(iso_to_epoch "${TS}"); then
        AGE=$((NOW_EPOCH - TS_EPOCH))
        if [ "${AGE}" -ge "${THRESHOLD_SECONDS}" ]; then
            AGE_HOURS=$((AGE / 3600))
            WARNINGS="${WARNINGS}🔄 Digest stale: last run ${AGE_HOURS}h ago (cutoff ${THRESHOLD_HOURS}h). Consider running \`/giovanni:digest\` — pulls sources, drift detection, briefs for ≤48h events, predictive lookback. Skip with one word if you're already mid-task.\n"
        fi
    fi
fi

EXPIRED_COUNT=$(python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" ack-expired "${STATE_FILE}")
if [ "${EXPIRED_COUNT:-0}" -gt 0 ]; then
    WARNINGS="${WARNINGS}⚠ ${EXPIRED_COUNT} active ack(s) past expiry in ${MEMORY_DIR}/${STATE_FILENAME}. Next \`/giovanni:digest\` will re-evaluate the underlying drift; either patch canonical state or extend the ack consciously.\n"
fi

LAST_SR=$(python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${STATE_FILE}" '^- last_shadow_review_date:' first)
case "${LAST_SR}" in
    null|"")
        if [ -n "${TS}" ]; then
            if TS_EPOCH=$(iso_to_epoch "${TS}"); then
                AGE_DAYS=$(( (NOW_EPOCH - TS_EPOCH) / 86400 ))
                if [ "${AGE_DAYS}" -gt "${SHADOW_CADENCE_DAYS}" ]; then
                    WARNINGS="${WARNINGS}⚠ /giovanni:shadow-review has never run; framework active >${SHADOW_CADENCE_DAYS}d. Pending shadow hypotheses are accumulating without verdict. Run \`/giovanni:shadow-review\` at next convenience.\n"
                fi
            fi
        fi
        ;;
    *)
        if SR_EPOCH=$(date_to_epoch "${LAST_SR}"); then
            AGE_DAYS=$(( (NOW_EPOCH - SR_EPOCH) / 86400 ))
            if [ "${AGE_DAYS}" -gt "${SHADOW_CADENCE_DAYS}" ]; then
                WARNINGS="${WARNINGS}⚠ /giovanni:shadow-review overdue: ${AGE_DAYS}d since ${LAST_SR} (cadence ${SHADOW_CADENCE_DAYS}d). Resolved-but-unverified shadow hypotheses are skewing calibration.\n"
            fi
        fi
        ;;
esac

[ -z "${WARNINGS}" ] && exit 0
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context SessionStart "$(printf '%b' "${WARNINGS}")"
exit 0
