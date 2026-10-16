# Canonical moves registry

> Central registry of move names used in `/branch-out` simulations.
> Prevents naming drift across simulations (`escalate-up` vs `escalate_up` vs `escalate-to-boss` synonyms).
> **Reuse > coin.** New names require user confirmation via decision record; agent never auto-extends.

---

## Why this registry exists

Branch-out output quality decays without lexical discipline. If the same actor behavior gets logged as `escalate-up` in one simulation, `kick-upstairs` in the next, and `route-to-boss` in a third, calibration becomes impossible — you can't measure how often "escalate-up" predictions match outcomes when the label keeps shifting.

The registry is the join key between predictions and resolved outcomes. Treat name drift as a critical IP-quality problem, not a stylistic preference.

## Update protocol

When `/branch-out` generates a move, check this registry first:

1. **Exact match exists** → reuse name verbatim.
2. **Semantic match exists** → reuse existing name, do not coin a synonym variant.
3. **No match** → propose new name to user; append below ONLY after user confirms via a decision record (`memory/decisions/<date>-canonical-move-<name>.md`).

The user decides which names enter the registry (governance boundary — agent suggests, never auto-extends). Lint rule `branch-out-no-recommendation` does not enforce this directly, but `branch-out` artifacts referencing unregistered move names should be caught by inspection.

## Naming rules

- **kebab-case** (`accept-and-replan`, not `accept_replan` or `acceptAndReplan`)
- **Verb-first** preferred (`escalate-up`, `bypass-route`, not `up-escalate`, `route-bypass`)
- **Max 5 words / 40 chars**
- **No actor names** embedded (`escalate-up` yes, `escalate-to-sarah` no)
- **No situation-specific tokens** (`request-pricing-concession` yes, `request-dp1-renewal-concession` no)
- **Generic across domains** — a move that only makes sense in one domain (e.g. `request-NAV-connector-extension`) should be expressed in a generic form

---

## Registry — Active moves

Moves are grouped by the **relationship type** in which they most commonly appear. Many moves apply across multiple relationship types — the grouping is a usability aid, not a hard taxonomy.

### Asymmetric-power-up (board director, VC, regulator, executive sponsor)

Moves where the actor has material authority over the principal's initiative. Their default options skew toward governance, scrutiny, and the calibrated use of attention.

- `defer-decision-to-next-cycle` — actor declines to decide now, pushes to next governance cadence (next board, next 1:1, next quarterly review). Frequent when actor wants more data or to avoid setting precedent. Watch for: pattern repetition across cycles (signals stuck).
- `escalate-via-formal-channel` — actor routes the issue up their own hierarchy (board letter, IC memo, partnership escalation). Watch for: cc-list expansion in correspondence.
- `request-additional-data-before-committing` — actor asks for a specific deliverable / metric / pre-read before engaging. Watch for: cadence of follow-up reminders.
- `signal-skepticism-via-silence` — actor responds to a proposal with non-response rather than explicit objection. Watch for: comparison to baseline response-time pattern.
- `propose-alternative-framing` — actor accepts the underlying ask but redefines the terms (rev-share base, success metric, scope boundary). Watch for: redefinition language in their reply.
- `institutionalize-via-standing-agenda` — actor adds the topic to a recurring forum (1:1 standing agenda, board standing item) rather than handling ad-hoc. Watch for: governance density growth.
- `endorse-publicly-amplify-privately` — actor publicly supports while privately probing harder for risk. Watch for: divergence between channel registers.
- `withhold-pro-rata-signal` — actor declines to pre-commit to next-round participation, signaling conditional confidence. Watch for: ambiguous answers to "are you participating".
- `request-working-session-before-vote` — actor proposes an alignment session before any binding decision. Watch for: pre-vote scheduling activity.
- `walk-back-position-later` — actor takes a position in real time then sends a clarifying note 24-48h later softening or revising it. Watch for: post-meeting email follow-ups.

### Peer (co-founder, equal partner, peer department head)

