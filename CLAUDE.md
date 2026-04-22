# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 이 저장소의 목적

**WAVE AI Networks** — 디딤교회의 주간 콘텐츠 자동화 및 AI 에이전트 시스템 허브.
핵심 작업 디렉토리는 `Claude_skills/weekly-works/`이며, 대부분의 실무는 여기서 실행된다.

---

## 절대 기준

> 어떤 상황에서도 예외 없이 적용. 효율·속도·토큰 비용을 이유로 우회 불가.

1. **품질 우선** — 콘텐츠 완성도와 신학적 정확성이 최우선. 일부만 완료하고 조용히 넘어가지 않는다.
2. **SOT 준수** — AI가 "기억"으로 데이터를 생성하지 않는다. 반드시 지정된 원천 파일에서 읽는다.
3. **CCP** — 세션 시작 시 `output/{월}/{주차}/status.md`를 확인하여 맥락을 이어받는다.
4. **코드 변경 전** — 의도 파악 → 영향 범위 분석 → 변경 설계 3단계 수행 (대규모 변경은 사용자 승인 필수).

---

## 실행 환경

```bash
# Node.js 의존성 (Puppeteer A4 캡쳐)
cd Claude_skills/weekly-works && npm install

# Python 3.12+

# NotebookLM CLI (최초 1회 설치)
uv tool install notebooklm-mcp-cli
nlm login  # 인증

# yt-dlp (리서치 파이프라인)
uv tool install yt-dlp
```

---

## 주요 커맨드

| 커맨드 | 동작 |
|--------|------|
| `/주간총괄 [주차번호]` | 주간 전체 콘텐츠 통합 생성 (메인 진입점) |
| `/주간현황` | 현재 주차 진행 상태 대시보드 |
| `/설교 [본문]` | 설교 준비 5단계 |
| `/wave [요청]` | WAVE AI Orchestrator (범용 요청) |
| `/연구 [주제]` | 리서치 에이전트 |
| `/research run <주제> --auto` | YouTube → NotebookLM → 리포트 파이프라인 |

**선택 실행 플래그** (`/주간총괄`에 추가):
`--설교만` / `--묵상만` / `--기도만` / `--나눔지만` / `--카드뉴스만` / `이어서`

---

## 아키텍처

```
Ai_works/
├── Claude_skills/              ← ⭐ 핵심 작업 공간
│   ├── .claude/commands/       ← 슬래시 커맨드 정의 (주간총괄, 주간현황, 설교, wave, 연구 등)
│   ├── weekly-works/           ← 주간 콘텐츠 통합 시스템 (상세: weekly-works/CLAUDE.md)
│   │   ├── .claude/skills/     ← 7개 전문 에이전트 스킬
│   │   ├── data/               ← SOT 데이터 (sermon-plan-2026.json, prayer/*.csv)
│   │   ├── src/                ← 템플릿, 에셋, 스크립트 (capture-a4.js, logos)
│   │   └── output/             ← 결과물 ({월}/{주차}/ 구조)
│   └── Wave-AI/                ← 멀티-LLM 에이전트 시스템 (8개 역할, Claude/GPT/Gemini 혼용)
├── AgenticWorkflow-Template/   ← 부모 프레임워크 — 모든 에이전트 시스템의 설계 철학 원본
│   ├── AGENTS.md               ← 방법론 허브 (가장 중요한 참조 문서)
│   ├── soul.md                 ← DNA 상속 원칙
│   └── docs/protocols/         ← autopilot, quality-gates, ulw-mode, code-change-protocol
├── Vibe-Practice/              ← 실험적 에이전트 프로젝트 모음
│   ├── 01.invest_test/         ← 주식 투자 스캔 시스템 (Python)
│   ├── Dissertation-Simulator/ ← 박사논문 자동화
│   ├── GlobalNews-Crawling/    ← 뉴스 수집·스캐닝
│   └── Sermon-Assistant/       ← 설교 보조 에이전트
├── church-accounting/          ← 교회 회계 웹앱 (Next.js 13+ / TypeScript / Vercel)
├── notebookLM/                 ← NotebookLM 작업 파일 ({노트북명}/ 하위)
├── output/                     ← 루트 산출물
│   └── 환경스캐닝/{날짜}_{주제}/
└── src/wave_ai/                ← WAVE AI 로고·에셋
```

### Weekly-Works 워크플로우 DAG

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
| 설교 맥락 | `output/{월}/{주차}/설교/sermon-context.md` | Sermon Agent만 |
| 진행 상태 | `output/{월}/{주차}/status.md` | Team Leader만 |

### Weekly-Works 에이전트 목록

| 에이전트 | 타입 | 역할 |
|---------|------|------|
| team-leader | interactive | DAG 총괄, status.md 관리 |
| sermon | interactive | 설교 준비 5단계 |
| weekly-devotion | auto | 매일묵상 15개 HTML 생성 |
| insert-images | auto | 묵상 이미지 삽입 + A4 PNG 캡쳐 |
| prayer-doc | auto | 수요기도회 기도카드 HTML+PNG |
| small-group | auto | 소그룹 나눔지 (장년+청소년) |
| sns-cardnews | auto | SNS 카드뉴스 7장 |

새 에이전트 등록: `weekly-works/.claude/skills/team-leader/rules/agent-registry.md`에 source 경로 + type 지정.

### Wave-AI 에이전트 구조

8개 역할: CEO / Flow-Operations Orchestrator(Claude) / CTO(GPT) / Learning Lead(Claude) / Content Lead(GPT) / Network Lead(Claude) / Knowledge Lead(Gemini Pro) / AI-Systems Lead(GPT).  
시스템 프롬프트: `Claude_skills/Wave-AI/system-prompts/`, Paperclip 설정: `Claude_skills/Wave-AI/paperclip/`.

---

## MCP 서버

- **NotebookLM MCP**: 도구 접두사 `mcp__notebooklm__`. 각 단계(collect/analyze/export) 시작 전 `refresh_auth()` 선제 호출.
- **Telegram**: `@kyle_cc_bot` — 메시지 수신 시 `<channel source="telegram">` 태그로 전달됨.

---

## 산출물 경로 규칙

- 카드뉴스 제작 전: `src/assets/templete src/` 레퍼런스 파일 반드시 먼저 확인
- 환경스캐닝 산출물: `output/환경스캐닝/{날짜}_{주제}/`에 저장
- NotebookLM 작업 파일: `notebookLM/{노트북 이름}/` 하위에 저장
- 모든 주간 산출물: `Claude_skills/weekly-works/output/{월}/{주차}/` 구조 준수

---

## 프로젝트별 참조 문서

| 프로젝트 | 진입점 |
|---------|--------|
| 주간 콘텐츠 시스템 | `Claude_skills/weekly-works/CLAUDE.md` |
| 에이전트 설계 방법론 | `AgenticWorkflow-Template/AGENTS.md` |
| Wave-AI 시스템 | `Claude_skills/Wave-AI/WAVE-AI.md` |
| 교회 회계 웹앱 | `church-accounting/README.md` |
| 각 Vibe-Practice 프로젝트 | 해당 폴더 내 `CLAUDE.md` |
