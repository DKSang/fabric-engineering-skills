# Setup

Run-once scaffolding: turn a repo into a Fabric brain and connect it to Fabric.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[setup-fabric-engineering-skills](./setup-fabric-engineering-skills/SKILL.md)**: Write `AGENTS.md` and pointer files, seed `reference/`, install the Fabric CLI and MCP servers, walk the user through sign-in, then verify every connection. Run once per repo; `verify` re-checks any time.
