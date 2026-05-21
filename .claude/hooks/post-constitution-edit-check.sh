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

INPUT=$(cat)

FILE=$(printf '%s' "${INPUT}" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" 2>/dev/null)

[ -z "${FILE}" ] && exit 0

KNOWLEDGE_DIR="${GIOVANNI_KNOWLEDGE_DIR:-knowledge}"
CONSTITUTION_FILE="${GIOVANNI_CONSTITUTION_FILE:-constitution.md}"

case "${FILE}" in
    */${KNOWLEDGE_DIR}/${CONSTITUTION_FILE}) ;;
    *) exit 0 ;;
esac

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/../.." && pwd )"
CONST_PATH="${REPO_ROOT}/${KNOWLEDGE_DIR}/${CONSTITUTION_FILE}"

cat <<EOF
⚠ ${KNOWLEDGE_DIR}/${CONSTITUTION_FILE} was just edited.

Per knowledge/README.md "How to amend safely" — pre-commit checklist:

  1. Commit prefix: docs(constitution): <slug>  (or decision: <slug>
     when this amendment is the artifact of a decision being recorded).
  2. Supersessions preserve the old section as a stub:
       ## <old_name> (SUPERSEDED → §<new-anchor>)
     with a one-paragraph stub. Do NOT delete prior content.
  3. Updated section has a last-touch date marker.
  4. Inbound pointers in other knowledge / memory docs still resolve
     (grep for the old anchor).
  5. Decision-record back-link present where applicable:
       Source: memory/decisions/<YYYY-MM-DD>-<slug>.md

Pre-commit lint will check:
  - constitution-anchors (every H2/H3 has {#anchor-id})
  - domain-leak (if denylist configured in governance.config.yaml)

Run manually before commit: bash scripts/lint.sh
EOF

# Optional: light supersession-pointer heuristic — warn if "SUPERSEDED"
# header appears WITHOUT an arrow pointer.
if grep -qE '^##.*SUPERSEDED' "${CONST_PATH}" 2>/dev/null; then
    if grep -qE '^##.*SUPERSEDED[^→]*$' "${CONST_PATH}" 2>/dev/null; then
        echo ""
        echo "⚠ Detected 'SUPERSEDED' header WITHOUT '→ §<anchor>' pointer."
        echo "   Expected format:  ## <name> (SUPERSEDED → §<new-anchor>)"
    fi
fi

exit 0
