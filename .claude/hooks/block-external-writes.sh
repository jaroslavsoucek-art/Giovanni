#!/usr/bin/env bash
# PreToolUse hook (matcher: mcp__.*) — technical enforcement of the external write gate.
#
# Policy source: docs/governance.md § External write gate (binding).
# The doc half of the gate is prose the agent can rationalise around. This hook is the
# half that cannot be talked out of: it sits between the model and the connector.
#
#   demoted channel write  -> deny   (channel demotion, governance.md § Channel demotion)
#   any other write verb   -> ask    (explicit per-action confirmation)
#   local / harness MCP    -> pass   (not an external destination)
#   reads                  -> pass
#
# Emits a PreToolUse permissionDecision JSON on stdout, exit 0. Unparseable input = pass
# (defer to the normal permission flow — permissions.deny/ask in .claude/settings.json
# apply independently of this hook; two layers, neither load-bearing alone).
#
# Configuration
#   GIOVANNI_READONLY_CHANNELS  comma-separated tool-name prefixes demoted to read-only
#                               (e.g. "slack,teams"). Falls back to `readonly_channels:`
#                               in docs/governance.config.yaml. Default: none.
#   GIOVANNI_MCP_EXEMPT_EXTRA   comma-separated extra exempt server prefixes.
#
# A demoted channel is read-only ABSOLUTELY: no send, no draft-in-platform, no schedule,
# no canvas/page edit — even when the instruction sounds like a send. Output for that
# channel is copy-paste text in chat; the principal posts it themselves.

set +e
INPUT=$(cat)

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)

printf '%s' "$INPUT" | GIOVANNI_REPO_ROOT="${REPO_ROOT}" python3 -c "
import json, os, re, sys

try:
    d = json.load(sys.stdin)
    name = d.get('tool_name', '')
except Exception:
    sys.exit(0)

if not name.startswith('mcp__'):
    sys.exit(0)

# --- Local / harness servers: not external destinations, no gate. ---
EXEMPT = [
    'mcp__ccd_', 'mcp__visualize__', 'mcp__pdf-viewer__', 'mcp__mcp-registry__',
    'mcp__Control_Chrome__', 'mcp__claude-in-chrome__', 'mcp__Claude_Preview__',
]
EXEMPT += [p.strip() for p in os.environ.get('GIOVANNI_MCP_EXEMPT_EXTRA', '').split(',') if p.strip()]
if name.startswith(tuple(EXEMPT)):
    sys.exit(0)

tool = name.split('__')[-1]
low = tool.lower()


def readonly_channels():
    env = os.environ.get('GIOVANNI_READONLY_CHANNELS')
    if env is not None:
        return [c.strip().lower() for c in env.split(',') if c.strip()]
    cfg = os.path.join(os.environ.get('GIOVANNI_REPO_ROOT', '.'), 'docs', 'governance.config.yaml')
    try:
        with open(cfg, encoding='utf-8') as fh:
            body = fh.read()
    except OSError:
        return []
    m = re.search(r'(?m)^readonly_channels:\s*(.*)$', body)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith('['):
        return [c.strip().strip('\'\"').lower() for c in inline.strip('[]').split(',') if c.strip()]
    out = []
    for line in body[m.end():].splitlines():
        if not line.startswith((' ', '\t', '-')):
            break
        item = line.strip()
        if item.startswith('- '):
            out.append(item[2:].strip().strip('\'\"').lower())
    return out


def decide(decision, reason):
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'permissionDecision': decision,
        'permissionDecisionReason': reason,
    }}))
    sys.exit(0)


# Only write-shaped calls are gated. Everything else — read, get, list, search — passes.
# Verbs are matched as a token (create_page, slack_send_message) or as a camelCase prefix
# (createConfluencePage), which is where every connector puts its verb. A mid-word match
# is deliberately NOT a hit: getConfluencePageFooterComments is a read.

WRITE_VERBS = (
    'create|update|delete|edit|send|post|publish|schedule|draft|add|remove|set|'
    'transition|upload|move|merge|reply|comment|insert|save|write|assign|invite|'
    'import|commit|cancel|archive|resize|copy|generate|share|approve|resolve|react'
)
WRITE_RE = re.compile(r'(^|[_-])(' + WRITE_VERBS + r')([_-]|$)|^(' + WRITE_VERBS + r')', re.IGNORECASE)
is_write = bool(WRITE_RE.search(low))

# --- Demoted channels: read-only, absolutely. ---
for channel in readonly_channels():
    if channel and (channel in name.lower()):
        if not is_write:
            sys.exit(0)
        decide('deny',
               channel + ' is a demoted channel — read-only, absolutely '
               '(docs/governance.md § Channel demotion). Produce copy-paste text in chat; '
               'the principal posts it. Re-promotion needs a decision record, not this call.')

# --- Everything else external: writes need explicit per-action confirmation. ---
if is_write:
    decide('ask',
           'External write gate (docs/governance.md): a write to an external system needs '
           'explicit confirmation of THIS action, naming destination and action. An ambiguous '
           'instruction (\"handle this\", \"do item 1\") is not publish authorization.')

sys.exit(0)
"

exit 0
