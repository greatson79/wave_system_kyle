"""Safety-contract tests for run_scoped."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ADAPTER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER_DIR))

from run_scoped import (  # noqa: E402
    RunLedger,
    StartTickMismatchError,
    start_scoped,
    stop_scoped,
)


class FakeProcess:
    pid = 4321


class RunScopedTests(unittest.TestCase):
    def test_start_records_argv_pid_pgid_and_start_tick(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            run = start_scoped(
                ["python3", "-c", "pass"],
                ledger=ledger,
                popen=lambda argv, **kwargs: FakeProcess(),
                getpgid=lambda pid: 4321,
                start_tick=lambda pid: "2026-07-10 21:00:00",
            )

            saved = json.loads(ledger.path.read_text(encoding="utf-8"))
            self.assertEqual(run["pid"], 4321)
            self.assertEqual(run["pgid"], 4321)
            self.assertEqual(run["start_tick"], "2026-07-10 21:00:00")
            self.assertEqual(run["argv"], ["python3", "-c", "pass"])
            self.assertEqual(saved["runs"][run["run_id"]], run)

    def test_stop_fails_closed_without_signal_when_start_tick_changed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            ledger.write(
                {
                    "runs": {
                        "run-1": {
                            "run_id": "run-1",
                            "pid": 4321,
                            "pgid": 4321,
                            "start_tick": "old",
                            "argv": ["sleep", "10"],
                        }
                    }
                }
            )
            signals: list[tuple[int, int]] = []

            with self.assertRaises(StartTickMismatchError):
                stop_scoped(
                    "run-1",
                    ledger=ledger,
                    getpgid=lambda pid: 4321,
                    start_tick=lambda pid: "new",
                    killpg=lambda pgid, sig: signals.append((pgid, sig)),
                )

            self.assertEqual(signals, [])

    def test_start_kills_the_identity_verified_orphan_when_ledger_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            signals: list[tuple[int, int]] = []

            def _boom(payload: dict) -> None:
                raise OSError("disk full")

            ledger.write = _boom  # type: ignore[method-assign]

            with self.assertRaises(OSError):
                start_scoped(
                    ["python3", "-c", "pass"],
                    ledger=ledger,
                    popen=lambda argv, **kwargs: FakeProcess(),
                    getpgid=lambda pid: 4321,
                    start_tick=lambda pid: "2026-07-10 21:00:00",
                    killpg=lambda pgid, sig: signals.append((pgid, sig)),
                )

            # getpgid+start_tick both captured and re-verified identical on cleanup -> safe to signal.
            self.assertEqual(signals, [(4321, 9)])

    def test_start_fails_closed_without_signal_when_start_tick_lookup_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            signals: list[tuple[int, int]] = []

            with self.assertRaises(ProcessLookupError):
                start_scoped(
                    ["python3", "-c", "pass"],
                    ledger=ledger,
                    popen=lambda argv, **kwargs: FakeProcess(),
                    getpgid=lambda pid: 4321,
                    start_tick=lambda pid: (_ for _ in ()).throw(ProcessLookupError("gone")),
                    killpg=lambda pgid, sig: signals.append((pgid, sig)),
                )

            # start_tick was never captured, so there is no verified identity to clean up
            # against — refuse to signal rather than guess (RS-START-2).
            self.assertEqual(signals, [])

    def test_start_fails_closed_without_signal_when_cleanup_observes_a_reused_pgid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            signals: list[tuple[int, int]] = []
            getpgid_calls = {"count": 0}

            def _getpgid(pid: int) -> int:
                getpgid_calls["count"] += 1
                # First call captures the real identity; the re-check during cleanup
                # observes a different pgid, simulating the pid having been reused
                # by an unrelated process after the original child exited.
                return 4321 if getpgid_calls["count"] == 1 else 9999

            def _boom(payload: dict) -> None:
                raise OSError("disk full")

            ledger.write = _boom  # type: ignore[method-assign]

            with self.assertRaises(OSError):
                start_scoped(
                    ["python3", "-c", "pass"],
                    ledger=ledger,
                    popen=lambda argv, **kwargs: FakeProcess(),
                    getpgid=_getpgid,
                    start_tick=lambda pid: "2026-07-10 21:00:00",
                    killpg=lambda pgid, sig: signals.append((pgid, sig)),
                )

            self.assertEqual(signals, [])

    def test_stop_signals_only_the_recorded_group_after_identity_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = RunLedger(Path(temp_dir) / "run_ledger.json")
            ledger.write(
                {
                    "runs": {
                        "run-1": {
                            "run_id": "run-1",
                            "pid": 4321,
                            "pgid": 4321,
                            "start_tick": "same",
                            "argv": ["sleep", "10"],
                        }
                    }
                }
            )
            signals: list[tuple[int, int]] = []

            stop_scoped(
                "run-1",
                ledger=ledger,
                getpgid=lambda pid: 4321,
                start_tick=lambda pid: "same",
                killpg=lambda pgid, sig: signals.append((pgid, sig)),
            )

            self.assertEqual(signals, [(4321, 15)])


if __name__ == "__main__":
    unittest.main()
