# Security and releases

This reference covers security red lines, release procedure, version numbers, and release history. It fixes cross-project intent; credential backends, CI matrices, and exact commands belong in project security and release ADRs.

## 1. Credentials

- Never write passwords, tokens, or API keys to configuration files, command lines, or logs.
- Manage credentials through the project's chosen secure mechanism. Possible backends include keychains, credential managers, Windows Credential Manager, GPG-encrypted files, and environment variables; record the choice in a security ADR.
- Return a structured “not configured” error for an empty credential; do not panic or enter a retry loop.
- Return a clear error when the security backend is unavailable, and provide an interactive fallback only when the project allows it.
- Fix the credential namespace in an ADR, for example `<project>:<module>:<account>`.

## 2. Network calls

- Configure timeouts on every HTTP/TCP client. A performance ADR should define the actual values; a generic reference is 30 seconds for reads and 10 seconds for writes.
- Do not use a low-level socket stream without a timeout wrapper.
- Treat authentication failures and parameter errors as terminal; never retry them.
- Honor `Retry-After` on 429 responses and cap the retry count; a generic default is one retry.

## 3. Local files and output

- Convert `PermissionDenied` during configuration reads into an explicit error type.
- Ensure the parent directory exists before writing a local cache database.
- Normalize user-controlled paths and reject `..` traversal.
- Do not print complete internal network fields or server-specific identifiers.
- Never embed credentials in structured output; an authentication error may say only that account X lacks credentials.
- Fall back to a generic error envelope when structured output fails without breaking the external contract.

## 4. Concurrency, time, and disclosure

- Probe runtime liveness before touching async runtimes in destructors or cleanup paths. If the runtime has exited, reclaim resources quietly and avoid panics or borrowed-session leaks.
- Use an explicit ambiguity policy for local time, calendar dates, DST boundaries, and cross-time-zone input, such as selecting the earliest or latest valid time.
- For a public repository vulnerability, open an issue without attaching a reproduction script. Follow the team's private vulnerability process for private repositories.

## 5. Release procedure

Recommended order:

```text
Complete the phase
  -> all quality gates green
  -> ADR extraction complete
  -> separate version-bump commit
  -> synchronize current version references in README / skills / ADR index
  -> update progress.md release history
  -> create an annotated tag
  -> push only to the primary remote
  -> monitor the CI release workflow to completion
```

### Version bump

1. Update the `version` in the primary configuration file (`package.json`, `Cargo.toml`, `pyproject.toml`, and so on).
2. Let the build tool update the lockfile; do not edit the lockfile by hand.
3. Synchronize user documentation, entry status, and release history.
4. Use `chore: release vX.Y.Z` in a separate commit from feature work.

### Tags and CI

- Use an annotated tag: `git tag -a vX.Y.Z -m "vX.Y.Z: <highlights>"`.
- Include highlights, known fixes, and breaking changes in the tag message.
- Push only to the agreed primary remote; do not push to mirror remotes.
- A release workflow should listen for `v*` and include builds for at least three platforms, artifact upload, and release-note generation.
- If CI fails, fix the issue and recreate the tag; never force-push an already published tag.

## 6. Version policy

| Change | SemVer |
| --- | --- |
| Breaking public API change | major |
| Backward-compatible feature | minor |
| Internal fix | patch |
| Documentation, tests, or CI | Usually no release |

Distinguish between:

- the current project version, synchronized on every release;
- a module's first-completed version and historical ADR references, which are facts and must not be rewritten.

Create an ADR before a breaking change, add `BREAKING CHANGE: <description>` to the commit footer, label it explicitly in README/skill documentation, and mark it as breaking in the release summary.

## 7. Release history

Maintain `progress.md` in descending version order:

```markdown
## Release history
| Version | Tag | Summary | Main ADR |
| --- | --- | --- | --- |
| vX.Y.Z | `vX.Y.Z` | One-line change | [ADR-id](...) |
```

Record the concrete security or release backend in a project-level ADR. This reference does not turn any platform-specific command into a universal requirement.
