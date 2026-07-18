# New-project initialization and existing-project migration

This reference covers the new-project checklist, existing-project inventory, layering, ADR extraction, acceptance redesign, incremental rollout, and completion criteria. The governing sequence is: inventory first, layer second, extract decisions third, implement last. Skipping a step creates a wall document disconnected from reality.

## 1. New-project initialization

### Required documents on day one

- [ ] `README.md` or `AGENTS.md`: project goals, technology stack, module list, and document navigation.
- [ ] `task_plan.md`: phase plan and current phase.
- [ ] `progress.md`: current status and release history; it may start empty and does not need an ADR chronology.
- [ ] `CONTEXT.md`: domain glossary covering at least the core modules.
- [ ] General governance document: copy or adapt the methodology as `GOVERNANCE.md` when the project needs a local copy.
- [ ] Project conventions file: shape-specific rules only.
- [ ] `docs/adr/README.md`: ADR index and empty table.
- [ ] `.rules/RULES.md`: rule index.
- [ ] `.rules/01-workflow.md`: development workflow.
- [ ] `.rules/02-coding-style.md`: coding style.
- [ ] `.rules/03-testing.md`: testing rules.
- [ ] `.rules/04-security.md`: security boundaries.
- [ ] `.rules/05-commit.md`: commit rules.
- [ ] `.rules/06-task-runner.md`: task-runner conventions.
- [ ] `.rules/07-dependency-pitfalls.md`: dependency-pitfall log, initially empty.

### Tools and process

- [ ] The task runner provides `format`, `check`, `test`, `build`, `ci`, and `check-links`.
- [ ] CI and local gates use the same configuration.
- [ ] `scripts/check-links.py` is connected to the task runner.
- [ ] Formatter and linter configuration is version-controlled.
- [ ] The PR template lists quality gates, ADR extraction, and progress-index updates as required steps.
- [ ] At least three ADRs exist before the first release; choose topics for the project shape.
- [ ] Every module has a README and at least one ADR describing its boundary.

### Recommended order for a new project

1. Create the entry, plan, progress, glossary, and empty indexes.
2. Create the `.rules/` skeleton and task runner.
3. Add link checking and CI.
4. Record the first security, architecture, error-model, or CLI-shape decisions.
5. Add a boundary document and ADR for each module.
6. Run the first complete gate and record open items.

## 2. Existing-project migration principles

| Dimension | New project | Existing project |
| --- | --- | --- |
| Documentation starting point | Empty | README files, design docs, comments, and commits are scattered |
| Decision visibility | Create ADRs explicitly | Decisions are implicit in code, comments, and scratch notes |
| Migration risk | Low | May affect live services and external dependencies |
| Pace | Can build the baseline at once | Must be staged, reversible, and preserve a runnable baseline |
| Acceptance | Designed from zero | Scattered CI, IDE, and task-runner flows must converge |

### Process map

```text
inventory -> extract -> layer -> extract ADRs -> redesign acceptance -> roll out incrementally
    |                                                               |
    +---------------- do not change the current state during inventory
```

## 3. Stage 1: inventory the current state

Keep the inventory in scratch space rather than git:

| Area | Action | Output |
| --- | --- | --- |
| Documents | List all `.md`, `.txt`, and `*.rst` files by directory | `inventory-docs.md` |
| Code | List source directories, main entry points, and test directories | `inventory-code.md` |
| Build tools | Read Justfiles, package scripts, Makefiles, and equivalents | Recipe inventory |
| CI | Read `.github/workflows/`, GitLab CI, and equivalents | CI steps |
| Existing process | Find CONTRIBUTING files, PR templates, and CODEOWNERS | Current conventions |
| Historical decisions | Search commit messages, legacy ADRs, and design docs | Candidate ADR list |

Read comprehensively rather than sampling. Do not modify files during inventory. Mark the source of every rule with a file and line, commit, or URL.

## 4. Stage 2: extract governance rules

Classify all non-obvious rules into three tiers:

| Tier | Meaning | Treatment |
| --- | --- | --- |
| Explicit rule | Directly stated in README, CONTRIBUTING, or comments | Move to `.rules/` |
| Implicit rule | Implied by code style, test patterns, or commit history | Decide in stage 3 |
| Historical decision | Traceable to a commit, legacy ADR, or design doc | Extract in stage 4 |

Ask: “Would a future reader be surprised by the reverse or non-obvious operation?”

- Yes: historical decision; extract an ADR.
- No, but the code follows it: implicit rule; layer it.
- No, and the code does not follow it: obsolete constraint; delete it instead of carrying it forward.

## 5. Stage 3: layer cross-cutting concerns and domains

Use both dimensions:

