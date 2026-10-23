#!/usr/bin/env python3
"""scripts/selftest-autonomy.py — end-to-end self-test of the autonomy layer.

Builds throwaway repos in a temp dir and exercises, through the real entry
points (CLIs and hook libs fed hook JSON on stdin): layer gating in lint,
project-owned lint rules, the inbox (dedupe, dated items never expire, expiry,
sync-source, lint→inbox), the confirm gate (ask / headless deny), autocommit
(auto paths committed, confirm paths left and surfaced), session recording,
workflow mining, correction capture, and the scheduler (plist + health check).

Exit 0 = all pass. Run by CI next to the lint fixtures.
"""
from __future__ import annotations

import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
S = PLUGIN / "scripts"
L = PLUGIN / "hooks" / "lib"
PY = sys.executable
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))


def run(args, cwd=None, stdin=None, env=None):
    e = {**os.environ, **(env or {})}
    e.pop("GIOVANNI_HEADLESS", None) if not (env or {}).get("GIOVANNI_HEADLESS") else None
    return subprocess.run(args, cwd=cwd, input=stdin, capture_output=True, text=True, env=e)


def git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q", "-b", "main"], cwd=root)
    run(["git", "config", "user.email", "t@example.invalid"], cwd=root)
    run(["git", "config", "user.name", "selftest"], cwd=root)


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def inbox_items(repo: Path) -> list[dict]:
    r = run([PY, str(S / "inbox.py"), "--repo", str(repo), "list", "--json"])
    return json.loads(r.stdout or "[]")


def t_layers(tmp: Path) -> None:
    repo = tmp / "layers"
    git_repo(repo)
    write(repo / "memory/stakeholders/jane-doe.md", "---\nslug: someone-else\n---\n# x\n")
    r = run([PY, str(S / "lint.py"), "--repo-root", str(repo), "--check", "stakeholder-frontmatter"])
    check("layers: rule fires when layer on", r.returncode == 1, r.stdout[-200:])
    write(repo / "docs/governance.config.yaml", "layers:\n  stakeholders: false\n")
    r = run([PY, str(S / "lint.py"), "--repo-root", str(repo), "--check", "stakeholder-frontmatter"])
    check("layers: rule skipped when layer off", r.returncode == 0, r.stdout[-200:])


def t_project_rules(tmp: Path) -> None:
    repo = tmp / "prules"
    git_repo(repo)
    write(repo / "scripts/lint_rules/demo.py", '''
        CHECK_ID = "project-demo"
        def run(ctx):
            ctx.add("medium", CHECK_ID, "project rule ran")
    ''')
    write(repo / "scripts/lint_rules/shadow.py", '''
        CHECK_ID = "l1-size"
        def run(ctx):
            ctx.add("critical", CHECK_ID, "should never run")
    ''')
    r = run([PY, str(S / "lint.py"), "--repo-root", str(repo), "--check", "project-demo"])
    check("project rules: discovered and run", r.returncode == 1 and "project rule ran" in r.stdout, r.stdout)
    r = run([PY, str(S / "lint.py"), "--repo-root", str(repo), "--check", "l1-size"])
    check("project rules: cannot shadow a plugin rule", "should never run" not in r.stdout, r.stdout + r.stderr)


