# InvestScan 사용자 매뉴얼

> **대상 독자**: InvestScan 시스템을 처음 사용하거나 일상적으로 사용하는 사용자
> **목표**: "시작하자" 한 마디로 시스템을 제어할 수 있게 되는 것

---

## 가장 중요한 한 가지

InvestScan을 사용하는 방법은 **딱 한 가지**만 기억하면 됩니다:

```
시작하자
```

Claude Code 터미널에 위 단어를 입력하면, 시스템이 알아서 모든 것을 안내합니다.

---

## 목차

1. [처음 사용하기 — "시작하자"](#1-처음-사용하기--시작하자)
2. [시스템 상태 읽는 법](#2-시스템-상태-읽는-법)
3. [6가지 실행 모드](#3-6가지-실행-모드)
4. [주간 리포트 생성 전체 흐름](#4-주간-리포트-생성-전체-흐름)
5. [HITL 게이트 — 사람의 승인이 필요한 순간](#5-hitl-게이트--사람의-승인이-필요한-순간)
6. [리포트 확인하기](#6-리포트-확인하기)
7. [자동 실행 스케줄](#7-자동-실행-스케줄)
8. [자주 사용하는 커맨드](#8-자주-사용하는-커맨드)
9. [문제 해결 (FAQ)](#9-문제-해결-faq)

---

## 1. 처음 사용하기 — "시작하자"

### 1.1 시작 명령어

Claude Code에서 아래 중 하나를 입력합니다 (모두 같은 결과):

```
시작하자
시작
start
InvestScan 시작
실행해줘
```

### 1.2 화면에 나타나는 것

입력 직후 **두 단계**가 순서대로 실행됩니다.

**Step 1 — 시스템 상태 자동 진단:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀  InvestScan — 제품 실행 모드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  시스템 상태
  ├─ M0.5 마일스톤  ✅ PASS
  ├─ M1 마일스톤    ✅ PASS
  ├─ 런타임 모드    📡 EnvScan 전용 (FRED fixture 사용)
  ├─ 마지막 리포트  📅 2026-03-29
  ├─ 마지막 실행    🕐 2026-03-29 19:01 (3시간 전)
  ├─ 다음 자동 실행  ⏰ 2026-04-05 20:00 (D-7)
  └─ API 연결 상태  FRED ⚠️ | DART ⚠️ | Telegram ⚠️
```

**Step 2 — 실행 모드 선택 메뉴:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  실행 모드를 선택하세요
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [1]  📊  주간 리포트 생성  ────────────── 권장
  [2]  🧪  Dry-Run 시뮬레이션  ──────────── 테스트
  [3]  📡  데이터 수집만  ──────────────── 데이터
  [4]  🔍  특정 종목 단독 분석  ────────── 개별
  [5]  ⚡  파이프라인 게이트 전체 검증  ── 진단
  [6]  📋  현재 상태 확인  ────────────── 조회
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  번호, 이름, 또는 자연어로 선택하세요.
```

### 1.3 선택하는 방법

번호, 이름, 자연어 — 어떤 방식으로든 선택할 수 있습니다:

```
"1"          → 주간 리포트 생성
"1번 실행"    → 주간 리포트 생성
"dry-run"    → Dry-Run 시뮬레이션
"테스트해보자" → Dry-Run 시뮬레이션
"상태 확인"   → 현재 상태 확인
"5"          → 게이트 검증
```

---

## 2. 시스템 상태 읽는 법

"시작하자" 입력 후 나타나는 상태 화면 각 항목의 의미:

| 항목 | 의미 | ✅ 정상 | ⚠️ 주의 |
|------|------|--------|--------|
| M0.5 마일스톤 | 파이프라인 기반 구축 완료 여부 | PASS | FAIL → `/install` 실행 필요 |
| M1 마일스톤 | 실제 API 통합 완료 여부 | PASS | FAIL → dry-run만 사용 |
| 런타임 모드 | 실제 API 사용 여부 | full (실제 API) | envscan_only (fixture) |
| 마지막 리포트 | 마지막으로 생성된 리포트 날짜 | 최근 날짜 | "없음" → 아직 생성 안 됨 |
| 마지막 실행 | 파이프라인 마지막 실행 시간 | 최근 시간 | "기록 없음" |
| 다음 자동 실행 | 다음 일요일 20:00까지 D-N일 | D-0~7 | - |
| API 연결 상태 | FRED/DART/Telegram 키 등록 여부 | ✅ | ⚠️ → HITL-1 필요 |

### 런타임 모드 3가지

```
📡 전체 파이프라인 (FRED + EnvScan + DART)
   → 실제 API 키 사용, 실제 데이터, 실제 Telegram 발송

📡 EnvScan 전용 (FRED fixture 사용)
   → FRED는 테스트 데이터, EnvScan은 실제 데이터
   → 현재 기본 모드 (M0.5)

📡 독립 모드 (fixture 전용, API 없음)
   → 모든 데이터가 테스트 데이터
   → API 키 없어도 완전 동작 (비용 없음)
```

---

## 3. 6가지 실행 모드

### [1] 📊 주간 리포트 생성 — 권장

**하는 일**: 데이터 수집 → 분석 → 내러티브 생성 → 한국어 번역 → Telegram 발송

**언제 사용**: 매주 실제 리포트를 만들 때

**실행 후 흐름**:
1. 파이프라인 완료 → 3줄 요약 출력 (종목/신호/품질)
2. 리포트 미리보기 (선택)
3. HITL-3 승인 → Telegram 발송

```
"1번 실행해줘"
"주간 리포트 만들자"
"full"
```

---

### [2] 🧪 Dry-Run 시뮬레이션 — 테스트

**하는 일**: 실제 API 없이 테스트 데이터(fixture)로 전체 파이프라인 실행

**언제 사용**:
- API 키 없을 때
- 시스템이 정상인지 확인할 때
- 비용 없이 연습할 때

**특징**: 외부 API 호출 없음, Telegram 실제 발송 없음

```
"2번"
"dry-run"
"드라이런"
"테스트"
```

---

### [3] 📡 데이터 수집만 — 데이터

**하는 일**: FRED + EnvScan 데이터 수집, 컨텍스트 파일 저장. 내러티브 생성 없음.

**언제 사용**: 데이터만 먼저 수집하고 나중에 분석할 때 (일요일 자동 실행과 동일)

```
"3번"
"데이터 수집"
"data-only"
```

---

### [4] 🔍 특정 종목 단독 분석 — 개별

**하는 일**: 사용자가 지정한 단일 종목만 분석

**사용법**:
```
"4번 삼성전자"
"005930 분석해줘"
```
시스템이 종목 코드(6자리), 종목명, 카테고리(A/B)를 차례로 질문합니다.

```
분석할 종목 코드를 입력하세요. (예: 005930): 005930
종목 이름을 입력하세요. (예: 삼성전자): 삼성전자
카테고리를 선택하세요. [A] 재무 실적 기반 / [B] 테마 기반: A
```

---

### [5] ⚡ 파이프라인 게이트 전체 검증 — 진단

**하는 일**: 16개 Done Gate(M0.5 + M1) 전체를 dry-run으로 재검증

**언제 사용**: 시스템이 이상한 것 같을 때, 업데이트 후 정상 확인

```
"5번"
"게이트 검증"
"진단"
```

---

### [6] 📋 현재 상태 확인 — 조회

**하는 일**: SOT state.yaml, 에러 로그, 마일스톤 게이트 현황 상세 출력

**언제 사용**: 시스템 상태를 자세히 보고 싶을 때

```
"6번"
"상태 확인"
"check"
```

---

## 4. 주간 리포트 생성 전체 흐름

한 번 리포트를 만드는 전체 과정입니다.

```
1. "시작하자" 입력
        ↓
2. 상태 확인 (M0.5 ✅, M1 ✅ 확인)
        ↓
3. "1" 또는 "주간 리포트" 선택
        ↓
4. 파이프라인 자동 실행 (약 2-5분)
   • 데이터 수집
   • 매크로 분석
   • 종목 선택
   • 내러티브 생성 (최대 3회 자동 재시도)
   • 품질 검증
   • 한국어 번역
        ↓
5. 완료 요약 자동 출력
   ✅ 파이프라인 완료 — 2026-03-29
   종목: Samsung Electronics (005930) | Category A
   신호: 📈 Positive momentum maintained
   실적: Revenue +8.3% YoY
   품질: pACS 🟢 88 GREEN
        ↓
6. 리포트 미리보기 (원하면)
   → "미리보기 보여줘" 입력
        ↓
7. HITL-3 승인
   → 3줄 요약 + "Telegram 발송하시겠습니까? [Y/N]"
   → Y 입력
        ↓
8. 📱 Telegram 발송 완료
```

---

## 5. HITL 게이트 — 사람의 승인이 필요한 순간

HITL(Human-in-the-Loop)은 자동화 흐름 중 **반드시 사람이 확인하고 넘어가야 하는 지점**입니다.
InvestScan에는 3개의 HITL 게이트가 있습니다.

### HITL-1 — API 키 등록 (최초 1회)

**언제**: 처음 시스템 설정할 때

**해야 할 것**:
- FRED API 키 등록 (무료, [fred.stlouisfed.org](https://fred.stlouisfed.org))
- Telegram Bot Token + Chat ID 등록
- DART API 키 등록 (선택사항)
- 관심 섹터 목록 확인

**완료 커맨드**:
```
/approve-hitl 1
```

---

### HITL-2 — 런타임 모드 선택 (최초 1회)

**언제**: API 키 등록 후

**해야 할 것**:
- 사용 모드 선택: `full` (전체 API) / `envscan_only` (EnvScan만) / `independent` (fixture만)
- M1 예상 비용 확인 및 동의

**현재 상태**: 완료 (envscan_only 모드 선택됨)

---

### HITL-3 — 리포트 최종 승인 (매주)

**언제**: 주간 리포트 생성 완료 후

**해야 할 것**:
- 생성된 리포트 내용 검토
- Telegram 발송 승인

**간소화 승인 방법** (권장):
```
python3 -m investscan.approve_hitl
```
→ 3줄 요약 확인 후 Y 입력

또는 전통적 방법:
```
/approve-hitl 3
```

---

## 6. 리포트 확인하기

### 6.1 생성된 리포트 위치

파이프라인은 두 곳에 파일을 저장합니다:

**시스템 내부 (파이프라인 중간 산출물)**
```
output/reports/weekly-report-2026-03-29.md     ← 영어 원본
output/reports/weekly-report-2026-03-29.ko.md  ← 한국어 번역 (생성된 경우)
```

**사용자 폴더 (최종 산출물 — TXT + PDF + MD)**
```
~/Desktop/Ai_works/output/투자분석제안/
├── 2026-03-30_주간투자분석.txt   ← 평문 텍스트 (터미널·메모장 직독)
├── 2026-03-30_주간투자분석.pdf   ← PDF (인쇄·공유용)
└── 2026-03-30_주간투자분석.md    ← 원본 마크다운 참조용
```

### 6.2 리포트 구조

```
# Weekly Investment Signal Report
**Samsung Electronics (005930)** | Week: 2026-W13 | Category: A

## Executive Summary      ← 핵심 분석 서술
## Financial Snapshot     ← YoY 성장률, 밸류에이션, 외국인 수급
## Signal Direction        ← 방향 판단 (Positive/Neutral/Risk)
## Macro Environment       ← Fed, 인플레이션, 위험선호, USD
## Accuracy Tracker        ← 예측 정확도 추적 기준
## Bear Case               ← 하방 리스크 시나리오
## Disclaimer              ← 법적 면책 조항
```

### 6.3 인라인 미리보기

리포트 파일을 열지 않고도 터미널에서 바로 볼 수 있습니다:

```
python3 -m investscan.preview_report
```

Executive Summary + Financial Snapshot + Macro 환경을 터미널에 바로 출력합니다.

### 6.4 TXT / PDF 내보내기

분석 결과를 TXT와 PDF로 저장합니다:

```bash
# 최신 리포트를 자동으로 찾아서 내보내기 (기본 형식: txt, pdf)
python3 -m investscan.export_report

# 날짜를 지정해서 내보내기
python3 -m investscan.export_report --date 2026-03-30

# 파일 경로를 직접 지정
python3 -m investscan.export_report --path "/path/to/report.md"

# 형식 선택 (txt만, pdf만, 또는 둘 다)
python3 -m investscan.export_report --formats txt
python3 -m investscan.export_report --formats pdf
python3 -m investscan.export_report --formats txt,pdf
```

저장 결과 예시:
```
✅ TXT  → ~/Desktop/Ai_works/output/투자분석제안/2026-03-30_주간투자분석.txt
✅ PDF  → ~/Desktop/Ai_works/output/투자분석제안/2026-03-30_주간투자분석.pdf
✅ MD   → ~/Desktop/Ai_works/output/투자분석제안/2026-03-30_주간투자분석.md
```

### 6.5 Telegram 메시지 형식

Telegram으로 발송되는 5줄 요약:
```
📊 삼성전자 (005930) | 카테고리 A
📈 매출 YoY +8.3%, 영업이익 +34.2%
✅ 긍정적 모멘텀 유지
⚠️ DRAM 공급 과잉 재발 리스크
📅 다음 확인: 2026-04-05
```

---

## 7. 자동 실행 스케줄

InvestScan은 **매주 일요일 저녁 8시**에 자동으로 실행됩니다.

```
일요일 20:00  →  데이터 수집 자동 실행 (launchd)
                  FRED + EnvScan 데이터 수집
                  컨텍스트 파일 저장 (output/context/)

월요일 이후   →  "시작하자" → [1] 선택
                  내러티브 생성 → 번역 → HITL-3 → Telegram
```

**자동 실행 확인**: `/start` 화면에서 "다음 자동 실행 D-N" 항목으로 확인.

**자동 실행이 안 된다면**:
```
python3 run_m05.py --dry-run   ← M0.5 게이트 재검증
```

---

## 8. 자주 사용하는 커맨드

### 일상 사용

```bash
# 시작 (가장 많이 사용)
시작하자

# 리포트 미리보기
python3 -m investscan.preview_report

# 완료 요약 확인
python3 -m investscan.run_summary

# HITL-3 승인
python3 -m investscan.approve_hitl
```

### 테스트 및 진단

```bash
# 전체 테스트 실행
/run-tdd

# 상태 상세 확인
/check-sot

# 게이트 재검증
python3 run_m05.py --dry-run
python3 run_m1.py --dry-run
```

### 파이프라인 직접 실행

```bash
# 전체 파이프라인 (실제 실행)
python3 -m investscan.weekly_orchestrator --mode full-auto

# Dry-run (테스트)
python3 -m investscan.weekly_orchestrator --mode dry-run

# 데이터 수집만
python3 -m investscan.weekly_orchestrator --mode data-only
```

---

## 9. 문제 해결 (FAQ)

### Q: "시작하자"를 입력했는데 아무것도 안 나와요.

A: Claude Code가 활성화된 상태인지 확인하세요. Claude Code 터미널에서 입력해야 합니다.

---

### Q: M0.5 마일스톤이 ⚠️ FAIL로 나와요.

A: `/install` 커맨드를 실행하세요. 인프라를 재검증합니다.
```
/install
```

---

### Q: API 연결 상태가 모두 ⚠️이에요.

A: HITL-1이 완료되지 않은 상태입니다. API 키를 등록해야 합니다.
```
/approve-hitl 1
```
키 등록 전에는 `독립 모드 (fixture 전용)`으로 모든 기능을 테스트할 수 있습니다.

---

### Q: 리포트 품질이 RED (pACS < 70)로 나왔어요.

A: 번역 품질이 낮은 경우입니다. 번역을 다시 실행하세요:
```
/translate
```

---

### Q: 파이프라인이 중간에 멈췄어요.

A: 로그를 확인하세요:
```bash
cat logs/orchestrator.log | tail -50
cat logs/orchestrator_err.log | tail -20
```
에러 내용을 확인한 후 `python3 run_m05.py --dry-run`으로 게이트를 재검증하세요.

---

### Q: Telegram으로 메시지가 안 와요.

A: 현재 M0.5 단계에서는 Telegram이 **Dry-run 모드**로 실제 발송이 되지 않습니다.
실제 발송을 위해서는 HITL-1에서 Telegram Bot Token과 Chat ID를 등록해야 합니다.

---

### Q: "Infrastructure Build 재실행" 옵션이 없어요.

A: 정상입니다. InvestScan 제품 실행 모드에서는 빌드 관련 옵션이 표시되지 않습니다.
빌드는 이미 완료된 단계입니다. 게이트 재검증이 필요하면 [5]번 옵션을 사용하세요.

---

### Q: 특정 종목을 분석하고 싶어요.

A: `시작하자` → [4]번 선택 → 종목 코드(6자리), 이름, 카테고리(A/B) 입력.
```
시작하자 → 4번 → 005380 입력 → 현대차 입력 → A 선택
```

---

### Q: 시스템 전체를 테스트하고 싶어요.

A: Dry-Run이 가장 안전한 방법입니다:
```
시작하자 → 2번 (Dry-Run)
```
또는 직접:
```
python3 -m investscan.weekly_orchestrator --mode dry-run
```
외부 API 호출 없이 전체 파이프라인을 테스트합니다.

---

## 부록 — 기술 문서

| 목적 | 문서 |
|------|------|
| 아키텍처 이해 | [INVESTSCAN-ARCHITECTURE-AND-PHILOSOPHY.md](INVESTSCAN-ARCHITECTURE-AND-PHILOSOPHY.md) |
| 설계 결정 근거 | [DECISION-LOG.md](DECISION-LOG.md) |
| AI 에이전트 지시서 | [INVESTSCAN.md](INVESTSCAN.md) |
| 부모 프레임워크 | [AGENTICWORKFLOW-USER-MANUAL.md](AGENTICWORKFLOW-USER-MANUAL.md) |

---

*InvestScan은 공개 정보 기반 분석이며 투자 조언을 제공하지 않습니다.*
*모든 투자 결정은 사용자 본인의 책임입니다.*
