#!/usr/bin/env bash
# scripts/init-fork.sh — scaffold the Giovanni layers into a project.
#
# Giovanni is a plugin (mechanism) that operates on files in your repo (state).
# This script creates the state half, from the plugin's skeleton:
#
#   1. Copy each template to its runtime filename (constitution, L1 memory,
#      digest sources/state, triage heuristic, governance config, the
#      permission layer of .claude/settings.json, the CLAUDE.md operating
#      contract) plus the READMEs and per-artifact templates the agents read
#      at run time (memory/templates/, memory/examples/, …). Existing files
#      are NEVER overwritten (idempotent; --force to re-copy).
#   2. Create the runtime memory subdirectories (stakeholders, topics,
#      decisions, briefs, archive, shadow/*, …) with .gitkeep.
#   3. Seed audit_state.md + the stakeholder roster README.
#   4. Record the plugin root in .git/ for the git hooks, and mark the
#      plugin's scripts executable.
#   5. Regenerate MAP.md / INDEX.md (skipped on shallow clones).
#   6. Run lint — INFORMATIONALLY. A freshly-scaffolded project still has
#      template placeholders to fill, so lint findings here are your
#      to-do list, not an error. init succeeds as long as scaffolding does.
#
# Two ways to get here, same result:
#   * plugin install:  /giovanni:init in a Claude Code session (the skill runs
#                      this script from the plugin root), or by hand:
#                      bash "$(claude plugin list --json | …)/scripts/init-fork.sh"
#   * fork clone:      git clone Giovanni, then  bash plugin/scripts/init-fork.sh
#                      — the clone carries the plugin at ./plugin; register it as a
#                      local marketplace afterwards (printed at the end).
#
# This is the mechanical half of "set up in <30 min" (definition-of-done #1).
# The other half — filling the constitution, bootstrapping stakeholders, wiring
# sources — is the multi-hour work walked through in docs/setup-guide.md.
#
# Usage:
#   bash <plugin>/scripts/init-fork.sh                       # scaffold the git repo of the cwd (interactive confirm)
#   bash <plugin>/scripts/init-fork.sh --yes                 # non-interactive
#   bash <plugin>/scripts/init-fork.sh --force               # re-copy templates over existing runtime files
#   bash <plugin>/scripts/init-fork.sh --skip-regen          # don't run MAP/INDEX regen
#   bash <plugin>/scripts/init-fork.sh --project-root <dir>  # scaffold a different directory
#   bash <plugin>/scripts/init-fork.sh --without predictive,stakeholders,digest
#                                                            # switch layers off (docs/autonomy.md § Layers)
#
# Idempotent — safe to re-run.

set -euo pipefail

ASSUME_YES=0
FORCE=0
SKIP_REGEN=0
PROJECT_ARG=""
WITHOUT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --yes|-y)        ASSUME_YES=1; shift ;;
        --force)         FORCE=1; shift ;;
        --skip-regen)    SKIP_REGEN=1; shift ;;
        --project-root)  [ $# -ge 2 ] || { echo "--project-root needs a path" >&2; exit 2; }; PROJECT_ARG="$2"; shift 2 ;;
        --without)       [ $# -ge 2 ] || { echo "--without needs a comma-separated layer list" >&2; exit 2; }; WITHOUT="$2"; shift 2 ;;
        --help|-h)       sed -n '2,46p' "$0" | sed -E 's/^# ?//'; exit 0 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$(dirname "${SCRIPT_DIR}")"
SKELETON="${PLUGIN_ROOT}/skeleton"
TEMPLATES="${PLUGIN_ROOT}/templates"

# The project is never where this script lives — installed as a plugin, the script
# sits in the plugin cache. Explicit flag, then the env the hooks export, then the
# git repo of the cwd.
PROJECT="${PROJECT_ARG:-${GIOVANNI_REPO_ROOT:-${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}}}"
PROJECT="$( cd "${PROJECT}" && pwd )"
cd "${PROJECT}"

# ----- Guard: refuse to scaffold inside the Giovanni framework repo itself -----
# A real fork's origin points at YOUR repo, not the upstream. This stops init from
# creating runtime files inside the framework.
ORIGIN_URL=$(git remote get-url origin 2>/dev/null || echo "")
if printf '%s' "${ORIGIN_URL}" | grep -qiE 'jaroslavsoucek-art/Giovanni(\.git)?$'; then
    if [ "${FORCE}" -ne 1 ]; then
        cat >&2 <<EOF
ERROR: origin looks like the Giovanni framework repo itself:
  ${ORIGIN_URL}

init-fork.sh creates runtime files (constitution.md, CLAUDE_MEMORY.md, …) that
do not belong in the framework. Fork/clone to your own repo first:

  git clone <this-repo> my-cos && cd my-cos
  git remote set-url origin <your-private-repo-url>
  bash plugin/scripts/init-fork.sh

