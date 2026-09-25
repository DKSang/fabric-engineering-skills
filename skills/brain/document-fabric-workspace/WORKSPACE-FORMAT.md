# reference/workspaces/&lt;workspace&gt;.md format

One file per workspace. Built for incremental updates: every item has its own section, anchored by its ID, so a re-run replaces exactly the sections that changed and nothing else.

## Template

```md
# Sales-DEV

Workspace ID `...` · Git: `fabric/` on `main` · Documented by `/document-fabric-workspace`; edit only `## Notes` by hand.

## Summary

| Type | Count |
| --- | --- |
| Lakehouse | 3 |
| Notebook | 1 |
| DataPipeline | 1 |

## Lineage

- `lh_landing/Files/webshop/*.csv` → **pl_ingest_bronze_webshop** → `lh_bronze/Files/raw/webshop/<dataset>/<ts>/`
- `lh_bronze/Files/raw/webshop/` → **nb_load_bronze** (run by pl_ingest_bronze_webshop) → `lh_bronze.webshop.orders`
- `lh_config/Files/webshop/webshop.json` → read by **nb_load_bronze**

## Lakehouses

<!-- item:11111111-0000-0000-0000-000000000001 -->
### lh_bronze

Schemas enabled · SQL endpoint available · Role: bronze layer (per `architecture/medallion-bronze.md`)

| Table | Columns | Written by |
| --- | --- | --- |
| `webshop.orders` | order_id (int), amount (decimal), _load_ts (timestamp), _source_file (string), _valid_from, _valid_to, _is_current | nb_load_bronze |

Files: `raw/<source>/<dataset>/<ts>/`

## Notebooks

<!-- item:11111111-0000-0000-0000-000000000002 -->
### nb_load_bronze

Repo: `fabric/nb_load_bronze.Notebook` · Default lakehouse: lh_bronze · Parameters: `source`

Reads the source config from lh_config, copies landing files into `Files/raw/...`, SCD2-merges each dataset into `lh_bronze.<source>.<dataset>`, exits with row counts.

## Pipelines

<!-- item:11111111-0000-0000-0000-000000000003 -->
### pl_ingest_bronze_webshop

Repo: `fabric/pl_ingest_bronze_webshop.DataPipeline` · Schedule: daily 02:00 UTC · Parameters: none

| Activity | Type | Calls / does |
| --- | --- | --- |
| Run nb_load_bronze | TridentNotebook | nb_load_bronze with source=webshop |

## Other items

<!-- item:... -->
### sm_sales (SemanticModel)

Direct Lake on lh_gold; used by rpt_sales_overview.

## Notes

(Owned by the user and `fabric-brain`. Never rewritten by `/document-fabric-workspace`.)
```

## Rules

- **One section per item**, opened by `<!-- item:<id> -->` then `### <name>`. The ID anchor is what makes incremental updates safe: find the anchor, replace up to the next anchor or `##` heading. Renames change the heading, never the anchor.
- **Group by type** under `##` headings (Lakehouses, Warehouses, Notebooks, Pipelines, Dataflows, Semantic models, Reports, Other items), sorted by name inside each group. Drop groups that are empty.
- **Summary and Lineage are derived** from the item sections every run; never edit them independently.
- **Lineage in one direction**: source → item → destination, one line per flow, item names in bold. Only edges you read in a definition; mark guesses `(inferred from name)`.
- **Say what it does, not how.** Two or three lines per notebook. No code, no SQL, no M.
- **Schemas, never data.** Column names and types; no sample rows, no distinct values.
- **Link, don't repeat.** Point at `architecture/` files for the pattern and at repo paths for the code.
- **Unreadable items** get their section anyway, with `(not readable: <reason>)`.
- **Split when big.** Past ~400 lines, move each type group to `reference/workspaces/<ws>/<group>.md` and keep Summary, Lineage and links in `<ws>.md`.
