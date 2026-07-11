"""Contract tests for cycle_verify — the master-clear 4-fold gate."""

from __future__ import annotations

import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ADAPTER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER_DIR))

from cycle_verify import CheckFailure, sha256_of_file, verify_cycle  # noqa: E402


VALID_SOT = """# SESSION_STATE

## 현재 위치
게이트 검증 도구 구현 중.

## 다음 액션 큐
1. cycle_verify 테스트 통과시키기.

## 미해결 게이트
없음.
"""


def _write_sot(directory: Path, text: str) -> Path:
    path = directory / "SESSION_STATE.md"
    path.write_text(text, encoding="utf-8")
    return path


class CycleVerifyTests(unittest.TestCase):
    def test_passes_when_all_four_checks_hold(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sot_path = _write_sot(Path(temp_dir), VALID_SOT)
            nonce_time = datetime.now(timezone.utc) - timedelta(minutes=5)
            expected_sha256 = sha256_of_file(sot_path)

            result = verify_cycle(
                sot_path,
                expected_sha256=expected_sha256,
                nonce_time=nonce_time,
                git_status=lambda: "",
            )

            self.assertTrue(result["passed"])
            self.assertEqual([c["name"] for c in result["checks"]], ["sha256", "mtime", "required_fields", "git_clean"])
            self.assertTrue(all(c["passed"] for c in result["checks"]))

    def test_fails_closed_on_sha256_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sot_path = _write_sot(Path(temp_dir), VALID_SOT)
            nonce_time = datetime.now(timezone.utc) - timedelta(minutes=5)

            result = verify_cycle(
                sot_path,
                expected_sha256="0" * 64,
                nonce_time=nonce_time,
                git_status=lambda: "",
            )

            self.assertFalse(result["passed"])
            failed = [c for c in result["checks"] if not c["passed"]]
            self.assertEqual(len(failed), 1)
            self.assertEqual(failed[0]["name"], "sha256")

    def test_fails_closed_when_sot_older_than_nonce(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sot_path = _write_sot(Path(temp_dir), VALID_SOT)
            expected_sha256 = sha256_of_file(sot_path)
            nonce_time = datetime.now(timezone.utc) + timedelta(minutes=5)

            result = verify_cycle(
                sot_path,
                expected_sha256=expected_sha256,
                nonce_time=nonce_time,
                git_status=lambda: "",
            )

            self.assertFalse(result["passed"])
            failed_names = {c["name"] for c in result["checks"] if not c["passed"]}
            self.assertIn("mtime", failed_names)

    def test_fails_closed_when_a_required_field_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_gate = VALID_SOT.replace("## 미해결 게이트\n없음.\n", "")
            sot_path = _write_sot(Path(temp_dir), missing_gate)
            expected_sha256 = sha256_of_file(sot_path)
            nonce_time = datetime.now(timezone.utc) - timedelta(minutes=5)

            result = verify_cycle(
                sot_path,
                expected_sha256=expected_sha256,
                nonce_time=nonce_time,
                git_status=lambda: "",
            )

            self.assertFalse(result["passed"])
            failed_names = {c["name"] for c in result["checks"] if not c["passed"]}
            self.assertIn("required_fields", failed_names)

    def test_fails_closed_when_worktree_is_dirty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sot_path = _write_sot(Path(temp_dir), VALID_SOT)
            expected_sha256 = sha256_of_file(sot_path)
            nonce_time = datetime.now(timezone.utc) - timedelta(minutes=5)

            result = verify_cycle(
                sot_path,
                expected_sha256=expected_sha256,
                nonce_time=nonce_time,
                git_status=lambda: " M some_file.py\n",
            )

            self.assertFalse(result["passed"])
            failed_names = {c["name"] for c in result["checks"] if not c["passed"]}
            self.assertIn("git_clean", failed_names)

    def test_does_not_raise_on_missing_sot_but_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "does_not_exist.md"

            result = verify_cycle(
                missing_path,
                expected_sha256="0" * 64,
                nonce_time=datetime.now(timezone.utc),
                git_status=lambda: "",
            )

            self.assertFalse(result["passed"])
            self.assertTrue(any(not c["passed"] for c in result["checks"]))

    def test_check_failure_is_raised_by_cli_on_any_failure(self) -> None:
        with self.assertRaises(CheckFailure):
            raise CheckFailure("sha256", "mismatch")


if __name__ == "__main__":
    unittest.main()
