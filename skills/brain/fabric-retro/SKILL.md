---
name: fabric-retro
description: "End-of-session sweep: find what this session taught that the Fabric brain doesn't know yet (facts, corrections, lessons), and what in reference/ it made stale. Proposes each change; you pick which to keep."
disable-model-invocation: true
---

# Fabric Retro

Run before closing a session. `fabric-brain` captures facts as they come up, but some slip through: things said in passing mid-task, a failure that took three tries and never became a lesson, a convention you only inferred after being corrected twice, a line in `reference/` that this session's work made false.

This skill finds those, proposes each one, and applies only what the user picks. It never writes anything unasked.

## 1. Gather

- **The session**: read back through the whole conversation. If it was compacted, say so up front: early details may be gone, so lean on the summary and on the diff below.
- **What's already captured**: `git status` and `git diff` for `reference/` and `AGENTS.md`. Anything already in the diff is done; don't propose it again.
- **What changed in Fabric**: the `fab` commands this session ran that created, changed or deleted items (`mkdir`, `import`, `rm`, `mv`, `set`, `cp` into a lakehouse).
- **The brain**: call the Skill tool with "fabric-brain" and read the reference files the session touched.

## 2. Find candidates

Look for five kinds, in this order of value:

| Kind | Look for | Goes to |
| --- | --- | --- |
| **Correction** | The user said "no", "that's the old one", "we don't do that", or fixed your output | the line that misled you, or a new line where none existed |
| **Lesson** | A failure that took more than one attempt, or whose cause wasn't obvious from the error | `lessons.md` (symptom with error text, cause, fix, Learn URL if verified) |
| **Uncaptured fact** | Durable things the user stated or you verified: names, IDs, conventions, business terms, pattern details | the file `fabric-brain`'s routing table picks |
| **Stale** | Lines in `reference/` contradicted by what happened: an item renamed or deleted, a convention the user changed, a workspace moved stage | edit or delete the line |
| **Drift** | The same fact in two places, or knowledge that crept into `AGENTS.md` | merge into one place; `AGENTS.md` keeps only rules and the index |

Apply `fabric-brain`'s test to each: durable (true next week) and worth not being asked again. Drop the rest. Never propose secrets or data rows.

If items were created, changed or deleted in Fabric this session, don't document them here: that's a separate candidate telling the user to run `/document-fabric-workspace <workspace>` (it only reads what changed, so it's cheap).

## 3. Propose

One numbered list, grouped by kind, sharpest first. Each entry is one line of change plus its evidence:

```md
### Corrections
1. `naming-conventions.md`: silver tables are `slv_<entity>`, singular. Replaces "silver_<entity>".
   Evidence: "no, singular, slv_order" (you, while naming the orders table)

### Lessons
2. `lessons.md` › Notebooks: "Workspace name isn't available when a notebook runs from a pipeline; resolve it at runtime."
   Evidence: first pipeline run failed with `PathNotFound ... lh_bronze`; fixed in the second run.

### Stale
3. `environment.md`: remove `lh_staging` from Key items (deleted this session with `fab rm`).

### Follow-ups
4. Run `/document-fabric-workspace Sales-DEV`: 3 items were created this session.
```

One entry per fact: when a fact touches two files (a connection in `environment.md` and its timeout in `lessons.md`), name both files in the same entry. Keep it to what matters: at most ~15 entries. If there's nothing, say "Nothing new for the brain this session" and stop.

Then ask: _"Which should I apply? (all / numbers / none; say if you want any reworded)"_

## 4. Apply

For each picked entry, write it through `fabric-brain`'s formats: update the existing line rather than adding a near-duplicate, verify environment facts with read-only tools where you can, mark the rest `(unverified)`. Follow-ups aren't applied; they're reminders for the user.

Finish with a short list of what changed, file by file. Leave it uncommitted: the user reviews `reference/` in the diff like any other change.
