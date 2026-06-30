# 상주 노드 수명주기 (이벤트 구동형 — 적대검증 H2 반영)

**Charter-level 상주**(전 부서 헌장 상시) ≠ **pane-level 상주**(물리 프로세스). CSO = 중앙 메시지 큐·라우터.

- **L0 활성(Active)**: 작업 수행 중. 병렬은 sub-agent fan-out(pane 추가 금지). 백그라운드 서버 0.
- **L1 대기(Idle, 단기)**: 작업 직후 짧은 유휴. 후속 작업 즉응용 잠깐 유지, 토큰 0.
- **L2 동면(Hibernate, 기본 휴지)**: 유휴 임계 초과 시 CSO가 핸드오프 저장 → pane 종료(메모리 회수).

## 전이 규칙
- L0→L1: 작업 완료·큐 빔.
- L1→L2: CSO가 유휴 임계 초과 감지 시 핸드오프 저장 후 pane 종료(기본 휴지 상태).
- L2→L0: 신규 작업 라우팅 시 CSO가 재기동 + 헌장·핸드오프 복원.
- 희소 부서는 평소 L2, 활성 부서만 L1 단기. 전 부서 L1/L2 = 감시 루프 중단([[feedback_monitoring_only_when_working]]).

## CSO watchdog 책무
- 14노드(정의상)·현행 활성 pane은 `SESSION_STATE.md` 참조 — 메모리·load·컨텍스트 60% 상시 감시.
- 컨텍스트 60% → 관리형 /clear. 장기 idle → L2 동면.
- 메모리·동시 토큰예산 임계 → 회장 에스컬레이션.
- "완전 상주"는 charter/identity 수준(전 부서 헌장 상주). 물리 pane은 수요 기반(활성 L1, 희소 L2). 14 pane(정의상) 동시 강제 기동 금지(현행 활성 pane은 `SESSION_STATE.md` 참조).
