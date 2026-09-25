# Changelog

Every release bumps `version` in `.claude-plugin/plugin.json` and adds a section here; that version change is what lets Claude Code offer the update to installed users.

## 0.1.0

First release.

- `setup-fabric-engineering-skills`: turn a repo into a Fabric brain (`AGENTS.md` and pointer files, `reference/`, Fabric CLI, Microsoft Learn MCP and Fabric MCP), hand sign-in to the user, then verify every connection read-only. `verify` re-checks any time.
- `fabric-brain`: read the relevant `reference/` files before Fabric work and capture every durable fact the user explains or corrects, in the same turn.
- `document-fabric-workspace`: inventory a workspace into `reference/workspaces/<ws>.md`, incrementally: a state file with fingerprints means re-runs read only what changed.
- `fabric-retro`: end-of-session sweep for corrections, lessons, uncaptured facts and stale lines; applies only what the user picks.
- `build-in-fabric`: plan, dry run, build in the writable workspace, verify, and end-to-end test with diagnose-fix-rerun.
