#!/usr/bin/env bash
# scripts/init-fork.sh — scaffold a fresh Giovanni fork for your own domain.
#
# Run this once, from the root of YOUR clone of Giovanni, to turn the
# framework (templates only) into a fillable operational instance:
#
#   1. Copy each *.template.* to its runtime filename (constitution, L1
#      memory, digest sources/state, triage heuristic). Existing runtime
#      files are NEVER overwritten (idempotent; --force to re-copy).
#   2. Create the runtime memory subdirectories (stakeholders, topics,
#      decisions, briefs, archive) with .gitkeep.
#   3. Seed audit_state.md + the stakeholder roster README.
#   4. Make scripts + hooks executable.
#   5. Regenerate MAP.md / INDEX.md (skipped on shallow clones).
#   6. Run lint — INFORMATIONALLY. A freshly-scaffolded fork still has
#      template placeholders to fill, so lint findings here are your
#      to-do list, not an error. init-fork succeeds as long as scaffolding
#      succeeds.
#
# This is the mechanical half of "fork in <30 min" (definition-of-done #1).
# The other half — filling the constitution, bootstrapping stakeholders,
# wiring sources — is the multi-hour work walked through in
# docs/setup-guide.md.
#
# Usage:
#   bash scripts/init-fork.sh            # scaffold (interactive confirm)
#   bash scripts/init-fork.sh --yes      # non-interactive
#   bash scripts/init-fork.sh --force    # re-copy templates over existing runtime files
#   bash scripts/init-fork.sh --skip-regen   # don't run MAP/INDEX regen
#
# Idempotent — safe to re-run.

set -euo pipefail

ASSUME_YES=0
FORCE=0
SKIP_REGEN=0
while [ $# -gt 0 ]; do
    case "$1" in
        --yes|-y)     ASSUME_YES=1; shift ;;
        --force)      FORCE=1; shift ;;
        --skip-regen) SKIP_REGEN=1; shift ;;
        --help|-h)    sed -n '2,31p' "$0" | sed -E 's/^# ?//'; exit 0 ;;
        *) echo "Unknown arg: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "${REPO_ROOT}"

# ----- Guard: refuse to scaffold inside the canonical framework repo -----
# A real fork's origin points at YOUR repo, not the upstream. This stops
# init-fork from creating runtime files inside the Giovanni framework itself.
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
  bash scripts/init-fork.sh

(If you really mean to scaffold here, re-run with --force.)
EOF
        exit 2
    fi
    echo "WARN: --force set; scaffolding despite framework-repo origin."
fi

# ----- Prerequisites -----
missing_templates=0
for t in \
    "knowledge/constitution.template.md" \
    "memory/templates/operational-memory.template.md" \
    "memory/digest-sources.template.md" \
    "memory/digest-state.template.md" \
    "memory/triage-heuristic.template.yaml"
do
    [ -f "$t" ] || { echo "ERROR: expected template missing: $t (is this a Giovanni clone?)" >&2; missing_templates=1; }
done
[ "${missing_templates}" -eq 0 ] || exit 2

# ----- Confirm -----
if [ "${ASSUME_YES}" -ne 1 ]; then
    echo "About to scaffold a Giovanni fork in: ${REPO_ROOT}"
    echo "  → copy templates to runtime files (existing files preserved)"
    echo "  → create memory/{stakeholders,topics,decisions,briefs,archive}/"
    echo "  → regenerate MAP.md / INDEX.md, run lint (informational)"
    printf "Proceed? [y/N] "
    read -r reply
    case "${reply}" in y|Y|yes|YES) ;; *) echo "Aborted."; exit 0 ;; esac
fi

echo ""
echo "Scaffolding fork…"

# ----- 1. Copy templates → runtime (skip existing unless --force) -----
copy_template() {
    local src="$1" dst="$2"
    if [ -f "${dst}" ] && [ "${FORCE}" -ne 1 ]; then
        echo "  = ${dst} exists — kept (use --force to re-copy)"
        return 0
    fi
    cp "${src}" "${dst}"
    echo "  + ${dst}"
}

