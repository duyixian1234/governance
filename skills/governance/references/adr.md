# ADRs and decision extraction

This reference covers Architecture Decision Records (ADRs) and the decision-extraction step that follows every task. An ADR records a choice that constrains future code, contracts, or collaboration and serves as the source of truth for that rule.

## 1. When an ADR is required

Create an ADR when any of these conditions is true:

- It constrains future code organization, a public interface, or a data model.
- A future reader would be surprised by the chosen reverse or non-obvious operation.
- It establishes a long-lived contract, security boundary, or performance budget.
- It replaces or supersedes an earlier decision.
- A reusable pattern affects at least two independent modules and violating it would break an established convention.
- A project-level Agent hook changes gate trigger points, failure handling, or dangerous-command boundaries.

Do not create an ADR for:

- spelling, renaming, or formatting changes;
- a single bug fix whose tests prove the behavior;
- a mechanical API quirk of one third-party library (record it in the dependency-pitfall log);
- behavior-preserving refactoring, unless it establishes a reusable cross-module pattern.

Ask “Will a future reader ask why this was done this way?” If yes, check whether there was a real trade-off before creating the record.

## 2. Standard structure

ADR sections must appear in this order:

```markdown
# ADR <id>: <title>

**Status:** Accepted | Superseded by [<new-id>](...)
**Date:** YYYY-MM-DD

## Context
<Background, constraints, and motivation; at least three sentences>

## Decision
<The final choice; protocols, data models, or code examples are allowed>

## Alternatives considered
### <Alternative 1>
- Description
- Reason for rejection

### <Alternative 2>
- Description
- Reason for rejection

## Consequences
<Short-term cost, long-term benefit, side effects, and migration impact>

## Cross-references
- [<id>](<id>-...) - One-sentence relationship
```

`Context` explains why the decision is needed. `Decision` states only the final choice. `Alternatives considered` explains rejected paths. `Consequences` records costs, benefits, and side effects. `Cross-references` preserves bidirectional traceability.

## 3. Numbering

Use a module prefix plus a three-digit number. Never reuse a number. General prefixes include:

| Prefix | Scope |
| --- | --- |
| `F` | Cross-cutting concerns: CLI shape, accounts, CI, performance budgets, security models |
| `R` | Refactoring patterns and reusable cross-module structures |

A project may define domain prefixes such as `AUTH`, `PAY`, `ORDER`, or `INFRA`. The first general or system ADR should lock the prefix set and publish it at the top of `docs/adr/README.md`. Do not reuse a number after deleting a file, renaming a project, or superseding a solution.

A pattern ADR must satisfy all of these conditions:

- it affects at least two independent modules;
- it provides a reusable interface, macro, trait, or utility;
- later code that violates it would break an established convention.

The `Consequences` section of a pattern ADR must state where the pattern should be applied.

## 4. Lifecycle

| Status | Meaning | Operation |
| --- | --- | --- |
| `Proposed` | Drafted but not implemented | Discuss only; do not cite as a rule |
| `Accepted` | Adopted by code or process | Rules and code may cite it |
| `Superseded by [id]` | Replaced by a new decision | Keep the old file and add the replacement link |

When superseding an ADR, never delete the old file. Add the new id to the new ADR's `Cross-references` and add `**Superseded by [<new-id>](...)**` to the old ADR header.

## 5. Index

`docs/adr/README.md` lists ADRs by prefix and ascending number:

```markdown
## Mail (M-series)
| # | Title | Status | Date |
|---|-------|--------|------|
| [M001](M001-mail-protocol.md) | Mail protocol | Accepted | 2026-07-08 |
```

The main index contains the current decision tree. Historical decisions that cannot be migrated may live under `docs/adr/legacy/` with ids such as `LEGACY-001`; keep them out of the main index.

## 6. ADR extraction after every task

After every task, inspect the diff and scratch notes:

1. List constraints, boundaries, contracts, and trade-offs introduced or confirmed by the task.
2. Classify each item against the ADR criteria.
3. For decision-bearing content, choose a prefix and number, write the ADR, and add it to the index.
4. For non-decision content, remove execution narrative from `progress.md` and `task_plan.md`, keeping only necessary links.
5. Check that source-code or comment references to an ADR have a reverse entry in `Cross-references`.
6. Sweep the documents once more before a release so facts do not exist only in narrative prose.

### End-of-task decision table

| Question | Yes | No |
| --- | --- | --- |
| Does it constrain future behavior or a public contract? | Create an ADR | Continue |
| Was there a real alternative and trade-off? | Create an ADR | Usually no ADR |
| Would a future reader be surprised? | Create an ADR | Usually no ADR |
| Is it only a mechanical third-party API fix? | Write a dependency pitfall | No ADR |
| Is it only a single bug fix plus a new test? | No ADR | Continue |

## 7. ADRs in existing projects

Existing projects must read historical commits, legacy design documents, and current code. Do not infer the original motivation solely from the current shape.

- Migratable decision: rewrite it as a new ADR and preserve the historical source.
- Non-migratable decision: use `LEGACY-NNN`, explain the old choice, why it was replaced, and the active decision.
- Superseded ADR: keep the old file and add `Superseded by`.
- Extraction cadence: one reviewable batch per business domain during migration; return to one extraction pass per task afterward.

## 8. Human confirmation boundary

An Agent must not silently make these decisions:

- changing a public API, data migration, authentication/credential backend, or performance budget;
- marking an existing ADR obsolete;
- changing CI blocking conditions, commit rules, or hook failure handling;
- deleting or merging rule documents;
- overriding the general methodology with project conventions.

The Agent should draft the ADR and impact analysis first, then wait for human confirmation before setting the status to `Accepted`.
