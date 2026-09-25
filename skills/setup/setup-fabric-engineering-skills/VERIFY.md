# Verify

Prove each piece works, **read-only**. Never create, change or delete anything in Fabric to test a connection. Never run a command that prints a token.

Run the checks in order; a later check is meaningless if an earlier one failed. Skip checks for pieces the user didn't choose. Report one table at the end.

## Checks

### Files

| # | Check | Pass when |
| --- | --- | --- |
| F1 | `AGENTS.md` has the `fabric-engineering-skills` marker block, with no `{...}` placeholders left | block present, no `{` placeholders |
| F2 | Each chosen pointer file exists and points to `AGENTS.md` | all present |
| F3 | `reference/environment.md`, `reference/naming-conventions.md`, `reference/fabric-cli.md` exist | all present |
| F4 | Every MCP config file written in step 4 parses (JSON/TOML) | parses |
| F5 | `git status --porcelain` and a scan of the written files show no secrets (no `Bearer ey`, `client_secret`, `password=`, `AccountKey=`) | nothing found |

### Fabric CLI

| # | Check | Command | Pass when |
| --- | --- | --- | --- |
| C1 | Installed | `fab --version` | prints a version |
| C2 | Signed in | `fab auth status` | `Logged In: True`; note `Account` and `Tenant ID` |
| C3 | Can reach the Fabric API | `fab ls` | lists at least one workspace, no `AuthenticationFailed` |
| C4 | Each writable workspace from Section B exists and is visible | `fab exists "<ws>.Workspace"` | `true` for each |
| C5 | Capture IDs for the brain | `fab get "<ws>.Workspace" -q id` | returns a GUID for each in-scope workspace |
| C6 | Identity is not broader than agreed | `fab ls` count vs. what the user expects | if a service principal was chosen and it sees workspaces outside Section B's scope, **flag it** (it has more access than planned) |

C4 checks visibility only. It does not prove write permission, and you must not test write permission by writing. If the user wants that confirmed, ask them to check the identity's role in the workspace's **Manage access** pane.

### Node.js and Azure CLI (required by Fabric MCP)

| # | Check | Command | Pass when |
| --- | --- | --- | --- |
| N1 | Node installed | `node --version` | v20 or newer |
| A1 | Azure CLI installed | `az --version` | prints a version |
| A2 | Signed in | `az account show --query "{tenant:tenantId, user:user.name}" -o json` | returns a tenant |
| A3 | Same tenant as `fab` | compare A2 `tenant` with C2 `Tenant ID` | identical |
| A4 | Can get a Fabric token | `az account get-access-token --resource https://api.fabric.microsoft.com --query expiresOn -o tsv` | prints an expiry time (the `--query expiresOn` is what keeps the token itself out of the output; never drop it) |

### MCP servers (need a new session after setup)

If the current session started before the MCP config was written, mark these **pending restart** and tell the user to restart and run `/setup-fabric-engineering-skills verify`.

| # | Check | How | Pass when |
| --- | --- | --- | --- |
| M1 | Server registered and connected | Claude Code: `claude mcp list` (and ask the user to glance at `/mcp`). Codex: `/mcp`. VS Code: **MCP: List Servers**. | each chosen server shows connected / running |
| M2 | Microsoft Learn answers | call `microsoft_docs_search` with `"Microsoft Fabric lakehouse schemas"` | returns results with `learn.microsoft.com` URLs |
| M3 | Fabric MCP answers (required) | call `docs_list-item-types` | returns item types including `lakehouse` and `notebook` |
| M4 | Fabric MCP reaches the tenant (required) | call `onelake_list-workspaces` | lists the writable workspaces from Section B, no auth error |
| M5 | Fabric MCP is read-only (if agreed in Section B) | look at the tool list | no `create`, `upload`, `delete` tools (e.g. no `core_create-item`, `onelake_delete-file`) |
| M6 | Remote Fabric MCPs (if chosen) | call a read-only discovery tool the server exposes (e.g. FabricIQ artifact search for a workspace from Section B) | returns data, no auth error |

