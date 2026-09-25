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
| **Connections** | `.mcp.json` (Microsoft Learn MCP, Fabric MCP), Fabric CLI `fab` | Live information: current docs, and the ability to build and run things in Fabric |
| **Workflows** | skills like the ones in this repo | The things you repeat all the time |

## Quick start

### 1. Install the skills

<details open>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add DKSang/fabric-engineering-skills
claude plugin install fabric-engineering-skills@fabric-engineering
```

</details>

<details>
<summary><strong>Codex, Copilot, Cursor and other agents</strong></summary>

```bash
npx skills@latest add DKSang/fabric-engineering-skills
```

This copies the skill files into your project so you can edit them.

</details>

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
5. **Install** the Fabric CLI and the chosen MCP servers
6. **Hand sign-in to you**: you run `fab auth login` (and `az login` if needed) in your own terminal. The agent never sees your password or secret
7. **Verify**, read-only: signed in, right tenant, workspaces visible, MCP servers actually answering. You get a pass/fail table with a fix for each failure

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
├── .mcp.json                         ← Microsoft Learn MCP (+ Fabric MCP if chosen)
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

## Skills

### Setup

**User-invoked**

- **[setup-fabric-engineering-skills](./skills/setup/setup-fabric-engineering-skills/SKILL.md)**: Turn this repo into a Fabric brain: write `AGENTS.md` and pointer files, seed `reference/`, install the Fabric CLI and MCP servers, walk you through sign-in, then verify every connection. Run once per repo; `verify` re-checks any time.

### Roadmap

Planned next, building on the brain the setup creates:

| Skill | Job |
| --- | --- |
| `fabric-brain` | Capture durable facts into `reference/` the moment you explain them |
| `verify-fabric-claims` | Check Fabric feature claims against Microsoft Learn before stating them |
| `build-in-fabric` | Plan from `reference/`, dry run, build in the allowed workspace, verify, end-to-end test, fix, re-run |
| `fabric-item-definitions` | Read and safely modify Git-connected item definitions (notebooks, pipelines, lakehouses) |
| `document-fabric-workspace` | Inventory a workspace into `reference/workspaces/<name>.md` |
| `fabric-guardrails` | A hook that blocks `fab` writes outside the allowed workspaces |
| `fabric-retro` | End-of-session sweep: what did we learn that the brain should keep? |

## Related

- [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric): Microsoft's workload skills (Spark, SQL, KQL, semantic models, ...). Complementary: this repo sets up *your* context; theirs teaches the workloads. The setup can install their plugin for you.
- [Fabric CLI docs](https://aka.ms/fabric-cli), [Microsoft Learn MCP](https://github.com/MicrosoftDocs/mcp), [Fabric MCP server](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server)
- Inspired by Aleksi Partanen's [My AI Setup for Microsoft Fabric: Never Explain Yourself Twice](https://youtu.be/5-sXBbBJbAk), and structured after [mattpocock/skills](https://github.com/mattpocock/skills).
