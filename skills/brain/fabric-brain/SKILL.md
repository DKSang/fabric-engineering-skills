---
name: fabric-brain
description: Keep the repo's Fabric brain (the reference/ folder) current so the user never has to explain the same thing twice. Use when the user explains something durable about their Microsoft Fabric work (tenant, capacities, workspaces, lakehouses, naming conventions, medallion layers, loading patterns, business terms, a gotcha they hit), when the user corrects you about how their Fabric setup works, when you discover a durable fact about their environment, before starting Fabric work that depends on their conventions, or when reading, creating or editing any file under reference/.
---

# Fabric Brain

The **Fabric brain** is the `reference/` folder that every session reads before doing Fabric work. This skill keeps it current: anything durable the user tells you, or that you discover, goes in the right file in the same turn, so the next session already knows it.

This skill owns the layout and the formats of `reference/`. Other skills (setup, build, document) write into it by calling the Skill tool with "fabric-brain".

## Layout

```
reference/
├── environment.md          ← where things live: tenant, capacities, workspaces, scope, key items
├── naming-conventions.md   ← how things are named
├── fabric-cli.md           ← how the agent uses fab here (seeded by setup)
├── architecture/
│   └── <pattern>.md        ← how things are built: one file per pattern
├── lessons.md              ← gotchas already paid for once
├── glossary.md             ← business vocabulary
├── decisions/
│   └── 0001-<slug>.md      ← hard-to-reverse choices
└── workspaces/
    └── <workspace>.md      ← inventory of one workspace (written by document-fabric-workspace)
```

Create a file only when you have a real fact to put in it. Never scaffold empty templates "for later": an empty heading looks like a fact waiting to be invented.

## 1. Read before you work

Before any Fabric task, read the `reference/` files the task touches. They are an index-first read, not a dump:

- Always: `environment.md` (to know the scope) and `naming-conventions.md` (to name anything you create)
- The `architecture/` file for the pattern in play (e.g. `medallion-bronze.md` before building bronze)
- `lessons.md`: scan the headings for the item types and tools you're about to use
- `glossary.md`: when the request uses a business term
- `decisions/`: only records touching the area you're changing
- `workspaces/<ws>.md`: only for the workspaces involved

Use their names and vocabulary verbatim. When a request contradicts them, say so **before** acting, and ask which one wins:

> _`naming-conventions.md` says silver tables are `slv_<entity>`, but you asked for `silver_orders`. Keep the convention, or is this an exception?_

## 2. Capture inline

When the user tells you something durable, record it in the same turn you act on it, then tell them in one line what you wrote and where:

> _Recorded in `naming-conventions.md`: bronze tables keep source column names._

Never batch captures for the end of the session. Sessions end early, context gets compacted, and a fact you meant to write down is lost; that's exactly the re-explaining this skill exists to prevent.

### What's durable

Write it down only if it will still be true next week **and** a future session would otherwise have to ask for it again.

| Durable: capture | Ephemeral: don't |
| --- | --- |
| "Prod workspace is `Sales-PRD`; the agent never touches it." | "Let's try it with 100 rows first." |
| "Bronze loads are SCD2 merges keyed on the source primary key." | "I'm working on the orders notebook today." |
| "The on-prem SQL gateway times out after 10 minutes, so big copies are chunked." | "That last run failed." (unless the cause is a lesson) |
| "'Active customer' means an order in the last 90 days." | Anything already visible in the code or the item definitions |

The task at hand belongs in the conversation, a ticket or a commit, never here.

### Corrections come first

When the user corrects you ("no, that's the old lakehouse", "we don't use schemas there"), that is the single most valuable capture: it's the explanation they least want to give twice. Fix the line that misled you, or add the missing fact if no file covered it.

### Also capture what you discover

Not everything comes from the user. When your own work establishes a durable fact, record it:

- an ID you had to look up (workspace, lakehouse, connection)
- a failure whose cause wasn't obvious, and its fix (goes to `lessons.md`)
- a platform limit or behaviour you verified on Microsoft Learn (goes to `lessons.md`, with the Learn URL)

## 3. Route to the right file

| The fact is about... | Write it to | Format |
| --- | --- | --- |
| Where something lives: tenant, capacity, workspace, item, connection, gateway, stage, scope | `environment.md` | [ENVIRONMENT-FORMAT.md](./ENVIRONMENT-FORMAT.md) |
| How things are named: items, tables, columns, activities, parameters | `naming-conventions.md` | [NAMING-FORMAT.md](./NAMING-FORMAT.md) |
| How a pattern is built: layer rules, load types, metadata columns, config shape, folder layout | `architecture/<pattern>.md` | [ARCHITECTURE-FORMAT.md](./ARCHITECTURE-FORMAT.md) |
| Something that went wrong and how it was fixed; a non-obvious platform limit | `lessons.md` | [LESSONS-FORMAT.md](./LESSONS-FORMAT.md) |
| What a business word means | `glossary.md` | [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md) |
| A choice between real alternatives that is hard to reverse | `decisions/NNNN-<slug>.md` | [DECISION-FORMAT.md](./DECISION-FORMAT.md) |
| How to run `fab` here: flags that work, a CLI quirk | `fabric-cli.md` (its `## Gotchas` section) | keep the existing shape |
| The contents of one workspace | `workspaces/<ws>.md` | owned by `document-fabric-workspace`; update a single line you know changed, and suggest re-running `/document-fabric-workspace` for anything bigger |

If a fact fits nowhere, it's probably not durable. Don't write it.

When you create a new file (a first `architecture/` pattern, the first `lessons.md`), add one line for it to the `## Reference` list in `AGENTS.md`, inside the `fabric-engineering-skills` marker block. That index line is the only thing that ever goes into `AGENTS.md`; knowledge never does.

## 4. Keep it trustworthy

A stale brain is worse than no brain, because it's trusted.

- **Verify environment facts.** A workspace name, an item's existence, a table's columns: check them against the tenant with read-only tools (`fab ls`, `fab exists`, `fab get`, Fabric MCP `onelake_*` tools) before recording. If you can't check, append `(unverified)`.
- **Verify platform facts.** Anything about what Fabric supports gets checked on Microsoft Learn (`microsoft_docs_search`) and cited with the URL.
- **One fact, one place.** Update the existing line instead of adding a near-duplicate somewhere else. Link rather than repeat.
- **Delete what became false.** When a workspace is renamed or a convention changes, edit the line; don't leave the old one alongside.
- **Stay terse.** Tables and bullets, no narratives, no dates-and-feelings diary. If a file passes ~300 lines, split it (e.g. one `architecture/` file per layer).
- **Don't commit on your own.** Leave `reference/` changes in the working tree; the user reviews them in the diff like any other change.

## Never write

- **Secrets**: client secrets, passwords, keys, SAS tokens, access tokens, connection strings with credentials. Record where the secret lives instead ("Key Vault `kv-data-prd`, secret `sql-reader`").
- **Personal data** from tables. Describe columns and their meaning; never paste rows about people.

IDs (tenant, capacity, workspace, item GUIDs) are not secrets and save the agent lookups. Record them unless `environment.md` or the user says otherwise.

## Decisions: sparingly

Offer a decision record only when all three hold: the choice is **hard to reverse**, a future reader would be **surprised** by it, and there were **real alternatives**. "Lakehouse over Warehouse for gold" qualifies. "Renamed a notebook" does not. Ask before writing one.
