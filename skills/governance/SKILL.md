---
name: governance
description: Establishes or improves governance for projects in any language or framework. Guides AI Code Agents and human collaborators through document layering, ADRs, task workflows, quality gates, commit discipline, security boundaries, and release practices. Use when starting a project, auditing an existing repository, extracting implicit decisions, or aligning local checks with CI.
compatibility: Requires Python 3 for scripts/check-links.py. Project-specific formatters, linters, test runners, build tools, and CI providers remain defined by the target project.
metadata:
  version: "1.0"
---

# Governance

## Purpose

Turn governance discipline into readable, executable, and verifiable project files. Do not leave rules only in prompts, personal memory, or scattered narrative documents. This skill serves two audiences:

- **AI Code Agents**: select the right path, load only the required references, make changes, and report acceptance results.
- **Human collaborators**: review, refine, or reject Agent proposals using the same document boundaries, ADR discipline, and quality gates.

This methodology is a cross-project baseline. A project may override the baseline, but every override must leave an ADR record.

## Core principles

1. **Traceable decisions**: choices that constrain future code organization, public contracts, data models, security boundaries, or performance budgets belong in ADRs.
2. **Document separation**: entry files provide navigation; rule directories contain procedures; ADRs contain decision records; `CONTEXT.md` defines terminology; plans and progress files do not store implementation logs.
3. **ADR as the source of truth**: narrative documents link to ADRs; ADRs win conflicts. Project-level overrides must also record their rationale.
4. **Atomic commits**: one commit represents one independently verifiable task; unrelated refactoring must not be mixed in; the commit should build and test independently.
5. **Hard quality gates**: run format -> lint -> test -> build -> check-links; a task is not complete while any gate fails.
6. **Non-rotting links**: cross-document references use relative paths and are checked by `scripts/check-links.py`.
7. **Zero-trust credentials**: passwords, tokens, and API keys must not enter configuration files, command lines, or logs.
8. **Explicit over fallback**: invalid parameters, missing security backends, and unsupported environments must fail explicitly rather than silently falling back.

## When to activate

Typical signals include:

- A new repository needs `README/AGENTS`, `CONTEXT.md`, `task_plan.md`, `progress.md`, `.rules/`, `docs/adr/`, a task runner, or CI.
- Existing rules are scattered across README files, comments, commit history, CI, and personal habits and need to be inventoried, layered, and introduced incrementally.
- A team needs to decide whether a statement belongs in a rule, ADR, glossary, plan, or progress document.
- A project needs link checking, pre-commit gates, Agent hooks, or a project-level acceptance workflow.
- A governance change needs review for scope creep, lost historical decisions, or missing rollback points.

## Default operating procedure

### 1. Audit before writing

Read the target project's entry document, rule index, `CONTEXT.md`, ADR index, task runner, CI, PR templates, and existing hooks. Load only the references relevant to the task. Record:

- current governance files and their ownership boundaries;
- explicit rules, implicit rules, and historical decisions;
- current format/lint/test/build/check-links commands, trigger points, and failure handling;
- conflicts or duplication between project conventions and the general methodology;
- irreversible choices that require human confirmation.

Do not overwrite existing governance documents, delete historical ADRs, or modify code during inventory. See [migration](references/migration.md) for the full existing-project inventory.

### 2. Choose the project path

- **New project**: use the initialization checklist in [migration](references/migration.md) to create the smallest useful governance skeleton.
- **Existing project**: proceed through inventory -> extraction -> layering -> ADR extraction -> acceptance redesign -> incremental rollout, keeping an independent rollback point for each batch.
- **Classification or review only**: read [document-structure](references/document-structure.md), [adr](references/adr.md), and the relevant sections; do not create unnecessary files.

### 3. Route by question

| Question | Read |
| --- | --- |
| Which file owns which information, and how should links be written? | [document-structure](references/document-structure.md) |
| Is an ADR required, and how should it be numbered, superseded, or indexed? | [adr](references/adr.md) |
| How should tasks, gates, task runners, or hooks be configured? | [workflow-and-acceptance](references/workflow-and-acceptance.md) |
| How should the project handle commits, comments, tests, dependencies, and coding style? | [collaboration-conventions](references/collaboration-conventions.md) |
| How should it handle credentials, networking, files, releases, and versions? | [security-and-release](references/security-and-release.md) |
| How should a new project be initialized or an existing one migrated? | [migration](references/migration.md) |

Keep references one level deep. Do not require a chain of references to understand a procedure.

### 4. Design and implement

Produce a gap list and a file-change plan before editing. For each change, state:

- the target file and its ownership boundary;
- whether it is a rule, decision, term, plan, progress update, or user-facing instruction;
- whether a new ADR or an update to an existing ADR is required;
- whether it changes code behavior, CI behavior, or team commit habits;
- the independent verification command and rollback path.

Do not treat a generic example as a project-specific requirement. Put project-specific tools, directories, names, and platforms in the project convention file or an ADR.

### 5. Acceptance order

1. Run the project's format, lint, test, and build commands through its task runner.
2. Run `python3 scripts/check-links.py` or the project wrapper.
3. Review the diff against [adr](references/adr.md) and extract every decision-bearing statement.
4. Check commit messages, atomicity, and ADR references.
5. Update `progress.md` current status and release history when applicable.
6. Report changed files, commands and results, remaining risks, open questions, and rollback paths.

The link checker accepts repeated `-e/--exclude DIR` arguments. See [workflow-and-acceptance](references/workflow-and-acceptance.md) and the script's `--help` output.

## Document ownership and conflicts

- Entry files: goals, technology stack, modules, and document navigation; no decision details.
- `.rules/`: non-decision workflows, style, testing, security, commits, task runners, and dependency pitfalls.
- `docs/adr/`: ADR Context, Decision, Alternatives, Consequences, and cross-references.
- `CONTEXT.md`: terminology, semantic roles, and counterexamples; no APIs or implementation details.
- `task_plan.md`: phases, error table, and decision summaries; no subtask logs or completion narratives.
- `progress.md`: current status and release history; no implementation details.
- `GOVERNANCE.md`: cross-project methodology; project-bound content belongs in project conventions.

Conflict order: ADR > rule directory > plan/progress narrative. Project conventions may override the general methodology, but the override requires an ADR explaining why.

## Output contract

Every use of this skill must report at least:

1. whether the target is a new or existing project;
2. current governance assets and gaps;
3. created, modified, and intentionally untouched files;
4. created, updated, or confirmed ADRs;
5. verification commands and pass/fail results;
6. open decisions, risks, human confirmation points, and rollback paths.

Unless explicitly requested, do not copy every reference back into the entry document, delete historical ADRs, or use `exit 0` to silently bypass a failed gate.

## Copyable assets

- [justfile.example](assets/justfile.example): task-runner template.
- [pyproject.toml.example](assets/pyproject.toml.example): Python formatting, static checking, testing, and build baseline.
- [package.json.example](assets/package.json.example): Node/TypeScript script baseline.

These files are templates, not project-level mandates. Replace the project name, package path, tool commands, and version policy after copying them.
