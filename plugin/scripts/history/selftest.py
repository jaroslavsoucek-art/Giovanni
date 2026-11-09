#!/usr/bin/env python3
"""history/selftest.py — end-to-end self-test of /giovanni:learn-history's scripts.

Builds a synthetic claude.ai export (fake people, fake identifiers, a personal
chat, a project with instructions, artifacts, corrections), runs extract →
harvest → triage → review → apply → package against a throwaway git repo, and
asserts the properties that matter: titles never in file names, personal chats
never clustered, identifiers redacted from the triage page, the PII gate blocks
a dirty spec and copies nothing, apply never overwrites, the lint rule catches a
tracked workspace. The model step (giovanni:history-analyst) is replaced by two
hand-written specs — one clean, one leaking a birth number.

Run: python3 plugin/scripts/history/selftest.py   (exit 0 = pass)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parents[1]
PY = sys.executable
FAILS: list[str] = []

CONFIG = """
learning:
  history:
    workspace: .history
    language: cs
    domain_hint: Asistentka insolvenčního správce; oddlužení a konkurzy.
    work_keywords: [oddlužení, přihlášk, pohledávk, insolven, dlužník, věřitel, ISIR, spis]
    personal_keywords: [recept, dovolen, narozenin]
    name_cues: [dlužník, dlužnice, dlužníka, věřitel]
    pii_patterns:
      - {name: rodne-cislo, regex: '\\b\\d{6}/?\\d{3,4}\\b'}
      - {name: spisova-znacka, regex: '\\b[A-Z]{2,4}\\s?\\d{1,3}\\s?INS\\s?\\d+/\\d{4}\\b'}
    house_style: knowledge/styl.md
