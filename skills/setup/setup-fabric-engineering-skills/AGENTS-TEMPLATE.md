# AGENTS.md template

The block that goes into the user's `AGENTS.md`. Fill every `{...}` from the answers in step 2; delete any line whose answer was "not applicable". Keep it short: this file is loaded in every session, so each line costs context forever. Knowledge goes in `reference/`, not here.

Everything between the markers is owned by this skill and replaced on re-run. Text outside the markers belongs to the user.

```md
<!-- fabric-engineering-skills:start -->
# Fabric brain

This folder is the second brain for {project or team} Microsoft Fabric development. It carries our conventions, projects and rules into every AI session, so nobody has to explain them twice. Read this file at the start of every session. It is the canonical instruction file for any AI tool working in this folder.

## Start of session

Before any Fabric work, read the `reference/` files relevant to the task (index below). Use their names and vocabulary verbatim. If a request contradicts them, say so before acting.

## Guardrails

- **Scope.** You may create or modify items only in: {writable workspaces, exact names}. Every other workspace is read-only. {PRD workspaces} are never modified, even if asked casually; ask for explicit confirmation naming the workspace.
- **Dry run first.** Before any write, show the exact commands or definition changes you will run, and what they will create, change or delete.
- **Confirm destructive operations.** Never delete, overwrite, move or re-permission an item without an explicit yes for that specific operation. Never use `--force` / `-f` to skip a prompt.
- **Secrets.** Never print, log or write tokens, passwords, client secrets or connection strings. Don't run commands that print access tokens.
- **Identity.** `fab` runs as {identity: e.g. "service principal sp-fabric-dev" or "the developer's own account"}. Treat everything that identity can see as sensitive.

## Verify before you claim

Fabric changes monthly and your training data has a cutoff. Before stating that Fabric supports (or doesn't support) a feature, setting, API or limit, verify it against Microsoft Learn using the `microsoft-learn` MCP server and cite the page. If you can't verify it, say so.

## Build, verify, test

1. Plan from `reference/` (naming, architecture) and confirm the plan.
2. Build in the writable workspace only, following the guardrails.
3. Verify each item exists and matches the plan (`fab ls`, `fab get`).
4. Offer an end-to-end test: run it, check the output data, and if it fails, diagnose, fix, and re-run. Report what failed and why.

## Keep the brain current

When the user explains something durable (a convention, an environment fact, a gotcha, a correction), update the right `reference/` file in the same turn and say in one line what you recorded. Never record secrets.

## Reference

- `reference/environment.md`: tenant, capacities, workspaces, what is in scope
- `reference/naming-conventions.md`: how items, tables, columns and activities are named
- `reference/fabric-cli.md`: how to use `fab` in this repo
- `reference/architecture/`: one file per pattern we use {list the files, e.g. `medallion-bronze.md`}

## Folders

- `data/`: sample files for development. Never production or personal data.
{- `{fabric items root}/`: Fabric item definitions, Git-connected to {workspace}. Edit these files instead of the live workspace when possible; the user syncs them through Git.}

## Tools

- **Fabric CLI** (`fab`): create, inspect and run items. Notes in `reference/fabric-cli.md`.
- **Microsoft Learn MCP** (`microsoft-learn`): current Microsoft documentation.
{- **Fabric MCP** (`fabric-mcp`): Fabric API specs, item definition schemas, best practices, OneLake.}
{- other MCP servers chosen in setup, one line each}
<!-- fabric-engineering-skills:end -->
```

## Filling rules

- **Exact names.** Workspace names go in exactly as Fabric shows them. A near-miss makes the scope rule useless.
- **One writable workspace is the norm.** If the user lists more than two, ask once whether they're sure.
- **No knowledge in `AGENTS.md`.** If you're tempted to paste a naming rule or an architecture description here, it belongs in `reference/` with a pointer from the index.
- **Drop, don't placeholder.** If a line doesn't apply (no Git-connected items, no Fabric MCP), delete it. Never leave `{...}` in the written file.
