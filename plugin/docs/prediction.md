# Giovanni Predictive Layer — branch-out, shadow, calibration

The predictive layer is **Giovanni's strongest IP moat**. Per market scan, no competitor or platform vendor — alfred_, Lindy, Bond, Murchison-style PE templates, or anything Google or Anthropic will ship in the next 24 months — bundles all four of these in one framework:

1. **Per-stakeholder predictive simulation** with explicit three-tier no-percentages framing
2. **Hard-stop discipline on shallow actors** (no caveat-degraded predictions)
3. **Invisible shadow hypotheses** with anti-self-fulfilling design
4. **Per-actor calibration scoring** with adversarial lookback discipline

This document is the binding rationale for the layer. The schemas live in their respective templates and READMEs. This doc explains **why the system is shaped this way** and how the components chain.

---

## Why prediction matters

Operational decision quality degrades into vibes without a structure. The principal of an initiative makes dozens of decisions per week that depend on predicted counterparty behavior — will the board director push for a comp committee meeting if VP Eng confidence drops? Will the customer signal evaluation of alternatives in the renewal call? Will the co-founder accept a scope cut or push back?

In the absence of structure, those predictions get made implicitly, anchored on the most recent emotional reading, and never tested against outcome. The result is systematic over-confidence on `likely` calls, under-prediction of adversarial moves, and a steady drift away from operational reality.

The predictive layer makes the structure explicit:

- **Branch-out** lays out the trade-off space before commitment — three tiers per actor per move, no recommendation creep.
- **Shadow hypotheses** track predictions the principal doesn't see, so the predictions don't self-fulfill or self-prevent.
- **Calibration** measures how often each tier hits, per actor, over time — surfacing biases.
- **Adversarial lookback** counterweights LLM overconfidence in verdict-recording.

All four together create a feedback loop: predict → observe → verdict → calibrate → re-derive predictions. The loop is what makes the layer honest over time.

---

## Three-tier framing rationale

**Why no percentages.**

Numeric probabilities create false precision in small-N stakeholder predictions. When the agent says "70% likely Karim will request a pricing concession", the number is implicit hallucination — there is no calibrated base rate, no underlying frequency the 70 corresponds to. The number reads as confidence; it is in fact vibes with arithmetic decoration.

Three tiers force the prediction into honest categories:

| Tier | What it means | Healthy hit rate |
|------|---------------|------------------|
| `likely` | Pattern matches against the actor's observed history. Default expectation. | 60-80% |
| `possible-but-surprising` | Plausible but non-default behavior. Would not be the first prediction. | 20-40% |
| `unlikely-but-impactful` | Low probability, high consequence if it happens. Worth modeling for option value. | 5-15% |

The healthy ranges are themselves the IP. If `likely` predictions hit at 95%, the agent is sandbagging (only making bets it knows it can win). If `unlikely-but-impactful` predictions hit at 30%, the tier label is broken (these are not actually unlikely). The three-tier system is a **forecasting calibration tool**, not a guess-the-future tool.

**Enforcement.**

- The branch-out template structures predictions with explicit tier columns
- `scripts/lint_rules/no_percentages_in_predictions.py` programmatically catches percentage syntax in branch-out artifacts
- Stakeholder profile `Predicted reactions` section follows the same discipline

---

## Horizon discipline

**Why max t+2.**

`t+1` is one user move + one actor response. `t+2` is the immediate counter-move OR a knock-on by a second actor. Anything beyond — actor 1 responds, principal responds back, actor 2 reacts to the response — is **strategic chess, not agentic prediction**. The branching factor explodes past t+2, and the LLM's pattern-matching against historical behavior breaks down because t+3 outcomes depend on path-dependent context the model doesn't have.

The cap is binding. Branch-outs that try to model t+3 produce confident-sounding noise. If the principal wants to think through a longer chain, that's a human strategy session — possibly using the branch-out's t+2 output as anchor — but not a prediction the framework should generate.

**Enforcement.**

- Branch-out template frontmatter has `horizon: t+1 | t+2` (no t+3 option)
- The `/branch-out` workflow refuses to generate t+3 predictions

---

## Shallow-actor hard stop

**Why hard stop, not caveat-degraded output.**

