# CLAUDE.md — _workflowhome/ (워크플로우 정본 저장소)

> **★모든 워크플로우 정본은 이 폴더에 둔다**(주인님 확정 2026-07-24 · 구 Vibe-Practice → STEP10 rename).
> 본부 작업축(개발본부·리서치본부 등)에서는 **심링크로 접근**한다 — 원본 이동 금지(gitlink 물리이동 금지 원칙).
> 산출물은 `output/WaveAI/{본부}/`(산출물 축)에 — 여기엔 워크플로우 코드·설계만.

## 워크플로우 목록 (2026-07-24 실측)

| 폴더 | 내용 | 소관(심링크 위치) |
|---|---|---|
| `AgenticWorkflow-main/` | 에이전트 설계 방법론·개발 규율 원본(전체 하네스 틀) — `AGENTS.md` | 전사 공용 |
| `EnvironmentScan-system-main-v4-main/` | 환경스캐닝(envscan) 5WF [gitlink] | 리서치본부 |
| `GlobalNews-Crawling-AgenticWorkflow/` | 뉴스크롤링 [gitlink] | 리서치본부(리서치2팀) |
| `Dissertation-Simulator-AgenticWorkflow-main/` | 박사논문 시뮬레이터 [gitlink] | 리서치본부(관리)·결과물=`output/개인/` |
| `Sermon-Assistant-AgenticWorkflow-main/` | 설교 어시스턴트 [gitlink] | 목회사역본부 |
| `Wave Landing Page/` | 랜딩 페이지 [gitlink] | 개발본부 |
| `Agent-Reach/` | agent-reach 스킬 소스 repo [gitlink·외부] — 스킬 실체는 `~/.claude/skills/agent-reach`(전역) | 개발본부 |
| `AgentWorkFlow-Lite/` · `harness_framework-main/` · `harness-landing/` · `harness-template/` | 하네스 프레임워크·템플릿 | 개발본부 |
| `SaaS-AgenticWorkflow-main/` | SaaS 워크플로우 | 개발본부 |
| `notebooklm-mcp-main/` | NotebookLM MCP 소스 | 리서치본부 |
| `AI_churchteam_archived_20260625/` | (아카이브 — 현행 ai_churchteam은 `목회사역본부/AI_churchteam`) | 이력 |
| `*.zip` | 백업 아카이브(원본 zip) | 이력 |

## 규율
1. **신규 워크플로우 = 여기에 생성**하고, 소관 본부 작업축에 상대경로 심링크를 건다.
2. **gitlink(외부 repo)는 물리이동 금지** — 심링크 접근만(원칙G).
3. 각 워크플로우 내부 규율은 각자의 `CLAUDE.md`/`AGENTS.md`가 정본(예: envscan·weekly 파이프라인 내부 불가침).
4. 구 경로 `Vibe-Practice/`는 소멸 — 참조 발견 시 이 폴더로 교정.
