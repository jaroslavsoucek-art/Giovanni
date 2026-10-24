#!/usr/bin/env bash
# Giovanni PreToolUse hook for `git commit` — validates that any staged
# decision record in memory/decisions/ has non-empty trigger_conditions
# (frontmatter field or `## Trigger conditions` section).
#
# This is the in-Claude-Code guard. The pre-commit lint
# (scripts/lint.sh → decision-trigger-conditions rule) is the
# command-line guard. Both exist because:
#   - Pre-commit catches commits from any CLI.
#   - This hook catches before Claude even calls `git commit`, surfacing
#     the failure inline.
#
# Returns:
#   exit 0  — no violations, commit proceeds
#   exit 2  — violation found, commit blocked (with explanation)
#
# Override:
#   GIOVANNI_SKIP_DECISION_CHECK=1 git commit <args>

set +e
if [ "${GIOVANNI_SKIP_DECISION_CHECK:-0}" = "1" ]; then
    exit 0
fi
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
# Self-filter: as a PreToolUse hook on Bash we see every command; gate only `git commit`.
if [ ! -t 0 ]; then
    VERDICT=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" commit-gate 2>/dev/null)
    if [ "${VERDICT}" = "skip" ]; then
        exit 0
    fi
fi
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"
STAGED=$(git -C "${REPO_ROOT}" diff --cached --name-only --diff-filter=ACM 2>/dev/null \
    | grep "^${MEMORY_DIR}/decisions/.*\.md$")
[ -z "${STAGED}" ] && exit 0
VIOLATIONS=()
while IFS= read -r FILE; do
    [ -f "${REPO_ROOT}/${FILE}" ] || continue
    STATUS=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" trigger-conditions "${REPO_ROOT}/${FILE}")
    if [ "${STATUS}" = "empty" ]; then
        VIOLATIONS+=("${FILE}")
    fi
done <<< "${STAGED}"
if [ "${#VIOLATIONS[@]}" -eq 0 ]; then
    exit 0
fi
{
    echo "Decision-record discipline check failed."
    echo ""
    echo "These decision records have empty trigger_conditions:"
    for f in "${VIOLATIONS[@]}"; do
        echo "  - ${f}"
    done
    echo ""
    echo "Fill the section '## Trigger conditions for re-evaluation' (or"
    echo "the frontmatter 'trigger_conditions:' field) with concrete signals"
    echo "that would cause revisiting this decision. Empty = no audit trail."
    echo ""
    echo "Override: GIOVANNI_SKIP_DECISION_CHECK=1 git commit <args>"
    echo "Or:       git commit --no-verify <args>"
} >&2
exit 2
