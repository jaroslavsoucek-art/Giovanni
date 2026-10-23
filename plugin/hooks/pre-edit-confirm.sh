#!/usr/bin/env bash
# Giovanni PreToolUse hook (Edit|Write|MultiEdit|NotebookEdit): confirm paths.
#
# Paths listed under autonomy.confirm_paths in docs/governance.config.yaml are
# canon. An edit there asks the principal first; in a headless run
# (GIOVANNI_HEADLESS=1) it is denied, because nobody is there to answer. Edits
# made through the shell walk past this hook — the Stop-side autocommit never
# commits a confirm path either, it lists it in the inbox instead. Two layers.
#
# Empty profile → no output → the normal permission flow decides.

set +e
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
export GIOVANNI_REPO_ROOT="${REPO_ROOT}"
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/autonomy.py" confirm-gate
exit 0
