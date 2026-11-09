#!/usr/bin/env bash
# Giovanni PostToolUse hook (Edit|Write): constitution edit guardrails.
#
# Fires on Edit/Write touching knowledge/<constitution>.md. Emits a
# checklist reminder for the human (and the agent's next turn) covering:
#
#   1. Supersedes-pointer presence if a section header changed to SUPERSEDED
#   2. Commit-message prefix expectation (`docs(constitution):` or
#      `decision:`)
#   3. Domain-leak quick scan (if config provides a denylist)
#
# This hook does not block — it surfaces reminders. The pre-commit lint
# (scripts/lint.sh) is the enforcement layer.
#
# Honors GIOVANNI_KNOWLEDGE_DIR / GIOVANNI_CONSTITUTION_FILE.

set +e
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${CLAUDE_PLUGIN_ROOT}/hooks/lib/env.sh"
FILE=$("${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" file-path 2>/dev/null)
[ -z "${FILE}" ] && exit 0
KNOWLEDGE_DIR="${GIOVANNI_KNOWLEDGE_DIR:-knowledge}"
CONSTITUTION_FILE="${GIOVANNI_CONSTITUTION_FILE:-constitution.md}"
case "${FILE}" in
    */${KNOWLEDGE_DIR}/${CONSTITUTION_FILE}) ;;
    *) exit 0 ;;
esac
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
CONST_PATH="${REPO_ROOT}/${KNOWLEDGE_DIR}/${CONSTITUTION_FILE}"
MSG=$(cat <<EOF
⚠ ${KNOWLEDGE_DIR}/${CONSTITUTION_FILE} was just edited.
Per knowledge/README.md "How to amend safely" — pre-commit checklist:
  1. Commit prefix: docs(constitution): <slug>  (or decision: <slug>
     when this amendment is the artifact of a decision being recorded).
  2. Supersessions preserve the old section as a stub:
     with a one-paragraph stub. Do NOT delete prior content.
  3. Updated section has a last-touch date marker.
  4. Inbound pointers in other knowledge / memory docs still resolve
     (grep for the old anchor).
  5. Decision-record back-link present where applicable:
       Source: memory/decisions/<YYYY-MM-DD>-<slug>.md
Pre-commit lint will check:
  - constitution-anchors (every H2/H3 has {#anchor-id})
  - domain-leak (if denylist configured in governance.config.yaml)
Run the plugin lint (scripts/lint.sh) manually before committing.
EOF
)
if grep -qE '^##.*SUPERSEDED' "${CONST_PATH}" 2>/dev/null; then
    if grep -qE '^##.*SUPERSEDED[^→]*$' "${CONST_PATH}" 2>/dev/null; then
        MSG="${MSG}
⚠ Detected 'SUPERSEDED' header WITHOUT '→ §<anchor>' pointer.
   Expected format:  ## <name> (SUPERSEDED → §<new-anchor>)"
    fi
fi
"${GIOVANNI_PY}" "${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py" context PostToolUse "${MSG}"
exit 0
