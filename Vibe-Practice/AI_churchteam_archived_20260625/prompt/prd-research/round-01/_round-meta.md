# Round-01 메타데이터

## 기본 정보
- **조사 차수**: 1차
- **날짜**: 2026-04-29
- **가정 축**: Claude Code 단독 완결 vs 외부 도구(MCP·스크립트) 연동 전제
- **가정 축 선택 이유**: 12개 에이전트의 실행 가능성과 신학 필터 구현 방식이 PRD 방향을 가장 크게 가르는 변수이기 때문

## 원본 질문 (사용자 지시)
- 로컬 실행 환경 전제
- teammate 심층조사 수행 → PRD.md 제작 방향 조언 산출
- 조사 깊이: 구조·선택지·트레이드오프 층위까지
- 조사 폭: 로컬 실행 아키텍처 / 에이전트 오케스트레이션 / 자동 트리거 / 로컬 LLM·외부 API 선택지 / 권한·보안 / 실패 복구 / 관찰 가능성

## 입력 문서
- `prompt/ai_pastoral_prompts/PRD.md`
- `prompt/ai_pastoral_prompts/WORKFLOW.md`
- `prompt/ai_pastoral_prompts/RULES.md`
- `prompt/ai_pastoral_prompts/SCHEMA.md`
- `prompt/ai_pastoral_prompts/ORCHESTRATOR_LOGIC.md`
- `prompt/ai_pastoral_prompts/AGENT_FLOW_MAP.md`
- `prompt/ai_pastoral_prompts/AGENT_PROMPTS_ADVANCED.md`
- `prompt/prd_teammate_executable.md` (teammate 실행 지침)

## 산출물 목록
| 파일 | 내용 |
|------|------|
| t1-workflow-architect/raw.md | Workflow Architect 전체 조사 원본 |
| t1-workflow-architect/summary.md | t1 핵심 발견 요약 |
| t2-scenario-explorer/raw.md | Scenario Explorer 전체 조사 원본 |
| t2-scenario-explorer/summary.md | t2 핵심 발견 요약 |
| t3-operator-analyst/raw.md | Operator Analyst 전체 조사 원본 |
| t3-operator-analyst/summary.md | t3 핵심 발견 요약 |
| t4-sustainability-strategist/raw.md | Sustainability Strategist 전체 조사 원본 |
| t4-sustainability-strategist/summary.md | t4 핵심 발견 요약 |
| cross-analysis/intersections.md | 전 teammate 동의 항목 |
| cross-analysis/conflicts.md | 최대 불일치 항목 |
| cross-analysis/parking-lot.md | 파킹 로트 통합 |
| cross-analysis/prd-direction-advice.md | PRD 방향 조언 (이번 turn 최종 산출) |

## 로컬 실행 불변 위반 여부
- 이번 조사 결과 내 클라우드·SaaS 전제 포함 항목: **없음**
- 외부 의존성 언급 항목: 원어 성경 DB (로컬 설치 전제로 조사됨) — 위반 아님
