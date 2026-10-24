# /giovanni:learn-history — procedure

`P` = `${CLAUDE_PLUGIN_ROOT}/scripts/history`. All scripts take `--repo` implicitly from the session's project.

## Step 0 — Get the export (the principal does this)

In the chat app (web or desktop): **Settings → Privacy → Export data**. The export arrives by e-mail as a download link; it expires, so download it the same day. Do not unzip it into the repo. Tell the principal this in their language if they have not done it yet, then stop.

If the principal also has skills of their own in the chat app, ask them to download each (skill menu → download) next to the export: they are the most explicit workflows they have, and the analysts should see them as `existing_skills`.

## Step 1 — Extract

```
python3 P/extract.py <export> --inspect     # optional: what is in it
python3 P/extract.py <export>
```

Relay the one-line result. If it printed unknown keys, mention them once (format drift) — extraction still worked unless it failed.

## Step 2 — Triage

```
python3 P/pii.py harvest
python3 P/triage.py
```

Show the principal `<workspace>/triage/triage.md` (open it, do not paste it). Ask once:

- whether the work/personal split looks right (corrections go to `<workspace>/overrides.yaml` as `<id>: work|personal|skip`, then re-run triage),
- whether to analyse all clusters or the top N (default: all clusters of size ≥ 2, at most 15).

## Step 3 — Analyse (parallel)

Read `<workspace>/triage/workplan.json`. List the instance's current skills (`.claude/skills/*/SKILL.md`: name + first line of description) as `existing_skills`. Read `learning.history.language` and `learning.history.domain_hint` from the config.

Spawn one `giovanni:history-analyst` per cluster, **in one message, up to 5 at a time**, each with: `workspace` (absolute), the cluster's id/size/span/terms/project, `sample`, `project_instructions`, `spec_path` (`specs/<id>.yaml`), `language`, `domain_hint`, `existing_skills`. Wait for all; collect the three-line returns. **Never open a transcript yourself and never read an analyst's transcript** — only its spec file.

## Step 4 — Review page

```
python3 P/convert.py review
```

Open `<workspace>/review/review.md` for the principal. Then walk it with them in plain language, one proposal at a time or as a batch ("1 yes, 3 to house style, 5 no"). Record each answer in `<workspace>/review/decisions.yaml` (`decision:`, `slug:` if they rename, `merge_target:` for merge-into). Answers to `open_questions` go into the spec file itself (edit the YAML), then re-run `review`.

A spec whose PII line says hits → fix the spec (replace with a placeholder) before it can be applied.

**Stop here** unless the principal said to continue.

## Step 5 — Apply

```
python3 P/convert.py apply [--only …]
```

- Exit 1 = the PII gate found something in staging; nothing was copied. Show the masked findings, fix the specs, re-run `review` + `apply`.
- On success, show `git status --short` and the list of written files. Run the lint (`bash ${CLAUDE_PLUGIN_ROOT}/scripts/lint.sh`). Do not commit — the principal reviews; if the instance has an autonomy profile, the next Stop hook commits the paths it owns and leaves canon (`.claude/`, `knowledge/`) for confirmation.
- Suggest trying one new skill right away on a real ask: the first use is the real test of the format.

## Step 6 — Package (optional)

```
python3 P/convert.py package
```

Tell the principal where the zips are and that they upload them in the chat app's skill settings themselves. The `-web` suffix is deliberate: the chat app syncs uploaded skills back into Claude Code, and the same name twice makes both ambiguous.

## Re-runs

The workspace keeps `overrides.yaml`, `denylist.txt` (with `# manual` lines) and `review/decisions.yaml` across exports. A monthly re-export → steps 1–4 again: decided clusters keep their decisions; new clusters arrive as `pending`. Learned skills already in the repo are never overwritten — a changed spec lands as `SKILL.md.proposed` for the principal to compare.
