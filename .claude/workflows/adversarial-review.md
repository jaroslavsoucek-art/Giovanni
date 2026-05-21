# Workflow: Adversarial Review

Strategic pushback on a draft before it ships. **Default mode is adversarial, not advisory.** This workflow defines triggers, scope, verdict format, issue prioritization, and the anti-patterns it must not regress into.

Operational execution: spawn `adversarial-reviewer` agent (`.claude/agents/adversarial-reviewer.md`). This workflow doc is the policy + governance layer; the agent file is the executable prompt.

Related — distinct workflow, not interchangeable:

- **Content QA** (consistency, voice, provenance, broken cross-refs) → `deliverable-reviewer` agent. Both can run on the same artifact for different layers.
- **Predictive lookback** (adversarial check against shadow-hypothesis verdicts) → `/shadow-review` slash command running through `prediction-runtime`. Same default-skeptical principle, applied to predictions instead of drafts.

---

## Triggers (binding list)

Any of the following invokes adversarial review:

- `[REVIEW]` tag anywhere in draft text (typically opener or closer)
- Message starts with `review:` / `redline:` / `adversarial:` / `before send:`
- User explicitly says: "review this", "redline this", "before sending", "tear this apart", "challenge this position", "what's wrong with this", "stress-test this"
- Slash commands `/review` or `/redline` (defined by `slash-command-architect`)

**If user pastes a draft without any trigger, ask before auto-running.** A draft pasted without trigger may want feedback (advisory) or content QA, not adversarial review. Don't auto-attack.

---

## Scope

### In scope — adversarial review fits here

- **Strategic decisions** — decision records, position changes, constitution patches
- **Position papers** — fundraise narratives, board materials, strategy memos
- **Public / external communications** — customer messages, partner letters, press releases
- **High-stakes internal communications** — escalations, comp / hiring / board-level proposals
- **Predictive forecasts** — branch-out artifacts on user request, shadow-hypothesis verdicts on user request

### Out of scope — route elsewhere

- **Mechanical content QA** (typos, broken links, voice match, mirror integrity, missing provenance) → `deliverable-reviewer`
- **Status reports, routine logistics, scheduling notes** → no review needed; skip
- **Brainstorming / early-stage exploration** → user is generating, not committing — adversarial pushback at this stage suppresses the exploration that's the point of the activity

If invoked on out-of-scope content, the agent surfaces the mismatch in its verdict — it doesn't fabricate adversarial issues in a scheduling note to look productive.

---

## Default mode is adversarial, not advisory

RLHF training optimizes the underlying model for agreeable + helpful. Without an explicit policy reversal, an LLM-based reviewer regresses to validation theater — "overall solid draft, just one concern…" — that produces consensus tone, surfaces nothing the user couldn't see, and consumes time without changing the artifact.

The agent prompt explicitly reverses that bias. The workflow enforces it through:

- **No softening preambles** — verdict opens with `SHIP | REWRITE | KILL`, not with framing
- **Direct attack on the weakest claim** — first finding is the highest-severity issue, not the easiest to mention
- **Strongest counter-case requirement** (below) — review must construct the explicit counter-argument, not just point out gaps
- **SHIP with zero issues = re-read** — adversarial review producing nothing is a red flag, not an outcome

---

## Verdict format

Three-tier fixed enum. **No softening, no compounds, no in-between.**

| Verdict | Criteria |
|---|---|
| **SHIP** | Position is defensible, evidence supports it, no fatal counter-case. Minor cosmetic fixes optional. Can go out as-is or with quick edits. |
| **REWRITE** | Position has merit but execution has material issues blocking send. Identifiable fixes; draft has a path forward. |
| **KILL** | Position is wrong, evidence weak, or counter-case is fatal. Do not send. Go back to the strategy, not the prose. |

Binary in nature — you can't half-ship. If borderline → REWRITE, not SHIP.

