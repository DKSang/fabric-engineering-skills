# Fabric CLI (`fab`)

The Fabric CLI is how the agent creates, inspects and runs things in Fabric: workspaces, lakehouses, notebooks, pipelines, jobs, tables. Package `ms-fabric-cli`, command `fab`. Docs: <https://aka.ms/fabric-cli>.

## Install

Requires Python 3.10 to 3.13.

| Situation | Command |
| --- | --- |
| `pipx` available (recommended: isolated, on PATH) | `pipx install ms-fabric-cli` |
| `uv` available | `uv tool install ms-fabric-cli` |
| Neither | `python -m pip install --user ms-fabric-cli` |
| Already installed, upgrade | `pipx upgrade ms-fabric-cli` / `uv tool upgrade ms-fabric-cli` / `pip install --upgrade ms-fabric-cli` |

Confirm with `fab --version`. If the command isn't found after a `--user` install, the user's scripts folder isn't on PATH: on Windows, `%APPDATA%\Python\Python3xx\Scripts`; on macOS/Linux, `~/.local/bin`. Tell the user to add it; don't edit their shell profile without asking.

## Choosing an identity

`fab` acts as whoever signs in, and so does the agent. Recommend in this order:

| Identity | When | Notes |
| --- | --- | --- |
| **Service principal** with Contributor on only the writable workspace(s) | Anything beyond a personal playground | The strongest guardrail: the agent physically can't touch what the principal can't see. Needs an Entra app registration, and the tenant setting "Service principals can use Fabric APIs" enabled for it. |
| **Own user account** | Personal playground tenant, or when a service principal isn't possible | The agent sees everything the user sees. If the user is a Fabric or tenant admin, say so plainly and recommend a playground tenant or a least-privilege identity. |
| **Managed identity** | The agent runs on Azure compute (VM, container) | `fab auth login --identity` |

Written guardrails in `AGENTS.md` limit what the agent *should* do. The identity limits what it *can* do. Both matter.

## Sign-in

The user runs this **themselves**, in the environment where the agent runs (same OS, same WSL distro or container):

```
fab auth login
```

It opens a menu:

- **Interactive with a web browser**: user account. Opens the browser.
- **Service principal authentication with secret / certificate / federated credential**: prompts for tenant ID, client ID and the secret. The secret is typed into a hidden prompt, which is why the user runs it and not the agent.
- **Managed identity authentication**

Avoid `fab auth login -u <id> -p <secret> --tenant <tenant>` on a shared machine: the secret lands in shell history. For unattended use (CI), `fab` also reads `FAB_SPN_CLIENT_ID`, `FAB_SPN_CLIENT_SECRET` and `FAB_TENANT_ID` from the environment; those belong in the CI secret store, never in the repo.

Check the result without exposing anything: `fab auth status`. It prints the account, tenant ID and principal ID; tokens are masked to their first four characters.

Sign out: `fab auth logout`.

## Node.js and Azure CLI

Both are required by Fabric MCP: Node.js runs it (`npx`), and its live tools take their token from the Azure CLI sign-in, which is separate from `fab`'s. Microsoft's remote Fabric MCPs use the same Azure CLI sign-in.

| OS | Node.js LTS | Azure CLI |
| --- | --- | --- |
| Windows | `winget install --exact --id OpenJS.NodeJS.LTS` | `winget install --exact --id Microsoft.AzureCLI` |
| macOS | `brew install node` | `brew install azure-cli` |
| Linux | <https://nodejs.org/en/download/package-manager> | <https://learn.microsoft.com/cli/azure/install-azure-cli-linux> |

After installing, the user usually needs a new terminal (and a restart of the AI tool) before `node` and `az` are on PATH.

Sign in (user runs it): `az login`, or `az login --tenant <tenant-id> --allow-no-subscriptions` when the tenant has no Azure subscription. Both `fab` and `az` must point at the **same tenant**; [VERIFY.md](./VERIFY.md) checks this.

