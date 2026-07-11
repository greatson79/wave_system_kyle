# Round-03 메타데이터

## 기본 정보
- **조사 차수**: 3차
- **날짜**: 2026-04-29
- **조사 축**: 코딩·구현 기술 축 (Coding & Implementation Axis)
- **1·2차와의 관계**:
  - 1차(일반 축): Claude Code 단독 vs 외부 도구 연동 등 운영·시나리오 가정 분기
  - 2차(기술·이론 축): Platform 역량·설정·오케스트레이션 이론·연동·이론 기반
  - 3차(코딩·구현 축): 위의 결론을 **실제 코드 구조 수준**으로 내려, workflow.md 표현·오케스트레이션 코드·skill/hook·검증 로직·상태 관리의 구현 패턴을 비교
- **참조 지침**: `prompt/Coding_Implementation_DeepDive_PRD_Teammate_Executable.md`
- **경계 메모**: 2차 t3 Orchestration Engineer 와 3차 t2 Agent Orchestration Coder 는 *이론 vs 코드 구조* 로 층위가 다르며, 본 차수에서 코드 레벨만 다룬다 (`cross-analysis/conflicts.md` §경계 중복 참조).

## 원본 질문 (사용자 지시)
- "코딩 및 구현 기술" 축 심층조사 수행 (5 Teammate × 2 Branch = 10 Branch + 4 토론 + 3 시나리오)
- 모든 선택지에 LOCAL-OK / LOCAL-PARTIAL / LOCAL-BLOCKED 태그와 근거 명시
- 산출은 "코딩·구현 축 PRD 방향 조언"; PRD.md 본문 작성 금지
- 깊이: 표면 프레임워크 나열 금지. 의사 코드/구조 예시·전제·트레이드오프·한계·반증까지

## 입력 문서
- `prompt/ai_pastoral_prompts/churchTeamPRD.md`
- `prompt/Coding_Implementation_DeepDive_PRD_Teammate_Executable.md`
- `prompt/prd-research/round-01/cross-analysis/prd-direction-advice.md`
- `prompt/prd-research/round-02/cross-analysis/prd-direction-advice.md`
- 부모 게놈 참조: `Claude_skills/weekly-works/.claude/skills/team-leader/rules/{agent-registry,quality-gates,workflow-dag}.md`,
  `AI_churhteam/.claude/hooks/scripts/validate_*.py` (11종)

## Teammate 구성 (Round-03 전용)

| ID | 이름 | 담당 축 | Branch |
|----|------|---------|--------|
| t1 | Workflow Script Architect | workflow.md 표현 방식 | 1.1 선언적 / 1.2 절차적 |
| t2 | Agent Orchestration Coder | orchestrator/sub-agent/swarm 코드 구조 | 2.1 중앙 집중 / 2.2 분산 |
| t3 | Skills & Hooks Developer | skill·hook·command 라이브러리 설계 | 3.1 범용 / 3.2 워크플로우 특화 |
| t4 | Verification & Quality Coder | task verification + 회귀 검증 | 4.1 엄격 / 4.2 선택적 |
| t5 | State & Recovery Coder | 상태·체크포인트·재개 | 5.1 파일 기반 / 5.2 구조 상태머신 |

> 식별자 정책: `_index.md` 의 "Teammate 식별자 고정" 표는 round-01 의 4축 구성 기준이다. round-02 가 이미 5팀(축 변경) 으로 차수별 재구성을 선례로 남겼으므로, round-03 도 코딩 5축에 맞춰 t1~t5 를 재정의했다. 임의 수정이 아니라 기존 선례 준수다. (`cross-analysis/conflicts.md` §식별자 정책 참조)

## 산출물 목록

| 파일 | 내용 |
|------|------|
| t1-workflow-script-architect/raw.md | Branch 1.1+1.2 원본 |
| t1-workflow-script-architect/summary.md | t1 핵심 발견 요약 |
| t2-agent-orchestration-coder/raw.md | Branch 2.1+2.2 원본 |
| t2-agent-orchestration-coder/summary.md | t2 핵심 발견 요약 |
| t3-skills-hooks-developer/raw.md | Branch 3.1+3.2 원본 |
| t3-skills-hooks-developer/summary.md | t3 핵심 발견 요약 |
| t4-verification-quality-coder/raw.md | Branch 4.1+4.2 원본 |
| t4-verification-quality-coder/summary.md | t4 핵심 발견 요약 |
| t5-state-recovery-coder/raw.md | Branch 5.1+5.2 원본 |
| t5-state-recovery-coder/summary.md | t5 핵심 발견 요약 |
| cross-analysis/intersections.md | 5팀 합의 항목 |
| cross-analysis/conflicts.md | 불일치 + 차수간 경계 |
| cross-analysis/parking-lot.md | 파킹 로트 + 미해결 7개 |
| cross-analysis/prd-direction-advice.md | 코딩·구현 축 PRD 방향 조언 |

## 로컬 실행 불변 검증
- **LOCAL-BLOCKED 항목**: **없음**.
- **LOCAL-PARTIAL 항목**:
  - 분산 오케스트레이션 (B-2.2): 파일 락이 OS 수준이며 분산 트랜잭션 없음 → race 조건이 부분 한계
  - NotebookLM MCP 인증 갱신 실패 시 워크플로우 차단 (외부 발견, 2차에서도 PARTIAL)
- **클라우드·SaaS 전제 항목**: 없음. 모든 후보가 사용자 단일 로컬 머신 내 Claude Code + 로컬 파일 시스템 + MCP 호출만 사용.
- **태그 누락 검증**: 본 차수 raw/summary 의 모든 패턴 항목에 `[LOCAL-*]` 태그가 1회 이상 부착됨. cross-analysis 도 권고 패턴별로 재태깅.

## 자기 점검 결과 (3층위)
- 1층위(사실): 17개 가상 Branch 중 코딩·구현 범위 일치, 외부 축 침범 없음.
- 2층위(구조): 가장 약한 지점은 4.5단계 → D·E 병렬 fan-out 시 sermon-context.md read-modify-write race. PRD 명문화 필요.
- 3층위(누락): 7개 미해결 — `cross-analysis/parking-lot.md` 에 카테고리화하여 보존.
