---
name: document-fabric-workspace
description: "Inventory a Fabric workspace into reference/workspaces/<workspace>.md: items, lakehouse tables and schemas, what each notebook and pipeline does, and the lineage between them. Incremental: re-runs read only what changed since last time. Read-only against Fabric."
argument-hint: "<workspace> [--full] [item names...]"
disable-model-invocation: true
---

# Document Fabric Workspace

Write down what a workspace contains and how it fits together, so future sessions answer "where does `webshop.orders` come from?" from a file instead of re-crawling the tenant.

The defining constraint: **never re-read what hasn't changed.** A state file records what was documented and a fingerprint for each piece; every run starts with a cheap change check, and only new, changed or stale pieces get the expensive reads.

Everything here is **read-only** against Fabric. No item is created, changed, run or exported to a lakehouse.

## Arguments

| Invocation | Does |
| --- | --- |
| `/document-fabric-workspace Sales-DEV` | Incremental: document what's new or changed since the last run (everything, the first time) |
| `/document-fabric-workspace Sales-DEV nb_load_bronze pl_ingest_bronze_webshop` | Refresh just those items (plus anything new) |
| `/document-fabric-workspace Sales-DEV --full` | Re-read everything and rewrite the file; use after big changes or when the doc seems wrong |

No workspace given: use the writable workspace from `reference/environment.md` if there's exactly one, otherwise ask.

## Files

```
reference/workspaces/
├── Sales-DEV.md            ← the document (format: WORKSPACE-FORMAT.md)
└── Sales-DEV.state.json    ← what was documented, with fingerprints (written only by the script)
```

Both are committed: the state file lets a teammate's next run stay incremental too. It holds names, IDs and hashes, no data and no secrets. Never edit it by hand.

## Process

### 1. Check before reading

- `fab auth status` shows `Logged In: True`; otherwise hand sign-in to the user.
- The workspace exists: `fab exists "<ws>.Workspace"`.
- Call the Skill tool with "fabric-brain" to read `environment.md` (is this workspace Git-connected to this repo? where is its items folder?) and `naming-conventions.md` (to recognise layers and roles from names).

### 2. Plan: find what changed

Run the change-detection script that ships with this skill ([scripts/workspace_state.py](./scripts/workspace_state.py)). It only ever calls `fab ls`.

```
python <this skill's folder>/scripts/workspace_state.py plan \
  --workspace "<ws>" \
  --state reference/workspaces/<ws>.state.json \
  --items-root <Git-connected items folder, if any> \
  --tables
```

Add `--full` or `--only "<name>,<name>"` to match the arguments. The script prints a summary and writes a plan file (its path is in the output). See [CHANGE-DETECTION.md](./CHANGE-DETECTION.md) for how each signal works and its blind spots.

Show the user the summary in one short table (new, changed, renamed, stale, removed, unchanged; tables new, changed, removed) and the rough cost ("7 items and 3 tables to read; 41 unchanged, skipped"). If the plan is large (more than ~30 items to read), ask whether to go ahead or narrow it.

If nothing changed, say so and stop. Don't touch the document.

### 3. Read only what the plan lists

For each item in `new`, `changed`, `renamed` and `stale`, gather what [WORKSPACE-FORMAT.md](./WORKSPACE-FORMAT.md) asks for, cheapest source first:

| Item | Read from |
| --- | --- |
| Anything in the repo's items folder | the repo files (`notebook-content.py`, `pipeline-content.json`, ...): no API call |
| Notebook, pipeline, other definitions not in the repo | `fab export "<ws>.Workspace/<item>.<Type>" -o <temp dir>` (to a local temp dir, never into a lakehouse), then read the files |
| Pipeline structure | Fabric MCP `datafactory_get-pipeline` if available, else the exported `pipeline-content.json` |
| Lakehouse tables in `tables.new` / `tables.changed` | `fab table schema "<ws>.Workspace/<lh>.Lakehouse/Tables/<schema>/<table>"` |
| Item properties (SQL endpoint, default schema) | `fab get "<ws>.Workspace/<item>.<Type>"` |

For `renamed` items, only the name changed: update the heading and every reference *to that item* (lineage, "Written by", "Calls"), without re-reading the definition. Leave other names that merely contain the old name, such as a pipeline activity called `Run nb_load_bronze`: those come from their own definitions, which haven't changed.

For `removed` items, delete their section and their lineage edges.

Rules while reading:

- **Summarise, don't copy.** Describe what a notebook does in two or three lines; never paste its code. Point at the repo path when one exists.
- **Schemas, never rows.** Column names and types only. Don't preview or sample data.
- **Delegate when it's big.** With many items to read, split them across subagents (if your tool has them), each returning finished sections in the WORKSPACE-FORMAT shape for its batch.
- **If a read fails** (no permission, unsupported item type), note it in the item's section as `(not readable: <reason>)` and remember the name for `--skip` in step 5.

### 4. Update the document

Edit `reference/workspaces/<ws>.md` in place, following [WORKSPACE-FORMAT.md](./WORKSPACE-FORMAT.md):

- Replace only the sections of items the plan listed. Every other section stays byte-for-byte as it was.
- Recompute the summary counts and the lineage from the item sections (both are cheap: no API calls).
- Never touch the `## Notes` section: it belongs to the user and `fabric-brain`.
- First run: create the file, and add one line for it to the `## Reference` list in `AGENTS.md` (inside the `fabric-engineering-skills` block).

### 5. Commit the state

Only after the document is written:

```
python <this skill's folder>/scripts/workspace_state.py commit --plan <plan file> [--skip "<names that failed>"]
```

Skipped items stay pending and come back in the next plan. Committing before the document is written would mark items as documented that aren't.

### 6. Report

Tell the user in a few lines: what was added, changed or removed in the document; what was skipped and why; anything surprising you noticed while reading (a pipeline calling a notebook that no longer exists, a table no item writes to, a hard-coded workspace ID). For durable facts beyond this workspace (a new convention, a lesson), call the Skill tool with "fabric-brain". Leave everything uncommitted for the user to review.
