#!/usr/bin/env python3
"""External write gate — the decision half of hooks/block-external-writes.sh.

Reads the PreToolUse JSON on stdin. Emits a permissionDecision for tool calls
on external connectors (mcp__*): `deny` for a write to a demoted (read-only)
channel, `ask` for any other write verb, nothing for reads or local/harness
servers. Unparseable input = no output = defer to the normal permission flow.

Policy source: docs/governance.md § External write gate. Configuration:
  GIOVANNI_READONLY_CHANNELS  comma-separated tool-name prefixes demoted to read-only;
                              falls back to `readonly_channels:` in docs/governance.config.yaml
  GIOVANNI_MCP_EXEMPT_EXTRA   comma-separated extra exempt server prefixes
  GIOVANNI_REPO_ROOT          project root (set by the shell wrapper)
"""
import json
import os
import re
import sys

EXEMPT = [
    "mcp__ccd_", "mcp__visualize__", "mcp__pdf-viewer__", "mcp__mcp-registry__",
    "mcp__Control_Chrome__", "mcp__claude-in-chrome__", "mcp__Claude_Preview__",
]
WRITE_VERBS = (
    "create|update|delete|edit|send|post|publish|schedule|draft|add|remove|set|"
    "transition|upload|move|merge|reply|comment|insert|save|write|assign|invite|"
    "import|commit|cancel|archive|resize|copy|generate|share|approve|resolve|react"
)
WRITE_RE = re.compile(r"(^|[_-])(" + WRITE_VERBS + r")([_-]|$)|^(" + WRITE_VERBS + r")", re.IGNORECASE)


def readonly_channels():
    env = os.environ.get("GIOVANNI_READONLY_CHANNELS")
    if env is not None:
        return [c.strip().lower() for c in env.split(",") if c.strip()]
    cfg = os.path.join(os.environ.get("GIOVANNI_REPO_ROOT", "."), "docs", "governance.config.yaml")
    try:
        with open(cfg, encoding="utf-8") as fh:
            body = fh.read()
    except OSError:
        return []
    m = re.search(r"(?m)^readonly_channels:\s*(.*)$", body)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith("["):
        return [c.strip().strip("'\"").lower() for c in inline.strip("[]").split(",") if c.strip()]
    out = []
    for line in body[m.end():].splitlines():
        if not line.startswith((" ", "\t", "-")):
            break
        item = line.strip()
        if item.startswith("- "):
            out.append(item[2:].strip().strip("'\"").lower())
    return out


def decide(decision, reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def main():
    try:
        d = json.load(sys.stdin)
        name = d.get("tool_name", "")
    except Exception:
        return
    if not name.startswith("mcp__"):
        return
    exempt = EXEMPT + [p.strip() for p in os.environ.get("GIOVANNI_MCP_EXEMPT_EXTRA", "").split(",") if p.strip()]
    if name.startswith(tuple(exempt)):
        return
    tool = name.split("__")[-1]
    is_write = bool(WRITE_RE.search(tool.lower()))
    for channel in readonly_channels():
        if channel and channel in name.lower():
            if not is_write:
                return
            decide("deny",
                   channel + " is a demoted channel — read-only, absolutely "
                   "(docs/governance.md § Channel demotion). Produce copy-paste text in chat; "
                   "the principal posts it. Re-promotion needs a decision record, not this call.")
    if is_write:
        decide("ask",
               "External write gate (docs/governance.md): a write to an external system needs "
               "explicit confirmation of THIS action, naming destination and action. An ambiguous "
               'instruction ("handle this", "do item 1") is not publish authorization.')


if __name__ == "__main__":
    main()
