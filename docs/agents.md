# Agent design patterns

How Giovanni uses custom subagents — when to spawn, how to compose them, what they do and don't do, and how the operational roster integrates with slash commands and digest workflows.

This doc is the "why" companion to [`.claude/agents/README.md`](../.claude/agents/README.md) (the roster).

## 1. Agent vs architect distinction

Two populations live under `.claude/agents/`. They look identical structurally — same frontmatter, same body shape — but their purposes are different.

**Architect agents** are framework-builders. They ran once during Giovanni bootstrap. Each architect owns a subsystem:

- `memory-architect` → 4-layer memory templates + docs
- `governance-architect` → constitution pattern + scripts + hooks
- `stakeholder-architect` → per-stakeholder profile schema
- `prediction-architect` → predictive-layer templates + 8 binding principles
- `subagent-roster-architect` → operational agent definitions
- `adversarial-architect` → adversarial review workflow + adversarial-reviewer agent + SHIP/REWRITE/KILL verdict policy
- `digest-architect` → daily digest workflow (12 steps) + state/sources templates + session-start hook
- `slash-command-architect` → 8 finalized slash commands + design patterns

After bootstrap, architects are frozen. You don't spawn `memory-architect` to do daily work; the templates and docs it produced are what daily work uses. Architects come back online only when the framework itself needs structural revision (rare).

**Operational agents** are worker agents. They run in daily operations, spawned by the principal (or by slash commands routing through `prediction-runtime`).

| Operational agent | Daily-use trigger |
|---|---|
| `source-puller` | Digest fan-out; isolated pull of one source |
| `researcher` | "Investigate X" — external research |
| `profile-bootstrap` | "Bootstrap / refresh stakeholder X" |
| `deliverable-reviewer` | Pre-share content QA |
| `consistency-checker` | `/consistency-check` semantic drift sweep |
| `market-radar` | `/market-radar` external competitive scan |
| `prediction-runtime` | `/branch-out`, `/shadow-review`, `/calibration-report` |

The framing matters because confusing the two leads to either over-spawning (treating a one-time framework task as a daily agent) or under-spawning (forgetting an operational agent exists because it's buried alongside frozen architects).

## 2. When to spawn an agent vs do the work inline

Spawn an agent when **at least one** is true:

1. **Context isolation matters.** The work would pollute main thread context with raw tool output. Example: pulling 50 chat messages and 30 emails through the main thread fills it with noise; routing through `source-puller` returns 15 clean bullets.

2. **Parallel work is independent.** Five sources to pull → fan-out 5 agents in one message → 30-second total instead of 2-3 minute serial run.

3. **Tool scope is materially different from main.** Heavy web-fetch budget (`researcher`, `market-radar`), repo-wide grep (`consistency-checker`), specialized read-only access — these are easier to scope on a dedicated agent than to mix into main.

4. **The work has a clear bounded contract.** Inputs → protocol → outputs that fit a structured return format. If the work is "explore and figure out what to do", it's not bounded enough for an agent yet.

5. **The work is reused across scenarios.** A one-off task isn't worth the spawn overhead. If you find yourself doing the same shape of work three times, that's the agent candidate.

Do the work **inline** when all of these hold:

- Single tool call, single read, single bullet response
- No context pollution risk
- No reuse — genuinely one-off
- Trivial enough that the agent's framing-and-handoff overhead would dominate

Examples of "do inline":
- `git log --oneline -5` to check recent commits
- Reading a single file to answer a single question
- A 3-line stakeholder profile correction the principal asked for in-thread

## 3. Parallel fan-out pattern

**One message, N agent calls.** Independent work runs concurrently in isolated contexts.

Canonical example — daily digest source pull:

```
Spawn 5 source-puller agents in a single message:
- Agent(source-puller, "source_type=chat-platform source_identifier=<config> window_start=<iso>")
- Agent(source-puller, "source_type=email source_identifier=<config> window_start=<iso>")
- Agent(source-puller, "source_type=calendar source_identifier=<config> window_start=<today> window_end=<friday>")
- Agent(source-puller, "source_type=project-tracker source_identifier=<config> window_start=<iso>")
- Agent(source-puller, "source_type=version-control source_identifier=<config> window_start=<iso> last_run_sha=<sha>")
```

Each agent returns structured bullets. Main thread merges and synthesizes.

**Why this works:**

- Each agent's context isolation prevents source A's raw output from polluting source B's reasoning
- Wall-clock time = max(agent durations), not sum
- Failures don't cascade (one source unreachable doesn't stop the others)