## Permission rules

Claude Code only: merge into `.claude/settings.json`. Read-only `fab` commands run without a prompt; anything that can change Fabric always asks, even in auto-accept modes. The `fab api` and `fab job` families stay on "ask" because the same command can read or write depending on its flags.

```json
{
  "permissions": {
    "allow": [
      "Bash(fab --version)",
      "Bash(fab auth status:*)",
      "Bash(fab ls:*)",
      "Bash(fab dir:*)",
      "Bash(fab exists:*)",
      "Bash(fab get:*)",
      "Bash(fab desc:*)",
      "Bash(fab pwd)",
      "Bash(fab config ls)",
      "Bash(fab job run-status:*)",
      "Bash(fab job run-list:*)",
      "Bash(npx -y @microsoft/fabric-mcp@latest docs:*)",
      "Bash(npx -y @microsoft/fabric-mcp@latest onelake list-workspaces:*)",
      "Bash(az --version)",
      "Bash(az account show:*)"
    ],
    "ask": [
      "Bash(fab mkdir:*)",
      "Bash(fab rm:*)",
      "Bash(fab mv:*)",
      "Bash(fab cp:*)",
      "Bash(fab set:*)",
      "Bash(fab import:*)",
      "Bash(fab export:*)",
      "Bash(fab bulk-export:*)",
      "Bash(fab ln:*)",
      "Bash(fab assign:*)",
      "Bash(fab unassign:*)",
      "Bash(fab start:*)",
      "Bash(fab stop:*)",
      "Bash(fab acl:*)",
      "Bash(fab label:*)",
      "Bash(fab table:*)",
      "Bash(fab job:*)",
      "Bash(fab api:*)",
      "Bash(fab auth login:*)",
      "Bash(fab auth logout:*)",
      "Bash(fab config set:*)",
      "Bash(az account get-access-token:*)"
    ]
  }
}
```

`fab export` is on "ask" because it can also write into a lakehouse (`-o /ws.Workspace/lh.Lakehouse/Files/...`). `az account get-access-token` is on "ask" because its default output is a live token.

## Seed for `reference/fabric-cli.md`

Write this in step 4, then fill the version and sign-in method after [VERIFY.md](./VERIFY.md) passes.

```md
# Fabric CLI notes

- **Version**: {fab --version}
- **Signed in as**: {identity type and display name, e.g. "service principal sp-fabric-dev" or "developer's own account"}. Never write the secret.
- **Docs**: https://aka.ms/fabric-cli. Run `fab <command> --help` before using a command for the first time in a session; flags change between versions.

## Paths

- Workspace: `"<Workspace name>.Workspace"`; item: `"<Workspace>.Workspace/<Item>.<Type>"` (e.g. `"Sales-DEV.Workspace/lh_sales_bronze.Lakehouse"`).
- Quote every path; names can contain spaces.
- Lakehouse content: `.../<Lakehouse>.Lakehouse/Files/...` and `.../<Lakehouse>.Lakehouse/Tables/<schema>/<table>`.

## Everyday commands

| Task | Command |
| --- | --- |
| List workspaces / items | `fab ls` / `fab ls "<ws>.Workspace" -l` |
| Does it exist? | `fab exists "<ws>.Workspace/<item>.<Type>"` |
| Properties (IDs etc.) | `fab get "<ws>.Workspace/<item>.<Type>" -q id` |
| What can I do with this? | `fab desc .<Type>` |
| Export a definition to local files | `fab export "<ws>.Workspace/<item>.<Type>" -o ./<folder>` |
| Run and wait | `fab job run "<ws>.Workspace/<item>.<Type>"` |
| Check a run | `fab job run-status "<ws>.Workspace/<item>.<Type>" --id <job-id>` |
| Raw REST call | `fab api -X get workspaces` |

## Gotchas

(Add here whenever `fab` surprises us: the error, the cause, the fix.)
```
