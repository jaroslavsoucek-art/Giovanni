#!/usr/bin/env bash
# scripts/lint.sh — Giovanni governance lint orchestrator
#
# Thin wrapper around scripts/lint.py. Bash adds two things the Python
# layer can't easily do cleanly:
#   1. INDEX/MAP staleness — run the regen --dry and diff against committed
#      file. Cheap from bash, awkward from Python.
#   2. Hook syntax check — `bash -n` over .claude/hooks/*.sh.
#
# Everything else (frontmatter / YAML / structural rules) lives in
# scripts/lint.py + scripts/lint_rules/.
#
# Usage:
#   bash scripts/lint.sh                  # run all checks
#   bash scripts/lint.sh --check <id>     # one check by id
#   bash scripts/lint.sh --list           # list check ids and exit
#
# Exit codes:
#   0 — no findings
#   1 — one or more findings
#   2 — internal error
#
# Configuration loaded from docs/governance.config.yaml if present (see
# docs/governance.config.template.yaml for the schema). Env vars override
# config:
#   GIOVANNI_L1_LIMIT             default 300
#   GIOVANNI_L1_LIMIT_CRITICAL    default 400
#   GIOVANNI_STRIKE_RATIO_MAX     default 0.02
#   GIOVANNI_KNOWLEDGE_DIR        default knowledge
#   GIOVANNI_MEMORY_DIR           default memory
#   GIOVANNI_CONSTITUTION_FILE    default constitution.md
#   GIOVANNI_L1_FILE              default CLAUDE_MEMORY.md

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="${LINT_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

ONLY_CHECK=""
LIST_MODE=0
while [ $# -gt 0 ]; do
    case "$1" in
        --check) ONLY_CHECK="$2"; shift 2 ;;
        --list)  LIST_MODE=1; shift ;;
        --help|-h)
            sed -n '1,32p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

cd "${REPO_ROOT}"

TOTAL_FINDINGS=0

KNOWLEDGE_DIR="${GIOVANNI_KNOWLEDGE_DIR:-knowledge}"
MEMORY_DIR="${GIOVANNI_MEMORY_DIR:-memory}"

emit_finding() {
    local severity="$1"
    local check_id="$2"
    local message="$3"
    local sev
    case "${severity}" in
        critical) sev=CRITICAL ;;
        high)     sev=HIGH ;;
        medium)   sev=MEDIUM ;;
        low)      sev=LOW ;;
        *)        sev="${severity}" ;;
    esac
    printf '[%s] [%s] %s\n' "${sev}" "${check_id}" "${message}"
    TOTAL_FINDINGS=$((TOTAL_FINDINGS + 1))
}

run_check() {
    local id="$1"
    local fn="$2"
    if [ -z "${ONLY_CHECK}" ] || [ "${ONLY_CHECK}" = "${id}" ]; then
        "${fn}"
    fi
}

# Strip the "Generated:" timestamp + commit hash line so two regen runs at
# different moments compare equal in normalized form.
normalize_generated_doc() {
    sed -E \
        -e 's/^> Generated: .+$/> Generated: <NORM>/' \
        -e 's/[[:space:]]+$//'
}

# ---------- Bash checks ----------

# index-stale — knowledge/INDEX.md vs build-knowledge-index.sh --dry
check_index_stale() {
    local id="index-stale"
    [ -f "${KNOWLEDGE_DIR}/INDEX.md" ] || return 0
    [ -x "${SCRIPT_DIR}/build-knowledge-index.sh" ] || return 0
    local current generated diff_preview
    current=$(normalize_generated_doc < "${KNOWLEDGE_DIR}/INDEX.md")
    generated=$("${SCRIPT_DIR}/build-knowledge-index.sh" --dry 2>/dev/null | normalize_generated_doc)
    if [ "${current}" != "${generated}" ]; then
        diff_preview=$(diff <(echo "${current}") <(echo "${generated}") | head -8 | tr '\n' '|' | sed 's/|$//')
        emit_finding critical "${id}" \
            "${KNOWLEDGE_DIR}/INDEX.md differs from regen — first diff: ${diff_preview}"
    fi
}

