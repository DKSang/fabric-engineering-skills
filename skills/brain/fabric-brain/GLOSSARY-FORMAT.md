# glossary.md format

The business vocabulary: what the words in requests, measures and column names mean in this organisation. Lets the agent turn "active customers by region" into the right filter without asking.

## Template

```md
# Glossary

## Customers

**Active customer**:
A customer with at least one completed order in the last 90 days.
_Avoid_: live customer, current customer
_In data_: `gold.dim_customer.is_active`

**Churned customer**:
A customer with no completed order for 12 months after having been active.

## Revenue

**Net revenue**:
Order value after discounts and returns, excluding VAT.
_Avoid_: sales, turnover
_In data_: measure `[Net Revenue]` in `sm_sales`
```

## Rules

- **Business terms only.** "Active customer" belongs; "lakehouse" or "SCD2" does not (those are platform or engineering terms, covered by `architecture/`).
- **Define what it is**, in one or two sentences, including the exact rule (the 90 days, the exclusions). Vague definitions produce wrong measures.
- **Be opinionated.** When several words mean the same thing, pick one and list the rest under `_Avoid_`.
- **Point at the data** (`_In data_`) when the term is implemented as a column or measure, so the agent uses the existing one instead of re-deriving it.
- **Group by subject** when natural clusters appear.
