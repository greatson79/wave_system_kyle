# Round-03 Cross-Analysis — PRD 방향 조언 (코딩·구현 축)

- **차수/축**: 3차 / 코딩·구현
- **생성**: 2026-04-29
- **주의**: 본 문서는 *조언* 이며 PRD.md 본문이 아니다. 각 권고에 LOCAL-* 태그가 부착됨.

## 합의 5축 (이번 차수의 결론)

1. **Workflow Script** — 상위 절차적 + 노드 내부 선언적 (`[LOCAL-OK]`).
2. **Orchestration** — Centralized + readonly fanout. SOT 단일 쓰기를 PreToolUse hook 으로 코드 강제 (`[LOCAL-OK]`).
3. **Skills & Hooks** — 레이어 분리: `val/*` 범용 (부모 11 validator) + `skill/*` churchTeam 특화. 신학 필터·SOT-pin checker 는 skill/sermon (`[LOCAL-OK]`).
4. **Verification** — L0 전면 + L1 형식 전면 + L2 핀포인트(설교 4.5, 신학 정확성, 번역, SOT-pin) (`[LOCAL-OK]`).
5. **State & Recovery** — File-state(`_state.json` 진실 / status.md 파생) + 얇은 phase enum guard (`[LOCAL-OK]`).

## PRD 섹션별 반영 가이드

### §Goals / Non-Goals
- Non-goals 명문화: 클라우드 전용 SDK·원격 워크플로우 엔진·서버형 큐(Redis/Celery)·외부 DB·다중 사용자 동시 편집(Phase 2 까지). 모두 LOCAL 전제 보존을 위함.

### §System Architecture
- 3 레이어 분리 다이어그램: Workflow DAG / Orchestration / State & Validation.
- 각 노드 4-tuple 표기: 입력 SOT · 출력 경로 · 검증자 · 재시도 예산.

### §Workflow Specification
- workflow.md 포맷 스키마(부록): `id, phase, agent, skill, inputs[], outputs[], validators[], retry_budget, depends_on, exit_criteria`.
- 4.5 단계 = phase enum hard gate. 잠금 후 sermon-context.md immutable.
- D(소그룹)·E(카드뉴스) 병렬을 DAG 구조로 강제 (`depends_on: [sermon-4_5]` 동일).

### §Agents & Skills Catalog
- agent-registry.md 의 의무 필드: `type=interactive|auto`, `writes={paths}`, `reads={paths}`, `mcp_required`, `local_tag`.
- 신학·SOT 검증을 별도 validator agent 로 분리 (이중 책임 금지).

### §Quality Gates
- L0/L1/L2 매트릭스 (어떤 노드에 어떤 게이트). SOT-pin checker 는 *모든* 설교 노드에 의무.

### §State & Recovery
- `_state.json` 스키마 + status.md 마크다운 표 페어. 원자 쓰기 규칙: `_state.json.tmp` → fsync+rename → status.md 재생성 → git add.
- PreCompact/SessionEnd 와의 상호작용 명시. 진실 = `_state.json`.

### §Local Constraint Compliance
- 외부 의존 표:
  - Telegram MCP `[LOCAL-OK]` (단 인증 경계 미정의 — Open Question #1)
  - NotebookLM MCP `[LOCAL-PARTIAL]` (인증 갱신 실패 시 차단 정책 미결 — Open Question #2)
  - Anthropic API (Claude Code 내부) `[LOCAL-OK]`
  - Gamma/Canva MCP `[LOCAL-PARTIAL]` (출력 단계만, 입력 데이터 송신 없음)
  - LOCAL-BLOCKED: **없음**

### §Risks & Open Questions
- parking-lot.md 카테고리 A 의 7개 항목을 그대로 박는다.

### §Phased Delivery
- **Phase 0 (Rapid-Prototype, 1주)**: 합의 5축 중 *workflow DAG + Centralized + L0/L1 + file-state*. L2 와 SOT-pin 은 sermon 만.
- **Phase 1 (Balanced, +2주)**: L2 핀포인트 전면, agent-registry 의무 필드 도입.
- **Phase 2 (Hardening)**: PreCompact 일관성, 비결정 산출 회귀 검출, 다중 사용자 시나리오.
- Full-Defensive 승격은 운영 데이터로 정당화될 때만.

### §What PRD Must NOT Do
- skill 내부 프롬프트 전문 박지 말 것 (버전 폭주). PRD 는 *경로·책임 경계* 까지만.
- SDK 이름 못박지 말 것. 부모 게놈(skills/hooks/commands) 호환만 요구.

## 다음 단계 진입 조건 (synthesis)

- round-01 + round-02 + round-03 의 `cross-analysis/prd-direction-advice.md` 3종 통합.
- Open Questions 7개 + 미해결 충돌 U1/U2 를 `synthesis/open-questions.md` 에 보존.
- PRD 본문 작성은 그 후 별도 승인.
