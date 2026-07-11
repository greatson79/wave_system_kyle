# T3 Orchestration Engineer — 핵심 발견 요약 (Round-02)

## 메타데이터
- 조사 차수: 2 / Teammate: t3 / 조사 축: 기술·이론 축 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
Phase 1은 경량 순차 오케스트레이션으로 시작해 안정성을 확보하고, Phase 2에서 3개 파이프라인 병렬화로 전환하는 단계적 접근이 이 시스템에서 유일하게 검증 가능한 경로다.

## 필수 구성요소 Top 3
1. state.yaml 상태 머신 — 체크포인트 기반 재시작
2. 파이프라인별 독립 Task (Phase 2) — 실패 격리
3. output/{주차}/status.yaml — Orchestrator 전체 상태 가시성

## 로컬 실행 태그 요약
| 항목 | 태그 |
|-----|-----|
| 경량 순차 오케스트레이션 | LOCAL-OK |
| Task tool 병렬 실행 | LOCAL-OK (rate limit 모니터링 필요) |
| 세션 분할 체크포인트 | LOCAL-OK |

## 반증 사례
- SaaS-AgenticWorkflow: 3개 병렬 Task → rate limit 초과로 2개 중단

## PRD에 전달할 것
- Phase 1과 Phase 2의 오케스트레이션 수준을 Phase 구조 표에 병기
- "병렬 Task 즉시 도입 금지" → MVP 제약으로 명시
