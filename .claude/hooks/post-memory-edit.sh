#!/usr/bin/env bash
# Giovanni PostToolUse hook (Edit|Write): rebuild memory/MAP.md whenever
# any file in memory/topics/, memory/decisions/, memory/briefs/,
# memory/stakeholders/, or memory/archive/ is touched. Skips MAP.md
# itself to avoid infinite loop.
#
# ‼ Resolves memory-architect open question #2: archive/ writes DO fire
# regen. Consistency over performance — regen is fast (<200ms on a
# typical fork), and the alternative (archive lands but MAP doesn't
# reflect it) is a known drift pattern.
#
# Trigger configuration (in .claude/settings.json — fork-defined):
#   PostToolUse → matcher "Edit|Write" → this script
#
# Honors GIOVANNI_MEMORY_DIR (default: memory). Always exits 0.

set +e

INPUT=$(cat)

FILE=$(printf '%s' "${INPUT}" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "${FILE}" ] && exit 0

MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"

case "${FILE}" in
    */${MEMORY_DIR}/MAP.md) exit 0 ;;
    */${MEMORY_DIR}/topics/*) ;;
    */${MEMORY_DIR}/decisions/*) ;;
    */${MEMORY_DIR}/briefs/*) ;;
    */${MEMORY_DIR}/stakeholders/*) ;;
    */${MEMORY_DIR}/archive/*) ;;
    *) exit 0 ;;
esac

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"

if [ -x "${REPO_ROOT}/scripts/build-memory-map.sh" ]; then
    "${REPO_ROOT}/scripts/build-memory-map.sh" 2>/dev/null
    echo "${MEMORY_DIR}/MAP.md auto-refreshed (${MEMORY_DIR}/ touched)"
fi

exit 0