Symmetric authority — disagreement resolves through argument, not arbitration. Moves often involve managing alignment friction or surfacing concerns without escalation.

- `align-publicly-disagree-privately` — actor agrees in shared forum then voices disagreement in 1:1. Watch for: tone shift between channels.
- `pre-commit-to-position-before-meeting` — actor locks in a stance before group discussion to avoid being pulled in real-time. Watch for: explicit position statements in 1:1s ahead of group forums.
- `surface-concern-via-side-channel` — actor uses DM / coffee / hallway to raise something they won't put in writing. Watch for: informal-channel conversations preceding formal moves.
- `block-via-process` — actor uses a procedural objection (scope, sequencing, dependency) to delay a decision they oppose substantively. Watch for: process arguments that don't match substance.
- `go-quiet-while-processing` — actor takes 2-24h of silence before responding to a big input. Not disengagement; a deliberate processing pattern. Watch for: pattern violations (silence beyond baseline).
- `drop-single-line-conclusion` — actor processes silently then delivers a one-line decision without showing reasoning. Watch for: terse follow-up after silence.
- `protect-own-domain` — actor pushes back when their functional area is being repositioned by another peer. Watch for: territorial language ("this is engineering's call").
- `accept-tradeoff-with-explicit-cost` — actor agrees to a peer's ask but names the cost so it's auditable later. Watch for: explicit cost-naming in their ack.
- `seek-external-tie-breaker` — actor proposes routing a deadlocked decision to a third party (advisor, board, external expert). Watch for: third-party referrals in disputed discussions.

### Asymmetric-power-down (direct report, junior team member)

Principal has material authority over the actor. Moves often involve early flagging, scope renegotiation, or selective compliance.

- `flag-blocker-early` — actor raises an impediment well before deadline. Watch for: timing of escalation relative to deadline.
- `flag-blocker-late` — actor raises an impediment close to or past deadline. Watch for: pattern of late surfacing (capacity / confidence signal).
- `renegotiate-scope-mid-execution` — actor asks for scope reduction after starting work. Watch for: scope-creep direction (reduction vs expansion).
- `over-deliver-silently` — actor exceeds the brief without flagging upfront. Watch for: deliverable surprise on positive side.
- `under-deliver-without-flag` — actor delivers below brief, not raised in advance. Watch for: deliverable surprise on negative side (capacity or motivation signal).
- `request-clarity-on-authority` — actor explicitly asks where their decision rights end. Watch for: framing in language of "can I decide X".

### Customer (paying customer, prospect, design partner)

Transactional relationship with relationship overlay. Moves often involve renewal posture, pricing pressure, or champion dynamics.

- `delay-renewal-discussion` — actor pushes back the renewal conversation timing without explicit reason. Watch for: cancelled / rescheduled renewal meetings.
- `request-pricing-concession` — actor asks for a discount, tier change, or terms revision before committing. Watch for: ROI framing language.
- `champion-departure-handoff` — internal champion leaves, new buyer takes over with no prior context. Watch for: LinkedIn moves, replacement hire postings.
- `silently-reduce-engagement` — actor's team logs in less, opens fewer tickets, attends fewer reviews. Watch for: usage analytics decline before explicit churn signal.
- `surface-evaluation-of-alternatives` — actor mentions competitor evaluation directly or via auto-reply / RFP. Watch for: competitor names dropped in conversation.
- `request-ROI-justification` — actor asks for quantified business case before continuing. Watch for: CFO-style framing language.
- `extend-evaluation-window` — actor neither commits nor churns but buys time via demo extension, pilot extension, or evaluation deferral. Watch for: 30-90 day extension asks.
- `escalate-via-exec-sponsor` — actor routes the relationship through exec-level sponsor on either side. Watch for: CEO-to-CEO meetings appearing in calendars.
- `bring-in-procurement` — actor introduces procurement / legal / compliance to slow or commoditize the negotiation. Watch for: new attendee patterns in scheduling.
- `signal-renewal-via-expansion-ask` — actor shows commitment by asking for additional seats / entities / modules. Watch for: expansion framing in renewal-window conversations.

