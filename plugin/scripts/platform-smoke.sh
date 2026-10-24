#!/usr/bin/env bash
# scripts/platform-smoke.sh — run the plugin's hooks the way Claude Code runs them, on this machine.
#
# The self-tests call the Python halves directly. This calls the hooks themselves —
# `bash "<plugin>/hooks/<file>.sh"` with CLAUDE_PLUGIN_ROOT and CLAUDE_PROJECT_DIR set to
# native paths (C:\... on Windows) — against a throwaway project, so what fails here is
# what would fail silently in a session: the interpreter probe, UTF-8, the lock, LF line
# endings, path handling, the background autocommit. CI runs it on Linux and Windows;
# on a principal's machine it is the one-command answer to "do the hooks work here?".
#
# Usage: bash <plugin>/scripts/platform-smoke.sh      (exit 0 = all hooks behave)

set -uo pipefail
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$(dirname "${SCRIPT_DIR}")"
# Interpreter + UTF-8 for this platform (python3 on macOS/Linux; probed on Windows).
. "${PLUGIN_ROOT}/hooks/lib/env.sh"

PASS=0
FAIL=0
ok()   { printf '  ok    %s\n' "$1"; PASS=$((PASS + 1)); }
bad()  { printf '  FAIL  %s\n        %s\n' "$1" "${2:-}"; FAIL=$((FAIL + 1)); }
native() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }

echo "Platform smoke test — $(uname -s 2>/dev/null) · interpreter: ${GIOVANNI_PY}"
echo ""

# 1. interpreter and line endings
if [ "$("${GIOVANNI_PY}" "${PLUGIN_ROOT}/hooks/lib/hookutil.py" ping 2>/dev/null | tr -d '\r')" = "ok" ]; then
    ok "interpreter runs the hook helpers (${GIOVANNI_PY})"
else
    bad "interpreter runs the hook helpers" "set GIOVANNI_PYTHON to a working Python 3 with PyYAML"
fi
# Count CR bytes with tr, not grep: GNU grep on Windows handles CR in text mode by its
# own rules (CI saw it flag every LF file), and a byte count has no heuristics.
CRLF=""
for f in "${PLUGIN_ROOT}"/hooks/*.sh "${PLUGIN_ROOT}"/hooks/lib/*.sh "${PLUGIN_ROOT}"/scripts/*.sh "${PLUGIN_ROOT}"/scripts/git-hooks/*; do
    [ -f "${f}" ] || continue
    [ "$(tr -dc '\r' < "${f}" | wc -c | tr -d ' ')" -gt 0 ] && CRLF="${CRLF} $(basename "${f}")"
done
if [ -z "${CRLF}" ]; then ok "hook scripts have LF line endings"; else bad "hook scripts have LF line endings" "${CRLF}"; fi

# 2. throwaway project with the autonomy layer on
TMP="$(mktemp -d "${TMPDIR:-/tmp}/giovanni-smoke.XXXXXX")"
trap 'rm -rf "${TMP}"' EXIT
PROJ="${TMP}/project"
mkdir -p "${PROJ}/docs" "${PROJ}/memory" "${PROJ}/knowledge"
git -C "${PROJ}" init -q
git -C "${PROJ}" config user.email smoke@example.invalid
git -C "${PROJ}" config user.name smoke
cat > "${PROJ}/docs/governance.config.yaml" <<'YAML'
inbox:
  title: "Přehled dne"
autonomy:
  auto_commit_paths: ["memory/*"]
  confirm_paths: ["knowledge/*"]
learning:
  enabled: true
  correction_markers: ['^\s*ne[,.!\s]', '\bpříště\b']
YAML
printf 'memory/.telemetry/\nmemory/.runs/\nmemory/.*.lock\n' > "${PROJ}/.gitignore"
printf '# L1\n' > "${PROJ}/memory/CLAUDE_MEMORY.md"
git -C "${PROJ}" add -A >/dev/null && git -C "${PROJ}" commit -qm init >/dev/null

NPLUGIN="$(native "${PLUGIN_ROOT}")"
NPROJ="$(native "${PROJ}")"
hook() {  # hook <file> <stdin-json>  → stdout; exit code in HOOK_RC
    local out
    out=$(printf '%s' "$2" | CLAUDE_PLUGIN_ROOT="${NPLUGIN}" CLAUDE_PROJECT_DIR="${NPROJ}" \
          bash "${PLUGIN_ROOT}/hooks/$1" 2>"${TMP}/err")
    HOOK_RC=$?
    printf '%s' "${out}"
}

# 3. UTF-8 through the config reader
TITLE=$("${GIOVANNI_PY}" "${PLUGIN_ROOT}/scripts/gconfig.py" --repo "${NPROJ}" get inbox.title 2>/dev/null | tr -d '\r')
if [ "${TITLE}" = "Přehled dne" ]; then ok "config with non-ASCII text reads as UTF-8"; else bad "config with non-ASCII text reads as UTF-8" "got: ${TITLE}"; fi

# 4. every hook exits 0 on an empty event
for h in "${PLUGIN_ROOT}"/hooks/*.sh; do
    name=$(basename "${h}")
    hook "${name}" '{}' >/dev/null
    if [ "${HOOK_RC}" -eq 0 ]; then ok "hook ${name} exits 0"; else bad "hook ${name} exits 0" "rc=${HOOK_RC} $(head -2 "${TMP}/err")"; fi
done

# 5. hooks do their job
"${GIOVANNI_PY}" "${PLUGIN_ROOT}/scripts/inbox.py" --repo "${NPROJ}" add --kind test --text "Ověřit lhůtu" --key smoke:1 >/dev/null 2>&1
OUT=$(hook session-start-inbox.sh '{}')
case "${OUT}" in *INBOX*"Ověřit lhůtu"*) ok "session-start shows the inbox (UTF-8 intact)" ;; *) bad "session-start shows the inbox" "${OUT:0:200}" ;; esac

OUT=$(hook pre-edit-confirm.sh "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":$("${GIOVANNI_PY}" "${PLUGIN_ROOT}/hooks/lib/hookutil.py" system "${NPROJ}/knowledge/k.md" | sed 's/^{"systemMessage": //; s/}$//')}}")
case "${OUT}" in *'"ask"'*) ok "confirm path asks before an edit" ;; *) bad "confirm path asks before an edit" "${OUT:0:200}" ;; esac

OUT=$(hook prompt-correction.sh '{"prompt":"ne, příště to napiš jinak"}')
case "${OUT}" in *"LEARNING LOOP"*) ok "a correction is noticed (Czech marker)" ;; *) bad "a correction is noticed" "${OUT:0:200}" ;; esac

printf 'změna\n' > "${PROJ}/memory/x.md"
hook stop-autocommit.sh '{}' >/dev/null
COMMITTED=0
for _ in $(seq 1 40); do
    if git -C "${PROJ}" log --format=%s -1 2>/dev/null | grep -q "^chore(auto):"; then COMMITTED=1; break; fi
    sleep 0.5
done
if [ "${COMMITTED}" -eq 1 ]; then ok "background autocommit commits working state"; else bad "background autocommit commits working state" "$(git -C "${PROJ}" status --short | head -3)"; fi

echo ""
echo "Passed: ${PASS}  Failed: ${FAIL}"
[ "${FAIL}" -eq 0 ]
