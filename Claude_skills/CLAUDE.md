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

### NLM 리서치
- `/research run <주제> --auto` — YouTube → NotebookLM → 리포트/팟캐스트/슬라이드
- 필수: `nlm login` (최초 1회)

## 실행 환경
- Node.js 18+, Puppeteer
- Python 3.12+
- nlm (NotebookLM CLI): `uv tool install notebooklm-mcp-cli`
- yt-dlp: `uv tool install yt-dlp`