When the agent tries to predict the behavior of an actor with no profile — or `profile_depth: shallow` (fewer than 5 observed touches) — it has nothing to pattern-match against. The prediction collapses to base-rate guessing wearing the costume of a confident structured output.

The temptation is to say "I can still generate predictions; I'll just caveat them." This is **the dangerous version**. The caveated output looks like a real prediction, gets relied upon, and corrupts both the decision and the calibration record.

Hard stop means: if 2+ key actors are shallow / missing, **/branch-out STOPS**. The output is:

```
⚠️ Insufficient actor models for branch-out.

Shallow/missing actors:
- <actor-1>: <reason>
- <actor-2>: <reason>

Recommended next step: bootstrap profile via stakeholder-profiler agent
or accept that this simulation cannot run.

Branch-out not executed.
```

No degraded prediction. No "best effort". The fix is to deepen profiles first.

**Enforcement.**

- The `/branch-out` command spec includes the hard-stop logic
- The branch-out template lists actor `profile_depth` requirements in the schema

---

## No-recommendation principle

**Why trade-off matrix, not prescription.**

The agent's role ends at **surfacing consequence space**. The principal weighs the dimensions (`optionality`, `speed`, `leverage`, `trust`, `reversibility`) against context the agent cannot see — political weight, gut judgment, prior commitments, long-running relationship history, the unwritten rules of how the organization operates.

If the agent recommends a move, two failure modes follow:

1. **The principal accepts the recommendation and loses agency.** The framework becomes an oracle; the decision becomes a rubber stamp; relationship context the agent doesn't have gets steamrolled.
2. **The principal rejects the recommendation and starts arguing with the matrix instead of using it.** The matrix's value as a trade-off lens degrades because every cell becomes a debate against the recommendation.

Recommendation creep is the failure mode. The template explicitly omits a "Recommended" column and includes a "No recommended move" callout that names the absence as intentional.

**Enforcement.**

- Branch-out template excludes any "Recommended" column from the trade-off matrix
- `scripts/lint_rules/branch_out_no_recommendation.py` catches recommendation prose patterns ("we recommend", "the agent suggests", "best move is", "should do")

---

## Shadow invisibility rule

**Why hide shadow hypotheses from the principal at generation time.**

A prediction surfaced to the principal during the prediction window does one of two things:

- **Self-fulfills.** "The agent predicted Karim will request a pricing concession" — now the principal walks into the call testing for the concession, framing the conversation around it, and the concession becomes more likely because the principal made room for it.
- **Self-prevents.** "The agent predicted Sarah will push for a comp committee meeting" — now the principal pre-empts by surfacing the issue first, and Sarah never has to push, so the prediction can't be tested.

Either way, the prediction loop is broken. The agent's track record becomes a record of how its surfaced predictions changed behavior, not a record of how accurate its predictions are.

The fix is to **NEVER show shadow hypotheses to the principal at generation time**. They live in `memory/shadow/pending/`. They are not quoted in digests. They are not mentioned in 1:1 briefs. They are not surfaced in branch-out output. They become visible only at `/shadow-review`, after the horizon date has passed and the outcome is structurally determined.

This is the **anti-self-fulfilling prophecy** rule. It is the single most important binding constraint in the entire framework, and it is the constraint most likely to be relaxed by well-meaning users who think "the principal should know what the agent thinks". They should not — at least not in the prediction window.

**Enforcement.**

- The shadow hypothesis template includes the invisibility rule as a binding inline comment
- The /branch-out workflow stores shadow hypotheses to `memory/shadow/pending/` but does not include them in the output
- Documentation, agent definitions, and constitution all reiterate the rule

---

## Adversarial lookback

**Why default-skeptical when matching outcomes.**

When `/shadow-review` resolves a pending hypothesis, the agent could read the signal generously ("close enough to match") or strictly ("technically the signal didn't match the prediction"). Default-generous reads inflate accuracy artificially, corrupt calibration, and over time create a confident system that is in fact poorly calibrated.

The adversarial lookback prompt is binding:

> What are the STRONGEST arguments this hypothesis was NOT fulfilled, even if the agent initially read the signal as a match?

