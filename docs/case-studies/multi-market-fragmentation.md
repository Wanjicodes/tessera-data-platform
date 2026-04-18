# Case study: unifying performance measurement across 12 markets

**Industry**: Multi-market commercial operations (anonymised)  
**Scale**: 4 enterprise clients · 12 markets · millions of records per cycle  
**Problem class**: Source fragmentation · definition conflicts · trust collapse

---

## The situation

A regional enterprise operating across 12 markets had accumulated a data environment that was technically functional but practically unusable for decision-making.

Each market had its own CRM system. Each system had its own field naming conventions. The same business concept — a "converted customer" — was defined differently in 7 of the 12 markets, and 3 of those markets had changed their definition mid-year without updating downstream reports.

The consequence: the regional leadership team was receiving monthly performance reports where the same KPI showed different numbers depending on which system it was pulled from. Finance and marketing were in regular disagreement about whether performance was improving or declining — both were technically correct given their respective data sources.

No one trusted the data. Decisions were being made on gut feel, or delayed until someone could manually reconcile the numbers.

---

## The diagnosis

The problem was architectural, not analytical. It could not be solved by building better reports on top of the existing data — the fragmentation was at the source level.

Root causes identified:

1. **No canonical data model**: Each source system used its own schema with no shared field definitions
2. **No metric contracts**: KPI calculations were embedded in spreadsheet formulas and dashboard filters — undocumented, unversioned, inconsistently applied
3. **No validation layer**: Bad data entered the reporting layer undetected and only surfaced when numbers were manually cross-checked
4. **No lineage**: When a number was questioned, there was no way to trace where it came from or what transformations had been applied

---

## The approach

Rather than patching individual reports, the platform was redesigned from the source layer:

**Step 1 — Source schema registry**  
Each source system was documented with a schema version. Field mappings to a canonical model were defined explicitly — not assumed.

**Step 2 — Data contracts**  
Validation rules were defined for each source: required fields, accepted value sets, range checks, uniqueness constraints. These ran immediately after ingestion. Any source that failed its contract was flagged before it could contaminate the merged dataset.

**Step 3 — Canonical metric definitions**  
Every KPI was documented with: a single agreed definition, the owner accountable for that definition, the calculation expressed in plain language and SQL, and the refresh cadence. Conflicting definitions were resolved explicitly — not silently overridden.

**Step 4 — Transformation with lineage**  
The transformation layer was rebuilt with full lineage tracking. Any output could be traced back to its source records, the schema version at ingestion, and whether it had passed contract validation.

---

## The outcome

- A single source of truth for 4 enterprise clients across 12 markets, running on a repeatable, automated pipeline
- Contract validation catching data quality issues at ingestion — before they reached stakeholders
- Metric definitions documented and versioned — disagreements resolved by reference, not by debate
- Pipeline observable end to end — failures surfaced immediately with structured logs rather than silent corruption

The platform did not eliminate data quality problems upstream. It made them visible, contained, and fixable — which is the realistic goal in complex, multi-system environments.

---

*This case study is anonymised. All client names, market identifiers, and commercially sensitive details have been removed. Written by Wanjiru Ndung'u based on direct experience.*
