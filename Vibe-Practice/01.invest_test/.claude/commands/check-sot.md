# /check-sot — InvestScan SOT 상태 확인

SOT Inspector SubAgent를 spawn하여 계층적 SOT + 번역 상태 리포트를 생성합니다.
출력은 한국어 (사용자 직접 조회 — P5-B 한국어 허용 채널).

## Execution Flow
1. Read `.claude/state.yaml` (Global SOT)
2. Read `.claude/state/phase-*.yaml` (Phase SOTs)
3. Read `.claude/agent-workspace/*.yaml` (SubAgent workspaces)
4. Read `pacs-logs/*.md` (translation pACS logs)
5. Render Korean dashboard output

## Output Format
```
InvestScan 상태 — [datetime]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase: [phase] | Step: [N]/15 | Mode: [runtime_mode]
언어 정책: English-First (P5) | HITL: H1=[✓/✗] H2=[✓/✗] H3=[✓/✗]

TDD 상태:
  P1 Critical (95%+):
    [✓/✗/○] compliance_filter
    [✓/✗/○] synthesize_macro
    [✓/✗/○] steeps_classifier
    [✓/✗/○] stock_selector
  핵심 파이프라인 (90%+):
    [✓/✗/○] normalizers
    [✓/✗/○] intelligence_engine
    [✓/✗/○] report_generator
    [✓/✗/○] weekly_orchestrator
    [✓/✗/○] validate_report_quality
    [✓/✗/○] citation_validator

번역 상태:
  [✓/✗/○] Step 2  (schema-mapping.ko.md)           pACS=[N/--]
  [✓/✗/○] Step 4  (completion-definition.ko.md)    pACS=[N/--]
  [✓/✗/○] Step 5  (blueprint.ko.md)                pACS=[N/--]
  [✓/✗/○] Step 11 (narrative_{date}.ko.json)       pACS=[N/--]
  [✓/✗/○] Step 12 (weekly-report-{date}.ko.md)     pACS=[N/--] Fd=[N/--]
  [✓/✗/○] Step 15 (watchlist-{date}.ko.md)         pACS=[N/--]

포트폴리오: [보유 종목 수]개 | 마지막 갱신: [date]
라이브러리: FDR=[가용률/--] pykrx=[가용률/--] dart-fss=[가용률/--]
오류: [count]개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
범례: ✓=통과 ✗=실패 ○=대기중/미실행 --=데이터없음
```

## Legend
- `✓` = passing / done (GREEN pACS)
- `✗` = failing / RED pACS
- `○` = pending / not yet run
- `--` = no data yet
