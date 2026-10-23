#!/usr/bin/env bash
# Giovanni UserPromptSubmit hook: notice corrections.
#
# When the principal's prompt matches one of learning.correction_markers, the
# agent is told to classify the correction (skill fix / standing rule / one-off),
# act on it, and log it to memory/learning/corrections.md — so nobody has to say
# "remember this". learning.enabled off → no-op. See docs/autonomy.md § Learning.

set +e
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/learning.py" correction-check
exit 0
