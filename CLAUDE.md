Maintainer notes for this repo. (The instruction files this repo's skills *generate* for users are a different thing: see `skills/setup/setup-fabric-engineering-skills/AGENTS-TEMPLATE.md`.)

## Layout

Skills live in bucket folders under `skills/`:

- `setup/`: run-once scaffolding and connection setup
- `brain/`: capturing and maintaining context in `reference/`
- `build/`: daily Fabric work on top of the brain
- `in-progress/`: public on purpose, feedback wanted, not shipped in the plugin

Each skill is a folder with a `SKILL.md`, an `agents/openai.yaml` (Codex UI metadata), and any reference files it owns, linked from `SKILL.md` by relative path. A skill never links into another skill's folder; to reuse another skill, it tells the agent to call the Skill tool with that skill's name.

## Invariants

- Every skill in a shipped bucket (`setup/`, `brain/`, `build/`) is listed in `.claude-plugin/plugin.json`'s `skills` array, in the top-level `README.md` (skill name linked to its `SKILL.md`), in `README.vi.md`, and in its bucket's `README.md`. `in-progress/` skills appear in none of them.
- Every skill is either **user-invoked** or **model-invoked**; see [.agents/invocation.md](./.agents/invocation.md). Keep `SKILL.md` frontmatter and `agents/openai.yaml` in sync.
- The frontmatter `name` equals the folder name.
- Run `claude plugin validate . --strict` and `scripts/check-skills.sh` after touching a manifest or adding, renaming or removing a skill.
- Every `fab` command written in a skill must match the current CLI. Check with `fab <command> --help` before adding one.
- Skills never tell the agent to handle a user's secret. Sign-in is always handed to the user.

## Shared vocabulary

Terms used across skills are defined in [CONTEXT.md](./CONTEXT.md). Use them verbatim.

## Local testing

`scripts/link-skills.sh` symlinks every shipped and in-progress skill into `~/.claude/skills` and `~/.agents/skills`, so a `git pull` keeps them current.
