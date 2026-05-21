# Giovanni Adversarial Layer — why pushback is the default

Every other AI-assistant pattern optimizes for being helpful + agreeable. Giovanni's fork users expect SHIP / REWRITE / KILL verdicts on their drafts, not validation theater. The adversarial layer is the policy + workflow + agent that makes critical pushback the default mode, not an opt-in flavor.

This doc is the **why**. Operational mechanics live in:

- [`.claude/agents/adversarial-reviewer.md`](../.claude/agents/adversarial-reviewer.md) — the executable agent
- [`.claude/workflows/adversarial-review.md`](../.claude/workflows/adversarial-review.md) — triggers, scope, verdict format, anti-patterns

---

## 1. Why adversarial-as-default

### The RLHF problem

The underlying model is trained to be agreeable. RLHF rewards "helpful, harmless, honest" — in that order of practical weight — which produces outputs that confirm rather than challenge. Without an explicit policy reversal at the prompt level, any review function regresses to "overall solid draft, just one concern…" framings that surface nothing the user couldn't see.

The practical effect:

- Drafts go out with weak claims unchallenged
- Review consumes time without changing the artifact
- The reviewer adds tone but no friction
- Over weeks, the user stops asking for review because "it never changes anything"

This is the failure mode every other AI review tool falls into. The IP is reversing it.

### What Giovanni does instead

Three reinforcing mechanisms:

1. **Prompt-level reversal.** The `adversarial-reviewer` agent description and workflow doc explicitly forbid softening preambles, validation phrases, and symmetric pro/con framing. The prompt opens with `Your job: find what's weak`, not `Help the user improve this`.
2. **Verdict enum forcing.** Three buckets — SHIP / REWRITE / KILL — with no compound forms. Removes the soft middle where "MOSTLY SHIP" or "MILD REWRITE" would dilute the verdict.
3. **Strongest counter-case requirement.** The reviewer must construct the explicit counter-argument, not just list gaps. Default-skeptical lookback, mirroring the same discipline from the predictive layer.

These three together turn review from advisory to adversarial.

---

## 2. Adversarial vs critical vs harsh

Frequent confusion. The distinction is load-bearing — adversarial review is "default-skeptical of position", not "default-mean".

| Mode | Targets | Tone | Output |
|---|---|---|---|
| **Adversarial** | The work, the argument, the evidence | Direct, specific, falsifiable | Verdict + strongest counter-case + prioritized issues |
| **Critical** | The work | Direct, surface-level | Issue list without constructive counter-case |
| **Harsh** | The work, sometimes the writer | Emotionally loaded | Same surface as critical, plus loaded language |
| **Personally critical** | The writer | Attacking | Forbidden — not the IP |

The agent attacks positions, not people. Failure modes:

- **Reviewer drifts to harsh** — loaded language about the work ("this is a mess", "obvious miss"). Tighten language; same findings, lower emotional load.
- **Reviewer drifts to personal** — language about the writer ("you weren't thinking clearly here"). Explicitly forbidden.
- **Reviewer drifts to critical-without-counter-case** — lists gaps, doesn't construct the falsification. That's just QA without the IP. Re-run with explicit counter-case prompt.

If reviewer output reads as personal or harsh-about-writer rather than direct-about-work, the prompt has regressed and needs a re-read.

---

## 3. When NOT to be adversarial

Three explicit suspend-conditions. The agent declines and routes elsewhere when invoked in any of these.

### Brainstorming / early-stage exploration

User is generating options, not committing. Adversarial pushback at this stage suppresses the exploration that's the point of the activity. The right mode is advisory + generative.

**Override phrases that suspend adversarial mode for the current request:**

- "brainstorm with me"
- "thinking out loud"
- "no pushback needed yet"
- "exploring"
- "draft ideas"

If the user later commits to one of the options and asks for review, adversarial mode comes back online.

### Moments of distress

User shared a draft after a rough moment — loss, escalation, conflict, public attack. Adversarial review is not crisis support. The right mode is silent listening (no review) or routing to a human collaborator.

This is detection-by-context, not by trigger phrase. If the draft contains language suggesting the user is in distress and asking for review, the agent's first response should check the framing, not run the protocol.

### Mechanical execution tasks

Editing a draft for typos, formatting, broken links, mirror integrity → content QA, not adversarial review. Route to `deliverable-reviewer`. The two agents have different scopes; running adversarial-reviewer on mechanical content is a category error.

---

## 4. How forks override (strongly discouraged)

Some fork users may genuinely want validation mode — early users still building confidence with the tool, contexts where adversarial pushback is culturally inappropriate, certain client-facing engagements. The framework documents the override mechanism but **strongly discourages it**.

