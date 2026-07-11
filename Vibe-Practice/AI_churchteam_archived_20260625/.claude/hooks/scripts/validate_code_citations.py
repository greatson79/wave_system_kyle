#!/usr/bin/env python3
"""
validate_code_citations.py — 산출 .md 내 `path:line` 형태 코드 인용을 사후 검증.

목적
----
LLM 산출 보고서가 흔히 환각하는 "파일 경로 + 라인 번호" 인용의 실재성을 결정적으로
검사한다. 절대 기준 ①(품질) — 할루시네이션 원천 봉쇄의 한 축.

작동 모드
---------
1) CLI: `python validate_code_citations.py <md_path> [<md_path> ...]`
2) Hook(stdin): Claude Code Hook payload(JSON) 수신 시 `tool_input.file_path` 또는
   `tool_response.filePath`에서 .md 경로 추출 후 검사.

검출 패턴
---------
- `foo/bar.py:42`           라인 단일
- `foo/bar.py:42-58`        라인 범위
- `foo/bar.py:L42`          GitHub 스타일
- `path/to/file.ext` (라인 없음 — 파일 존재만 검사)

판정 규칙
---------
- 파일 없음 → MISSING
- 라인 번호가 파일 라인 수 초과 → OUT_OF_RANGE
- 검사 통과 → OK

종료코드
--------
- 0: 항상 (경고 모드). settings.json에서 활성화될 때까지 비파괴적.
- 환경변수 `VALIDATE_CITATIONS_STRICT=1` 시 위반 발견 → exit 2.

SOT/RLM 영향
------------
- 쓰기 없음. 읽기 전용. SOT 무결성 보존.
- 어떤 SOT 필드도 수정하지 않음.

활성화 (별도 승인 후)
---------------------
.claude/settings.json `hooks.PostToolUse` 또는 `Stop`에 등록:
    {"matcher": "Write|Edit", "command": "python3 .claude/hooks/scripts/validate_code_citations.py"}
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

# path 후보: 영문/숫자/._/- 와 슬래시. 공백 직전까지. 확장자 필수로 파일성 확보.
CITATION_RE = re.compile(
    r"(?P<path>(?:[\w./\-]+/)?[\w.\-]+\.(?:py|md|json|yaml|yml|txt|sh|js|ts|tsx|html|css))"
    r"(?::L?(?P<start>\d+)(?:-(?P<end>\d+))?)?"
)

# 명백히 인용이 아닌 토큰 (코드블록 path 변수, requirements 등)
DENY_PREFIXES = ("http://", "https://", "git@", "ssh://", "ftp://")


def _is_real_file(p: Path) -> bool:
    try:
        return p.is_file()
    except OSError:
        return False


def _line_count(p: Path) -> int:
    try:
        with p.open("rb") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def scan_text(text: str, anchor_dir: Path) -> list[dict]:
    """
    text 내 모든 인용 후보 추출 → 검증 결과 리스트 반환.
    anchor_dir 기준 상대 경로 + 절대 경로 모두 시도.
    """
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for m in CITATION_RE.finditer(text):
        raw = m.group("path")
        if any(raw.startswith(pre) for pre in DENY_PREFIXES):
            continue
        start = m.group("start")
        end = m.group("end")
        key = (raw, start or "")
        if key in seen:
            continue
        seen.add(key)

        candidates = [Path(raw), anchor_dir / raw]
        # 프로젝트 루트(.claude/.git 보유) 탐색
        project_root = anchor_dir
        for _ in range(6):
            if (project_root / ".claude").exists() or (project_root / ".git").exists():
                candidates.append(project_root / raw)
                break
            if project_root.parent == project_root:
                project_root = anchor_dir
                break
            project_root = project_root.parent

        resolved = next((c for c in candidates if _is_real_file(c)), None)
        # basename만 적힌 경우 (e.g. "validate_pacs.py") — 프로젝트 루트 내 rglob
        if resolved is None and "/" not in raw:
            try:
                hits = list(project_root.rglob(raw))
                # node_modules/.git 등 노이즈 제외
                hits = [
                    h for h in hits
                    if not any(part.startswith(".") and part not in (".claude",) for part in h.parts)
                    and "node_modules" not in h.parts
                ]
                if hits:
                    resolved = hits[0]
            except OSError:
                pass
        if resolved is None:
            findings.append({"path": raw, "status": "MISSING", "line": start})
            continue

        if start is not None:
            s = int(start)
            e = int(end) if end else s
            n = _line_count(resolved)
            if s < 1 or e > n:
                findings.append(
                    {
                        "path": raw,
                        "status": "OUT_OF_RANGE",
                        "line": f"{s}-{e}",
                        "actual_lines": n,
                        "resolved": str(resolved),
                    }
                )
                continue

        findings.append({"path": raw, "status": "OK", "line": start})

    return findings


def report(findings_by_file: dict[str, list[dict]]) -> int:
    violations = 0
    for src, findings in findings_by_file.items():
        bad = [f for f in findings if f["status"] != "OK"]
        if not bad:
            continue
        violations += len(bad)
        print(f"[validate_code_citations] {src}", file=sys.stderr)
        for f in bad:
            line = f.get("line") or "-"
            extra = ""
            if f["status"] == "OUT_OF_RANGE":
                extra = f" (actual={f.get('actual_lines')})"
            print(
                f"  [{f['status']}] {f['path']}:{line}{extra}",
                file=sys.stderr,
            )
    return violations


def collect_md_paths_from_args(argv: list[str]) -> list[Path]:
    return [Path(a) for a in argv if a.endswith(".md")]


def collect_md_path_from_hook_payload() -> Path | None:
    if sys.stdin.isatty():
        return None
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    candidates = [
        payload.get("tool_input", {}).get("file_path"),
        payload.get("tool_response", {}).get("filePath"),
    ]
    for c in candidates:
        if c and c.endswith(".md"):
            return Path(c)
    return None


def main() -> int:
    targets: list[Path] = collect_md_paths_from_args(sys.argv[1:])
    if not targets:
        hook_target = collect_md_path_from_hook_payload()
        if hook_target:
            targets = [hook_target]
    if not targets:
        return 0  # 검사 대상 없음 — 무해 종료

    findings_by_file: dict[str, list[dict]] = {}
    for t in targets:
        if not _is_real_file(t):
            continue
        try:
            text = t.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings_by_file[str(t)] = scan_text(text, anchor_dir=t.parent)

    violations = report(findings_by_file)

    strict = os.environ.get("VALIDATE_CITATIONS_STRICT") == "1"
    if violations and strict:
        print(
            f"[validate_code_citations] STRICT mode: {violations} violation(s) — blocking.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
