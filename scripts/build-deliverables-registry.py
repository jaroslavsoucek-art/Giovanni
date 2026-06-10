#!/usr/bin/env python3
"""scripts/build-deliverables-registry.py — render deliverables/REGISTRY.md.

Generates a human-readable lifecycle view of <deliverables_dir>/_registry.yaml.
Deterministic output (no timestamps, stable sort) so lint can diff a regen
against the committed file — same pattern as the INDEX / MAP staleness checks
(`registry-stale` in scripts/lint.sh).

The registry is OPT-IN: it only makes sense once a flat output directory has
grown past the point where filenames alone carry the lifecycle (~50 files).
Status lives in metadata, not in the path — a status flip is a YAML edit,
never a file rename/move (anti-link-rot).

Usage:
    python3 scripts/build-deliverables-registry.py                # write REGISTRY.md
    python3 scripts/build-deliverables-registry.py --dry          # print to stdout
    python3 scripts/build-deliverables-registry.py --repo-root <path>

Configuration:
    GIOVANNI_DELIVERABLES_DIR   deliverables dir relative to repo root
                                (default: deliverables) — mirrors the
                                `deliverables_dir` key in governance config.

Requires PyYAML (same soft dependency as scripts/lint.py).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import-not-found]
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

STATUS_ORDER = ["live", "draft", "sent", "superseded"]
STATUS_HEADINGS = {
    "live": "Live — maintained artifacts and standing references",
    "draft": "Draft — in preparation / send queue (not yet sent)",
    "sent": "Sent — delivered / presented (frozen, do not edit)",
    "superseded": "Superseded — outdated (candidates for `_archive/`)",
}


def load_entries(registry_yaml: Path) -> list[dict]:
    data = yaml.safe_load(registry_yaml.read_text())
    entries = (data or {}).get("entries") or []
    for e in entries:
        for field in ("file", "status", "type", "date"):
            if not e.get(field):
                raise ValueError(f"registry entry missing '{field}': {e}")
        if e["status"] not in STATUS_ORDER:
            raise ValueError(f"invalid status '{e['status']}' for {e['file']}")
    return entries


def render(entries: list[dict]) -> str:
    lines = [
        "# Deliverables registry",
        "",
        "> AUTO-GENERATED from `_registry.yaml` by `scripts/build-deliverables-registry.py` — do not hand-edit.",
        "> Status flip = edit `_registry.yaml` and regenerate (never rename/move the file — status lives in metadata, not in the path).",
        "> A file without an entry = lint finding (`deliverables-registry`).",
        "",
    ]
    counts = ", ".join(
        f"{status} {sum(1 for e in entries if e['status'] == status)}"
        for status in STATUS_ORDER
    )
    lines += [f"**{len(entries)} entries** ({counts}) + `_archive/` outside the registry.", ""]

    for status in STATUS_ORDER:
        group = [e for e in entries if e["status"] == status]
        if not group:
            continue
        group.sort(key=lambda e: (str(e["date"]), e["file"]), reverse=True)
        lines += [f"## {STATUS_HEADINGS[status]}", ""]
        lines += ["| File | Type | Date | Note |", "|---|---|---|---|"]
        for e in group:
            note = str(e.get("note", "")).replace("|", "\\|").strip()
            lines.append(f"| [{e['file']}]({e['file']}) | {e['type']} | {e['date']} | {note} |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="print to stdout, no file write")
    parser.add_argument("--repo-root", default=None, help="repo root (default: script's parent dir)")
    args = parser.parse_args(argv)

    if not HAVE_YAML:
        print(
            "ERROR: PyYAML missing — cannot parse _registry.yaml "
            "(pip install pyyaml)",
            file=sys.stderr,
        )
        return 2

    repo = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent.parent
    )
    deliverables_dir = os.environ.get("GIOVANNI_DELIVERABLES_DIR", "deliverables")
    deliv = repo / deliverables_dir
    registry_yaml = deliv / "_registry.yaml"
    registry_md = deliv / "REGISTRY.md"

    if not registry_yaml.is_file():
        print(f"ERROR: {registry_yaml} not found — registry is opt-in; "
              f"create it from deliverables/_registry.template.yaml first", file=sys.stderr)
        return 2

    entries = load_entries(registry_yaml)
    out = render(entries)
    if args.dry:
        sys.stdout.write(out)
    else:
        registry_md.write_text(out)
        print(f"{deliverables_dir}/REGISTRY.md regenerated ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