**Other parallel fan-out candidates:**

- Multi-stakeholder profile refresh ("refresh profiles for everyone with signal today") → parallel `profile-bootstrap` agents
- Multi-perspective review on a feasibility question → parallel `researcher` (external) + domain-specific architect/expert (internal) agents — orchestrator merges

**Don't fan-out when:**

- Agents depend on each other's output (use sequential chain instead)
- The fan-out is just to feel concurrent — if 2 of 5 agents will block on the same shared resource, you didn't gain anything

## 4. Sequential chain pattern

Agent A's output feeds Agent B. **Main thread orchestrates** — no auto-handoff between agents.

Canonical example — research → adversarial review:

1. `researcher` produces a memory note + proposed constitution patch
2. Main thread reads the note, decides the patch is non-trivial
3. Main thread spawns `adversarial-reviewer` (per [`.claude/agents/adversarial-reviewer.md`](../.claude/agents/adversarial-reviewer.md)) with the proposed patch as input
4. Adversarial reviewer returns redline / kill / ship verdict
5. Main thread applies the patch or rejects it

**Critical rule:** agents never call other agents. Main thread is the orchestrator. This prevents:

- **Hidden cascades** — agent A spawning B spawning C three layers deep, with the principal having no visibility
- **Failure amplification** — error in B propagating through opaque chain
- **Context bleed** — agent A passing its raw thoughts into agent B's prompt instead of clean structured handoff

**Other chain candidates:**

- `market-radar` flags a drift candidate → main thread spawns `prediction-runtime` with mode=branch-out for the affected situation
- `profile-bootstrap` returns shallow profile → main thread notes that `/branch-out` requiring that actor will hard-stop, surfaces to principal

## 5. Isolation principle

**Main thread never sees an agent's raw tool output, only its final structured report.** The agent's body is the contract; what it returns is what main sees.

Consequences:

- Agents are forced to summarize / synthesize at their boundary (no "here's the dump for you to figure out")
- Main thread context stays clean — even after 5 source-pullers ran, main sees ~50 bullets, not 1000 lines of raw tool output
- Agents can use heavy tools (web fetch, big greps) without burdening main's context window

The flip side: an agent that produces bad final output is opaque to main. Mitigation:

- Strong **reporting format** rules in each agent definition (what fields must appear, what format)
- Hard rules around honesty (no coverage faking, no confidence inflation, no fabrication)
- Spot-checks via slash command output where the principal sees the final artifact

## 6. Model selection

| Model | When to use | Rationale |
|---|---|---|
| `opus` | Multi-actor reasoning, deep adversarial analysis, generative synthesis | Branch-out simulation, research with cross-source synthesis, deliverable QA where judgment matters |
| `sonnet` | Structured execution with clear protocol, lower-stakes drift detection, source pulling | Source-puller (mechanical extraction), consistency-checker (rule-based drift), shadow-review + calibration-report (aggregation over schema) |
| `haiku` | High-volume / simple tasks (none currently in Giovanni roster) | Future use: per-message classification, simple lookups, mechanical formatting |

**Tradeoffs:**

- Opus is expensive — using it for source-puller would burn budget without quality gain
- Sonnet on multi-actor branch-out is risky — the predictive layer's IP depends on judgment that opus delivers more reliably
- Resist the urge to "upgrade all agents to opus for safety" — it's not safety, it's cost without proportional value

Document the model choice per agent. If you find yourself switching mid-development ("this is harder than I thought, bump to opus"), document why so the next forker doesn't repeat the calibration.

## 7. Tool scope

**Each agent requests only tools it needs.** Three reasons:

