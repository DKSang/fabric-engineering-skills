# MCP servers

The connections that give the agent live information. Configure only the ones the user chose in Section C, and only for the tools they use (Section A). Always **merge** into existing config files: keep every unrelated server and setting.

| Server | What it gives the agent | Auth | Needs |
| --- | --- | --- | --- |
| `microsoft-learn` | Search and fetch current Microsoft Learn docs and code samples | None | Nothing |
| `fabric-mcp` (local) | Fabric OpenAPI specs, item definition JSON schemas, best practices, OneLake file operations | Azure sign-in, only for the OneLake / live tools | Node.js LTS |
| Microsoft remote Fabric MCPs | FabricIQ (discovery, DAX), Power BI modeling, SQL endpoint queries | Azure CLI sign-in (`az login`) | Azure CLI |
| `fabric-rti-mcp` | Eventhouse / KQL queries, Eventstreams | Azure sign-in | `uv` (Python) |

## Microsoft Learn MCP (always)

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

## Fabric MCP, local (`@microsoft/fabric-mcp`)

Open source, from [microsoft/mcp](https://github.com/microsoft/mcp/tree/main/servers/Fabric.Mcp.Server). The docs tools (`docs_list-item-types`, `docs_item-definitions`, `docs_best-practices`, ...) work offline from bundled specs; the OneLake and core tools act on the live tenant with the user's Azure sign-in, so they fall under the same guardrails as `fab`.

**Claude Code** (`.mcp.json`), **Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "fabric-mcp": {
      "command": "npx",
      "args": ["-y", "@microsoft/fabric-mcp@latest", "server", "start", "--mode", "all"]
    }
  }
}
```

**VS Code**: recommend the [Fabric MCP Server extension](https://marketplace.visualstudio.com/items?itemName=fabric.vscode-fabric-mcp-server) instead of a hand-written entry. Manual entry: same `command`/`args` under `"servers"` with `"type": "stdio"`.

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.fabric-mcp]
command = "npx"
args = ["-y", "@microsoft/fabric-mcp@latest", "server", "start", "--mode", "all"]
```

On Windows, if `npx` fails to start from the tool, use `"command": "cmd"` with `"args": ["/c", "npx", "-y", ...]`.

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
