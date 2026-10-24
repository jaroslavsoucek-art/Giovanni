#!/usr/bin/env python3
"""history/pii.py — identifiers out of anything that leaves the workspace.

The workspace holds raw chat history; the repo must not. Three layers, because
none of them alone is enough:

  1. Patterns — identifiers with a shape: e-mail, phone, IBAN, card number, plus
     the instance's own (`learning.history.pii_patterns`: a national ID, a court
     case number, a bank account in local notation…). Cheap, exact, blind to names.
  2. A denylist harvested from the export itself — names that appear after an
     honorific or a role word ("pan", "Mrs", "debtor", "JUDr."), and anything the
     principal adds by hand. Stored in the workspace (it is itself personal data)
     and matched with a short inflection tail, so "Novák" also catches "Nováka".
  3. The principal's review of every generated file before conversion — the only
     layer that understands context. The other two exist so that review is about
     judgement, not about spotting a birth number on line 40.

CLI:
  pii.py [--repo R] scan PATH... [--denylist F]   exit 1 if anything matched; values masked
  pii.py [--repo R] redact IN OUT [--denylist F]  copy IN to OUT with ⟨KIND⟩ tokens
  pii.py [--repo R] harvest [--workspace W]       (re)build <workspace>/denylist.txt from raw/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import gconfig  # noqa: E402

BUILTIN = [
    ("email", r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    # A bare 9-digit group is as often an amount ("150 000 000") as a phone number,
    # so a phone needs an international prefix or a phone word in front of it.
    ("phone", r"(?:\+\d{2,3}[ ]?\d{3}[ ]?\d{3}[ ]?\d{3,4}|(?i:tel\.?|telefon|mobil|phone)[ ]?:?[ ]?\d{3}[ ]?\d{3}[ ]?\d{3})(?![\d])"),
    ("iban", r"\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]{4}){3,7}(?:[ ]?[A-Z0-9]{1,4})?\b"),
    ("card", r"\b(?:\d{4}[ -]){3}\d{1,4}\b"),
]
UPPER = "A-ZÁÄČĎÉĚËÍĹĽŇÓÔÖŔŘŠŤÚŮÜÝŽ"
LOWER = "a-záäčďéěëíĺľňóôöŕřšťúůüýž"
NAME_WORD = f"[{UPPER}][{LOWER}]{{2,}}"
# Role / honorific words after which a capitalised word is very likely a person.
# Generic set; an instance adds its own through learning.history.name_cues.
CUES_DEFAULT = [
    "pan", "pana", "panu", "panem", "paní", "slečna", "slečny",
    "mr", "mrs", "ms", "dr", "judr", "mgr", "ing", "bc", "phdr", "mudr", "doc", "prof",
]
STOP_NAMES = {"Vážený", "Vážená", "Dobrý", "Dobrá", "Děkuji", "Prosím", "Dear", "Hello", "Thanks", "The",
              "Claude", "Anthropic"}


def _cfg(repo: Path) -> dict:
    return (gconfig.config(repo).get("learning") or {}).get("history") or {}


def patterns(repo: Path) -> list[tuple[str, re.Pattern]]:
    out = [(k, re.compile(rx)) for k, rx in BUILTIN]
    for item in _cfg(repo).get("pii_patterns") or []:
        if isinstance(item, dict) and item.get("regex"):
            out.append((str(item.get("name") or "custom"), re.compile(item["regex"])))
    return out


def workspace(repo: Path) -> Path:
    raw = _cfg(repo).get("workspace") or ".history"
    p = Path(raw).expanduser()
    return p if p.is_absolute() else repo / p


def denylist_path(repo: Path, explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    raw = _cfg(repo).get("denylist")
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_absolute() else repo / p
    return workspace(repo) / "denylist.txt"


def load_denylist(path: Path) -> list[re.Pattern]:
    out = []
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        word = line.split("#", 1)[0].strip()
        if len(word) < 3:
            continue
        stem = re.escape(word[:-1] if len(word) >= 6 else word)
        out.append(re.compile(rf"(?<![\w]){stem}\w{{0,4}}(?![\w])", re.IGNORECASE))
    return out


def mask(value: str) -> str:
    """Enough to find the hit in the file, not enough to read the identifier."""
    v = value.strip()
    return f"{v[:2]}…({len(v)})"


def find(text: str, pats, deny) -> list[tuple[str, str, int]]:
    hits = []
    for kind, rx in pats:
        for m in rx.finditer(text):
            hits.append((kind, m.group(0), m.start()))
    for rx in deny:
        for m in rx.finditer(text):
            hits.append(("name", m.group(0), m.start()))
    return hits


def redact(text: str, pats, deny) -> str:
    for kind, rx in pats:
        text = rx.sub(f"⟨{kind.upper()}⟩", text)
    for rx in deny:
        text = rx.sub("⟨JMÉNO⟩", text)
    return text


def harvest(repo: Path, ws: Path | None = None) -> Path:
    ws = ws or workspace(repo)
    cues = CUES_DEFAULT + [c.lower() for c in (_cfg(repo).get("name_cues") or [])]
    # Only the cue word is case-insensitive; the name itself must be capitalised,
    # or every "debtor pays …" would harvest "pays".
    cue_rx = re.compile(rf"(?<!\w)(?i:{'|'.join(re.escape(c) for c in cues)})[.:]?\s+({NAME_WORD})(?:\s+({NAME_WORD}))?")
    # Company names before a legal-form suffix: "Stavby Novák s.r.o." → Stavby, Novák
    corp_rx = re.compile(rf"((?:{NAME_WORD}\s+){{1,3}})(?:s\.\s?r\.\s?o\.|a\.\s?s\.|spol\.|k\.\s?s\.|v\.\s?o\.\s?s\.|GmbH|Ltd|Inc)")
    names: dict[str, int] = {}
    for f in sorted((ws / "raw").rglob("*")):
        if not f.is_file() or f.suffix not in (".md", ".txt", ".csv", ".html", ".json"):
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in cue_rx.finditer(text):
            for g in m.groups():
                if g and g not in STOP_NAMES:
                    names[g] = names.get(g, 0) + 1
        for m in corp_rx.finditer(text):
            for w in m.group(1).split():
                if w not in STOP_NAMES:
                    names[w] = names.get(w, 0) + 1
    manual = []
    out = denylist_path(repo)
    if out.is_file():
        manual = [ln for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip().endswith("# manual")]
    lines = ["# Harvested by pii.py harvest — personal data, never commit. Add your own lines with '# manual'."]
    lines += sorted({f"{n}" for n in names}) + manual
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def scan_paths(repo: Path, paths: list[Path], deny_file: Path) -> list[str]:
    pats, deny = patterns(repo), load_denylist(deny_file)
    findings = []
    for root in paths:
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for f in files:
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for kind, value, pos in find(text, pats, deny):
                line = text.count("\n", 0, pos) + 1
                findings.append(f"{f}:{line}: {kind} ({mask(value)})")
    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("paths", nargs="+")
    s.add_argument("--denylist")
    r = sub.add_parser("redact")
    r.add_argument("src")
    r.add_argument("dst")
    r.add_argument("--denylist")
    h = sub.add_parser("harvest")
    h.add_argument("--workspace")
    args = ap.parse_args(argv)
    repo = gconfig.repo_root(args.repo)
    if args.cmd == "harvest":
        out = harvest(repo, Path(args.workspace).expanduser() if args.workspace else None)
        n = sum(1 for ln in out.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#"))
        print(f"denylist: {n} entries → {out}")
        return 0
    deny_file = denylist_path(repo, getattr(args, "denylist", None))
    if args.cmd == "redact":
        text = Path(args.src).read_text(encoding="utf-8")
        Path(args.dst).write_text(redact(text, patterns(repo), load_denylist(deny_file)), encoding="utf-8")
        return 0
    findings = scan_paths(repo, [Path(p) for p in args.paths], deny_file)
    for f in findings:
        print(f)
    if not deny_file.is_file():
        print(f"note: no denylist at {deny_file} — names were not checked", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