# map-stale — memory/MAP.md vs build-memory-map.sh --dry
check_map_stale() {
    local id="map-stale"
    [ -f "${MEMORY_DIR}/MAP.md" ] || return 0
    [ -x "${SCRIPT_DIR}/build-memory-map.sh" ] || return 0
    local current generated diff_preview
    current=$(normalize_generated_doc < "${MEMORY_DIR}/MAP.md")
    generated=$("${SCRIPT_DIR}/build-memory-map.sh" --dry 2>/dev/null | normalize_generated_doc)
    if [ "${current}" != "${generated}" ]; then
        diff_preview=$(diff <(echo "${current}") <(echo "${generated}") | head -8 | tr '\n' '|' | sed 's/|$//')
        emit_finding critical "${id}" \
            "${MEMORY_DIR}/MAP.md differs from regen — first diff: ${diff_preview}"
    fi
}

# hook-syntax — every .claude/hooks/*.sh passes `bash -n`
check_hook_syntax() {
    local id="hook-syntax"
    [ -d .claude/hooks ] || return 0
    local file err
    for file in .claude/hooks/*.sh; do
        [ -f "$file" ] || continue
        if ! bash -n "$file" 2>/dev/null; then
            err=$(bash -n "$file" 2>&1 | head -1)
            emit_finding critical "${id}" "${file}: bash -n failed — ${err}"
        fi
    done
}

# script-syntax — every scripts/*.sh passes `bash -n`
check_script_syntax() {
    local id="script-syntax"
    local file err
    for file in scripts/*.sh; do
        [ -f "$file" ] || continue
        if ! bash -n "$file" 2>/dev/null; then
            err=$(bash -n "$file" 2>&1 | head -1)
            emit_finding critical "${id}" "${file}: bash -n failed — ${err}"
        fi
    done
}

# ---------- Bash check registry ----------

BASH_CHECKS=(
    "index-stale|check_index_stale"
    "map-stale|check_map_stale"
    "hook-syntax|check_hook_syntax"
    "script-syntax|check_script_syntax"
)

if [ "${LIST_MODE}" = 1 ]; then
    echo "Bash checks (scripts/lint.sh):"
    for entry in "${BASH_CHECKS[@]}"; do
        IFS='|' read -r id _fn <<< "${entry}"
        printf "  %-32s\n" "${id}"
    done
    echo ""
    echo "Python checks (scripts/lint.py + scripts/lint_rules/):"
    if command -v python3 >/dev/null 2>&1 && [ -f "${SCRIPT_DIR}/lint.py" ]; then
        python3 "${SCRIPT_DIR}/lint.py" --list
    else
        echo "  (lint.py not available)"
    fi
    exit 0
fi

for entry in "${BASH_CHECKS[@]}"; do
    IFS='|' read -r id fn <<< "${entry}"
    run_check "${id}" "${fn}"
done

# ---------- Python checks ----------

LINT_PY="${SCRIPT_DIR}/lint.py"
if [ -f "${LINT_PY}" ]; then
    if ! command -v python3 >/dev/null 2>&1; then
        emit_finding critical "lint-py-missing-runtime" "python3 not available — Python checks skipped"
    else
        py_args=("--repo-root" "${REPO_ROOT}")
        [ -n "${ONLY_CHECK}" ] && py_args+=("--check" "${ONLY_CHECK}")
        py_out=$(python3 "${LINT_PY}" "${py_args[@]}" 2>&1) || true
        if [ -n "${py_out}" ]; then
            echo "${py_out}"
            py_findings=$(echo "${py_out}" | grep -cE '^\[(CRITICAL|HIGH|MEDIUM|LOW)\]' 2>/dev/null || true)
            [ -z "${py_findings}" ] && py_findings=0
            TOTAL_FINDINGS=$((TOTAL_FINDINGS + py_findings))
        fi
    fi
fi

# ---------- Summary ----------

echo ""
if [ "${TOTAL_FINDINGS}" -gt 0 ]; then
    echo "Total findings: ${TOTAL_FINDINGS}"
    exit 1
fi
echo "Lint clean."
exit 0
