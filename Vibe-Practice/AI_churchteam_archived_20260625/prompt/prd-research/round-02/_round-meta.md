# Round-02 메타데이터

## 기본 정보
- **조사 차수**: 2차
- **날짜**: 2026-04-29
- **조사 축**: 기술·이론 축 (Technology & Theory Axis)
- **가정 축**: 해당 없음 (이번 차수는 가정 분기 대신 5개 Teammate × 2 Branch 병렬 탐색)
- **조사 축 선택 이유**: 1차 조사(일반 가정 축)에서 "로컬 실행 가능성 + 신학 필터 구현 방식"이 PRD를 크게 가르는 변수로 식별됨. 이를 기술·이론 근거로 뒷받침하기 위해 2차에서 전문화 조사 수행.
- **참조 지침**: Technology_Development_DeepDive_PRD_Teammate_Executable.md

## 원본 질문 (사용자 지시)
- 로컬 실행 불변 전제 하에 기술·이론 축 심층조사 수행
- 5개 Teammate × 2 Branch (10개 Branch 병렬 탐색)
- 조사 폭: 에이전트 오케스트레이션 이론 / 로컬 LLM·추론 스택 / 도구 호출 패러다임 /
          플래닝·리플렉션 알고리즘 / 메모리·상태 관리 / 자동화 트리거·스케줄링 /
          샌드박싱·권한 모델 / 실패 복구·관찰 가능성 / 평가·벤치마킹 방법론
- 최종 산출물: 기술·이론 축 PRD 방향 조언 (PRD 본문 아님)

## 입력 문서
- `prompt/ai_pastoral_prompts/churchTeamPRD.md`
- `prompt/ai_pastoral_prompts/ORCHESTRATOR_LOGIC.md`
- `prompt/ai_pastoral_prompts/RULES.md`
- `prompt/prd-research/round-01/cross-analysis/prd-direction-advice.md` (1차 결과 참조)
- `prompt/Technology_Development_DeepDive_PRD_Teammate_Executable.md`

## Teammate 구성 (Round-02 전용)

| ID | 이름 | 담당 축 | Branch |
|----|------|---------|--------|
| t1 | Platform Capability Researcher | Claude Code 플랫폼 역량·한계 | 1.1 최대 활용 / 1.2 한계 인식 |
| t2 | Configuration Architect | 설정 아키텍처 (CLAUDE.md·Hooks) | 2.1 단순 설정 / 2.2 정밀 설정 |
| t3 | Orchestration Engineer | 오케스트레이션 구조 | 3.1 경량 / 3.2 고도 |
| t4 | Integration Specialist | 연동 전략 (MCP·CLI·외부) | 4.1 최소 연동 / 4.2 적극 연동 |
| t5 | Theory Foundation Expert | 에이전틱 이론 + 자동화 원칙 | 5.1 최신 이론 / 5.2 검증된 원칙 |

## 산출물 목록

| 파일 | 내용 |
|------|------|
| t1-platform-capability/raw.md | Platform Capability 전체 조사 원본 (Branch 1.1 + 1.2) |
| t1-platform-capability/summary.md | t1 핵심 발견 요약 |
| t2-configuration-architect/raw.md | Configuration Architect 전체 조사 원본 (Branch 2.1 + 2.2) |
| t2-configuration-architect/summary.md | t2 핵심 발견 요약 |
| t3-orchestration-engineer/raw.md | Orchestration Engineer 전체 조사 원본 (Branch 3.1 + 3.2) |
| t3-orchestration-engineer/summary.md | t3 핵심 발견 요약 |
| t4-integration-specialist/raw.md | Integration Specialist 전체 조사 원본 (Branch 4.1 + 4.2) |
| t4-integration-specialist/summary.md | t4 핵심 발견 요약 |
| t5-theory-foundation/raw.md | Theory Foundation Expert 전체 조사 원본 (Branch 5.1 + 5.2) |
| t5-theory-foundation/summary.md | t5 핵심 발견 요약 |
| cross-analysis/intersections.md | 전 Teammate 동의 항목 |
| cross-analysis/conflicts.md | 최대 불일치 항목 |
| cross-analysis/parking-lot.md | 파킹 로트 통합 |
| cross-analysis/prd-direction-advice.md | PRD 방향 조언 (이번 차수 최종 산출) |

## 로컬 실행 불변 위반 여부
- LOCAL-BLOCKED 항목: **없음**
- LOCAL-PARTIAL 항목: NotebookLM MCP (Google 계정 의존) / Telegram Bot (Bot API 의존) / 원어 성경 DB 일부 옵션
- 클라우드·SaaS 전제 항목: **없음** (외부 MCP는 로컬 Claude Code에서 호출되는 구조이므로 로컬 실행 불변 유지)
