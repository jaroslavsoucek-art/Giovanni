#!/usr/bin/env bash
# Giovanni SessionStart hook: surface memory hygiene + cadence warnings.
#
# Single state file: memory/audit_state.md (flat, per memory-architect open
# question #1 resolution — flat at memory/<name>_state.md, NOT nested at
# memory/state/audit.md).
#
# Expected state file format (parsed line-prefixed YAML-ish for simplicity):
#
#   # Audit state
#   - last_audit_full: YYYY-MM-DD
#   - last_audit_light: YYYY-MM-DD
#
# Optional additional lines (silently ignored if absent):
#   - last_watch_scan: YYYY-MM-DD
#
# Checks (all soft warnings — never blocks):
#   1. Full memory-audit overdue (default 35d, env: GIOVANNI_AUDIT_FULL_CADENCE_DAYS)
#   2. Light pruning pass overdue (default 14d, env: GIOVANNI_AUDIT_LIGHT_CADENCE_DAYS)
#   3. L1 size > config.l1_limit (default 300)
#   4. Strikethrough ratio > config.strike_ratio_max (default 2 %)
#
# Silent if state file missing (fresh fork — no signal). Emits warnings
# via Claude Code's stdout-as-additional-context channel. Always exits 0.

set +e
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"
L1_FILE="${GIOVANNI_L1_FILE:-CLAUDE_MEMORY.md}"
STATE_FILE="${REPO_ROOT}/${MEMORY_DIR}/audit_state.md"
L1_PATH="${REPO_ROOT}/${MEMORY_DIR}/${L1_FILE}"
AUDIT_FULL_CADENCE=${GIOVANNI_AUDIT_FULL_CADENCE_DAYS:-35}
AUDIT_LIGHT_CADENCE=${GIOVANNI_AUDIT_LIGHT_CADENCE_DAYS:-14}
L1_LIMIT=${GIOVANNI_L1_LIMIT:-300}
STRIKE_RATIO_MAX=${GIOVANNI_STRIKE_RATIO_MAX:-0.02}
WARNINGS=""

# Days since YYYY-MM-DD, UTC. Returns 1 when the date is empty or unparsable.
age_days() {
    local d=$1
    [ -z "$d" ] && return 1
    local epoch
    epoch=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" epoch date "$d" 2>/dev/null)
    [ -z "$epoch" ] && return 1
    local now
    now=$(date -u +%s)
    echo $(( (now - epoch) / 86400 ))
}

if [ -f "${STATE_FILE}" ]; then
    LAST_AUDIT_FULL=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${STATE_FILE}" '^- last_audit_full:' first)
    LAST_AUDIT_LIGHT=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${STATE_FILE}" '^- last_audit_light:' first)
    if AGE=$(age_days "${LAST_AUDIT_FULL}"); then
        if [ "${AGE}" -gt "${AUDIT_FULL_CADENCE}" ]; then
            WARNINGS="${WARNINGS}⚠ Full memory-audit overdue: ${AGE}d since ${LAST_AUDIT_FULL} (cadence ${AUDIT_FULL_CADENCE}d). Run the memory-audit workflow.\n"
        fi
    fi
    if AGE=$(age_days "${LAST_AUDIT_LIGHT}"); then
        if [ "${AGE}" -gt "${AUDIT_LIGHT_CADENCE}" ]; then
            WARNINGS="${WARNINGS}⚠ Light memory pruning overdue: ${AGE}d since ${LAST_AUDIT_LIGHT} (cadence ${AUDIT_LIGHT_CADENCE}d). Quick pass — grep '~~' in ${L1_FILE} and archive resolved items.\n"
        fi
    fi
fi

if [ -f "${L1_PATH}" ]; then
    LINES=$(wc -l < "${L1_PATH}" | tr -d ' ')
    if [ "${LINES}" -gt "${L1_LIMIT}" ]; then
        WARNINGS="${WARNINGS}⚠ ${MEMORY_DIR}/${L1_FILE} = ${LINES} lines (limit ${L1_LIMIT}). L1 is operational shortcut — classify before append (decision → ${MEMORY_DIR}/decisions/, artifact → ${MEMORY_DIR}/archive/, canonical → constitution patch). See memory/README.md.\n"
    fi
    STRIKE_LINES=$(grep -c '~~' "${L1_PATH}" 2>/dev/null)
    [ -z "${STRIKE_LINES}" ] && STRIKE_LINES=0
    if [ "${LINES}" -gt 0 ] && [ "${STRIKE_LINES}" -gt 0 ]; then
        # "<exceeds 0|1> <pct> <max pct>"
        RATIO_OUT=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" strike-ratio "${STRIKE_LINES}" "${LINES}" "${STRIKE_RATIO_MAX}")
        set -- ${RATIO_OUT}
        if [ "${1:-0}" = "1" ]; then
            WARNINGS="${WARNINGS}⚠ Strikethrough creep in ${L1_FILE}: ${STRIKE_LINES}/${LINES} lines (${2}% > ${3}%). Persistent strikethrough = soft delete. Archive resolved items in same commit.\n"
        fi
    fi
fi

CONSISTENCY_STATE="${REPO_ROOT}/${MEMORY_DIR}/audits/consistency/_state.md"
CONSISTENCY_CADENCE=${GIOVANNI_CONSISTENCY_CADENCE_DAYS:-7}
if [ -f "${CONSISTENCY_STATE}" ]; then
    LAST_RUN_DATE=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${CONSISTENCY_STATE}" '^## Run ' last)
    LAST_REVIEW_STATUS=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${CONSISTENCY_STATE}" '^- review_status:' last)
    LAST_FINDINGS=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" field "${CONSISTENCY_STATE}" '^- findings_total:' last)
    if AGE=$(age_days "${LAST_RUN_DATE}"); then
        if [ "${AGE}" -gt "${CONSISTENCY_CADENCE}" ]; then
            WARNINGS="${WARNINGS}⚠ Consistency-check overdue: ${AGE}d since ${LAST_RUN_DATE} (cadence ${CONSISTENCY_CADENCE}d). Run /giovanni:consistency-check.\n"
        fi
    fi
    if [ "${LAST_REVIEW_STATUS}" = "pending" ]; then
        WARNINGS="${WARNINGS}ℹ Consistency run ${LAST_RUN_DATE}: ${LAST_FINDINGS:-?} findings pending triage — /giovanni:consistency-review ${LAST_RUN_DATE}.\n"
    fi
fi

[ -n "${WARNINGS}" ] && printf '%b' "${WARNINGS}"
exit 0