The agent constructs the falsification case before being allowed to record "matched". If the falsification case is weak, matched stands. If it has merit, the verdict flips to falsified. **Default rule on uncertainty: falsified.** Generosity in verdict equals motivated reasoning equals calibration corruption.

This is uncomfortable. The framework deliberately runs the agent's predictions against an adversarial reviewer (the agent itself, primed adversarially). High-accuracy months should be celebrated less than they are scrutinized — `overall_accuracy > 80%` triggers an immediate `/shadow-review` because it usually means tier labels have drifted or verdicts are motivated.

**Enforcement.**

- The shadow hypothesis template includes the adversarial-check prompt verbatim
- `/shadow-review` workflow spec includes the default-skeptical framing
- `/calibration-report` template includes the >80% accuracy guard rail

---

## Calibration discipline

**Why per-actor monthly aggregation.**

Calibration is meaningless at the framework level. The agent's accuracy averaged across all actors hides the patterns that matter — that it predicts `likely` well for board-level interactions but badly for customer-renewal moves, or that one specific actor's behavior is systematically inverted in the agent's predictions.

Per-actor aggregation, per-tier, surfaces these patterns:

- **`likely` hit rate per actor** — is the agent's pattern-match against this actor's history working?
- **`possible-but-surprising` hit rate per actor** — is the agent labeling non-default moves correctly?
- **`unlikely-but-impactful` hit rate per actor** — is the rare-but-consequential tier label accurate?

The monthly /calibration-report aggregates these, identifies bias-watch flags, and surfaces threshold suggestions for the triage heuristic. The agent **surfaces**; the principal **applies**.

**Enforcement.**

- `memory/calibration/actor-scores.yaml` is the canonical state — schema enforces per-tier breakdown
- `/calibration-report` workflow updates the YAML and writes monthly markdown report
- Healthy ranges (60-80% likely, 20-40% possible-but-surprising, 5-15% unlikely-but-impactful) are documented in the calibration README and the monthly report template

---

## Canonical-moves reuse

**Why lexical discipline matters.**

If the same actor behavior gets logged as `escalate-up` in one branch-out, `kick-upstairs` in the next, and `route-to-boss` in a third, calibration breaks. You cannot measure "how often does `escalate-up` hit when predicted" when the label keeps shifting.

The canonical-moves registry (`memory/branch-out/canonical-moves.md`) is the **join key between predictions and resolved outcomes**. Reuse > coin. New names enter only via decision record with explicit user confirmation. Lint can warn on unregistered names, but the rule is fundamentally about discipline, not enforcement.

The registry includes 50+ moves across 6 relationship types (asymmetric-power-up, peer, asymmetric-power-down, customer, vendor, counterparty) plus cross-relationship general moves. The taxonomy is observation-derived: these are moves observed across multiple domains, not abstract categories.

**Enforcement.**

- `memory/branch-out/canonical-moves.md` is append-only — new names only via decision record
- `/branch-out` workflow loads the registry and reuses existing names

---

## Workflow chains

The four components chain into one prediction loop:

```
1. /branch-out <slug>
     ├─ loads stakeholder profiles + canonical moves
     ├─ runs actor depth check → STOP if 2+ shallow
     ├─ generates moves (canonical names) → predictions (3-tier) → trade-off matrix
     ├─ writes draft decision record (empty chosen_move, reasoning, trigger_conditions)
     ├─ drops invisible shadow hypotheses to memory/shadow/pending/
     └─ output: branch-out artifact + decision record draft

2. Principal makes decision → fills decision record → commits

3. [silently] Days pass; horizon dates arrive

4. /shadow-review (quarterly)
     ├─ pulls 10-20 resolved + past-horizon hypotheses
     ├─ runs adversarial lookback per hypothesis → verdict (matched/falsified/mixed/expired)
     ├─ moves files: pending → resolved/<YYYY-MM>/ or expired/<YYYY-MM>/
     ├─ appends to memory/calibration/audit-log.md (does NOT touch actor-scores.yaml)
     └─ output: shadow review audit log

5. /calibration-report (monthly)
     ├─ aggregates the month's resolved hypotheses
     ├─ computes per-actor + per-tier accuracy
     ├─ updates memory/calibration/actor-scores.yaml (sole writer of the YAML)
     ├─ identifies bias patterns + threshold suggestions
     ├─ writes monthly report to memory/calibration/monthly/<YYYY-MM>.md
     └─ output: monthly calibration report

6. Bias patterns surface → principal applies fixes manually
     ├─ Stakeholder profile updates (re-read sentiment trajectory, refine predicted reactions)
     ├─ Triage heuristic updates (tighten specificity_gate, adjust daily_max)
     └─ Canonical-moves registry updates (rare; only on consistent new pattern)
```

