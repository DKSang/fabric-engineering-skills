# architecture/&lt;pattern&gt;.md format

How one pattern is built: a medallion layer, a metadata-driven loading framework, an incremental refresh approach. One file per pattern, named after it (`medallion-bronze.md`, `metadata-framework.md`). This is what lets the agent build "my bronze layer" without being told what that means.

## Template

```md
# Bronze layer

## Purpose

Land source data unchanged and keep full history, so silver can always be rebuilt.

## Items

| Item | Role |
| --- | --- |
| `lh_landing` | where source extracts arrive (mock source in DEV) |
| `lh_config` | one JSON config per source, `Files/<source>/<source>.json` |
| `lh_bronze` | raw files and bronze tables |
| `nb_load_bronze` | generic loader, driven by the config |
| `pl_ingest_bronze_<source>` | copies files, then runs the loader |

## Structure

- Raw files: `lh_bronze/Files/raw/<source>/<dataset>/<yyyyMMddHHmmss>/<file>`; every run archived, never overwritten.
- Tables: `lh_bronze/Tables/<source>/<dataset>`.

## Rules

- Load type: SCD2 merge keyed on the source primary key.
- Metadata columns on every table: `_load_ts`, `_source_file`, `_valid_from`, `_valid_to`, `_is_current`.
- Column names stay as the source delivers them.
- The loader reads everything from the config; nothing source-specific is hard-coded.

## Config example

    {
      "source": "webshop",
      "datasets": [
        { "name": "orders", "file_pattern": "orders*.csv", "keys": ["order_id"], "load_type": "scd2" }
      ]
    }

## Flow

1. `pl_ingest_bronze_<source>` copies new files from landing to `Files/raw/...`.
2. It runs `nb_load_bronze` with `source=<source>`.
3. The notebook merges each dataset into its table and stamps the metadata columns.
```

## Rules

- **The non-negotiables first.** Load types, metadata columns, config location and shape: the things a wrong guess breaks.
- **Name items by pattern**, and let `naming-conventions.md` own the naming rules; don't redefine them here.
- **One small, real example** (a config, a folder tree) beats a paragraph of description.
- **Write what the team does, not best practice.** If they differ from Microsoft's guidance, that's worth a line saying why (or a decision record).
- **No code dumps.** Link to the notebook or item definition in the repo instead of pasting it; the code is its own source of truth.
