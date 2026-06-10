#!/usr/bin/env bash
# scripts/load-shell-env.sh
#
# Source only the export-like lines from the user's shell rc files so
# non-interactive shells (agent Bash tool, cron, hook contexts, scripts
# spawned from automation) see env vars — e.g. an <API_TOKEN> a source
# puller needs for a project-tracker or chat-platform API — that the user
# normally only exports in an interactive rc file.
#
# Why: agent tooling typically runs `bash -c "..."`, which is non-interactive
# and does NOT source ~/.zshrc / ~/.bashrc. Many users put exports in those
# interactive rc files (not .zshenv / .bash_profile), so tokens stay invisible
# to automation until this helper is sourced.
#
# Usage:
#   In a script:                source "$(dirname "$0")/load-shell-env.sh"
#   In a one-off bash command:  source scripts/load-shell-env.sh && <command>
#   In a cron entry:            bash -c 'source <repo>/scripts/load-shell-env.sh && <command>'
#
# Safe to source multiple times. Silent on errors. Only sources export-like
# lines (so the rc files' interactive bits — prompts, completions, aliases —
# don't fire and crash a non-interactive bash).
#
# Portable: bash 3.2 (macOS) + Linux.

_load_exports_from() {
  local file="$1"
  [ -f "$file" ] || return 0
  # Only `export NAME=VALUE` lines — skip aliases, function defs, shell-isms.
  while IFS= read -r line; do
    eval "$line" 2>/dev/null || true
  done < <(grep -E '^[[:space:]]*export[[:space:]]+[A-Z_][A-Z0-9_]*=' "$file" 2>/dev/null || true)
}

_load_exports_from "$HOME/.zshenv"
_load_exports_from "$HOME/.zshrc"
_load_exports_from "$HOME/.bash_profile"
_load_exports_from "$HOME/.bashrc"

unset -f _load_exports_from
