#!/usr/bin/env bash
# scripts/install-hooks.sh
#
# Bootstrap Giovanni governance hooks:
#
#   1. Make .claude/hooks/*.sh executable (Claude Code triggers them via
#      Edit/Write/SessionStart events — see .claude/settings.json for the
#      trigger mapping).
#   2. Install git pre-commit hook running `scripts/lint.sh`. Existing
#      pre-commit is backed up to .git/hooks/pre-commit.bak.
#
# The Claude Code hook trigger config (.claude/settings.json) is owned by
# the user / fork — this script does not modify it. It only ensures the
# scripts referenced by settings.json exist and are executable.
#
# Usage:
#   bash scripts/install-hooks.sh
#   bash scripts/install-hooks.sh --skip-precommit   # only chmod hooks
#
# Idempotent — safe to re-run.

set -euo pipefail

SKIP_PRECOMMIT=0
[ "${1:-}" = "--skip-precommit" ] && SKIP_PRECOMMIT=1

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "${REPO_ROOT}"

# ----- 1. chmod .claude/hooks/*.sh -----

if [ -d ".claude/hooks" ]; then
    hook_count=0
    for f in .claude/hooks/*.sh; do
        [ -f "$f" ] || continue
        chmod +x "$f"
        hook_count=$((hook_count + 1))
    done
    echo "  .claude/hooks/: ${hook_count} script(s) marked executable"
else
    echo "  .claude/hooks/: directory missing (skipped)"
fi

# ----- 2. chmod scripts/*.sh -----

for f in scripts/*.sh; do
    [ -f "$f" ] || continue
    chmod +x "$f"
done
echo "  scripts/: shell scripts marked executable"

# ----- 3. install git pre-commit running lint.sh -----

if [ "${SKIP_PRECOMMIT}" -eq 1 ]; then
    echo "  (skipping pre-commit install per --skip-precommit)"
    exit 0
fi

GIT_HOOKS_DIR=$(git rev-parse --git-path hooks 2>/dev/null || echo ".git/hooks")
[ -d "${GIT_HOOKS_DIR}" ] || mkdir -p "${GIT_HOOKS_DIR}"

PRECOMMIT="${GIT_HOOKS_DIR}/pre-commit"
NEW_CONTENT=$(cat <<'EOF'
#!/usr/bin/env bash
# Giovanni governance pre-commit: run scripts/lint.sh on staged tree.
# Override: GIOVANNI_SKIP_LINT=1 git commit ... (or --no-verify).
set -uo pipefail

if [ "${GIOVANNI_SKIP_LINT:-0}" = "1" ]; then
    exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
LINT="${REPO_ROOT}/scripts/lint.sh"

[ -x "${LINT}" ] || { echo "WARN: scripts/lint.sh not executable — skipping lint" >&2; exit 0; }

if ! "${LINT}"; then
    echo "" >&2
    echo "Pre-commit lint failed. Fix findings or:" >&2
    echo "  GIOVANNI_SKIP_LINT=1 git commit ..." >&2
    echo "  git commit --no-verify ..." >&2
    exit 1
fi
exit 0
EOF
)

# Back up existing pre-commit if it differs
if [ -f "${PRECOMMIT}" ]; then
    EXISTING=$(cat "${PRECOMMIT}")
    if [ "${EXISTING}" != "${NEW_CONTENT}" ]; then
        cp "${PRECOMMIT}" "${PRECOMMIT}.bak"
        echo "  pre-commit: existing hook backed up → ${PRECOMMIT}.bak"
    fi
fi

printf '%s\n' "${NEW_CONTENT}" > "${PRECOMMIT}"
chmod +x "${PRECOMMIT}"
echo "  pre-commit: installed (runs scripts/lint.sh; override via GIOVANNI_SKIP_LINT=1)"

echo ""
echo "Done. To verify:"
echo "  bash scripts/lint.sh --list"
echo "  bash scripts/lint.sh"
