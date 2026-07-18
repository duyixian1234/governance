# Workflow, quality gates, and acceptance

This reference covers starting and completing tasks, quality gates, task runners, link checks, and Agent hooks.

## 1. Before starting a task

1. Open the entry document and confirm the project goal, phase, and module list.
2. Find the relevant phase in `task_plan.md` and mark it `in_progress`.
3. Read only the `.rules/*.md` files relevant to the task; do not load every rule by default.
4. Use `docs/adr/README.md` to find the ADRs for the affected modules and read them in order.
5. Read the relevant source files, tests, task runner, and CI; do not infer the current state from memory.
6. For an existing project, finish the inventory before making code or governance changes.

## 2. During the task

- After every two external searches or fetches, ask whether the new information constitutes a decision. If yes, write it to scratch and extract it into an ADR at task completion; otherwise discard it.
- Add every non-obvious error to the project-level `Errors Encountered` table in `task_plan.md`.
- Do not put implementation detail, completion summaries, or activity logs in `progress.md`.
- Do not commit unfinished work; the project convention file defines what counts as unfinished.
- When the current state conflicts with an ADR or project convention, stop and record the conflict instead of silently overwriting it.

## 3. Task completion order

Each step can fail independently:

| Order | Step | Pass condition |
| --- | --- | --- |
| 1 | Quality gates | format -> lint -> test -> build is green |
| 2 | Document links | `python3 scripts/check-links.py` has no failures |
| 3 | ADR extraction | Decision-bearing content has a new or updated ADR |
| 4 | Commit review | Message and diff follow the commit convention |
| 5 | Progress sync | `progress.md` status and release history are current |

A task may be a complete feature, module skeleton, phase, or a tightly coupled bug-and-test change.

## 4. Quality gates

| Order | Check | Generic command shape | Failure handling |
| --- | --- | --- | --- |
| 1 | Format | `formatter --check` or equivalent | Fix immediately and rerun |
| 2 | Static check | `linter --deny warnings` | Zero warnings required |
| 3 | Test | `test_runner` | No unexplained skips |
| 4 | Build | `build` | Must succeed |
| 5 | Links | `check-links` | Fix broken links |

Format must run before lint. CI and local gates must use the same configuration. Third-party noise may be suppressed in project configuration, but `.rules/` must contain a one-line explanation.

### Tool substitution table

| Placeholder | Rust | Node/TS | Python | Go |
| --- | --- | --- | --- | --- |
| formatter | `cargo fmt` | `pnpm exec prettier` | `uv run ruff format` | `gofmt` |
| linter | `cargo clippy -- -D warnings` | `pnpm exec eslint --max-warnings 0` | `uv run ruff check` | `staticcheck` |
| test | `cargo test -q` | `pnpm exec vitest run --reporter=basic` | `uv run pytest -q` | `go test ./...` |
| build | `cargo build -q` | `pnpm exec tsc` / `vite build` | `python -m build` | `go build ./...` |

### Test skips

Do not commit an unexplained skip to the main branch. Tests that need networks, third-party accounts, or paid APIs must use a conditional feature or `@ignore` marker and state the required facility. CI should skip ignored tests by default; local runs must enable them explicitly.

## 5. Task runners

A task runner may be a `Justfile`, `package.json scripts`, `Makefile`, or `Taskfile.yml`. It must provide at least:

| Command | Meaning |
| --- | --- |
| `format` | Automatic formatting |
| `check` | Format plus static checking; stop immediately if format fails |
| `test` | Tests with quiet output by default |
| `build` | Build with quiet output by default |
| `ci` | `check -> test -> build -> check-links` |
| `check-links` | Document link integrity |

Use quiet flags for tests and builds unless full traces are needed for debugging. Recipe bodies must follow the project's shell convention. For native Windows support, provide a PowerShell equivalent or use a Node/Python implementation.

## 6. `check-links.py` interface

The script lives at `scripts/check-links.py` and uses only the Python 3 standard library; it does not require a shell. Examples:

```bash
python3 scripts/check-links.py
python3 scripts/check-links.py --exclude vendor --exclude generated
python3 scripts/check-links.py -e docs/archive -e fixtures --workers 4
python3 scripts/check-links.py --root path/to/repository
```

Behavior:

- Scan all `.md` files in the repository; exclude `.git`, `node_modules`, `dist`, `out`, and `target` by default.
- Accept repeated `-e/--exclude DIR` arguments, relative to the repository root; explicitly supplied non-existent directories fail clearly.
- Use `--root` to set the repository root; otherwise prefer the Git root and fall back to the current directory.
- Use `--workers` to control process parallelism; process one Markdown file per job and sort output in the main process for reproducibility.
- Use `concurrent.futures.ProcessPoolExecutor`; fall back to serial processing with a warning when the process pool is unavailable or the file set is small.
- Remove fenced and inline code before parsing `[label](target)`; skip `http:`, `https:`, `mailto:`, pure anchors, and placeholder targets containing `< >`.
- Resolve relative paths from the source file directory; check `#fragment` anchors on a best-effort basis, emit `[WARN]` when an anchor cannot be confirmed, and emit `[FAIL]` when a file is missing.
- Emit `[OK]`, `[WARN]`, and `[FAIL]`; return `1` for broken links, `2` for argument or environment errors, and `0` when no broken links exist.

## 7. Agent acceptance hooks

Hooks are the execution layer for gates; they do not replace ADRs or CI. Default mapping:

| Event | Purpose |
| --- | --- |
| `PreToolUse` | Block obvious dangerous commands such as `rm -rf`, force push, or `git reset --hard` |
| `PostToolUse` | Format after edits, test after test-file changes, and check links after Markdown changes |
| `Stop` | Run the complete `ci` gate when the turn ends |
| `UserPromptSubmit` | Inject the current project phase and gate commands |
| `PreCompact` | Persist governance discipline before context compaction |
| `Notification` | Report acceptance completion or failure |

Bind acceptance checks to `PostToolUse`, dangerous-operation blocking to `PreToolUse`, and final delivery checks to `Stop`.

### Trigger allowlists

PostToolUse must filter by file pattern:

- Formatting: source extensions such as `.rs`, `.ts`, `.py`, and `.go`.
- Testing: `tests/`, `*_test.*`, `*.spec.*`, and `__tests__/`.
- Links: `.md`, `.mdx`, `.mdc`, and project-specific `.txt` files.

Exit silently when a file does not match an allowlist. Editing Markdown must not trigger an unrelated formatter.

### Failure handling

| Failure type | Hook exit code | Agent behavior |
| --- | --- | --- |
| Gate failure | Non-zero | Inspect the error and fix/retry |
| Tool problem | Zero plus stderr log | Do not block editing; retain a diagnostic trail |
| Environment difference | Zero plus stderr warning | Do not block editing; let CI provide the final gate |

Hooks must be idempotent, observable, and fast (PostToolUse under 30 seconds, Stop under 600 seconds). Check hook configuration and scripts into git. Every project-level hook choice and boundary should have an ADR. Never use `exit 0` as a permanent bypass.

## 8. Completion checklist

- [ ] format, lint, test, and build are green.
- [ ] `check-links.py` reports no `[FAIL]` entries.
- [ ] Decision-bearing changes have been extracted into ADRs.
- [ ] Hooks use allowlists and CI runs independently.
- [ ] The hook/CI responsibility boundary is clear.
- [ ] Hook configuration and scripts are version-controlled.
