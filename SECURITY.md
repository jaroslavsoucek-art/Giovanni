# Security policy

Giovanni is a **template / methodology repo**, not a deployed service. It ships
templates, schemas, agent definitions, lint rules, and bash/python helper
scripts that run **inside the user's own Claude Code session**, against their
own files.

There is no Giovanni-hosted endpoint, no Giovanni database, no Giovanni-side
authentication boundary. The threat model is therefore narrow.

## In scope

- **Lint/build scripts** in `scripts/` that could mishandle user paths (e.g.
  path traversal, command injection on filenames with shell metacharacters).
- **Claude Code hooks** in `.claude/hooks/` that could execute unintended code
  against the user's repo.
- **Workflow / agent prompts** that could be hijacked by malicious content in
  source files (prompt injection escalation paths).
- **Lint rules** that fail open on classes of footguns they claim to catch.

## Out of scope

- Whatever happens inside a user's fork (their domain content, their
  stakeholder data, their decision records).
- Claude Code itself, Anthropic API behaviors, or third-party MCP servers
  referenced abstractly in `<source_type>` enums.
- The fact that this is templates — no service to attack.

## Reporting a vulnerability

Open a private security advisory on GitHub:
**https://github.com/jaroslavsoucek-art/Giovanni/security/advisories/new**

Do **not** open a public Issue or Discussion for security findings.

Best-effort triage. No SLA — this is a hobby project. If you need
guaranteed turnaround, fork and own the patch.

## Disclosure

I will acknowledge receipt within 14 days when possible. If a fix lands, I'll
credit the reporter in the release notes unless asked otherwise.
