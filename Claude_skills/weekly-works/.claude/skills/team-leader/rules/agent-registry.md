# Agent Registry

Team Leader가 소환할 수 있는 모든 에이전트의 단일 등록부.
새 프로젝트의 에이전트를 추가하려면 해당 섹션에 행을 추가하면 된다.

---

## 등록 규칙

- `source`: SKILL 또는 에이전트 정의 파일의 경로 (weekly-works/ 기준 상대경로, 외부는 절대경로)
- `type`: auto (백그라운드 위임 가능) | interactive (메인 대화 필수) | research (연구 보조)
- `input`: 필요한 입력 데이터
- `output`: 생성하는 산출물 경로 패턴

---

## Weekly Works (주간 콘텐츠)

| ID | 이름 | type | source | input | output |
|----|------|------|--------|-------|--------|
| WK-A | 설교 | interactive | `.claude/skills/sermon/sermon_SKILL.md` | scripture, audience | `설교/*.md` |
| WK-B | 매일묵상 | auto | `.claude/skills/weekly-devotion/SKILL.md` | week#, devotion-data.json | `매일묵상/html-original/` |
| WK-C | 기도카드 | auto | `.claude/skills/prayer-doc/SKILL.md` | month, week#, CSV | `수요기도회/` |
| WK-D | 소그룹나눔지 | auto | `.claude/skills/small-group/small-group_SKILL.md` | sermon-context.md | `소그룹나눔지/` |
| WK-E0 | 디자인스카우트 | auto | `.claude/skills/design-template-scout/SKILL.md` | sermon-context.md | `카드뉴스/design-guide.md` |
| WK-E | 카드뉴스 | auto | `.claude/skills/sns-cardnews/sns-cardnews_SKILL.md` | sermon-context.md, design-brief.md | `카드뉴스/` |
| WK-F | 이미지삽입 | auto | `.claude/skills/insert-images/SKILL.md` | week#, image paths | `매일묵상/html-with-images/` |
| WK-G | 디자인에이전트 | auto | `.claude/skills/sns-cardnews/rules/design-agent.md` | sermon-context.md, brand-guide.md | `카드뉴스/design-brief.md` |
| WK-H | 주보 | auto | `.claude/skills/bulletin/bulletin_SKILL.md` | sermon-context.md, service-plan-2026.csv, devotion-data.json, 광고(사용자입력) | `주보/주보앞면.html+png+pdf`, `주보/주보뒷면.html+png+pdf` |

---

## Sermon-Assistant (심층 연구)

> 소스 기본 경로: `/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/Sermon-Assistant-AgenticWorkflow-main/.claude/agents/`

| ID | 이름 | type | source (기본 경로 이하) | input | output |
|----|------|------|------------------------|-------|--------|
| SA-1 | 원어분석가 | research | `original-text-analyst.md` | scripture | `research/01-원어분석-original-text.md` |
| SA-2 | 사본비교가 | research | `manuscript-comparator.md` | scripture | `research/02-번역사본비교.md` |
| SA-3 | 핵심단어전문가 | research | `keyword-expert.md` | scripture | `research/03-핵심단어연구.md` |
| SA-4 | 성경지리전문가 | research | `biblical-geography-expert.md` | scripture | `research/04-성경지리.md` |
| SA-5 | 역사문화전문가 | research | `historical-cultural-expert.md` | scripture | `research/05-역사문화배경.md` |
| SA-6 | 역사적맥락분석가 | research | `historical-context-analyst.md` | scripture | `research/06-역사적맥락.md` |
| SA-7 | 신학분석가 | research | `theological-analyst.md` | scripture | `research/07-신학분석.md` |
| SA-8 | 문학분석가 | research | `literary-analyst.md` | scripture | `research/08-문학분석.md` |
| SA-9 | 구조분석가 | research | `structure-analyst.md` | scripture | `research/09-구조분석.md` |
| SA-10 | 평행본문분석가 | research | `parallel-passage-analyst.md` | scripture | `research/10-평행본문.md` |
| SA-11 | 수사학분석가 | research | `rhetorical-analyst.md` | scripture + SA-8,9,10 결과 | `research/11-수사학분석.md` |

### 확장 에이전트 (3~4단계 협업, 필요 시 on-demand 소환)

| ID | 이름 | type | source (기본 경로 이하) | 협업 시점 | output |
|----|------|------|------------------------|----------|--------|
| SA-12 | 메시지합성가 | auto | `message-synthesizer.md` | 2-4 종합통찰 이후 CMT/HP 도출 지원 | `research/core-message.md` |
| SA-13 | 아웃라인설계가 | auto | `outline-architect.md` | 4단계 구조설계 진입 시 | `research/sermon-outline.md` |
| SA-14 | 연구합성가 | auto | `research-synthesizer.md` | 전체 연구 수신 후 압축 요약 | `research/research-synthesis.md` |

### 연구 에이전트 ↔ /설교 단계 매핑

> **선택적 실행**: 본문 장르·목사 요청에 따라 일부만 소환한다. `research-bridge.md` § 지능적 에이전트 선택 참조.

| /설교 하위단계 | 기본 에이전트 세트 | 실행 방식 |
|---------------|-----------------|----------|
| 2-1 원어분석 | SA-1, SA-2, SA-3 | 3개 병렬 (background) |
| 2-2 배경분석 | SA-4, SA-5, SA-6 | 3개 병렬 (background) |
| 2-3 우상분석 | SA-7, SA-8 | 2개 병렬 (background) |
| 2-4 종합통찰 | SA-9, SA-10 병렬 → SA-11 순차 | SA-11은 SA-8,9,10 의존 |
| 2-4 이후 (선택) | SA-12 메시지합성가 | CMT/HP 정리 필요 시 on-demand |
| 4단계 구조설계 (선택) | SA-13 아웃라인설계가 | 목사 요청 시 on-demand |
| 전체 연구 후 (선택) | SA-14 연구합성가 | 결과 압축 필요 시 on-demand |

---

## Wave-AI (범용)

> 소스 기본 경로: `Claude skills/Wave-AI/agents/`

| ID | 이름 | type | source (기본 경로 이하) | input | output |
|----|------|------|------------------------|-------|--------|
| WV-O | 오케스트레이터 | interactive | `orchestrator/orchestrator_SKILL.md` | topic | 종합 조율 |
| WV-R | 리서치 | auto | `research/research_SKILL.md` | topic, depth | 리서치 보고서 |
| WV-C | 콘텐츠 | auto | `content-creator/content-creator_SKILL.md` | topic, format | 콘텐츠 파일 |
| WV-K | 지식설계 | auto | `knowledge-architect/knowledge_architect_SKILL.md` | info, graph | 지식베이스 |

---

## 확장 방법

새 프로젝트의 에이전트를 추가하려면:

1. 이 파일에 새 섹션(## 프로젝트명) 추가
2. `source` 경로에 에이전트 정의 파일(.md) 경로 기재
3. `type` (auto / interactive / research) 지정
4. Team Leader가 자동으로 해당 에이전트를 소환 가능
