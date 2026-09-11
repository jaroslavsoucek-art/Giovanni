#!/usr/bin/env bash
# Portable: dates via python3, bounded fetch via a probed timeout.
# Counter-example kept in a comment on purpose — `date -j` here must NOT trip the rule.
set -euo pipefail

age_days() {
    python3 -c "
import datetime, sys
print(int(datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
      .replace(tzinfo=datetime.timezone.utc).timestamp()))
" "$1" 2>/dev/null
}

if command -v timeout >/dev/null 2>&1; then TIMEOUT=timeout; else TIMEOUT=""; fi
echo "${TIMEOUT:-no-timeout} $(age_days 2026-01-01)"
