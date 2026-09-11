# Giovanni — Claude Code Instructions (meta-builder mode)

This repo is a **methodology framework**, not a working assistant. Claude Code sessions here operate in **meta-builder mode**: read patterns from the live reference implementation, produce sanitized generic artifacts in this repo.

## Source

Giovanni is distilled from a **live** AI Chief of Staff implementation. Resolve its path with `bash scripts/source-path.sh`, which reads `$GIOVANNI_SOURCE` or the gitignored `.source-path`. Architect agents read from there. **Read-only: never write to that path, never commit there.**

### Why live, and not a snapshot

This used to point at a frozen copy, and the copy is why you are reading this. A snapshot stops the day it is taken; the source does not. Three months later the framework was behind its own source by 58 apparatus commits — most of them the interesting kind, rules written after something broke — and nothing in the repo showed it, because every architect was still reading a copy that looked complete.

A frozen source makes the drift invisible *and* unmeasurable: no diff, no date, no signal. Reading live means the gap between framework and source is always one `git log` away.

### What reading live costs you

- **The source moves under you.** Anything extracted records the source commit it came from (`bash scripts/source-path.sh --sha`). An unanchored "the source does X" rots like any other unanchored claim, and nobody can re-check it.
- **It is somebody's working repo.** A stray write is damage to live operational state. Read-only is not a convention here, it is the rule.
- **It is full of live domain content** — current names, numbers, open decisions, profiles of real people. The no-leak rule below is what makes reading live safe, and it is the thing to get right *before* the extraction, not in review.
- **The pointer stays off GitHub.** This repo is public; the source is a private operational repo whose name identifies the domain this framework was deliberately sanitised of. `.source-path` and the framework's own `docs/governance.config.yaml` (whose denylist is a list of that domain's proper nouns) are gitignored for that reason. Forks commit their own config — see `.gitignore`.

### Porting drift from the source

The recurring job here is not the original extraction, it is keeping up: the source keeps learning things, usually from incidents, and the generic version of each lesson belongs in this framework.

1. `git -C "$(bash scripts/source-path.sh)" log --oneline --since=<last port> -- .claude/ scripts/`
2. Sort into **mechanism** (portable: a rule, a gate, a cadence, a failure mode) and **domain** (not portable: a vendor, a market, a named system). Roughly a third is portable. When in doubt, ask whether a solo founder or a head of legal would hit the same failure.
3. Port the mechanism with the *reason* attached. A rule without the incident that produced it gets relaxed by the first person who finds it inconvenient — this is why the docs here carry failure stories instead of directives.
4. Cite the source commit in the commit message. That is the only thing making the next port able to start where this one stopped.

## Critical rules

1. **No domain content carry-over.** No stakeholder names, no project codenames, no business specifics from the source. Any source-domain codename, person name, integration partner, or country reference → translate to schema placeholder (`<stakeholder_slug>`, `<project_name>`, `<integration_partner>`, `<market>`, etc.).
2. **Schema over content.** Output templates, not filled examples. One worked example per artifact is fine to show shape — use a synthetic domain (default: solo fintech founder, see `docs/test-domain.md`).
3. **Critical mode is default.** No flattery. No RLHF. Pushback is default. Source has good ideas and bad ideas — flag both. If a pattern in source is over-engineered or domain-specific masquerading as generic, say so and propose a leaner version.
4. **Generic-first thinking.** Every template question: "would this work for a portfolio CEO? a solo founder? a consultant? a head of legal?" If only fits one domain shape, redesign.

## Specialist architects

Custom subagents live in `.claude/agents/`. Each has a narrow scope (memory, governance, digest, prediction, stakeholder, adversarial, subagent-roster, slash-command). They read source, output templates + schema explanation to their domain in this repo.

Specialist agents do NOT modify the source implementation. Ever, for any reason.

## Output structure

```
Giovanni/
├── CLAUDE.template.md (the FORK's operating contract — init-fork swaps it in for this file)
├── memory/
│   ├── README.md (schema explanation)
│   ├── templates/ (operational-memory, topic-shard, stakeholder, decision-record, brief, etc.)
│   └── examples/ (worked example using synthetic domain)
├── knowledge/
│   ├── README.md
│   └── constitution.template.md
├── .claude/
│   ├── agents/ (generic specialist agents)
│   ├── commands/ (generic slash commands)
│   ├── hooks/ (auto-regen, audit warnings, etc.)
│   └── workflows/ (digest, branch-out, audit, etc.)
├── docs/
│   ├── invariants.md (the register: what the repo asserts, and what enforces it)
│   ├── setup-guide.md (how to fork + customize for your domain)
│   ├── customization.md (per-layer customization points)
│   ├── test-domain.md (synthetic 2nd domain for pseudo-fork validation)
│   └── origin.md (where this came from)
├── scripts/ (auto-regen, audit cadence checks)
└── examples/ (filled fork on synthetic domain)
```

## Definition of done (whole project)

Giovanni is "done enough" when:
1. Repo can be cloned + customized for a new domain in <30 minutes (`docs/setup-guide.md` walks through).
2. Pseudo-fork test passes — templates filled for synthetic 2nd domain produce coherent operational artifacts.
3. All 8 specialist agents have generic versions.
4. At least 1 end-to-end workflow runs (e.g. daily digest) on a clean fork.

Not "done": specific cohort course material, marketing site, paid SaaS. Those are downstream of Giovanni shipping clean.

## What this repo is NOT

- Not a personal assistant (assistant lives in the fork, not the framework).
- Not a Claude Code marketplace listing.
- Not opinionated on Claude Code vs Antigravity vs other harnesses — design for portability.

## Commit style

Conventional commits. Squash specialist agent outputs into single coherent commits (`feat(memory): generic 4-layer schema templates`), not per-file.