"""


def check(cond: bool, label: str) -> None:
    print(("  ok    " if cond else "  FAIL  ") + label)
    if not cond:
        FAILS.append(label)


def msg(sender: str, text: str, ts: str, artifact: dict | None = None, attach: str | None = None) -> dict:
    content = [{"type": "text", "text": text}]
    if artifact:
        content.append({"type": "tool_use", "name": "artifacts", "input": artifact})
    m = {"uuid": os.urandom(8).hex(), "text": text, "content": content, "sender": sender,
         "created_at": ts, "updated_at": ts, "attachments": [], "files": []}
    if attach:
        m["attachments"] = [{"file_name": "vypis.pdf", "file_type": "pdf", "file_size": 10, "extracted_content": attach}]
    return m


def conv(uuid: str, name: str, day: str, msgs: list[dict], project: str | None = None) -> dict:
    c = {"uuid": uuid, "name": name, "summary": "", "created_at": f"{day}T09:00:00Z",
         "updated_at": f"{day}T10:00:00Z", "account": {"uuid": "acc"}, "chat_messages": msgs}
    if project:
        c["project_uuid"] = project
    return c


def build_export(dst: Path) -> Path:
    proj = "11111111-aaaa-bbbb-cccc-000000000001"
    zprava = []
    for i, (day, jmeno) in enumerate([("2026-03-02", "Jan Testovací"), ("2026-05-11", "Eva Zkušební"),
                                      ("2026-09-30", "Petr Ukázkový")], 1):
        t = f"{day}T09:0{i}:00Z"
        zprava.append(conv(f"a000000{i}-0000-0000-0000-00000000000{i}", f"Zpráva o plnění – {jmeno}", day, [
            msg("human", f"Napiš zprávu o plnění oddlužení, dlužník pan {jmeno.split()[1]}, "
                         f"r.č. 80010{i}/123{i}, spis KSBR 99 INS 1234{i}/2025. Splátky v příloze.", t,
                attach="leden 3 000 Kč, únor 3 000 Kč, březen 0 Kč"),
            msg("assistant", "Zde je návrh zprávy.", t, artifact={
                "id": f"zp{i}", "type": "text/markdown", "title": "Zpráva o plnění oddlužení", "command": "create",
                "content": f"# Zpráva o plnění oddlužení\n\nDlužník: {jmeno}\n\n## 1. Přehled splátek\n| Měsíc | Částka |\n\n## 2. Hodnocení\nDlužník plní dle § 412 IZ."}),
            msg("human", "ne, citaci vždy celou: § 412 odst. 1 písm. f) IZ, a datum piš 1. 1. 2026", t),
            msg("assistant", "Opraveno.", t, artifact={
                "id": f"zp{i}", "type": "text/markdown", "title": "Zpráva o plnění oddlužení", "command": "update",
                "content": "# Zpráva o plnění oddlužení\n\n## 1. Přehled splátek\n\n## 2. Hodnocení\n§ 412 odst. 1 písm. f) IZ"}),
            msg("human", "díky, super", t),
        ], project=proj))
    prihl = [conv(f"b000000{i}-0000-0000-0000-00000000000{i}", f"Kontrola přihlášky {i}", day, [
        msg("human", f"Zkontroluj přihlášku pohledávky věřitele Banka Fiktivní a.s., IČO 1234567{i}, "
                     "jestli sedí jistina a příslušenství s úvěrovou smlouvou.", f"{day}T11:00:00Z"),
        msg("assistant", "Jistina sedí, příslušenství je nadhodnocené o úrok z prodlení.", f"{day}T11:01:00Z"),
        msg("human", "výsledek vždy jako tabulku: položka | přihlášeno | doloženo | rozdíl", f"{day}T11:02:00Z"),
        msg("assistant", "| položka | přihlášeno | doloženo | rozdíl |", f"{day}T11:03:00Z"),
    ]) for i, day in [(1, "2026-04-14"), (2, "2026-07-21"), (3, "2026-10-01")]]
    personal = conv("c0000001-0000-0000-0000-000000000001", "Svíčková", "2026-06-06", [
        msg("human", "dej mi recept na svíčkovou pro 6 lidí", "2026-06-06T18:00:00Z"),
        msg("assistant", "Ingredience: …", "2026-06-06T18:01:00Z")])
    oneoff = conv("d0000001-0000-0000-0000-000000000001", "Odměna správce", "2026-02-02", [
        msg("human", "spočítej odměnu správce v oddlužení za 36 měsíců", "2026-02-02T08:00:00Z"),
        msg("assistant", "…", "2026-02-02T08:01:00Z")])
    empty = conv("e0000001-0000-0000-0000-000000000001", "", "2026-01-01", [])
    projects = [{"uuid": proj, "name": "Oddlužení – zprávy", "description": "Zprávy o plnění",
                 "prompt_template": "Píšeš zprávy o plnění oddlužení pro insolvenční soud. Formálně, třetí osoba.",
                 "is_private": True, "is_starter_project": False, "created_at": "2026-01-10T00:00:00Z",
                 "updated_at": "2026-01-10T00:00:00Z", "docs": [{"uuid": "d1", "filename": "vzor zpravy.md",
                                                                "content": "# Vzor\n## 1. Přehled splátek\n## 2. Hodnocení"}]}]
    src = dst / "export"
    src.mkdir()
    (src / "conversations.json").write_text(json.dumps(zprava + prihl + [personal, oneoff, empty], ensure_ascii=False))
    (src / "projects.json").write_text(json.dumps(projects, ensure_ascii=False))
    (src / "users.json").write_text(json.dumps([{"uuid": "acc", "full_name": "Testovací Uživatelka"}], ensure_ascii=False))
    z = dst / "data-2026-10-23.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for f in src.iterdir():
            zf.write(f, f.name)
    return z


CLEAN_SPEC = """id: c01
slug: zprava-o-plneni-oddluzeni
name: Zpráva o plnění oddlužení
summary: Pravidelná zpráva soudu o tom, jak dlužník plní oddlužení, z výpisu splátek.
frequency: {conversations: 3, sampled: 3, first: 2026-03-02, last: 2026-09-30}
trigger_phrases: ["napiš zprávu o plnění oddlužení", "zpráva o plnění za <OBDOBÍ>"]
inputs: ["výpis splátek za období (pdf)"]
steps: ["Sečti splátky po měsících", "Porovnej se splátkovým kalendářem", "Napiš hodnocení s citací"]
output_format:
  kind: document
  language: cs
  structure: ["Záhlaví se spisovou značkou <SPISOVÁ ZNAČKA>", "1. Přehled splátek (tabulka)", "2. Hodnocení"]
  style: ["formálně, třetí osoba", "datum ve tvaru 1. 1. 2026"]
  length: "1 strana"
  exemplar: |
    # Zpráva o plnění oddlužení
    Dlužník: <DLUŽNÍK>
    ## 1. Přehled splátek
    | Měsíc | Částka |
    ## 2. Hodnocení
    Dlužník plní podle § 412 odst. 1 písm. f) IZ.
