# Document structure and link governance

This reference covers document ownership, plans and progress files, the domain glossary, cross-document references, and self-audits. It answers where information belongs, which source wins conflicts, and how to prevent links and facts from rotting.

## 1. Document types and ownership

| Document | Should contain | Should not contain |
| --- | --- | --- |
| Entry file (`AGENTS.md` / `agents.md` / `README.md`) | Project goals, technology stack, module list, document navigation | Decision details, procedural detail |
| Rule directory (`.rules/` or project equivalent) | Workflow, style, testing, security, commits, task runners, dependency pitfalls, comment rules | Full decisions; link to ADRs instead |
| ADR directory (`docs/adr/` or project equivalent) | Context / Decision / Alternatives / Consequences for each architecture decision | Procedures; link to rules instead |
| Domain glossary (`CONTEXT.md`) | Term definitions, semantic roles, counterexamples | Implementation details, APIs, data models |
| Task plan (`task_plan.md`) | Phase status, error table, decision summaries, necessary configuration drafts | Subtask lists, completion summaries, implementation logs, full decisions |
| Progress log (`progress.md`) | Current status and release history | Phase details, subtasks, quality-gate logs |
| User documentation (`README*.md` / `skills/`) | User and collaboration instructions | Internal architecture, full decisions |
| General methodology (`GOVERNANCE.md`) | Cross-project governance discipline | Project-specific tools, directories, or platform details |
| Project conventions (`<project>-conventions.md` / `CONVENTIONS.md`) | Project-shape-specific rules | Duplicated cross-project principles |

File names are not mandatory. If a project already has an equivalent file, reuse it and document the mapping in the entry navigation.

## 2. Conflict arbitration

Resolve conflicts in this order:

1. An ADR wins over any other document.
2. An ADR wins over the rule directory; update the rule to link to the ADR.
3. When `task_plan.md`, `progress.md`, and discovery notes duplicate content, keep the full decision only in the ADR and use links or short summaries elsewhere.
4. Project conventions win over the general methodology, but every override must record its context, scope, and rationale in an ADR.
5. When code and documentation disagree, record the gap first. Read code, tests, and history before deciding whether to migrate behavior or fix the documentation.

## 3. Document health check

Run weekly or before each release:

- [ ] The ADR count matches the number of index rows in `docs/adr/README.md`.
- [ ] Every `[id](...)` link in the ADR index is valid.
- [ ] The rule index row count matches the number of rule files.
- [ ] The module list in the entry document matches the code modules.
- [ ] Every non-obvious fact can be located in an ADR or rule rather than only in narrative prose.
- [ ] The general methodology and project conventions contain no duplicate clauses.
- [ ] Plan and progress files contain no subtask logs, completion summaries, or expanded descriptions of released features.
- [ ] No absolute paths appear in Markdown or source comments.
- [ ] `check-links.py` produces the same result locally and in CI.

## 4. Plan and progress file discipline

### `task_plan.md`

Recommended structure:

1. Top status: current release and most recently completed phase, in one line.
2. Overall goal: a one- to three-sentence project vision.
3. Phase plan: `Phase N: <title> [complete|in_progress|pending]`, with two to ten summary lines per phase.
4. `Errors Encountered`: a project-level table of non-obvious errors and fixes.
5. `Key Design Decisions`: a project-level table of choices, rationale, and ADR links; do not duplicate full decisions.
6. Configuration examples: only when multi-account, protocol, or configuration drafts are genuinely needed.

Do not include `T1.1`-style subtasks, completion summaries, per-commit acceptance recaps, or itemized descriptions of released features. Ask: “Can a future reader find this in an ADR or commit history?” If yes, remove it and keep only the ADR link.

### `progress.md`

Carry only two types of information:

- Current status: released version, current phase, and one sentence per module; one sentence per line.
- Release history: version, tag, one-line change summary, and the main related ADR.

An ADR chronology is optional here. The canonical index belongs in `docs/adr/README.md`.

## 5. Domain glossary

`CONTEXT.md` answers only “What do the terms in this domain mean?” Each term contains:

- a definition;
- its semantic role in the project;
- counterexamples that prevent confusion.

Do not include implementation details, APIs, data models, or behavior. Add terminology before documenting a new module.

## 6. Cross-document links

- Use relative paths for cross-document references.
- Absolute paths are forbidden.
- Link to a file in the same directory by its file name.
- Link from a child directory to a parent with `../file.md`.
- Link from a parent directory to a child with `subdir/file.md`.
- Resolve links relative to the source file's directory, not by guessing from the repository root.
- Update all references in the same commit when a file is renamed.
- Remove an index entry before deleting the indexed file.
- Run link checks after renaming a section; anchor checks are best effort and do not replace human review.

The source directory depth determines the usual ADR prefix:

| Source location | Typical ADR prefix |
| --- | --- |
| Top-level or one-level flat directory | `../docs/adr/<id>-...md` |
| One child directory | `../../docs/adr/<id>-...md` |
| Two child directories | `../../../docs/adr/<id>-...md` |

A project may use `architecture/decisions/` or another equivalent directory, but it must establish one canonical location in the ADR index.

## 7. Terminology map

| Methodology term | Common synonyms | Do not confuse with |
| --- | --- | --- |
| Entry file | `AGENTS.md` / `agents.md` / `README.md` | `CONTRIBUTING.md` (contribution workflow) |
| Rule directory | `.rules/` / `.standards/` / `.conventions/` | `docs/` (general documentation) |
| General methodology | `GOVERNANCE.md` | `STYLE.md` (single-file style guide) |
| Project conventions | `CONVENTIONS.md` / `<project>-conventions.md` | `CONTRIBUTING.md` |
| ADR | Architecture Decision Record | `RFC` (not necessarily a mandatory record) |
| Task plan | `task_plan.md` / `ROADMAP.md` / `PLAN.md` | `TODO.md` |
| Progress log | `progress.md` / structured `CHANGELOG.md` | Release notes themselves |
| Quality gate | `ci` / `lint` / `verify` | `build` (only one gate) |
| Link integrity | `check-links` / `link-check` | `spell-check` |

## 8. Shared review questions

When reviewing a governance change, ask:

1. Which document owns this content?
2. Is it a fact, rule, decision, term, plan, or progress update?
3. If it is a long-lived constraint, should it become an ADR?
4. If it is project-specific, has it been incorrectly written into the general methodology?
5. Do the code, tests, and CI actually follow this rule?
6. Were links checked after a document was renamed, deleted, or moved?
