#!/usr/bin/env bash
# scripts/run-lint-fixtures.sh — self-test for scripts/lint.sh + lint.py
#
# Iterates every scripts/lint-fixtures/<check-id>/{pass,fail}/ directory,
# runs lint with that fixture as LINT_REPO_ROOT scoped to the matching check,
# asserts: pass → exit 0, fail → exit 1.
#
# Per-check env overrides (GIOVANNI_*) keep fixtures compact — e.g. l1-size
# runs with a 7-line warn / 9-line critical limit so the fixture doesn't need
# 400 lines of filler.
#
# Returns 0 if all fixtures behave as expected, 1 otherwise.
#
# New rule ⇒ new fixture suite: see scripts/lint-fixtures/README.md.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." && pwd )"
FIXTURES="${SCRIPT_DIR}/lint-fixtures"

PASS_COUNT=0
FAIL_COUNT=0

run_one() {
    local check_id="$1"
    local variant="$2"   # pass | fail
    local target="${FIXTURES}/${check_id}/${variant}"
    [ -d "${target}" ] || return 0

    # Per-check env overrides so fixtures can stay compact.
    local -a env_overrides=()
    case "${check_id}" in
        l1-size)
            env_overrides=(GIOVANNI_L1_LIMIT=7 GIOVANNI_L1_LIMIT_CRITICAL=9)
            ;;
        l1-strikethrough-ratio)
            env_overrides=(GIOVANNI_STRIKE_RATIO_MAX=0.10)
            ;;
    esac

    local exit_code=0
    if [ "${#env_overrides[@]}" -gt 0 ]; then
        env "${env_overrides[@]}" LINT_REPO_ROOT="${target}" \
            bash "${REPO_ROOT}/scripts/lint.sh" --check "${check_id}" > /dev/null 2>&1 \
            || exit_code=$?
    else
        LINT_REPO_ROOT="${target}" \
            bash "${REPO_ROOT}/scripts/lint.sh" --check "${check_id}" > /dev/null 2>&1 \
            || exit_code=$?
    fi

    local expected
    if [ "${variant}" = "pass" ]; then
        expected=0
    else
        expected=1
    fi

    if [ "${exit_code}" -eq "${expected}" ]; then
        printf "  ok    %s/%s\n" "${check_id}" "${variant}"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        printf "  FAIL  %s/%s — expected exit %d, got %d\n" \
            "${check_id}" "${variant}" "${expected}" "${exit_code}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "Lint fixture self-test"
echo ""

for fixture_dir in "${FIXTURES}"/*/; do
    [ -d "${fixture_dir}" ] || continue
    check_id=$(basename "${fixture_dir}")
    run_one "${check_id}" pass
    run_one "${check_id}" fail
done

echo ""
echo "Passed: ${PASS_COUNT}  Failed: ${FAIL_COUNT}"
[ "${FAIL_COUNT}" -gt 0 ] && exit 1
exit 0