rules_from_corrections:
  - {rule: "Citace zákona vždy celá: paragraf, odstavec, písmeno.", evidence: [a0000001], confidence: high}
knowledge_refs: ["§ 412 IZ"]
tools_and_sources: ["výpis z účtu"]
automation: assisted
risks: ["chybná citace", "přehlédnutá chybějící splátka"]
decision_proposal: skill
decision_reason: "Opakuje se třikrát se stejnou strukturou."
confidence: high
open_questions: []
evidence: [a0000001, a0000002, a0000003]
"""
DIRTY_SPEC = """id: c02
slug: kontrola-prihlasky
name: Kontrola přihlášky pohledávky
summary: Kontrola přihlášky proti smlouvě.
frequency: {conversations: 3, sampled: 3, first: 2026-04-14, last: 2026-10-01}
trigger_phrases: ["zkontroluj přihlášku pohledávky"]
output_format:
  kind: table
  exemplar: |
    Dlužník Testovací, r.č. 800101/1231
decision_proposal: skill
confidence: medium
evidence: [b0000001]
"""


def run(args, cwd, env=None, expect=0, label=""):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if expect is not None and r.returncode != expect:
        print(r.stdout[-1500:], r.stderr[-1500:])
    check(expect is None or r.returncode == expect, f"{label} (exit {r.returncode}, expected {expect})")
    return r


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="giovanni-history-selftest-") as tmp:
        tmp = Path(tmp)
        repo = tmp / "instance"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        (repo / "docs").mkdir()
        (repo / "docs/governance.config.yaml").write_text(CONFIG, encoding="utf-8")
        (repo / ".gitignore").write_text(".history/\n", encoding="utf-8")
        (repo / "CLAUDE.md").write_text("# Instance\n\n## Naučené skilly\n\n<!-- giovanni:learned-skills -->\n<!-- /giovanni:learned-skills -->\n", encoding="utf-8")
        env = dict(os.environ, GIOVANNI_REPO_ROOT=str(repo))
        export = build_export(tmp)
        H = PLUGIN / "scripts/history"
        ws = repo / ".history"

        print("extract")
        run([PY, str(H / "extract.py"), str(export), "--inspect"], repo, env, label="--inspect runs")
        check(not ws.exists(), "--inspect writes nothing")
        run([PY, str(H / "extract.py"), str(export)], repo, env, label="extract")
        man = json.loads((ws / "manifest.json").read_text())
        check(man["conversations"] == 8 and man["skipped_empty"] == 1, "8 conversations, 1 empty skipped")
        check(man["projects"] == 1 and man["artifacts"] == 6, "1 project, 6 artifacts")
        names = " ".join(p.name for p in (ws / "raw/conversations").iterdir())
        check("Testovac" not in names and "Svíčk" not in names, "titles never in file names")
        check((ws / "raw/projects/11111111/instructions.md").read_text().count("třetí osoba") == 1, "project instructions extracted")
        check(not (ws / "raw/users.json").exists(), "account data not copied")

        print("triage")
        run([PY, str(H / "pii.py"), "harvest"], repo, env, label="harvest")
        deny = (ws / "denylist.txt").read_text()
        check("Testovací" in deny and "Fiktivní" in deny, "denylist has cue names and company names")
        run([PY, str(H / "triage.py")], repo, env, label="triage")
        cl = json.loads((ws / "triage/clusters.json").read_text())
        sizes = sorted(c["size"] for c in cl["clusters"])
        check(sizes == [3, 3], f"two recurring clusters of 3 (got {sizes})")
        all_files = json.dumps(cl)
        check("c0000001" not in all_files, "personal conversation never clustered")
        page = (ws / "triage/triage.md").read_text()
        check("800101" not in page and "KSBR" not in page and "Testovac" not in page, "triage page redacted")
        check("osobní 1" in page, "personal counted on the page")

        print("review + apply")
        (ws / "specs").mkdir()
        (ws / "specs/c01.yaml").write_text(CLEAN_SPEC, encoding="utf-8")
        (ws / "specs/c02.yaml").write_text(DIRTY_SPEC, encoding="utf-8")
        run([PY, str(H / "convert.py"), "review"], repo, env, label="review")
        rv = (ws / "review/review.md").read_text()
        check("hit(s)" in rv.split("## c02")[1] and "clean" in rv.split("## c02")[0], "review flags the dirty spec only")
        dec = (ws / "review/decisions.yaml").read_text()
        check(dec.count("decision: pending") == 2, "decisions start pending")
        dec = dec.replace("decision: pending", "decision: skill")
        (ws / "review/decisions.yaml").write_text(dec)
        run([PY, str(H / "convert.py"), "apply"], repo, env, expect=1, label="PII gate blocks a dirty spec")
        check(not (repo / ".claude").exists(), "gate copied nothing into the repo")
        dec = dec.replace("kontrola-prihlasky\n", "kontrola-prihlasky\n")
        import re as _re
        dec = _re.sub(r"(c02:\n(?:  .*\n)*?  decision: )skill", r"\1ignore", dec)
        (ws / "review/decisions.yaml").write_text(dec)
        run([PY, str(H / "convert.py"), "review"], repo, env, label="review keeps decisions")
        check("decision: ignore" in (ws / "review/decisions.yaml").read_text(), "re-review kept the decision")
        run([PY, str(H / "convert.py"), "apply"], repo, env, label="apply")
        sk = repo / ".claude/skills/zprava-o-plneni-oddluzeni/SKILL.md"
        check(sk.is_file() and (sk.parent / "format.md").is_file(), "skill + format written")
        text = sk.read_text() if sk.is_file() else ""
        check("generated_from: chat-history c01" in text and "name: zprava-o-plneni-oddluzeni" in text, "frontmatter + provenance")
        check("Citace zákona vždy celá" in text and "## Hranice" in text, "rules and limits rendered (cs)")
        check("`zprava-o-plneni-oddluzeni`" in (repo / "CLAUDE.md").read_text(), "CLAUDE.md learned-skills block updated")
        check((sk.parent / "references/project-instructions.md").is_file() and (sk.parent / "references/vzor_zpravy.md").is_file()
              and "references/vzor_zpravy.md" in text, "project instructions + template travel with the skill")
        prov = list((repo / "memory/learning").glob("history-*.md"))
        check(len(prov) == 1 and "Testovac" not in prov[0].read_text(), "provenance written, no names")
        check(not (repo / ".claude/skills/kontrola-prihlasky").exists(), "ignored spec not converted")
        run([PY, str(H / "convert.py"), "apply"], repo, env, label="apply again")
        check((sk.parent / "SKILL.md.proposed").is_file(), "existing skill kept, .proposed beside it")

        print("package")
        run([PY, str(H / "convert.py"), "package"], repo, env, label="package")
        z = ws / "claude-ai/zprava-o-plneni-oddluzeni-web.zip"
        ok = z.is_file()
        if ok:
            with zipfile.ZipFile(z) as zf:
                body = zf.read("zprava-o-plneni-oddluzeni-web/SKILL.md").decode()
                ok = "name: zprava-o-plneni-oddluzeni-web" in body and not any(n.endswith(".proposed") for n in zf.namelist())
        check(ok, "chat-app package renamed -web, no .proposed inside")

        print("lint")
        lint = [PY, str(PLUGIN / "scripts/lint.py"), "--repo-root", str(repo), "--check", "pii-scan"]
        run(lint, repo, env, expect=0, label="pii-scan clean on learned files")
        (sk.parent / "format.md").write_text("kontakt: test.osoba@example.com\n", encoding="utf-8")
        run(lint, repo, env, expect=1, label="pii-scan catches an e-mail in a learned file")
        (sk.parent / "format.md").write_text("ok\n", encoding="utf-8")
        subprocess.run(["git", "add", "-f", ".history/manifest.json"], cwd=repo, check=True)
        r = run(lint, repo, env, expect=1, label="pii-scan catches a tracked workspace file")
        check("[CRITICAL] [pii-scan]" in r.stdout, "tracked workspace is CRITICAL")

    print("")
    print("history selftest: " + ("PASS" if not FAILS else f"FAIL ({len(FAILS)})"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
