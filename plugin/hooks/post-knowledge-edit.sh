#!/usr/bin/env bash
# Giovanni PostToolUse hook (Edit|Write): rebuild knowledge/INDEX.md
# whenever any file in knowledge/ is touched. Skips INDEX.md itself to
# avoid infinite loop.
#
# Trigger configuration (in .claude/settings.json — fork-defined):
#   PostToolUse → matcher "Edit|Write" → this script
#
# Receives JSON via stdin (Claude Code hook protocol):
#   {"hook_event_name": "PostToolUse", "tool_name": "Edit|Write",
#    "tool_input": {"file_path": "...", ...}, ...}
#
# Honors GIOVANNI_KNOWLEDGE_DIR (default: knowledge). Always exits 0.

set +e
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
FILE=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" file-path 2>/dev/null)
[ -z "${FILE}" ] && exit 0
KNOWLEDGE_DIR="${GIOVANNI_KNOWLEDGE_DIR:-knowledge}"
case "${FILE}" in
    */${KNOWLEDGE_DIR}/INDEX.md) exit 0 ;;
    */${KNOWLEDGE_DIR}/*) ;;
    *) exit 0 ;;
esac
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
if [ -x "${CLAUDE_PLUGIN_ROOT}/scripts/build-knowledge-index.sh" ]; then
    if "${CLAUDE_PLUGIN_ROOT}/scripts/build-knowledge-index.sh" >/dev/null 2>&1; then
        "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context PostToolUse "${KNOWLEDGE_DIR}/INDEX.md auto-refreshed (${KNOWLEDGE_DIR}/ touched) — include the regenerated INDEX.md in the same commit as the knowledge change."
    else
        "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context PostToolUse "⚠ build-knowledge-index.sh FAILED — ${KNOWLEDGE_DIR}/INDEX.md may be stale. Run it manually and read the error before committing."
    fi
fi
exit 0
