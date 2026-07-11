# T1 Workflow Architect — 핵심 발견 요약 (Round-01)

## 메타데이터
- 조사 차수: 1 / Teammate: t1 / 생성일: 2026-04-29

---

## 핵심 결론 (1문장)
Claude Code 에이전트 구조를 뼈대로, Theology Filter(Python Hook)와 원어 데이터(로컬 DB)만 외부 보강하는 혼합 구조가 품질과 운용성 사이 최적점이다.

## 필수 구성요소 Top 5
1. Orchestrator 에이전트 (`.claude/agents/orchestrator.md`) — 라우팅 전담
2. state.yaml — 단일 SOT, 에이전트 간 상태 공유
3. `.claude/agents/` 구조 — 12개 에이전트 파일 집중 관리
4. Theology Filter (Python Hook 권장) — 규칙 기반 신학 검증
5. 원어 성경 로컬 DB — Exegesis Agent 환각 방지

## 반드시 피해야 할 것
- 에이전트가 state.yaml을 직접 수정하는 구조 (SOT 충돌)
- 컨텍스트 격리 없이 모든 에이전트를 단일 세션에서 실행 (context 소진)
- Theology Filter를 LLM 판단에만 의존 (일관성 보장 불가)

## 미해결 / 후속 조사 필요
- 원어 성경 로컬 DB 옵션 비교 (BibleOL, OSIS XML, Unbound Bible)
- Python Hook 설치 시 비개발자 환경 지원 방법
