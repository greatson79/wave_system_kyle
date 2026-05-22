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
└── Wave-AI/                ← WAVE AI 시스템 설계 문서
    ├── WAVE-AI.md
    └── agents/             ← 범용 에이전트 (orchestrator, research, content-creator, knowledge)
```

## 핵심 사용법

### 주간 콘텐츠 (weekly-works/)
- `/주간총괄 [주차번호]` — 설교 + 매일묵상 + 기도카드 + 소그룹 나눔지 + 카드뉴스 한번에
- `/주간현황` — 진행 상태 대시보드
- `/설교 [본문]` — 설교 준비 5단계
- 상세: `weekly-works/CLAUDE.md` 참조

### 청소년 인생계획 (youth_life_plan/)

스킬 위치: `Claude_skills/youth_life_plan/SKILL.md`

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

## 실행 환경
- Node.js 18+, Puppeteer
- Python 3.12+
- nlm (NotebookLM CLI): `uv tool install notebooklm-mcp-cli`
- yt-dlp: `uv tool install yt-dlp`
