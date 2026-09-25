# User-invoked vs model-invoked

Every skill is one of two kinds, split by who can reach it:

- **User-invoked**: only the human can fire it, by typing `/<name>`. Frontmatter has `disable-model-invocation: true`; `agents/openai.yaml` has `policy.allow_implicit_invocation: false`. The `description` is a one-line human-facing summary. Use this for skills that start something the user didn't ask for in so many words: scaffolding a repo, installing software, sweeping a whole session.
- **Model-invoked**: the default. The agent can reach for it when a task fits, and the user can still type it. Omit both flags. The `description` is model-facing and names its triggers ("Use when the user ..."). Use this for discipline around work the user already asked for, even when that work changes Fabric: `build-in-fabric` fires on "set up my bronze layer", and its own plan gate plus the `fab` permission prompts are what hold each write back.

A user-invoked skill may tell the agent to call the Skill tool with a model-invoked skill. It can never reach another user-invoked skill; when it depends on one, it tells the user to run it (e.g. "tell the user to run `/setup-fabric-engineering-skills verify`").

Keep `SKILL.md` and `agents/openai.yaml` in agreement: a skill is user-invoked in both harnesses or in neither.
