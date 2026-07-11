#!/usr/bin/env python3
"""4-fold deterministic gate before a master `/clear` (CSO_DIRECTIVE.md §5).

Checks, in order: sha256 of the SOT matches the ack, SOT mtime is at or after
the notification nonce, the 3 required narrative fields are present, and the
git worktree has no uncommitted changes. Any single failure fails the whole
gate closed — this tool never guesses "probably fine".
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

REQUIRED_FIELD_PATTERNS: dict[str, tuple[str, ...]] = {
    "현재 위치": ("현재 위치", "현재 상태"),
    "다음 액션": ("다음 액션",),
    "미해결 게이트": ("미해결 게이트", "블로커"),
}


class CheckFailure(RuntimeError):
    """A single verify_cycle check failed; carries the item name and reason."""

    def __init__(self, name: str, reason: str) -> None:
        super().__init__(f"{name}: {reason}")
        self.name = name
        self.reason = reason


def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _default_git_status(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _check_sha256(sot_path: Path, expected_sha256: str) -> tuple[bool, str]:
    try:
        actual = sha256_of_file(sot_path)
    except OSError as error:
        return False, f"could not read SOT: {error}"
    if actual != expected_sha256:
        return False, f"expected {expected_sha256}, got {actual}"
    return True, actual


def _check_mtime(sot_path: Path, nonce_time: datetime) -> tuple[bool, str]:
    try:
        mtime = datetime.fromtimestamp(sot_path.stat().st_mtime, tz=timezone.utc)
    except OSError as error:
        return False, f"could not stat SOT: {error}"
    if mtime < nonce_time:
        return False, f"SOT mtime {mtime.isoformat()} is before nonce {nonce_time.isoformat()}"
    return True, mtime.isoformat()


def _check_required_fields(sot_path: Path) -> tuple[bool, str]:
    try:
        text = sot_path.read_text(encoding="utf-8")
    except OSError as error:
        return False, f"could not read SOT: {error}"
    missing = [
        field
        for field, patterns in REQUIRED_FIELD_PATTERNS.items()
        if not any(pattern in text for pattern in patterns)
    ]
    if missing:
        return False, f"missing field(s): {', '.join(missing)}"
    return True, "all required fields present"


def _check_git_clean(git_status: Callable[[], str]) -> tuple[bool, str]:
    try:
        output = git_status()
    except (OSError, subprocess.SubprocessError) as error:
        return False, f"git status failed: {error}"
    if output.strip():
        return False, f"worktree not clean:\n{output.strip()}"
    return True, "worktree clean"


def verify_cycle(
    sot_path: Path,
    *,
    expected_sha256: str,
    nonce_time: datetime,
    git_status: Callable[[], str],
) -> dict[str, object]:
    """Run all 4 checks and return a deterministic PASS/FAIL report.

    Every check always runs (no short-circuit) so a single report shows the
    full picture instead of one failure at a time.
    """
    checks = []
    for name, check in (
        ("sha256", lambda: _check_sha256(sot_path, expected_sha256)),
        ("mtime", lambda: _check_mtime(sot_path, nonce_time)),
        ("required_fields", lambda: _check_required_fields(sot_path)),
        ("git_clean", lambda: _check_git_clean(git_status)),
    ):
        passed, detail = check()
        checks.append({"name": name, "passed": passed, "detail": detail})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}


def _parse_nonce_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sot", type=Path, required=True, help="path to the SOT markdown file")
    parser.add_argument("--sha256", required=True, help="expected sha256 from the ack")
    parser.add_argument("--nonce-time", required=True, help="ISO 8601 timestamp of the clear notification")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="git worktree root for the clean check")
    args = parser.parse_args(argv)

    result = verify_cycle(
        args.sot,
        expected_sha256=args.sha256,
        nonce_time=_parse_nonce_time(args.nonce_time),
        git_status=lambda: _default_git_status(args.repo),
    )

    for check in result["checks"]:
        if check["passed"]:
            print(f"PASS {check['name']}")
        else:
            print(f"FAIL {check['name']} {check['detail']}", file=sys.stderr)

    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
