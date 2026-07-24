# Claude Skills — 디딤교회 자동화 프로젝트

이 폴더는 디딤교회의 주간 콘텐츠를 자동 생성하는 Claude Code 스킬 모음입니다.

## 프로젝트 구조

```
Claude skills/
├── CLAUDE.md               ← 이 파일
├── .claude/
│   ├── commands/
│   │   ├── 주간총괄.md     ← /주간총괄 → weekly-works 연결
│   │   ├── 주간현황.md     ← /주간현황 → weekly-works 연결
│   │   ├── 설교.md         ← /설교 → weekly-works 연결
│   │   ├── wave.md         ← /wave → Wave-AI Orchestrator
│   │   ├── 연구.md         ← /연구 → Wave-AI Research
│   │   ├── 지식저장.md     ← /지식저장 → Wave-AI Knowledge
│   │   └── 콘텐츠.md       ← /콘텐츠 → Wave-AI Content
│   ├── skills/research/    ← NLM 리서치 파이프라인
│   └── rules/
├── weekly-works/           ← ⭐ 주간 콘텐츠 통합 시스템
│   ├── CLAUDE.md           ← 상세 사용법
│   ├── .claude/skills/     ← 모든 주간 스킬 (7개)
│   ├── data/               ← 설교계획, 기도회 CSV
│   ├── src/                ← 에셋, 템플릿, 스크립트
│   └── output/             ← 주간 결과물
├── youth_life_plan/        ← ⭐ 청소년 인생계획 스킬 (9개 전문 에이전트)
│   ├── SKILL.md            ← 메인 진입점 (페르소나·라우팅·안전장치)
│   └── references/         ← 에이전트 11개 파일
│       ├── interview_mode.md          ← InterviewAgent (학년대 분기)
│       ├── calling_direction_mode.md  ← CallingSoningAgent (진로·소명)
│       ├── family_mode.md             ← FamilyAgent (부모·가족)
│       ├── peers_mode.md              ← PeersAgent (또래·학교)
│       ├── faith_life_mode.md         ← FaithLifeAgent (신앙·정체성)
│       ├── analysis_agent.md          ← AnalysisAgent (4개 도메인 통합)
│       ├── coaching_agent.md          ← CoachingAgent (코칭 플랜)
│       ├── retrospective_mode.md      ← RetrospectiveAgent (반기회고 10문)
│       ├── output_templates.md        ← YouthCardAgent + PastorPlanAgent
│       ├── calendar_mode.md           ← 학사일정·신앙 루틴 통합
│       └── retreat_mode.md            ← 수련회 45~60분 집중 모드
├── AI_churchteam/          ← ⭐ 디딤 백본 오케스트레이터 (부교역자팀 31인)
│   ├── CLAUDE.md           ← 진입점 (/팀 /팀-전략분析 /팀-연간계획 /팀-월간 /팀-분기)
│   ├── .claude/
│   │   ├── commands/       ← /팀 등 8개 커맨드
│   │   └── skills/
│   │       ├── weekly-works-bridge.md   ← weekly-works 브릿지 (★내부 불가침)
│   │       ├── church-admin-bridge.md   ← church-admin 브릿지
│   │       ├── theological-reasoning/   ← 개혁주의 신학 추론
│   │       └── theology_filter_dual/    ← 이중 신학 필터
│   ├── pastor/             ← 목회철학·연간계획·참고자료
│   └── reports/            ← 시대통찰·월간기획·정렬검증
└── Wave-AI/                ← WAVE AI 시스템 설계 문서
    ├── WAVE-AI.md
    └── agents/             ← 범용 에이전트 (orchestrator, research, content-creator, knowledge)
```

> ★통합 구조: AI_churchteam(백본) → weekly-works·church-admin 브릿지 호출. weekly-works 내부(sermon·research-bridge·team-leader) 절대 불가침.

## 핵심 사용법

### 주간 콘텐츠 (weekly-works/)
- `/주간총괄 [주차번호]` — 설교 + 매일묵상 + 기도카드 + 소그룹 나눔지 + 카드뉴스 한번에
- `/주간현황` — 진행 상태 대시보드
- `/설교 [본문]` — 설교 준비 5단계
- 상세: `weekly-works/CLAUDE.md` 참조

### 청소년 인생계획 (youth_life_plan/)

