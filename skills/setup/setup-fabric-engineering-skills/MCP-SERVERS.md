# MCP servers

The connections that give the agent live information. Two are **required** on every setup; the rest are optional and configured only when chosen in Section C. Configure each for the tools the user uses (Section A). Always **merge** into existing config files: keep every unrelated server and setting.

| Server | Required? | What it gives the agent | Auth | Needs |
| --- | --- | --- | --- | --- |
| `microsoft-learn` | **yes** | Search and fetch current Microsoft Learn docs and code samples | None | Nothing |
| `fabric-mcp` (local) | **yes** | Fabric OpenAPI specs, item definition JSON schemas, best practices, examples (offline); OneLake files and tables, workspaces and items (live) | Azure CLI sign-in, for the live tools | Node.js LTS, Azure CLI |
| Microsoft remote Fabric MCPs | optional | FabricIQ (discovery, DAX), Power BI modeling, SQL endpoint queries | Azure CLI sign-in | Azure CLI |
| `fabric-rti-mcp` | optional | Eventhouse / KQL queries, Eventstreams | Azure sign-in | `uv` (Python) |

Only write config for the tools picked in Section A. File locations per tool are in [AGENT-TOOLS.md](./AGENT-TOOLS.md).

## Microsoft Learn MCP (required)

Endpoint: `https://learn.microsoft.com/api/mcp` (streamable HTTP, no auth). Tools: `microsoft_docs_search`, `microsoft_docs_fetch`, `microsoft_code_sample_search`.

**Claude Code**: project scope, `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

(Equivalent CLI: `claude mcp add --transport http --scope project microsoft-learn https://learn.microsoft.com/api/mcp`.) Claude Code asks the user to approve project-scoped servers the first time; tell them to accept. Prefer this project entry over the `microsoft-docs` plugin from the official marketplace: it is committed with the repo, so teammates and other tools get the same connection.

**VS Code (Copilot)**: `.vscode/mcp.json` (note the root key is `servers`):

```json
{
  "servers": {
    "microsoft-learn": {
      "type": "http",
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

**Cursor**: `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "url": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

**Codex**: user config `~/.codex/config.toml` (Codex has no project-level MCP file; ask before editing a file outside the repo):

```toml
[mcp_servers.microsoft-learn]
url = "https://learn.microsoft.com/api/mcp"
```

(Equivalent CLI: `codex mcp add microsoft-learn --url https://learn.microsoft.com/api/mcp`.)

