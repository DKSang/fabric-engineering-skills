# Fabric Engineering Skills

Agent skills that turn any repo into a **Fabric brain**: a folder your AI reads at the start of every session, so it already knows your Microsoft Fabric projects, naming conventions, guardrails and the latest Fabric features. You never explain yourself twice.

[Tiếng Việt](./README.vi.md)

Works with Claude Code, GitHub Copilot, Codex, Cursor and Gemini CLI. The knowledge lives in plain files (`AGENTS.md` + `reference/`), not inside any one tool, so it moves with you when you switch.

## Why

The bottleneck for AI-assisted Fabric development is no longer model intelligence, it is **context**. A fresh chat doesn't know your workspaces, your naming conventions, your medallion architecture or what your team decided last month. So it gives generic answers, you correct it, and tomorrow it has forgotten everything again.

The fix is the same one you'd use for a new consultant: an onboarding package. A Fabric brain has four pieces:

| Piece | Files | Job |
| --- | --- | --- |
| **Instruction file** | `AGENTS.md` (+ one-line pointers: `CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`) | How the agent behaves: guardrails, standing rules, where the knowledge is |
| **Reference files** | `reference/environment.md`, `naming-conventions.md`, `fabric-cli.md`, `architecture/*.md` | What you know: your tenant, conventions, patterns |
| **Connections** | Fabric CLI `fab`, and in `.mcp.json` the required **Microsoft Learn MCP** and **Fabric MCP** | Live information: current docs, real item schemas, OneLake, and the ability to build and run things in Fabric |
| **Workflows** | skills like the ones in this repo | The things you repeat all the time |

## Quick start

### 1. Install the skills

**Requirements**: an AI coding tool (Claude Code, Codex, GitHub Copilot, Cursor, Gemini CLI, ...) and Git. The setup skill installs the rest for you (Python 3.10 to 3.13 for the Fabric CLI, Node.js LTS and the Azure CLI for Fabric MCP) or tells you the exact command for your OS.

Pick **one** route; installing both gives you every skill twice.

<details open>
<summary><strong>Claude Code (recommended): plugin</strong></summary>

A managed bundle that updates when a new version ships. From a terminal:

```bash
claude plugin marketplace add DKSang/fabric-engineering-skills
claude plugin install fabric-engineering-skills@fabric-engineering
```

Or from inside a session:

```
/plugin marketplace add DKSang/fabric-engineering-skills
/plugin install fabric-engineering-skills@fabric-engineering
```

**For a whole team**, declare it in the repo instead, so everyone who opens the repo is offered the plugin:

```bash
claude plugin marketplace add DKSang/fabric-engineering-skills --scope project
claude plugin install fabric-engineering-skills@fabric-engineering --scope project
```

and commit `.claude/settings.json`.

Skills are namespaced by the plugin: `/setup-fabric-engineering-skills` works, and so does `/fabric-engineering-skills:setup-fabric-engineering-skills` if another skill has the same name.

</details>

<details>
<summary><strong>Codex, GitHub Copilot, Cursor and other agents: <code>npx skills</code></strong></summary>

Copies the skill folders into your project (`.agents/skills/`, `.claude/skills/`, ...) as ordinary files you own and can edit:

```bash
npx skills@latest add DKSang/fabric-engineering-skills
```

The installer asks which skills and which agents. Non-interactive, all skills, chosen agents:

```bash
npx skills@latest add DKSang/fabric-engineering-skills --skill '*' --agent codex github-copilot cursor -y
```

Add `-g` to install for your user instead of this project.

</details>

<details>
<summary><strong>Manual</strong></summary>

Clone the repo and copy (or symlink) each folder under `skills/*/` that contains a `SKILL.md` into your agent's skills folder: `.claude/skills/` for Claude Code, `.agents/skills/` for Codex and other Agent Skills-compatible tools. Keep each folder whole: some skills ship files and scripts next to their `SKILL.md`.

</details>

<details>
<summary><strong>Update, uninstall</strong></summary>

| Route | Update | Uninstall |
| --- | --- | --- |
| Claude Code plugin | `claude plugin marketplace update fabric-engineering` then `claude plugin update fabric-engineering-skills@fabric-engineering`, or enable auto-update in `/plugin` → Marketplaces | `claude plugin uninstall fabric-engineering-skills@fabric-engineering` |
| `npx skills` | `npx skills update` | `npx skills remove` |
| Manual | `git pull` in your clone (symlinks pick it up) | delete the folders |

Uninstalling the skills leaves everything they wrote in your repo (`AGENTS.md`, `reference/`, MCP config) in place: that's your Fabric brain, and it keeps working without the skills.

</details>

**Check the install**: start a new session and type `/setup-fabric-engineering-skills`. If the command isn't offered, restart the tool; for the plugin route, `claude plugin list` should show `fabric-engineering-skills` as enabled.

### 2. Run `/setup-fabric-engineering-skills`

Run it once in the repo you want to turn into a Fabric brain. It will:

1. **Explore** the repo and your machine: existing instruction files, MCP configs, Fabric item folders, and whether Python, `fab`, Node and `az` are installed
2. **Ask** a few questions, one at a time, each with a recommended answer:
   - which AI tools you use
   - which workspaces the agent may modify (everything else stays read-only)
   - which MCP servers to connect
   - which identity `fab` should sign in as
