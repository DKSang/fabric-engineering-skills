# naming-conventions.md format

How things are named, so everything the agent creates follows the team's conventions without anyone restating them.

## Template

```md
# Naming conventions

## Items

| Item type | Pattern | Example |
| --- | --- | --- |
| Workspace | `<Domain>-<STAGE>` | `Sales-DEV` |
| Lakehouse | `lh_<layer or purpose>` | `lh_bronze`, `lh_landing` |
| Notebook | `nb_<verb>_<object>` | `nb_load_bronze` |
| Data pipeline | `pl_<verb>_<layer>_<source>` | `pl_ingest_bronze_webshop` |

## Pipeline activities

`<Verb> <object>` in title case, e.g. `Copy orders`, `Run nb_load_bronze`.

## Tables and columns

- One schema per source system in bronze (e.g. `webshop`); per subject area in silver and gold.
- Tables and columns in `snake_case`.
- Technical metadata columns start with `_` (e.g. `_load_ts`, `_source_file`).

## Exceptions

| Name | Why it breaks the rule |
| --- | --- |
| `Sales Legacy` | pre-dates the conventions; renaming breaks report links |
```

## Rules

- **Pattern plus example, always.** A pattern alone gets misread; the example settles it.
- **Record exceptions, with the reason.** Otherwise the agent "fixes" them.
- **Only the team's real rules.** Don't pad with general advice ("use descriptive names").

## Starter set

When the user has no conventions yet and asks for some, offer this set for them to edit. Never write it without their say-so: an invented convention recorded as fact is worse than none.

| Item type | Pattern | Example |
| --- | --- | --- |
| Workspace | `<Domain>-<STAGE>` | `Sales-DEV` |
| Lakehouse | `lh_<layer or purpose>` | `lh_bronze`, `lh_config` |
| Warehouse | `wh_<purpose>` | `wh_gold` |
| Notebook | `nb_<verb>_<object>` | `nb_load_bronze` |
| Data pipeline | `pl_<verb>_<layer>_<source>` | `pl_ingest_bronze_webshop` |
| Dataflow Gen2 | `df_<verb>_<object>` | `df_clean_customers` |
| Semantic model | `sm_<subject>` | `sm_sales` |
| Report | `rpt_<subject>` | `rpt_sales_overview` |
| Variable library | `vl_<scope>` | `vl_sales` |

Plus: activities as `<Verb> <object>`; `snake_case` tables and columns; `_`-prefixed metadata columns.
