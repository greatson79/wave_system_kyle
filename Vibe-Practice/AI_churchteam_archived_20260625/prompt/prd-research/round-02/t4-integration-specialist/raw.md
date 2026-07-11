# T4 Integration Specialist — 원본 산출 (Round-02)

## 메타데이터
- 조사 차수: 2
- Teammate: Integration Specialist (t4)
- 조사 축: 기술·이론 축 — 연동 전략 (MCP·CLI·외부 도구)
- 생성일: 2026-04-29
- 근거 출처: Claude Code MCP 공식 문서 / weekly-works 실제 MCP 운용 사례 / AgenticWorkflow hook 스크립트 목록

---

## Branch 4.1: Minimal Integration (최소 연동)

**관점**: "외부 의존이 적을수록 안정적이다."

### Claude Code 단독으로 대체 가능한 것

| 기능 | 대체 방법 | 로컬 실행 |
|-----|---------|---------|
| 설교 초안 생성 | Claude 자체 생성 | LOCAL-OK |
| 신학 검증 | 프롬프트 기반 Theology Filter | LOCAL-OK |
| 상태 관리 | YAML 파일 읽기/쓰기 | LOCAL-OK |
| 슬래시 커맨드 진입점 | .claude/commands/ | LOCAL-OK |
| 산출물 포매팅 | 마크다운 렌더링 | LOCAL-OK |
| 한국어 신학 용어 처리 | 프롬프트 내 용어 사전 | LOCAL-OK |

### 반드시 외부가 필요한 기능

| 기능 | 외부 의존 | 로컬 대안 | 로컬 실행 |
|-----|---------|---------|---------|
| 원어 성경 DB | Logos, Accordance (유료 SaaS) | OSIS XML 로컬 설치 (무료) | LOCAL-OK (대안 선택 시) |
| 자동 스케줄링 | cron (OS 기본) | OS 내장 | LOCAL-OK |
| PDF/DOCX 출력 | Pandoc | 로컬 설치 | LOCAL-OK |
| A4 PNG 캡처 | Puppeteer (Node.js) | 로컬 설치 | LOCAL-OK |

### 최소 연동의 이점
- 설치·설정 단순화
- 이식성 최고 (다른 로컬 머신으로 이동 용이)
- 연동 실패 위험 없음

### 한계
- 원어 분석 품질: 로컬 DB 없이 Claude 단독 원어 분석은 환각 위험 높음
- 리서치 자동화 불가: 신학 자료 수집은 수동

**커버 가능 범위**: 설교 초안·신학 검증·행정 자동화 핵심

**로컬 실행**: LOCAL-OK (전범위)

🅿️ 파킹 로트: OSIS XML 로컬 설치 방법 구체 비교 필요 (Round-03 추가 조사 제안)

---

## Branch 4.2: Active Integration (적극 연동)

**관점**: "적절한 연동이 워크플로우의 역량을 극대화한다."

### MCP 서버 연동 전략

| MCP 서버 | 기능 | 안정성 | 로컬 실행 | 비고 |
|---------|-----|-------|---------|-----|
| `mcp__notebooklm__` | 리서치 자료 수집·분석 | 중간 | LOCAL-PARTIAL | Google 계정 의존, 인증 만료 위험 |
| `mcp__playwright__` | A4 캡처, 브라우저 자동화 | 높음 | LOCAL-OK | weekly-works 검증됨 |
| `mcp__context7__` | 라이브러리 문서 조회 | 높음 | LOCAL-OK | 신학 라이브러리 문서 조회 가능 |
| `mcp__plugin_telegram__` | 알림 발송 | 중간 | LOCAL-PARTIAL | Telegram Bot API 의존 |

### 로컬 CLI 도구 연동

| 도구 | 기능 | 설치 방법 | 로컬 실행 |
|-----|-----|---------|---------|
| cron (OS 기본) | 자동 주간 트리거 | OS 내장 | LOCAL-OK |
| pandoc | DOCX/PDF 변환 | brew install pandoc | LOCAL-OK |
| puppeteer | A4 PNG 캡처 | npm install | LOCAL-OK |
| yt-dlp | YouTube 리서치 | uv tool install yt-dlp | LOCAL-OK |

### LOCAL-PARTIAL 항목 상세

**NotebookLM MCP**
- 연동 실패 시: 파이프라인 리서치 단계 중단
- 대안: 파일 기반 수동 리서치 (품질 저하)
- 우회: `refresh_auth()` 선제 호출 + 실패 시 수동 자료 주입

**Telegram Bot**
- 연동 실패 시: 알림만 영향, 파이프라인 미중단
- 대안: 출력 파일 직접 확인

### 연동 관리 전략
- 버전 관리: requirements.txt / package.json으로 CLI 도구 버전 고정
- 실패 감지: Hook 스크립트에서 CLI 도구 존재 여부 사전 확인
- 테스트: 주간 시작 전 `setup_init.py` 연동 상태 점검

**로컬 실행**: LOCAL-OK (CLI), LOCAL-PARTIAL (MCP 일부)

---

## Branch 4 통합 결론

- 핵심 기능(설교·신학·묵상)은 **최소 연동으로 충분**
- 가치 추가 연동(원어 DB, 리서치 자동화, A4 캡처): 추가 로컬 설치로 LOCAL-OK 전환 가능
- NotebookLM MCP는 LOCAL-PARTIAL → 인증 재시도 로직 Orchestrator 내장 필요
- **PRD에서 "필수 연동" vs "선택 연동" 표 명시 필수**
- 연동 스펙트럼 위치: **최소+α (원어 DB, Playwright 추가)**

### 연동 분류표 (PRD용)

| 연동 항목 | 분류 | 로컬 실행 |
|---------|-----|---------|
| state.yaml | 필수 | LOCAL-OK |
| cron (자동 트리거) | 선택 | LOCAL-OK |
| OSIS XML 원어 DB | 권장 | LOCAL-OK (설치 필요) |
| pandoc | 선택 | LOCAL-OK |
| Playwright MCP | 선택 | LOCAL-OK |
| NotebookLM MCP | 선택 | LOCAL-PARTIAL |
| Telegram Bot | 선택 | LOCAL-PARTIAL |
| Logos/Accordance | 제외 | LOCAL-BLOCKED: SaaS 유료 구독 전제 |
