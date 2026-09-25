# End-to-end test

Prove the build works by running it and checking the **data**, not just the run status. A pipeline can succeed and load nothing.

Only run in a writable workspace, and only after the user said yes to the test in step 6.

## 1. Define "passed" before running

Write down what a passing run produces, from the plan and the architecture file, and show it with the test offer:

```md
Passes when:
- pl_ingest_bronze_webshop run status is Completed
- lh_bronze/Files/raw/webshop/orders/<ts>/orders.csv exists for this run
- table webshop.orders exists with the source columns plus _load_ts, _source_file, _valid_from, _valid_to, _is_current
- row count of current rows = 30 (rows in data/orders.csv)
```

Take expected counts from the sample files in `data/` (count them locally), never from the run itself.

## 2. Build for testability

When you write a loader notebook, make it end with a summary the test can read, e.g. `notebookutils.notebook.exit(json.dumps({"orders": {"rows_read": 30, "rows_current": 30}}))`. The exit value appears in the pipeline's activity run output, which gives the test a row count without extra items or extra MCP servers. Verify the exit utility on Learn before relying on it.

## 3. Run

```
fab job start "<ws>.Workspace/<pipeline>.DataPipeline"
fab job run-list "<ws>.Workspace/<pipeline>.DataPipeline"
fab job run-status "<ws>.Workspace/<pipeline>.DataPipeline" --id <job instance id>
```

Poll `run-status` every 30 to 60 seconds and tell the user it's running. Don't use `fab job run --timeout` for this: on timeout the CLI cancels the job by default.

## 4. Check the output

| Check | How |
| --- | --- |
| Run status | `fab job run-status ... --id <id>`: `Completed` |
| Files landed where the pattern says | `fab ls "<ws>.Workspace/<lakehouse>.Lakehouse/Files/<path>"` |
| Table exists with the right columns | `fab table schema "<ws>.Workspace/<lakehouse>.Lakehouse/Tables/<schema>/<table>"` |
| Row counts | in order of preference: the loader's exit value in the activity output (below); a `fabric-sqlendpoint` MCP query (`SELECT COUNT(*) ...`) if that server is configured; otherwise sum `numRecords` in the table's `_delta_log` add actions (download the JSON files read-only with Fabric MCP `onelake_download-file`), minus files later removed |

Activity output and errors for a pipeline run (read-only, but it's a POST, so it hits the permission prompt):

```
fab api -X post "workspaces/<workspace id>/datapipelines/pipelineruns/<job instance id>/queryactivityruns" -i '{"lastUpdatedAfter":"<run start, ISO 8601>","lastUpdatedBefore":"<now, ISO 8601>"}'
```

Each activity comes back with `status`, `output` (a notebook's exit value is in there) and `error`. Endpoint documented in [REST API capabilities for Fabric Data Factory](https://learn.microsoft.com/fabric/data-factory/pipeline-rest-api-capabilities); re-check it on Learn if the call fails.

### Idempotency (when the pattern claims it)

If the architecture says re-runs are safe (SCD2, merge, incremental), offer a second run with the same input and check that the current-row count doesn't change and a second raw folder was archived. This is the check that catches merge keys that don't match.

## 5. On failure: diagnose, fix, re-run

1. **Get the real error**: the failed activity's `error` from `queryactivityruns`; for a notebook, its message and the failing cell. Quote it.
2. **Check what's known**: `lessons.md` for the same symptom; then `microsoft_docs_search` with the error text.
3. **Find the cause** before changing anything. State it in one sentence. "Try something else" is not a cause.
4. **Fix the definition in the repo**, show the diff, and get a yes; then re-import (`fab import ... -f`) and re-run.
5. **Stop after three failed attempts.** Report what you tried, what you learned, and what you need from the user (a permission, a connection, a capacity, a design decision).

Never make a test pass by weakening it: don't lower the expected count, drop a check, or catch and ignore the error.

## 6. After the test

- Report pass/fail per check, and for any failed run, the cause and the fix.
- Call the Skill tool with "fabric-brain" to add any non-obvious cause to `lessons.md` (symptom with the error text, cause, fix, Learn URL).
- Leave the test data in place and say where it is. Offer cleanup as its own plan (exact paths, marked destructive); never delete on your own.