Installation success is not connection success. Only an actual tool call counts for M2 to M6.

**Before a restart**, Fabric MCP can still be checked from the terminal, because the same package runs one-off commands. Run these instead of M3 and M4, and keep M1 and M5 as "pending restart":

```
npx -y @microsoft/fabric-mcp@latest docs list-item-types
AZURE_TOKEN_CREDENTIALS=AzureCliCredential npx -y @microsoft/fabric-mcp@latest onelake list-workspaces
```

(PowerShell: `$env:AZURE_TOKEN_CREDENTIALS="AzureCliCredential"; npx -y @microsoft/fabric-mcp@latest onelake list-workspaces`.) Pinning the credential matters here: without it the command line may open a browser sign-in instead of using `az`.

**Setup is not complete** until M2, M3 and M4 pass. Say so plainly in the report if they don't.

### Guardrails

| # | Check | Pass when |
| --- | --- | --- |
| G1 | Restate the rules: read `AGENTS.md` and list, in one line each, the writable workspaces, the read-only ones, and when you must ask for confirmation | matches what the user agreed in Section B |
| G2 | Claude Code: `.claude/settings.json` has the `ask` rules for `fab` write commands | present |

## Report

```md
| Check | Result | Detail |
| --- | --- | --- |
| C2 Signed in | pass | user@contoso.com, tenant 1234... |
| C4 Sales-DEV exists | pass | |
| A3 Same tenant | fail | fab: 1234..., az: 9876... → run `az login --tenant 1234...` |
| M2 Learn MCP | pending restart | restart, then `/setup-fabric-engineering-skills verify` |
```

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `fab: command not found` | Scripts folder not on PATH after a `--user` install | Add it to PATH (see FABRIC-CLI.md), or reinstall with `pipx` |
| `Logged In: False` | Not signed in, or signed in on another environment (Windows host vs. WSL, host vs. container) | User runs `fab auth login` where the agent runs |
| `[AuthenticationFailed] Failed to get access token` | Sign-in expired, or service principal secret wrong or expired | User runs `fab auth logout`, then `fab auth login` again |
| `fab ls` works but a workspace is missing (C4 false) | Name typo (case, spaces, suffix), or the identity has no role on it | Compare with `fab ls` output exactly; if absent, the user grants the identity a role on the workspace |
| Service principal gets `Unauthorized` / `PrincipalTypeNotSupported` | Tenant setting "Service principals can use Fabric APIs" is off for it, or it has no workspace role | A Fabric admin enables the setting for its security group; add it to the workspace |
| A3 tenant mismatch | `az` defaulted to another tenant | `az login --tenant <tenant-id> --allow-no-subscriptions` |
| `az login` fails with "no subscriptions found" | Tenant has Fabric but no Azure subscription | Add `--allow-no-subscriptions` |
| M4 fails with a credential error | `az login` missing where the agent runs, or signed in to another tenant | Fix A2 and A3; the MCP reads the Azure CLI sign-in only (pinned by `AZURE_TOKEN_CREDENTIALS`) |
| M4 works but a writable workspace is missing | The Azure CLI identity differs from the `fab` identity | Sign `az` in as the same user or principal as `fab` |
| First Fabric MCP start times out | `npx` downloading the package during the first session | Run `npx -y @microsoft/fabric-mcp@latest --help` once, then restart |
| MCP server not listed | Session started before the config was written, or config in the wrong file for this tool | Restart the tool; check the path against MCP-SERVERS.md |
| Claude Code shows the project server as disabled | Project-scoped servers need approval | User approves it in `/mcp` |
| `npx` server fails to start on Windows | Tool can't spawn `npx` directly | Use `"command": "cmd"`, `"args": ["/c", "npx", ...]` |
| Remote MCP connects, every call fails | Azure sign-in missing where the client runs, or an older registration with the same name overrides the plugin's | Fix A2 to A4 first; then remove the stale entry (with the user's approval) |
| Learn MCP times out | Corporate proxy or firewall blocks `learn.microsoft.com/api/mcp` | User allows the host, or configures the tool's proxy settings |