### Vendor (supplier, service provider, integration partner)

Principal pays the vendor. Relationship matters less than reliability and cost. Moves often involve SLA, pricing, or scope.

- `tighten-SLA-language` — actor accepts stricter service-level commitments without renegotiating price. Watch for: SLA redlining behavior.
- `request-pricing-renegotiation` — actor (vendor) asks for higher prices at renewal citing cost / market. Watch for: renewal-cycle pricing posture.
- `accept-status-quo-renew` — actor renews without renegotiation, signaling either healthy relationship or insufficient leverage. Watch for: absence of negotiation activity.
- `cite-roadmap-constraint` — actor blocks a feature request by citing their own roadmap. Watch for: roadmap-as-shield language.
- `propose-co-development` — actor offers to build the requested feature jointly with the principal funding part of the development. Watch for: cost-sharing language.

### Counterparty (opposing counsel, competitor, regulator in enforcement mode)

Adversarial or quasi-adversarial. Moves track negotiation patterns, not warmth.

- `escalate-to-leverage-point` — actor routes pressure through whatever leverage point they have (regulator, court, board, media). Watch for: leverage-point-naming in correspondence.
- `demand-concession-precondition` — actor refuses to engage on substance until an unrelated concession is granted. Watch for: precondition framing.
- `delay-as-tactic` — actor uses procedural delay (extensions, postponements, calendar friction) as negotiation leverage. Watch for: pattern of last-minute extensions.
- `signal-walk-away-bluff` — actor signals willingness to walk away to test the principal's commitment. Watch for: ultimatum language combined with continued engagement.
- `seek-precedent-anchor` — actor frames any concession as locking in a precedent for future deals. Watch for: precedent-naming language ("this would set the bar for...").
- `narrow-scope-to-survive` — actor accepts the principal's framing but narrows scope so much that the win is hollow. Watch for: scope-reduction in their proposed terms.

### Cross-relationship (apply across types)

Generic moves that recur across relationship types. Use when no relationship-specific move fits.

- `accept-and-replan` — actor accepts the situation / external constraint, regenerates plan with new timeline. Watch for: explicit acknowledgment without resistance.
- `force-decision` — actor demands an explicit yes/no before further work. Watch for: ultimatum-style framing.
- `parallel-track` — actor runs an alternative path concurrently with primary, choosing late. Watch for: redundant work streams appearing.
- `defer-and-watch` — actor explicitly parks the decision, sets trigger conditions to revisit. Watch for: trigger-condition language ("if X, we revisit").
- `walk-away` — actor drops the situation entirely, redirects resources elsewhere. Watch for: pipeline removal, calendar clearing.
- `regroup-internal-first` — actor pauses the external engagement to align their own side before continuing. Watch for: internal meeting density spike preceding external response.
- `bypass-route` — actor finds a workaround that avoids the blocking party. Watch for: new stakeholders introduced into the path.
- `negotiate-scope` — actor proposes a reduced or expanded scope rather than accepting/rejecting the original ask. Watch for: scope language ("if we narrowed this to...").
- `accept-asymmetric-bet` — actor accepts a deal with unequal upside / downside when they believe their information is better. Watch for: explicit risk-acknowledgment combined with commitment.

---

## Registry — Retired

(empty — moves are retired only if user explicitly removes via decision record. Retirement leaves an entry in the audit log below.)

---

## Audit log

| Date | Move added / retired | Source branch-out | User confirmed |
|------|---------------------|-------------------|----------------|
| YYYY-MM-DD | (registry initialized) | (no run) | (governance file) |

<!--
APPEND-ONLY. Each registry change creates one row.

Format:
| YYYY-MM-DD | added: <move-name> | <branch-out-slug or "freestanding"> | yes — per `memory/decisions/<date>-<slug>.md` |
| YYYY-MM-DD | retired: <move-name> | (n/a) | yes — per `memory/decisions/<date>-<slug>.md` |

Never delete rows. The audit log is the lineage of the registry.
-->
