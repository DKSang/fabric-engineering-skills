# Change detection

How `scripts/workspace_state.py` decides what to re-read. The goal is to spend one cheap call to find out whether an expensive read is needed.

## Signals, cheapest first

| Tier | Signal | Cost | Detects |
| --- | --- | --- | --- |
| 1. Inventory | `fab ls "<ws>.Workspace" -l`: every item's name, type and **ID** | 1 call per run | new, removed and renamed items (matched by ID, so a rename isn't a delete plus a create) |
| 2. Definitions, Git-connected | SHA-256 of the item's folder in the repo (found by the `displayName` and `type` in each `.platform`) | 0 API calls | any change to the item's committed or working-tree definition |
| 2. Definitions, not in the repo | none available: Fabric's item API has no last-modified date | 0 calls | only age: re-read after `max_age_days` (default 30) as **stale** |
| 3. Tables | `fab ls -l` on each lakehouse's `Tables/` (and each schema): every table's `lastModified` | 1 call per lakehouse + 1 per schema | new, removed and written-to tables; only those get `fab table schema` |

## States

| Bucket | Meaning | What the skill does |
| --- | --- | --- |
| `new` | ID not in the state file | read and write a section |
| `changed` | repo fingerprint differs, or `--full`, or named with `--only` | re-read and replace the section |
| `renamed` | same ID, different name | rename the section and its references; no re-read |
| `stale` | no change signal, documented longer ago than `max_age_days` | re-read and replace the section |
| `removed` | in the state file, not in the workspace | delete the section and its lineage edges |
| `unchanged` | none of the above | leave alone |

## The state file

`reference/workspaces/<ws>.state.json`, written only by the script:

```json
{
  "schema_version": 1,
  "workspace": {"name": "Sales-DEV"},
  "max_age_days": 30,
  "updated_at": "2026-09-25T10:00:00+00:00",
  "full_scan_at": "2026-09-01T09:00:00+00:00",
  "items": {
    "<item id>": {
      "name": "nb_load_bronze",
      "type": "Notebook",
      "fingerprint": "files:sha256:...",
      "repo_folder": "fabric/nb_load_bronze.Notebook",
      "documented_at": "2026-09-25T10:00:00+00:00"
    }
  },
  "tables": {
    "lh_bronze/webshop/orders": {"lastModified": "...", "documented_at": "..."}
  }
}
```

To change the staleness window for one workspace, the user edits `max_age_days` in this file; nothing else in it is meant for hands.

## Blind spots (tell the user when they matter)

- **Definitions outside Git.** A notebook edited in the Fabric UI of a workspace that isn't Git-connected is only caught when it goes stale, or when named with `--only`. Git-connecting the workspace makes every change visible for free.
- **Uncommitted workspace changes.** In a Git-connected workspace, edits made in Fabric but not yet committed to Git aren't in the repo, so the fingerprint doesn't see them. `fab api "workspaces/<id>/git/status"` lists them if the user wants them included (it's on the permission prompt).
- **Table timestamps.** `lastModified` is the table folder's timestamp in OneLake. A write that only touches subfolders (a partitioned table) may not move it. `--full` re-reads every schema.
- **Schedules, permissions, connections** have no cheap signal; they're refreshed with their item (when it's new, changed or stale) and by `--full`.

A `--full` run now and then (monthly, or after a big release) closes all of these.
