#!/usr/bin/env python3
"""history/extract.py — step 1 of /giovanni:learn-history: a claude.ai data export
→ a private, normalised workspace the analysis can read.

Why. Someone who has used Claude in the chat app for a year already *has* their
workflows: the same kind of ask, the same corrections, the same output shape,
repeated across dozens of conversations. Those are the skills an instance should
start with — better than any list a builder guesses. The official export
(claude.ai → Settings → Privacy → Export data, a zip by e-mail) is the only
complete, supported copy of that history, so this script starts there.

Where the output goes, and why there. The workspace (default `.history/` in the
project, gitignored; `learning.history.workspace`) holds the raw transcripts:
other people's names, case numbers, whatever the principal pasted into a chat.
It never enters git — init adds it to .gitignore and the `pii-scan` lint rule
fails the build if anything under it is tracked. Inside the project rather than
in ~/Documents because the principal reviews the analysis in the same app the
assistant runs in, and the app's file pane opens project files only.

Input: the export zip, or the directory it unpacked to. Files used when present:
conversations.json (required), projects.json, memories.json / memory*.json,
users.json (account only — never copied). The format is not a published,
versioned schema; unknown keys are counted in manifest.json, and a missing or
reshaped conversations.json fails loudly instead of extracting nothing.

Output (<workspace>/):
  manifest.json                      counts, date range, schema notes, export path
  raw/conversations/<date>_<id8>.md  one transcript per conversation, title inside only
  raw/projects/<id8>/instructions.md project instructions + docs/<file>
  raw/artifacts/<id8>_<n>.<ext>      artifacts the assistant produced (output-format exemplars)
  raw/memories.md                    the chat app's memory, if exported
  index.jsonl                        one feature row per conversation (for triage.py)

File names carry dates and ids, never titles: a title is often a person's name.

Usage:
  extract.py EXPORT(.zip|dir) [--repo R] [--workspace DIR] [--inspect]
    --inspect   print what the export contains and exit; writes nothing
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import gconfig  # noqa: E402

ARTIFACT_EXT = {
    "text/markdown": "md", "text/html": "html", "application/vnd.ant.code": "txt",
    "application/vnd.ant.react": "jsx", "image/svg+xml": "svg", "application/vnd.ant.mermaid": "mmd",
    "text/plain": "txt", "text/csv": "csv",
}
KNOWN_CONV_KEYS = {"uuid", "name", "summary", "created_at", "updated_at", "account", "chat_messages",
                   "project_uuid", "project", "is_starred", "current_leaf_message_uuid", "settings", "model"}
KNOWN_MSG_KEYS = {"uuid", "text", "content", "sender", "index", "created_at", "updated_at", "truncated",
                  "attachments", "files", "files_v2", "parent_message_uuid", "stop_reason", "sync_sources"}


def history_workspace(repo: Path, cfg: dict, override: str | None) -> Path:
    raw = override or ((cfg.get("learning") or {}).get("history") or {}).get("workspace") or ".history"
    p = Path(raw).expanduser()
    return p if p.is_absolute() else (repo / p)


def open_export(src: Path) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    if src.is_dir():
        return src, None
    if src.suffix.lower() == ".zip" and src.is_file():
        tmp = tempfile.TemporaryDirectory(prefix="giovanni-export-")
        with zipfile.ZipFile(src) as zf:
            for member in zf.namelist():
                target = (Path(tmp.name) / member).resolve()
                if not str(target).startswith(str(Path(tmp.name).resolve())):
                    raise SystemExit(f"refusing zip member outside the archive: {member}")
            zf.extractall(tmp.name)
        return Path(tmp.name), tmp
    raise SystemExit(f"export not found or not a .zip / directory: {src}")


def find_file(root: Path, *names: str) -> Path | None:
    for name in names:
        hits = sorted(root.rglob(name))
        if hits:
            return hits[0]
    return None


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def ts(value) -> str:
    return str(value or "")[:19].replace("T", " ")


def day(value) -> str:
    return str(value or "")[:10] or "0000-00-00"


def message_parts(msg: dict) -> tuple[str, list[dict]]:
    """Text of one message plus the artifacts it created.

    Newer exports carry a `content` list (text / thinking / tool_use / tool_result
    blocks); older ones only `text`. Thinking blocks are dropped: they are the
    model's scratch work, not something the principal saw or accepted.
    """
    texts, artifacts = [], []
    content = msg.get("content")
    if isinstance(content, list) and content:
        for block in content:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "text" and block.get("text"):
                texts.append(block["text"])
            elif kind == "tool_use":
                inp = block.get("input") or {}
                if block.get("name") in ("artifacts", "artifact") and isinstance(inp, dict) and inp.get("content"):
                    artifacts.append({
                        "title": inp.get("title") or "",
                        "type": inp.get("type") or "",
                        "command": inp.get("command") or "",
                        "content": inp["content"],
                    })
                    texts.append(f"[artifact: {inp.get('title') or inp.get('id') or ''}]")
                else:
                    texts.append(f"[tool: {block.get('name')}]")
    if not texts and msg.get("text"):
        texts.append(msg["text"])
    return "\n\n".join(texts).strip(), artifacts


def attachment_lines(msg: dict) -> tuple[list[str], list[str]]:
    lines, types = [], []
    for att in msg.get("attachments") or []:
        if not isinstance(att, dict):
            continue
        name = att.get("file_name") or "attachment"
        ftype = (att.get("file_type") or Path(name).suffix.lstrip(".") or "?").lower()
        types.append(ftype)
        body = (att.get("extracted_content") or "").strip()
        lines.append(f"> **Příloha / attachment:** {name} ({ftype})")
        if body:
            lines.append("```text\n" + body + "\n```")
    for f in (msg.get("files") or []) + (msg.get("files_v2") or []):
        if isinstance(f, dict) and f.get("file_name"):
            types.append((Path(f["file_name"]).suffix.lstrip(".") or "file").lower())
            lines.append(f"> **Soubor / file:** {f['file_name']}")
    return lines, types


def inspect(root: Path) -> int:
    print(f"Export root: {root}")
    for p in sorted(root.rglob("*.json")):
        try:
            data = load_json(p)
        except Exception as e:  # noqa: BLE001
            print(f"  {p.relative_to(root)}: unreadable ({e})")
            continue
        shape = f"list[{len(data)}]" if isinstance(data, list) else type(data).__name__
        keys = sorted(data[0].keys()) if isinstance(data, list) and data and isinstance(data[0], dict) else []
        print(f"  {p.relative_to(root)}: {shape}" + (f" keys={keys}" if keys else ""))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export")
    ap.add_argument("--repo")
    ap.add_argument("--workspace")
    ap.add_argument("--inspect", action="store_true")
    args = ap.parse_args(argv)

    root, tmp = open_export(Path(args.export).expanduser())
    try:
        if args.inspect:
            return inspect(root)
        repo = gconfig.repo_root(args.repo)
        cfg = gconfig.config(repo)
        ws = history_workspace(repo, cfg, args.workspace)

        conv_path = find_file(root, "conversations.json")
        if conv_path is None:
            raise SystemExit("conversations.json not found in the export — is this a claude.ai data export? "
                             "Run with --inspect to see what it contains.")
        conversations = load_json(conv_path)
        if not isinstance(conversations, list) or (conversations and not isinstance(conversations[0], dict)):
            raise SystemExit("conversations.json is not a list of conversation objects — the export format "
                             "changed. Run with --inspect and adapt extract.py before analysing anything.")

        for sub in ("raw/conversations", "raw/projects", "raw/artifacts"):
            d = ws / sub
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)

        projects = {}
        proj_path = find_file(root, "projects.json")
        if proj_path:
            for pr in load_json(proj_path) or []:
                if not isinstance(pr, dict) or not pr.get("uuid"):
                    continue
                pid = pr["uuid"][:8]
                projects[pr["uuid"]] = pr.get("name") or pid
                pdir = ws / "raw/projects" / pid
                (pdir / "docs").mkdir(parents=True, exist_ok=True)
                body = [f"# {pr.get('name') or pid}", "",
                        f"- uuid: {pr['uuid']}", f"- created: {ts(pr.get('created_at'))}",
                        f"- updated: {ts(pr.get('updated_at'))}", f"- starter: {pr.get('is_starter_project', False)}", "",
                        "## Description", "", (pr.get("description") or "").strip() or "_(none)_", "",
                        "## Instructions (prompt_template)", "", (pr.get("prompt_template") or "").strip() or "_(none)_", ""]
                docs = pr.get("docs") or []
                if docs:
                    body += ["## Knowledge docs", ""]
                for i, doc in enumerate(docs, 1):
                    if not isinstance(doc, dict):
                        continue
                    fname = re.sub(r"[^\w.-]+", "_", doc.get("filename") or f"doc-{i}.txt")[:80]
                    (pdir / "docs" / fname).write_text(doc.get("content") or "", encoding="utf-8")
                    body.append(f"- docs/{fname} ({len(doc.get('content') or '')} chars)")
                (pdir / "instructions.md").write_text("\n".join(body) + "\n", encoding="utf-8")

        mem_lines = []
        for p in sorted(root.rglob("*.json")):
            if p.name.lower().startswith("memor"):
                mem_lines += [f"## {p.name}", "", "```json",
                              json.dumps(load_json(p), ensure_ascii=False, indent=2), "```", ""]
        if mem_lines:
            (ws / "raw").mkdir(parents=True, exist_ok=True)
            (ws / "raw/memories.md").write_text("# Chat-app memory (export)\n\n" + "\n".join(mem_lines), encoding="utf-8")

        unknown_conv = collections.Counter()
        unknown_msg = collections.Counter()
        index_rows, dates, n_artifacts_total, skipped_empty = [], [], 0, 0
        for conv in conversations:
            unknown_conv.update(k for k in conv if k not in KNOWN_CONV_KEYS)
            msgs = conv.get("chat_messages") or []
            if not msgs:
                skipped_empty += 1
                continue
            cid = str(conv.get("uuid") or "")[:8] or f"x{len(index_rows):07d}"
            created = conv.get("created_at") or (msgs[0].get("created_at") if msgs else "")
            fname = f"{day(created)}_{cid}.md"
            project_uuid = conv.get("project_uuid") or ((conv.get("project") or {}).get("uuid") if isinstance(conv.get("project"), dict) else None)
            project = projects.get(project_uuid, "") if project_uuid else ""

            out = ["---", f"uuid: {conv.get('uuid', '')}", f"created: {ts(created)}",
                   f"updated: {ts(conv.get('updated_at'))}", f"project: {json.dumps(project, ensure_ascii=False)}",
                   f"messages: {len(msgs)}", "---", "", f"# {conv.get('name') or '(untitled)'}", ""]
            human_texts, n_human, h_chars, a_chars, att_types, n_art = [], 0, 0, 0, [], 0
            for i, msg in enumerate(msgs):
                unknown_msg.update(k for k in msg if k not in KNOWN_MSG_KEYS)
                sender = msg.get("sender") or "?"
                text, arts = message_parts(msg)
                a_lines, a_types = attachment_lines(msg)
                att_types += a_types
                who = "ČLOVĚK / HUMAN" if sender == "human" else "CLAUDE"
                out += [f"## [{i + 1}] {who} · {ts(msg.get('created_at'))}", ""]
                if text:
                    out += [text, ""]
                out += a_lines + ([""] if a_lines else [])
                if sender == "human":
                    n_human += 1
                    h_chars += len(text)
                    human_texts.append(text)
                else:
                    a_chars += len(text)
                for art in arts:
                    n_art += 1
                    ext = ARTIFACT_EXT.get(art["type"], "txt")
                    aname = f"{cid}_{n_art:02d}.{ext}"
                    (ws / "raw/artifacts" / aname).write_text(art["content"], encoding="utf-8")
                    out.append(f"> artifact → raw/artifacts/{aname} ({art['type'] or '?'}, {art['command'] or 'create'})")
                    out.append("")
            n_artifacts_total += n_art
            (ws / "raw/conversations" / fname).write_text("\n".join(out), encoding="utf-8")
            dates.append(day(created))
            sample = "\n".join(human_texts)
            index_rows.append({
                "id": cid, "uuid": conv.get("uuid"), "file": f"raw/conversations/{fname}",
                "title": conv.get("name") or "", "created": day(created), "updated": day(conv.get("updated_at")),
                "project": project, "messages": len(msgs), "human_turns": n_human,
                "human_chars": h_chars, "assistant_chars": a_chars, "artifacts": n_art,
                "attachment_types": sorted(set(att_types)),
                "first_human": (human_texts[0] if human_texts else "")[:600],
                "human_sample": sample[:5000],
            })

        index_rows.sort(key=lambda r: (r["created"], r["id"]))
        with (ws / "index.jsonl").open("w", encoding="utf-8") as fh:
            for row in index_rows:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        manifest = {
            "extracted_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "export": str(Path(args.export).expanduser().resolve()),
            "conversations": len(index_rows), "skipped_empty": skipped_empty,
            "projects": len(projects), "artifacts": n_artifacts_total,
            "memories": bool(mem_lines),
            "date_range": [min(dates), max(dates)] if dates else [],
            "unknown_conversation_keys": dict(unknown_conv),
            "unknown_message_keys": dict(unknown_msg),
        }
        (ws / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Extracted {len(index_rows)} conversations ({manifest['date_range'][0] if dates else '-'} → "
              f"{manifest['date_range'][1] if dates else '-'}), {len(projects)} projects, "
              f"{n_artifacts_total} artifacts → {ws}")
        if unknown_conv or unknown_msg:
            print(f"Note: unknown keys (format drift?) — conversation {dict(unknown_conv)}, message {dict(unknown_msg)}")
        return 0
    finally:
        if tmp is not None:
            tmp.cleanup()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
