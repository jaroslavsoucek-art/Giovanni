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

INPUT=$(cat)

# Extract file_path field via python (jq not assumed)
FILE=$(printf '%s' "${INPUT}" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "${FILE}" ] && exit 0

KNOWLEDGE_DIR="${GIOVANNI_KNOWLEDGE_DIR:-knowledge}"

case "${FILE}" in
    */${KNOWLEDGE_DIR}/INDEX.md) exit 0 ;;
    */${KNOWLEDGE_DIR}/*) ;;
    *) exit 0 ;;
esac

# Project = $CLAUDE_PROJECT_DIR (exported to hook processes); plugin = where this
# script lives. Different directories once Giovanni is installed as a plugin, so the
# generator is told the project explicitly instead of guessing from its own path.
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )}"
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

if [ -x "${PLUGIN_ROOT}/scripts/build-knowledge-index.sh" ]; then
    if "${PLUGIN_ROOT}/scripts/build-knowledge-index.sh" >/dev/null 2>&1; then
        emit_context "${KNOWLEDGE_DIR}/INDEX.md auto-refreshed (${KNOWLEDGE_DIR}/ touched) — include the regenerated INDEX.md in the same commit as the knowledge change."
    else
        emit_context "⚠ build-knowledge-index.sh FAILED — ${KNOWLEDGE_DIR}/INDEX.md may be stale. Run it manually and read the error before committing."
    fi
fi

exit 0
