#!/usr/bin/env python3
"""scripts/schedule.py — headless runs on a clock, and a check that they really ran.

A self-maintaining assistant needs something to wake it. This turns the
`schedule:` list in docs/governance.config.yaml into OS jobs that run
`claude -p "<prompt>"` in the repo, headless:

  GIOVANNI_HEADLESS=1          skills and hooks know nobody is there: questions go
                               to the inbox, confirm paths are denied, not asked
  --permission-mode dontAsk    anything not pre-allowed in .claude/settings.json
  --permission-prompts none    is denied — a headless run never waits on a prompt

Each run is logged to memory/.runs/<name>-<date>.log (gitignored); the last
success per job is kept in memory/.runs/state.json. A failed run, a job that has
not succeeded within its period, or jobs configured but never installed become
inbox items — a scheduler that silently stopped is worse than none.

Config:
  schedule:
    - name: morning            # [a-z0-9-]
      prompt: "/<skill> args"  # what the headless session is asked to do
      at: "07:30"              # local time
      weekdays: [1,2,3,4,5]    # optional, 1 = Monday … 7 = Sunday; omit = every day
      monthday: 1              # optional, instead of weekdays: day of month
      model: sonnet            # optional
      max_budget_usd: 2        # optional
      timeout_min: 30          # optional, default 30

Usage:
  schedule.py [--repo R] install [--dry-run]   macOS: write + load launchd agents; Linux: print crontab
  schedule.py [--repo R] uninstall
  schedule.py [--repo R] status
  schedule.py [--repo R] plist NAME
  schedule.py [--repo R] run NAME              the job body (what launchd calls)
  schedule.py [--repo R] check                 inbox items for failed / stale / uninstalled jobs
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gconfig  # noqa: E402
from inbox import Inbox  # noqa: E402

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")


def _jobs(cfg: dict) -> list[dict]:
    out = []
    for j in cfg.get("schedule") or []:
        if not isinstance(j, dict) or not NAME_RE.match(str(j.get("name", ""))) or not j.get("prompt"):
            continue
        hh, mm = (str(j.get("at", "07:00")).split(":") + ["0"])[:2]
        out.append({**j, "hour": int(hh), "minute": int(mm)})
    return out


def _runs(repo: Path, cfg: dict) -> Path:
    d = repo / cfg["memory_dir"] / ".runs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _state(repo: Path, cfg: dict) -> dict:
    f = _runs(repo, cfg) / "state.json"
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(repo: Path, cfg: dict, st: dict) -> None:
    (_runs(repo, cfg) / "state.json").write_text(json.dumps(st, indent=2, sort_keys=True))


def _label(repo: Path, name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", repo.name.lower()).strip("-") or "repo"
    return f"dev.giovanni.{slug}.{name}"


def _plugin_marker(repo: Path) -> str:
    common = subprocess.run(["git", "-C", str(repo), "rev-parse", "--git-common-dir"],
                            capture_output=True, text=True).stdout.strip() or ".git"
    p = Path(common)
    if not p.is_absolute():
        p = repo / p
    return str(p / "giovanni-plugin-root")


def _claude_bin() -> str:
    return os.environ.get("GIOVANNI_CLAUDE_BIN") or shutil.which("claude") or "claude"


def plist_for(repo: Path, cfg: dict, job: dict) -> dict:
    # The plugin path changes with every plugin version, so the job resolves it at
    # run time from the marker the session-start hook refreshes — never baked in.
    script = ('p="$(cat \'' + _plugin_marker(repo) + '\' 2>/dev/null)"; '
              'exec python3 "$p/scripts/schedule.py" --repo \'' + str(repo) + '\' run ' + job["name"])
    cal: list[dict] | dict
    if job.get("monthday"):
        cal = {"Day": int(job["monthday"]), "Hour": job["hour"], "Minute": job["minute"]}
    elif job.get("weekdays"):
        cal = [{"Weekday": int(w) % 7, "Hour": job["hour"], "Minute": job["minute"]} for w in job["weekdays"]]
    else:
        cal = {"Hour": job["hour"], "Minute": job["minute"]}
    claude = _claude_bin()
    path = ":".join(dict.fromkeys([str(Path(claude).parent), "/opt/homebrew/bin", "/usr/local/bin",
                                   "/usr/bin", "/bin"]))
    runs = _runs(repo, cfg)
    return {
        "Label": _label(repo, job["name"]),
        "ProgramArguments": ["/bin/bash", "-lc", script],
        "StartCalendarInterval": cal,
        "EnvironmentVariables": {"PATH": path, "GIOVANNI_CLAUDE_BIN": claude},
        "StandardOutPath": str(runs / f"launchd-{job['name']}.log"),
        "StandardErrorPath": str(runs / f"launchd-{job['name']}.log"),
        "RunAtLoad": False,
        "ProcessType": "Background",
    }


def cron_line(repo: Path, job: dict) -> str:
    dow = "*"
    dom = "*"
    if job.get("monthday"):
        dom = str(int(job["monthday"]))
    elif job.get("weekdays"):
        dow = ",".join(str(int(w) % 7) for w in job["weekdays"])
    return (f"{job['minute']} {job['hour']} {dom} * {dow} "
            f"bash -lc 'python3 \"$(cat {_plugin_marker(repo)})/scripts/schedule.py\" --repo {repo} run {job['name']}'")


def install(repo: Path, cfg: dict, dry: bool) -> int:
    jobs = _jobs(cfg)
    if not jobs:
        print("no valid jobs under `schedule:` in docs/governance.config.yaml")
        return 1
    if platform.system() != "Darwin":
        print("# Add these lines with `crontab -e` (this script does not edit your crontab):")
        for j in jobs:
            print(cron_line(repo, j))
        return 0
    agents = Path.home() / "Library" / "LaunchAgents"
    st = _state(repo, cfg)
    for j in jobs:
        pl = plist_for(repo, cfg, j)
        dst = agents / f"{pl['Label']}.plist"
        if dry:
            print(f"--- {dst}")
            print(plistlib.dumps(pl).decode())
            continue
        agents.mkdir(parents=True, exist_ok=True)
        uid = os.getuid()
        subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(dst)], capture_output=True)
        dst.write_bytes(plistlib.dumps(pl))
        r = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(dst)], capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{'✓' if ok else '✗'} {pl['Label']} → {dst}" + ("" if ok else f"  ({r.stderr.strip()})"))
        st.setdefault(j["name"], {})["installed"] = ok
        st[j["name"]]["installed_on"] = dt.date.today().isoformat()
    if not dry:
        _save_state(repo, cfg, st)
        check(repo, cfg)
    return 0


def uninstall(repo: Path, cfg: dict) -> int:
    agents = Path.home() / "Library" / "LaunchAgents"
    st = _state(repo, cfg)
    for j in _jobs(cfg):
        label = _label(repo, j["name"])
        dst = agents / f"{label}.plist"
        if platform.system() == "Darwin":
            subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(dst)], capture_output=True)
            dst.unlink(missing_ok=True)
        st.setdefault(j["name"], {})["installed"] = False
        print(f"removed {label}")
    _save_state(repo, cfg, st)
    return 0


def run(repo: Path, cfg: dict, name: str) -> int:
    job = next((j for j in _jobs(cfg) if j["name"] == name), None)
    if job is None:
        print(f"no job {name}", file=sys.stderr)
        return 2
    runs = _runs(repo, cfg)
    stamp = dt.datetime.now().strftime("%Y-%m-%d")
    log = runs / f"{name}-{stamp}.log"
    cmd = [_claude_bin(), "-p", str(job["prompt"]), "--permission-mode", "dontAsk",
           "--permission-prompts", "none", "--output-format", "text"]
    if job.get("model"):
        cmd += ["--model", str(job["model"])]
    if job.get("max_budget_usd"):
        cmd += ["--max-budget-usd", str(job["max_budget_usd"])]
    env = {**os.environ, "GIOVANNI_HEADLESS": "1", "GIOVANNI_REPO_ROOT": str(repo)}
    started = dt.datetime.now().isoformat(timespec="seconds")
    try:
        with open(log, "a", encoding="utf-8") as fh:
            fh.write(f"\n===== {started} {' '.join(cmd[:3])} …\n")
            fh.flush()
            r = subprocess.run(cmd, cwd=repo, stdout=fh, stderr=subprocess.STDOUT, env=env,
                               timeout=int(job.get("timeout_min", 30)) * 60)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        rc = 124
    except OSError as e:
        rc = 127
        log.write_text(log.read_text() + f"\n{e!r}\n" if log.exists() else repr(e))
    st = _state(repo, cfg)
    js = st.setdefault(name, {})
    js["last_run"] = started
    js["last_rc"] = rc
    if rc == 0:
        js["last_success"] = started
    _save_state(repo, cfg, st)
    for old in sorted(runs.glob(f"{name}-*.log"))[:-14]:
        old.unlink(missing_ok=True)
    with Inbox(repo).locked() as box:
        if rc == 0:
            box.close(f"schedule:{name}:failed", "done", "next run succeeded")
        else:
            box.add("warning", f"Scheduled run `{name}` failed (exit {rc}). Log: memory/.runs/{log.name}",
                    key=f"schedule:{name}:failed", source="schedule", priority="high",
                    on_yes=f"read memory/.runs/{log.name}, find the cause, fix it")
    return rc


def _period_days(job: dict) -> int:
    if job.get("monthday"):
        return 31
    wd = sorted({int(w) for w in job.get("weekdays") or []})
    if not wd:
        return 1
    gaps = [(wd[(i + 1) % len(wd)] - wd[i]) % 7 or 7 for i in range(len(wd))]
    return max(gaps)


def check(repo: Path, cfg: dict) -> int:
    jobs = _jobs(cfg)
    st = _state(repo, cfg)
    keep: set[str] = set()
    with Inbox(repo).locked() as box:
        not_installed = [j["name"] for j in jobs if not st.get(j["name"], {}).get("installed")]
        if not_installed:
            keep.add("schedule:not-installed")
            box.add("setup", f"Scheduled runs configured but not installed on this machine: "
                    f"{', '.join(not_installed)}.", key="schedule:not-installed", source="schedule-check",
                    on_yes="/giovanni:schedule install", priority="high")
        now = dt.datetime.now()
        for j in jobs:
            js = st.get(j["name"], {})
            if not js.get("installed"):
                continue
            anchor = js.get("last_success") or js.get("installed_on")
            if not anchor:
                continue
            try:
                last = dt.datetime.fromisoformat(anchor)
            except ValueError:
                continue
            limit = dt.timedelta(days=_period_days(j) + 1)
            if now - last > limit:
                key = f"schedule:{j['name']}:stale"
                keep.add(key)
                box.add("warning", f"Scheduled run `{j['name']}` has not succeeded since {last:%Y-%m-%d} "
                        "(machine off or asleep at run time, or the run fails).", key=key,
                        source="schedule-check", priority="high",
                        on_yes=f"run it now: schedule.py run {j['name']}; if the machine is often off at "
                               f"{j.get('at')}, move the time")
        box.sync_source("schedule-check", keep, "scheduler healthy")
    return 0


def status(repo: Path, cfg: dict) -> int:
    st = _state(repo, cfg)
    for j in _jobs(cfg):
        js = st.get(j["name"], {})
        when = f"day {j['monthday']}" if j.get("monthday") else \
            ("days " + ",".join(map(str, j["weekdays"])) if j.get("weekdays") else "daily")
        print(f"{j['name']:<16} {j['hour']:02d}:{j['minute']:02d} {when:<16} installed={js.get('installed', False)!s:<5} "
              f"last_success={js.get('last_success', '-')}  last_rc={js.get('last_rc', '-')}  prompt={j['prompt']!r}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("install")
    i.add_argument("--dry-run", action="store_true")
    sub.add_parser("uninstall")
    sub.add_parser("status")
    sub.add_parser("check")
    pl = sub.add_parser("plist")
    pl.add_argument("name")
    r = sub.add_parser("run")
    r.add_argument("name")
    args = ap.parse_args(argv)
    repo = gconfig.repo_root(args.repo)
    cfg = gconfig.config(repo)
    if args.cmd == "install":
        return install(repo, cfg, args.dry_run)
    if args.cmd == "uninstall":
        return uninstall(repo, cfg)
    if args.cmd == "status":
        return status(repo, cfg)
    if args.cmd == "check":
        return check(repo, cfg)
    if args.cmd == "plist":
        job = next((j for j in _jobs(cfg) if j["name"] == args.name), None)
        if not job:
            return 2
        sys.stdout.write(plistlib.dumps(plist_for(repo, cfg, job)).decode())
        return 0
    if args.cmd == "run":
        return run(repo, cfg, args.name)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
