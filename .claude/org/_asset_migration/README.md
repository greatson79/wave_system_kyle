# 작업자산축 마이그레이션 — 외부 앵커 (root-of-trust)

> 위치: `.claude/org/_asset_migration/` (★git 추적 영역 — history 불변성이 앵커를 보호)
> 목적: `scan_asset_refs.sh` 검증기의 **신뢰의 뿌리**를 `output/…/refscan/`(작업 쓰기영역) **밖**에 둔다.

## 왜 외부 앵커인가 (codex BLOCK v1.5 §1)
`summary`·`SEAL`·`baseline`이 전부 `refscan/`(같은 쓰기영역)이면, 셋을 **동시에 바꿔치기**하면 검증을 통과한다. 신뢰의 뿌리는 작업 쓰기영역 밖에 있어야 한다.

- **`APPROVED_SEAL.sha`** = 스캔마다 append되는 앵커 레코드(아래 형식). `.claude/`는 git 추적이라 변조 시 `git diff`·`git log`에 드러난다.
- 검증기(`verify`)는 **이 앵커부터** 검증한다: 앵커의 `summary_sha256` = 실제 summary 해시, 앵커의 `seal_sha` = summary 헤더 seal = 실제 SEAL 해시 — **삼중 일치**. 하나라도 어긋나면 exit 4.
- 신뢰 사슬: **git 앵커(외부)** → summary → SEAL → baseline 5파일.

## APPROVED_SEAL.sha 형식 (TSV · 1행/스캔)
```
<STAMP>	<baseline_seal_sha256>	<summary_sha256>	<UTC>	<승인자>
```
- `승인자` = `strategy-team`(스캔 시점) → 실제 마이그레이션 집행 승인 시 `owner-gate`로 갱신(주인님 게이트 레코드).
- 커밋 메시지에 STAMP를 남겨 git history로 이중 추적한다.

## 운영
- `scan` 완료 시 append(기존 행 보존) + git add/commit(집행 게이트에서).
- 실제 자산 이동은 주인님 게이트 후에만. 이 앵커는 이동 전 baseline을 봉인해 이동 후 verify가 대조할 기준을 고정한다.
