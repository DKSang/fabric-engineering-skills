# decisions/NNNN-&lt;slug&gt;.md format

A short record of a hard-to-reverse choice, so a future session doesn't "fix" it or re-open it without knowing why it was made. Number sequentially from `0001`; the slug is the decision in a few words (`0003-lakehouse-for-gold.md`).

Write one only when all three hold: **hard to reverse**, **surprising** to a future reader, and the result of **real alternatives**. Ask the user before writing it.

## Template

```md
# Lakehouse, not Warehouse, for the gold layer

- **Status**: accepted
- **Date**: 2026-09

## Context

Gold serves one Direct Lake semantic model and two Spark-based ML notebooks. The team writes PySpark, not T-SQL.

## Decision

Gold tables live in `lh_gold` (Lakehouse). No Warehouse.

## Alternatives

- **Warehouse**: T-SQL writes and multi-table transactions, but the team doesn't use T-SQL and the notebooks would read through the SQL endpoint.

## Consequences

- Transformations to gold are notebooks only.
- Reporting users who want T-SQL use the Lakehouse SQL analytics endpoint (read-only).
```

## Rules

- **One decision per record**, a page at most.
- **Alternatives are required.** A record without them is a statement, not a decision.
- **Never rewrite history.** When a decision changes, set the old one's status to `superseded by NNNN` and write a new record.
- **Surface conflicts.** If a request contradicts an accepted decision, say so before acting: _"This contradicts decision 0003 (Lakehouse for gold). Reopen it?"_
