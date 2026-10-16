---
description: Adversarial review variant emphasizing verbatim strike list — same agent as /review, prompt biased toward line-level redlines. Returns SHIP / REWRITE / KILL.
allowed-tools: Task, Read, Grep, Glob, Bash
---

# /redline

Run adversarial review on a draft with **emphasis on the verbatim-strike list** (lines, phrases, and sentences the principal should delete or replace). This command is an **alias** for `/review` — same agent (`adversarial-reviewer`), same verdict enum, same protocol — with a prompt parameter that biases the agent's output toward maximal line-level redlines.

Use `/redline` instead of `/review` when:

- The draft is ready in shape but needs surgical cuts before sending
- The principal already has the position locked and wants pure strike output, not strategic pushback
- Cosmetic / RLHF-stylism cleanup is the goal (the agent flags those as a verbatim strike list)

Use `/review` (not `/redline`) when:

- The position itself may be wrong (strategic pushback is the point)
- The draft is early-stage and needs counter-case construction, not line edits

The two commands return the same verdict format. The difference is emphasis: `/redline` weights Pass 3 (symmetry/padding/RLHF-stylisms) and the verbatim-strike section higher than the strongest-counter-case section. Both still run all four passes.

## Usage

```
/redline <draft-path>                     # required positional
/redline <draft-path> --position "..."    # optional one-line position statement
/redline <draft-path> --audience external # internal | external | mixed
```

If `<draft-path>` is omitted, the orchestrator looks for the draft inline in the message.

## Argument syntax

Identical to `/review`:

| Arg | Type | Default | Meaning |
|---|---|---|---|
| `<draft-path>` | positional | — | Relative path to draft file. |
| `--position "<text>"` | parameterized string | derived | One-line position statement. |
| `--audience <level>` | parameterized | inferred | `internal` / `external` / `mixed`. |

## Pre-flight (binding — STOP on failure)

Identical to `/review`. See `.claude/commands/review.md` § Pre-flight.

## Execution flow

1. **Run pre-flight.** STOP on any failure.
2. **Spawn `adversarial-reviewer`** via `Task` with the same params as `/review`, plus a prompt emphasis flag:
   ```
   subagent_type: adversarial-reviewer
   path: <draft-path or "inline">
   position: <text or null>
   audience: <internal | external | mixed | null>
   emphasis: redline                  # biases output toward verbatim-strike list
   ```
3. **Wait for agent return.** The agent runs all four passes but produces output weighted toward:
   - **Verbatim strikes** — exact phrases to delete or replace, expanded list
   - **Pass 3 findings** (symmetry, padding, RLHF preambles, AI-stylisms, hedge phrasing)
   - **Voice/quality findings** (Pass 4) when audience mismatch detected
4. **Relay agent output verbatim** to chat. Same verdict enum (SHIP / REWRITE / KILL).
5. **Do NOT modify the draft.** Read-only.

## Output emphasis (vs `/review`)

| Section | `/review` weighting | `/redline` weighting |
|---|---|---|
| Verdict (SHIP/REWRITE/KILL) | identical | identical |
| Strongest counter-case | full | full (still constructed, not skipped) |
| Pass 1 (factual integrity) | full | full |
| Pass 2 (missing perspectives) | full | full |
| Pass 3 (symmetry + padding) | normal | **heavier** |
| Pass 4 (voice + quality) | normal | **heavier** |
| Verbatim strikes section | normal list | **expanded — exhaustive line-level strikes** |
| Recommended next action | "fix and re-review" | "apply strikes, re-read" |

The discipline (no softening, no compounds, no validation theater) is **identical** to `/review`. The verdict enum is **identical**. The strongest counter-case is still constructed — `/redline` does not skip it, just doesn't lead with it.

## When NOT to use `/redline`

Same declines as `/review`:

1. **Brainstorming / early-stage exploration** — line-level redlines on an exploratory draft suppress the exploration
2. **Moments of distress** — not crisis support
3. **Mechanical execution tasks** — typos / formatting / link-check belong to `deliverable-reviewer`, not adversarial review

Additionally:

4. **Position is unclear** — if the draft's central position is ambiguous, `/redline` will surface that as a finding but won't fix the underlying ambiguity. Use `/review` (or revisit the draft) first.

## Output behavior

Identical to `/review`. See `.claude/commands/review.md` § Output behavior.

## Cross-references

- **Sibling command:** `/review` (full adversarial review, equal emphasis across passes)
- **Agent:** `.claude/agents/adversarial-reviewer.md`
- **Workflow policy:** `.claude/workflows/adversarial-review.md`
- **Adjacent agent:** `deliverable-reviewer` (mechanical content QA — different layer)

## Anti-patterns (binding)

Identical to `/review`. Plus:

- **Treating `/redline` as a "lighter" adversarial review** — it's not. Same verdict discipline, same protocol, different emphasis.
- **Skipping the strongest counter-case** because emphasis is on strikes — the counter-case still runs. If the draft's position is fatally flawed, `/redline` still returns KILL.
- **Using `/redline` to polish AI-generated text** — that's the AI-stylisms strike list, which `/redline` is good at; not "polishing" in a cosmetic sense, but stripping RLHF residue.