| Cross-cutting layer | Questions | Example |
| --- | --- | --- |
| Architecture | Boundaries, dependency direction, layering | A controller does not call a repository directly |
| Security | Credentials, input validation, output sanitization | No passwords in logs; parameterized SQL |
| Observability | Logs, metrics, traces | Every external call has a trace id |
| Performance | Budgets, caches, resource cleanup | P99 target; no full loading |
| Testing | Coverage, mocks, skips | Network calls accept a fake |
| Dependencies | Library boundaries, upgrade policy | Only the core module may use a library |

Each cross-cutting layer produces a rule table with the rule, source, and current-state decision (keep, change, or retire).

For each domain, record:

- scope: what it does and does not do;
- key dependencies: external services and internal modules;
- known constraints: protocol, compatibility matrix, and quotas;
- implicit rules;
- related ADR ids.

A domain is usually one or more tightly coupled modules plus a set of external contracts. Make it independent when it can be released, configured, or assigned an ADR prefix independently.

## 6. Stage 4: ADR extraction order

- Extract cross-cutting ADRs before business-domain ADRs.
- Prioritize security to avoid adding risk during migration.
- Extract observability next so the migration itself can be monitored.
- Process business domains from highest risk and frequency to lowest.
- Read historical motivation in existing projects instead of describing only the current shape.

Keep the general prefix rules and never reuse historical ids. For a non-migratable legacy decision, use `LEGACY-NNN` under `docs/adr/legacy/` and keep it out of the main index.

## 7. Stage 5: redesign acceptance

### Inventory current checks

Record each current step, its trigger, frequency, and failure handling: formatter, linter, tests, check-links, dependency audit, and so on.

### Define the target

Compare target, current state, and gap:

| Check | Example target | Trigger |
| --- | --- | --- |
| Formatting | Required before commit and verified in CI | After edit / before commit |
| Static checks | Zero warnings across all modules | Before commit / CI |
| Tests | Full run; no unexplained skips | Test changes / CI |
| Links | Part of CI | Markdown edit / CI |
| Security | Credential scan and dependency audit | Release / scheduled |

Recommended trigger points:

- after file edits: Agent PostToolUse or IDE save;
- before commit: pre-commit or `just check`;
- on push: full CI `ci` plus check-links;
- before release: release recipe plus dependency audit.

## 8. Stage 6: incremental rollout and rollback

Recommended batches:

1. Infrastructure: task runner, CI, `.rules/`, link checker, and README split.
2. Cross-cutting ADRs: security, architecture, and observability.
3. Domain ADRs: one domain per PR.
4. Acceptance wiring: task runner, CI, and Agent hooks.
5. Documentation closeout: progress, plan, and first release.

Before each batch:

- mark the file scope, for example with `git diff --name-only main`;
- confirm that a revert still leaves tests and builds runnable;
- describe in the PR which checks are affected after `git revert <commit-hash>`;
- keep a PR to roughly 20 files or fewer to avoid a big-bang rewrite.

## 9. Completion criteria

A migration is complete only when all items are true:

- [ ] Every explicit rule lives in `.rules/` or an ADR.
- [ ] Every implicit rule has been kept, extracted into an ADR, or deleted.
- [ ] Acceptance matches the quality gates and every check has an explicit trigger.
- [ ] Agent hooks are configured and do not conflict with CI.
- [ ] Documentation versions, progress history, and ADR index agree.
- [ ] The first release has completed the full process.
- [ ] Every methodology self-check answers “yes”.

## 10. Common traps

| Trap | Symptom | Countermeasure |
| --- | --- | --- |
| Big-bang rewrite | One PR changes 30+ files | Roll out in batches; keep PRs to 20 files or fewer |
| Write rules before extracting ADRs | Rules remain permanently in progress files | Create the ADR first, then link to it from rules |
| Skip gates during migration | “This case is special; CI can wait” | Run gates for every commit |
| Overuse `LEGACY` | Every old decision is archived | Use it only for decisions that cannot be migrated |
| Overly broad domain ADR | One ADR describes an entire domain | Split by domain and key decision; cover the important choices |

## 11. Methodology self-check

| Dimension | Self-check question |
| --- | --- |
| Traceable decisions | Can every code constraint point to an ADR? |
| Document separation | Does each document contain one kind of information? |
| ADR source of truth | Does the team default to the ADR in conflicts? |
| Atomic commits | Can recent commits build and test independently? |
| Hard gates | Did every commit run `ci` and `check-links`? |
| Link integrity | Are renamed documents detected promptly? |
| Zero-trust credentials | Can credential locations be found and eliminated quickly? |
| Explicit validation | Do invalid parameters produce errors instead of silent defaults? |
| Layering | Are general rules and project conventions free of duplication? |

If any answer is “no” or “not sure,” return to the relevant section and strengthen it.
