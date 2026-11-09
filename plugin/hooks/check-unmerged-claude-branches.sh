#!/usr/bin/env bash
# Giovanni SessionStart / Stop hook: warn about unmerged claude/* branches.
#
# When Claude Code commits to a feature branch but never merges back,
# subsequent sessions can work off stale main while the work sits
# orphaned. This hook surfaces such branches at session boundaries.
#
# Warns when:
#   - Any local refs/heads/claude/* not merged to main
#   - Any refs/remotes/origin/claude/* not merged to main
#
# If GIOVANNI_BRANCH_WARN_THRESHOLD is set (default 1), only warns when
# the count exceeds that threshold. Set to 3 if you tolerate a small
# branch backlog.
#
# Always exits 0. Output goes to stdout (consumed as additionalContext)

set +e
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
THRESHOLD="${GIOVANNI_BRANCH_WARN_THRESHOLD:-1}"
MAIN_BRANCH="${GIOVANNI_MAIN_BRANCH:-main}"
cd "${REPO_ROOT}" || exit 0
git rev-parse --git-dir > /dev/null 2>&1 || exit 0
branches=$(git for-each-ref --format='%(refname:short)' \
    'refs/heads/claude/*' \
    "refs/remotes/origin/claude/*" 2>/dev/null | sort -u)
[ -z "${branches}" ] && exit 0
unmerged_lines=""
unmerged_count=0
while IFS= read -r ref; do
    [ -z "${ref}" ] && continue
    display="${ref#origin/}"
    if ! git merge-base --is-ancestor "${ref}" "${MAIN_BRANCH}" 2>/dev/null; then
        ahead=$(git rev-list --count "${MAIN_BRANCH}..${ref}" 2>/dev/null || echo "?")
        unmerged_lines="${unmerged_lines}   - ${display} (${ahead} commits ahead of ${MAIN_BRANCH})\n"
        unmerged_count=$((unmerged_count + 1))
    fi
done <<< "${branches}"
[ "${unmerged_count}" -lt "${THRESHOLD}" ] && exit 0
msg="⚠ UNMERGED CLAUDE SESSION BRANCHES (${unmerged_count}):\n${unmerged_lines}\nMerge: git merge origin/claude/<name>  |  Delete: git push origin --delete claude/<name>"
"${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" system "$(printf '%b' "${msg}")"
exit 0
