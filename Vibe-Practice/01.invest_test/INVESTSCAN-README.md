# InvestScan

**자동 주간 투자 인텔리전스 시스템 — AI Agentic Workflow Automation**

글로벌 경제 데이터(FRED, EnvironmentScan)를 자동 수집·분석하여
매주 한국어 투자 관찰 리포트를 생성하고 Telegram으로 발송하는 AI 자동화 시스템.

> 이 시스템은 [AgenticWorkflow](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md) 만능줄기세포 프레임워크에서
> 분화한 **자식 시스템**입니다. 부모의 전체 DNA(절대 기준, 품질 보장, 안전장치, 기억 체계)를 내장합니다.

---

## ⚡ 빠른 시작 (30초)

Claude Code 터미널에서 한 줄만 입력하면 됩니다:

```
시작하자
```

→ 스마트 라우터가 시스템 상태를 자동 진단하고 6가지 실행 옵션을 보여줍니다.
→ 번호 또는 자연어로 원하는 모드를 선택하면 실행됩니다.

**상세 사용법**: [INVESTSCAN-USER-MANUAL.md](INVESTSCAN-USER-MANUAL.md)

---

## 시스템 현황

| 항목 | 상태 |
|------|------|
| **M0.5 마일스톤** | ✅ 달성 — 8/8 Done Gates PASS |
| **테스트** | 775개 전체 PASS |
| **Python 모듈** | 27개 (production) |
| **런타임 모드** | EnvScan 전용 (FRED fixture 사용) |
| **자동 실행 스케줄** | 매주 일요일 20:00 (macOS launchd) |
| **주요 출력** | Telegram 한국어 5줄 요약 + 마크다운 리포트 |

---

## InvestScan이 하는 일

```
[일요일 20:00 자동 실행]
      ↓
글로벌 경제 신호 수집
FRED 금리·인플레이션·위험선호 데이터
EnvironmentScan 정치·경제·사회 신호
      ↓
AI 분석 파이프라인 (10단계)
매크로 맥락 합성 → 종목 선택 → 내러티브 생성
Python 품질 검증 → 컴플라이언스 필터
      ↓
리포트 생성
영어 원본 + 한국어 번역 쌍
      ↓
[사용자 최종 검토 — HITL-3]
      ↓
📱 Telegram 발송
한국어 5줄 요약 메시지
```

---

## 핵심 설계 원칙

| 원칙 | 내용 |
|------|------|
| **P6 Python-First** | "Python is the judge, LLM is the narrator" — 모든 분류·검증은 Python 코드 |
| **P5 English-First** | 내부 에이전트 로직은 영어 (토큰 효율 + 정확도) |
| **단일 SOT** | 모든 상태는 `.claude/state.yaml` 한 파일에 집중 |
| **품질 절대주의** | 속도·비용·작업량보다 최종 결과물 품질이 유일한 기준 |

**절대 불변 상수**:
- `sentiment_weight = 0.0` — 비감정 분석 보장 (변경 시 파이프라인 즉시 중단)
- `BULLISH_THRESHOLD = 0.01` — 종목 선택 임계값 +1%

---

## 문서 구조

### InvestScan 자식 시스템 문서 (이 시스템)

| 문서 | 목적 |
|------|------|
| **[INVESTSCAN-README.md](INVESTSCAN-README.md)** (이 파일) | 시스템 개요 + 빠른 시작 |
| **[INVESTSCAN-USER-MANUAL.md](INVESTSCAN-USER-MANUAL.md)** | 사용자 매뉴얼 (실사용 방법) |
| **[INVESTSCAN-ARCHITECTURE-AND-PHILOSOPHY.md](INVESTSCAN-ARCHITECTURE-AND-PHILOSOPHY.md)** | 아키텍처 + 설계 철학 |
| **[DECISION-LOG.md](DECISION-LOG.md)** | 모든 설계 결정 이력 (ADR) |
| **[INVESTSCAN.md](INVESTSCAN.md)** | AI 에이전트 온보딩 문서 |

### AgenticWorkflow 부모 프레임워크 문서

