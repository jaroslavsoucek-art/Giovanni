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
#   GIOVANNI_SKIP_DECISION_CHECK=1 git commit ...

set +e

if [ "${GIOVANNI_SKIP_DECISION_CHECK:-0}" = "1" ]; then
    exit 0
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"

MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"

# Read staged files
STAGED=$(git -C "${REPO_ROOT}" diff --cached --name-only --diff-filter=ACM 2>/dev/null \
    | grep "^${MEMORY_DIR}/decisions/.*\.md$")
[ -z "${STAGED}" ] && exit 0

VIOLATIONS=()

while IFS= read -r FILE; do
    [ -f "${REPO_ROOT}/${FILE}" ] || continue

    # Extract section content
    CONTENT=$(awk '
        /^## Trigger conditions/ { capturing=1; next }
        capturing && /^## / { exit }
        capturing { print }
    ' "${REPO_ROOT}/${FILE}")

    STRIPPED=$(printf '%s' "${CONTENT}" | sed 's/<!--[^>]*-->//g' | tr -d '[:space:]')

    if [ -z "${STRIPPED}" ] || printf '%s' "${CONTENT}" | grep -qiE '<EMPTY|<TBD|<TODO|^[[:space:]]*TBD[[:space:]]*$|^[[:space:]]*TODO[[:space:]]*$'; then
        # Check frontmatter field as fallback
        FM_TRIGGER=$(awk '
            BEGIN { in_fm = 0 }
            /^---$/ {
                if (in_fm) { exit }
                in_fm = 1
                next
            }
            in_fm && /^trigger_conditions:/ {
                sub("^trigger_conditions:[ \t]*", "")
                print
                exit
            }
        ' "${REPO_ROOT}/${FILE}")
        # FM_TRIGGER empty / [] / "" → violation
        FM_STRIPPED=$(printf '%s' "${FM_TRIGGER}" | tr -d '[:space:]')
        if [ -z "${FM_STRIPPED}" ] || [ "${FM_STRIPPED}" = "[]" ] || [ "${FM_STRIPPED}" = '""' ] || [ "${FM_STRIPPED}" = "''" ]; then
            VIOLATIONS+=("${FILE}")
        fi
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
    echo "Override: GIOVANNI_SKIP_DECISION_CHECK=1 git commit ..."
    echo "Or:       git commit --no-verify ..."
} >&2

exit 2