(If you really mean to scaffold here, re-run with --force.)
EOF
        exit 2
    fi
    echo "WARN: --force set; scaffolding despite framework-repo origin."
fi

# Fork mode: the project carries the plugin at ./plugin and that is the plugin
# running now. The only difference it makes is the closing advice (register the
# local marketplace); the scaffold is identical.
FORK_MODE=0
if [ -d "${PROJECT}/plugin/.claude-plugin" ] && [ "$( cd "${PROJECT}/plugin" && pwd )" = "${PLUGIN_ROOT}" ]; then
    FORK_MODE=1
fi

# ----- Prerequisites -----
missing_templates=0
for t in \
    "${SKELETON}/knowledge/constitution.template.md" \
    "${SKELETON}/memory/templates/operational-memory.template.md" \
    "${SKELETON}/memory/digest-sources.template.md" \
    "${SKELETON}/memory/digest-state.template.md" \
    "${SKELETON}/memory/triage-heuristic.template.yaml" \
    "${TEMPLATES}/settings.template.json" \
    "${TEMPLATES}/governance.config.template.yaml" \
    "${TEMPLATES}/CLAUDE.template.md"
do
    [ -f "$t" ] || { echo "ERROR: expected template missing: ${t#"${PLUGIN_ROOT}"/} (is this a Giovanni plugin?)" >&2; missing_templates=1; }
done
[ "${missing_templates}" -eq 0 ] || exit 2

for layer in $(printf '%s' "${WITHOUT}" | tr ',' ' '); do
    case "${layer}" in
        predictive|stakeholders|digest) ;;
        *) echo "ERROR: unknown layer in --without: ${layer} (known: predictive, stakeholders, digest)" >&2; exit 2 ;;
    esac
done

# ----- Confirm -----
if [ "${ASSUME_YES}" -ne 1 ]; then
    echo "About to scaffold Giovanni in: ${PROJECT}"
    echo "  → copy templates to runtime files (existing files preserved)"
    echo "  → create memory/{stakeholders,topics,decisions,briefs,archive,…}/"
    echo "  → regenerate MAP.md / INDEX.md, run lint (informational)"
    printf "Proceed? [y/N] "
    read -r reply
    case "${reply}" in y|Y|yes|YES) ;; *) echo "Aborted."; exit 0 ;; esac
fi

echo ""
echo "Scaffolding Giovanni in ${PROJECT}…"

# ----- 1. Copy templates → runtime (skip existing unless --force) -----
copy_template() {
    local src="$1" dst="$2"
    if [ -f "${dst}" ] && [ "${FORCE}" -ne 1 ]; then
        echo "  = ${dst} exists — kept (use --force to re-copy)"
        return 0
    fi
    mkdir -p "$(dirname "${dst}")"
    cp "${src}" "${dst}"
    echo "  + ${dst}"
}

