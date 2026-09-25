# lessons.md format

Gotchas already paid for once: a failure whose cause wasn't obvious, or a platform limit that shaped how something is built. The agent scans the headings before touching the same item type or tool, so the second time costs nothing.

## Template

```md
# Lessons

## Notebooks

### Workspace name is not available in a pipeline-triggered notebook session

- **Symptom**: `nb_load_bronze` failed only when run from `pl_ingest_bronze_webshop`, with a path error on `lh_bronze`.
- **Cause**: the notebook built the OneLake path from a hard-coded workspace name that didn't match the run context.
- **Fix**: resolve the workspace at runtime (`notebookutils.runtime.context`) instead of hard-coding it.
- **Source**: https://learn.microsoft.com/... (verified 2026-09)

## Pipelines

### ...

## Fabric CLI

(CLI quirks go in `fabric-cli.md` under `## Gotchas`, not here.)
```

## Rules

- **Group by item type or tool** (`## Notebooks`, `## Pipelines`, `## Lakehouse`, `## Gateways`), so a scan of the headings finds the relevant ones.
- **The heading is the lesson**, phrased so it's useful on its own: "Workspace name is not available in a pipeline-triggered session", not "Bronze load error".
- **Symptom, cause, fix.** Include the error text the agent would see, so it can match it next time.
- **Cite platform facts.** When the lesson is about how Fabric behaves, verify it on Microsoft Learn and add the URL. Unverified: say so.
- **Delete lessons that expire.** When a Fabric update removes a limit, remove the lesson (or mark it with the date it stopped applying).
- **Not a run log.** A one-off failure with an obvious cause (a typo, a paused capacity) is not a lesson.
