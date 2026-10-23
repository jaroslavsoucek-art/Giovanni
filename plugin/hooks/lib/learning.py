#!/usr/bin/env python3
"""Learning loop — the decision half of stop-session-record.sh and prompt-correction.sh.

An assistant "learns" here in exactly two ways, both as files in the repo:

1. **Repetition becomes a skill.** Every turn's Stop hook records the session's
   *shape* — the ordered tool steps, generalised (paths under a unit dir become
   `*`, digits become `#`, no prompt text, no file contents) — into
   memory/.telemetry/sessions.jsonl (gitignored, machine-local). The weekly
   miner (scripts/mine-workflows.py) finds sequences repeated across sessions
   and proposes them as skills through the inbox. Nothing activates itself.
2. **A correction becomes a rule.** When the principal's prompt reads like a
   correction (configurable regexes in learning.correction_markers), this hook
   tells the agent to classify it before continuing: a skill fix (apply it now,
   say so), a house rule (propose a canon patch via the inbox), or a one-off —
   and log it to memory/learning/corrections.md. One-offs that repeat are
   proposed as rules by the weekly run.

The principal never has to say "remember this". That is the point.

Subcommands:
  record            stdin Stop JSON (transcript_path, session_id) → upsert telemetry
  correction-check  stdin UserPromptSubmit JSON (prompt) → additionalContext or nothing
  steps FILE        print the normalised steps of one transcript (debugging)
"""
from __future__ import annotations

import datetime as dt
import json
import re
import shlex
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN / "scripts"))
import gconfig  # noqa: E402

NOISE_TOOLS = {"ToolSearch", "TodoWrite", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet",
               "AskUserQuestion", "ExitPlanMode", "EnterPlanMode", "ListAgents", "SendMessage"}
NOISE_PREFIXES = ("mcp__ccd_",)
READ_CMDS = {"cat", "sed", "head", "tail", "grep", "rg", "ls", "find", "wc", "echo", "printf",
             "awk", "sort", "uniq", "diff", "less", "file", "stat", "tree", "pwd", "which", "jq"}
UUIDISH = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-|^[0-9a-f]{20,}$", re.IGNORECASE)
CMD_RE = re.compile(r"<command-name>\s*/?([\w:.-]+)\s*</command-name>")
MAX_SESSIONS = 500


def genpath(repo: Path, raw: str, unit_dirs) -> str:
    p = Path(raw)
    if p.is_absolute():
        try:
            rel = p.resolve().relative_to(repo.resolve()).as_posix()
        except (ValueError, OSError):
            return "ext"
    else:
        rel = p.as_posix()
    parts = rel.split("/")
    for u in unit_dirs or []:
        up = u.strip("/").split("/")
        if parts[:len(up)] == up and len(parts) > len(up) + 1:
            parts[len(up)] = "*"
    rel = "/".join(parts)
    return re.sub(r"\d+", "#", rel)


def normalise(repo: Path, name: str, inp: dict, unit_dirs) -> str | None:
    if name in NOISE_TOOLS or name.startswith(NOISE_PREFIXES):
        return None
    if name in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = inp.get("file_path") or inp.get("notebook_path") or ""
        return f"{name.lower()}:{genpath(repo, path, unit_dirs)}"
    if name in ("Grep", "Glob"):
        return "search"
    if name == "Skill":
        return f"skill:{inp.get('skill', '?')}"
    if name in ("Agent", "Task"):
        return f"agent:{inp.get('subagent_type') or 'general'}"
    if name == "Bash":
        cmd = str(inp.get("command", "")).strip()
        cmd = re.sub(r"^(cd\s+\S+\s*(&&|;)\s*)+", "", cmd)
        try:
            toks = shlex.split(cmd)[:4]
        except ValueError:
            toks = cmd.split()[:4]
        if not toks:
            return None
        head = Path(toks[0]).name
        if head in READ_CMDS and not re.search(r"(^|\s)(-i|>|>>)(\s|$)", cmd.split("|")[0]):
            return "read"
        if "=" in head or head in ("for", "while", "if"):
            return "bash:shell"
        if head in ("python", "python3", "bash", "sh", "zsh", "node") and len(toks) > 1:
            arg = next((t for t in toks[1:] if not t.startswith("-")), "")
            if arg.startswith("<"):
                return f"bash:{head} inline"
            return f"bash:{head} {genpath(repo, arg, unit_dirs) if arg else ''}".strip()
        if head == "git" and len(toks) > 1:
            return f"bash:git {toks[1]}"
        return f"bash:{head}"
    if name.startswith("mcp__"):
        parts = name.split("__")
        server = parts[1] if len(parts) > 2 else ""
        tool = parts[-1]
        return f"mcp:{tool}" if (not server or UUIDISH.search(server)) else f"mcp:{server}:{tool}"
    return name.lower()


