# memory/shadow/ — invisible predictive hypotheses

This directory holds **shadow hypotheses** — testable predictions about specific actor behavior within bounded time windows. Shadow hypotheses are the **invisible half of the predictive layer**: they are NEVER surfaced to the principal at generation time. They exist only to be tested against ground truth at horizon and to feed calibration scoring.

The visible half — `/branch-out` simulations — lives in `memory/branch-out/`.

---

## What's here

```
memory/shadow/
├── README.md                          ← this file
├── pending/                           ← currently active hypotheses
│   └── <YYYY-MM-DD>-<actor>-<topic>-<4char-hash>.yaml
├── resolved/
│   └── <YYYY-MM>/                     ← resolved within that month
│       └── <YYYY-MM-DD>-<actor>-<topic>-<4char-hash>.yaml
└── expired/
    └── <YYYY-MM>/                     ← past horizon, no verdict possible
        └── <YYYY-MM-DD>-<actor>-<topic>-<4char-hash>.yaml
```

Template for new hypotheses: `memory/templates/shadow-hypothesis.template.md`.

---

## Invisibility rule (BINDING — the IP)

**SHADOW HYPOTHESES ARE NEVER SHOWN TO THE PRINCIPAL AT GENERATION TIME.**

Surfacing a prediction to the actor or principal during the prediction window self-fulfills or self-prevents it (Heisenberg / observer effect). The whole point of the shadow layer is to track what would have happened **without** the prediction influencing behavior. The principal must NOT know "the agent predicted Karim will request a pricing concession" before the 2026-05-27 call, because the principal would then walk into that call preempting the concession or testing for it — corrupting the experiment.

### Visibility lifecycle

| Stage | Visibility |
|-------|------------|
| Generated (status: pending) | Invisible — stored in `pending/`, never quoted in digests / 1:1 prep / drafts |
| Horizon date reached | Invisible — lint rule `shadow-expired-pending` flags overdue resolution |
| `/shadow-review` cycle | Visible — surfaced for batch adversarial lookback |
| Post-review (status: resolved-*) | Visible — but typically only consulted at /calibration-report |

A hypothesis the principal sees during the prediction window is **no longer a shadow hypothesis**. It's an active prediction. Move it to `/branch-out` or delete it; do not keep it in `shadow/pending/`.

---

## Lifecycle

```
pending/ (status: pending)
   │
   │  horizon_at reached
   │
   ├──► /shadow-review verdict = matched  → resolved/<YYYY-MM>/ (status: resolved-yes)
   ├──► /shadow-review verdict = falsified → resolved/<YYYY-MM>/ (status: resolved-no)
   ├──► /shadow-review verdict = partial  → resolved/<YYYY-MM>/ (status: resolved-mixed)
   └──► no human verdict by horizon+30d  → expired/<YYYY-MM>/ (status: expired)
```

### File movement

Hypotheses MOVE between subdirectories on status change. Filenames stay stable.

```bash
git mv memory/shadow/pending/<id>.yaml memory/shadow/resolved/<YYYY-MM>/<id>.yaml
```

Movement is **human-initiated** — either at `/shadow-review` or via the post-horizon expiration sweep. No auto-promotion. The user decides verdicts; the agent assists with the adversarial-check structure.

---

## Adversarial lookback (BINDING)

At `/shadow-review` cycle, each pending-past-horizon and resolved hypothesis is reviewed with an **adversarial prompt**:

> What are the STRONGEST arguments this hypothesis was NOT fulfilled, even if the agent initially read the signal as a match?

This is **default-skeptical**, not default-confirming. The agent must construct the falsification case before being allowed to record a verdict of "matched". If the falsification case is weak, the verdict can be matched. If the falsification case has merit, verdict = falsified.

Default rule on uncertainty: **falsified**. Generosity in verdict equals motivated reasoning equals calibration corruption.

The `adversarial_check` field in each hypothesis YAML is where this reasoning gets recorded. **Empty `adversarial_check` field at resolution time = governance breach.**

---

## Specificity gate

Vague hypotheses do not get generated. The `specificity_gate` in `memory/triage-heuristic.yaml` requires:

- `expected_signal.search_terms_min`: at least 2 search terms
- `expected_signal.source_channels_min`: at least 1 channel
- `prediction_one_sentence_specific`: prediction must be a single specific testable claim

If a candidate hypothesis fails any of these, it is **rejected at generation time**, not stored as a vague hypothesis. The /calibration-report tracks specificity_gate rejection counts as a discipline health signal.

---

## What CAN trigger a shadow hypothesis

A shadow hypothesis SHOULD be generated when:

1. The actor has a profile in `memory/stakeholders/` with `profile_depth: partial` or deeper
2. There is a specific testable expected signal
3. The horizon is within 1-14 days
4. The hypothesis would NOT change behavior if the principal knew it at generation time

Common generation triggers:

- A `/branch-out` simulation surfaces predicted moves that are testable within the horizon window
- The daily digest surfaces a passive signal where actor follow-up is predictable
- A 1:1 brief surfaces an expected actor follow-up the principal won't actively pursue

## What CANNOT trigger a shadow hypothesis

- Actor has `profile_depth: shallow` or no profile (noise)
- The prediction is vague enough that "matched / falsified" is a coin flip
- Outcome is already determined by external constraint (contract date, calendar event, decided plan)
- Horizon would exceed 14 days
- The principal would change behavior if told the prediction (it belongs in `/branch-out`, not shadow)

---

## Retention

Shadow hypotheses are **never deleted**. They feed calibration in perpetuity. After 12 months in resolved/ or expired/, hypotheses may be moved to an `_archived/` subdirectory if MAP regen performance becomes an issue. None are deleted — the lineage of the prediction loop is the IP.

---

## Cross-references

- **Template:** `memory/templates/shadow-hypothesis.template.md`
- **Triage heuristic (specificity_gate):** `memory/triage-heuristic.yaml`
- **Calibration aggregation:** `memory/calibration/README.md`
- **/shadow-review slash command:** `.claude/commands/shadow-review.md`
- **/calibration-report slash command:** `.claude/commands/calibration-report.md`
- **Full predictive-layer documentation:** `docs/prediction.md`
- **Branch-out artifacts that spawn shadows:** `memory/branch-out/`
- **Constitution governance section:** `knowledge/<constitution-file>.md` § "Predictive layer governance"

---

## Anti-patterns

If you see any of these in operation, the discipline has broken:

- A shadow hypothesis quoted in `/branch-out` output (invisibility violated)
- A shadow hypothesis mentioned in a 1:1 brief (invisibility violated)
- The principal "checking in" on what the agent predicted before horizon (invisibility violated by the principal — agent should refuse)
- `adversarial_check` field left empty at resolution time (governance breach)
- Hypotheses with `prediction_tier: likely` hitting >85% (sandbagging — agent is only making safe bets to inflate accuracy)
- Hypotheses with `prediction_tier: likely` hitting <40% (over-confidence on top tier — recalibrate)
- Expired-without-verdict rate climbing month over month (specificity gate too loose)
- Hypothesis file in `pending/` past horizon_at by > 30 days (lint will flag — overdue review)
