# Vibe-Practice — 실험적 AI 에이전트 프로젝트

AI 에이전트 아이디어를 빠르게 검증하는 실험 공간.
완성도보다 속도·탐색이 우선. 검증된 것은 `Claude_skills/`로 이전.

---

## 프로젝트 목록

| 프로젝트 | 상태 | 설명 |
|---------|------|------|
| `01.invest_test/` | 🟡 개발 중 | 주식 투자 주간 스캔 시스템 (Python) |
| `GlobalNews-Crawling-AgenticWorkflow/` | 🟢 운영 중 | 글로벌 뉴스 수집·분석 파이프라인 |
| `EnvironmentScan-system-main-v4-main/` | 🟢 운영 중 | 환경 스캐닝 자동화 |
| `Dissertation-Simulator-AgenticWorkflow-main/` | 🔵 대기 | 박사논문 설계 자동화 |
| `Sermon-Assistant-AgenticWorkflow-main/` | 🔵 대기 | 설교 보조 에이전트 |
| `AI_churchteam/` | 🔵 대기 | 교회 팀 AI 지원 |
| `harness-template/` | 📦 템플릿 | 에이전트 하네스 기본 구조 |
| `Wave Landing Page/` | 📦 보관 | WAVE AI 랜딩 페이지 |
| `연습_챌린지/` | 📦 학습 | 챌린지·연습 프로젝트 모음 |

---

## InvestScan 커맨드 (01.invest_test/)

```bash
cd Vibe-Practice/01.invest_test

# Done Gate 검증 (API 호출 없음)
python3 run_m05.py --dry-run        # M0.5 게이트 DG-01~08
python3 run_m1.py --dry-run         # M1 게이트 DG-09~16

# 파이프라인 실행
python3 -m investscan.weekly_orchestrator    # 전체 주간 파이프라인

# 보고서
python3 -m investscan.preview_report         # 미리보기
python3 -m investscan.approve_hitl           # HITL 승인
python3 -m investscan.export_report          # 최종 내보내기

# 단일 게이트 테스트
python3 run_m05.py --gate DG-04
```

**현재 브랜치:** `feat-0-mvp` — Phase 0 완료, `main` 머지 대기 중.
상세: `01.invest_test/CLAUDE.md`

---

## 산출물 경로

- 환경스캐닝: `output/환경스캐닝/{날짜}_{주제}/`
- 뉴스 크롤링: `output/뉴스크롤링/{날짜}/`
- InvestScan 보고서: `01.invest_test/output/reports/`

---

## 개별 프로젝트 진입점

각 프로젝트 폴더 내 `CLAUDE.md` 참조.
