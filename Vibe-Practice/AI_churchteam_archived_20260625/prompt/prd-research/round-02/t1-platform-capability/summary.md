# T1 Platform Capability Researcher — 핵심 발견 요약 (Round-02)

## 메타데이터
- 조사 차수: 2 / Teammate: t1 / 조사 축: 기술·이론 축 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
Claude Code Max는 12 에이전트 목회 보조 시스템의 핵심 기능을 로컬 단독으로 구현할 수 있으나, 자동 트리거 불가와 컨텍스트 소진은 PRD에 구조적 제약으로 명시해야 한다.

## 필수 구성요소 Top 3
1. state.yaml SOT — 세션 간 상태 유지의 유일한 방법
2. 설교 파이프라인 단계별 세션 분할 — 컨텍스트 소진 우회
3. 2중 Theology Filter — 1차 프롬프트 + 2차 키워드 Hook

## 로컬 실행 태그 요약
| 항목 | 태그 |
|-----|-----|
| 설교·묵상·행정 파이프라인 | LOCAL-OK |
| Theology Filter (2중) | LOCAL-OK |
| 자동 트리거 (Claude Code 단독) | LOCAL-BLOCKED |
| cron 연동 자동 트리거 | LOCAL-OK (OS 기본 cron 활용) |

## 반증 사례
- SaaS-AgenticWorkflow 사례: 3개 병렬 Task 실행 시 rate limit 초과로 2개 중단 (RATELIMIT_FAILURE_ANALYSIS.md)
- Claude Code Max에서는 5배 한도로 완화되나 보증 없음

## PRD에 전달할 것
- "자동 트리거 불가" → 기술 전제 섹션에 명시
- "병렬 Task 수 상한 미명시" → Phase 2 이후 점진 도입 근거
