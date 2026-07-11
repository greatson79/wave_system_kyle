#!/usr/bin/env python3
"""Start and stop dedicated process groups with a fail-closed run ledger."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence
from uuid import uuid4


class RunScopedError(RuntimeError):
    """Base error for a run-scoped safety check."""


class StartTickMismatchError(RunScopedError):
    """Raised when a PID no longer identifies the recorded process."""


class ProcessGroupMismatchError(RunScopedError):
    """Raised when a PID no longer belongs to the recorded process group."""


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temporary_path = Path(handle.name)
    os.replace(temporary_path, path)


class RunLedger:
    """The only persistent source used by safe group termination."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"runs": {}}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or not isinstance(payload.get("runs"), dict):
            raise RunScopedError(f"invalid run ledger: {self.path}")
        return payload

    def write(self, payload: dict[str, Any]) -> None:
        _atomic_json_write(self.path, payload)


def process_start_tick(pid: int) -> str:
    """Return macOS process start time; failure is unsafe for a later stop."""
    completed = subprocess.run(
        ["ps", "-p", str(pid), "-o", "lstart="],
        check=True,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    if not value:
        raise ProcessLookupError(f"process start tick unavailable for pid {pid}")
    return value


def _validate_argv(argv: Sequence[str]) -> list[str]:
    if not argv or any(not isinstance(part, str) or not part for part in argv):
        raise ValueError("argv must contain one or more non-empty string arguments")
    return list(argv)


def start_scoped(
    argv: Sequence[str],
    *,
    ledger: RunLedger,
    popen: Callable[..., Any] = subprocess.Popen,
    getpgid: Callable[[int], int] = os.getpgid,
    start_tick: Callable[[int], str] = process_start_tick,
    killpg: Callable[[int, int], None] = os.killpg,
) -> dict[str, Any]:
    """Start an argv-only command in a new session and record its identity.

    Transactional: if anything after the spawn fails (pgid/start-tick lookup,
    ledger read/write), the just-spawned process group is killed before the
    error propagates — a run_scoped hygiene tool must never itself leave an
    unrecorded, unmanaged orphan behind.
    """
    command = _validate_argv(argv)
    process = popen(command, start_new_session=True)
    pid = int(process.pid)
    captured_pgid: int | None = None
    captured_tick: str | None = None
    try:
        captured_pgid = int(getpgid(pid))
        captured_tick = start_tick(pid)
        now = datetime.now(timezone.utc).isoformat()
        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:12]}"
        record = {
            "run_id": run_id,
            "argv": command,
            "pid": pid,
            "pgid": captured_pgid,
            "start_tick": captured_tick,
            "started_at": now,
            "status": "running",
        }
        payload = ledger.read()
        payload["runs"][run_id] = record
        ledger.write(payload)
    except BaseException:
        _kill_unrecorded_orphan(
            pid,
            captured_pgid=captured_pgid,
            captured_tick=captured_tick,
            getpgid=getpgid,
            start_tick=start_tick,
            killpg=killpg,
        )
        raise
    return record