def t_inbox(tmp: Path) -> None:
    repo = tmp / "inbox"
    git_repo(repo)
    write(repo / "docs/governance.config.yaml", "inbox:\n  title: Dnes\n  lint_to_inbox: true\n")
    ib = [PY, str(S / "inbox.py"), "--repo", str(repo)]
    run(ib + ["add", "--kind", "deadline", "--text", "A", "--key", "k1", "--due", "2026-01-10", "--source", "cases"])
    run(ib + ["add", "--kind", "deadline", "--text", "A2", "--key", "k1", "--due", "2026-01-10", "--source", "cases"])
    run(ib + ["add", "--kind", "proposal", "--text", "B", "--key", "k2", "--expires-days", "1", "--source", "x"])
    items = inbox_items(repo)
    check("inbox: dedupe by key", len(items) == 2 and items[0]["text"] == "A2", json.dumps(items))
    run(ib + ["refresh"], env={"GIOVANNI_SNAPSHOT_DATE": "2099-01-01"})
    items = inbox_items(repo)
    keys = {i["key"]: i for i in items}
    check("inbox: dated item never expires, escalates", "k1" in keys and keys["k1"].get("overdue") and
          keys["k1"]["priority"] == "high", json.dumps(items))
    check("inbox: undated item expires", "k2" not in keys, json.dumps(items))
    arch = list((repo / "memory/archive").glob("inbox-*.md"))
    check("inbox: expired item archived", arch and "· expired ·" in arch[0].read_text(), str(arch))
    run(ib + ["sync-source", "cases"])
    check("inbox: sync-source closes vanished items", not inbox_items(repo))
    run(ib + ["add", "--kind", "proposal", "--text", "C", "--key", "k3", "--source", "x"])
    run(ib + ["resolve", "k3", "--status", "dismissed"])
    run(ib + ["add", "--kind", "proposal", "--text", "C again", "--key", "k3", "--source", "x"])
    check("inbox: dismissed key is muted", not any(i["key"] == "k3" for i in inbox_items(repo)), json.dumps(inbox_items(repo)))
    run(ib + ["add", "--kind", "proposal", "--text", "C later", "--key", "k3", "--source", "x"],
        env={"GIOVANNI_SNAPSHOT_DATE": "2099-01-01"})
    check("inbox: mute runs out", any(i["key"] == "k3" for i in inbox_items(repo)), json.dumps(inbox_items(repo)))
    run(ib + ["resolve", "k3"])
    run(ib + ["add", "--kind", "deadline", "--text", "D", "--key", "k4", "--due", "2026-01-01", "--source", "x"])
    run(ib + ["resolve", "k4", "--status", "dismissed"])
    run(ib + ["add", "--kind", "deadline", "--text", "D", "--key", "k4", "--due", "2026-01-01", "--source", "x"])
    check("inbox: dated item cannot be muted", any(i["key"] == "k4" for i in inbox_items(repo)), json.dumps(inbox_items(repo)))
    run(ib + ["resolve", "k4"])
    # lint → inbox: an L1 over the line cap is a finding that must become an item, then close itself.
    write(repo / "memory/CLAUDE_MEMORY.md", "x\n" * 5)
    run(ib + ["refresh"], env={"GIOVANNI_L1_LIMIT": "2", "GIOVANNI_L1_LIMIT_CRITICAL": "50"})
    lint_items = [i for i in inbox_items(repo) if i["source"] == "lint"]
    check("inbox: lint finding becomes an item", any("l1-size" in i["text"] for i in lint_items), json.dumps(lint_items))
    run(ib + ["refresh"])
    lint_items = [i for i in inbox_items(repo) if i["source"] == "lint" and "l1-size" in i["text"]]
    check("inbox: lint item closes when lint is clean", not lint_items, json.dumps(lint_items))
    out = run(ib + ["session-start"]).stdout
    check("inbox: session-start silent when empty or valid JSON",
          out.strip() == "" or "additionalContext" in json.loads(out)["hookSpecificOutput"], out)
    other = tmp / "noinbox"
    git_repo(other)
    run([PY, str(S / "inbox.py"), "--repo", str(other), "session-start"])
    check("inbox: unconfigured project gets no files", not (other / "memory").exists())