The loop is **manually-paced**. No auto-commits. No auto-threshold adjustments. The agent surfaces; the principal applies. This is the governance rule that prevents the calibration loop from drifting into a self-tuning hallucination engine.

---

## Anti-patterns

A summary of failure modes to recognize and refuse:

### Recommendation creep

Symptom: branch-out output adds a "Recommended" column to the trade-off matrix, or includes a paragraph saying "we recommend X" or "the best move is Y". 
Fix: refuse. Strip the recommendation. The matrix is generative, not prescriptive. The principal decides.

### False precision

Symptom: predictions written as `70% likely Karim will request concession` or `high confidence ~85%`. 
Fix: lint catches percentage syntax. Re-express as one of the three tiers (`likely`, `possible-but-surprising`, `unlikely-but-impactful`).

### Shadow leakage

Symptom: shadow hypothesis quoted in a branch-out output, mentioned in a 1:1 brief, or discussed with the principal before horizon. 
Fix: refuse. The principal should not know what the agent predicted in the shadow layer during the prediction window. If the principal asks "what did you predict for Karim?", the agent refuses to reveal pending shadows.

### Calibration manipulation

Symptom: adversarial-check verdicts consistently lean matched even when the signal was ambiguous; `overall_accuracy > 80%` without callout. 
Fix: trigger `/shadow-review` immediately. Re-evaluate verdicts adversarially. Default-skeptical, not default-confirming.

### Depth-shallow override

Symptom: branch-out runs despite 2+ shallow actors, with caveats appended. 
Fix: refuse. Hard stop is hard stop. Bootstrap profiles first or accept that the simulation cannot run. The caveats degrade output integrity worse than the absent simulation would.

### Triage threshold creep

Symptom: shadow daily_max keeps drifting upward each month to accommodate growing volume. 
Fix: refuse. Threshold values change only via deliberate review (and decision record). High volume signals an upstream problem (too-loose digest triage), not a need for higher caps.

### Trigger conditions empty

Symptom: decision records spawned by /branch-out have empty `trigger_conditions` field. 
Fix: `scripts/lint_rules/decision_trigger_conditions.py` catches this. Empty trigger conditions = decision theatre — no signal to revisit on. Principal must fill before commit.

### Tier-label drift

Symptom: `likely` predictions hit at <40% or `unlikely-but-impactful` predictions hit at >25%. 
Fix: the tiers are no longer testing what they should. Re-read actor profile, recalibrate tier criteria, or accept that the actor model is broken (re-bootstrap).

---

## Cross-references

- **Templates:**
  - `memory/templates/branch-out.template.md`
  - `memory/templates/shadow-hypothesis.template.md`
  - `memory/templates/calibration-actor-score.template.md`
  - `memory/templates/calibration-monthly-report.template.md`
- **Schemas:**
  - `memory/branch-out/canonical-moves.md`
  - `memory/calibration/actor-scores.template.yaml`
  - `memory/triage-heuristic.template.yaml`
- **READMEs:**
  - `memory/branch-out/README.md`
  - `memory/shadow/README.md`
  - `memory/calibration/README.md`
- **Slash commands:**
  - `.claude/commands/branch-out.md`
  - `.claude/commands/shadow-review.md`
  - `.claude/commands/calibration-report.md`
- **Lint rules:**
  - `scripts/lint_rules/no_percentages_in_predictions.py`
  - `scripts/lint_rules/shadow_expired_pending.py`
  - `scripts/lint_rules/branch_out_no_recommendation.py`
- **Constitution section:**
  - `knowledge/<constitution-file>.md` § "Predictive layer governance"
- **Examples:**
  - `memory/examples/branch-out.example.md`
  - `memory/examples/shadow-hypothesis.example.md`
  - `memory/examples/calibration-actor-score.example.yaml`
