# Recipes

Verified `fab` patterns for building (Fabric CLI 1.7). Flags change between versions: run `fab <command> --help` before first use in a session. Quote every path; names can contain spaces.

## Where definitions live

Keep every definition you build as files in the repo, in the Fabric Git folder format, then import from there:

```
fabric/<Workspace>/
├── nb_load_bronze.Notebook/
│   ├── .platform
│   └── notebook-content.py
├── pl_ingest_bronze_webshop.DataPipeline/
│   ├── .platform
│   └── pipeline-content.json
└── config/
    └── webshop.json          ← files you upload to a lakehouse, not items
```

On the **repo route**, use the Git-connected items folder the repo already has (the one holding `.platform` files) instead of `fabric/<Workspace>/`, and match how existing items there are laid out.

`fab import` sends every file in the item folder as a definition part, so keep only definition files inside it.

## `.platform`

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Notebook",
    "displayName": "nb_load_bronze"
  },
  "config": {
    "version": "2.0",
    "logicalId": "<new GUID>"
  }
}
```

Generate a fresh `logicalId` for each new item (`python -c "import uuid; print(uuid.uuid4())"`). Never copy another item's.

## Lakehouse

```
fab mkdir "<ws>.Workspace/lh_bronze.Lakehouse" -P enableSchemas=true
fab mkdir "<ws>.Workspace/lh_bronze.Lakehouse/Files/raw"
```

`fab mkdir "x.Lakehouse" -P` lists the optional parameters for a type. Schema support is chosen at creation; check the architecture file for whether the pattern wants it.

## Files into a lakehouse

```
fab mkdir "<ws>.Workspace/lh_landing.Lakehouse/Files/webshop"
fab cp ./data/orders.csv "<ws>.Workspace/lh_landing.Lakehouse/Files/webshop/orders.csv"
```

Only upload sample files from `data/`, never production or personal data. `fab cp` from local doesn't prompt; `-f` overwrites an existing file, which counts as destructive.

## Notebook

Get the current format first: Fabric MCP `docs_item-definitions` with `notebook`. The PySpark Git format (`notebook-content.py`) looks like this (shape taken from Microsoft's own samples); the metadata block binds the default lakehouse by ID, so create the lakehouse first and read its ID and the workspace ID with `fab get ... -q id`:

```python
# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "<lakehouse id>",
# META       "default_lakehouse_name": "lh_bronze",
# META       "default_lakehouse_workspace_id": "<workspace id>",
# META       "known_lakehouses": [
# META         { "id": "<lakehouse id>" }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

# ... loader code ...

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
```

Other cell kinds (markdown cells, the **parameters cell** that pipeline parameters bind to) have their own markers. Don't guess them. Copy them from a notebook exported from this tenant (`fab export`, or the repo's Git-connected items). If none has a parameters cell yet: import without it, ask the user to mark the cell as the parameters cell once in the Fabric UI, then `fab export` the notebook and keep that exact marker in the repo copy. Record the marker in `reference/fabric-cli.md` so it's never needed again.

If the repo already has an exported notebook, copy its exact markers and metadata shape in general: that is ground truth for this tenant.

Import (the `.py` format must be named; the CLI's default is `.ipynb`):

```
fab import "<ws>.Workspace/nb_load_bronze.Notebook" -i ./fabric/<ws>/nb_load_bronze.Notebook --format .py -f
```

## Data pipeline

Get the schema first: `docs_item-definitions` with `dataPipeline`, and `docs_api-examples` for a sample. `pipeline-content.json` is `{"properties": {"activities": [...], "parameters": {...}}}`. A notebook activity references the notebook and its workspace by ID:

```json
{
  "name": "Run nb_load_bronze",
  "type": "TridentNotebook",
  "dependsOn": [],
  "typeProperties": {
    "notebookId": "<notebook id>",
    "workspaceId": "<workspace id>",
    "parameters": {
      "source": { "value": "webshop", "type": "string" }
    }
  }
}
```

For activities with complex `typeProperties` (Copy, ForEach with Lookup), don't write them from memory: take the shape from `docs_api-examples`, or ask the user to build one activity in the UI once and `fab export` it as a template. Activity names follow `naming-conventions.md`.

```
fab import "<ws>.Workspace/pl_ingest_bronze_webshop.DataPipeline" -i ./fabric/<ws>/pl_ingest_bronze_webshop.DataPipeline -f
```

## Reading IDs

```
fab get "<ws>.Workspace" -q id
fab get "<ws>.Workspace/lh_bronze.Lakehouse" -q id
```

## Modifying an existing item

1. Export the live definition: `fab export "<ws>.Workspace/<item>.<Type>" -o <temp dir>`
2. Diff it against the new definition in the repo, and show the diff in the plan.
3. After an explicit yes for that item: `fab import ... -f` (this overwrites the live definition).

If the live item differs from the repo copy in ways you didn't make, someone edited it in the UI: stop and ask which version wins.

## Running

Don't use `fab job run --timeout` for long jobs: by default the CLI **cancels the job** when the timeout hits (`job_cancel_ontimeout`). Start it and poll instead:

```
fab job start "<ws>.Workspace/pl_ingest_bronze_webshop.DataPipeline"
fab job run-list "<ws>.Workspace/pl_ingest_bronze_webshop.DataPipeline"
fab job run-status "<ws>.Workspace/pl_ingest_bronze_webshop.DataPipeline" --id <job instance id>
```

Take the instance ID from `run-list` (the newest run). Poll every 30 to 60 seconds; tell the user it's running rather than waiting silently. Pass parameters with `-P name:type=value` (e.g. `-P source:string=webshop`).

For a short job (a small notebook), `fab job run "<path>"` waits for completion; leave `--timeout` off, or set it well above the expected duration.

## Never

- `fab rm --hard`, or `rm` of anything the plan didn't list and the user didn't approve on its own line
- `-f` on a command the user didn't approve in the plan
- writes to a workspace that isn't writable in `environment.md`
- `fab config set` to change the user's CLI behaviour as a workaround
