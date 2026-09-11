#!/usr/bin/env bash
# scripts/source-path.sh — resolve the path to the LIVE reference implementation.
#
# Giovanni is distilled from a working AI Chief of Staff implementation. Architect
# agents read that implementation to extract patterns. This script is the one place
# that answers "where is it", so no path is hardcoded anywhere in the tree.
#
# Resolution order:
#   1. $GIOVANNI_SOURCE            — env var, wins
#   2. .source-path                — machine-local file at repo root (gitignored)
#   3. nothing                     — exit 1 with instructions
#
# Why not commit the path: this repo is public and the source is a private
# operational repo. Its name identifies the domain Giovanni was deliberately
# sanitised of, and its contents include financials and profiles of named people.
# The pointer is machine-local; the framework is not.
#
# Usage:
#   SRC=$(bash scripts/source-path.sh) || exit 1
#   bash scripts/source-path.sh --check     # validate only, print nothing on success
#   bash scripts/source-path.sh --sha       # print the source's current HEAD (provenance)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-path}"

resolve() {
    if [ -n "${GIOVANNI_SOURCE:-}" ]; then
        printf '%s' "${GIOVANNI_SOURCE}"
        return 0
    fi
    if [ -f "${REPO_ROOT}/.source-path" ]; then
        head -1 "${REPO_ROOT}/.source-path" | tr -d '\n' | sed "s|^~|${HOME}|"
        return 0
    fi
    return 1
}

if ! SRC=$(resolve) || [ -z "${SRC}" ]; then
    cat >&2 <<EOF
No source implementation configured.

Architect agents read patterns from a live reference implementation. Point at it:

  echo "/path/to/your/source-repo" > ${REPO_ROOT}/.source-path

or export GIOVANNI_SOURCE=/path/to/your/source-repo

.source-path is gitignored — the pointer stays on this machine.
EOF
    exit 1
fi

if [ ! -d "${SRC}" ]; then
    echo "Source path does not exist: ${SRC}" >&2
    exit 1
fi

case "${MODE}" in
    --check) exit 0 ;;
    --sha)   git -C "${SRC}" rev-parse --short HEAD 2>/dev/null || echo "unknown" ;;
    *)       printf '%s\n' "${SRC}" ;;
esac
