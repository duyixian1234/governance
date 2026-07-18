#!/usr/bin/env python3
"""Check relative Markdown links with optional parallel file processing.

Exit codes:
  0: no broken links
  1: at least one broken link
  2: invalid arguments or environment error
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from urllib.parse import unquote

DEFAULT_EXCLUDES = (".git", "node_modules", "dist", "out", "target")
# Captures either an angle-bracket target (which may contain spaces) or a
# compact target. Optional link titles are deliberately ignored.
LINK_RE = re.compile(
    r"\[[^\]]*\]\((?:<([^>\n]+)>|([^\s)]+))(?:\s+[^)]*)?\)"
)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")


class ConfigurationError(ValueError):
    """Raised for invalid command-line or repository configuration."""


def git_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return Path(value).resolve() if value else None


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def strip_code(text: str) -> str:
    """Remove fenced and inline code while preserving line numbers."""
    output: list[str] = []
    in_fence = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence = True
            fence = stripped[:3]
            output.append("")
            continue
        if in_fence:
            output.append("")
            if stripped.startswith(fence):
                in_fence = False
                fence = ""
            continue
        output.append(re.sub(r"`[^`\n]*`", "", line))
    return "\n".join(output)


def slugify_heading(value: str) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"<[^>]+>", "", value).strip().lower()
    value = re.sub(r"[^\w\s-]", "", value, flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", value).strip("-")


def heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            slug = slugify_heading(match.group(1))
            if slug:
                slugs.add(slug)
    return slugs


def check_file(payload: tuple[str, str, str]) -> list[tuple[str, str, int, str]]:
    """Check one Markdown file; kept top-level so it can run in a process pool."""
    file_name, root_name, display_name = payload
    path = Path(file_name)
    root = Path(root_name)
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return [("FAIL", display_name, 0, f"cannot read file: {exc}")]

    cleaned = strip_code(text)
    issues: list[tuple[str, str, int, str]] = []
    for match in LINK_RE.finditer(cleaned):
        target = (match.group(1) or match.group(2) or "").strip()
        line_no = cleaned.count("\n", 0, match.start()) + 1
        if not target:
            continue
        if re.match(r"^(?:https?:|mailto:|ftp:)", target, flags=re.IGNORECASE):
            continue
        if target.startswith("#"):
            continue
        if "<" in target or ">" in target:
            continue

        path_part, separator, fragment = target.partition("#")
        path_part = unquote(path_part)
        fragment = unquote(fragment) if separator else ""
        if not path_part:
            continue
        candidate = Path(path_part)
        if candidate.is_absolute():
            issues.append(("FAIL", display_name, line_no, f"absolute path is forbidden: {target}"))
            continue

        resolved = (path.parent / candidate).resolve()
        if not resolved.exists():
            issues.append(
                (
                    "FAIL",
                    display_name,
                    line_no,
                    f"{target} -> {resolved.relative_to(root) if is_within(resolved, root) else resolved}",
                )
            )
            continue

        if fragment and resolved.is_file() and resolved.suffix.lower() == ".md":
            try:
                linked_text = resolved.read_text(encoding="utf-8", errors="replace")
                known_slugs = heading_slugs(linked_text)
            except OSError:
                known_slugs = set()
            if slugify_heading(fragment) not in known_slugs and fragment not in known_slugs:
                issues.append(
                    (
                        "WARN",
                        display_name,
                        line_no,
                        f"anchor not confirmed (best-effort): {target}",
                    )
                )
    return issues


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check relative links in Markdown files. Exclusions may be repeated."
    )
    parser.add_argument(
        "-e",
        "--exclude",
        action="append",
        default=[],
        metavar="DIR",
        help="directory relative to the repository root to exclude; may be repeated",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="repository root (default: Git root, otherwise current directory)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, os.cpu_count() or 1),
        metavar="N",
        help="number of worker processes (default: CPU count; use 1 for serial)",
    )
    return parser.parse_args(argv)


def resolve_root(value: Path | None) -> Path:
    root = value.resolve() if value else (git_root() or Path.cwd().resolve())
    if not root.exists() or not root.is_dir():
        raise ConfigurationError(f"root is not a directory: {root}")
    return root


def resolve_excludes(root: Path, values: list[str]) -> list[Path]:
    resolved: list[Path] = [(root / name).resolve() for name in DEFAULT_EXCLUDES]
    for value in values:
        raw = Path(value).expanduser()
        candidate = raw.resolve() if raw.is_absolute() else (root / raw).resolve()
        if not is_within(candidate, root):
            raise ConfigurationError(f"exclude path is outside root: {value}")
        if not candidate.exists() or not candidate.is_dir():
            raise ConfigurationError(f"exclude path is not an existing directory: {value}")
        resolved.append(candidate)
    # Preserve order for deterministic traversal while removing duplicates.
    return list(dict.fromkeys(resolved))


def collect_markdown(root: Path, excludes: list[Path]) -> list[Path]:
    files: list[Path] = []
    for current, dir_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current).resolve()
        dir_names[:] = [
            name
            for name in sorted(dir_names)
            if not any(is_within((current_path / name).resolve(), excluded) for excluded in excludes)
        ]
        for name in sorted(file_names):
            path = (current_path / name).resolve()
            if path.suffix.lower() == ".md" and not any(is_within(path, excluded) for excluded in excludes):
                files.append(path)
    return sorted(files)


def format_issue(issue: tuple[str, str, int, str]) -> str:
    level, display_name, line_no, detail = issue
    location = f"{display_name}:{line_no}" if line_no else display_name
    return f"[{level}] {location}: {detail}"


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv or sys.argv[1:])
        if args.workers < 1:
            raise ConfigurationError("--workers must be at least 1")
        root = resolve_root(args.root)
        excludes = resolve_excludes(root, args.exclude)
        files = collect_markdown(root, excludes)
        payloads = [
            (
                str(path),
                str(root),
                path.relative_to(root).as_posix(),
            )
            for path in files
        ]
    except ConfigurationError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 2

    issues: list[tuple[str, str, int, str]] = []
    if len(payloads) > 1 and args.workers > 1:
        try:
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                for result in pool.map(check_file, payloads):
                    issues.extend(result)
        except (OSError, RuntimeError) as exc:
            print(f"[WARN] process pool unavailable; falling back to serial: {exc}", file=sys.stderr)
            issues = [issue for payload in payloads for issue in check_file(payload)]
    else:
        issues = [issue for payload in payloads for issue in check_file(payload)]

    issues.sort(key=lambda item: (item[1], item[2], item[0], item[3]))
    for issue in issues:
        print(format_issue(issue))

    failures = sum(issue[0] == "FAIL" for issue in issues)
    warnings = sum(issue[0] == "WARN" for issue in issues)
    if failures:
        print(f"[FAIL] {failures} broken link(s) across {len(files)} files.")
        if warnings:
            print(f"[WARN] {warnings} warning(s).")
        return 1
    if warnings:
        print(f"[WARN] {warnings} warning(s); no broken links across {len(files)} files.")
    else:
        print(f"[OK] no broken links across {len(files)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
