# Pointer files

Tools that don't read `AGENTS.md` natively get a tiny file that sends them there. The pointer holds no knowledge of its own, so nothing drifts between tools.

Wrap each pointer in the same markers as `AGENTS.md` so a re-run can update it in place.

## Claude Code: `CLAUDE.md`

Claude Code imports files with `@path`, so the pointer pulls `AGENTS.md` into context directly:

```md
<!-- fabric-engineering-skills:start -->
@AGENTS.md

`AGENTS.md` is the canonical instruction file for this folder. Follow it.
<!-- fabric-engineering-skills:end -->
```

## GitHub Copilot: `.github/copilot-instructions.md`

VS Code Copilot also reads `AGENTS.md` when `chat.useAgentsMdFile` is on, but the pointer makes it work everywhere Copilot runs:

```md
<!-- fabric-engineering-skills:start -->
Read and follow `AGENTS.md` at the repo root before doing anything. It is the canonical instruction file for this folder and links to the reference docs in `reference/`.
<!-- fabric-engineering-skills:end -->
```

## Gemini CLI: `GEMINI.md`

```md
<!-- fabric-engineering-skills:start -->
@AGENTS.md
<!-- fabric-engineering-skills:end -->
```

## Cursor: `.cursor/rules/agents.mdc`

```md
---
description: Canonical project instructions
alwaysApply: true
---
<!-- fabric-engineering-skills:start -->
Read and follow `AGENTS.md` at the repo root before doing anything. It is the canonical instruction file for this folder.
<!-- fabric-engineering-skills:end -->
```

## Codex, OpenCode, Jules, Windsurf

These read `AGENTS.md` natively. No pointer needed.

## Rules

- Never copy `AGENTS.md` content into a pointer. One source of truth.
- If a pointer file already has the user's own content, keep it and add the marker block at the top.
- Only create pointers for tools the user actually uses (Section A).