1. **Surface area discipline** — fewer tools means fewer ways to drift outside scope
2. **Spawn-time clarity** — reading the frontmatter tells you what the agent can touch
3. **Cost/safety** — tools like WebFetch / WebSearch should be on agents that genuinely need them, not all

| Agent | Tools | Why |
|---|---|---|
| `source-puller` | Bash, Read, Grep | Pulls from CLI tools and reads repo config; no writes |
| `researcher` | WebFetch, WebSearch, Read, Grep, Glob, Bash, Write | Web research + writes memory note |
| `profile-bootstrap` | Read, Write, Edit, Grep, Glob, Bash | Reads cross-source signals (via Bash hooks), writes profile |
| `deliverable-reviewer` | Read, Grep, Glob, Bash | Read-only; runs git for prior-version detection |
| `consistency-checker` | Read, Grep, Glob, Bash, Write | Writes only to `memory/audits/consistency/` |
| `market-radar` | WebFetch, WebSearch, Read, Grep, Glob, Bash, Write | Web scan + writes to `memory/intel/market-radar/` only |
| `prediction-runtime` | Read, Write, Edit, Glob, Grep, Bash | Reads templates / profiles, writes branch-out + shadow + decision draft + calibration |

**Reality check on tool-list portability:** in this snapshot of agent definitions, tool names are kept generic (`Bash`, `Read`, etc.). Source pullers in the source-domain implementation hardcoded specific MCP tool identifiers (`mcp__edead074-c9ff-4f68-936f-5f0071b68cc3__asana_*`, `mcp__e5c99758-3627-406a-b17c-dc1459809b75__slack_*`, etc.). **Fork-time:** when a fork wires their actual chat platform / project tracker, the frontmatter `tools:` list extends with the specific MCP identifiers. This generic version of `source-puller` documents the source_type enum but doesn't pre-wire — that's a fork concern.

## 8. Reporting format

Every agent returns a structured final message to main thread. **Not chain-of-thought, not raw tool output, not "here's what I did".** A structured report.