def _kill_unrecorded_orphan(
    pid: int,
    *,
    captured_pgid: int | None,
    captured_tick: str | None,
    getpgid: Callable[[int], int],
    start_tick: Callable[[int], str],
    killpg: Callable[[int, int], None],
) -> None:
    """Fail-closed cleanup of a just-spawned, never-recorded process (RS-START-2).

    A group signal is only ever sent when BOTH the pgid and the immutable
    start tick were captured right after spawn AND still match on a fresh
    lookup — the same two-factor identity check RS-1 established for
    stop_scoped. If the direct child already exited before we captured its
    identity (captured_pgid/captured_tick is None), or a fresh lookup now
    disagrees with what we captured (pid/pgid reused by an unrelated
    process), we refuse to signal and instead surface the incident for a
    human/operator to handle — guessing here would risk killing an
    unrelated process group, exactly the class of bug this tool exists to
    prevent.

    ★Residual race (CEO technical review, 2026-07-10 — honest disclosure,
    not fixed by this function): this is TOCTOU (time-of-check-to-time-of-
    use), not a solved race. Re-verifying identity narrows the window to
    "lookup, then killpg()" instead of the original full gap, but cannot
    close it to zero — the process can still exit and its pid/pgid be
    reused by the kernel in the instant between the identity re-check
    above and the killpg() call below. A 3rd occurrence of this defect
    class (RS-1 -> RS-START-1 -> RS-START-2) already happened before this
    fix; if it recurs a 4th time, that is a signal to stop patching and
    adopt the supervisor-held-handle pattern instead (spawn via a
    supervisor that retains the child via waitpid and only ever signals
    its own tracked child — this removes PID/PGID reuse ambiguity at the
    source rather than re-checking against it).
    """
    if captured_pgid is None or captured_tick is None:
        print(
            f"run_scoped: unrecorded process pid={pid} — identity was never "
            "captured, refusing to signal (fail-closed)",
            file=sys.stderr,
        )
        return
    try:
        current_pgid = int(getpgid(pid))
        current_tick = start_tick(pid)
    except OSError:
        print(
            f"run_scoped: unrecorded process pid={pid} — could not re-verify "
            "identity, refusing to signal (fail-closed)",
            file=sys.stderr,
        )
        return
    if current_pgid != captured_pgid or current_tick != captured_tick:
        print(
            f"run_scoped: unrecorded process pid={pid} — identity changed since "
            "spawn (pid/pgid reuse), refusing to signal (fail-closed)",
            file=sys.stderr,
        )
        return
    try:
        killpg(captured_pgid, signal.SIGKILL)
    except OSError:
        pass  # already exited — nothing left to clean up


def stop_scoped(
    run_id: str,
    *,
    ledger: RunLedger,
    getpgid: Callable[[int], int] = os.getpgid,
    start_tick: Callable[[int], str] = process_start_tick,
    killpg: Callable[[int, int], None] = os.killpg,
) -> dict[str, Any]:
    """Send TERM only after PID, PGID, and immutable process start tick all match.

    ★Residual race (CEO technical review, 2026-07-10 — honest disclosure):
    same TOCTOU class as `_kill_unrecorded_orphan` — the identity check
    below narrows, but cannot close to zero, the window between "verified
    match" and the killpg() call. See that function's docstring for the
    supervisor-held-handle escalation rule if this defect class recurs.
    """
    payload = ledger.read()
    record = payload["runs"].get(run_id)
    if not isinstance(record, dict):
        raise RunScopedError(f"unknown run_id: {run_id}")
    pid = record.get("pid")
    pgid = record.get("pgid")
    recorded_tick = record.get("start_tick")
    if not isinstance(pid, int) or not isinstance(pgid, int) or not isinstance(recorded_tick, str):
        raise RunScopedError(f"invalid run record: {run_id}")

    current_pgid = getpgid(pid)
    if current_pgid != pgid:
        raise ProcessGroupMismatchError(
            f"refusing TERM: pid {pid} now has pgid {current_pgid}, expected {pgid}"
        )
    current_tick = start_tick(pid)
    if current_tick != recorded_tick:
        raise StartTickMismatchError(
            f"refusing TERM: pid {pid} start tick changed from {recorded_tick!r} to {current_tick!r}"
        )

    killpg(pgid, signal.SIGTERM)
    record["status"] = "term_requested"
    record["term_requested_at"] = datetime.now(timezone.utc).isoformat()
    ledger.write(payload)
    return record


def _default_ledger_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "output" / "DiA" / "경영본부" / "_round" / "run_ledger.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=_default_ledger_path())
    subparsers = parser.add_subparsers(dest="action", required=True)
    start_parser = subparsers.add_parser("start", help="start an argv-only command in a new session")
    start_parser.add_argument("command", nargs=argparse.REMAINDER)
    stop_parser = subparsers.add_parser("stop", help="TERM a previously recorded process group")
    stop_parser.add_argument("run_id")
    args = parser.parse_args(argv)
    ledger = RunLedger(args.ledger)
    try:
        if args.action == "start":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            print(json.dumps(start_scoped(command, ledger=ledger), ensure_ascii=False))
        else:
            print(json.dumps(stop_scoped(args.run_id, ledger=ledger), ensure_ascii=False))
    except (RunScopedError, ValueError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
