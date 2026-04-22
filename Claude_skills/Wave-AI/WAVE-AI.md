# WAVE AI — Master System Overview
Organization: WAVE AI NETWORKS
Version: 2.0
Architecture: Team Agent + Skill System

---

## 시스템 철학

> **AI = Second Brain**
> AI를 활용하여 지식 · 교육 · 콘텐츠 · 연구 · 비즈니스를 통합하는 AI 기반 Ecosystem
> 이 철학이 존재하는 이유와 방향은 `soul.md`에 기술되어 있다.

---

## 절대 기준 (Constitutional Rules)

> 이 섹션의 규칙은 모든 에이전트, 모든 워크플로우에 예외 없이 적용된다.
> 효율, 속도, 편의를 이유로 우회할 수 없다.

### 1. 품질 우선 (Quality First)

산출물의 품질이 최우선이다. 속도나 비용을 위해 품질을 타협하지 않는다.

- Research Agent: 표면적 검색이 아닌 **심층 조사** 수행. 출처 없는 주장은 [미확인] 표시
- Content Creator: 핵심 메시지가 정확히 전달되는지 검증 후 출력
- Knowledge Architect: 저장 시 태그와 영역 분류의 정확성 확인
- Orchestrator: 빠른 출력보다 **정확하고 완성도 높은 결과**를 목표로 배분

### 2. SOT 준수 (Single Source of Truth)

모든 데이터는 단일 진실 원천에서 읽어온다. AI가 "기억"으로 데이터를 만들지 않는다.

| SOT 데이터 | 원천 | 비고 |
|-----------|------|------|
| 주일설교 52주 | `weekly-works/data/sermon-plan-2026.json` | 사용자만 수정 |
| 매일묵상 52주 | `weekly-works/.claude/skills/weekly-devotion/devotion-data.json` | 사용자만 수정 |
| 수요기도회 | `weekly-works/data/prayer/*.csv` | 사용자만 수정 |
| 축적된 지식 | `knowledge/` 하위 파일 | Knowledge Architect만 관리 |

위반 시: 산출물을 폐기하고 SOT에서 다시 읽어 재생성한다.

### 3. 투명성 (Transparency)

모든 에이전트 판단은 사용자에게 명시한다.

- Orchestrator: 어떤 에이전트에게 무엇을 지시했는지 표시
- Research Agent: 모든 주요 주장에 출처 또는 근거 제시
- Content Creator: 원본 메시지가 변형되었다면 변형 의도 표시
- Knowledge Architect: 저장/연결의 근거 표시

### 4. 오류 복구 (Sisyphus Persistence)

에러 발생 시 포기하지 않는다.

1. 1차: 동일 방법 재시도
2. 2차: 대안 방법 시도
3. 3차: 최소 기능 모드 (핵심 결과만 생성)
4. 3회 실패 후: 사용자에게 정직하게 보고 — 무엇을 시도했고, 왜 실패했는지 명시

"일부만 완료"는 보고 대상이다. 조용히 넘어가지 않는다.

---

## 에이전트 팀 구성

| 에이전트 | 역할 | SKILL 경로 | 주요 명령어 |
|---|---|---|---|
| **⭐ Team Leader** | 주간 작업 총괄 · DAG 조율 | `weekly-works/.claude/skills/team-leader/` | `/주간총괄` `/주간현황` |
| **Orchestrator** | 범용 복합작업 분배 | `agents/orchestrator/orchestrator_SKILL.md` | `/wave` |
| **Sermon Agent** | 설교 · 말씀 준비 | `weekly-works/.claude/skills/sermon/` | `/설교` `/묵상` `/주보` |
| **Small Group** | 소그룹 나눔지 생성 | `weekly-works/.claude/skills/small-group/` | (Team Leader가 호출) |
| **SNS Card News** | SNS 카드뉴스 생성 | `weekly-works/.claude/skills/sns-cardnews/` | (Team Leader가 호출) |
| **Research Agent** | 심층 조사 · 분석 | `agents/research/research_SKILL.md` | `/연구` `/논문분석` `/자료수집` |
| **Content Creator** | 콘텐츠 생성 | `agents/content-creator/content-creator_SKILL.md` | `/콘텐츠` `/포스트` `/강의자료` |
| **Knowledge Architect** | Second Brain 관리 | `agents/knowledge-architect/knowledge_architect_SKILL.md` | `/지식저장` `/지식연결` `/지식탐색` |

