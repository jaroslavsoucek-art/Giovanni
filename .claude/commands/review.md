---
description: Adversarial review of a draft. Routes to adversarial-reviewer agent. Returns SHIP / REWRITE / KILL verdict + prioritized issues + strongest counter-case. Read-only.
allowed-tools: Task, Read, Grep, Glob, Bash
---

# /review

Run adversarial review on a draft (decision record, position paper, board material, customer message, fundraise narrative, constitution patch, predictive forecast). This command is a **thin shell** — the adversarial mode policy, four-pass protocol, strongest counter-case requirement, and SHIP/REWRITE/KILL discipline live in the `adversarial-reviewer` agent. This file is the invocation contract.

## Usage

```
/review <draft-path>                     # required positional — path to draft file
/review <draft-path> --position "..."    # optional one-line position statement
/review <draft-path> --audience external # internal | external | mixed
```

If `<draft-path>` is omitted, the orchestrator looks for the draft inline in the message (paste-mode). If neither is present → STOP with usage hint.

## Argument syntax

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `<draft-path>` | positional | — | Relative path to draft file (e.g. `deliverables/<file>`, `memory/briefs/<file>`, `memory/decisions/<file>`). |
| `--position "<text>"` | parameterized string | derived from draft | One-line statement of the position the draft is defending. If absent, the agent derives it from the draft itself. If the agent can't derive a clear position, that ambiguity is itself a finding. |
| `--audience <level>` | parameterized | inferred | `internal` / `external` / `mixed`. If absent, the agent infers from path and content. |

Quoted strings supported. `--flag=value` and `--flag value` both work.

## Pre-flight (binding — STOP on failure)

Before spawning `adversarial-reviewer`:

1. **CWD check.** Working directory is a Giovanni repo. Otherwise STOP.
2. **Agent definition present.** `.claude/agents/adversarial-reviewer.md` exists. Missing → STOP.
3. **Draft accessible.** If `<draft-path>` is set: file exists and is readable. Otherwise STOP: `ERROR: cannot read <path>.`
4. **Trigger sanity check.** If the draft contains explicit out-of-scope markers ("brainstorming", "thinking out loud", "[no review yet]"), surface advisory:
   `WARN: draft contains brainstorming-mode marker. Adversarial review may suppress the exploration that's the point. Proceed? [y/N]`. Default = abort.
5. **No required state files.** Adversarial review is read-only over the draft and repo — no state files to validate.

If `<draft-path>` is absent AND no draft inline in message → STOP: `ERROR: /review requires either <draft-path> or inline draft block. Usage: /review <relative/path/to/draft>`.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Spawn `adversarial-reviewer`** via `Task` with:
   ```
   subagent_type: adversarial-reviewer
   path: <draft-path or "inline">
   position: <text or null>
   audience: <internal | external | mixed | null>
   ```
   If inline mode, the orchestrator passes the draft body as `extra_context`.
3. **Wait for agent return.** The agent:
   - Reads draft top-to-bottom + referenced files (constitution, decision records, profiles, topic shards)
   - Runs four passes (factual integrity, missing perspectives, symmetry/padding, voice/quality)
   - Constructs strongest counter-case
   - Emits verdict (SHIP / REWRITE / KILL) + prioritized issues
4. **Relay agent output verbatim** to chat. The verdict body opens with `SHIP`, `REWRITE`, or `KILL` — no softening preamble.
5. **No persistent artifact by default.** Adversarial review is delivered in-conversation. Forks that opt into persistent logging (per `docs/adversarial.md`) write to `memory/intel/adversarial/<YYYY-MM-DD>_<slug>.md`. The orchestrator does NOT auto-write the log — the principal decides.
6. **Do NOT modify the draft.** Read-only. The principal acts on the verdict.

## Verdict discipline

The agent returns one of three verdicts — fixed enum, no compounds:

- **SHIP** — defensible position, evidence supports, no fatal counter-case. Minor cosmetic fixes optional.
- **REWRITE** — position has merit but execution has material issues. Identifiable fixes; path forward.
- **KILL** — position is wrong, evidence weak, or counter-case fatal. Do not send. Go back to strategy.

If borderline → REWRITE, not SHIP. The verdict is binary in nature.

The orchestrator does **not** soften the verdict in relay. "MOSTLY SHIP" is not a real verdict.

## When the agent declines

The agent declines adversarial review in three contexts (returns one-line decline + route hint):

1. **Brainstorming / early-stage exploration** → route to free dialogue, not pushback
2. **Moments of distress** → adversarial review is not crisis support
3. **Mechanical execution tasks** (typos, formatting, link-check) → route to `deliverable-reviewer`

The principal can override the decline with explicit "yes I want adversarial review on this anyway" — at that point, the agent runs the protocol.

## Output behavior

- **Render target:** chat (verdict + issues + strongest counter-case + verbatim strikes)
- **Persistent artifacts:** none by default. Optional `memory/intel/adversarial/<YYYY-MM-DD>_<slug>.md` if fork opted in (principal writes manually).
- **No mutation to the draft or any other file.** Read-only agent, read-only command.
- **No auto-commit.**

## Error handling

- **Pre-flight failure** → STOP with diagnostic.
- **Draft path unreadable** → STOP at pre-flight.
- **Agent decline (out of scope)** → relay decline verbatim with route hint.
- **SHIP with zero issues** → the agent re-reads once. If still zero issues, the verdict is returned but flagged: "no issues surfaced after two passes; consider whether this draft is too low-stakes to warrant adversarial review". The orchestrator relays the flag.

## Output language

The agent matches the draft's language (Czech draft → Czech verdict; English draft → English). The orchestrator does NOT switch languages in relay.

## Cross-references

- **Agent (executor):** `.claude/agents/adversarial-reviewer.md`
- **Workflow policy:** `.claude/workflows/adversarial-review.md` (triggers, scope, anti-patterns, calibration)
- **Related command:** `/redline` (alias emphasizing verbatim strike list)
- **Adjacent agent:** `deliverable-reviewer` (mechanical content QA — different layer, same artifact OK)
- **Optional persistent log + lint:** `memory/intel/adversarial/`, `scripts/lint_rules/adversarial_verdict_format.py`

## Anti-patterns (binding)

- **Softening the verdict in relay** — "MOSTLY SHIP" / "MILD REWRITE" / "SOFT KILL" are anti-patterns. The three-tier enum is exhaustive.
- **Auto-running on a pasted draft without explicit trigger** — the agent declines and asks. The orchestrator does not bypass that decline.
- **Auto-applying suggested fixes** — adversarial review is read-only. The principal fixes.
- **Adding RLHF preambles in relay** ("Great draft, just...") — verdict opens with SHIP/REWRITE/KILL.
- **Switching languages between draft and verdict** — agent matches; orchestrator does not override.
- **Auto-writing the persistent log** — opt-in only, principal-written.
