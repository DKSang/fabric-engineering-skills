---
name: setup-fabric-engineering-skills
description: "Set up this repo as a Fabric brain for AI: write AGENTS.md and pointer files, seed reference/ docs, install the Fabric CLI and MCP servers, then walk the user through sign-in and verify every connection. Run once per repo; re-run with `verify` after restarting the agent."
argument-hint: "[verify]"
disable-model-invocation: true
---

# Setup Fabric Engineering Skills

Turn the current repo into a **Fabric brain**: a folder that any AI tool reads at the start of a session so it already knows the user's projects, conventions and guardrails, and can reach live Fabric and up-to-date docs. The user should never have to explain themselves twice.

The setup has four pieces:

- **Instruction file**: `AGENTS.md`, the canonical file every tool reads, plus tiny pointer files for tools that use their own name (`CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`)
- **Reference files**: `reference/`, the knowledge (environment, naming conventions, architecture, CLI notes)
- **Connections**: the Fabric CLI (`fab`) and two required MCP servers, **Microsoft Learn MCP** and **Fabric MCP**, plus optional extras
- **Guardrails**: which workspaces the agent may touch, and what needs confirmation

This is a prompt-driven skill, not a script. Explore, present what you found, confirm with the user, write, install, hand sign-in to the user, then verify.

## Modes

