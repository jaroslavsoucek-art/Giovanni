#!/usr/bin/env bash
# scripts/install-hooks.sh — install Giovanni's git gates into a project.
#
#   1. Mark the plugin's hooks/*.sh and scripts/*.sh executable (Claude Code
#      runs the hooks via hooks/hooks.json; a plugin cache copy may have lost
#      the bits).
#   2. Record the plugin root in the project's .git/giovanni-plugin-root, so
#      the git hooks can find the generators and the lint outside any session.
#   3. Install the git pre-commit hook from scripts/git-hooks/pre-commit
#      (regenerate INDEX / MAP / REGISTRY from HEAD + staged, then run the
#      lint), and a pre-push hook running lint + the fixture self-test.
#      Existing hooks are backed up to .git/hooks/<name>.bak.
#
# The Claude Code hook trigger map ships with the plugin (hooks/hooks.json);
# the project's .claude/settings.json carries only permissions. This script
# touches neither.
#
# Usage:
#   bash <plugin>/scripts/install-hooks.sh                        # project = git repo of the cwd
#   bash <plugin>/scripts/install-hooks.sh --project-root <dir>
#   bash <plugin>/scripts/install-hooks.sh --skip-precommit       # steps 1–2 only
#
# Idempotent — safe to re-run.

set -euo pipefail

