# Contributing to Giovanni

Thanks for taking a look. Read this first — Giovanni is a hobby project with
unusual contribution constraints. PRs that miss them get sent back.

## What Giovanni is

A **methodology framework**, not a working assistant. The runtime lives in
*forks*, not here. This repo holds templates, schemas, agent definitions,
workflows, and lint rules — everything domain-agnostic.

## What gets merged

- **Schema improvements** that strictly increase generality (works for ≥2 domain
  shapes — e.g. solo founder, portfolio CEO, head of legal, consultant).
- **New worker agents / slash commands** that solve a common chief-of-staff
  pattern across domain shapes.
- **Governance / lint rules** that catch real footguns.
- **Honest docs fixes** — typos, broken refs, stale claims, missing
  cross-references.
- **Honest status updates** to the README (e.g. "Setup2 walkthrough now exists").

## What does NOT get merged

- Domain content. No real stakeholder names. No project codenames from
  your employer. No business specifics. If your PR contains a person's name
  that isn't `Alex Park / Sarah Vyas / Morgan Chen / Karim Solanki / DP1` (the
  Lattice Finance synthetic test domain) — it does not get merged.
- "Helper" abstractions for hypothetical future use. CLAUDE.md is strict on
  this. Three similar lines is fine; premature abstraction is not.
- Vendor lock-in. Giovanni works with Claude Code today and is designed to
  migrate to platform-native primitives as they ship. PRs that hardcode one
  vendor's quirks don't fit.
- Marketing surface area. No paid-tier signposting, no "sponsored by" links,
  no closed-source plugin pointers.

## Workflow

1. **Open an issue first** for anything beyond a typo. Avoid building 200 lines
   then finding out the pattern doesn't fit.
2. **One concern per PR.** Conventional Commits: `feat(memory): …`,
   `fix(governance): …`, `docs(readme): …`, `chore(release): …`.
3. **Test on the synthetic domain** (`docs/test-domain.md` — Alex Park /
   Lattice Finance). If your template breaks against Lattice, redesign before
   submitting.
4. **Lint must pass**: `./scripts/lint.sh`.
5. **Critical mode is default** for review. No flattery. PRs may get hard
   pushback. Read `docs/adversarial.md` for the review philosophy — SHIP /
   REWRITE / KILL verdicts, strongest-counter-case requirement.

## Realistic expectations

- This is part-time work. PRs may sit. Issues may sit. That's the deal.
- There is no SLA, no roadmap, no support commitment. MIT license, fork at
  your own risk.
- If you have a use case that needs guaranteed maintenance, fork and own it.

## Sanitization checklist (before opening a PR)

- [ ] No real person names anywhere (except documented Lattice synthetics)
- [ ] No employer codenames, project codenames, or product names
- [ ] No country / region references tied to a real program
- [ ] No vendor names beyond the abstract `<source_type>` enum
- [ ] No PII anywhere (emails, phone numbers, addresses)
- [ ] `./scripts/lint.sh` passes

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Critical review is welcome;
personal attacks are not. The two are not the same.
