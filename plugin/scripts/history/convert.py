#!/usr/bin/env python3
"""history/convert.py — steps 2b–3 of /giovanni:learn-history: specs → review →
skills, house style and provenance in the repo.

  review   Collect <workspace>/specs/*.yaml into review/review.md (for the
           principal) and review/decisions.yaml (one entry per spec, decision
           `pending`). Re-running keeps decisions already made.
  apply    For every decision skill / knowledge / merge-into: render the files
           into <workspace>/staging/ first, PII-scan the staging tree, and only
           when it is clean copy it into the repo. A file that already exists in
           the repo is never overwritten — the new version lands beside it as
           `<name>.proposed`. Writes a provenance note (ids and counts, no
           content) to memory/learning/history-<date>.md.
  package  Zip each learned skill for upload to the chat app, renamed `<slug>-web`
           so the uploaded copy and the repo copy never collide by name when the
           chat app syncs skills back into Claude Code.

Decisions in review/decisions.yaml:
  skill        new skill under .claude/skills/<slug>/ (SKILL.md + format.md)
  knowledge    rules + style appended to the house-style doc (learning.history.house_style)
  merge-into   references/learned-<slug>.md inside an existing skill + one pointer line
  ignore       nothing
  pending      not decided yet — skipped by apply

Usage:
  convert.py [--repo R] review
  convert.py [--repo R] apply [--only c01,c03] [--dry-run]
  convert.py [--repo R] package
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import gconfig  # noqa: E402
import pii  # noqa: E402

try:
    import yaml  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    print("convert.py needs PyYAML", file=sys.stderr)
    sys.exit(2)

DECISIONS = ("skill", "knowledge", "merge-into", "ignore", "pending")
MARK_START = "<!-- giovanni:learned-skills -->"
MARK_END = "<!-- /giovanni:learned-skills -->"

L = {
    "en": dict(when="When to use", need="What I need", steps="Steps", fmt="Output format", rules="Rules (from your corrections)",
               refs="Grounding", limits="Limits", open="Open questions", kind="Kind", lang="Language", length="Length",
               structure="Structure", style="Style", exemplar="Exemplar", gen="Generated from chat history",
               gen_tail="Edit it as you like; the learning loop never overwrites this file.",
               never="Nothing is sent, filed or submitted from here — the output is a draft for you.",
               use_when="Use when", review_title="Proposed skills from chat history", conv="conversations",
               house="House style (learned from chat history)", learned="Learned skills",
               project="From the chat-app project (instructions and templates)"),
    "cs": dict(when="Kdy použít", need="Co potřebuju", steps="Postup", fmt="Formát výstupu", rules="Pravidla (z tvých oprav)",
               refs="Opory", limits="Hranice", open="Otevřené otázky", kind="Druh", lang="Jazyk", length="Délka",
               structure="Struktura", style="Styl", exemplar="Vzor", gen="Vygenerováno z historie konverzací",
               gen_tail="Uprav si ho podle sebe; učící smyčka tenhle soubor nikdy nepřepíše.",
               never="Odsud se nic neodesílá, nepodává ani nevkládá do systémů — výstup je návrh pro tebe.",
               use_when="Použij, když", review_title="Navržené skilly z historie konverzací", conv="konverzací",
               house="Styl kanceláře (naučeno z historie konverzací)", learned="Naučené skilly",
               project="Z projektu v claude.ai (instrukce a vzory)"),
}


def hcfg(repo: Path) -> dict:
    return (gconfig.config(repo).get("learning") or {}).get("history") or {}


def labels(repo: Path) -> dict:
    return L.get(str(hcfg(repo).get("language") or "en"), L["en"])


def load_specs(ws: Path) -> list[dict]:
    specs = []
    for p in sorted((ws / "specs").glob("*.yaml")):
        try:
            data = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"WARNING: {p.name} is not valid YAML — skipped ({e})", file=sys.stderr)
            continue
        if isinstance(data, dict) and data.get("id"):
            data["_file"] = str(p.relative_to(ws))
            specs.append(data)
    return specs


def slugify(s: str) -> str:
    import unicodedata
    s = "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48] or "skill"


def lst(v) -> list:
    if v is None:
        return []
    return [clean(x) if isinstance(x, str) else x for x in (v if isinstance(v, list) else [v])]


_EVIDENCE = re.compile(r"\s*\((?:[0-9a-z]{8}(?:,\s*)?)+\)")


def clean(text: str) -> str:
    """Evidence ids belong in the spec and the provenance note, not in the skill
    the principal reads every day: "(a1b2c3d4, e5f6a7b8)" is stripped on render."""
    return _EVIDENCE.sub("", text).strip()


# ------------------------------------------------------------------ review

def cmd_review(repo: Path, ws: Path) -> int:
    lb = labels(repo)
    specs = load_specs(ws)
    if not specs:
        raise SystemExit(f"no specs in {ws / 'specs'} — run the analysts first")
    rdir = ws / "review"
    rdir.mkdir(parents=True, exist_ok=True)
    dpath = rdir / "decisions.yaml"
    old = yaml.safe_load(dpath.read_text(encoding="utf-8")) if dpath.is_file() else {}
    old = old or {}
    pats, deny = pii.patterns(repo), pii.load_denylist(pii.denylist_path(repo))
    decisions, md = {}, [f"# {lb['review_title']}", ""]
    for s in sorted(specs, key=lambda x: (-int((x.get("frequency") or {}).get("conversations") or 0), x["id"])):
        prev = old.get(s["id"]) or {}
        decisions[s["id"]] = {
            "name": s.get("name") or "",
            "proposal": s.get("decision_proposal") or "skill",
            "decision": prev.get("decision") if prev.get("decision") in DECISIONS else "pending",
            "slug": prev.get("slug") or slugify(s.get("slug") or s.get("name") or s["id"]),
        }
        if (s.get("decision_proposal") == "merge-into") or prev.get("merge_target"):
            decisions[s["id"]]["merge_target"] = prev.get("merge_target") or s.get("merge_target") or ""
        f = s.get("frequency") or {}
        hits = pii.find((ws / s["_file"]).read_text(encoding="utf-8"), pats, deny)
        of = s.get("output_format") or {}
        md += [f"## {s['id']} · {s.get('name', '')}", "",
               f"- **{f.get('conversations', '?')} {lb['conv']}** ({f.get('first', '?')} → {f.get('last', '?')}), "
               f"confidence **{s.get('confidence', '?')}**, automation {s.get('automation', '?')}",
               f"- Proposal: **{s.get('decision_proposal', '?')}**"
               + (f" → `{s.get('merge_target')}`" if s.get("merge_target") else "") + f" — {s.get('decision_reason', '')}",
               f"- Skill: `{decisions[s['id']]['slug']}`",
               f"- {lb['when']}: " + "; ".join(f"„{t}“" for t in lst(s.get("trigger_phrases"))[:4]),
               f"- {lb['fmt']}: {of.get('kind', '?')}, {of.get('length', '?')} — " + " → ".join(lst(of.get("structure"))[:8]),
               ]
        rules = lst(s.get("rules_from_corrections"))
        if rules:
            md.append(f"- {lb['rules']}:")
            md += [f"  - {r.get('rule') if isinstance(r, dict) else r}" for r in rules[:6]]
        if lst(s.get("open_questions")):
            md.append(f"- {lb['open']}:")
            md += [f"  - {q}" for q in lst(s.get("open_questions"))]
        md.append(f"- PII check of the spec: {'**' + str(len(hits)) + ' hit(s) — fix the spec before apply**' if hits else 'clean'}")
        md += [f"- Spec: `{s['_file']}`", ""]
    header = ("# decision per proposal: skill | knowledge | merge-into | ignore | pending\n"
              "# slug = skill name; merge_target = existing skill (merge-into only)\n")
    dpath.write_text(header + yaml.safe_dump(decisions, allow_unicode=True, sort_keys=True), encoding="utf-8")
    (rdir / "review.md").write_text("\n".join(md), encoding="utf-8")
    print(f"{len(specs)} specs → {rdir / 'review.md'} · decisions in {dpath}")
    return 0


# ------------------------------------------------------------------ render

def render_skill(s: dict, slug: str, lb: dict, today: str) -> tuple[str, str]:
    f = s.get("frequency") or {}
    of = s.get("output_format") or {}
    triggers = lst(s.get("trigger_phrases"))
    desc = (s.get("summary") or s.get("name") or slug).strip().replace("\n", " ")
    if triggers:
        desc += f" {lb['use_when']}: " + "; ".join(f"„{t}“" for t in triggers[:5]) + "."
    desc = desc[:1000]
    fm = {"name": slug, "description": desc,
          "metadata": {"generated_from": f"chat-history {s['id']}", "generated": today,
                       "evidence_conversations": int(f.get("conversations") or 0)}}
    out = ["---", yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip(), "---", "",
           f"# {s.get('name') or slug}", "", (s.get("summary") or "").strip(), "",
           f"> {lb['gen']} ({s['id']}, {f.get('conversations', '?')} {lb['conv']}, {f.get('first', '?')} → {f.get('last', '?')}). {lb['gen_tail']}", ""]
    if triggers:
        out += [f"## {lb['when']}", ""] + [f"- „{t}“" for t in triggers] + [""]
    if lst(s.get("inputs")):
        out += [f"## {lb['need']}", ""] + [f"- {x}" for x in lst(s.get("inputs"))] + [""]
    if lst(s.get("steps")):
        out += [f"## {lb['steps']}", ""] + [f"{i}. {x}" for i, x in enumerate(lst(s.get("steps")), 1)] + [""]
    out += [f"## {lb['fmt']}", "",
            f"- {lb['kind']}: {of.get('kind', '?')} · {lb['lang']}: {of.get('language', '?')} · {lb['length']}: {of.get('length', '?')}"]
    if lst(of.get("structure")):
        out += [f"- {lb['structure']}:"] + [f"  {i}. {x}" for i, x in enumerate(lst(of.get("structure")), 1)]
    if lst(of.get("style")):
        out += [f"- {lb['style']}:"] + [f"  - {x}" for x in lst(of.get("style"))]
    if of.get("exemplar"):
        out.append(f"- {lb['exemplar']}: [format.md](format.md)")
    out.append("")
    rules = lst(s.get("rules_from_corrections"))
    if rules:
        out += [f"## {lb['rules']}", ""]
        out += [f"- {clean(str(r.get('rule') if isinstance(r, dict) else r))}" for r in rules] + [""]
    refs = lst(s.get("knowledge_refs")) + lst(s.get("tools_and_sources"))
    if refs:
        out += [f"## {lb['refs']}", ""] + [f"- {x}" for x in refs] + [""]
    out += [f"## {lb['limits']}", ""] + [f"- {x}" for x in lst(s.get("risks"))] + [f"- {lb['never']}", ""]
    if lst(s.get("open_questions")):
        out += [f"## {lb['open']}", ""] + [f"- {q}" for q in lst(s.get("open_questions"))] + [""]
    fmt = ""
    if of.get("exemplar"):
        fmt = f"# {lb['exemplar']} — {s.get('name') or slug}\n\n```text\n{str(of['exemplar']).rstrip()}\n```\n"
    return "\n".join(out), fmt


def render_knowledge(s: dict, lb: dict, today: str) -> str:
    of = s.get("output_format") or {}
    out = [f"## {s.get('name') or s['id']} {{#learned-{slugify(s.get('slug') or s['id'])}}}", "",
           f"<!-- chat-history {s['id']}, {today} -->", ""]
    out += [f"- {clean(str(r.get('rule') if isinstance(r, dict) else r))}" for r in lst(s.get("rules_from_corrections"))]
    out += [f"- {x}" for x in lst(of.get("style"))]
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ apply

def project_refs(ws: Path, cid: str) -> list[tuple[str, str]]:
    """A cluster seeded by a chat-app project brings that project's instructions
    and knowledge docs — usually the principal's own templates, i.e. the output
    format in its purest form. In Claude Code there is no project around the
    skill, so they travel with it, through the same PII gate as everything else."""
    wp = ws / "triage" / "workplan.json"
    if not wp.is_file():
        return []
    import json
    for c in json.loads(wp.read_text(encoding="utf-8")).get("clusters", []):
        if c.get("id") != cid or not c.get("project_instructions"):
            continue
        inst = ws / c["project_instructions"]
        out = [("project-instructions.md", inst.read_text(encoding="utf-8"))] if inst.is_file() else []
        docs = inst.parent / "docs"
        if docs.is_dir():
            out += [(d.name, d.read_text(encoding="utf-8", errors="replace")) for d in sorted(docs.iterdir()) if d.is_file()]
        return out
    return []


def cmd_apply(repo: Path, ws: Path, only: set[str] | None, dry: bool) -> int:
    lb, cfg = labels(repo), hcfg(repo)
    dpath = ws / "review" / "decisions.yaml"
    if not dpath.is_file():
        raise SystemExit("no review/decisions.yaml — run `convert.py review` first")
    decisions = yaml.safe_load(dpath.read_text(encoding="utf-8")) or {}
    specs = {s["id"]: s for s in load_specs(ws)}
    today = dt.date.today().isoformat()
    stage = ws / "staging" / today
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    house_rel = cfg.get("house_style") or "knowledge/house-style.md"
    plan, house_parts, learned_rows = [], [], []
    for cid, d in sorted(decisions.items()):
        if only and cid not in only:
            continue
        dec = (d or {}).get("decision")
        if dec not in ("skill", "knowledge", "merge-into") or cid not in specs:
            continue
        s, slug = specs[cid], slugify(d.get("slug") or cid)
        if dec == "skill":
            refs = project_refs(ws, cid)
            skill_md, fmt = render_skill(s, slug, lb, today)
            if refs:
                skill_md = skill_md.rstrip() + f"\n\n## {lb['project']}\n\n" + "\n".join(
                    f"- [references/{name}](references/{name})" for name, _ in refs) + "\n"
            plan.append((f".claude/skills/{slug}/SKILL.md", skill_md))
            if fmt:
                plan.append((f".claude/skills/{slug}/format.md", fmt))
            for name, text in refs:
                plan.append((f".claude/skills/{slug}/references/{name}", text))
            learned_rows.append((slug, s))
        elif dec == "merge-into":
            target = d.get("merge_target") or s.get("merge_target")
            if not target or not (repo / ".claude/skills" / target / "SKILL.md").is_file():
                print(f"{cid}: merge target `{target}` is not a skill in this repo — skipped", file=sys.stderr)
                continue
            skill_md, fmt = render_skill(s, slug, lb, today)
            body = skill_md.split("---", 2)[2].lstrip() + ("\n" + fmt if fmt else "")
            plan.append((f".claude/skills/{target}/references/learned-{slug}.md", body))
        else:
            house_parts.append(render_knowledge(s, lb, today))
    if house_parts:
        existing = (repo / house_rel).read_text(encoding="utf-8") if (repo / house_rel).is_file() else f"# {lb['house']}\n\n"
        plan.append((house_rel, existing.rstrip() + "\n\n" + "\n".join(house_parts)))
    if not plan:
        print("nothing to apply — no decision is skill / knowledge / merge-into")
        return 0
    for rel, text in plan:
        p = stage / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    findings = pii.scan_paths(repo, [stage], pii.denylist_path(repo))
    if findings:
        print("PII gate: staging is NOT clean — nothing was copied into the repo:")
        for f in findings:
            print("  " + f.replace(str(stage) + "/", ""))
        print("Fix the spec (or the decision), re-run review + apply. The staged files are in " + str(stage))
        print("A `name` hit on an ordinary word is a false positive: delete that line from "
              f"{pii.denylist_path(repo)} (lines you add yourself end with '# manual').")
        return 1
    if dry:
        print(f"dry run — staging clean, {len(plan)} file(s) in {stage}")
        return 0
    written, proposed = [], []
    for rel, _text in plan:
        src, dst = stage / rel, repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and rel != house_rel:
            dst = dst.with_name(dst.name + ".proposed")
            proposed.append(str(dst.relative_to(repo)))
        shutil.copyfile(src, dst)
        written.append(str(dst.relative_to(repo)))
    for cid, d in decisions.items():
        if (d or {}).get("decision") == "merge-into" and (not only or cid in only):
            target = d.get("merge_target") or (specs.get(cid) or {}).get("merge_target")
            sk = repo / ".claude/skills" / str(target) / "SKILL.md"
            line = f"- Learned from chat history: [references/learned-{slugify(d.get('slug') or cid)}.md](references/learned-{slugify(d.get('slug') or cid)}.md)"
            if sk.is_file() and line not in sk.read_text(encoding="utf-8"):
                sk.write_text(sk.read_text(encoding="utf-8").rstrip() + "\n\n" + line + "\n", encoding="utf-8")
                written.append(str(sk.relative_to(repo)))
    claude_md = repo / "CLAUDE.md"
    if learned_rows and claude_md.is_file():
        text = claude_md.read_text(encoding="utf-8")
        if MARK_START in text and MARK_END in text:
            head, rest = text.split(MARK_START, 1)
            block, tail = rest.split(MARK_END, 1)
            rows = [ln for ln in block.strip().splitlines() if ln.startswith("| `")]
            have = {r.split("`")[1] for r in rows}
            for slug, s in learned_rows:
                if slug not in have:
                    t = lst(s.get("trigger_phrases"))
                    rows.append(f"| `{slug}` | {('„' + t[0] + '“') if t else ''} | {(s.get('output_format') or {}).get('kind', '')} | {s['id']} |")
            hdr = "| Skill | Typical ask | Output | Source |\n|---|---|---|---|"
            claude_md.write_text(head + MARK_START + "\n" + hdr + "\n" + "\n".join(sorted(rows)) + "\n" + MARK_END + tail, encoding="utf-8")
            written.append("CLAUDE.md")
        else:
            print(f"note: CLAUDE.md has no {MARK_START} block — learned skills not listed there")
    prov = repo / "memory/learning" / f"history-{today}.md"
    prov.parent.mkdir(parents=True, exist_ok=True)
    manifest = ws / "manifest.json"
    lines = [f"# Chat-history learning run {today}", "",
             f"- Export extracted: {yaml.safe_load(manifest.read_text()).get('extracted_at') if manifest.is_file() else '?'}",
             "- Decisions (cluster → decision → target; ids and counts only, no content):", ""]
    for cid, d in sorted(decisions.items()):
        s = specs.get(cid) or {}
        lines.append(f"  - {cid} · {(s.get('frequency') or {}).get('conversations', '?')} conv · "
                     f"{(d or {}).get('decision')} → {(d or {}).get('merge_target') or (d or {}).get('slug')} · "
                     f"evidence {', '.join(lst(s.get('evidence'))[:8])}")
    prov.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(str(prov.relative_to(repo)))
    print("written:\n  " + "\n  ".join(written))
    if proposed:
        print("existing files kept; new versions beside them:\n  " + "\n  ".join(proposed))
    return 0


# ------------------------------------------------------------------ package

def cmd_package(repo: Path, ws: Path) -> int:
    out = ws / "claude-ai"
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for sk in sorted((repo / ".claude/skills").glob("*/SKILL.md")):
        text = sk.read_text(encoding="utf-8")
        if "generated_from: chat-history" not in text:
            continue
        slug = sk.parent.name
        web = f"{slug}-web"
        text = re.sub(r"(?m)^name:\s*.+$", f"name: {web}", text, count=1)
        with zipfile.ZipFile(out / f"{web}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(f"{web}/SKILL.md", text)
            for extra in sorted(sk.parent.rglob("*")):
                if extra.is_file() and extra.name != "SKILL.md" and not extra.name.endswith(".proposed"):
                    zf.write(extra, f"{web}/{extra.relative_to(sk.parent)}")
        n += 1
    print(f"{n} skill package(s) → {out}")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("review")
    a = sub.add_parser("apply")
    a.add_argument("--only")
    a.add_argument("--dry-run", action="store_true")
    sub.add_parser("package")
    args = ap.parse_args(argv)
    repo = gconfig.repo_root(args.repo)
    ws = pii.workspace(repo)
    if args.cmd == "review":
        return cmd_review(repo, ws)
    if args.cmd == "apply":
        return cmd_apply(repo, ws, set(args.only.split(",")) if args.only else None, args.dry_run)
    return cmd_package(repo, ws)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
