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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"

MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"
L1_FILE="${GIOVANNI_L1_FILE:-CLAUDE_MEMORY.md}"

STATE_FILE="${REPO_ROOT}/${MEMORY_DIR}/audit_state.md"
L1_PATH="${REPO_ROOT}/${MEMORY_DIR}/${L1_FILE}"

AUDIT_FULL_CADENCE=${GIOVANNI_AUDIT_FULL_CADENCE_DAYS:-35}
AUDIT_LIGHT_CADENCE=${GIOVANNI_AUDIT_LIGHT_CADENCE_DAYS:-14}
L1_LIMIT=${GIOVANNI_L1_LIMIT:-300}
STRIKE_RATIO_MAX=${GIOVANNI_STRIKE_RATIO_MAX:-0.02}

WARNINGS=""

age_days() {
    local d=$1
    [ -z "$d" ] && return 1
    local epoch
    epoch=$(date -j -u -f "%Y-%m-%d" "$d" +%s 2>/dev/null) \
        || epoch=$(date -u -d "$d" +%s 2>/dev/null) \
        || return 1
    local now
    now=$(date -u +%s)
    echo $(( (now - epoch) / 86400 ))
}

# ----- 1 + 2: cadence (only if state file present) -----

if [ -f "${STATE_FILE}" ]; then
    LAST_AUDIT_FULL=$(grep -E '^- last_audit_full:' "${STATE_FILE}" | head -1 | awk '{print $3}')
    LAST_AUDIT_LIGHT=$(grep -E '^- last_audit_light:' "${STATE_FILE}" | head -1 | awk '{print $3}')

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

# ----- 3: L1 size -----

if [ -f "${L1_PATH}" ]; then
    LINES=$(wc -l < "${L1_PATH}" | tr -d ' ')
    if [ "${LINES}" -gt "${L1_LIMIT}" ]; then
        WARNINGS="${WARNINGS}⚠ ${MEMORY_DIR}/${L1_FILE} = ${LINES} lines (limit ${L1_LIMIT}). L1 is operational shortcut — classify before append (decision → ${MEMORY_DIR}/decisions/, artifact → ${MEMORY_DIR}/archive/, canonical → constitution patch). See memory/README.md.\n"
    fi

    # ----- 4: strikethrough ratio -----

    STRIKE_LINES=$(grep -c '~~' "${L1_PATH}" 2>/dev/null)
    [ -z "${STRIKE_LINES}" ] && STRIKE_LINES=0
    if [ "${LINES}" -gt 0 ] && [ "${STRIKE_LINES}" -gt 0 ]; then
        RATIO=$(awk "BEGIN { printf \"%.4f\", ${STRIKE_LINES} / ${LINES} }")
        EXCEEDS=$(awk "BEGIN { print (${RATIO} > ${STRIKE_RATIO_MAX}) ? 1 : 0 }")
        if [ "${EXCEEDS}" = "1" ]; then
            PCT=$(awk "BEGIN { printf \"%.1f\", ${RATIO} * 100 }")
            MAX_PCT=$(awk "BEGIN { printf \"%.0f\", ${STRIKE_RATIO_MAX} * 100 }")
            WARNINGS="${WARNINGS}⚠ Strikethrough creep in ${L1_FILE}: ${STRIKE_LINES}/${LINES} lines (${PCT}% > ${MAX_PCT}%). Persistent strikethrough = soft delete. Archive resolved items in same commit.\n"
        fi
    fi
fi

[ -n "${WARNINGS}" ] && printf '%b' "${WARNINGS}"

exit 0