def steps_from_transcript(repo: Path, path: Path, unit_dirs) -> tuple[list[str], int]:
    steps: list[str] = []
    user_turns = 0
    try:
        fh = open(path, encoding="utf-8")
    except OSError:
        return steps, 0
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = d.get("type")
            msg = d.get("message") or {}
            content = msg.get("content")
            if t == "user":
                text = content if isinstance(content, str) else " ".join(
                    c.get("text", "") for c in (content or []) if isinstance(c, dict) and c.get("type") == "text")
                m = CMD_RE.search(text or "")
                if m:
                    steps.append(f"cmd:/{m.group(1)}")
                if text and not (isinstance(content, list) and any(
                        isinstance(c, dict) and c.get("type") == "tool_result" for c in content)):
                    user_turns += 1
            elif t == "assistant" and isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        s = normalise(repo, c.get("name", ""), c.get("input") or {}, unit_dirs)
                        if s:
                            steps.append(s)
    collapsed: list[str] = []
    for s in steps:
        if not collapsed or collapsed[-1] != s:
            collapsed.append(s)
    return collapsed, user_turns


def record() -> int:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0
    repo = gconfig.repo_root()
    lcfg = gconfig.config(repo)["learning"]
    if not lcfg["enabled"]:
        return 0
    tpath, sid = d.get("transcript_path"), d.get("session_id")
    if not tpath or not sid:
        return 0
    steps, turns = steps_from_transcript(repo, Path(tpath), lcfg["unit_dirs"])
    if not steps:
        return 0
    mem = repo / gconfig.config(repo)["memory_dir"] / ".telemetry"
    mem.mkdir(parents=True, exist_ok=True)
    f = mem / "sessions.jsonl"
    rows = []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("session") != sid:
                rows.append(r)
    rows.append({"session": sid, "date": dt.date.today().isoformat(), "headless": gconfig.headless(),
                 "user_turns": turns, "steps": steps})
    rows = rows[-MAX_SESSIONS:]
    f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return 0


def correction_check() -> int:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = str(d.get("prompt") or "")
    if not prompt or prompt.lstrip().startswith("/"):
        return 0
    repo = gconfig.repo_root()
    lcfg = gconfig.config(repo)["learning"]
    if not lcfg["enabled"]:
        return 0
    hit = None
    for pat in lcfg["correction_markers"] or []:
        try:
            if re.search(pat, prompt, re.IGNORECASE | re.MULTILINE):
                hit = pat
                break
        except re.error:
            continue
    if not hit:
        return 0
    msg = ("LEARNING LOOP — this prompt reads like a correction (marker `" + hit + "`). Before you "
           "continue, classify it in one line to the principal: (a) skill-fix — the way a skill or "
           "procedure does something is wrong: fix that file now and say which; (b) rule — a standing "
           "rule of how the principal works: propose it with `scripts/inbox.py add --kind canon-patch` "
           "(plugin scripts) naming the target file; (c) one-off — only this case. Then append one line "
           "to memory/learning/corrections.md: `- YYYY-MM-DD · <skill-fix|rule|one-off> · <target file "
           "or topic> · <the rule in ≤ 15 words, no names or case data>`. If it was not a correction, "
           "ignore this note.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": msg}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if cmd == "record":
            sys.exit(record())
        if cmd == "correction-check":
            sys.exit(correction_check())
        if cmd == "steps" and len(sys.argv) > 2:
            repo = gconfig.repo_root()
            s, n = steps_from_transcript(repo, Path(sys.argv[2]),
                                         gconfig.config(repo)["learning"]["unit_dirs"])
            print(json.dumps({"user_turns": n, "steps": s}, ensure_ascii=False, indent=1))
            sys.exit(0)
    except Exception as e:  # noqa: BLE001 — a hook never breaks a session
        print(f"learning: {e!r}", file=sys.stderr)
        sys.exit(0)
    sys.stderr.write(__doc__)
    sys.exit(2)
