# Brain

Keep the Fabric brain (`reference/`) current, so the agent already knows what you'd otherwise explain every session.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[document-fabric-workspace](./document-fabric-workspace/SKILL.md)**: Inventory a workspace into `reference/workspaces/<ws>.md` (items, tables and schemas, what each notebook and pipeline does, lineage). Incremental: a state file with fingerprints means re-runs read only what changed. Read-only against Fabric.
- **[fabric-retro](./fabric-retro/SKILL.md)**: End-of-session sweep for corrections, lessons, uncaptured facts and stale lines the brain should know about. Proposes each change; applies only what you pick.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the agent reaches for them on its own).

- **[fabric-brain](./fabric-brain/SKILL.md)**: Read the relevant `reference/` files before Fabric work, and record every durable fact the user explains (or you discover) in the right file, in the same turn. Owns the layout and formats of `reference/`.