| 문서 | 목적 |
|------|------|
| **[AGENTS.md](AGENTS.md)** | 모든 AI 에이전트 공통 지시서 (Hub) |
| **[CLAUDE.md](CLAUDE.md)** | Claude Code 전용 구현 가이드 |
| **[AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md)** | 부모 프레임워크 설계 철학 |
| **[AGENTICWORKFLOW-USER-MANUAL.md](AGENTICWORKFLOW-USER-MANUAL.md)** | 부모 프레임워크 사용 매뉴얼 |
| **[soul.md](soul.md)** | 프로젝트 철학 + DNA 유전 정의 |

> **부모-자식 문서 분리 패턴**: 부모 문서(`AGENTICWORKFLOW-*.md`)는 방법론/프레임워크를,
> 자식 문서(`INVESTSCAN-*.md`)는 InvestScan 도메인 고유 아키텍처를 기술합니다.
> 이 분리로 InvestScan 시스템이 AgenticWorkflow 없이도 독립적으로 이해·운영될 수 있습니다.

---

## 프로젝트 구조

```
01.invest_test/
├── INVESTSCAN-README.md                ← 이 파일
├── INVESTSCAN-USER-MANUAL.md           ← 사용자 매뉴얼
├── INVESTSCAN-ARCHITECTURE-AND-PHILOSOPHY.md  ← 아키텍처
├── INVESTSCAN.md                        ← AI 에이전트 온보딩
├── DECISION-LOG.md                      ← 설계 결정 이력 (ADR)
│
├── investscan/                          ← 27개 Python 모듈
│   ├── weekly_orchestrator.py           ← 메인 파이프라인 (494줄)
│   ├── schema.py                        ← 데이터 스키마 SOT
│   ├── synthesize_macro.py             ← FRED 매크로 분석
│   ├── intelligence_engine.py          ← LLM 내러티브 생성
│   ├── compliance_filter.py            ← 10패턴 컴플라이언스
│   ├── report_generator.py             ← Jinja2 리포트 생성
│   ├── telegram_notifier.py            ← Telegram 발송
│   └── ... (21개 추가 모듈)
│
├── tests/                               ← 26개 테스트 파일 (775개 테스트)
├── output/reports/                      ← 생성된 리포트 (마크다운)
├── output/dashboard/                    ← HTML 상태 대시보드
├── logs/                                ← 실행 로그
│
├── .claude/
│   ├── state.yaml                       ← SOT (단일 상태 파일)
│   ├── commands/                        ← 슬래시 커맨드 9개
│   ├── agents/                          ← 전문 에이전트 12개
│   └── hooks/scripts/                  ← 32개 Hook 스크립트
│
└── investscan.yaml                      ← 시스템 설정 파일
```

---

## 슬래시 커맨드 레퍼런스

| 커맨드 | 기능 |
|--------|------|
| `시작하자` (또는 `start`) | 스마트 라우터 → 실행 모드 선택 메뉴 |
| `/weekly-report` | 주간 리포트 전체 파이프라인 실행 |
| `/run-investscan` | 데이터 수집 + 분석만 실행 |
| `/approve-hitl 3` | 최종 리포트 승인 + Telegram 발송 |
| `/check-sot` | 시스템 상태 확인 |
| `/run-tdd` | 전체 테스트 스위트 실행 |
| `/translate` | 한국어 번역 수동 실행 |

---

## 마일스톤

```
M0.5 ✅ 완료 — 파이프라인 기반 구축
  ├─ DG-01~08: 8개 Done Gate 전체 PASS
  ├─ 775개 테스트 전체 PASS
  └─ Dry-run 전체 파이프라인 동작 확인

M1 🎯 진행 예정 — 실제 API 통합
  ├─ DG-09~16: 실제 FRED·DART API 연결
  ├─ HITL-1 완료 필요 (API 키 등록)
  └─ 실제 Telegram 발송

M2 📋 계획 — 고도화
  └─ 멀티 종목, 포트폴리오 분석, 정확도 추적
```

---

*InvestScan은 공개 정보 기반 분석이며 투자 조언을 제공하지 않습니다.*
*모든 투자 결정은 사용자의 책임입니다.*