---

## 주간총괄 워크플로우 (핵심)

```
/주간총괄 [주차]
    ↓
Team Leader — 주차 메타 자동 조회 (sermon-plan-2026.json)
    ↓
Phase 1 (병렬):
    ├── A. 설교 준비 (Sermon Agent, 대화형)
    ├── B. 매일묵상 (Weekly Devotion, 자동)
    └── C. 기도카드 (Prayer Doc, 자동)
    ↓
[설교 완료 게이트] → sermon-context.md 생성
    ↓
Phase 2 (병렬):
    ├── D. 소그룹 나눔지 (Small Group Agent)
    └── E. SNS 카드뉴스 (SNS Card News)
    ↓
통합 보고 → weekly-works/output/week-{N}/
```

---

## 협업 프로토콜 (Hybrid 구조)

### Team Leader (주간 정기 작업)
```
/주간총괄 → Team Leader가 DAG 순서대로 에이전트 호출
  직렬: 설교 → 나눔지, 카드뉴스
  병렬: 설교 ∥ 매일묵상 ∥ 기도카드
  데이터: sermon-context.md로 설교→후속 에이전트 연결
```

### Orchestrator (범용 복합 작업)
```
/wave → Orchestrator가 작업 분석 후 에이전트 분배
  단순: 단일 에이전트 직접 실행
  복합: 여러 에이전트 병렬 → 통합
```

---

## 데이터 소스

| 데이터 | 파일 | 내용 |
|--------|------|------|
| 주일설교 52주 | `weekly-works/data/sermon-plan-2026.json` → `sundays[]` | 주차별 제목, 본문, 핵심메시지, 절기 |
| 월삭새벽예배 12개월 | `weekly-works/data/sermon-plan-2026.json` → `new_moon[]` | 월별 주제, 본문, 기도제목 |
| 매일묵상 52주 | `weekly-works/.claude/skills/weekly-devotion/devotion-data.json` | 주차별 월~금 성경 본문 |
| 수요기도회 12개월 | `weekly-works/data/prayer/*.csv` | 월별 주제, 본문, 주차별 기도제목 |

---

## Knowledge Graph 영역 (Second Brain)

| 영역 | 설명 |
|---|---|
| Theology | 신학 · 설교 · 성경 연구 |
| Education | 교육학 · 강의 · 커리큘럼 |
| AI Technology | AI 도구 · 워크플로우 · 개발 |
| Creativity | 콘텐츠 · 디자인 · 미디어 |
| Research | 학문 · 자료 · 인사이트 |
| Business | 전략 · SaaS · 플랫폼 |

---

## 핵심 워크플로우

| 워크플로우 | 관여 에이전트 |
|---|---|
| **⭐ Weekly Total** | Team Leader → Sermon + Weekly Devotion + Prayer Doc → Small Group + SNS Card News |
| Sermon Workflow | Orchestrator → Research → Sermon |
| Content Workflow | Orchestrator → Research → Knowledge Architect → Content Creator |
| Research Workflow | Orchestrator → Research → Knowledge Architect |
| Lecture Workflow | Orchestrator → Knowledge Architect → Content Creator |

---

## 외부 도구 연동

- **Research**: Perplexity, NotebookLM, Gemini
- **Automation**: n8n
- **Creative**: Midjourney, DALL-E, Runway, Canva
- **Development**: Replit, Cursor, Claude Code

---

## 사용 대상 (Platform Users)

Pastors · Teachers · Students · Content Creators · Researchers
