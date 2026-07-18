# Governance Skills

A portable Agent Skill for establishing and improving project governance across languages, frameworks, and collaboration models.

The repository packages a governance methodology for both **AI Code Agents** and human collaborators. It turns document ownership, architecture decisions, task workflows, quality gates, commit discipline, security boundaries, and release practices into a repeatable workflow.

## What this repository contains

```text
skills/
└── governance/
    ├── SKILL.md
    ├── references/
    │   ├── document-structure.md
    │   ├── adr.md
    │   ├── workflow-and-acceptance.md
    │   ├── collaboration-conventions.md
    │   ├── security-and-release.md
    │   └── migration.md
    ├── scripts/
    │   └── check-links.py
    └── assets/
        ├── justfile.example
        ├── pyproject.toml.example
        └── package.json.example
```

## The `governance` skill

Use `skills/governance/` when you need to:

- initialize governance for a new project;
- audit and improve governance in an existing repository;
- decide whether information belongs in an entry document, rule, ADR, glossary, plan, or progress log;
- extract implicit decisions from code, comments, documents, CI, and commit history;
- align local quality checks, Agent hooks, and CI;
- review governance changes for missing ADRs, broken links, scope creep, or absent rollback paths.

The skill uses progressive disclosure:

- `SKILL.md` contains the activation rules, operating procedure, routing table, and output contract;
- `references/` contains focused governance guidance loaded on demand;
- `scripts/` contains executable validation code;
- `assets/` contains copyable task-runner and toolchain templates.

## Agent Skills compatibility

The skill follows the [Agent Skills specification](https://agentskills.io/specification):

- the directory name and frontmatter `name` are both `governance`;
- `description` states what the skill does and when to use it;
- the main `SKILL.md` remains below the recommended 500-line limit;
- bundled resources are referenced with paths relative to the skill root;
- detailed material is split into focused references for on-demand loading.

## Using the skill

Copy the directory `skills/governance/` into the skills directory supported by your Agent client. Then invoke or enable the `governance` skill according to that client's conventions.

The default workflow is:

1. **Audit** the current project before writing.
2. **Classify** the project as new or existing.
3. **Route** the question to the smallest relevant reference.
4. **Plan** file ownership, ADR impact, verification, and rollback.
5. **Implement** the governance changes incrementally.
6. **Validate** quality gates, links, ADR extraction, and progress synchronization.
7. **Report** changed files, verification results, risks, open decisions, and rollback paths.

The skill does not silently overwrite existing governance documents or delete historical ADRs. Project-specific overrides require an ADR.

## Link checker

The bundled checker uses Python 3 standard-library modules and supports parallel processing:

```bash
python3 skills/governance/scripts/check-links.py --root .
```

Exclude directories by repeating `--exclude` or `-e`:

```bash
python3 skills/governance/scripts/check-links.py \
  --root . \
  --exclude vendor \
  --exclude generated \
  --workers 4
```

Behavior:

- scans Markdown files relative to the repository root;
- excludes `.git`, `node_modules`, `dist`, `out`, and `target` by default;
- checks relative file links and performs best-effort anchor validation;
- emits `[OK]`, `[WARN]`, and `[FAIL]` messages;
- returns `0` for a clean run, `1` for broken links, and `2` for argument or environment errors.

Run `python3 skills/governance/scripts/check-links.py --help` for the full interface.

## Copyable assets

- [`justfile.example`](skills/governance/assets/justfile.example) provides `format`, `check`, `test`, `build`, `ci`, and `check-links` recipes.
- [`pyproject.toml.example`](skills/governance/assets/pyproject.toml.example) provides a Python project baseline for Ruff, Pytest, and builds.
- [`package.json.example`](skills/governance/assets/package.json.example) provides a Node/TypeScript script baseline using pnpm.

These are templates, not universal project requirements. Replace project names, package paths, tool commands, and version policies before committing them to a target project.

## Local validation

From the repository root:

```bash
python3 skills/governance/scripts/check-links.py --root .
just --justfile skills/governance/assets/justfile.example --list
```

For the Python script and example configuration files, use the Python runtime and package-management conventions of the host project. The skill itself requires no third-party Python dependency.

## Repository maintenance

When changing the skill:

1. Keep user-facing text in English.
2. Keep `SKILL.md` focused and move detailed guidance into the appropriate reference.
3. Preserve relative links and run the link checker.
4. Update examples when the documented task-runner contract changes.
5. Review the diff for new decision-bearing content and create or update an ADR when needed.
6. Keep the skill self-contained; do not rely on files outside `skills/governance/`.

## License

This repository is licensed under the [MIT License](LICENSE).

- Copyright (c) 2026 Yixian Du
- The bundled `skills/governance/` package is distributed under the same MIT terms.
- No warranty is provided; see the [LICENSE](LICENSE) file for the full text.
