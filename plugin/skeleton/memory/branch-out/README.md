# memory/branch-out/ — predictive simulation artifacts

This directory holds **active predictive simulations** (`/branch-out` outputs). Each artifact is a structured trade-off matrix for a high-stakes decision: who the actors are, what moves the principal could make, how each actor would plausibly respond at three confidence tiers, and the consequence dimensions of each move.

Branch-outs are the visible half of the predictive layer. The invisible half — **shadow hypotheses** — lives in `memory/shadow/`. Calibration scoring of both lives in `memory/calibration/`.

---

## What's here

| File / pattern | Purpose |
|---|---|
| `canonical-moves.md` | Registry of canonical move names. Reuse > coin. Lint-adjacent. |
| `README.md` | This file. |
| `<YYYY-MM-DD>-<situation-slug>.md` | Individual branch-out simulations. |
| `_archived/<YYYY-MM-DD>-<situation-slug>.md` | Closed branch-outs retained for calibration after 90 days. |

The template for new branch-outs is at `memory/templates/branch-out.template.md`.

---

## Lifecycle

```
status: draft           → simulation generated
status: active          → decision pending, simulation referenced
status: closed-resolved → decision made, outcome known
status: closed-overtaken-by-events → situation changed, simulation no longer applies
                                     (still retained for calibration)
```

A branch-out is **never deleted**. Closed artifacts are retained because they feed the calibration loop — months later you can re-read the predictions and check what actually happened.

After **90 days in closed status**, the artifact moves to `memory/branch-out/_archived/`. The MAP regen treats archived as a separate section.

---

## Binding rules (carry these — they're the IP)

These rules are repeated here verbatim from `docs/prediction.md` and the constitution. They are the IP moat. **Do not relax them in your fork.**

1. **No percentages.** Three tiers only: `likely` / `possible-but-surprising` / `unlikely-but-impactful`. Numeric probabilities create false precision. The branch-out template enforces this in cell structure; `scripts/lint_rules/no_percentages_in_predictions.py` enforces it programmatically.

2. **Max horizon t+2.** One user move + one actor response (t+1), optionally with a knock-on counter-move (t+2). Anything beyond t+2 is a human strategy session, not agentic prediction.

3. **Hard stop on shallow actors.** If 2+ key actors in the scenario have `profile_depth: shallow` or no profile, `/branch-out` STOPS. No caveat-degraded output. The fix is to deepen profiles first.

4. **No "recommended move".** Trade-off matrix has five fixed dimensions (`optionality`, `speed`, `leverage`, `trust`, `reversibility`) and no recommendation column. The agent surfaces consequence space; the principal decides. `scripts/lint_rules/branch_out_no_recommendation.py` catches recommendation creep.

5. **Canonical names from registry.** Every move name in a branch-out artifact draws from `canonical-moves.md`. Reuse > coin. New names only via decision record + user confirm. Lexical drift destroys calibration.

6. **Shadow hypotheses invisible at generation.** Hypotheses dropped during the `/branch-out` workflow land in `memory/shadow/pending/` and are NOT surfaced to the principal at generation time. Self-fulfilling / self-preventing prophecy is the failure mode the invisibility rule prevents.

7. **Adversarial lookback at /shadow-review.** Default prompt is skeptical: "what are the STRONGEST arguments this hypothesis was NOT fulfilled?" Counterweights LLM overconfidence.

8. **Decision records draft only.** `/branch-out` writes a draft decision record (`memory/decisions/<date>-<slug>.md`) with empty `chosen_move`, `reasoning`, `trigger_conditions`. Agent NEVER commits. Principal fills + commits.

---

## How a branch-out gets created

1. Principal runs `/branch-out <situation-slug>` referencing today's digest item.
2. Agent loads:
   - `memory/triage-heuristic.yaml`
   - `canonical-moves.md`
   - Each key actor's `memory/stakeholders/<slug>.md`
   - Source signals cited in the digest
3. Agent runs **actor confidence check** — if 2+ shallow / missing → HARD STOP.
4. Agent generates moves (3-5) using canonical names.
5. Agent predicts t+1 (and t+2 if horizon: t+2) actor responses per move per actor.
6. Agent writes trade-off matrix.
7. Agent drops shadow hypotheses **invisibly** into `memory/shadow/pending/`.
8. Agent writes draft decision record to `memory/decisions/<date>-<slug>.md`.
9. Principal fills decision record + commits separately.

The full `/branch-out` command spec lives at `.claude/commands/branch-out.md`.

---

## How to read a branch-out

The output is structured for **decision support, not consumption**. Read in this order:

1. **Situation** + **Decision at stake** — orient yourself
2. **Actors involved** — verify the profile-depth gate (no shallow / missing)
3. **Predicted actor responses table** — the prediction surface
4. **Trade-off matrix** — the consequence surface
5. **Watch points** — what to monitor between now and decision moment
6. **Key question to ask yourself** — what the matrix can't decide for you

**Skip the "Confidence note" section only if you're already familiar with the actors.** Otherwise read it first — it's the agent's accountability for what it modeled.

---

## Anti-patterns to recognize

If you see any of these in a branch-out artifact, the artifact is **broken**:

- A `Recommended` column anywhere in any matrix
- Any percentage anywhere (`70%`, `~85% confidence`, etc.)
- A prediction citing an actor not in the "Actors involved" list
- An "Agent suggests..." paragraph at the bottom
- t+3 predictions in any form ("if X happens, then Y, then Z, then ...")
- Move names that don't appear in `canonical-moves.md` without a corresponding decision record adding them
- Shadow hypotheses mentioned in the artifact body (they should be invisible)

---

## Cross-references

- **Template:** `memory/templates/branch-out.template.md`
- **Canonical moves registry:** `memory/branch-out/canonical-moves.md`
- **Triage heuristic:** `memory/triage-heuristic.yaml`
- **Shadow hypotheses:** `memory/shadow/README.md`
- **Calibration scoring:** `memory/calibration/README.md`
- **Slash command spec:** `.claude/commands/branch-out.md`
- **Full predictive-layer documentation:** `docs/prediction.md`
- **Constitution governance section:** `knowledge/<constitution-file>.md` § "Predictive layer governance"