def t_autonomy(tmp: Path) -> None:
    repo = tmp / "auto"
    git_repo(repo)
    write(repo / "docs/governance.config.yaml", """
        inbox: {}
        autonomy:
          auto_commit_paths: ["memory/*", "cases/*"]
          confirm_paths: ["knowledge/*"]
    """)
    write(repo / "knowledge/k.md", "v1\n")
    write(repo / "memory/m.md", "v1\n")
    write(repo / ".gitignore", "memory/.*.lock\nmemory/.telemetry/\nmemory/.runs/\n")
    run(["git", "add", "-A"], cwd=repo)
    run(["git", "commit", "-q", "-m", "init"], cwd=repo)
    gate = [PY, str(L / "autonomy.py"), "confirm-gate"]
    env = {"GIOVANNI_REPO_ROOT": str(repo)}
    payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(repo / "knowledge/k.md")}})
    r = run(gate, stdin=payload, env=env)
    check("confirm-gate: ask on confirm path", '"ask"' in r.stdout, r.stdout)
    r = run(gate, stdin=payload, env={**env, "GIOVANNI_HEADLESS": "1"})
    check("confirm-gate: deny headless", '"deny"' in r.stdout, r.stdout)
    r = run(gate, stdin=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(repo / "memory/m.md")}}), env=env)
    check("confirm-gate: silent elsewhere", r.stdout.strip() == "", r.stdout)
    write(repo / "knowledge/k.md", "v2\n")
    write(repo / "memory/m.md", "v2\n")
    write(repo / "cases/a/case.md", "new\n")
    r = run([PY, str(L / "autonomy.py"), "autocommit"], env=env)
    log = run(["git", "log", "--name-only", "--format=%s", "-1"], cwd=repo).stdout
    check("autocommit: auto paths committed", "memory/m.md" in log and "cases/a/case.md" in log, log + r.stderr)
    check("autocommit: confirm path not committed", "knowledge/k.md" not in log, log)
    items = inbox_items(repo)
    check("autocommit: confirm path surfaced in inbox",
          any(i["key"] == "autocommit:confirm:knowledge/k.md" for i in items), json.dumps(items))


def t_learning(tmp: Path) -> None:
    repo = tmp / "learn"
    git_repo(repo)
    write(repo / "docs/governance.config.yaml", r"""
        inbox: {}
        learning:
          unit_dirs: [cases]
          min_sessions: 3
          correction_markers: ['^\s*ne[,.!]', '\bpříště\b']
    """)
    tr = tmp / "t.jsonl"
    lines = [
        {"type": "user", "message": {"content": "<command-name>/kauza-sync</command-name>"}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Read", "input": {"file_path": str(repo / "cases/novak-2026/case.md")}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "python3 scripts/case.py sync novak-2026"}},
            {"type": "tool_use", "name": "Edit", "input": {"file_path": str(repo / "cases/novak-2026/timeline.md")}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "cat cases/novak-2026/case.md"}},
        ]}},
    ]
    tr.write_text("".join(json.dumps(x) + "\n" for x in lines))
    env = {"GIOVANNI_REPO_ROOT": str(repo)}
    run([PY, str(L / "learning.py"), "record"], stdin=json.dumps({"transcript_path": str(tr), "session_id": "s1"}), env=env)
    run([PY, str(L / "learning.py"), "record"], stdin=json.dumps({"transcript_path": str(tr), "session_id": "s1"}), env=env)
    tel = repo / "memory/.telemetry/sessions.jsonl"
    rows = [json.loads(x) for x in tel.read_text().splitlines()] if tel.exists() else []
    steps = rows[0]["steps"] if rows else []
    check("record: one row per session (upsert)", len(rows) == 1, str(rows))
    check("record: unit dir masked, no names", steps and all("novak" not in s for s in steps)
          and "edit:cases/*/timeline.md" in steps and "cmd:/kauza-sync" in steps, str(steps))
    seq = ["read:cases/*/case.md", "bash:python3 scripts/case.py", "edit:cases/*/deadlines.yaml", "read"]
    today = subprocess.run([PY, "-c", "import datetime;print(datetime.date.today())"], capture_output=True, text=True).stdout.strip()
    tel.write_text("".join(json.dumps({"session": f"m{i}", "date": today, "steps": ["read"] + seq + ["bash:git status"]}) + "\n"
                           for i in range(3)))
    r = run([PY, str(S / "mine-workflows.py"), "--repo", str(repo), "mine"])
    cands = list((repo / "memory/learning/candidates").glob("wf-*.md"))
    items = [i for i in inbox_items(repo) if i["kind"] == "skill-candidate"]
    check("mine: candidate written + proposed", len(cands) == 1 and len(items) == 1, r.stdout + json.dumps(items))
    r = run([PY, str(S / "mine-workflows.py"), "--repo", str(repo), "mine"])
    check("mine: idempotent", len([i for i in inbox_items(repo) if i["kind"] == "skill-candidate"]) == 1)
    cc = [PY, str(L / "learning.py"), "correction-check"]
    r = run(cc, stdin=json.dumps({"prompt": "ne, příště to piš česky"}), env=env)
    check("correction: marker fires", "LEARNING LOOP" in r.stdout, r.stdout)
    r = run(cc, stdin=json.dumps({"prompt": "připrav zprávu"}), env=env)
    check("correction: silent otherwise", r.stdout.strip() == "", r.stdout)
    write(repo / "memory/learning/corrections.md", """
        # Corrections
        - 2026-01-01 · one-off · zprava-o-plneni · datum vždy ve formátu D. M. RRRR
        - 2026-01-08 · one-off · zprava-o-plneni · datum ve formátu D. M. RRRR
    """)
    run([PY, str(S / "mine-workflows.py"), "--repo", str(repo), "corrections"])
    check("corrections: repeated one-off proposed as rule",
          any(i["kind"] == "canon-patch" for i in inbox_items(repo)))


