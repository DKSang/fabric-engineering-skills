---
name: build-in-fabric
description: Build or change Microsoft Fabric items (lakehouses, notebooks, pipelines, folders, files) from the repo's conventions, then verify them and offer an end-to-end test that runs, checks the data, and fixes failures. Use when the user asks to create, build, set up, scaffold, implement or change something in a Fabric workspace, e.g. "set up my bronze layer for the orders data in dev", "create a pipeline that loads X", "add a notebook that...", or asks to test what was built.
---

# Build in Fabric

Turn a request like _"set up my metadata-driven bronze layer for the orders data in my dev workspace"_ into working items in Fabric, built the way the team builds things, without the user restating a single convention. Then prove it works.

The loop is **plan, dry run, build, verify, test, fix**, with a user gate before anything changes. Every phase below ends with a clear output; don't skip ahead.

## Before you start

Stop and tell the user what's missing if any of these fail:

- `AGENTS.md` and `reference/` exist. If not: _"This repo isn't set up yet; run `/setup-fabric-engineering-skills` first."_
- `fab auth status` shows `Logged In: True`. If not, hand sign-in to the user (`fab auth login` in their terminal); never sign in for them.
- The target workspace is **writable** in `reference/environment.md`'s scope table. If it's read-only or not listed, don't build there, even if asked casually. Say which workspaces are writable and that changing scope is an edit to `environment.md` and `AGENTS.md` the user makes deliberately.

## 1. Load context

Call the Skill tool with "fabric-brain" and read what the task touches:

- `environment.md`: exact workspace name and ID, existing key items, connections
- `naming-conventions.md`: the name of everything you're about to create
- `architecture/<pattern>.md`: the pattern being built (bronze layer, metadata framework, ...)
- `lessons.md`: anything about the item types involved
- `data/`: sample files the task mentions (e.g. `data/orders.csv`)

**If the pattern isn't documented**, don't invent one. Ask the user to describe it in a few sentences (layers, load type, metadata columns, config shape), record it in `architecture/<pattern>.md` through `fabric-brain`, then continue. An invented framework looks plausible and is wrong in the ways that matter.

## 2. Research

Your training data is older than Fabric. For every item type and feature involved:

