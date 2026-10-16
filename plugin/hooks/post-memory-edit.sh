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

# Project = $CLAUDE_PROJECT_DIR (exported to hook processes); plugin = where this
# script lives. Different directories once Giovanni is installed as a plugin, so the
# generator is told the project explicitly instead of guessing from its own path.
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"


# PostToolUse hooks reach the agent through hookSpecificOutput.additionalContext,
# not through stdout. A plain echo lands in the transcript and the agent may never
# see it — which for a regeneration notice means the agent does not learn that a
# generated file changed under it, and commits a stale one.
emit_context() {
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import json, sys
print(json.dumps({'hookSpecificOutput': {
    'hookEventName': 'PostToolUse',
    'additionalContext': sys.argv[1],
}}))
" "$1"
    else
        echo "$1"
    fi
}

if [ -x "${PLUGIN_ROOT}/scripts/build-memory-map.sh" ]; then
    if "${PLUGIN_ROOT}/scripts/build-memory-map.sh" >/dev/null 2>&1; then
        emit_context "${MEMORY_DIR}/MAP.md auto-refreshed (${MEMORY_DIR}/ touched) — include the regenerated MAP.md in the same commit as the memory change."
    else
        emit_context "⚠ build-memory-map.sh FAILED — ${MEMORY_DIR}/MAP.md may be stale. Run it manually and read the error before committing."
    fi
fi

exit 0
