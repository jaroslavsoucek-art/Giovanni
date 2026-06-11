# Origin

Giovanni was extracted from a working implementation of an AI Chief of Staff system built for a specific high-stakes program (multi-market e-commerce platform expansion). The source implementation accumulated months of daily operational use, multiple stakeholders, dozens of tracked decision records, daily digest runs, predictive simulations, and adversarial reviews.

The extraction goal: keep the **structure** (memory architecture, governance discipline, predictive layer, agent roster, adversarial-default workflow), drop all **content** (specific stakeholders, decisions, project context, domain-specific compliance maps).

## Extraction method

Specialist architect agents (one per layer: memory, governance, digest, prediction, stakeholder, adversarial, subagent-roster, slash-command) read from a read-only snapshot of the source implementation and produce sanitized templates + schema documentation in this repo. An orchestrator agent coordinates conflicts (e.g. memory schema references stakeholder schema).

Each architect operates under a strict no-leak rule: any source-domain reference (project name, person name, country, vendor) translates to a placeholder.

## Why distill?

Two reasons:

1. **The source system works.** Months of daily operational use validated the architecture beyond toy-example level. Most public AI Chief of Staff templates are starter kits at <500 stars with a few commits — they ship vision, not validated implementation.
2. **The structure is portable.** Memory layering, predictive simulation, governance discipline, adversarial review — none of these are domain-bound. A solo founder, a portfolio CEO, a consultant, a head of legal, can all benefit from the same structure filled with their own content.

## Not in scope of extraction

- Domain-specific compliance frameworks (e.g. country-specific regulatory adapters).
- Domain-specific market intelligence routines (e.g. competitor scans for a specific market).
- Domain-specific terminology baked into commands or workflows.
- Private operational data, stakeholder profiles, decision records — none migrate.

## Provenance

The source repository remains private. Giovanni is a clean-room reconstruction of the structural pattern, MIT-licensed and free to fork.
