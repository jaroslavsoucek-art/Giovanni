# Example fork

## WORKFLOWS (route table)

| Trigger | File | Writes | Stops at | Autonomy |
|---|---|---|---|---|
| `/digest` | `.claude/commands/digest.md` | `memory/digest_state.md` | Chat, no auto-commit | hook-startable |
| `/ghost` | `.claude/commands/ghost.md` | nothing | nowhere | explicit |

## AGENTS

The workflow file has no row; the ghost command has no file.
