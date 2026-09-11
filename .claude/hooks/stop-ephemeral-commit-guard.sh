#!/usr/bin/env bash
# Stop hook: ephemeral-session guard.
#
# In a throwaway environment — a cloud session, a container, a remote worktree —
# uncommitted or unpushed work is not "work in progress", it is work that is about
# to stop existing. The rule is usually written down ("commit before the session
# ends") and prose does not survive the end of a long session, which is exactly
# when it is needed and exactly when nobody is reading docs.
#
# Local, persistent machine: no-op. The disk is still there tomorrow.
# Ephemeral session: dirty tree or unpushed commits -> a message at Stop.
#
# Detection: $CLAUDE_CODE_REMOTE (set by remote/cloud Claude Code sessions), or
# GIOVANNI_EPHEMERAL=1 for any other throwaway environment you want guarded.

set +e

if [ -z "${CLAUDE_CODE_REMOTE:-}" ] && [ "${GIOVANNI_EPHEMERAL:-0}" != "1" ]; then
    exit 0
fi

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
cd "${REPO_ROOT}" || exit 0

DIRTY=$(git status --porcelain 2>/dev/null | head -5)
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null)
[ -z "${AHEAD}" ] && AHEAD=0

if [ -z "${DIRTY}" ] && [ "${AHEAD}" -eq 0 ]; then
    exit 0
fi

MSG="⚠ Ephemeral session with unsaved work: "
[ -n "${DIRTY}" ] && MSG="${MSG}dirty tree (git status). "
[ "${AHEAD}" -gt 0 ] && MSG="${MSG}${AHEAD} commit(s) unpushed. "
MSG="${MSG}This environment does not survive the session — commit and push before it ends."

if command -v python3 >/dev/null 2>&1; then
    python3 -c "
import json, sys
print(json.dumps({'systemMessage': sys.argv[1]}))
" "${MSG}"
else
    printf '%s\n' "${MSG}"
fi

exit 0
