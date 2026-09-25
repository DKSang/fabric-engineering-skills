# Fabric Engineering Skills

Agent skills that give AI coding tools durable context about a user's Microsoft Fabric work, plus the connections to act on it.

## Language

**Fabric brain**:
The repo folder an agent reads at the start of every session: the **instruction file**, the **reference files**, and the MCP and CLI **connections**. Created by `setup-fabric-engineering-skills`.
_Avoid_: second brain (fine in prose for humans, not in skill text), knowledge base, memory

**Instruction file**:
`AGENTS.md`, the one canonical file of behaviour rules for every AI tool. Other tools reach it through **pointer files**.
_Avoid_: system prompt, rules file

**Pointer file**:
A tool-specific file (`CLAUDE.md`, `.github/copilot-instructions.md`, `GEMINI.md`, `.cursor/rules/agents.mdc`) whose only job is to send the tool to `AGENTS.md`.

**Reference files**:
Everything under `reference/` in the user's repo: environment, naming conventions, CLI notes, architecture patterns. Knowledge, not behaviour.
_Avoid_: docs (too broad), context files

**Durable fact**:
Something about the user's Fabric work that will still be true next week and that a future session would otherwise have to ask for again. Only durable facts go into **reference files**.
_Avoid_: memory, note

**Capture**:
Recording a **durable fact** in the right **reference file** in the same turn it came up. Done by `fabric-brain`.
_Avoid_: save, remember (as verbs for this)

**Scope**:
The set of workspaces the agent may modify. Everything outside it is read-only.
_Avoid_: allowlist (fine for the hook implementation only)

**Guardrails**:
The written rules in `AGENTS.md` (scope, dry run, confirm destructive operations, no secrets) plus any enforcement (permission rules, hooks).

**Standing rule**:
A rule in `AGENTS.md` that applies to every task, e.g. "verify Fabric claims against Microsoft Learn before stating them".

**Managed block**:
The region between `<!-- fabric-engineering-skills:start -->` and `<!-- fabric-engineering-skills:end -->` in a user file. Owned by the skills and replaced on re-run; everything outside it belongs to the user.

## Relationships

- A **Fabric brain** has one **instruction file**, any number of **pointer files**, and a `reference/` folder of **reference files**
- The **instruction file** holds the **guardrails** and **standing rules**, and indexes the **reference files**
- **Scope** is recorded in both the **instruction file** (the rule) and `reference/environment.md` (the IDs)