- **Definition format**: call Fabric MCP `docs_item-definitions` for each item type you will write (e.g. `notebook`, `dataPipeline`, `lakehouse`), and `docs_api-examples` when a sample helps. Write definitions from these, never from memory.
- **Behaviour claims**: check anything you're about to rely on (an activity type, a notebook utility, a lakehouse feature, a limit) with `microsoft_docs_search` / `microsoft_docs_fetch`. Keep the URLs for the report.
- **What exists**: `fab ls "<ws>.Workspace" -l`. An item with the same name turns "create" into "modify" (see [RECIPES.md](./RECIPES.md#modifying-an-existing-item)).
- **Commands**: `fab <command> --help` for any command you haven't used this session. [RECIPES.md](./RECIPES.md) has the verified patterns.

If Fabric MCP or Microsoft Learn MCP isn't available in this session, say so at the top of the plan ("Not verified on Learn: MCP unavailable"), design around anything you couldn't check (prefer shapes already verified in RECIPES.md), and suggest `/setup-fabric-engineering-skills verify` to the user.

## 3. Plan and dry run (gate)

Present the plan and **wait for an explicit yes**. The plan is the dry run: it shows exactly what will change.

```md
## Plan: bronze layer for webshop orders in Sales-DEV

Route: direct (build in the workspace with fab)

| # | Action | Item / path | How |
| --- | --- | --- | --- |
| 1 | create | lh_landing.Lakehouse | fab mkdir |
| 2 | create | lh_config.Lakehouse | fab mkdir |
| 3 | create | lh_bronze.Lakehouse (schemas on) | fab mkdir -P enableSchemas=true |
| 4 | upload | lh_landing/Files/webshop/orders.csv | fab cp from data/orders.csv |
| 5 | upload | lh_config/Files/webshop/webshop.json | fab cp from fabric/Sales-DEV/config/webshop.json |
| 6 | create | nb_load_bronze.Notebook | fab import from fabric/Sales-DEV/nb_load_bronze.Notebook |
| 7 | create | pl_ingest_bronze_webshop.DataPipeline | fab import (after 6, needs its ID) |

Won't touch: everything else in Sales-DEV; every other workspace.
Conventions applied: naming-conventions.md (lh_, nb_, pl_), architecture/medallion-bronze.md (raw/<source>/<dataset>/<ts>/, SCD2, _ metadata columns).
Verified on Learn: <urls>
Test plan: run pl_ingest_bronze_webshop once, check files and table (see E2E-TEST.md).
```

Rules for the plan:

- **Dependency order.** Lakehouses before notebooks (a notebook's default lakehouse is an ID); notebooks before pipelines (an activity references the notebook's ID).
- **Every name** comes from `naming-conventions.md`. Name the rule you applied when it isn't obvious.
- **Modifications show a diff** of the current definition against the new one.
- **Nothing destructive by default.** A plan that deletes or overwrites anything lists it on its own line, marked **destructive**, and needs its own yes.

### Choose the route

Ask once, recommending based on the repo:

| Situation | Recommend | What happens |
| --- | --- | --- |
| Workspace is Git-connected to this repo (`environment.md`, or `.platform` folders) | **Repo route** | Write the item definitions into the repo's items folder. The user reviews the diff, commits, and syncs the workspace from Git ("Update all"). No direct writes. Test after they sync. |
| Workspace isn't Git-connected | **Direct route** | Keep the definitions in `fabric/<Workspace>/` in this repo as the source of truth, and import them with `fab`. |

On the direct route to a Git-connected workspace, warn that the workspace will show uncommitted changes against its branch.

## 4. Build

Execute the plan in order, one step at a time. Follow [RECIPES.md](./RECIPES.md).

- **Definitions live in files first.** Write each notebook, pipeline and config into the repo (`fabric/<Workspace>/<Item>.<Type>/...`), then import or upload from there. The repo then holds a reviewable copy of everything built.
- **Resolve IDs as you go.** After creating an item that others reference, read its ID (`fab get "<ws>.Workspace/<item>.<Type>" -q id`) and write it into the dependent definition before importing that one.
- **No hard-coded environment in code.** Workspace and lakehouse names or IDs in notebook code break as soon as the code runs in another context. Pass them as parameters from the pipeline, or resolve them at runtime; bind the default lakehouse in the notebook's metadata, not in code.
- **`-f` only for the approved step.** `fab import` always asks its own "Are you sure?" and the agent's shell can't answer it, so an import needs `-f`. Use it only for an import the user approved in step 3, and never `rm --hard`.
- **Stop on the first failure.** Show the error, check `lessons.md` and Learn, propose a fix, and get a yes before retrying. Never "try something else" silently.

## 5. Verify

Read-only checks that each item matches the plan:

| Check | How |
| --- | --- |
| Each item exists, with the planned name | `fab exists`, `fab ls "<ws>.Workspace"` |
| Properties are right (e.g. lakehouse schemas enabled) | `fab get ... -q <property>` |
| Files are where the pattern says | `fab ls ".../Files/<path>"` |
| Definitions round-trip | `fab export` to a temp folder and compare with the repo copy |

Report what passed. Fix any mismatch before offering the test.

## 6. Offer an end-to-end test (gate)

Building isn't done until it has run. Offer the test and say what it will do: which job runs, what data it writes and where (writable workspace only), and roughly how long. Wait for a yes, then follow [E2E-TEST.md](./E2E-TEST.md): run, check the output data, and on failure diagnose, fix, re-run.

## 7. Report and capture

Tell the user what was built, in this shape:

```md
## Built in Sales-DEV

| Item | Type | Purpose |
| --- | --- | --- |
| lh_bronze | Lakehouse | raw files under Files/raw, tables per source schema |
| nb_load_bronze | Notebook | config-driven SCD2 loader |
| pl_ingest_bronze_webshop | DataPipeline | copy files, then run the loader |

**Run flow**: pipeline copies landing files to Files/raw/webshop/orders/<ts>/, then runs nb_load_bronze with source=webshop.
**Test**: passed on the 2nd run; webshop.orders has 30 rows with all metadata columns.
**First run failed because**: <cause, fix>.
**Repo changes** (not committed): fabric/Sales-DEV/..., reference/lessons.md
**Verified on Learn**: <urls>
```

Then call the Skill tool with "fabric-brain" to capture what this build taught you: the cause of any failure that wasn't obvious (`lessons.md`), new key items (`environment.md`), and any convention the user clarified along the way. Leave all repo changes uncommitted for the user to review.
