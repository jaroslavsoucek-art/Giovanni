#!/usr/bin/env bash
# Giovanni Stop hook: automatic backup commit of working state.
#
# Commits changes under autonomy.auto_commit_paths (never under confirm_paths)
# at the end of every turn, through the normal git pre-commit gate, and pushes
# when autonomy.auto_push is set. Runs in the background so a turn never waits
# on the commit; a blocked commit or a failed push becomes an inbox item.
# Empty autonomy profile → no-op. See docs/autonomy.md § Autocommit.

set +e
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
nohup python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/autonomy.py" autocommit >/dev/null 2>&1 &
exit 0