**DeepSeek Harness (`dsh`)**: one `@deepseek-ai/dsh-mcp-client` row per server in the overlay `.dsh/fabric-engineering.cordis.yml` (the Fabric MCP row below goes in the same `insert` list; see [DeepSeek Harness](#deepseek-harness-dsh) for the complete file):

```yaml
- insert:
    - id: fabric-engineering-microsoft-learn
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: microsoft-learn
        transport: streamable-http
        url: https://learn.microsoft.com/api/mcp
```

**Gemini CLI**: `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "microsoft-learn": {
      "httpUrl": "https://learn.microsoft.com/api/mcp"
    }
  }
}
```

## Fabric MCP, local (required)

Package `@microsoft/fabric-mcp`, open source in [microsoft/mcp](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server). Tool groups:

| Group | Examples | Touches the tenant? |
| --- | --- | --- |
| `docs` | `list-item-types`, `item-definitions`, `item-api-spec`, `best-practices`, `api-examples` | no, bundled specs, no auth |
| `onelake` | `list-workspaces`, `list-items`, `list-files`, `list-tables`, `upload-file`, `delete-file` | yes |
| `core`, `datafactory` | `create-item`, list and run pipelines, dataflows | yes |

### Arguments

```
npx -y @microsoft/fabric-mcp@latest server start --mode all --read-only
```

- `--mode all` exposes every tool individually (names like `docs_list-item-types`), which models pick more reliably than the default one-tool-per-group mode.
- `--read-only` blocks every write tool. **Default: on.** Writes then go through `fab`, where each one hits a permission prompt and the guardrails, so there is one audited path that changes Fabric. Drop the flag only if the user explicitly wants the MCP to write (Section B).

### Authentication

Running as an MCP server, Fabric MCP never opens a browser; it takes an existing sign-in from a chain (environment variables, Visual Studio, VS Code, Azure CLI, ...). Pin it to the Azure CLI with `AZURE_TOKEN_CREDENTIALS=AzureCliCredential` so it uses the same, verified identity as `az login` and never silently picks a VS Code account from another tenant.

### Config

**Claude Code** (`.mcp.json`), **Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "fabric-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/fabric-mcp@latest", "server", "start", "--mode", "all", "--read-only"],
      "env": {
        "AZURE_TOKEN_CREDENTIALS": "AzureCliCredential"
      }
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`): the same entry under `"servers"` with `"type": "stdio"`. The [Fabric MCP Server extension](https://marketplace.visualstudio.com/items?itemName=fabric.vscode-fabric-mcp-server) is an alternative, but a committed `mcp.json` keeps the flags and the server name identical for the whole team.

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.fabric-mcp]
command = "npx"
args = ["-y", "@microsoft/fabric-mcp@latest", "server", "start", "--mode", "all", "--read-only"]
env = { AZURE_TOKEN_CREDENTIALS = "AzureCliCredential" }
```

**Gemini CLI** (`.gemini/settings.json`): same `command`, `args` and `env` under `"mcpServers"`.

**DeepSeek Harness (`dsh`)**: a stdio row in the same overlay; see below.

On Windows, if the tool can't spawn `npx` directly, use `"command": "cmd"` with `"args": ["/c", "npx", "-y", ...]`.

### Also a command line

The same package runs one-off commands in a terminal, which is how [VERIFY.md](./VERIFY.md) checks it before a restart:

```
npx -y @microsoft/fabric-mcp@latest docs list-item-types
npx -y @microsoft/fabric-mcp@latest onelake list-workspaces
```

## DeepSeek Harness (`dsh`)

dsh reads MCP servers from Cordis patch rows, not from a JSON file. Write this overlay to `.dsh/fabric-engineering.cordis.yml` (merge rows into it if it exists):

```yaml
# Fabric Engineering Skills: MCP servers for DeepSeek Harness.
# Load with: dsh web --patch "$PWD/.dsh/fabric-engineering.cordis.yml"
- insert:
    - id: fabric-engineering-microsoft-learn
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: microsoft-learn
        transport: streamable-http
        url: https://learn.microsoft.com/api/mcp
    - id: fabric-engineering-fabric-mcp
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: fabric-mcp
        transport: stdio
        command: npx
        args: ['-y', '@microsoft/fabric-mcp@latest', 'server', 'start', '--mode', 'all', '--read-only']
        env:
          AZURE_TOKEN_CREDENTIALS: AzureCliCredential
```

- `serverName` must match `[A-Za-z0-9_-]{1,32}` and be unique; tools appear as `mcp__<serverName>__<tool>` (e.g. `mcp__fabric-mcp__docs_list-item-types`).
- On Windows use `command: npx.cmd`: dsh starts stdio servers without a shell.
- Loading: per launch with `--patch` (recommended; nothing outside the repo changes), or merged into `~/.dsh/cordis.patch.yml` so every launch has it. Ask before touching the home file, and merge its `insert` rows rather than overwriting it.
- dsh validates rows at boot: a malformed row stops dsh with `invalid config` and names the row's `id`, so a wrong field shows up immediately.

## Microsoft remote Fabric MCPs

FabricIQ, Power BI modeling and SQL endpoint servers, maintained in [microsoft/skills-for-fabric](https://github.com/microsoft/skills-for-fabric/blob/main/mcp-setup/README.md). They authenticate with the Azure CLI token for `https://api.fabric.microsoft.com`.

**Claude Code: install Microsoft's plugin** (recommended; it also brings workload skills for Spark, SQL, KQL, semantic models and more, and wires the auth header for you):

```bash
claude plugin marketplace add microsoft/skills-for-fabric
claude plugin install fabric-skills@fabric-collection
```

Don't also copy these servers into `.mcp.json`: a project entry with the same name overrides the plugin's.

**Codex, VS Code**: follow Microsoft's [MCP setup guide](https://github.com/microsoft/skills-for-fabric/blob/main/mcp-setup/README.md) verbatim. Their VS Code route pastes a short-lived token into a prompted input; tell the user that it expires and must be refreshed, and that it must never be written into the file.

## Fabric RTI MCP (only if the user works with Eventhouse / KQL)

From [microsoft/fabric-rti-mcp](https://github.com/microsoft/fabric-rti-mcp). Ask the user for their Eventhouse query URI and default database.

```json
{
  "mcpServers": {
    "fabric-rti-mcp": {
      "command": "uvx",
      "args": ["microsoft-fabric-rti-mcp"],
      "env": {
        "KUSTO_SERVICE_URI": "{eventhouse query URI}",
        "KUSTO_SERVICE_DEFAULT_DB": "{database}"
      }
    }
  }
}
```

## Rules

- **Merge, never overwrite.** Read the file, add the entry, write it back with everything else intact.
- **No tokens in files.** No `Authorization` header with a literal token in any committed file. Remote servers get their token from a helper or a prompted input.
- **Names matter.** `AGENTS.md` refers to these servers by name (`microsoft-learn`, `fabric-mcp`). Keep the names consistent across tools.
- **Restart to load.** A new server is only visible in a new session. Say so, and verify after the restart ([VERIFY.md](./VERIFY.md)).