- **No argument**: run the full process below.
- **`verify`**: skip to [step 7](#7-verify). Use it after a restart (new MCP servers only load in a new session), or any time later to re-check the setup.

## Process

### 1. Explore

Read what exists; don't assume. Run read-only checks only.

**The repo**

- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`, `.cursor/rules/`: which exist? Does any already hold a `<!-- fabric-engineering-skills:start -->` block from a previous run?
- `reference/`, `data/`: prior output of this skill, or the user's own notes?
- `.mcp.json`, `.vscode/mcp.json`, `.cursor/mcp.json`, `.claude/settings.json`: existing MCP servers and permissions. You will merge into these, never overwrite them.
- Fabric item folders: any directory containing `.platform` files (`<Name>.<Type>/.platform`) means the repo is Git-connected to a workspace. Note the root folder and the item types present.
- `git remote -v`: GitHub, Azure DevOps, or none.

**The machine** (see [FABRIC-CLI.md](./FABRIC-CLI.md) and [MCP-SERVERS.md](./MCP-SERVERS.md) for what each tool is for)

- OS and shell (Windows PowerShell, WSL, macOS, Linux). A Windows sign-in is not visible inside WSL or a dev container; note where the agent actually runs.
- `python --version` / `python3 --version` (the Fabric CLI needs Python 3.10 or newer)
- `pipx --version`, `uv --version` (preferred installers for CLI tools)
- `fab --version` and, if present, `fab auth status`
- `node --version`, `npx --version` (**required**: Fabric MCP runs through `npx`)
- `az --version` and, if present, `az account show --query "{tenant:tenantId, user:user.name}" -o json` (**required**: Fabric MCP's live tools authenticate through the Azure CLI sign-in)
- Which AI tools are in use: you are running inside one; also look for `.claude/`, `.vscode/`, `.cursor/`, `.codex/`, `~/.codex/config.toml`.

### 2. Present findings and ask

Summarise what's present and what's missing in a short table. Then take the sections in order: **one section, one answer, then the next.** Lead each with the recommended answer so the user can accept it in a word. Skip a section when exploration already settled it.

**Section A: AI tools.**

> Explainer: `AGENTS.md` is the open standard most AI coding tools read. Tools with their own file name get a one-line pointer to it, so the knowledge lives in your files, not inside any single tool.

Recommend: `AGENTS.md` + pointers for every tool found in step 1. Offer: Claude Code (`CLAUDE.md`), GitHub Copilot (`.github/copilot-instructions.md`), Gemini CLI (`GEMINI.md`), Cursor (`.cursor/rules/agents.mdc`), Codex (reads `AGENTS.md` natively, no pointer). See [POINTERS.md](./POINTERS.md).

**Section B: Guardrails and scope.**

> Explainer: The agent will act with whatever identity you sign in with. Written guardrails keep it honest, but what really limits it is what that identity can access. These rules tell it which workspaces it may change.

Ask, in order, one at a time:

1. Which workspace(s) may the agent **create or modify** items in? (recommend: one DEV or playground workspace). Record exact names.
2. Are there workspaces it may **read** but never change (e.g. PRD)? (recommend: yes, every other workspace is read-only)
3. Keep the default safety rules? (recommend: **yes**: dry run first, confirm every destructive or write operation, never print secrets or tokens)
4. Run Fabric MCP read-only? (recommend: **yes**: the agent still reads OneLake, tables and schemas through it, but every change goes through `fab`, where each one asks you first). See [MCP-SERVERS.md](./MCP-SERVERS.md#arguments).

**Section C: Connections (MCP servers).** See [MCP-SERVERS.md](./MCP-SERVERS.md).

> Explainer: Every model has a training cutoff, and Fabric ships features monthly. MCP servers let the agent look things up live instead of guessing.

Two servers are **required** and installed on every run; don't ask whether to add them, only tell the user they're coming:

- **Microsoft Learn MCP** (`microsoft-learn`): official, free, no authentication. Powers the standing rule "verify Fabric claims against Microsoft Learn".
- **Fabric MCP** (`fabric-mcp`, local): Fabric API specs, item definition schemas and best practices (work offline), plus live OneLake and workspace tools (use the Azure CLI sign-in). It is what lets the agent build item definitions that match the real schema instead of guessing. It needs Node.js and the Azure CLI; if either is missing, step 5 installs it before anything else.

If the user objects to a required server, explain what they lose (no live docs means confident wrong answers about new features; no Fabric MCP means guessed item schemas) and that the setup is not complete without it. If they still refuse, stop and tell them to re-run the skill when they're ready; don't write a half setup.

Then offer the optional ones:

- **Microsoft Fabric remote MCPs** (FabricIQ, Power BI modeling, SQL endpoint): offer when the user works with semantic models or SQL endpoints. Needs Azure CLI sign-in. On Claude Code, recommend installing Microsoft's `fabric-skills` plugin, which configures them, rather than copying entries by hand.
- **Fabric RTI MCP**: offer only when the user mentions Eventhouse, KQL or Real-Time Intelligence.

**Section D: Fabric CLI sign-in identity.** See [FABRIC-CLI.md](./FABRIC-CLI.md#choosing-an-identity).

> Explainer: `fab` is how the agent creates and runs things in Fabric. It uses the identity you sign in with, so anything that identity can see, the agent can see.

Recommend, in this order: a **service principal** with Contributor on only the writable workspace(s) from Section B; otherwise **interactive sign-in with the user's own account**, restricted by the guardrails. Warn plainly if the user's account is a Fabric or tenant admin and recommend a playground tenant or a least-privilege identity instead. Do not collect secrets in chat; the user types them into `fab` directly.

**Section E: Reference files.** Call the Skill tool with "fabric-brain": it owns the layout and formats of `reference/`. Setup seeds three files and a folder; the rest (`lessons.md`, `glossary.md`, `decisions/`, `workspaces/`) appear later, when there is something real to write:

```
reference/
├── environment.md          ← tenant, scope, workspaces (filled from Section B and step 7)
├── naming-conventions.md   ← how things are named
├── fabric-cli.md           ← how the agent uses fab here (seed in FABRIC-CLI.md)
└── architecture/           ← one file per pattern, created when the user describes one
data/                       ← sample files the agent may use during development
```

Ask, one at a time:

1. _"Do you already have naming conventions or architecture notes written down somewhere (wiki, doc, another repo)?"_ If yes, read them (with permission) and convert them into `fabric-brain`'s formats instead of starting blank.
2. If not: _"Want a starter set of naming conventions to edit?"_ (recommend: **yes**). Show `fabric-brain`'s starter set and write only what the user keeps. Never record invented conventions as fact.
3. _"Is there a pattern you always build the same way (e.g. your bronze layer, a metadata-driven loader)? Describe it in a few sentences."_ If yes, write `reference/architecture/<pattern>.md`. If no, skip; it can come later.

### 3. Confirm

Show the user a draft of:

- The `AGENTS.md` block (from [AGENTS-TEMPLATE.md](./AGENTS-TEMPLATE.md)), filled in with Sections A to E
- Each pointer file
- The MCP entries to merge into each config file, and the permission rules for `.claude/settings.json` (Claude Code only)
- The `reference/` seeds, in `fabric-brain`'s formats

Let them edit before anything is written.

### 4. Write

- **`AGENTS.md`**: if it exists, insert or replace only the region between `<!-- fabric-engineering-skills:start -->` and `<!-- fabric-engineering-skills:end -->`; never touch the user's text outside it. If it doesn't exist, create it with the block.
- **Pointer files**: same marker rule. If a `CLAUDE.md` already has real content, keep it and add the pointer block at the top.
- **MCP config**: merge the chosen servers into the existing JSON/TOML. Keep every unrelated server and setting. If a server with the same name already exists and works, leave it alone and tell the user.
- **`.claude/settings.json`** (Claude Code only): merge the permission rules from [FABRIC-CLI.md](./FABRIC-CLI.md#permission-rules). Keep existing rules.
- **`reference/`**: write seeds only for files that don't exist yet, in `fabric-brain`'s formats. `environment.md` gets the scope table from Section B now; IDs come in step 7. Put only facts the user confirmed; leave out sections you don't know rather than filling them with placeholders.
- **`data/`**: create it with a one-line `README.md` ("Sample files for development. No production or personal data.").
- **`.gitignore`**: append `.env` and `*.local.json` if missing. Never write a secret into any file.

### 5. Install

Install what is required or chosen and missing. Required first, in this order: Node.js, Azure CLI, Fabric CLI; then the MCP config is already in place from step 4. Show each command, then run it with the user's approval. Follow [FABRIC-CLI.md](./FABRIC-CLI.md#install) and [MCP-SERVERS.md](./MCP-SERVERS.md).

- Fabric CLI: `pipx install ms-fabric-cli` (or `uv tool install ms-fabric-cli`, or `pip install --user ms-fabric-cli`). Confirm with `fab --version`.
- **Node.js LTS** and **Azure CLI** (both required): these need an OS installer (winget, Homebrew, apt). Give the user the exact command for their OS from [FABRIC-CLI.md](./FABRIC-CLI.md#nodejs-and-azure-cli); run it only if they ask you to. Confirm with `node --version` and `az --version` before moving on; an installer usually needs a new terminal before the command is on PATH.
- Warm the Fabric MCP package so the first session doesn't time out on download: `npx -y @microsoft/fabric-mcp@latest --help`.
- Claude Code plugin for Microsoft's remote MCPs (if chosen in Section C): `claude plugin marketplace add microsoft/skills-for-fabric` then `claude plugin install fabric-skills@fabric-collection`.

If an install fails, stop and show the error. Don't try alternative installers silently.

### 6. Hand sign-in to the user

You cannot complete an interactive sign-in for the user, and you must never see their password or secret. Tell them exactly what to run, **in their own terminal**, then wait for them to say they're done:

```
fab auth login          # the Fabric CLI; choose the identity agreed in Section D
az login                # the Fabric MCP; sign in as the same identity, same tenant
```

Both are required: `fab` and Fabric MCP keep separate sign-ins. When the tenant has no Azure subscription, use `az login --tenant <tenant-id> --allow-no-subscriptions`. For a service principal, the user runs `az login --service-principal --help` and signs in with the same principal as `fab`.

Claude Code users can also type `! fab auth login` in the prompt, but a separate terminal is more reliable for the interactive menu and the browser pop-up. If the agent runs in WSL or a container, the sign-in must happen **there**, not on the Windows host. See [FABRIC-CLI.md](./FABRIC-CLI.md#sign-in).

Then tell them: new MCP servers only load in a new session. Ask them to **restart the agent** (or reload the MCP servers) and run `/setup-fabric-engineering-skills verify`. If they would rather continue now, run the parts of step 7 that don't need the new MCP servers and mark the rest as "pending restart".

### 7. Verify

Run the checks in [VERIFY.md](./VERIFY.md). Every check is **read-only**: never create, change, or delete anything in Fabric to prove a connection works.

Report the result as one table: check, result (pass / fail / skipped / pending restart), and for each failure the fix from VERIFY.md's troubleshooting section. Fix what you can with the user's approval (a missing config entry, a wrong path) and re-run just that check. Anything that needs the user (a sign-in, an admin install, a tenant setting) goes back to them with the exact command.

When the checks pass, record what you verified, and only that:

- `reference/environment.md`: tenant ID, the signed-in identity type (not the secret), each in-scope workspace with its ID and whether the agent may write to it
- `reference/fabric-cli.md`: the CLI version and sign-in method that worked

### 8. Done

Tell the user:

- what was written (a short file list) and what was verified
- how to start: open a new session and ask for a Fabric task without restating their conventions; the agent reads `AGENTS.md` first
- that `reference/` is theirs to grow: whenever they explain or correct something durable, the agent records it there in the same turn (the `fabric-brain` skill), so the brain gets smarter every session. They review those changes in the Git diff like any other change
- that re-running this skill is only needed to change tools, scope or MCP servers; `/setup-fabric-engineering-skills verify` re-checks the connections any time
