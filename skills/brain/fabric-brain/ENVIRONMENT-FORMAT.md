# environment.md format

Where things live, and what the agent may touch. The agent reads this to turn "the sales lakehouse in dev" into an exact path it can pass to `fab` or an MCP tool, and to know whether it may change it.

## Template

```md
# Fabric environment

## Tenant

- **Tenant ID**: `00000000-0000-0000-0000-000000000000`
- **Home region**: West Europe
- **Agent identity**: service principal `sp-fabric-dev` (no secrets here)

## Scope

| Workspace | ID | Stage | Agent may write? |
| --- | --- | --- | --- |
| Sales-DEV | `...` | DEV | yes, after a dry run and confirmation |
| Sales-TST | `...` | TEST | only when asked explicitly, naming the workspace |
| Sales-PRD | `...` | PRD | never |

Every workspace not listed here is out of scope: read only if the task needs it, never modify.

## Capacities

| Capacity | SKU | Region | Used by |
| --- | --- | --- | --- |
| cap-data-dev | F8 | West Europe | Sales-DEV, Sales-TST |
| cap-data-prd | F64 | West Europe | Sales-PRD |

## Key items

| Item | Workspace | Type | Purpose |
| --- | --- | --- | --- |
| lh_landing | Sales-DEV | Lakehouse | mock source system for development |
| lh_config | Sales-DEV | Lakehouse | metadata framework configs, `Files/<source>/*.json` |
| lh_bronze | Sales-DEV | Lakehouse | schema-enabled; `Files/raw/`, one schema per source |

## Connections and gateways

| Name | Kind | Points at | Credential lives in |
| --- | --- | --- | --- |
| conn-erp-sql | On-prem gateway | ERP SQL Server | Key Vault `kv-data`, secret `erp-reader` |

## Source control and deployment

- `Sales-DEV` is Git-connected to this repo, folder `fabric/`, branch `main`.
- Promotion DEV -> TEST -> PRD through deployment pipeline `dp-sales`.
```

## Rules

- **Scope is mandatory.** Every workspace the agent knows about has a stage and a write policy. This table is what stops an agent from editing prod.
- **Exact names.** Copy names as Fabric shows them, including case and spaces. The `fab` path is `"<Workspace>.Workspace/<Item>.<Type>"`, so one wrong character is a failed call, or worse, a different item.
- **IDs when known.** They make MCP and REST calls exact. Get them read-only: `fab get "<ws>.Workspace" -q id`.
- **Tables over prose.** The agent scans for one row.
- **No secrets.** Point to where a credential lives, never the credential.
- **Drop what doesn't apply.** A single-workspace playground needs the tenant and one scope row, not this whole template.
