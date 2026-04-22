# InvestScan 완료 정의서
**Step 4 산출물** | 생성일: 2026-03-29 | 언어: English (P5-A)

---

## InvestScan의 "완료" 기준

### M0.0: Day 0 설치 완료 (DG-00)
- [ ] `personalizer.py --hello-test` 실행 시 10분 이내에 Telegram "설치 완료" 메시지 전송
- [ ] Telegram Bot Token + chat_id 정상 작동 확인

### M0.5: 핵심 파이프라인 준비 완료 (DG-01~08)
- [ ] `DG-01`: config.py가 investscan.yaml + keyring에서 API 키를 로드
- [ ] `DG-02`: normalizers.py가 database.json → 통합 신호(UnifiedSignal) 변환 (실제 필드명 기준)
- [ ] `DG-03`: synthesize_macro.py가 InvestmentMeta + 섹터 방향성 생성
- [ ] `DG-04`: sentinel 통과 — 모든 곳에서 `assert sentiment_weight == 0.0` 충족
- [ ] `DG-05`: compliance_filter.py가 10개 금지 패턴 전체를 대체/탐지
- [ ] `DG-06`: telegram_notifier.py가 `--dry-run` 모드에서 정상 작동
- [ ] `DG-07`: `run_m05.py --dry-run` 실행 시 전체 파이프라인이 오류 없이 완료
- [ ] `DG-08`: state.yaml에 `milestones.m05.dg_01_to_08_passed: true` 기록

### M1: 전체 파이프라인 준비 완료 (DG-09~16)
- [ ] `DG-09`: dedup.py가 source 필드를 포함한 콘텐츠 해시 기반 중복 제거 수행
- [ ] `DG-10`: steeps_classifier.py가 6개 STEEPs 전체에 대해 키워드 조회 사용 + 소문자 s/대문자 S 구분
- [ ] `DG-11`: signal_bridge.py가 E_env → industrials/materials 라우팅, 소문자 s → sector 필드 매핑
- [ ] `DG-12`: synthesize_stock.py가 DART 재무 데이터 + pykrx를 통합하되, 실패 시 우아하게 건너뜀
- [ ] `DG-13`: intelligence_engine.py가 영문 기준 1,000바이트 이상의 NarrativeOutput 생성
- [ ] `DG-14`: validate_report_quality.py Python 정규식 8개 기준 PASS + citation_validator.py PASS
- [ ] `DG-15`: `weekly_orchestrator.py --mode full-auto` 엔드투엔드 실행 성공
- [ ] `DG-16`: accuracy_tracker.py가 PredictionRecord를 기록하고 state.yaml 갱신
- [ ] `DG-17`: 포트폴리오 컨텍스트 — state.yaml의 portfolio.holdings 업데이트 가능, 리포트 생성기 비교 기능 검증 완료

### 번역 완료 게이트(Translation Done Gates) (TDG-01~06)
- [ ] `TDG-01`: schema-mapping.ko.md 존재, pACS >= 70
- [ ] `TDG-02`: completion-definition.ko.md 존재, pACS >= 70
- [ ] `TDG-03`: blueprint.ko.md 존재, pACS >= 70
- [ ] `TDG-04`: narrative_{date}.ko.json 존재, pACS >= 70
- [ ] `TDG-05`: weekly-report-{date}.ko.md 존재, pACS >= 70 (Fd 차원 포함)
- [ ] `TDG-06`: watchlist-{date}.ko.md 존재, pACS >= 70

---

## 품질 기준치

| 등급 | 모듈 | 커버리지 |
|------|------|----------|
| P1 핵심 | compliance_filter, synthesize_macro, steeps_classifier, stock_selector | 95% 이상 |
| 핵심 파이프라인 | normalizers, intelligence_engine, report_generator, weekly_orchestrator, validate_report_quality, citation_validator | 90% 이상 |
| 일반 | 기타 전체 | 85% 이상 |
| 인프라 | Hook, 스크립트 | 75% 이상 |

---

## 사용자 준비 완료 기준 (Phase E)

시스템이 "사용자 준비 완료" 상태가 되려면 다음 조건을 모두 충족해야 한다:
1. `run_m05.py --dry-run` → exit 0 (DG-01~08 전체 통과)
2. `python3 -m pytest tests/ -q` → 전체 통과, 커버리지 기준치 충족
3. 번역 완료 게이트 TDG-01~06 전체 GREEN (pACS >= 70)
4. `/weekly-report` 명령 → 영문 리포트 + 한국어 번역 쌍(.ko.md) 생성
5. Telegram 전송이 --dry-run 모드에서 정상 작동
6. 포트폴리오 컨텍스트(DG-17) 정상 작동

---

*본 문서는 구속력 있는 완료 계약서이다. "완료"로 표시된 모든 작업은 state.yaml 마일스톤을 true로 설정하기 전에 해당 완료 게이트를 반드시 충족해야 한다.*