SKIP_PRECOMMIT=0
PROJECT_ARG=""
while [ $# -gt 0 ]; do
    case "$1" in
        --skip-precommit) SKIP_PRECOMMIT=1; shift ;;
        --project-root)   [ $# -ge 2 ] || { echo "--project-root needs a path" >&2; exit 2; }; PROJECT_ARG="$2"; shift 2 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
PROJECT="${PROJECT_ARG:-${GIOVANNI_REPO_ROOT:-${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}}}"
PROJECT="$( cd "${PROJECT}" && pwd )"
cd "${PROJECT}"

# ----- 1. executable bits -----
chmod +x "${PLUGIN_ROOT}"/hooks/*.sh "${PLUGIN_ROOT}"/scripts/*.sh "${PLUGIN_ROOT}"/scripts/git-hooks/* 2>/dev/null || true
echo "  plugin hooks + scripts marked executable (${PLUGIN_ROOT})"

# ----- 2. plugin root marker -----
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null) || { echo "ERROR: ${PROJECT} is not a git repo" >&2; exit 2; }
case "${GIT_COMMON}" in /*) ;; *) GIT_COMMON="${PROJECT}/${GIT_COMMON}" ;; esac
printf '%s\n' "${PLUGIN_ROOT}" > "${GIT_COMMON}/giovanni-plugin-root"
echo "  plugin root recorded in ${GIT_COMMON#"${PROJECT}"/}/giovanni-plugin-root (refreshed at every session start)"

if [ "${SKIP_PRECOMMIT}" -eq 1 ]; then
    echo "  (skipping git hook install per --skip-precommit)"
    exit 0
fi

# ----- 3. git pre-commit -----
#
# The hook body lives in a tracked file, not in a heredoc here: it is long enough to
# need its reasons next to it, and a tracked file gets `bash -n` from the lint.

GIT_HOOKS_DIR=$(git rev-parse --git-path hooks 2>/dev/null || echo ".git/hooks")
case "${GIT_HOOKS_DIR}" in /*) ;; *) GIT_HOOKS_DIR="${PROJECT}/${GIT_HOOKS_DIR}" ;; esac
[ -d "${GIT_HOOKS_DIR}" ] || mkdir -p "${GIT_HOOKS_DIR}"

PRECOMMIT="${GIT_HOOKS_DIR}/pre-commit"
PRECOMMIT_SRC="${PLUGIN_ROOT}/scripts/git-hooks/pre-commit"
[ -f "${PRECOMMIT_SRC}" ] || { echo "ERROR: ${PRECOMMIT_SRC} missing" >&2; exit 2; }

if [ -f "${PRECOMMIT}" ] && ! cmp -s "${PRECOMMIT}" "${PRECOMMIT_SRC}"; then
    cp "${PRECOMMIT}" "${PRECOMMIT}.bak"
    echo "  pre-commit: existing hook backed up → ${PRECOMMIT}.bak"
fi

cp "${PRECOMMIT_SRC}" "${PRECOMMIT}"
chmod +x "${PRECOMMIT}"
echo "  pre-commit: installed (regen INDEX/MAP/REGISTRY from HEAD+staged, then lint; override via GIOVANNI_SKIP_LINT=1)"

# ----- 4. git pre-push: last gate before the work leaves the machine -----
#
# The pre-commit hook is the one people skip. `--no-verify` on a hurried commit is
# normal and usually harmless — until it is the commit that lands. Pre-push is the
# gate that runs once per push instead of once per commit, which makes it cheap
# enough to also run the fixture self-test. Where a fork works directly on main with
# no pull-request check, this is the only gate left between a broken invariant and
# the shared branch.
#
# Plugin resolution mirrors the pre-commit hook: the marker written at session
# start, then the env, then ./plugin in a fork clone.

PREPUSH="${GIT_HOOKS_DIR}/pre-push"
PREPUSH_CONTENT=$(cat <<'EOF'
#!/usr/bin/env bash
# Giovanni governance pre-push: lint + fixture self-test before anything leaves.
# Override: GIOVANNI_SKIP_LINT=1 git push ... (or --no-verify).
set -uo pipefail

if [ "${GIOVANNI_SKIP_LINT:-0}" = "1" ]; then
    exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
MARKER="$(git rev-parse --git-common-dir)/giovanni-plugin-root"
PLUGIN=""
if [ -n "${GIOVANNI_PLUGIN_ROOT:-}" ] && [ -f "${GIOVANNI_PLUGIN_ROOT}/scripts/lint.sh" ]; then
    PLUGIN="${GIOVANNI_PLUGIN_ROOT}"
elif [ -f "${MARKER}" ] && [ -f "$(cat "${MARKER}")/scripts/lint.sh" ]; then
    PLUGIN="$(cat "${MARKER}")"
elif [ -f "${REPO_ROOT}/plugin/scripts/lint.sh" ]; then
    PLUGIN="${REPO_ROOT}/plugin"
fi
if [ -z "${PLUGIN}" ]; then
    echo "WARN: Giovanni plugin not found (no .git/giovanni-plugin-root, no ./plugin) — pre-push lint skipped. Start a Claude session once, or run install-hooks.sh again." >&2
    exit 0
fi

FAILED=0
LINT_REPO_ROOT="${REPO_ROOT}" bash "${PLUGIN}/scripts/lint.sh" || FAILED=1

if [ -f "${PLUGIN}/scripts/run-lint-fixtures.sh" ]; then
    bash "${PLUGIN}/scripts/run-lint-fixtures.sh" >/dev/null || {
        echo "Lint fixtures failed — a rule changed behaviour. Run: bash ${PLUGIN}/scripts/run-lint-fixtures.sh" >&2
        FAILED=1
    }
fi

if [ "${FAILED}" -ne 0 ]; then
    echo "" >&2
    echo "Pre-push gate failed. Fix findings or:" >&2
    echo "  GIOVANNI_SKIP_LINT=1 git push ..." >&2
    echo "  git push --no-verify ..." >&2
    exit 1
fi
exit 0
EOF
)

if [ -f "${PREPUSH}" ]; then
    EXISTING_PP=$(cat "${PREPUSH}")
    if [ "${EXISTING_PP}" != "${PREPUSH_CONTENT}" ]; then
        cp "${PREPUSH}" "${PREPUSH}.bak"
        echo "  pre-push: existing hook backed up → ${PREPUSH}.bak"
    fi
fi

printf '%s\n' "${PREPUSH_CONTENT}" > "${PREPUSH}"
chmod +x "${PREPUSH}"
echo "  pre-push: installed (lint + fixture self-test; override via GIOVANNI_SKIP_LINT=1)"

echo ""
echo "Done. To verify:"
echo "  bash \"${PLUGIN_ROOT}/scripts/lint.sh\" --list"
echo "  bash \"${PLUGIN_ROOT}/scripts/lint.sh\""