# Copy every file of a skeleton directory, one level, never overwriting.
copy_dir() {
    local src="$1" dst="$2" f pat skip
    [ -d "${src}" ] || return 0
    mkdir -p "${dst}"
    for f in "${src}"/*; do
        [ -f "${f}" ] || continue
        case "$(basename "${f}")" in .gitkeep) continue ;; esac
        skip=0
        for pat in ${EXCLUDE:-}; do
            # shellcheck disable=SC2254
            case "$(basename "${f}")" in ${pat}) skip=1 ;; esac
        done
        [ "${skip}" -eq 1 ] && continue
        if [ -f "${dst}/$(basename "${f}")" ] && [ "${FORCE}" -ne 1 ]; then
            continue
        fi
        cp "${f}" "${dst}/"
    done
    echo "  + ${dst}/ ($(find "${dst}" -maxdepth 1 -type f | wc -l | tr -d ' ') files)"
}

# Runtime files a session reads and writes.
copy_template "${TEMPLATES}/governance.config.template.yaml"                "docs/governance.config.yaml"

# Layers. --without switches a layer off in the project config; the config then
# decides what gets scaffolded, now and on every re-run.
for layer in $(printf '%s' "${WITHOUT}" | tr ',' ' '); do
    python3 "${SCRIPT_DIR}/gconfig.py" --repo "${PROJECT}" set-layer "${layer}" false
    echo "  · layer ${layer}: off"
done
layer_on() { python3 "${SCRIPT_DIR}/gconfig.py" --repo "${PROJECT}" layer "$1" 2>/dev/null; }
PREDICTIVE=1; layer_on predictive || PREDICTIVE=0
STAKEHOLDERS=1; layer_on stakeholders || STAKEHOLDERS=0
DIGEST=1; layer_on digest || DIGEST=0
# Template / example files that belong to a switched-off layer are not copied.
EXCLUDE=""
[ "${PREDICTIVE}" -eq 0 ] && EXCLUDE="${EXCLUDE} branch-out* shadow* calibration* triage* decided-terms*"
[ "${STAKEHOLDERS}" -eq 0 ] && EXCLUDE="${EXCLUDE} stakeholder*"
[ "${DIGEST}" -eq 0 ] && EXCLUDE="${EXCLUDE} digest*"

copy_template "${SKELETON}/knowledge/constitution.template.md"              "knowledge/constitution.md"
copy_template "${SKELETON}/memory/templates/operational-memory.template.md" "memory/CLAUDE_MEMORY.md"
if [ "${DIGEST}" -eq 1 ]; then
    copy_template "${SKELETON}/memory/digest-sources.template.md"           "memory/digest_sources.md"
    copy_template "${SKELETON}/memory/digest-state.template.md"             "memory/digest_state.md"
fi
if [ "${PREDICTIVE}" -eq 1 ]; then
    copy_template "${SKELETON}/memory/triage-heuristic.template.yaml"       "memory/triage-heuristic.yaml"
fi

# The permission half of the external write gate + autoMemoryEnabled: false. The
# hooks ship with the plugin; a plugin cannot carry permissions, so this file does.
copy_template "${TEMPLATES}/settings.template.json"                         ".claude/settings.json"

# What the agents read at run time: schema READMEs, per-artifact templates, worked
# examples, the canonical-moves registry. Project-owned so a fork can edit them.
copy_template "${SKELETON}/knowledge/README.md"                             "knowledge/README.md"
copy_template "${SKELETON}/memory/README.md"                                "memory/README.md"
copy_dir      "${SKELETON}/memory/templates"                                "memory/templates"
copy_dir      "${SKELETON}/memory/examples"                                 "memory/examples"
if [ "${PREDICTIVE}" -eq 1 ]; then
    copy_dir  "${SKELETON}/memory/branch-out"                               "memory/branch-out"
    copy_dir  "${SKELETON}/memory/calibration"                              "memory/calibration"
    copy_dir  "${SKELETON}/memory/shadow"                                   "memory/shadow"
fi
copy_dir      "${SKELETON}/deliverables"                                    "deliverables"

# The operating contract. Three cases:
#   no CLAUDE.md                      → the template becomes CLAUDE.md
#   the framework's meta-builder one  → swapped (a fresh fork clone), original kept
#   your own CLAUDE.md                → never touched; the contract is written beside
#                                       it and you import it with one @ line
if [ ! -f "CLAUDE.md" ] || grep -q "meta-builder mode" "CLAUDE.md" 2>/dev/null || [ "${FORCE}" -eq 1 ]; then
    if [ -f "CLAUDE.md" ]; then
        mkdir -p docs && cp "CLAUDE.md" "docs/framework-CLAUDE.md.bak"
        echo "  · previous CLAUDE.md kept at docs/framework-CLAUDE.md.bak"
    fi
    cp "${TEMPLATES}/CLAUDE.template.md" "CLAUDE.md"
    echo "  + CLAUDE.md (operating contract)"
else
    copy_template "${TEMPLATES}/CLAUDE.template.md" "docs/CLAUDE.giovanni.md"
    if ! grep -q "@docs/CLAUDE.giovanni.md" "CLAUDE.md" 2>/dev/null; then
        echo "  ! CLAUDE.md is yours — kept. Import the contract by adding this line to it:"
        echo "        @docs/CLAUDE.giovanni.md"
    fi
fi

# ----- 2. Runtime memory subdirectories -----
RUNTIME_DIRS="topics decisions briefs archive"
[ "${STAKEHOLDERS}" -eq 1 ] && RUNTIME_DIRS="stakeholders ${RUNTIME_DIRS}"
[ "${PREDICTIVE}" -eq 1 ] && RUNTIME_DIRS="${RUNTIME_DIRS} shadow/pending shadow/resolved shadow/expired branch-out calibration/monthly"
for d in ${RUNTIME_DIRS}
do
    if [ ! -d "memory/${d}" ]; then
        mkdir -p "memory/${d}"
        touch "memory/${d}/.gitkeep"
        echo "  + memory/${d}/"
    fi
done

# ----- 3. Seed audit_state.md + stakeholder roster README -----
if [ ! -f "memory/audit_state.md" ]; then
    TODAY=$(date +%F)
    cat > "memory/audit_state.md" <<EOF
# Memory audit state

> Seeded by Giovanni's init on ${TODAY}. Read by the session-start audit hook
> (plugin hooks/session-start-audit-check.sh); update the dates when you run an audit.

- last_audit_full: ${TODAY}
- last_audit_light: ${TODAY}
- last_watch_scan: ${TODAY}
EOF
    echo "  + memory/audit_state.md"
fi

if [ "${STAKEHOLDERS}" -eq 1 ] && [ -f "${SKELETON}/memory/templates/stakeholders-README.template.md" ] && [ ! -f "memory/stakeholders/README.md" ]; then
    cp "${SKELETON}/memory/templates/stakeholders-README.template.md" "memory/stakeholders/README.md"
    echo "  + memory/stakeholders/README.md"
fi

# Machine-local state of the autonomy layer (telemetry, run logs, locks) and the
# raw chat-export workspace of /giovanni:learn-history (.history/) never go into
# git: per machine, noisy, and full of personal data.
touch .gitignore
for pat in "memory/.telemetry/" "memory/.runs/" "memory/.*.lock" ".history/"; do
    grep -qxF "${pat}" .gitignore 2>/dev/null || { printf '%s\n' "${pat}" >> .gitignore; echo "  + .gitignore: ${pat}"; }
done

# ----- 4. Plugin root marker + executable bits -----
# The git hooks run outside any Claude session and have to find the plugin; the
# session-start hook refreshes this marker every session, this is the first write.
GIT_COMMON=$(git rev-parse --git-common-dir 2>/dev/null || echo "")
if [ -n "${GIT_COMMON}" ]; then
    case "${GIT_COMMON}" in /*) ;; *) GIT_COMMON="${PROJECT}/${GIT_COMMON}" ;; esac
    printf '%s\n' "${PLUGIN_ROOT}" > "${GIT_COMMON}/giovanni-plugin-root"
    echo "  · plugin root recorded in $(basename "${GIT_COMMON}")/giovanni-plugin-root"
fi
chmod +x "${PLUGIN_ROOT}"/hooks/*.sh "${PLUGIN_ROOT}"/scripts/*.sh "${PLUGIN_ROOT}"/scripts/git-hooks/* 2>/dev/null || true

# ----- 5. Regenerate navigation indexes -----
if [ "${SKIP_REGEN}" -ne 1 ]; then
    if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
        echo "  · shallow clone — skipping MAP/INDEX regen (run 'git fetch --unshallow' then re-run)"
    else
        # INDEX first: the MAP lists knowledge/INDEX.md when it exists, so the other
        # order leaves a MAP that the very next lint calls stale.
        GIOVANNI_REPO_ROOT="${PROJECT}" bash "${SCRIPT_DIR}/build-knowledge-index.sh" >/dev/null 2>&1 && echo "  · knowledge/INDEX.md regenerated"
        GIOVANNI_REPO_ROOT="${PROJECT}" bash "${SCRIPT_DIR}/build-memory-map.sh"     >/dev/null 2>&1 && echo "  · memory/MAP.md regenerated"
    fi
fi

# ----- 6. Lint (informational — placeholders are expected in a fresh project) -----
echo ""
echo "Running lint (informational — findings below are your fill-in to-do list)…"
echo "────────────────────────────────────────────────────────────────────"
LINT_REPO_ROOT="${PROJECT}" bash "${SCRIPT_DIR}/lint.sh" || true
echo "────────────────────────────────────────────────────────────────────"

echo ""
echo "Scaffolded. Next steps (docs/setup-guide.md in the plugin has the full walkthrough):"
echo ""
echo "  · Fill knowledge/constitution.md          — your operating principles, posture, roles"
[ "${STAKEHOLDERS}" -eq 1 ] && echo "  · Bootstrap memory/stakeholders/<slug>.md  — 5-10 key people (agent giovanni:profile-bootstrap)"
[ "${DIGEST}" -eq 1 ] && echo "  · Configure memory/digest_sources.md      — your chat / email / calendar / tracker sources"
[ "${DIGEST}" -eq 1 ] && echo "  · Seed memory/digest_state.md             — set a first-run window timestamp"
echo "  · bash \"${PLUGIN_ROOT}/scripts/install-hooks.sh\""
echo "                                             — git pre-commit (regen + lint) and pre-push gates"
echo "  · Review .claude/settings.json            — the external write gate's permission layer"
echo "  · Autonomy layer (inbox, autocommit, schedule, learning) is opt-in: docs/autonomy.md in the plugin"
[ "${DIGEST}" -eq 1 ] && echo "  · /giovanni:digest --force                — first digest run"

if [ "${FORK_MODE}" -eq 1 ]; then
    cat <<EOF

This is a fork clone: the plugin is at ./plugin. Register it once so Claude Code
loads its skills, agents and hooks in this repo:

  claude plugin marketplace add "${PROJECT}"
  claude plugin install giovanni@giovanni --scope project

A fully-filled reference instance lives in examples/lattice-finance/.
EOF
fi
