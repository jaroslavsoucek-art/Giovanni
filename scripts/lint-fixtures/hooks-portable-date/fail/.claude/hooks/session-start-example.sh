#!/usr/bin/env bash
set -euo pipefail

age_days() {
    date -j -u -f "%Y-%m-%d" "$1" +%s 2>/dev/null || date -u -d "$1" +%s 2>/dev/null
}

timeout 10 git fetch --quiet origin
echo "$(age_days 2026-01-01)"