def t_schedule(tmp: Path) -> None:
    repo = tmp / "sched"
    git_repo(repo)
    write(repo / "docs/governance.config.yaml", """
        inbox: {}
        schedule:
          - name: morning
            prompt: "/giovanni:inbox refresh"
            at: "07:30"
            weekdays: [1, 2, 3, 4, 5]
          - name: monthly
            prompt: "/x"
            at: "08:00"
            monthday: 1
    """)
    r = run([PY, str(S / "schedule.py"), "--repo", str(repo), "plist", "morning"])
    try:
        pl = plistlib.loads(r.stdout.encode())
        ok = pl["StartCalendarInterval"][0] == {"Weekday": 1, "Hour": 7, "Minute": 30} and len(pl["StartCalendarInterval"]) == 5
    except Exception as e:  # noqa: BLE001
        ok, pl = False, repr(e)
    check("schedule: plist valid, weekdays mapped", ok, str(pl)[:300])
    if shutil.which("plutil"):
        f = tmp / "p.plist"
        f.write_text(r.stdout)
        check("schedule: plutil -lint", run(["plutil", "-lint", str(f)]).returncode == 0)
    run([PY, str(S / "schedule.py"), "--repo", str(repo), "check"])
    check("schedule: not-installed surfaced",
          any(i["key"] == "schedule:not-installed" for i in inbox_items(repo)))
    r = run([PY, str(S / "schedule.py"), "--repo", str(repo), "run", "morning"],
            env={"GIOVANNI_CLAUDE_BIN": "/usr/bin/false"})
    check("schedule: failed run surfaced",
          r.returncode != 0 and any(i["key"] == "schedule:morning:failed" for i in inbox_items(repo)))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="giovanni-selftest-"))
    try:
        for t in (t_layers, t_project_rules, t_inbox, t_autonomy, t_learning, t_schedule):
            try:
                t(tmp)
            except Exception as e:  # noqa: BLE001
                check(f"{t.__name__} crashed", False, repr(e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    fails = 0
    print("Autonomy layer self-test\n")
    for name, ok, detail in RESULTS:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n        {detail[:400]}"))
        fails += 0 if ok else 1
    print(f"\nPassed: {len(RESULTS) - fails}  Failed: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
