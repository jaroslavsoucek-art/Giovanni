#!/usr/bin/env bash
# Giovanni SessionStart hook: refresh the inbox and show it.
#
# The inbox (scripts/inbox.py, docs/autonomy.md) is the one list every loop
# writes to: deadlines from project refreshers, lint findings, scheduler health,
# skill proposals. This hook runs the cheap producers, expires stale items and
# hands the ranked list to the session as additionalContext, with the
# instruction to show it first. No inbox configured and no inbox file → no-op.
#
# Never blocks the session: every failure path exits 0.

set +e
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
"${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/scripts/inbox.py" --repo "${REPO_ROOT}" session-start 2>/dev/null
exit 0
