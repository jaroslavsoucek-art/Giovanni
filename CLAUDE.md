# Giovanni — Claude Code Instructions (meta-builder mode)

This repo is a **methodology framework**, not a working assistant. Claude Code sessions here operate in **meta-builder mode**: read patterns from a source snapshot, produce sanitized generic artifacts in this repo.

## Source

The reference implementation lives in `~/dev/giovanni-source-snapshot/` (read-only). Specialist architect agents read from there. **Never write to that path.**

## Critical rules

1. **No domain content carry-over.** No stakeholder names, no project codenames, no business specifics from the source. If you find a `Hospodka` / `Shoptet` / `NEO` / `MH` / `SOFA` / specific person name / specific country reference in source → translate to schema placeholder (`<stakeholder_slug>`, `<project_name>`, `<market>`, etc.).
2. **Schema over content.** Output templates, not filled examples. One worked example per artifact is fine to show shape — use a synthetic domain (default: solo fintech founder, see `docs/test-domain.md`).
3. **Critical mode is default.** No flattery. No RLHF. Pushback is default. Source has good ideas and bad ideas — flag both. If a pattern in source is over-engineered or domain-specific masquerading as generic, say so and propose a leaner version.
4. **Generic-first thinking.** Every template question: "would this work for a portfolio CEO? a solo founder? a consultant? a head of legal?" If only fits one domain shape, redesign.

## Specialist architects

Custom subagents live in `.claude/agents/`. Each has a narrow scope (memory, governance, digest, prediction, stakeholder, adversarial, subagent-roster, slash-command). They read source, output templates + schema explanation to their domain in this repo.

Specialist agents do NOT modify the source snapshot.

## Output structure

```
Giovanni/
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