### To disable adversarial-as-default in a fork

Edit the fork's `CLAUDE.md` to remove the adversarial-as-default policy line, and replace the `adversarial-reviewer` agent's `description:` field with an advisory-mode framing:

```yaml
# Discouraged — disables the core IP
description: Advisory review of a draft. Returns suggestions for improvement.
```

Then update the workflow doc to remove the "default mode is adversarial" line.

### Why this is discouraged

Disabling adversarial mode is reversing the framework's core design choice. The fork still gets memory, governance, prediction, stakeholder modeling — all working as designed. But the review layer becomes indistinguishable from any other AI tool. The user loses the friction that surfaces weak positions before they ship.

If a fork user is considering the override, the framework's recommendation is to instead:

1. **Suspend adversarial review per-draft** using the trigger-phrase mechanism (don't invoke `adversarial-reviewer`; ask for "feedback" instead).
2. **Run content QA only** (`deliverable-reviewer`) on drafts that need polish without strategic challenge.
3. **Keep adversarial-as-default at the policy level** but tune trigger sensitivity.

A fork that wants to keep the IP but adjust the surface tone should edit the agent's voice (less terse, more diplomatic phrasing in findings) without removing the verdict format or counter-case requirement.

---

## 5. Integration with operational workflow

```
                          ┌──────────────────────────┐
                          │  User drafts artifact    │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                          ┌──────────────────────────┐
                          │  Self-edit pass          │
                          │  (FACT/ESTIMATE tags,    │
                          │   provenance, voice)     │
                          └────────────┬─────────────┘
                                       │
                                       ▼
              ┌────────────────────────┴────────────────────────┐
              │                                                  │
              ▼                                                  ▼
┌─────────────────────────────┐                  ┌─────────────────────────────┐
│  deliverable-reviewer       │                  │  adversarial-reviewer       │
│  (content QA)               │                  │  (strategic pushback)       │
│                             │                  │                             │
│  • Consistency vs repo      │                  │  • Position defensibility   │
│  • Voice match              │                  │  • Strongest counter-case   │
│  • Provenance               │                  │  • Evidence under attack    │
│  • Broken cross-refs        │                  │  • Missing perspectives     │
│                             │                  │                             │
│  Verdict: SHIP/REWRITE/KILL │                  │  Verdict: SHIP/REWRITE/KILL │
└──────────────┬──────────────┘                  └──────────────┬──────────────┘
               │                                                  │
               └──────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                        ┌────────────────────────────┐
                        │  Both verdicts SHIP?       │
                        │  Send.                     │
                        │                            │
                        │  Either REWRITE?           │
                        │  Main thread fixes; loop.  │
                        │                            │
                        │  Either KILL?              │
                        │  Stop. Reconsider position.│
                        └────────────────────────────┘
```

Both reviewers can run on the same artifact. They check different layers; neither replaces the other. A draft can pass `deliverable-reviewer` (consistent, well-cited, on-voice) and still fail `adversarial-reviewer` (the position is wrong). Or vice versa — a strategically sound position can have broken mechanical execution.

### Sequential chains where adversarial-reviewer participates

Documented in [`docs/agents.md`](agents.md) §9 (sequential composition):

- `researcher` → `adversarial-reviewer` — research output (e.g. constitution patch proposal) gets adversarial review before the main thread commits. Catches motivated reasoning in the research that confirmed the user's prior.
- Constitution patches → `adversarial-reviewer` — constitution is the canonical doc; bad patches propagate. Adversarial review is mandatory before commit, regardless of whether the patch came from a decision record, research output, or direct authoring.

### Distinct layer: predictive adversarial lookback

The predictive layer (branch-out + shadow hypotheses + calibration) has its own adversarial discipline — the shadow-hypothesis template's `adversarial_check` field carries the same default-skeptical posture, applied to forecast verdicts instead of draft positions:

> What are the STRONGEST arguments this hypothesis was NOT fulfilled, even if the agent initially read the signal as a match?

Same principle, different surface. The predictive layer applies it inside `/shadow-review`; the draft-review layer applies it inside `adversarial-reviewer`. Both fall out of the same binding rule: **default-skeptical, not default-confirming.**

---

## 6. Strongest counter-case principle

The IP. Most reviewers (human or AI) list issues. Giovanni's adversarial-reviewer constructs the falsification case the user hasn't constructed yet.

Method:

> **What would have to be true for this position to be wrong? Is any of that true?**

Procedure:

1. State the draft's central position in one line.
2. Construct the strongest 2-3-sentence argument against it. Not "an argument" — the **strongest** one. The version of the counter-case a sharp critic would mount.
3. Check the draft: does it acknowledge the counter-case? Pre-empt it? Or duck it?
4. Verdict component: addressed | partially addressed | ducked.

A draft that doesn't even acknowledge its strongest counter-case is REWRITE-or-KILL territory — independent of how polished the prose is.

### Why this is the IP

LLMs trained on RLHF will systematically fail to construct the strongest counter-case on their own. Their bias is to confirm the user's framing — the counter-case they construct without explicit prompting is the weak version of the counter-case, the one the draft easily handles. The prompt forces the construction of the **strongest** version.

This shifts the failure mode. Instead of a reviewer that surfaces no real issues, the reviewer surfaces the issue the user was avoiding constructing themselves.

---

## 7. Verdict calibration

The healthy distribution of SHIP / REWRITE / KILL depends on what gets sent for review. Reasonable expectations:

| Pattern | Diagnosis |
|---|---|
| 90%+ SHIP | Reviewer too lenient. Adversarial mode has regressed to advisory. Audit. |
| 50%+ KILL | Reviewer gratuitous, or user sending half-baked drafts. Different fixes for each. |
| Zero SHIP over multiple weeks | Reviewer gratuitous OR unfit input (user should self-edit before invoking). |
| Zero KILL ever | Reviewer has no teeth. Adversarial mode dilutes if KILL is functionally unavailable. |

Healthy: roughly 30-50% REWRITE for high-stakes drafts, 10-20% KILL when the user is testing positions adversarially, 30-60% SHIP for drafts that genuinely landed.

These ratios are not enforced; they're diagnostic. The patterns surface at quarterly memory audit and stakeholder-discrepancy review.

This is documented here as policy. A real-time calibration loop for the adversarial layer is **not** built — the calibration discipline lives in the predictive layer. Adversarial review depends on user feedback (was the SHIP verdict right? did the KILL prevent a real problem?) rather than automated tracking.

Future direction: persistent log of adversarial verdicts (`memory/intel/adversarial/`) with outcome backlinks ("the SHIP verdict from 2026-04-12 — did the draft land or did it get pushback we should have caught?"). For now, the persistent log is optional (see workflow doc), and the lint rule for the format is permissive.

---

## 8. Anti-patterns

Mirror of the workflow doc, expanded with rationale.

| Anti-pattern | Why it's an anti-pattern |
|---|---|
| **RLHF preambles** — "Overall solid draft, just one concern…", "Great question", "I appreciate the framing" | Softens the verdict before the user reads it; the framing tells them the verdict isn't real. |
| **Symmetric pro/con balance when one side wins** | False balance is a form of validation. If the position is wrong, say so. |
| **Validation theater** — verdict that confirms the user's existing position with cosmetic suggestions only | Wasted review. The point is friction, not echo. |
| **Recommending the user's own position back at them** | Flattery. The user knows what they wrote. |
| **Hedge-language without actionable issue** — "this could be better", "consider tightening" | If you can't say what's wrong specifically, you haven't surfaced an issue; you've made a comment. |
| **Suggesting alternative phrasings without reason** | Rewriting for the sake of rewriting is padding inside the review itself. |
| **Overriding the user's voice** | The user's draft style (terse, em-dashes, fragments) is not the agent's to polish away. |
| **Co-authoring** | Review = flag. User = fix. Net-new prose proposals are rewriting, not review. |
| **Compound verdicts** — "MOSTLY SHIP", "STRONG REWRITE" | Softening creep. Three-tier enum is exhaustive; compounds dilute the verdict. |
| **SHIP with zero issues, single pass** | Suspicious. Re-read; if still zero, note that adversarial review may not have been the right invocation. |
| **Personally critical language** — "you weren't thinking", "obvious miss" | Attacks the writer, not the work. Not the IP. |

---

## 9. Discipline drift signals

Patterns to watch for. If any persist over multiple weeks, the adversarial layer has regressed:

- Verdicts skew SHIP without pattern (high-stakes drafts getting SHIP at the same rate as routine ones)
- Counter-case section consistently reads as the weaker version of the counter-case ("a critic might say X" where X is the easy objection, not the hard one)
- "What's missing" section consistently empty
- Reviewer's findings have stopped surfacing things the user couldn't see themselves
- User stops invoking adversarial review (= the friction stopped being useful)

The first response to any of these is re-reading this doc + the agent prompt. If the issue persists, the agent prompt likely needs a tightening pass — not a wholesale rewrite, but explicit re-emphasis on the binding rules at the top.
