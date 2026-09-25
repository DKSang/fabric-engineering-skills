# Reference seeds

Starting content for `reference/`. Fill them only with what the user confirmed or what verification proved. Drop any section you have nothing real for: an empty heading teaches the agent nothing and looks like a fact to fill in later.

The agent grows these files over time: whenever the user explains something durable, it lands here, so they never explain it twice.

## `reference/environment.md`

```md
# Fabric environment

## Tenant

- **Tenant ID**: {from `fab auth status`}
- **Agent identity**: {service principal name / "developer's own account"}. No secrets here.

## Scope

| Workspace | ID | Stage | Agent may write? |
| --- | --- | --- | --- |
| {Sales-DEV} | {guid} | DEV | yes, after a dry run and confirmation |
| {Sales-PRD} | {guid} | PRD | never |

Every workspace not listed here is out of scope: read only if the task needs it, never modify.

## Key items

| Item | Workspace | Type | Purpose |
| --- | --- | --- | --- |

## Connections and gateways

| Name | Points at | Credential lives in |
| --- | --- | --- |
```

## `reference/naming-conventions.md`

If the user has no conventions yet, offer this common starting set and let them edit it. Never impose it silently.

```md
# Naming conventions

## Items

| Item type | Pattern | Example |
| --- | --- | --- |
| Workspace | `<Domain>-<STAGE>` | `Sales-DEV` |
| Lakehouse | `lh_<layer or purpose>` | `lh_bronze`, `lh_landing` |
| Warehouse | `wh_<purpose>` | `wh_gold` |
| Notebook | `nb_<verb>_<object>` | `nb_load_bronze` |
| Data pipeline | `pl_<verb>_<layer>_<source>` | `pl_ingest_bronze_webshop` |
| Dataflow Gen2 | `df_<verb>_<object>` | `df_clean_customers` |
| Semantic model | `sm_<subject>` | `sm_sales` |
| Report | `rpt_<subject>` | `rpt_sales_overview` |

## Pipeline activities

`<Verb> <object>` in title case, e.g. `Copy orders`, `Run nb_load_bronze`.

## Tables and columns

- Schemas per source system in bronze (e.g. `webshop`); per subject area in silver and gold.
- Tables and columns in `snake_case`.
- Technical metadata columns are prefixed `_` (e.g. `_load_ts`, `_source_file`).
```

## `reference/architecture/<pattern>.md`

Create one file per pattern only when the user describes one (e.g. `medallion-bronze.md` for how they build bronze layers, `metadata-framework.md` for their config-driven loading). Capture:

```md
# {Pattern name}

## Purpose

{One or two sentences.}

## Structure

{Items involved, folder layout, e.g. `Files/raw/<source>/<dataset>/<yyyyMMddHHmmss>/`.}

## Rules

{The non-negotiables: load type (append, SCD2 merge), metadata columns, config location and format.}

## Example

{A minimal real example: a config file, a folder tree, a table.}
```

Link each new file from the `## Reference` list in `AGENTS.md`.
