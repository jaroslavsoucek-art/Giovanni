#!/usr/bin/env bash
# hooks/lib/env.sh — sourced by every Giovanni hook and shell script. Plain shell.
#
# Two things differ on native Windows (Git Bash) and fail silently there:
#
#   * The interpreter. `python3` is often missing, or is the Microsoft Store
#     stub that prints a message and exits; a python.org install provides
#     `python` and `py` instead. On Windows the first candidate that actually
#     runs hookutil.py wins. Everywhere else it is `python3`, unprobed, so the
#     hooks cost no extra process start on macOS and Linux.
#   * Text encoding. Python's default there is the ANSI code page, so a config
#     or a memory file with non-ASCII text fails to parse and a hook's JSON
#     with non-ASCII text fails to print. PYTHONUTF8=1 fixes both.
#
# GIOVANNI_PYTHON overrides the probe (a name on PATH or an absolute path).
# Sets and exports GIOVANNI_PY.

export PYTHONUTF8=1
GIOVANNI_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "${GIOVANNI_PY:-}" ]; then
    if [ -n "${GIOVANNI_PYTHON:-}" ]; then
        GIOVANNI_PY="${GIOVANNI_PYTHON}"
    else
        case "$(uname -s 2>/dev/null)" in
            MINGW*|MSYS*|CYGWIN*)
                for candidate in python3 python py; do
                    if command -v "${candidate}" >/dev/null 2>&1 \
                        && [ "$("${candidate}" "${GIOVANNI_LIB_DIR}/hookutil.py" ping 2>/dev/null | tr -d '\r')" = "ok" ]; then
                        GIOVANNI_PY="${candidate}"
                        break
                    fi
                done
                ;;
        esac
        GIOVANNI_PY="${GIOVANNI_PY:-python3}"
    fi
fi
export GIOVANNI_PY
