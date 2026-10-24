#!/usr/bin/env bash
# Giovanni Stop hook: record the session's shape for the learning loop.
#
# Writes the generalised tool-step sequence of this session (no prompt text,
# no file contents, unit-dir paths masked) to memory/.telemetry/sessions.jsonl,
# which is gitignored and machine-local. scripts/mine-workflows.py reads it to
# propose skills. learning.enabled off → no-op. See docs/autonomy.md § Learning.

set +e
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
INPUT=$(cat)
if command -v nohup >/dev/null 2>&1; then
    printf '%s' "${INPUT}" | nohup "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/learning.py" record >/dev/null 2>&1 &
else
    printf '%s' "${INPUT}" | "${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/learning.py" record >/dev/null 2>&1 &
fi
exit 0
