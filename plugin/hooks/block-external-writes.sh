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
# Run only under Claude Code: the helpers live at a literal path under the plugin root.
[ -n "${CLAUDE_PLUGIN_ROOT:-}" ] || exit 0
REPO_ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
GIOVANNI_REPO_ROOT="${REPO_ROOT}" python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lib/write_gate.py"
exit 0