스킬 위치: `Edu본부/youth_life_plan/SKILL.md`

**사용 방법:** Claude Code에서 이 디렉토리를 열고 SKILL.md를 참조하면 자동 활성화.

| 명령어 | 기능 |
|--------|------|
| `/인터뷰` | 청소년 본인 또는 사역자 진입 — 학년대 분기 5문 인터뷰 |
| `/진로소명` | 진로·소명 탐색 (3축: 관심·재능·하나님 나라) |
| `/가족관계` | 부모·형제·가정 환경 설계 |
| `/또래관계` | 친구·학교·교회 관계 지도 (투자/소모/방어 분류) |
| `/나의삶` | 신앙·정체성·자기돌봄 루틴 |
| `/분석` | AnalysisAgent — 4개 도메인 통합 분석 |
| `/코칭` | CoachingAgent — 수치화 코칭 플랜 생성 |
| `/전체출력` | 청소년 결과 카드 + 사역자 코칭 플랜 이중 출력 |
| `/반기회고` | RetrospectiveAgent — "나는 잘 자라고 있는가" 10문 |
| `/수련회` | 45~60분 집중 플로우 (수련회 전용) |
| `/캘린더` | 학사일정·신앙 루틴 구글 캘린더 포맷 출력 |

**결과물 저장 경로:**
- 평상시: `output/youth-life-planner/{날짜}_{닉네임}/` (md · txt · pdf)
- 수련회: `output/youth-life-planner/retreat/{날짜}_{교회명}/`

**안전 장치:** 자살(1393) · 학교폭력(117) · 가정폭력(1391) · 이단 — 전역 자동 발동

---

### NLM 리서치
- `/research run <주제> --auto` — YouTube → NotebookLM → 리포트/팟캐스트/슬라이드
- 필수: `nlm login` (최초 1회)

---

## Weekly-Works 운영 상세

### 워크플로우 DAG

```
Phase 1-Auto (병렬):  매일묵상 15개 HTML  ∥  수요기도회 기도카드
Phase 1-Interactive:  설교 1~4단계 (심층 연구 에이전트 소환 가능)
                              ↓
                      4.5 제목확정 → sermon-context.md 갱신
                              ↓
Phase 2 (병렬):       소그룹 나눔지  ∥  SNS 카드뉴스
                              ↓
                          주간 보고서
```

### SOT 데이터 원천

| 데이터 | 파일 | 쓰기 권한 |
|--------|------|----------|
| 주일설교 52주 + 월삭 12개 | `weekly-works/data/sermon-plan-2026.json` | 사용자만 |
| 매일묵상 52주 | `weekly-works/.claude/skills/weekly-devotion/devotion-data.json` | 사용자만 |
| 수요기도회 | `weekly-works/data/prayer/*.csv` | 사용자만 |
| 설교 맥락 | `output/{월}/{주차}/설교/sermon-context.md` | Team Leader 생성 (Sermon Agent 산출물 기반) |
| 진행 상태 | `output/{월}/{주차}/status.md` | Team Leader만 |

### 에이전트 목록

| 에이전트 | 타입 | 역할 |
|---------|------|------|
| team-leader | interactive | DAG 총괄, status.md 관리 |
| sermon | interactive | 설교 준비 5단계 |
| weekly-devotion | auto | 매일묵상 15개 HTML 생성 |
| insert-images | auto | 묵상 이미지 삽입 + A4 PNG 캡쳐 |
| prayer-doc | auto | 수요기도회 기도카드 HTML+PNG |
| small-group | auto | 소그룹 나눔지 (장년+청소년) |
| sns-cardnews | auto | SNS 카드뉴스 7장 |

새 에이전트 등록: `weekly-works/.claude/skills/team-leader/rules/agent-registry.md`

### 산출물 경로 규칙
- 카드뉴스 제작 전: `src/assets/templete src/` 레퍼런스 파일 먼저 확인
- 모든 주간 산출물: `weekly-works/output/{월}/{주차}/` 구조 준수

---

## 실행 환경
- Node.js 18+, Puppeteer: `cd weekly-works && npm install`
- Python 3.12+
- nlm (NotebookLM CLI): `uv tool install notebooklm-mcp-cli`
- yt-dlp: `uv tool install yt-dlp`
