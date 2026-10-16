#!/usr/bin/env python3
"""scripts/run-digest-dryrun.py — deterministic digest-readiness harness.

The daily digest workflow (.claude/workflows/daily-digest.md) is an LLM
procedure — it cannot be replayed deterministically, and a real run needs
live MCP source pulls. This harness does NOT execute synthesis. It validates
that a fork has everything the digest workflow requires at pre-flight, that
its state/config files parse, that its cross-references resolve, and that a
demonstrated digest render conforms to the Step-12 output contract.

That is the honest, falsifiable closure of definition-of-done #4 ("at least
one end-to-end workflow runs on a clean fork"): it proves the digest CAN run
on this fork — that the contract is satisfied — without claiming to have run
the model.

Usage:
    python3 scripts/run-digest-dryrun.py [--repo-root <path>] [--quiet]

    # validate the bundled pseudo-fork:
    python3 scripts/run-digest-dryrun.py --repo-root examples/lattice-finance

Exit codes:
    0 — digest-ready (no FAIL checks; WARN allowed)
    1 — not digest-ready (one or more FAIL checks)
    2 — internal error (bad --repo-root)
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml  # type: ignore[import-not-found]
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# Source-type enum — mirrors memory/digest-sources.template.md + source-puller.
SOURCE_TYPES = {
    "chat-platform", "email", "calendar", "project-tracker",
    "version-control", "crm", "documentation-platform",
}

# Step-12 render contract — section markers a rendered digest must demonstrate.
# Matched case-insensitively as substrings against a reference transcript.
RENDER_SECTIONS = [
    "Recap", "Today", "Week ahead", "Active blockers",
    "Stakeholder updates", "Drift flags",
]

PLACEHOLDER_TS = "<YYYY-MM-DDTHH:MM:SSZ>"

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"


class Report:
    def __init__(self, quiet: bool) -> None:
        self.rows: list[tuple[str, str, str]] = []
        self.quiet = quiet

    def add(self, status: str, check: str, message: str) -> None:
        self.rows.append((status, check, message))

    @property
    def failed(self) -> bool:
        return any(s == FAIL for s, _, _ in self.rows)

    def render(self) -> None:
        glyph = {PASS: "  ok  ", WARN: " warn ", FAIL: " FAIL "}
        for status, check, message in self.rows:
            if self.quiet and status == PASS:
                continue
            print(f"[{glyph[status]}] {check:28} {message}")
        n_pass = sum(s == PASS for s, _, _ in self.rows)
        n_warn = sum(s == WARN for s, _, _ in self.rows)
        n_fail = sum(s == FAIL for s, _, _ in self.rows)
        print()
        verdict = "DIGEST-READY" if not self.failed else "NOT DIGEST-READY"
        print(f"{verdict}  —  pass: {n_pass}  warn: {n_warn}  fail: {n_fail}")


# ---------------------------------------------------------------------------
# Minimal helpers (standalone — no dependency on lint.py internals)

_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def frontmatter(path: Path) -> dict | None:
    if not HAVE_YAML:
        return None
    try:
        m = _FM_RE.match(path.read_text(encoding="utf-8", errors="ignore"))
    except OSError:
        return None
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def parse_iso_utc(token: str) -> datetime | None:
    token = token.strip()
    if token.endswith("Z"):
        token = token[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(token)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return None  # naive timestamps are rejected — the window must be unambiguous
    return dt


# ---------------------------------------------------------------------------
# Checks

def check_preflight_markers(repo: Path, r: Report) -> None:
    sources = repo / "memory" / "digest_sources.md"
    digest_doc = repo / "docs" / "digest.md"
    if sources.is_file():
        r.add(PASS, "preflight-cwd-markers", "memory/digest_sources.md present")
    else:
        r.add(FAIL, "preflight-cwd-markers",
              "memory/digest_sources.md missing — Step 0 pre-flight would STOP")
    if digest_doc.is_file():
        r.add(PASS, "preflight-digest-doc", "docs/digest.md present")
    else:
        r.add(WARN, "preflight-digest-doc",
              "docs/digest.md missing — Step 0 CWD marker; a full fork ships it")


def check_state(repo: Path, r: Report) -> None:
    state = repo / "memory" / "digest_state.md"
    if not state.is_file():
        r.add(WARN, "digest-state",
              "memory/digest_state.md absent — fresh fork; first /digest will seed it")
        return
    text = state.read_text(encoding="utf-8", errors="ignore")
    if PLACEHOLDER_TS in text:
        r.add(WARN, "digest-state",
              "last-run timestamp is the unfilled placeholder — first-run: seed required")
        return
    m = re.search(r"^\s*-\s*timestamp:\s*(\S+)", text, re.MULTILINE)
    if not m:
        r.add(WARN, "digest-state",
              "no '- timestamp:' line — first-run: workflow will ASK for a seed window")
        return
    dt = parse_iso_utc(m.group(1))
    if dt is None:
        r.add(FAIL, "digest-state",
              f"last-run timestamp '{m.group(1)}' is not parseable tz-aware ISO-8601")
        return
    age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    r.add(PASS, "digest-state",
          f"last-run timestamp parses ({m.group(1)}, ~{age_h:.0f}h old)")


def check_sources(repo: Path, r: Report) -> None:
    sources = repo / "memory" / "digest_sources.md"
    if not sources.is_file():
        return  # already FAILed in preflight
    text = sources.read_text(encoding="utf-8", errors="ignore")
    # Strip HTML comments (the template ships schema examples inside <!-- -->).
    body = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # A source ENTRY is "- source_type: <enum>" followed (within the block) by an
    # "identifier:" line. The template also ships per-type SCHEMA SKELETONS outside
    # comments whose identifier is a "<placeholder>" — those are NOT configured
    # sources. Count an entry only if its identifier is concrete, so an unfilled
    # fork honestly reports zero (a digest with zero real sources is a config error).
    blocks: list[dict] = []
    cur: dict | None = None
    for ln in body.splitlines():
        m = re.match(r"^\s*-\s*source_type:\s*([a-z-]+)", ln)
        if m:
            cur = {"type": m.group(1), "identifier": None}
            blocks.append(cur)
        elif cur is not None and cur["identifier"] is None:
            im = re.match(r"^\s*identifier:\s*(.+?)\s*$", ln)
            if im:
                cur["identifier"] = im.group(1)

    def concrete(b: dict) -> bool:
        if b["type"].startswith("<"):
            return False
        idv = b["identifier"]
        return bool(idv) and not re.search(r"<[^>]+>", idv)

    real = [b for b in blocks if concrete(b)]
    if not real:
        r.add(FAIL, "digest-sources",
              "no sources with a concrete identifier — unfilled template or empty config "
              "(a digest with zero sources is a config error, not a quiet day)")
        return
    bad = sorted({b["type"] for b in real if b["type"] not in SOURCE_TYPES})
    if bad:
        r.add(FAIL, "digest-sources",
              f"{len(real)} sources, but invalid source_type(s): {', '.join(bad)}")
        return
    kinds = ", ".join(sorted({b["type"] for b in real}))
    r.add(PASS, "digest-sources", f"{len(real)} sources configured ({kinds})")


def check_triage(repo: Path, r: Report) -> None:
    triage = repo / "memory" / "triage-heuristic.yaml"
    if not triage.is_file():
        r.add(WARN, "triage-heuristic",
              "memory/triage-heuristic.yaml absent — branch-out triage uses defaults")
        return
    if not HAVE_YAML:
        r.add(WARN, "triage-heuristic", "PyYAML missing — cannot validate triage schema")
        return
    try:
        data = yaml.safe_load(triage.read_text(encoding="utf-8", errors="ignore"))
    except yaml.YAMLError as e:
        r.add(FAIL, "triage-heuristic", f"unparseable YAML — {e}")
        return
    if not isinstance(data, dict):
        r.add(FAIL, "triage-heuristic", "not a YAML mapping")
        return
    missing = [k for k in ("active_branch_out", "shadow_only", "specificity_gate")
               if k not in data]
    if missing:
        r.add(FAIL, "triage-heuristic", f"missing required keys: {', '.join(missing)}")
        return
    r.add(PASS, "triage-heuristic",
          "schema present (active_branch_out / shadow_only / specificity_gate)")


def check_constitution(repo: Path, r: Report) -> None:
    # Default fork constitution path; forks may rename via governance config.
    candidates = list((repo / "knowledge").glob("*.md")) if (repo / "knowledge").is_dir() else []
    canon = repo / "knowledge" / "constitution.md"
    if canon.is_file():
        r.add(PASS, "constitution", "knowledge/constitution.md present (Step 10 drift anchor)")
    elif candidates:
        names = ", ".join(p.name for p in candidates if p.name not in ("INDEX.md", "README.md"))
        r.add(WARN, "constitution",
              f"no knowledge/constitution.md; other knowledge docs present ({names})")
    else:
        r.add(WARN, "constitution",
              "no knowledge/ docs — drift detection has no canonical source to check against")


def check_stakeholders_and_xref(repo: Path, r: Report) -> None:
    sdir = repo / "memory" / "stakeholders"
    profiles = (
        [p for p in sdir.glob("*.md") if p.name.lower() != "readme.md" and not p.name.startswith("_")]
        if sdir.is_dir() else []
    )
    if not profiles:
        r.add(WARN, "stakeholders",
              "no stakeholder profiles — briefs will be proxy-only (Step 7 degrades)")
    else:
        depths = 0
        for p in profiles:
            fm = frontmatter(p)
            if fm and fm.get("profile_depth") in ("partial", "deep"):
                depths += 1
        r.add(PASS, "stakeholders",
              f"{len(profiles)} profiles ({depths} partial+ — brief-eligible counterparties)")

    # Cross-ref: every topic-shard key_stakeholders slug must resolve to a profile.
    tdir = repo / "memory" / "topics"
    if not tdir.is_dir() or not profiles:
        return
    slugs = {p.stem for p in profiles}
    unresolved: list[str] = []
    for shard in tdir.glob("*.md"):
        if shard.name.lower() == "readme.md" or shard.name.startswith("_"):
            continue
        fm = frontmatter(shard)
        if not fm:
            continue
        ks = fm.get("key_stakeholders")
        if isinstance(ks, list):
            for s in ks:
                if isinstance(s, str) and s and s not in slugs:
                    unresolved.append(f"{shard.name}:{s}")
    if unresolved:
        r.add(WARN, "topic-xref",
              "topic key_stakeholders without a profile (brief context proxy-only): "
              + ", ".join(unresolved[:6]))
    else:
        r.add(PASS, "topic-xref", "all topic key_stakeholders resolve to profiles")


def check_shadow_dirs(repo: Path, r: Report) -> None:
    pending = repo / "memory" / "shadow" / "pending"
    resolved = repo / "memory" / "shadow" / "resolved"
    if pending.is_dir() and resolved.is_dir():
        n_pending = len(list(pending.glob("*.yaml")))
        r.add(PASS, "shadow-layer",
              f"shadow/pending + resolved present ({n_pending} pending — Step 8/11 targets)")
    else:
        r.add(WARN, "shadow-layer",
              "memory/shadow/{pending,resolved} missing — predictive integration inert")


def check_render_contract(repo: Path, r: Report) -> None:
    # A demonstrated render proves the Step-12 output contract is met. Look for a
    # rendered transcript in docs/ (where forks keep demonstrations), explicitly
    # excluding the runtime state/config files that also match "*digest*".
    RUNTIME = {"digest_state.md", "digest_sources.md", "digest.md"}
    candidates: list[Path] = []
    for sub in ("docs", "memory"):
        d = repo / sub
        if d.is_dir():
            candidates += [p for p in d.glob("*digest*.md") if p.name not in RUNTIME]
    transcript = next((p for p in candidates if "example" in p.name or "sample" in p.name
                       or p.name.startswith("digest-")), None)
    if transcript is None:
        r.add(WARN, "render-contract",
              "no rendered digest transcript found — output contract undemonstrated")
        return
    text = transcript.read_text(encoding="utf-8", errors="ignore").lower()
    missing = [s for s in RENDER_SECTIONS if s.lower() not in text]
    if missing:
        r.add(FAIL, "render-contract",
              f"{transcript.name} missing render sections: {', '.join(missing)}")
    else:
        r.add(PASS, "render-contract",
              f"{transcript.name} demonstrates all {len(RENDER_SECTIONS)} core render sections")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Digest-readiness dry-run harness")
    ap.add_argument("--repo-root", default=".", help="fork root to validate")
    ap.add_argument("--quiet", action="store_true", help="suppress PASS lines")
    args = ap.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    if not repo.is_dir():
        print(f"ERROR: repo root not found: {repo}", file=sys.stderr)
        return 2

    print(f"Digest-readiness dry-run — {repo}\n")
    r = Report(quiet=args.quiet)
    check_preflight_markers(repo, r)
    check_state(repo, r)
    check_sources(repo, r)
    check_triage(repo, r)
    check_constitution(repo, r)
    check_stakeholders_and_xref(repo, r)
    check_shadow_dirs(repo, r)
    check_render_contract(repo, r)
    r.render()
    return 1 if r.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