3. **Show you a draft** of everything it will write, and let you edit it
4. **Write** `AGENTS.md`, the pointer files, `reference/`, `data/`, and merge MCP servers and permission rules into your existing config
5. **Install** Node.js, the Azure CLI and the Fabric CLI if missing, and connect the two required MCP servers: **Microsoft Learn MCP** (current docs) and **Fabric MCP** (item schemas, API specs, OneLake; read-only by default so every change goes through `fab`). Other Fabric MCPs are optional
6. **Hand sign-in to you**: you run `fab auth login` and `az login` in your own terminal. The agent never sees your password or secret
7. **Verify**, read-only: signed in, same tenant for `fab` and `az`, workspaces visible, both MCP servers actually answering. You get a pass/fail table with a fix for each failure

New MCP servers load only in a new session, so restart your agent and run:

```
/setup-fabric-engineering-skills verify
```

### 3. Start building

Open a new session and ask for Fabric work without restating your conventions:

> Set up my metadata-driven bronze layer for the orders data in my dev workspace and walk me through what you built.

The agent reads `AGENTS.md`, pulls your naming and architecture rules from `reference/`, checks current Fabric behaviour against Microsoft Learn, builds only in the workspace you allowed, and offers an end-to-end test. Whenever you explain something new, it records it in `reference/`, so the brain gets better every session.

## What the setup writes

```
your-repo/
├── AGENTS.md                         ← canonical instructions (guardrails, standing rules, index)
├── CLAUDE.md                         ← pointer: @AGENTS.md
├── .github/copilot-instructions.md   ← pointer (if you use Copilot)
├── GEMINI.md                         ← pointer (if you use Gemini CLI)
├── .mcp.json                         ← Microsoft Learn MCP + Fabric MCP (required)
├── .claude/settings.json             ← fab read commands allowed, write commands always ask
├── reference/
│   ├── environment.md                ← tenant, workspaces, what's in scope
│   ├── naming-conventions.md
│   ├── fabric-cli.md
│   └── architecture/                 ← one file per pattern you use
└── data/                             ← sample files for development
```

It merges into files you already have and never overwrites your own content: everything it owns sits between `<!-- fabric-engineering-skills:start -->` and `<!-- fabric-engineering-skills:end -->` markers.

## Safety

The agent acts as whoever signs in to `fab`. Written guardrails keep it honest, but **the identity is what really limits it**.

- Prefer a **service principal** with access to only your dev workspace. If you use your own account and you're a Fabric admin, the agent can see everything you can; use a playground tenant.
- Read-only `fab` commands run freely; anything that can change Fabric asks you first.
- The safest workflow of all: let the agent edit item definitions in a Git-connected repo, and sync them to Fabric yourself.
- Git restores **definitions** (notebooks, pipelines, item settings), not **data**: files in a lakehouse, Delta tables, and items deleted with `--hard` don't come back from Git. That's why every destructive command needs its own yes.

## Skills

### Setup

**User-invoked**

- **[setup-fabric-engineering-skills](./skills/setup/setup-fabric-engineering-skills/SKILL.md)**: Turn this repo into a Fabric brain: write `AGENTS.md` and pointer files, seed `reference/`, install the Fabric CLI and MCP servers, walk you through sign-in, then verify every connection. Run once per repo; `verify` re-checks any time.

### Brain

**User-invoked**

- **[document-fabric-workspace](./skills/brain/document-fabric-workspace/SKILL.md)**: Inventory a workspace into `reference/workspaces/<ws>.md`: items, tables and schemas, what each notebook and pipeline does, and the lineage between them. Incremental: a state file with fingerprints (item IDs, repo definition hashes, table timestamps) means a re-run reads only what's new, changed or stale. Read-only against Fabric.
- **[fabric-retro](./skills/brain/fabric-retro/SKILL.md)**: Run before closing a session. Finds corrections, lessons, uncaptured facts and stale lines the brain should know about, proposes each one with its evidence, and applies only what you pick.

**Model-invoked**

- **[fabric-brain](./skills/brain/fabric-brain/SKILL.md)**: Read the relevant `reference/` files before Fabric work, and record every durable fact you explain or correct (conventions, environment facts, gotchas, business terms) in the right file, in the same turn. Owns the layout and formats of `reference/`.

User-invoked skills fire only when you type them; model-invoked skills are also picked up by the agent on its own when the task fits.

### Build

**Model-invoked**

- **[build-in-fabric](./skills/build/build-in-fabric/SKILL.md)**: Turn "set up my bronze layer for the orders data in dev" into working items: load your conventions, research current formats on Fabric MCP and Microsoft Learn, present a dry-run plan for your yes, build only in the writable workspace (directly with `fab`, or as definitions in your Git-connected repo), verify, then run an end-to-end test that checks the data and fixes failures.

## License

MIT. See [LICENSE](./LICENSE). Release notes are in [CHANGELOG.md](./CHANGELOG.md).

## Related

- [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric): Microsoft's workload skills (Spark, SQL, KQL, semantic models, ...). Complementary: this repo sets up *your* context; theirs teaches the workloads. The setup can install their plugin for you.
- [Fabric CLI docs](https://aka.ms/fabric-cli), [Microsoft Learn MCP](https://github.com/MicrosoftDocs/mcp), [Fabric MCP server](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server)
- Inspired by Aleksi Partanen's [My AI Setup for Microsoft Fabric: Never Explain Yourself Twice](https://youtu.be/5-sXBbBJbAk), and structured after [mattpocock/skills](https://github.com/mattpocock/skills).