Minimum fields (each agent's "Reporting" section formalizes its exact shape):

- **Files written** (paths)
- **Key decisions / findings** (≤5 bullets)
- **Open questions** (if any)
- **Cross-references** (links to artifacts the principal needs to act on next)

Example — `profile-bootstrap` report:

```
Updated/created: memory/stakeholders/<slug>.md
Mode: bootstrap | refresh
Profile depth: <prior> → <new>
Key changes:
- New trajectory entry: <date>, signal=<warming/cooling>, channel=<source>
- New thread opened: <name>
Sentiment shift: no
Active threads delta: +1 / -0
Open follow-ups for principal: <list, or "none">
```

The principal can act on this in seconds. They don't need to re-read the agent's internal reasoning.

**Anti-pattern:** agents that dump their stream-of-thought as the "report". This burns main thread context and forces the principal to re-do the agent's synthesis work.

## 9. Anti-patterns

### Over-spawning

Spawning an agent for a single grep or single file read. Cost: 5-10s overhead per agent invocation; the read itself is sub-second. Net loss.

**Test:** if your agent's bounded contract is "read this one file and return its contents", just do it inline.

### Auto-handoff between agents

Agent A internally spawns Agent B. Symptoms:
- Hidden cascade visibility loss (the principal can't see what B saw)
- Failure modes amplified (A's error → B's bad input → C's wrong output, all opaque)
- Context bleed (A's reasoning becomes B's prompt)

**Rule:** agents never spawn other agents. Main thread is the orchestrator.

### Context bleeding

Agent writes outside its scope. `source-puller` writes to memory; `consistency-checker` patches the constitution; `market-radar` updates stakeholder profiles. Each is a violation of the "What you do NOT own" section.

**Mitigation:** every agent definition has an explicit "What you do NOT own" section. Read it when defining a new agent; enforce it when reviewing agent runs.

### Recommendation creep

`consistency-checker` should report findings, not auto-fix. `deliverable-reviewer` should verdict, not rewrite. `market-radar` should flag drift, not "consider switching to X". Each of these is a slow drift — agents start helpful, become opinionated, then become wrong.

**Mitigation:** every agent definition explicitly forbids the next-step action. Lint rules catch some (e.g. `branch_out_no_recommendation.py`). Adversarial review on agent outputs catches the rest.

### Confidence inflation

Agents marking findings as `FACT` when the evidence is `ESTIMATE`. Markings as `high` confidence when sources disagree. Hiding that 5 of 25 sources were unreachable.

**Mitigation:** explicit confidence-tier definitions in every agent that reports findings (researcher, market-radar). Hard rule: "no coverage faking".

### Single-pass deliverable

Agent runs once, output is treated as final. No adversarial review. No spot-checking. Over time, agent quality degrades silently.

**Mitigation:** important agents (researcher proposing constitution patches, prediction-runtime in branch-out mode) feed into adversarial review (sequential chain to adversarial-reviewer). Calibration discipline catches degradation in the predictive layer.

## 10. Workflow integration

### Slash commands

Slash commands route through `prediction-runtime` (for `/branch-out`, `/shadow-review`, `/calibration-report`) or directly invoke other agents (`/market-radar` → `market-radar`; `/consistency-check` → `consistency-checker`).

Slash command runtime implementation lives in `.claude/commands/*.md` (one file per command). Each file is a thin invocation shell — pre-flight, argument parsing, agent routing. The mechanics live in the agents and workflows. See [`docs/slash-commands.md`](slash-commands.md) for design patterns + argument conventions and [`.claude/commands/README.md`](../.claude/commands/README.md) for the registry.

### Daily digest

Daily digest workflow (per [`.claude/workflows/daily-digest.md`](../.claude/workflows/daily-digest.md)) orchestrates parallel fan-out to `source-puller` agents, then synthesizes and routes to:

- Drift detection (main thread, against constitution + memory)
- Stakeholder profile update triggers (spawning `profile-bootstrap` for stakeholders with signal)
- Branch-out candidate triage (surface for principal to run `/branch-out`)
- Pre-meeting brief generation (main thread, against stakeholder profiles)
- Shadow lookback (silent, internal to digest)

### Hooks

Most hooks are governance plumbing (INDEX/MAP regen, audit cadence warnings). Some hooks invoke agents:

- Session-start hook can surface "shadow-review due" → user runs `/shadow-review`, which spawns prediction-runtime
- Memory-edit hook regenerates MAP (doesn't spawn agent — it's a script)

Agents are not the primary hook actors; scripts are. Agents enter when judgment is needed.

## 11. Adding a new agent

Bar: bounded, parallelizable OR pollution-prone, reused enough to justify the overhead.

Process:

1. **Validate the need.** Have you done this work inline 3+ times? Does it consistently pollute main context or require parallel execution?
2. **Draft the frontmatter.** Name (kebab-case), description with trigger phrases, tools (minimal), model (justify the choice).
3. **Define the contract.** Inputs the caller must provide. Protocol steps (numbered). Reporting format.
4. **Define what it does NOT own.** This section is load-bearing — without it, scope creep is inevitable.
5. **Mental fit test.** Walk through 3 concrete scenarios (real or representative). Does the agent definition give clear, unambiguous behavior for each?
6. **Add to `.claude/agents/README.md`** roster table. Update CLAUDE.md if the fork's project instructions also reference the roster.
7. **Lint pass.** `bash scripts/lint.sh` should stay clean. Add frontmatter assertions to lint rules if you've introduced a new agent-shape.

Don't add an agent because it would be cool. Add it because the workflow without it is meaningfully worse.

## Cross-references

- **Roster table:** [`.claude/agents/README.md`](../.claude/agents/README.md)
- **Memory system:** [`memory/README.md`](../memory/README.md)
- **Governance:** [`docs/governance.md`](governance.md)
- **Stakeholder profiles:** [`docs/stakeholder-profiles.md`](stakeholder-profiles.md)
- **Predictive layer:** [`docs/prediction.md`](prediction.md)
- **Test domain (for fork-time validation):** [`docs/test-domain.md`](test-domain.md)
