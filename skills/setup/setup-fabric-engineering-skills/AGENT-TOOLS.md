# Agent tools

What setup configures for each AI tool the user **picks** in Section A. Nothing here is configured for a tool the user didn't pick, even if its folder exists in the repo.

| # | Tool | Instruction file | MCP config (Section C) | Skills folder | `fab` permission rules |
| --- | --- | --- | --- | --- | --- |
| 1 | Claude Code | pointer `CLAUDE.md` | `.mcp.json` (project) | `.claude/skills/` or the plugin | `.claude/settings.json` |
| 2 | DeepSeek Harness (`dsh`) | reads `AGENTS.md` natively | overlay `.dsh/fabric-engineering.cordis.yml`, loaded with `--patch`, or merged into `~/.dsh/cordis.patch.yml` | `.dsh/skills/` or `.agents/skills/` | none; see below |
| 3 | Codex | reads `AGENTS.md` natively | `~/.codex/config.toml` (user, outside the repo) | `.agents/skills/` | none |
| 4 | GitHub Copilot (VS Code) | pointer `.github/copilot-instructions.md` | `.vscode/mcp.json` | `.agents/skills/` | none |
| 5 | Cursor | pointer `.cursor/rules/agents.mdc` | `.cursor/mcp.json` | `.agents/skills/` | none |
| 6 | Gemini CLI | pointer `GEMINI.md` | `.gemini/settings.json` | `.agents/skills/` | none |

`AGENTS.md` itself is always written: it's the one source of truth every tool reaches, natively or through its pointer. Skills folders are where `npx skills add` puts these skills for each tool; setup doesn't install skills, it only tells the user the right `--agent` value (`claude-code`, `codex`, `github-copilot`, `cursor`, `gemini-cli`, and `universal` for dsh) if they're missing.

## How to ask

Show the table above as a numbered list and mark:

- **(running now)** on the tool executing this setup. It is the default and the only pre-selected one.
- **(found)** on tools whose folders or config exist in the repo or home directory (step 1).

Then ask: _"Which tools should I configure? (default: only the one running now; give numbers, e.g. `1, 2`)"_

Rules:

- **Never pre-select a tool just because its folder exists.** A stray `.vscode/` doesn't mean the user wants Copilot configured.
- **One answer covers the whole setup.** Pointers (POINTERS.md), MCP config (MCP-SERVERS.md), permission rules and verification (VERIFY.md) are done for the picked tools only.
- **Config outside the repo** (Codex's `~/.codex/config.toml`, dsh's `~/.dsh/cordis.patch.yml`) is the user's personal config: show the exact change and ask before writing it, separately from the repo files.
- **Adding a tool later** is a re-run of this skill: it keeps everything in place and adds the new tool's files.

## DeepSeek Harness (`dsh`)

[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) is in developer preview; its config format can change between releases. What setup relies on:

- **Instructions**: dsh loads every `AGENTS.md` and `CLAUDE.md` it finds from the project root down to the working directory (identical copies once), so it needs no pointer file. A Claude Code pointer in the same repo just adds its two lines.
- **Skills**: dsh discovers skills in `.dsh/skills/` and `.agents/skills/` of the project, and in `~/.dsh/skills/` and `~/.agents/skills/`. It honours `disable-model-invocation`, and the user runs a skill by typing `/<name>`, so these skills work unchanged. `npx skills add ... --agent universal` installs into `.agents/skills/`.
- **MCP**: dsh has no project MCP file it reads on its own. Servers are `@deepseek-ai/dsh-mcp-client` rows in a Cordis patch. Setup writes them to `.dsh/fabric-engineering.cordis.yml` in the repo (see MCP-SERVERS.md) and offers two ways to load it:

  | Option | How | When |
  | --- | --- | --- |
  | Per launch (recommended for a shared repo) | `dsh web --patch "$PWD/.dsh/fabric-engineering.cordis.yml"` (or `dsh --profile tui --patch ...`) | the repo carries the config; nothing outside it changes |
  | Every launch on this machine | merge the file's `insert` rows into `~/.dsh/cordis.patch.yml` (`$DSH_HOME/cordis.patch.yml`) | the user always works on Fabric; ask first, and merge rather than overwrite: the file may hold other patches |

- **Permission rules**: the `.claude/settings.json` rules don't apply to dsh. Say so plainly: the guardrails in `AGENTS.md`, `build-in-fabric`'s plan gate, and a least-privilege `fab` identity (Section D) are what limit it, plus whatever approval or sandbox settings the user runs dsh with.
- **Stdio environment**: dsh strips ambient variables whose names contain `KEY`, `PASSWORD`, `SECRET` or `TOKEN` before starting a stdio server, then adds the row's own `env`. That's why the Fabric MCP row sets `AZURE_TOKEN_CREDENTIALS` explicitly; the Azure CLI sign-in itself lives in `~/.azure` and isn't affected.
- **Windows**: dsh starts stdio servers without a shell, so use `npx.cmd` instead of `npx` as the `command`.
