#!/usr/bin/env python3
"""Shared helper for Giovanni's hook scripts.

The hooks in ../ are plain shell on purpose: Anthropic's directory validator
follows plain shell scripts and refuses inline programs (python3 -c, awk '…',
jq '…') inside them. Everything that needs more than grep/tr/wc lives here and
is called by its literal path, `${CLAUDE_PLUGIN_ROOT}/hooks/lib/hookutil.py`.

Subcommands (stdin is the hook's JSON where noted):
  tool-name                      stdin → tool_name
  file-path                      stdin → tool_input.file_path
  commit-gate                    stdin → gate | skip | fallthrough
  context EVENT MSG              print hookSpecificOutput.additionalContext JSON
  system MSG                     print {"systemMessage": MSG}
  epoch date|iso VALUE           YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ → unix epoch (exit 1 if unparsable)
  field FILE REGEX first|last    third whitespace-separated token of the matching line
  trigger-conditions FILE        decision record → ok | empty
  strike-ratio STRIKE LINES MAX  → "<exceeds 0|1> <pct> <max pct>"
  ack-expired FILE               count of `- [ack …expires YYYY-MM-DD…]` lines past today
  ping                           prints "ok" — lib/env.sh uses it to find a working interpreter on Windows
"""
import datetime
import json
import re
import sys


def _stdin_json():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return None
    return d if isinstance(d, dict) else None


def cmd_tool_name(_args):
    d = _stdin_json()
    print((d or {}).get("tool_name", "") or "")


def cmd_file_path(_args):
    d = _stdin_json()
    ti = (d or {}).get("tool_input") or {}
    print(ti.get("file_path", "") if isinstance(ti, dict) else "")


def cmd_commit_gate(_args):
    d = _stdin_json()
    if d is None:
        print("fallthrough")
        return
    ti = d.get("tool_input") or {}
    cmd = ti.get("command") or "" if isinstance(ti, dict) else ""
    print("gate" if re.search(r"(^|[;&|]\s*)git(\s+-C\s+\S+)?\s+commit\b", cmd) else "skip")


def cmd_context(args):
    event, msg = args[0], args[1]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": msg}}))


def cmd_system(args):
    print(json.dumps({"systemMessage": args[0]}))


def cmd_epoch(args):
    kind, value = args[0], args[1]
    fmt = "%Y-%m-%dT%H:%M:%SZ" if kind == "iso" else "%Y-%m-%d"
    try:
        dt = datetime.datetime.strptime(value, fmt).replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        sys.exit(1)
    print(int(dt.timestamp()))


def cmd_field(args):
    path, pattern, which = args[0], args[1], args[2]
    rx = re.compile(pattern)
    hits = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if rx.search(line):
                    hits.append(line)
    except OSError:
        return
    if not hits:
        return
    line = hits[0] if which == "first" else hits[-1]
    parts = line.split()
    print(parts[2] if len(parts) > 2 else "")


_PLACEHOLDER = re.compile(r"<EMPTY|<TBD|<TODO|^\s*TBD\s*$|^\s*TODO\s*$", re.IGNORECASE | re.MULTILINE)


def cmd_trigger_conditions(args):
    """ok when the record carries trigger conditions in its section or frontmatter."""
    try:
        text = open(args[0], encoding="utf-8").read()
    except OSError:
        print("ok")
        return
    section, capturing = [], False
    for line in text.splitlines():
        if line.startswith("## Trigger conditions"):
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            section.append(line)
    body = "\n".join(section)
    stripped = re.sub(r"\s+", "", re.sub(r"<!--[^>]*-->", "", body))
    if stripped and not _PLACEHOLDER.search(body):
        print("ok")
        return
    fm = ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            m = re.search(r"(?m)^trigger_conditions:[ \t]*(.*)$", text[3:end])
            fm = m.group(1).strip() if m else ""
    fm_stripped = re.sub(r"\s+", "", fm)
    print("empty" if fm_stripped in ("", "[]", '""', "''") else "ok")


def cmd_strike_ratio(args):
    strike, lines, max_ratio = int(args[0]), int(args[1]), float(args[2])
    ratio = strike / lines if lines else 0.0
    print(f"{1 if ratio > max_ratio else 0} {ratio * 100:.1f} {max_ratio * 100:.0f}")


def cmd_ack_expired(args):
    today = datetime.datetime.now(datetime.timezone.utc).date()
    count = 0
    try:
        with open(args[0], encoding="utf-8") as fh:
            for line in fh:
                if not line.startswith("- [ack "):
                    continue
                m = re.search(r"expires (\d{4}-\d{2}-\d{2})", line)
                if not m or m.group(1) == "9999-12-31":
                    continue
                try:
                    exp = datetime.date.fromisoformat(m.group(1))
                except ValueError:
                    continue
                if exp < today:
                    count += 1
    except OSError:
        pass
    print(count)


def cmd_ping(_args):
    print("ok")


COMMANDS = {
    "ping": cmd_ping,
    "tool-name": cmd_tool_name,
    "file-path": cmd_file_path,
    "commit-gate": cmd_commit_gate,
    "context": cmd_context,
    "system": cmd_system,
    "epoch": cmd_epoch,
    "field": cmd_field,
    "trigger-conditions": cmd_trigger_conditions,
    "strike-ratio": cmd_strike_ratio,
    "ack-expired": cmd_ack_expired,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.stderr.write(__doc__)
        sys.exit(2)
    COMMANDS[sys.argv[1]](sys.argv[2:])
