# CLAUDE.md — Ai_works 루트

**WAVE AI Networks** — 디딤교회 AI 자동화 허브.
`Claude_skills/weekly-works/`가 핵심 운영 공간. `Vibe-Practice/`는 실험 공간.

---

## 절대 기준

어떤 상황에서도 예외 없이 적용.

1. **품질 우선** — 신학적 정확성과 콘텐츠 완성도가 최우선. 일부만 완료하고 넘어가지 않는다.
2. **SOT 준수** — AI가 기억으로 데이터를 생성하지 않는다. 반드시 지정 원천 파일에서 읽는다.
3. **CCP** — 세션 시작 시 해당 프로젝트의 status 파일을 확인해 맥락을 이어받는다.
4. **코드 변경 전** — 의도 파악 → 영향 범위 분석 → 변경 설계 3단계. 대규모 변경은 승인 필수.

---

## 폴더 구조 및 진입점

| 폴더 | 목적 | 상세 문서 |
|------|------|----------|
| `Claude_skills/` | ⭐ 핵심 스킬·콘텐츠 운영 공간 | `Claude_skills/CLAUDE.md` |
| `Vibe-Practice/` | 실험적 에이전트 프로젝트 | `Vibe-Practice/CLAUDE.md` |
| `AgenticWorkflow-Template/` | 에이전트 설계 방법론 원본 | `AgenticWorkflow-Template/AGENTS.md` |
| `church-accounting/` | 교회 회계 웹앱 (Next.js/Vercel) | `church-accounting/README.md` |
| `notebookLM/` | NotebookLM 작업 파일 | `{노트북명}/` 하위 |
| `output/` | 루트 산출물 | `환경스캐닝/{날짜}_{주제}/` |

---

## 주요 커맨드 빠른 참조

### 주간 콘텐츠 (Claude_skills/weekly-works/)
| 커맨드 | 동작 |
|--------|------|
| `/주간총괄 [주차]` | 설교·묵상·기도카드·나눔지·카드뉴스 통합 생성 |
| `/주간현황` | 진행 상태 대시보드 |
| `/설교 [본문]` | 설교 준비 5단계 |
| `/wave [요청]` | WAVE AI Orchestrator |
| `/연구 [주제]` | 리서치 에이전트 |

### 청소년 인생계획 (Claude_skills/youth_life_plan/)
| 커맨드 | 동작 |
|--------|------|
| `/인터뷰` | 인생계획 시작 — 학년대 분기 |
| `/수련회` | 45~60분 집중 플로우 |
| `/반기회고` | 반기 성찰 10문 |

---

## 전역 MCP 서버

- **NotebookLM MCP**: 도구 접두사 `mcp__notebooklm__`. 각 단계 시작 전 `mcp__notebooklm__re_auth` 선제 호출. 인증 만료 시 `nlm login` 재실행.
- **Telegram**: `@kyle_cc_bot` — 메시지 수신 시 `<channel source="telegram">` 태그로 전달됨.

---

## 전역 실행 환경

```bash
# NotebookLM CLI (최초 1회)
uv tool install notebooklm-mcp-cli && nlm login

# yt-dlp
uv tool install yt-dlp

# weekly-works Node.js (Puppeteer)
cd Claude_skills/weekly-works && npm install
```