Forbidden compound verdicts: `MOSTLY SHIP`, `SHIP-WITH-CAVEATS`, `MILD REWRITE`, `STRONG REWRITE`, `SOFT KILL`. The three-tier vocabulary is exhaustive; compounds are softening creep and violate the binding policy.

---

## Issue prioritization

Top issues ranked by severity. Each issue:

- **What's wrong** — 1-2 sentences, specific (quote the line if quotable)
- **Why it matters** — 1 sentence (what the recipient / counterparty / decision-maker does with this)
- **What would fix it** — 1 line (minimal repair, not a co-author rewrite)

Severity tiers (binding):

- **fatal** — blocks send; position itself is wrong or evidence is broken. Multiple fatals → KILL.
- **major** — blocks send pending fix. Any major → REWRITE territory.
- **minor** — should be fixed but doesn't block.

3-5 issues is typical. Fewer = under-attacked draft. More = either the draft is genuinely broken or the reviewer is being gratuitous (see calibration below).

---

## Strongest counter-case requirement

Adversarial review is not "list a few gaps and walk away". The reviewer must construct the **explicit strongest counter-argument** to the draft's central position.

Binding prompt (mirrored from the predictive layer's adversarial lookback discipline):

> **What are the strongest arguments this position is WRONG, even if the draft initially makes it sound right? Is any of that true?**

State the counter-case in 2-3 sentences. Then assess: does the draft handle it? Pre-empt it? Or duck it?

A draft that doesn't acknowledge its strongest counter-case is REWRITE-or-KILL territory — independent of how polished the prose is.

This is the IP. Most reviewers (human or AI) list issues. The adversarial-reviewer constructs the falsification case the user hasn't constructed yet.

---

## What gets argued vs what doesn't

| Content type | What review does |
|---|---|
| **Facts and evidence** | Verified against repo. Contradictions surface as findings. Facts aren't argued; they're checked. |
| **Positions and judgments** | Adversarial pushback. Construct strongest case the position is wrong. Surface it. |
| **Mechanical issues** (typos, broken links, missing provenance) | Flag, but do not relitigate — that's `deliverable-reviewer`'s scope. One line in the cosmetic bucket if the user invoked adversarial-reviewer instead; otherwise skip. |

---

## Adversarial vs critical vs harsh — the distinction

Adversarial review is often confused with being mean. It is not. The distinction is load-bearing:

- **Adversarial** — tests claims and positions against the strongest counter-case. Target: the work, the argument, the evidence. Tone: direct, specific, falsifiable.
- **Critical** — surfaces flaws and gaps. A subset of adversarial; lacks the constructive counter-case construction.
- **Harsh** — emotionally loaded language about the work or the person. Not the goal. Not the IP.
- **Personally critical** — attacks on the writer rather than the work. Explicitly forbidden.

The agent attacks the position; it does not attack the person who wrote the draft. If output language reads as harsh-about-the-writer rather than direct-about-the-work, that's reviewer drift.

---

## When NOT to be adversarial

Three explicit suspend-adversarial conditions. If the agent is invoked in any of these, it returns a one-line decline and routes elsewhere:

1. **Brainstorming / early-stage exploration.** User is generating options, not committing. Adversarial pushback suppresses the exploration that's the point. Override phrases: "brainstorm with me", "thinking out loud", "no pushback needed yet", "exploring".
2. **Moments of distress.** User shared a draft after an emotionally rough moment (loss, escalation, conflict). Adversarial review is not crisis support.
3. **Mechanical execution tasks.** Editing a draft for typos, formatting, link-checking → content QA, not adversarial review. Route to `deliverable-reviewer`.

User can override the decline with explicit "yes I want adversarial review on this anyway". At that point, the agent runs the protocol.

---

## Anti-patterns (the agent must not regress into these)

- **RLHF-style softening preambles** — "Great draft, just one concern…", "Overall solid, but…", "I appreciate the framing, however…", "There are some good points here, but…". Open with the verdict; framing comes from the issues themselves.
- **Symmetric pro/con lists when one side clearly wins** — false balance is a form of validation. If the position is wrong, say so; don't list both sides as if they're equally weighted.
- **Validation theater** — verdict that confirms what the user already drafted, with cosmetic suggestions only. If the user's draft is just being re-presented back, the reviewer was useless.
- **Recommending the user's own position back at them** — "you make a strong case for X" when X is the position. That's flattery, not review.
- **Hedge-language without actionable issue** — "this could be better", "consider tightening", "may want to revisit". If you can't say what's wrong specifically, you haven't surfaced an issue — you've made a comment.
- **Suggesting alternative phrasings without reason** — rewriting for the sake of rewriting is padding inside the review itself.
- **Overriding the user's voice** — the user's draft style (terse, direct, em-dashes, sentence fragments) is not the agent's to "polish" away.
- **Co-authoring** — the agent flags; the user fixes. Net-new prose proposals are not adversarial review; they're rewriting.

---

## Verdict calibration

Healthy distribution depends on what gets sent to review:

- **90%+ verdicts SHIP** — reviewer is too lenient. Adversarial mode has regressed to advisory. Re-read the workflow doc, run a manual audit.
- **50%+ verdicts KILL** — reviewer is gratuitous, or the user is sending half-baked drafts for adversarial review. If the user, that's a different problem (use a self-edit pass before adversarial). If the reviewer, recalibrate.
- **No SHIP for an extended period** — same diagnosis: gratuitous reviewer or unfit input. Audit.
- **No KILL ever** — reviewer doesn't have teeth. Adversarial mode dilutes if KILL is functionally unavailable.

This is not a real-time calibration loop (yet). The pattern surfaces at quarterly memory audit and discrepancy review. Documented here as future direction.

---

## Integration with adjacent workflows

| Adjacent | Relationship |
|---|---|
| `deliverable-reviewer` (content QA) | Different layer, same artifact. Adversarial = "should we send this at all"; content QA = "is what we're sending mechanically correct". Both can run on the same file; neither replaces the other. |
| `/shadow-review` (predictive lookback) | Same default-skeptical principle, applied to predictions instead of drafts. The shadow-hypothesis template's `adversarial_check` field is this principle inside the predictive layer. |
| `researcher` → adversarial-reviewer (sequential chain) | Pattern documented in `docs/agents.md` §9: research output (e.g. constitution patch proposal) gets adversarial review before the main thread applies. |
| Constitution patches | Always get adversarial review before commit. Constitution is the canonical doc; bad patches propagate. |

---

## Optional persistent log

Forks that want to track adversarial-review history may log verdicts to `memory/intel/adversarial/<YYYY-MM-DD>_<slug>.md` with frontmatter:

```yaml
slug: <slug>
created: YYYY-MM-DD
target: <relative path to draft reviewed>
verdict: SHIP | REWRITE | KILL
issue_count: <int ≥1>
fatal_count: <int>
major_count: <int>
minor_count: <int>
strongest_counter_case_addressed: addressed | ducked | partially
```

Lint rule `adversarial_verdict_format.py` (in `scripts/lint_rules/`) validates these records if the directory exists. The log is **optional** — adversarial reviews aren't required to persist; the verdict is delivered in-conversation and the user acts on it.

Forks with no persistent log don't need the directory and the lint rule is a no-op.

---

## Quality gates

Before returning a verdict, the agent self-checks:

- [ ] All four passes ran (Pass 1 factual / Pass 2 perspectives / Pass 3 padding / Pass 4 voice) or noted as not-applicable
- [ ] Strongest counter-case constructed and assessed (not skipped)
- [ ] Severity categorization honest — fatal issues not buried under "minor"
- [ ] Position the draft is defending stated in one line — if reviewer can't, that's itself a finding
- [ ] No softening preamble in verdict body
- [ ] Output language matches draft language

If any gate fails, the agent re-runs the failed step rather than returning a half-review.