copy_template "knowledge/constitution.template.md"              "knowledge/constitution.md"
copy_template "memory/templates/operational-memory.template.md" "memory/CLAUDE_MEMORY.md"
copy_template "memory/digest-sources.template.md"               "memory/digest_sources.md"
copy_template "memory/digest-state.template.md"                 "memory/digest_state.md"
copy_template "memory/triage-heuristic.template.yaml"           "memory/triage-heuristic.yaml"

# ----- 2. Runtime memory subdirectories -----
for d in stakeholders topics decisions briefs archive \
         shadow/pending shadow/resolved shadow/expired branch-out calibration/monthly
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

> Seeded by scripts/init-fork.sh on ${TODAY}. Updated by the audit hooks
> (see .claude/hooks/session-start-audit-check.sh).

- **Monthly memory audit** — last: ${TODAY}. Next due ~${TODAY} (cadence 35d).
- **Light prune** — last: ${TODAY}. Next due ~${TODAY} (cadence 14d).
- **Watch scan** — last: ${TODAY}. Next due ~${TODAY} (cadence 7d).
EOF
    echo "  + memory/audit_state.md"
fi

if [ -f "memory/templates/stakeholders-README.template.md" ] && [ ! -f "memory/stakeholders/README.md" ]; then
    cp "memory/templates/stakeholders-README.template.md" "memory/stakeholders/README.md"
    echo "  + memory/stakeholders/README.md"
fi

# ----- 4. Make scripts + hooks executable -----
if [ -x "${SCRIPT_DIR}/install-hooks.sh" ] || [ -f "${SCRIPT_DIR}/install-hooks.sh" ]; then
    bash "${SCRIPT_DIR}/install-hooks.sh" --skip-precommit >/dev/null 2>&1 || true
    echo "  · scripts + hooks marked executable (run 'bash scripts/install-hooks.sh' to add the git pre-commit)"
fi

# ----- 5. Regenerate navigation indexes -----
if [ "${SKIP_REGEN}" -ne 1 ]; then
    if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
        echo "  · shallow clone — skipping MAP/INDEX regen (run 'git fetch --unshallow' then re-run)"
    else
        [ -f "${SCRIPT_DIR}/build-memory-map.sh" ]     && bash "${SCRIPT_DIR}/build-memory-map.sh"     >/dev/null 2>&1 && echo "  · memory/MAP.md regenerated"
        [ -f "${SCRIPT_DIR}/build-knowledge-index.sh" ] && bash "${SCRIPT_DIR}/build-knowledge-index.sh" >/dev/null 2>&1 && echo "  · knowledge/INDEX.md regenerated"
    fi
fi

# ----- 6. Lint (informational — placeholders are expected in a fresh fork) -----
echo ""
echo "Running lint (informational — findings below are your fill-in to-do list)…"
echo "────────────────────────────────────────────────────────────────────"
if [ -f "${SCRIPT_DIR}/lint.sh" ]; then
    bash "${SCRIPT_DIR}/lint.sh" || true
fi
echo "────────────────────────────────────────────────────────────────────"

cat <<'EOF'

Fork scaffolded. Next steps (see docs/setup-guide.md for the full walkthrough):

  1. Fill knowledge/constitution.md       — your operating principles, posture, stakeholders
  2. Bootstrap memory/stakeholders/<slug>.md — 5-10 key people (or run the profile-bootstrap agent)
  3. Configure memory/digest_sources.md   — your chat / email / calendar / tracker sources
  4. Seed memory/digest_state.md          — set a first-run window timestamp
  5. bash scripts/lint.sh                 — should go clean as you fill placeholders
  6. /digest --force                      — first digest run

A fully-filled reference fork lives in examples/lattice-finance/.
EOF
