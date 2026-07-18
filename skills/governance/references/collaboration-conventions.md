# Collaboration conventions: commits, comments, tests, dependencies, and code

This reference covers commit conventions, comments, tests, dependency management, and coding-style baselines.

## 1. Conventional Commits

Message format:

```text
<type>(<scope>): <subject>

<body - wrap at 72 columns; explain what and why, not how>

<footer - issue, breaking change, co-author>
```

### Types

| Type | Use when |
| --- | --- |
| `feat` | Adding user-visible behavior such as a command, action, or flag |
| `fix` | Fixing an observable bug |
| `refactor` | Changing internal structure without changing behavior |
| `test` | Changing tests only |
| `docs` | Changing documentation only |
| `chore` | Changing build, CI, dependencies, or release files |
| `perf` | Only when the benefit is quantified in the body |

Use the main module or layer as `scope`; omit it for cross-project changes when appropriate. One commit equals one independently verifiable task and must build and test independently. Keep feature work and version bumps in separate commits. If a body exceeds roughly ten lines, check whether multiple tasks have been mixed together.

### The body must answer

1. **What** changed;
2. **Why** it changed when the reason is not obvious;
3. **Trade-offs**, including rejected alternatives and an ADR link for decision-bearing changes;
4. **Impact** on modules or user behavior.

### Pre-commit checklist

- [ ] Quality gates are green.
- [ ] Cross-document links are valid.
- [ ] Decision-bearing changes have a new or updated ADR.
- [ ] The commit message follows the format.
- [ ] The diff contains one task and no unrelated changes.

## 2. Comments

### Language and content

- Use one team language for source comments; avoid mixing languages.
- User-visible strings, test fixtures, and business URLs are not comments and should be reviewed as code behavior.
- Delete comments that merely repeat the code; do not narrate code that already explains itself.
- Replace comments that contain constraints, trade-offs, boundaries, or reasons for a shape with an ADR link.

### Comment-cleanup commits

Commit each cleaned source file independently. Do not bundle comment translation or cleanup across multiple files. Use `refactor(comments)` or `docs(comments)` as the commit type.

## 3. Tests

### Locations

| Type | Recommended location | Use when |
| --- | --- | --- |
| Unit test | Same file as the code or the language convention | Testing module-internal logic |
| Integration test | Top-level `tests/` | Testing cross-module or entry-point behavior |
| External-facility test | Ignore marker or feature gate | Requiring networks, accounts, or paid APIs |

### General required coverage

1. Configuration loading and multi-account parsing;
2. Serialization from error types to a structured envelope;
3. At least one happy-path integration test for every core execution unit;
4. At least one new regression test for every bug fix.

Projects may add module-specific requirements, but coverage percentage must not be the only quality signal. Every core path needs a test hit.

### Mock discipline

- Put network calls behind an interface or abstraction and inject a fake in tests.
- Pass a `Clock` function or test-controlled time source to time-dependent code.
- Pass a `gen_id` function or resettable counter to random-ID code.
- Keep mocks near the code under test or in the project-defined location, with clear names.
- Record performance budgets in an F-series or project-equivalent ADR. CI need not enforce performance assertions; structural constraints such as pagination and no full loading are acceptable.

## 4. Dependencies and third-party components

### Before adding a dependency

1. Does the standard library or an existing dependency already provide the capability?
2. Is the dependency genuinely necessary?
3. Is it needed by one module only, and should it be isolated behind a feature flag?
4. Do its TLS backend, runtime, and platform requirements fit the project?
5. Are maintenance activity, license, size, and known CVEs acceptable?

### Versions and features

- Disable unnecessary default features and enable only what is required.
- Commit lockfiles and use the same lockfile locally and in CI.
- Prefer a TLS backend that shares the runtime's implementation when applicable, avoiding unnecessary system C-library dependencies.
- Run a dependency security audit before every major-version upgrade. Create a dedicated ADR for credential, cryptography, and serialization dependencies.

### Dependency-pitfall log

Record non-obvious dependency problems with mechanical fixes in `.rules/07-dependency-pitfalls.md`:

- one-line principle;
- one-line fix;
- one-line source (commit, issue, or documentation link).

“Why library A instead of library B?” is a decision and belongs in an ADR, not only in the pitfall log.

## 5. Coding-style baseline

### Required items

| Item | Rule |
| --- | --- |
| Formatting | Run the project formatter before committing; CI verifies check mode |
| Static checks | Use `--deny warnings` or an equivalent; local and CI configurations match |
| Public APIs | Add documentation comments describing contracts, invariants, and side effects |
| Modules | Add a module-level document comment describing purpose and key invariants |
| Error handling | Do not rely on panic or unhandled exceptions in production code; use structured errors, context, and wrapping |
| Constructors | Constructors that can fail return an error rather than panicking; use “construct successfully or fail explicitly” |

### Naming

- Name modules and files after domain concepts, not verbs or CLI commands.
- Use the language's standard PascalCase for types and interfaces.
- Use the language's standard snake_case or camelCase for functions and variables.
- Use the language's standard SCREAMING_SNAKE_CASE or UPPER_SNAKE_CASE for constants.
- Follow language conventions for collection types.

### Async, time, and parameters

- State the runtime model explicitly: single-threaded/multi-threaded, event-driven/multi-process, and so on.
- Probe runtime liveness before touching async resources in destructors or cleanup paths.
- Use an explicit ambiguity policy for local time, DST, daylight-saving changes, and cross-time-zone input.
- Return a clear error for explicit validation failures; never silently use a default.
- Detect global mode flags once and store the result in context or thread-local state.
- Distinguish single-character values from prefixed flags explicitly.

### Persistence and queries

- Use exact matching, GLOB, regular expressions, or a parser for token boundaries; do not use fuzzy substrings.
- Allow configuration-path array access to grow automatically instead of treating a missing index as an error.
- Normalize synonymous configuration keys at the loading boundary and list accepted aliases in an ADR.
