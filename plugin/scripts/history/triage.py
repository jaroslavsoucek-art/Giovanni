#!/usr/bin/env python3
"""history/triage.py — step 2a of /giovanni:learn-history: decide what is worth
reading, cheaply, before any model reads anything.

A year of chat history is hundreds of conversations; most are one-offs, some are
personal, a few are the same job done twenty times. Reading all of them with a
model costs a lot and surfaces mostly noise. This step is deterministic:

  1. Classify each conversation work / personal / unknown — keyword hits from
     `learning.history.work_keywords` / `personal_keywords`, project membership
     (`work_projects`, or every project when unset), and the principal's own
     overrides in <workspace>/overrides.yaml (id: work|personal|skip). Personal
     conversations are never clustered, sampled, summarised or shown — only
     counted.
  2. Cluster the work (and, with --include-unknown, unknown) conversations: a
     project is a cluster seed; within and across, TF-IDF cosine over title +
     the principal's own messages, greedy single pass, threshold `--threshold`.
  3. Rank clusters by repetition × effort (size × median human turns) and pick
     up to `--sample` conversations each (most recent first, then the longest)
     for the analyst agent. Clusters below `--min-size` are listed as singletons.

Output (<workspace>/triage/): clusters.json, workplan.json, triage.md — the last
one is for the principal and shows titles and terms with identifiers redacted.

Usage:
  triage.py [--repo R] [--threshold 0.22] [--min-size 2] [--sample 5] [--include-unknown]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import re
import statistics
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import gconfig  # noqa: E402
import pii  # noqa: E402

try:
    import yaml  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    yaml = None

STOP = set("""
a aby ale ani ano asi az až bez bude budu by byl byla bylo byly bych být co což či dal
další do ho i jak jako je jeho její jen jestli již jsem jsi jsme jste jsou k kde když
kterou který která které ku má mám máme mi mít mně mne mnou moc mohu muj můj my na nad
nám nás ne nebo něco není nic o od on ona ono oni pak po pod podle pokud pro proto
protože před při s se si sa tak také taky tam ten tento teď tím to toho tohle tom tu tuto
ty tyto u už v ve vám vás však všechno z za ze že jsem prosím děkuji díky můžeš můžete
napiš udělej potřebuji potřebuju chci chtěla chtěl dobrý den ahoj zdravím tady tedy
the and for with that this you your are was were have has can could would please
thanks hello hi need want make write what how about into from will just also
""".split())
TOKEN = re.compile(r"[^\W\d_]{3,}", re.UNICODE)


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))


def tokens(text: str, deny_folded: set[str]) -> list[str]:
    out = []
    for t in TOKEN.findall(text):
        f = fold(t)
        if f in STOP or any(f.startswith(d) for d in deny_folded):
            continue
        out.append(f[:7])  # crude stemming: Czech inflection lives in the tail
    return out


def tfidf(docs: list[list[str]]) -> list[dict[str, float]]:
    df = collections.Counter()
    for d in docs:
        df.update(set(d))
    n = len(docs) or 1
    vecs = []
    for d in docs:
        tf = collections.Counter(d)
        v = {t: (c / len(d)) * math.log((1 + n) / (1 + df[t])) for t, c in tf.items()} if d else {}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norm for t, x in v.items()})
    return vecs


def cos(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


def classify(row: dict, hcfg: dict, overrides: dict) -> str:
    if row["id"] in overrides:
        return str(overrides[row["id"]])
    work_projects = hcfg.get("work_projects")
    if row.get("project"):
        if work_projects is None or row["project"] in work_projects:
            return "work"
    text = fold(row.get("title", "") + " " + row.get("human_sample", ""))
    w = sum(1 for k in hcfg.get("work_keywords") or [] if fold(k) in text)
    p = sum(1 for k in hcfg.get("personal_keywords") or [] if fold(k) in text)
    if w >= 1 and w >= p:
        return "work"
    if p >= 1:
        return "personal"
    return "unknown"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo")
    ap.add_argument("--threshold", type=float, default=0.22)
    ap.add_argument("--min-size", type=int, default=2)
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--include-unknown", action="store_true")
    args = ap.parse_args(argv)

    repo = gconfig.repo_root(args.repo)
    hcfg = (gconfig.config(repo).get("learning") or {}).get("history") or {}
    ws = pii.workspace(repo)
    index = ws / "index.jsonl"
    if not index.is_file():
        raise SystemExit(f"{index} missing — run extract.py first")
    rows = [json.loads(ln) for ln in index.read_text(encoding="utf-8").splitlines() if ln.strip()]

    if not pii.denylist_path(repo).is_file():
        pii.harvest(repo, ws)
    deny = pii.load_denylist(pii.denylist_path(repo))
    deny_words = set()
    for ln in pii.denylist_path(repo).read_text(encoding="utf-8").splitlines():
        w = ln.split("#", 1)[0].strip()
        if len(w) >= 3:
            deny_words.add(fold(w)[:6])
    pats = pii.patterns(repo)

    overrides = {}
    ov = ws / "overrides.yaml"
    if ov.is_file() and yaml is not None:
        overrides = yaml.safe_load(ov.read_text(encoding="utf-8")) or {}

    for r in rows:
        r["class"] = classify(r, hcfg, overrides)
    counts = collections.Counter(r["class"] for r in rows)
    pool = [r for r in rows if r["class"] == "work" or (args.include_unknown and r["class"] == "unknown")]

    docs = [tokens(r["title"] + " " + r["title"] + " " + r["human_sample"], deny_words) for r in pool]
    vecs = tfidf(docs)
    clusters: list[dict] = []
    for r, v in sorted(zip(pool, vecs), key=lambda x: x[0]["created"]):
        best, best_sim = None, 0.0
        for c in clusters:
            sim = cos(v, c["centroid"])
            if r.get("project") and r["project"] == c.get("project"):
                sim += 0.35  # same project = same job, unless the text says otherwise
            if sim > best_sim:
                best, best_sim = c, sim
        if best is not None and best_sim >= args.threshold:
            best["members"].append(r)
            k = len(best["members"])
            keys = set(best["centroid"]) | set(v)
            best["centroid"] = {t: (best["centroid"].get(t, 0.0) * (k - 1) + v.get(t, 0.0)) / k for t in keys}
        else:
            clusters.append({"centroid": dict(v), "members": [r], "project": r.get("project") or ""})

    df_all = collections.Counter()
    for d in docs:
        df_all.update(set(d))
    out_clusters, singletons = [], []
    for c in clusters:
        m = c["members"]
        tf = collections.Counter()
        for r in m:
            tf.update(set(tokens(r["title"] + " " + r["human_sample"], deny_words)))
        terms = [t for t, _ in sorted(tf.items(), key=lambda x: (-x[1] * math.log((1 + len(docs)) / (1 + df_all[x[0]])), x[0]))[:6]]
        turns = [r["human_turns"] for r in m]
        entry = {
            "size": len(m), "project": c["project"], "terms": terms,
            "first": min(r["created"] for r in m), "last": max(r["created"] for r in m),
            "median_turns": statistics.median(turns), "artifacts": sum(r["artifacts"] for r in m),
            "attachment_types": sorted({t for r in m for t in r["attachment_types"]}),
            "score": round(len(m) * statistics.median(turns), 1),
            "members": [{"id": r["id"], "file": r["file"], "created": r["created"], "title": r["title"],
                         "human_turns": r["human_turns"], "artifacts": r["artifacts"]} for r in m],
        }
        (out_clusters if len(m) >= args.min_size else singletons).append(entry)
    out_clusters.sort(key=lambda e: (-e["score"], e["first"]))
    for i, c in enumerate(out_clusters, 1):
        c["id"] = f"c{i:02d}"
        recent = sorted(c["members"], key=lambda x: x["created"], reverse=True)
        longest = sorted(c["members"], key=lambda x: (x["human_turns"], x["artifacts"]), reverse=True)
        pick = []
        for x in recent[: max(1, args.sample - 2)] + longest:
            if x not in pick and len(pick) < args.sample:
                pick.append(x)
        c["sample"] = [x["file"] for x in pick]

    tdir = ws / "triage"
    tdir.mkdir(parents=True, exist_ok=True)
    (tdir / "clusters.json").write_text(json.dumps({"clusters": out_clusters, "singletons": singletons},
                                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    projects_dir = ws / "raw/projects"
    workplan = {
        "workspace": str(ws),
        "clusters": [{"id": c["id"], "size": c["size"], "project": c["project"], "terms": c["terms"],
                      "first": c["first"], "last": c["last"], "sample": c["sample"],
                      "project_instructions": next((str(p.relative_to(ws)) for p in sorted(projects_dir.glob("*/instructions.md"))
                                                    if c["project"] and p.read_text(encoding="utf-8").startswith(f"# {c['project']}\n")), None),
                      "spec": f"specs/{c['id']}.yaml"} for c in out_clusters],
    }
    (tdir / "workplan.json").write_text(json.dumps(workplan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def red(s: str) -> str:
        return pii.redact(s, pats, deny)

    lang = str(hcfg.get("language") or "en")
    TABLES = {
        "en": dict(title="Chat history triage", conv="Conversations", work="work", personal="personal",
                   personal_note="(never read, only counted)", unknown="unclassified", inc="(included)",
                   exc="(left out; `--include-unknown` adds them)", rec="Recurring jobs", single="one-offs",
                   cols="| # | Conversations | Span | Project | Typical terms | Artifacts | Example title |",
                   fix="To fix a classification, write `<conversation id>: work|personal|skip` into `overrides.yaml` and run triage again.",
                   idnote="The conversation id is in the file name under `raw/conversations/` (the part after the date)."),
        "cs": dict(title="Triáž historie konverzací", conv="Konverzací", work="pracovní", personal="osobní",
                   personal_note="(nečtou se, jen počítají)", unknown="nezařazené", inc="(zahrnuté)",
                   exc="(vynechané; `--include-unknown` je přidá)", rec="Opakované úlohy", single="jednorázové",
                   cols="| # | Konverzací | Období | Projekt | Typické výrazy | Artefakty | Příklad názvu |",
                   fix="Oprava zařazení: do `overrides.yaml` napiš `<id konverzace>: work|personal|skip` a spusť triáž znovu.",
                   idnote="Id konverzace je v názvu souboru v `raw/conversations/` (část za datem)."),
    }
    T = TABLES.get(lang, TABLES["en"])
    md = [f"# {T['title']}", "",
          f"{T['conv']}: **{len(rows)}** · {T['work']} {counts.get('work', 0)} · {T['personal']} {counts.get('personal', 0)} "
          f"{T['personal_note']} · {T['unknown']} {counts.get('unknown', 0)} " + (T["inc"] if args.include_unknown else T["exc"]), "",
          f"{T['rec']} (≥ {args.min_size}): **{len(out_clusters)}** · {T['single']}: {len(singletons)}", "",
          T["cols"], "|---|---|---|---|---|---|---|"]
    for c in out_clusters:
        md.append(f"| {c['id']} | {c['size']} | {c['first']} → {c['last']} | {red(c['project']) or '—'} | "
                  f"{', '.join(c['terms'])} | {c['artifacts']} | {red(c['members'][-1]['title'])[:60]} |")
    md += ["", T["fix"], T["idnote"], ""]
    (tdir / "triage.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(rows)} conversations: work {counts.get('work', 0)}, personal {counts.get('personal', 0)}, "
          f"unknown {counts.get('unknown', 0)} → {len(out_clusters)} clusters, {len(singletons)} singletons → {tdir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
