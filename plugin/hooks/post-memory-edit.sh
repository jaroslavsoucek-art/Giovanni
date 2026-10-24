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
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
FILE=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" file-path 2>/dev/null)
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
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
if [ -x "${CLAUDE_PLUGIN_ROOT}/scripts/build-memory-map.sh" ]; then
    if "${CLAUDE_PLUGIN_ROOT}/scripts/build-memory-map.sh" >/dev/null 2>&1; then
        "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context PostToolUse "${MEMORY_DIR}/MAP.md auto-refreshed (${MEMORY_DIR}/ touched) — include the regenerated MAP.md in the same commit as the memory change."
    else
        "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context PostToolUse "⚠ build-memory-map.sh FAILED — ${MEMORY_DIR}/MAP.md may be stale. Run it manually and read the error before committing."
    fi
fi
exit 0
