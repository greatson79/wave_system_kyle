# InvestScan PRD — 제품 요구사항 문서

> **문서 버전**: v1.3
> **작성일**: 2026-03-28 | **최종 수정**: 2026-03-28
> **소스**: final-research.md R1-R10 성찰 통합 + PRD 황금 원칙 6가지 적용 + 9개 성찰 에이전트 권장사항 전체 반영 (Round 1 핵심목적·워크플로우준비도 + Round 2 구현완전성·벤치마킹·파이프라인 + Round 3 적대적 공격-방어 실현가능성·기술결함·사용성)
> **독자**: (1) 사용자(비코더 목사님) — Section 1-5, (2) Claude Code(구현자) — Section 0, Section 6-15

---

## 핵심 목적 (절대 목표)

> 사용자의 최소 입력을 받아, 글로벌 경제 흐름과 매크로 맥락을 반영한 날카로운 통찰로 — 수치·근거·리스크를 갖춘 — **거시 신호 기반 섹터 방향 인텔리전스** 리포트와 종목 관찰 원고를 자동 생성한다. *(전문가 수준 대체가 아닌 거시 신호 기반 방향성 참고 자료 — 법적 이유로 매수/매도 의견 제외, 거시 방향성 + 관찰 종목 중심)* 안정적 현재 종목과 미래 성장 테마를 구분하여 제공하며, 편집 없이 즉시 투자 판단과 콘텐츠 게시에 활용할 수 있는 완성본을 출력한다.

이 목적을 workflow의 모든 단계와 모든 기능에 **절대 목표**로 고정한다.

**"날카로운 통찰"의 조작적 정의:**
- 각 근거 신호에 최소 1개의 정량 데이터 포인트(수치·비율·금액) 포함 필수
- 정량 데이터 없는 신호는 pSST 가중치 50% 감산 적용
- 신호 간 인과 논리 경로 최소 2단계 이상 명시 (예: "CHIPS Act 예산 집행 → TSMC 수주 확대 → SK하이닉스 HBM 공급 계약 증가")
- 입력 신호 `summary` 필드가 빈 문자열이거나 50자 미만이면 리포트 근거로 사용 불가

**리포트 품질 최소 기준** (Claude Code가 리포트 발송 전 자가 검증 — 7개):
1. 모든 섹터 방향에 **독립** 소스 신호 ≥ 3개 사용 *(독립 소스 = 다른 미디어 기관 OR 다른 원본 데이터 포인트. 동일 보도자료 인용 2건은 독립 소스 1개로 산정)*
2. 각 신호에 출처(미디어명 + 날짜) 명시
3. 하방 리스크 신호 1개 이상 포함
4. 타임프레임 명시 (4-12주)
5. "이번 주 행동 1가지" 포함
6. 핵심 섹터 인과 논리 체인 최소 2단계 명시 (Section 7.8 참조)
7. 방향 반전 시나리오(Bear Case) 1개 이상 포함 (Section 7.8 참조)

→ 7/7 충족 시 정상 발송. 미충족 항목당 신뢰도 **-5% 감산** 후 발송 (기존 "경고 후 발송" 대체).

---

## Table of Contents

**[사용자가 읽는 섹션 — 기술 용어 최소화]**
- [Section 1: 이 시스템이 무엇인가](#section-1)
- [Section 2: 왜 만드는가](#section-2)
- [Section 3: 어떻게 사용하는가 (비코더 사용자 여정)](#section-3)
- [Section 4: 성공 기준](#section-4)
- [Section 5: 비용과 시간](#section-5)

**[Claude Code가 읽는 섹션 — 모호함 0]**
- [Section 0: 설치 전제 조건 (Prerequisites)](#section-0)
- [Section 6: M0.5 구현 명세 (6.5 실패 복구 프로토콜)](#section-6)
- [Section 7: M1 구현 명세 (7.6 워치리스트+Category B / 7.8 리포트 순서+Bear Case+온보딩 / 7.9 행동 생성 / 7.10 한국 신호 / 7.11 합성 알고리즘 / 7.11.1 가중치 자동 최적화 / 7.12 YAML 스키마)](#section-7)
- [Section 8: 데이터 스키마 계약 (8.1 UnifiedSignal — steeps_tags 다중 레이블)](#section-8)
- [Section 9: 기술 아키텍처 (9.6 네트워크 의존성 / 9.8 EnvironmentScan 자동화 갭 + envscan_bridge.sh)](#section-9)
- [Section 10: 구현 원칙 (7가지 비타협 원칙)](#section-10)
- [Section 11: 에러 복구 + 한국어 알림 명세 (11.6 MacBook 전원 꺼짐 침묵 실패 대비)](#section-11)
- [Section 12: 외부 연동](#section-12)
- [Section 13: 검증 프레임워크 (13.1 Naive Baseline / 13.3 KS + pause_weeks / 13.6 HITL 게이트)](#section-13)
- [Section 14: M2 백로그 (PRD 범위 밖)](#section-14)

**[두 독자 공통]**
- [Section 15: 한국 법적 컴플라이언스](#section-15)

---

<a id="section-0"></a>
## Section 0: 설치 전제 조건 (Prerequisites)

> **대상**: Claude Code — Day 0 설치 시작 전 반드시 이 섹션을 순서대로 확인한다.

### 0.1 하드웨어 / OS 요건

| 항목 | 최소 요건 | 권장 |
|------|---------|------|
| 기기 | MacBook M1 이상 | MacBook M3 이상 |
| RAM | 16GB | 32GB |
| macOS | Ventura 13.0 이상 | Sonoma 14.0 이상 |
| 저장 여유 공간 | 10GB | 50GB |

---

### 0.2 소프트웨어 전제 조건 체크리스트

Claude Code가 설치 시작 전 다음 항목을 순서대로 확인한다.

| 확인 항목 | 검증 명령 | 합격 기준 | 실패 시 조치 |
|----------|---------|---------|------------|
| Python 버전 | `python3 --version` | 3.11.0 이상 | `brew install python@3.11` |
| pip | `pip3 --version` | 설치됨 | `python3 -m ensurepip` |
| EnvironmentScan | `ls ~/path/to/envscan/database.json` | 파일 존재 | 사용자에게 EnvironmentScan 실행 안내 |
| GlobalNews | `ls ~/path/to/gnews/signals.parquet` | 파일 존재 | M0.5는 EnvScan만으로 진행 가능 (graceful) |
| 인터넷 연결 | `curl -s https://api.telegram.org` | HTTP 응답 200 | Telegram 봇 설정 전 필수 |

---

### 0.3 Python 패키지 (requirements.txt — M1 전체 기준)

```
# InvestScan requirements.txt
finance-datareader>=0.9.50    # 한국 주식 가격 + 외국인 수급
pandas>=2.0.0                 # 데이터 처리
pyarrow>=14.0.0               # Parquet 파일 읽기
jinja2>=3.1.0                 # 리포트 템플릿
requests>=2.31.0              # Telegram HTTP 발송
keyring>=24.0.0               # macOS Keychain 통합
fredapi>=0.5.0                # FRED 미국 경제 지표 (M1 포함)
dart-fss>=0.4.0               # DART 기업 실적 공시 (M1 포함)
pykrx>=1.0.35                 # 한국 주식 팩터 PER/PBR/ROE (M1 포함)
```

설치 명령: `pip3 install -r requirements.txt`

M0.5 최소 설치: `pip3 install finance-datareader pandas pyarrow jinja2 requests keyring`

---

### 0.4 EnvironmentScan 스키마 사전 확인 (normalizers.py 구현 전 필수)

`normalizers.py`를 작성하기 전에 실제 `database.json`의 필드 구조를 반드시 확인한다.

```bash
# Claude Code가 M0.5 구현 시작 전에 실행하는 명령
python3 -c "
import json
with open('PATH/database.json') as f:
    data = json.load(f)
record = data[0] if isinstance(data, list) else list(data.values())[0]
print('필드 목록:', list(record.keys()))
print('샘플 레코드:', record)
"
```

이 명령 출력 결과를 `normalizers.py`의 필드 매핑(`preliminary_category`, `psst_score` 등 실제 필드명)에 사용한다.
실제 필드명이 PRD의 예시와 다른 경우, 실제 필드명을 우선한다.

---

<a id="section-1"></a>
## Section 1: 이 시스템이 무엇인가

### 1.1 한 문장 정의 + 월요일 아침 시나리오

**한 문장 정의**

> InvestScan은 150+ 글로벌 소스를 매주 자동 분석하여, 비코더도 6분 안에 주간 투자 방향을 결정할 수 있는 Telegram 메시지를 생성하는 로컬 AI 인텔리전스 시스템이다.

---

**월요일 아침 시나리오**

> 2026년 5월 18일(월) 오전 10:45. 주일 예배를 마친 목사님이 Telegram을 열었다. 메시지가 와 있다.
>
> *"이번 주 반도체 긍정, 행동 1가지: ETF 비중 점검."*
>
> 6분 후 목사님은 결정을 내렸다. **시스템은 이 6분을 위해 존재한다.**

이 메시지 하나가 도달하기까지, 시스템은 일요일 저녁부터 이미 움직이고 있었다. 116개 뉴스 사이트를 14개 언어로 수집하고, 37개 AI 에이전트가 거시 신호를 분류하고, 섹터 방향을 판단하고, 신뢰도를 계산한 뒤 Telegram으로 전송한다. 목사님이 할 일은 메시지를 읽고 6분 안에 결정하는 것뿐이다.

---

### 1.2 제품 개요

| 항목 | 내용 |
|------|------|
| **제품명** | InvestScan — 한국시장 주간 투자방향 + 종목 관찰 AI 인텔리전스 |
| **핵심 자산** | EnvironmentScan (v2.5.0, 4 Workflow, 37 agents) + GlobalNews-Crawling (116 사이트, 14+ 언어) |
| **실행 환경** | 로컬 오케스트레이션 (MacBook M3 이상, 16GB+ RAM) — 분석 추론은 Claude API 활용 — **SaaS 절대 아님** |
| **최종 산출물** | 주간 Telegram 요약 메시지 + Markdown 상세 리포트 + 섹터별 종목 관찰 목록 |
| **개발자 프로필** | 비코더, 솔로, 파트타임 (주 2–4시간) |
| **구현 방식** | Claude Code가 workflow.md를 읽고 전체 시스템을 자동 구현 — 사용자는 코딩 불필요 |

---

### 1.3 시스템이 생산하는 것 (산출물)

**매주 월요일 — Telegram 5줄 요약**

주간 핵심을 5줄로 압축한 메시지. 섹터 방향 3개(긍정/중립/주의), 이번 주 행동 1가지, 신뢰도 퍼센트. 읽는 데 30초.

**매주 월요일 — 상세 Markdown 리포트**

Telegram 요약의 근거가 되는 전체 분석 문서. 각 섹터 방향 판단에 사용된 글로벌 신호 목록, 종목 관찰 워치리스트(매수/매도 판단 아님, 주목할 종목 목록), 이번 주 핵심 이벤트 요약. 읽는 데 2–3분.

**매월 — 예측 정확도 자가 검토 리포트**

지난 4주 동안 시스템이 내린 섹터 방향 예측이 실제 시장 흐름과 얼마나 일치했는지 자동 검토. 적중한 신호와 빗나간 신호를 함께 공개하며, 다음 달 신뢰도 가중치 조정 결과를 포함.

---

<a id="section-2"></a>
## Section 2: 왜 만드는가

### 2.1 해결하는 문제

현재 한국 투자 앱의 한계는 명확하다. AlphaSquare를 비롯한 대부분의 투자 정보 앱은 "어떤 종목을 살 것인가(What)"를 알려준다. 차트, 수급, 리포트 요약, 매수 신호. 이 정보들은 유용하지만, 한 가지 질문에 답하지 못한다.

**"왜 지금 이 섹터가 움직이는가?"**

반도체 ETF 비중을 늘려야 하는 이유가 단순히 "차트가 상향 돌파해서"인지, 아니면 "미국 AI 데이터센터 투자 확대 → TSMC 수주 증가 → 삼성/SK하이닉스 수혜 구조가 형성되고 있어서"인지 — 이 맥락의 차이가 판단의 확신을 결정한다.

InvestScan은 이 거시 맥락 레이어를 제공한다.

| 역할 | 도구 | 핵심 질문 |
|------|------|-----------|
| 종목 신호 | AlphaSquare 등 | **What** — 무엇을 살 것인가 |
| 거시 맥락 | InvestScan | **Why** — 왜 지금 그 섹터인가 |
| **완전한 판단** | **둘을 함께** | **What + Why = 확신 있는 결정** |

AlphaSquare는 InvestScan의 경쟁자가 아니다. InvestScan은 AlphaSquare 사용자가 "신호는 있는데 확신이 없을 때" 거시 맥락으로 판단을 보완하는 도구다.

---

### 2.2 핵심 차별점

**① 글로벌 소스 150+ (116 뉴스 사이트 + arXiv + 정책 문서), 14+ 언어 동시 처리**

한국 투자 판단에 영향을 주는 신호는 한국어 뉴스에만 있지 않다. 미국 연준 성명, 유럽 반도체 보조금 정책, 중국 기술 제재 업데이트, 일본 엔화 동향 — 이 신호들이 14개 언어로 동시에 수집된다. 한국어 뉴스만 읽는 사람이 놓치는 맥락이 자동으로 포함된다.

**② STEEPs 프레임워크로 거시 신호 → 섹터 방향 자동 연결**

수집된 신호는 STEEPs(사회·기술·경제·환경·정치·보안) 프레임워크로 분류된 뒤, 한국 시장 섹터(반도체, IT서비스, 바이오 등)와 자동 연결된다. "미국 AI 예산 확대"라는 신호가 "반도체 긍정"으로 연결되는 논리 경로가 리포트에 명시된다.

**③ 감성 분석 0% — 사실 기반 이벤트 + 토픽 트렌드만 사용**

"시장 심리 개선" 같은 감성 신호는 허위 상관을 생성한다. InvestScan은 감성 분석을 사용하지 않는다. 사실로 확인된 이벤트(정책 발표, 실적 공시, 수주 계약)와 토픽 트렌드(특정 키워드의 언급 빈도 변화)만 신호로 처리한다.

**④ 100% 로컬 실행 — 개인 투자 판단이 외부 서버에 전송되지 않음**

클라우드 SaaS 투자 도구를 사용할 때, 사용자의 관심 종목과 포트폴리오 패턴이 외부 서버에 저장된다. InvestScan은 MacBook에서만 실행된다. 투자 판단 과정이 외부로 나가지 않는다.

**⑤ 모든 결론에 근거 신호 번호 명시 — 블랙박스 없음**

"반도체 긍정 72%"라는 결론 옆에는 항상 "근거: 신호 #14(TSMC 수주 확대), #27(미국 CHIPS Act 예산 집행 확인), #31(삼성 HBM 공급 계약)"처럼 구체적 근거가 붙는다. 왜 그 결론이 나왔는지 2분 안에 확인할 수 있다.

---

<a id="section-3"></a>
## Section 3: 어떻게 사용하는가 (비코더 사용자 여정)

### 3.1 Day 0 설치 (2–4시간, Claude Code와 함께)

설치 과정에서 사용자가 직접 코드를 작성하거나 터미널 명령어를 외울 필요는 없다. Claude Code가 단계마다 정확히 무엇을 입력할지 안내한다. 사용자는 확인하고 진행만 하면 된다.

| 단계 | 작업 | 소요 시간 |
|------|------|-----------|
| **1단계** | Claude Code와 함께 GlobalNews 환경 설치 (AI 모델 다운로드 포함) | 30–60분 |
| **2단계** | EnvironmentScan 첫 실행 확인 (이미 운영 중인 기존 시스템) | 15분 |
| **3단계** | InvestScan 코어 설치 + Telegram 봇 연결 | 30분 |
| **4단계** | investscan.yaml 초기 설정 (Claude Code와 3–4가지 대화로 수행) | 30분 |

**investscan.yaml 초기 설정이란?**
관심 섹터(반도체, 바이오, IT서비스 등), Telegram 봇 토큰, 리포트 수신 시각(기본값: 월요일 08:00) 등 3–4가지 개인 설정을 Claude Code와 대화하며 결정하는 과정이다. 코드 편집이 아니라 "반도체와 바이오를 주로 보고 싶어요"라고 말하면 Claude Code가 설정 파일을 자동으로 수정한다.

**Day 0 인터랙티브 설정 질문 (Claude Code가 순서대로 진행)**

| 순서 | Claude Code의 질문 | 유효 입력 | 기본값 | 저장 위치 |
|------|------------------|---------|--------|---------|
| 1 | "관심 섹터를 2–5개 말씀해주세요" | 반도체·바이오·IT서비스·금융·에너지·방산·소비재 중 선택 | 반도체·IT서비스·바이오 | `user.sectors_of_interest` |
| 2 | "Telegram 봇 토큰을 입력해주세요 (BotFather에서 발급)" | `숫자:문자열` 형식 | 없음 (필수) | macOS Keychain |
| 3 | "주간 리포트 수신 시각은? (예: 08:00)" | HH:MM 형식 | 08:00 | `user.report_delivery_time` |
| 4 | "투자 성향은? (conservative / balanced / aggressive)" | 3가지 중 선택 | conservative | `user.investment_style` |

**Telegram BotFather 봇 생성 (처음 사용자):**
1. Telegram 앱에서 `@BotFather` 검색 → 대화 시작
2. `/newbot` 입력
3. 봇 이름 입력 (예: `InvestScan`)
4. 봇 사용자명 입력 (`_bot`으로 끝나야 함, 예: `my_investscan_bot`)
5. BotFather가 발급하는 토큰(`1234567890:AAF...` 형식)을 복사하여 Claude Code에 전달

**Day 0 오류 발생 시**: 터미널에 표시된 오류 메시지를 Claude Code에 그대로 붙여넣으면 된다. 코드 이해 없이도 Claude Code가 원인 분석과 해결 방법을 단계별로 안내한다.

---

### 3.1.1 설치 후 첫 2주: 침묵 기간 안내

Day 0 설치 완료 후 첫 Telegram 메시지를 받기까지 최대 **2주**가 걸릴 수 있다.

| 기간 | 상태 | 이유 |
|------|------|------|
| Day 0 설치 완료 후 | 시스템 구축 중 | Claude Code가 M0.5 코드를 자동 작성하는 시간 |
| Week 1 (첫 일요일) | 첫 실행 시도 | 처음 실행 시 소규모 오류 수정 가능 |
| Week 2 (두 번째 일요일) | 첫 Telegram 메시지 수신 목표 | M0.5 Done Gate 통과 기준 |

**이 침묵 기간은 정상이다.** 시스템이 멈춘 것이 아니라 Claude Code가 코드를 완성하고 있는 것이다. Day 0 이후 Claude Code와의 대화를 계속 유지하면 Week 2 안에 첫 메시지를 받을 수 있다.

---

### 3.2 Week 2: 첫 Telegram 메시지 (M0.5 완료 기준)

M0.5는 첫 번째 작동 단계다. 전체 시스템(M1)이 완성되기 전에도, Week 2에 첫 주간 요약 메시지를 수신할 수 있다.

M0.5 완료 시 수신 가능한 메시지 형식:

```
반도체 긍정 / IT 중립 / 바이오 주의
행동 1가지: ETF 비중 점검
신뢰도: 71%
```

이 단계에서 상세 리포트는 아직 간략하지만, 핵심 방향과 행동 1가지는 정확히 전달된다. "시스템이 실제로 작동한다"는 것을 Week 2 안에 확인할 수 있다.

---

### 3.3 주간 루틴 (첫 4주: 약 20분 → 이후: 6분)

M1 완성 후 매주 반복되는 루틴이다. **처음 4주는 약 20분**이 소요된다 — 리포트 구조와 신호 해석에 익숙해지는 시간이다. 4주 후 패턴이 익숙해지면 6분으로 단축된다. 6분이 목표다.

| 순서 | 행동 | 시간 |
|------|------|------|
| 1 | Telegram 핵심 요약 읽기 (섹터 방향 3개 + 행동 1가지) | 30초 |
| 2 | 상향된 섹터 1개 → 상세 리포트에서 근거 신호 2–3건 확인 | 2분 |
| 3 | "이번 주 행동 체크리스트" 확인 | 1분 |
| 4 | 내 포트폴리오와 대조하여 1가지 결정 | 1분 |
| 5 | 결정 근거 Telegram 답장 → 자동 저장 (결정 저널 누적) | 30초 |

---

### 3.4 첫 번째 월요일 아침 6분 시뮬레이션

**2026년 5월 18일(월), 10:45–10:51**

**10:45 — Telegram 열기 (30초)**

```
📊 InvestScan 주간 리포트 (5/18)
신뢰도: 78% | 데이터: EnvScan✅ GlobalNews✅

이번 주 행동 1가지:
→ 반도체 ETF 비중 5% 이상이면 현행 유지 확인

방향 요약:
• 반도체: 🟢 긍정 (72%)
• IT서비스: ⚪ 중립 (58%)
• 바이오: 🔴 주의 (34%)

상세 보고서: /reports/2026-05-18.md
```

**10:46–10:48 — 상세 리포트 근거 확인 (2분)**

```
## 반도체 섹터: 🟢 긍정 (72%)

근거 신호 (상위 3건):
  #14 TSMC 2026 Q2 수주량 전분기 대비 +18% 확인 (출처: DigiTimes, 5/15)
  #27 미국 CHIPS Act 2차 보조금 집행 확정 발표 (출처: Commerce Dept, 5/14)
  #31 SK하이닉스 HBM4 공급 계약 3건 추가 확인 (출처: 전자신문, 5/16)

방향성 타임프레임: 이 신호는 4–12주 방향성 (단기 등락 예측 아님)

종목 관찰 워치리스트:
  • 삼성전자 — HBM 수혜 구조, 신호 강도 ★★★
  • SK하이닉스 — HBM4 계약 직접 수혜, 신호 강도 ★★★★
  • KODEX 반도체 ETF — 섹터 방향 플레이, 신호 강도 ★★★
```

**10:48–10:49 — 이번 주 행동 체크리스트 확인 (1분)**

```
이번 주 행동 체크리스트:
  ☐ 현재 반도체 ETF 비중 확인 (목표: 5% 이상이면 현행 유지)
  ☐ SK하이닉스 최근 2주 주가 흐름 AlphaSquare에서 확인
  ☐ 바이오 섹터 보유 종목 있다면 비중 점검 (주의 신호)
```

**10:49–10:50 — 포트폴리오 대조 후 결정 (1분)**

현재 반도체 ETF 비중 3%. 행동 기준은 5% 이상 시 현행 유지. 즉 지금은 비중 확대 검토 대상.

결정: "반도체 ETF 2% 추가 매수 검토. 이번 주 중 AlphaSquare에서 매수 타이밍 확인."

**10:50–10:51 — 결정 저장 (30초)**

```
결정: 반도체 ETF +2% 검토. AlphaSquare 타이밍 확인 예정.
근거: InvestScan 반도체 긍정 72% + HBM 수혜 구조

✅ 결정 저널 저장 완료 (#23)
다음 검토: 4주 후 예측 정확도 리포트에서 확인 가능
```

**10:51 — 완료.** 6분. 다음 결정까지 7일.

---

### 3.5 EnvScan 실행 절차 (일요일 저녁, 5단계)

| 단계 | 행동 | 비고 |
|------|------|------|
| **1** | EnvironmentScan 터미널에서 실행 명령 입력 | `실행방법.txt` 파일에 명령어 저장됨 (설치 시 자동 생성) |
| **2** | 약 120분 대기 (완료 시 Telegram 알림 자동 수신) | MacBook 전원 어댑터 연결 + 덮개 열어두기 필수 |
| **3** | database.json 생성 확인 (Telegram 알림에 포함) | 파일 직접 열 필요 없음 |
| **4** | InvestScan 파이프라인 자동 시작 | launchd 설정 시 단계 1–4 완전 자동 |
| **5** | 월요일 아침 08:00 Telegram 메시지 수신 | |

**launchd 자동화 설정 후 일요일 루틴:** 저녁 9시에 MacBook 덮개를 닫지 않고 전원을 연결해두는 것이 전부다. 나머지는 시스템이 처리한다.

**실행방법.txt**: Claude Code가 Day 0 설치 완료 시 자동 생성하는 파일. 수동 실행 명령어, Telegram 봇 확인 방법, 오류 시 대응 방법 3가지를 담는다. 이 파일만 있으면 언제든 1분 안에 수동 실행할 수 있다.

⚠️ **macOS 업데이트 후**: macOS 메이저 업데이트 이후 launchd 에이전트가 비활성화될 수 있다. 업데이트 직후 첫 월요일에 Telegram 메시지를 수신하지 못하면 Claude Code에게 "launchd 확인해줘"라고 요청하면 된다.

---

### 3.6 3개월 후 유지보수 체크리스트 (연 1회, Claude Code와 함께)

| 점검 항목 | 내용 | 예상 소요 |
|-----------|------|-----------|
| EnvironmentScan 스키마 변경 확인 | EnvScan 업데이트로 database.json 구조가 바뀌었는지 확인 | 15분 |
| GlobalNews 수집 사이트 변경 확인 | 116개 사이트 중 폐쇄·이전된 사이트 업데이트 | 15분 |
| Claude API 가격 변경 검토 | 비용 구조 변동 여부 확인 | 5분 |
| investscan.yaml 설정 갱신 | 관심 섹터 추가·삭제, 알림 시각 변경 등 | 10분 |

Claude Code에게 "InvestScan 연간 점검해줘"라고 말하면 위 4가지를 순서대로 안내한다.

---

<a id="section-4"></a>
## Section 4: 성공 기준

### 4.1 한 줄 정의

> "월요일 아침 6분 안에 이번 주 투자 방향을 결정할 수 있는가?"

| 시스템이 보장하는 것 | 사용자가 해야 하는 것 |
|---|---|
| 주간 리포트 자동 생성 (일요일 → 월요일 08:00) | 월요일 아침 6분 루틴 실행 |
| 섹터 방향 3개 + 행동 1가지 제공 | 결정 저널 기록 (Telegram 답장) |
| 월간 정확도 리포트 자동 생성 | 월 1회 정확도 확인 + 피드백 |
| 파이프라인 실패 시 즉시 알림 | — |

---

### 4.2 Month 2 Kill Switch

다음 3가지 중 1가지라도 충족되면 시스템 지속 여부를 진지하게 재검토한다.

| Kill Switch | 기준 | 측정 방법 |
|-------------|------|-----------|
| **KS-1 정량** | 섹터 방향 적중률 < 40% (누적 **8회** 이상) | 월간 정확도 리포트 자동 집계 |
| **KS-2 정성** | "이 리포트가 도움이 됐나요? (1-5점)" 평균 < 2.5/5 (4주 연속) | 리포트 발송 직후 Telegram 자동 질문 |
| **KS-3 기술** | 파이프라인 완전 실패 3회 연속 (Telegram 미수신) | 시스템 자동 에러 로그 |

▶ Kill Switch 상세 기준 + SOT: **Section 13.3** 참조

---

### 4.3 Month 6 목표

| 목표 | 기준값 |
|------|--------|
| 섹터 방향 적중률 | ≥ 55% |
| 주간 루틴 연속 실행 | 12회 연속 (읽기 + 결정 저널 작성) |
| 결정 저널 누적 건수 | 15건 이상 |
| 주관 유용성 평점 | 평균 ≥ 3.5/5 |

---

### 4.4 3가지 실패 시나리오와 예방

**실패 A: "만들었지만 안 쓴다"**

*원인:* 리포트가 결정과 연결되지 않는다. 읽어도 행동이 달라지지 않는다.

*예방:* 리포트의 가장 첫 줄은 반드시 "이번 주 행동 1가지: [구체적 행동]"으로 시작한다. 1가지 행동만 읽어도 루틴을 완료할 수 있는 구조를 유지한다.

**실패 B: "4주 후 무음 실패"**

*원인:* launchd 실패를 4주 후에야 발견한다. 시스템이 실패해도 침묵한다.

*예방:* 월요일 08:00에는 리포트 유무와 관계없이 반드시 알림이 전송된다. 실패했으면 "⚠️ 이번 주 리포트 생성 실패. 원인: EnvScan 미완료. 지난주 리포트 참고 권장."이 온다. 침묵은 없다.

**실패 C: "6개월 후 신뢰 붕괴"**

*원인:* 단기 편차(4주 하락)와 구조적 추세(4-12주 방향)를 구분하지 못한다.

*예방:* 모든 방향 판단 옆에 타임프레임이 명시된다. "이 신호는 4–12주 방향성 (단기 등락 예측 아님)." 월간 정확도 리포트에서 틀린 예측을 숨기지 않고 명시한다.

**실패 D: "리포트 항상 긍정 고착"**

*원인:* 시스템이 긍정 신호만 반복 출력하고, 하방 리스크를 구조적으로 과소평가한다.

*예방:* 리포트 발송 전 자가검증에서 "하방 리스크 신호 1개 이상 포함" 항목을 의무 충족 조건으로 설정한다. 3주 연속 전 섹터 Bullish 출력 시 Telegram 경고 자동 발송: "⚠️ 3주 연속 전 섹터 긍정 신호 감지. 하방 리스크를 재검토하세요."

---

### 4.5 자가 검증 가이드 (첫 리포트 수신 시 2분)

"반도체 🟢 긍정 (72%)"를 받았다면:

1. 상세 리포트에서 "근거 신호 상위 3건" 확인 (30초)
2. 각 신호의 출처 이름 확인 — 알려진 미디어/공식 기관인지 (30초)
3. 신뢰도 72%가 납득 가능한 수준인지 주관적으로 평가 (1분)
   - 납득 가능: 이번 주 루틴 진행
   - 납득 불가: Telegram에 "반도체 신뢰도 근거 더 보여줘" 답장 → 시스템이 추가 신호 목록 전송

---

### 4.6 시스템이 틀렸을 때 메시지 (월간 정확도 리포트)

```
📋 지난달 예측 검토 (2026년 4월)

• 반도체 Bullish → 실제 +3.2% ✅ (맞음)
• IT서비스 Bearish → 실제 +0.8% ❌ (틀림)
  분석: IT 섹터 상향 요인 과소평가. 국내 클라우드 수요 신호 미반영.

• 바이오 Neutral → 실제 -1.1% ✅ (방향 일치)

이번 달 조정:
  IT 서비스 신호 가중치 -5% (과소평가 보정)

누적 적중률 (10회): 반도체 70% | IT 50% | 바이오 60%
```

---

<a id="section-5"></a>
## Section 5: 비용과 시간

### 5.1 실제 비용 (투명 공개)

| 항목 | 월간 비용 | 비고 |
|------|-----------|------|
| Claude Max | $200/월 (한화 약 28만원) | MVP 운영 권장 플랜 |
| GlobalNews 수집 | $0 | 자체 구축, 외부 API 없음 |
| EnvironmentScan | $0 | Claude API 포함 |
| pykrx / FDR | $0 | 오픈소스 |
| Telegram 봇 | $0 | 공식 무료 API |
| **총 월간 비용** | **$200/월 (약 28만원)** | 추가 숨은 비용 없음 |

**Claude Max $200/월이 전부다.** Claude Code 전체 사용료 안에 InvestScan 운영이 포함된다.

> **현재 Claude Max를 이미 구독 중이라면 추가 비용 없음.** InvestScan 구축과 운영에 드는 Claude Code 사용료는 기존 Claude Max 구독에 포함된다.

---

### 5.2 실제 시간

| 단계 | 사용자 시간 | 내용 |
|------|------------|------|
| **Day 0 설치** | 2–4시간 | Claude Code와 함께 설치 + 초기 설정 |
| **M0.5 개발 (Week 1–2)** | 1–2시간 | Claude Code 자동 구현, 사용자는 확인만 |
| **M1 개발 (Week 3–8)** | 3–5시간 | Claude Code 자동 구현, 사용자는 확인만 |
| **M1 이후 주간 루틴** | **6분/주** | Telegram 읽기 + 결정 저널 |
| **유지보수** | 1–2시간/연 | Claude Code와 함께 연 1회 점검 |

---

### 5.3 AlphaSquare와의 관계

| 도구 | 역할 | 핵심 질문 |
|------|------|-----------|
| AlphaSquare | 종목 신호, 차트, 수급 분석 | **What** — 무엇을 살 것인가 |
| InvestScan | 거시 맥락, 섹터 방향, 글로벌 신호 | **Why** — 왜 지금 그 섹터인가 |

**실제 사용 흐름:** InvestScan에서 "반도체 긍정 72%" 수신 → AlphaSquare에서 SK하이닉스 매수 타이밍 차트 확인 → InvestScan 맥락 + AlphaSquare 신호 = 확신 있는 결정

---

<a id="section-6"></a>
## Section 6: M0.5 구현 명세

### 6.1 M0.5 정의

| 항목 | 내용 |
|------|------|
| 목적 | Week 2에 첫 Telegram 메시지 수신 — 즉각적 가치 검증 |
| 입력 | EnvironmentScan `database.json` (WF1, 이미 운영 중) |
| 처리 | STEEPs 신호 집계 → 섹터 방향 합성 |
| 출력 | Telegram 5줄 요약 |
| 목표 LOC | ~400 |

M0.5는 완전한 파이프라인이 아닌 **가치 검증 스파이크**다. GlobalNews, 한국 신호 레이어, 워치리스트는 M0.5 범위 밖이다.

---

### 6.2 M0.5 모듈 목록

| 모듈 | LOC | 역할 |
|------|-----|------|
| `config.py` | ~50 | `investscan.yaml` 로드 + 실제 파일 경로 관리 |
| `schema.py` | ~80 | `UnifiedSignal` frozen dataclass 정의 |
| `normalizers.py` (WF1만) | ~150 | EnvScan WF1 `database.json` → `UnifiedSignal` 변환 |
| `synthesize.py` (단순) | ~80 | STEEPs 집계 → 섹터 방향 (Bullish/Neutral/Bearish) |
| `telegram_notifier.py` | ~40 | 5줄 요약 Telegram 발송 |
| **합계** | **~400** | |

구현 순서: `config → schema → normalizers → synthesize → telegram_notifier`

---

### 6.3 M0.5 Done Gate

> "EnvironmentScan `database.json`을 입력받아 Telegram으로 '이번 주 반도체 긍정, IT 중립, 바이오 주의 | 행동 1가지' 메시지를 발송한다."

| 검증 항목 | 방법 |
|----------|------|
| Telegram 채널에서 메시지 수신 확인 | 실제 채널에서 육안 확인 |
| 섹터 방향 3개 이상 포함 | 메시지 파싱 확인 |
| 행동 지침 1가지 포함 | 메시지 내용 확인 |
| `database.json` 없을 때 명시적 에러 | 파일 제거 후 실행 |
| `database.json` 신선도 | 파일 수정 시각이 7일 이내 | `os.path.getmtime()` 확인 |
| 신뢰도 점수 유효 범위 | 0%–100% 사이 | `assert 0 <= confidence <= 100` |
| 신호 출처 비어있지 않음 | `source` 필드 ≥ 1건 | 파싱 후 `len > 0` 확인 |

---

### 6.4a M0.5 실패 복구 프로토콜

| 실패 유형 | 진단 방법 | 해결 방법 |
|---------|---------|---------|
| Telegram 인증 실패 (401) | 토큰 형식 `숫자:문자` 확인 | Keychain에서 토큰 삭제 후 재저장: `keyring.set_password(...)` |
| `database.json` 파싱 실패 | Section 0.4 스키마 확인 명령 실행 | `normalizers.py` 필드 매핑 수정 (실제 필드명 반영) |
| 신호 0건 추출 | database.json 내용 육안 확인 | EnvironmentScan 재실행 요청 |
| 전 섹터 동일 방향 (100% Bullish 등) | `synthesize.py` 가중치·입력값 확인 | 입력 신호 품질 점검 + 임계값 조정 |
| Week 2 초과 미완료 | 에러 로그 전체 확인 | Claude Code에게 에러 로그 전달 → 수동 디버그 세션 |

**자동 재시도 예산:** 동일 실패 유형 최대 2회. 3회 후 실패 시 Telegram 알림 (실패하면 이메일 확인이나 Claude Code에게 로그 전달).

**롤백 절차:** `normalizers.py` 또는 `synthesize.py`에서 `ImportError`가 3회 이상 발생하면, 해당 파일을 `.bak`으로 백업 후 Section 6.2 모듈 명세에서 처음부터 재작성.

---

### 6.5 M0.5 실행 방법

```
python run_m05.py --input ~/path/to/envscan/database.json
```

- `--input` 경로: CLI 인자 또는 `investscan.yaml`의 `envscan.wf1_output_path`에서 로드
- CLI 인자 우선, 없으면 YAML 경로 사용
- 경로가 둘 다 없으면 즉시 에러 출력 후 종료 (묵음 실패 금지)
- `investscan.yaml` 기본 위치: `~/.investscan/investscan.yaml`

---

<a id="section-7"></a>
## Section 7: M1 구현 명세

### 7.1 M1 정의

| 항목 | 내용 |
|------|------|
| 목적 | GlobalNews 통합 + 한국 시장 독립 신호 + 종목 관찰 워치리스트 포함 상세 리포트 |
| 입력 | EnvironmentScan 6가지 포맷 + GlobalNews `signals.parquet` |
| 출력 | Telegram 요약 + Markdown 상세 리포트 + 종목 관찰 워치리스트 |
| 목표 LOC | **~2,200** (버퍼 15% 포함) |
| Done Gate | "종목 워치리스트가 포함된 주간 Markdown 리포트 자동 생성" |

---

### 7.2 M1 모듈 목록

| 모듈 | LOC | 역할 | 우선순위 |
|------|-----|------|---------|
| `config.py` | ~100 | 실제 경로 하드코딩, YAML 로드 | M0.5 확장 |
| `schema.py` | ~110 | `UnifiedSignal` + `StockRecommendation` frozen dataclass | M0.5 확장 |
| `normalizers.py` | ~300 | **M1 최우선 모듈** — 6가지 포맷 파서 | 최우선 |
| `dedup.py` | ~150 | content-hash 기반 중복 신호 제거 | 높음 |
| `steeps_classifier.py` | ~200 | STEEPs 재분류 (규칙 기반) | 높음 |
| `signal_bridge.py` | ~200 | STEEPs 신호 → GICS 11 섹터 매핑 | 높음 |
| `synthesize.py` | ~200 | 섹터 방향 합성 (감성 가중치 0%) | M0.5 확장 |
| `report_generator.py` | ~200 | Jinja2 한국어 Markdown 리포트 | 높음 |
| `weekly_orchestrator.py` | ~150 | 파이프라인 순서 제어 + 체크포인트 | 높음 |
| `telegram_notifier.py` | ~100 | 요약 메시지 발송 (단방향) | M0.5 확장 |
| `personalizer.py` (P0/P1) | ~200 | `investscan.yaml` 설정 + macOS Keychain | 중간 |
| `accuracy_tracker.py` | ~150 | 경로 A — 예측 기록 + 월간 정확도 리포트 | 중간 |
| `korea_signal_layer.py` | ~150 | 한국 독립 신호 (외국인 수급, 환율, 정책) | 높음 |
| `health_dashboard.py` | ~50 | `weekly_dashboard.html` 자동 생성 | 낮음 |
| `watchdog.py` | ~50 | 월요일 08:00 강제 알림 (리포트 유무 무관) | **높음** |
| **합계** | **~2,200** | | |

`normalizers.py`는 M1 전체의 입구다. 이 모듈이 완성되지 않으면 이후 모든 모듈이 실데이터 없이 동작한다.

`watchdog.py`는 침묵 실패(실패 B) 예방의 핵심이다. 리포트 생성 성공 여부와 무관하게 월요일 08:00에 반드시 Telegram 알림을 발송한다. 성공이면 리포트 링크, 실패이면 원인 1줄 + 행동 지침 1가지.

---

### 7.3 normalizers.py 포맷 지원 순서

| 단계 | 지원 포맷 수 | 포함 포맷 |
|------|------------|---------|
| Phase 1-2 | 2 | WF1 `database.json` + GlobalNews `signals.parquet` |
| Phase 3-4 | 3 | + WF4 priority-ranked |
| M2 | 6 | + 나머지 3 포맷 |

---

### 7.4 신호 통합 원칙 (SIGNAL_WEIGHT_POLICY)

| 신호 유형 | 가중치 | 근거 |
|----------|--------|------|
| `steeps_event` (STEEPs 사실 기반 이벤트) | **70%** | 실제 발생한 사건, 허위 상관 최소 |
| `topic_trend` (뉴스 토픽 빈도 트렌드) | **20%** | 방향성 압력 반영 |
| `sentiment` (감성 분석) | **0%** | 허위 상관 90-95% 차단 — P1 원칙 |
| `factor_score` (팩터 스코어) | **10%** | 정량 팩터 보완 |

`sentiment` 0%는 구현 선택이 아닌 **원칙 P1**이다. Claude Code는 이 값을 수정하지 않는다.

---

### 7.5 섹터 방향 출력 형식 (3단계)

| 방향 | 이모지 | 신뢰도 기준 | 리포트 표기 |
|------|-------|-----------|-----------|
| Bullish (긍정) | 🟢 | ≥ 65% | `🟢 긍정 (신뢰도 XX%)` |
| Neutral (중립) | ⚪ | 45% 이상 65% 미만 | `⚪ 중립 (신뢰도 XX%)` |
| Bearish (주의) | 🔴 | < 45% | `🔴 주의 (신뢰도 XX%)` |

---

### 7.6 종목 관찰 워치리스트 형식

워치리스트는 두 카테고리로 **구분 출력**한다 (핵심 목적 — 안정적 현재 종목 vs 미래 성장 테마 구분):

**카테고리 A: 안정적 관찰 종목** (현재 섹터 신호 기반, 4–12주 방향)
```
[SK하이닉스 000660 — 안정적 관찰]
근거 신호: 글로벌 반도체 수요 회복 (신호 1), 외국인 수급 순매수 (신호 3)
섹터 방향 신뢰도: 68%
하방 리스크: HBM 공급 과잉 우려 (신호 9, 강도 낮음)
⚠️ 이 목록은 투자 권고가 아닌 데이터 기반 관찰 목록입니다.
```

**카테고리 B: 미래 성장 테마 종목** (신흥 STEEPs 신호 기반, 12–24주 테마)
```
[에코프로비엠 247540 — 테마 관찰]
테마: 유럽 배터리 공급망 재편
근거 신호: EU 핵심원자재법 시행 확정 (신호 15), 국내 배터리 소재 수주 급증 (신호 18)
테마 신뢰도: 61%
하방 리스크: 중국 LFP 배터리 경쟁 심화 (신호 22, 강도 중간)
⚠️ 이 목록은 투자 권고가 아닌 데이터 기반 관찰 목록입니다.
```

**카테고리 B "신흥 테마" 식별 알고리즘 (steeps_classifier.py + synthesize.py 연동):**

```python
# 신흥 테마 식별 pseudo-code
for topic in topic_trends:
    current_week_count = topic.signal_count_this_week
    avg_4week_count = topic.avg_signal_count_past_4_weeks or 1  # 0 나눗셈 방지

    if current_week_count >= avg_4week_count * 2.0:   # 4주 평균 대비 200% 급증
        if topic.steeps_category in ['T', 'E_env', 'P']:  # 성장 테마 카테고리
            theme_confidence = min(
                current_week_count / (avg_4week_count * 3.0), 1.0
            )
            if theme_confidence >= 0.55:
                add_to_category_b(topic, theme_confidence)

# 카테고리 B 유지·제거 정책
for theme in category_b_themes:
    if theme.consecutive_below_55 >= 4:     # 4주 연속 55% 미만 → 자동 제거
        remove_from_category_b(theme)
    elif theme.weeks_in_category_b >= 24:   # 24주 최대 유지 → M2 아카이브
        archive_to_m2_themes(theme)
```

**종목 수량 제한 (6분 루틴 유지 필수):**
- 카테고리 A: 최대 **5종목** (섹터 방향 신뢰도 내림차순 정렬)
- 카테고리 B: 최대 **3종목** (테마 신뢰도 내림차순 정렬)
- 초과 종목은 `data/watchlist_candidates.jsonl`에 저장 (리포트 미포함)

**섹터 → 종목 선정 로직 (`signal_bridge.py` + `config/sector_stock_map.yaml`):**

```python
# 섹터에서 종목 선정 pseudo-code
def select_stocks_for_sector(sector: str, direction: str) -> list[Stock]:
    # 사전 정의 매핑 테이블 (Claude Code가 Day 0에 기본값으로 생성)
    candidates = SECTOR_STOCK_MAP[sector]  # 예: "반도체" → [삼성전자, SK하이닉스, 한미반도체]

    # FDR에서 최근 4주 외국인 순매수 순위 가져오기
    foreign_flow = fdr.DataReader('KRX/FOREIGNER', start=four_weeks_ago)

    # 외국인 수급 강도로 정렬 → 상위 5개 반환
    ranked = sorted(candidates, key=lambda s: foreign_flow.get(s.code, 0), reverse=True)
    return ranked[:5]
```

`config/sector_stock_map.yaml`은 Day 0 설치 시 기본 섹터-종목 매핑으로 자동 생성.
사용자가 "바이오 종목에 셀트리온 추가해줘"라고 말하면 Claude Code가 이 파일을 수정.

워치리스트 공통 규칙:
- 근거 신호 반드시 2개 이상 명시 (P4 원칙)
- **하방 리스크 신호 1개 이상 필수** (미충족 시 리포트 발송 차단 — 7/7 자가검증)
- 카테고리 A: 섹터 방향 신뢰도 ≥ 65% 종목만 포함
- 카테고리 B: 테마 신뢰도 ≥ 55% 종목만 포함 (신흥 테마 특성 반영)
- 면책 문구는 모든 종목 블록에 반복 출력 (생략 불가)
- 투자 권고 언어(`매수`, `매도`, `목표가`) 절대 사용 금지

---

### 7.7 M1 구현 단계

| 단계 | 기간 | 내용 | Done Gate |
|------|------|------|---------|
| Phase 1 | Week 1 | M0.5 완료 | Telegram 5줄 발송 확인 |
| Phase 2 | Week 2-3 | GlobalNews 통합 + normalizers 2포맷 | WF1 + Parquet 정상 파싱 |
| Phase 3 | Week 4-5 | korea_signal_layer + synthesize 확장 | 한국 신호 포함 섹터 방향 출력 |
| Phase 4 | Week 6-7 | report_generator + 워치리스트 | 상세 Markdown 리포트 파일 생성 |
| Phase 5 | Week 8 | launchd + health_dashboard | 완전 자동화 실행 |

각 Phase Done Gate를 통과하지 못하면 다음 Phase로 진행하지 않는다.

---

### 7.8 리포트 섹션 고정 순서

리포트 내 섹션 순서는 **고정**이다. Claude Code는 이 순서를 변경하지 않는다.

```
1.  [필수] 분석 타임프레임 안내 (Section 10.3 문구 그대로)
2.  [필수] 이번 주 행동 1가지 (최우선 노출)
3.  [필수] 섹터 방향 요약 (Telegram 5줄 요약 내용)
4.  [필수] 섹터별 상세 분석 (근거 신호 + 출처 + 인과 논리 체인 2단계)
5.  [필수] Bear Case — 방향 반전 시나리오 (상위 1–2개 섹터 대상)
6.  [필수] 종목 관찰 워치리스트 — 카테고리 A (안정적 관찰, 최대 5종목)
7.  [필수] 종목 관찰 워치리스트 — 카테고리 B (미래 성장 테마, 최대 3종목)
8.  [필수] 이번 주 행동 체크리스트
9.  [조건부] 경고 — 전 섹터 동일 방향 3주 연속 시만 출력
10. [필수] 면책 조항 (Section 15.3)
```

**Bear Case 섹션 출력 형식 (5번 섹션):**

```
## Bear Case: 반도체 방향 반전 시나리오

현재 방향(긍정 72%)이 틀렸을 때 가장 가능성 높은 시나리오:
→ 미국–중국 반도체 제재 확대 시 삼성·SK 수출 제한 리스크 (신호 #22)
→ 글로벌 AI 투자 사이클 조기 종료 징후 포착 시 HBM 수요 급감 가능성 (신호 #31)

⚠️ 이 시나리오는 현재 방향의 반대 가능성입니다. 투자 결정 전 확인하세요.
```

인과 논리 체인 출력 예시 (4번 섹션):
```
근거 체인: CHIPS Act 예산 집행 확정 (신호 #27)
  → TSMC 미국 공장 수주 확대 (신호 #14, +18%)
  → SK하이닉스 HBM4 공급 계약 3건 추가 (신호 #31)
  → 반도체 섹터 긍정 72% 판정
```

**온보딩 모드 리포트 동작 (`onboarding_mode: true` 시):**

`investscan.yaml`에서 `onboarding_mode: true`이면 리포트 내 전문 용어에 괄호 설명을 자동 삽입한다. 기본값 `true`, 4주 후 사용자 확인 후 `false`로 전환 권장.

```
# onboarding_mode: true 시 출력 예시
반도체 섹터: 🟢 긍정 (72%)

근거 신호:
  #14 TSMC(대만 반도체 제조 기업) 수주량 +18% 확인
  #27 CHIPS Act(미국 반도체 지원법) 예산 집행 확정
  #31 HBM(High Bandwidth Memory: 고대역폭 메모리) 공급 계약 3건 추가

섹터 방향: Bullish(강세, 상승 기대) → 긍정 판정

# onboarding_mode: false 시 출력 예시
반도체 섹터: 🟢 긍정 (72%)
  #14 TSMC 수주량 +18% | #27 CHIPS Act 집행 확정 | #31 HBM 계약 3건
```

> **전환 Telegram 알림 (4주 후 자동):** `"처음 4주가 지났습니다. 용어 설명을 없애고 간결한 리포트로 전환할까요? (예 / 아니오)"`

---

### 7.9 "이번 주 행동 1가지" 생성 로직

행동 지침은 **규칙 기반**으로 자동 생성한다. AI 자유 생성 금지.

```python
# 행동 생성 우선순위 (pseudo-code)
if sectors with Bullish ≥ 1:
    top_sector = max(bullish_sectors, key=confidence)
    action = f"{top_sector.name} ETF 비중 확인 (현재 {top_sector.confidence}% 긍정)"
elif sectors with Bearish ≥ 2:
    action = "방어 포지션 점검 — 하방 리스크 섹터 비중 재확인"
else:  # all Neutral
    action = "관망 유지 — 다음 주 방향성 신호 확인 후 결정"
```

행동 지침 형식: `{섹터명} ETF 비중 {숫자}% 이상이면 현행 유지 확인` (구체적 행동 1개만)

---

### 7.10 korea_signal_layer.py 데이터 소스

| 신호 유형 | 소스 | 방법 |
|---------|------|------|
| 외국인 수급 (순매수/순매도) | FinanceDataReader (FDR) | `fdr.DataReader('KRX/ETF', start)` |
| 환율 (USD/KRW, JPY/KRW) | FDR | `fdr.DataReader('USD/KRW', start)` |
| 정책 신호 (금리, 정부 예산) | EnvironmentScan `P/s` 카테고리 필터 | `database.json` P·s 필드 추출 |

글로벌 신호는 P7 원칙에 따라 이 레이어를 반드시 통과한 후 섹터 방향에 반영된다.

---

### 7.11 M0.5 synthesize.py 집계 알고리즘

```python
# 섹터 방향 합성 (pseudo-code)
weighted_score = (
    steeps_event_score * 0.70 +   # P1: 감성 0%
    topic_trend_score  * 0.20 +
    factor_score       * 0.10
)

if weighted_score >= 0.65:   direction = Bullish
elif weighted_score >= 0.45: direction = Neutral
else:                         direction = Bearish

confidence = round(weighted_score * 100, 1)  # 예: 72.3%
source_count = len(signals_used)              # CP7: 명시적 소스 수 기록
```

`sentiment` 가중치는 항상 0.0이다. 이 값을 변경하는 코드 라인은 P1 위반이다.

---

### 7.11.1 가중치 자동 최적화 명세 (M1 accuracy_tracker 연동)

초기 가중치 (`steeps_event: 0.70 / topic_trend: 0.20 / factor_score: 0.10`)는 고정 출발값이다. M1 운영 이후 `accuracy_tracker.py`가 수집한 데이터를 기반으로 **월 1회** 가중치 조정 제안을 생성한다.

**조정 알고리즘 (pseudo-code):**

```python
# accuracy_tracker.py — 월간 가중치 조정 제안
def suggest_weight_adjustment(sector_accuracy_by_signal_type: dict) -> dict:
    """
    sector_accuracy_by_signal_type 예시:
    {"steeps_event": 0.68, "topic_trend": 0.41, "factor_score": 0.52}
    """
    # 성능 기준치 미달 신호 유형 탐지
    adjustments = {}
    for signal_type, accuracy in sector_accuracy_by_signal_type.items():
        if accuracy < 0.45:  # 45% 미만 = 무작위 예측 수준
            adjustments[signal_type] = -0.05  # 가중치 5% 감소 제안
        elif accuracy > 0.65:
            adjustments[signal_type] = +0.03  # 가중치 3% 증가 제안

    # P1 원칙 수호: sentiment_weight는 항상 0.0 — 조정 대상에서 영구 제외
    adjustments.pop("sentiment_weight", None)

    return adjustments  # 제안만 반환, 자동 적용 ❌
```

**적용 방식:**
- `accuracy_tracker.py`가 제안값을 계산하여 Telegram으로 전송한다.
- **사용자 명시적 승인 후** Claude Code가 `investscan.yaml` `signal_policy` 값을 수정한다.
- 자동 적용 절대 금지 — 가중치 변경은 HITL 필수.
- 가중치 변경 이력은 `investscan.yaml` `_config_history`에 자동 기록.

> **제안 Telegram 메시지 형식:**
> `"📊 이번 달 신호 유형별 성능 분석 결과, topic_trend 가중치를 20% → 15%로 줄이면 IT 섹터 정확도가 개선될 것으로 예상됩니다. 변경할까요? (예 / 아니오)"`

---

### 7.12 investscan.yaml 전체 스키마

```yaml
# investscan.yaml — 사용자 설정 파일 (전체 스키마)
# 기본 위치: ~/.investscan/investscan.yaml
# Claude Code가 Day 0 설치 시 자동 생성. 직접 편집 가능하나 Claude Code 대화 권장.

# --- 경로 설정 (필수) ---
paths:
  envscan_wf1_output: "~/path/to/envscan/database.json"   # EnvironmentScan WF1 출력
  gnews_signals: "~/path/to/gnews/signals.parquet"         # GlobalNews 출력
  reports_dir: "~/investscan/output/reports/"              # 상세 리포트 저장 경로
  journal_dir: "~/investscan/data/journal/"                # 결정 저널 저장 경로
  accuracy_dir: "~/investscan/data/accuracy/"              # 정확도 추적 저장 경로

# --- 사용자 설정 ---
user:
  sectors_of_interest: ["반도체", "IT서비스", "바이오"]      # 관심 섹터 목록
  report_delivery_time: "08:00"                             # 리포트 수신 시각 (월요일)
  investment_style: "conservative"                          # conservative / balanced / aggressive

# --- Telegram 설정 ---
telegram:
  bot_token_keychain_key: "investscan.telegram.bot_token"  # Keychain 조회 키 (평문 저장 금지)
  chat_id: ""                                               # 수신 채팅 ID (설치 시 자동 입력)

# --- 신호 처리 설정 (원칙 P1 관련) ---
signal_policy:
  sentiment_weight: 0.0       # P1 원칙 — 절대 변경 금지
  steeps_event_weight: 0.70
  topic_trend_weight: 0.20
  factor_score_weight: 0.10

# --- 온보딩 모드 (초보 사용자 용어 설명) ---
onboarding_mode: true         # true: 첫 4주 동안 전문 용어 괄호 설명 자동 삽입
                               # false: 간결 리포트 (4주 후 자동 전환 권장)
                               # 예: "HBM(High Bandwidth Memory: 고대역폭 메모리)"

# --- 일시 중단 설정 ---
pause_weeks: []               # 제외할 날짜 목록 (형식: ["2026-07-20", "2026-08-03"])
                               # 해당 주는 KS-3 연속 실패 카운트에서 제외됨
                               # 사용 예: 해외 여행, 연휴 등 MacBook 미가동 기간

# --- 이력 ---
_config_history: []           # Claude Code가 자동 기록
```

---

<a id="section-8"></a>
## Section 8: 데이터 스키마 계약

### 8.1 UnifiedSignal (핵심 스키마)

| 필드 | 타입 | 설명 | 필수 여부 |
|------|------|------|---------|
| `id` | `str` | 고유 신호 ID (`{source}-{hash8}` 형식) | 필수 |
| `title` | `str` | 신호 제목 | 필수 |
| `summary` | `str` | 요약 (최대 500자, 초과 시 자동 절삭) | 필수 |
| `source` | `str` | 출처 시스템 (`envscan` / `gnews`) | 필수 |
| `steeps_category` | `SteepsCategory` | T / E / P / S / E_env / s (1차 분류, 필수) | 필수 |
| `steeps_tags` | `list[SteepsCategory]` | 복수 STEEPs 태그 (예: `[T, P]` — CHIPS Act처럼 복수 범주 해당 신호) | 선택 (기본값: `[]`) |
| `psst_score` | `float` | 0.0–1.0 (정규화 후) | 필수 |
| `signal_date` | `date` | 신호 날짜 (`YYYY-MM-DD`) | 필수 |
| `schema_version` | `str` | 스키마 버전 태그 | 필수 |

모든 필드는 `frozen=True, slots=True` dataclass로 선언한다.

> **`steeps_tags` 사용 지침:** `steeps_category`는 신호의 **지배적(primary)** STEEPs 범주 1개를 의미한다. `steeps_tags`는 부가적 범주를 추가로 표기한다 (예: CHIPS Act = `steeps_category: P`, `steeps_tags: [T, E]`). `steeps_tags`가 없으면 `steeps_category`만으로 처리한다. 복수 태그가 있는 신호는 합성 알고리즘에서 각 태그에 분할 가중치(1/len(tags))를 적용한다.

---

### 8.2 STEEPs 6가지 분류 + SteepsCategory StrEnum

**필수 Python 선언** (schema.py에 그대로 사용):

```python
from enum import StrEnum

class SteepsCategory(StrEnum):
    T     = "T"      # 기술 (Technology)
    E     = "E"      # 경제 (Economy)
    P     = "P"      # 정치/정책 (Politics/Policy)
    S     = "S"      # 사회 (Society)
    E_env = "E_env"  # 환경 (Environment) — 'E'와 충돌 방지용 이름
    s     = "s"      # 법적/보안 (Security/Legal) — 소문자 's' 필수 (대문자 'S'와 구분)
```

⚠️ `s`(보안/법적)는 **소문자**다. 대문자 `S`(사회)와 혼용 금지. 파서에서 `lower()` 적용 후 매핑할 것.

| 코드 | 의미 | 한국 GICS 섹터 연결 | 예시 신호 |
|------|------|-------------------|---------|
| `T` | 기술 | 반도체, IT서비스, 통신 | HBM 수요 증가, AI 칩 수출 규제 |
| `E` | 경제 | 금융, 에너지, 산업재 | 미국 금리 결정, 유가 변동 |
| `P` | 정치/정책 | 방산, 규제 관련 섹터 | 방산 예산 증액, 반도체 보조금 |
| `S` | 사회 | 소비재, 헬스케어 | 고령화 가속, 소비 심리 변화 |
| `E_env` | 환경 | 에너지, 소재, 유틸리티 | 탄소세 도입, RE100 의무화 |
| `s` | 법적 | 섹터 무관 (리스크 플래그) | 공정거래 규제, 개인정보법 개정 |

---

### 8.3 스키마 버전 관리 (필수)

| 버전 태그 | 소스 | 도입 시점 |
|----------|------|---------|
| `envscan-wf1-v1` | EnvironmentScan WF1 `database.json` | M0.5 |
| `envscan-wf4-v1` | EnvironmentScan WF4 priority-ranked | M1 Phase 3 |
| `gnews-signals-v1` | GlobalNews `signals.parquet` | M1 Phase 2 |

**알 수 없는 스키마 변이 발견 시:**
1. 자동 처리 절대 금지
2. 즉시 파이프라인 해당 소스 처리 중단
3. Telegram 알림: "새로운 데이터 형식이 감지되었습니다. Claude Code와 함께 업데이트가 필요합니다."
4. 부분 리포트 생성 계속 (해당 소스 제외)

---

### 8.4 pSST 점수 정규화 규칙

| 소스 | 원본 스케일 | 판별 기준 | 정규화 방법 |
|------|-----------|---------|-----------|
| EnvScan WF1 | 정수 0–100 | `engine: "envscan-wf1"` | ÷ 100 |
| EnvScan WF4 priority | 부동소수점 0–10 | `engine: "envscan-wf4"` | ÷ 10 |
| GlobalNews Parquet | 부동소수점 0–1 | `engine: "gnews"` | 그대로 |

- `engine` 필드 명시적 참조 필수 — auto-detection 절대 금지
- 정규화 후 값이 0.0 미만 또는 1.0 초과이면 crash-loud

---

### 8.5 STEEPs → GICS 매핑 신뢰도

| 신뢰도 범위 | 처리 방식 |
|-----------|---------|
| ≥ 0.7 | 정상 매핑, 리포트에 표준 출력 |
| 0.5 이상 0.7 미만 | ⚠️ 표시 + 가능한 섹터 후보 복수 제시 |
| < 0.5 | 매핑 결과 리포트 제외, 로그 기록 |

---

<a id="section-9"></a>
## Section 9: 기술 아키텍처

### 9.1 실제 파일 경로 구조

```
investscan/
├── run_m05.py                ← M0.5 진입점
├── run_m1.py                 ← M1 진입점 (weekly_orchestrator 호출)
├── config.py                 ← YAML 로드 + 경로 관리
├── schema.py                 ← frozen dataclass + StrEnum 정의
├── normalizers.py            ← THE critical module (6-format parser)
├── dedup.py                  ← content-hash + 중복 제거
├── steeps_classifier.py      ← 규칙 기반 STEEPs 재분류
├── signal_bridge.py          ← STEEPs → GICS 11 섹터
├── synthesize.py             ← 섹터 방향 합성
├── korea_signal_layer.py     ← 한국 독립 신호 레이어
├── report_generator.py       ← Jinja2 한국어 Markdown
├── weekly_orchestrator.py    ← 파이프라인 제어 + 체크포인트
├── telegram_notifier.py      ← Telegram 발송
├── personalizer.py           ← 설정 + Keychain
├── accuracy_tracker.py       ← 예측 기록 + 정확도
├── health_dashboard.py       ← HTML 대시보드
├── templates/
│   └── weekly-report.md.j2  ← Jinja2 Markdown 템플릿
└── config/
    └── investscan.yaml       ← 사용자 설정
```

---

### 9.2 모듈 의존성 순서 (이 순서로 구현)

```
config → schema → normalizers → dedup → steeps_classifier
→ signal_bridge → korea_signal_layer → synthesize
→ report_generator → weekly_orchestrator
→ telegram_notifier + accuracy_tracker + health_dashboard
```

의존성 역방향 참조 금지. 모든 데이터 흐름은 `weekly_orchestrator`를 통과한다.

---

### 9.3 파이프라인 실행 흐름

```
[일요일 20:00 — launchd 트리거]
EnvironmentScan 실행 완료 대기 (~120분)
  ↓
InvestScan 자동 시작
  ↓
normalizers.py: 6포맷 → UnifiedSignal 변환
  (스키마 변이 감지 시 → crash-loud + Telegram 알림)
  ↓
dedup.py: content-hash 중복 제거
  ↓
steeps_classifier.py: STEEPs 재분류
  ↓
korea_signal_layer.py: 외국인 수급 + 환율 + 정책 신호 추가
  ↓
synthesize.py: 섹터 방향 합성 (감성 0% 강제)
  ↓
signal_bridge.py: GICS 섹터 → 종목 스크리닝
  ↓
report_generator.py: Jinja2 Markdown 리포트 생성
  ↓
accuracy_tracker.py: 예측 기록 저장
  ↓
[월요일 08:00 이전]
telegram_notifier.py: 5줄 요약 발송
  ↓
health_dashboard.py: weekly_dashboard.html 갱신
```

---

### 9.4 파일 크기 관리

| 파일 | 최대 허용 크기 | 초과 시 처리 |
|------|-------------|-----------|
| `database.json` | 10MB | 최근 4주치만 유지, 나머지 `archive/` 이동 |
| `signals.parquet` | 50MB | 최근 2주치만 유지, 나머지 `archive/` 이동 |

---

### 9.5 체크포인트/재시작

체크포인트 파일: `~/.investscan/checkpoint.json`

**스키마 예시:**
```json
{
  "run_id": "2026-05-18",
  "last_completed_step": "korea_signal_layer",
  "steps_completed": ["normalizers", "dedup", "steeps_classifier", "korea_signal_layer"],
  "steps_pending": ["synthesize", "report_generator", "telegram_notifier"],
  "retry_count": 0,
  "started_at": "2026-05-18T20:03:11",
  "error_log": []
}
```

- 파이프라인 중단 시: `last_completed_step` 이후 단계부터 재시작
- 자동 재시도: 동일 단계 최대 2회 (`retry_count` 기록)
- 2회 후 실패: 파이프라인 중단 + Telegram 한국어 에러 알림
- 성공 완료 시: `checkpoint.json` 삭제 (스테일 상태 방지)

---

### 9.6 모듈별 네트워크 의존성 매트릭스

| 모듈 | 인터넷 필요 | 외부 서비스 | 연결 실패 시 동작 |
|------|-----------|----------|----------------|
| `config.py` | ❌ | 없음 | 완전 로컬 |
| `schema.py` | ❌ | 없음 | 완전 로컬 |
| `normalizers.py` | ❌ | 없음 | 완전 로컬 |
| `dedup.py` | ❌ | 없음 | 완전 로컬 |
| `steeps_classifier.py` | ❌ | 없음 | 완전 로컬 |
| `signal_bridge.py` | ❌ | 없음 | 완전 로컬 |
| `synthesize.py` | ❌ | 없음 | 완전 로컬 |
| `report_generator.py` | ❌ | 없음 | 완전 로컬 |
| `personalizer.py` | ❌ | macOS Keychain (로컬) | 완전 로컬 |
| `health_dashboard.py` | ❌ | 없음 | 완전 로컬 |
| `korea_signal_layer.py` | ✅ 필수 | FDR (KRX), FRED API, pykrx | graceful 스킵 — 한국 신호 없이 글로벌 신호만 사용 |
| `accuracy_tracker.py` | ✅ (4주 후) | FDR 가격 조회 | 조회 실패 시 대기 + 다음 실행 시 재시도 |
| `telegram_notifier.py` | ✅ 필수 | Telegram Bot API | 3회 재시도 후 로컬 에러 로그 저장 |
| `watchdog.py` | ✅ 필수 | Telegram Bot API | 실패 시 에러 로그만 기록 (알림 없음) |

**오프라인 테스트 모드:** `python run_m05.py --offline` 플래그로 실행 시, FDR·Telegram 호출을 모두 mock으로 대체. 파이프라인 로직 단독 검증 가능.

**FDR API 연결 실패 시 알림 문구:**
`"⚠️ 한국 수급 데이터를 일시적으로 가져오지 못했습니다. 이번 주 리포트는 글로벌 신호만 반영합니다."`

---

### 9.7 빌드 순서 vs 런타임 실행 순서 구분

> **⚠️ 두 순서는 다르다. 혼동 금지.**

| 구분 | 순서 | 근거 |
|------|------|------|
| **빌드(구현) 순서** (Section 9.2) | `config → schema → normalizers → dedup → ...` | 의존성 역방향 참조 방지 |
| **런타임 실행 순서** (Section 9.3) | `normalizers → dedup → steeps → korea_signal → synthesize → report → telegram` | 데이터 흐름 순서 |

`signal_bridge.py`는 빌드 순서에서 `korea_signal_layer` 앞에 위치하지만, 런타임에서는 `korea_signal_layer` 이후 `synthesize`와 함께 호출된다. 이 차이는 정상이다.

---

### 9.8 EnvironmentScan 자동화 갭 + envscan_bridge.sh

> **⚠️ 중요한 아키텍처 제약:** EnvironmentScan은 **Claude Code 에이전트로 실행**된다. 일반 Python 스크립트가 아니므로 launchd가 subprocess로 직접 호출할 수 없다.

**갭 요약:**

| 구성 요소 | 자동화 가능 여부 | 이유 |
|-----------|---------------|------|
| InvestScan `run_m1.py` | ✅ launchd 자동 실행 가능 | 일반 Python 스크립트 |
| EnvironmentScan WF1 | ❌ launchd 직접 호출 불가 | Claude Code 에이전트 세션 필요 |

**권장 해결 방안 — 2단계 접근:**

**방안 A: `envscan_bridge.sh` (준자동화)**

```bash
#!/bin/bash
# envscan_bridge.sh — EnvironmentScan 완료 감지 후 InvestScan 트리거
# 위치: ~/investscan/scripts/envscan_bridge.sh
# 용도: 사용자가 EnvScan 수동 실행 완료 후 이 스크립트 실행

ENVSCAN_OUTPUT="${ENVSCAN_OUTPUT_PATH:-~/path/to/envscan/database.json}"
INVESTSCAN_DIR="${HOME}/investscan"
LOG="${HOME}/Library/Logs/investscan/bridge.log"

# database.json 최근 수정 시각 확인 (4시간 이내 = 새 실행)
if [ -f "$ENVSCAN_OUTPUT" ]; then
    MODIFIED=$(find "$ENVSCAN_OUTPUT" -mmin -240 2>/dev/null)
    if [ -n "$MODIFIED" ]; then
        echo "[$(date)] EnvScan 출력 감지 — InvestScan 파이프라인 시작" >> "$LOG"
        cd "$INVESTSCAN_DIR" && python3 run_m1.py >> "$LOG" 2>&1
    else
        echo "[$(date)] EnvScan 출력 4시간 초과 — 수동 실행 필요" >> "$LOG"
        # Telegram 알림 발송 (watchdog 활용)
        python3 watchdog.py --reason "EnvScan 출력 만료" >> "$LOG" 2>&1
    fi
else
    echo "[$(date)] database.json 없음 — EnvironmentScan 먼저 실행하세요" >> "$LOG"
fi
```

**방안 B: 수동 2단계 루틴 (명시적 대안, 비코더 친화)**

1. 일요일 저녁: 사용자가 EnvironmentScan 수동 실행 (터미널 명령 1줄)
2. 완료 Telegram 알림 수신 후: `~/investscan/scripts/envscan_bridge.sh` 실행 (또는 launchd가 database.json 타임스탬프 감시)
3. 월요일 08:00: InvestScan 리포트 수신

> **Claude Code 구현 지침:** Day 0 설치 시 `envscan_bridge.sh`를 자동 생성하고 `실행방법.txt`에 2단계 루틴 안내를 포함한다. launchd plist는 `run_m1.py` 직접 실행 대신 `envscan_bridge.sh`를 호출하도록 설정한다.

---

<a id="section-10"></a>
## Section 10: 구현 원칙 (7가지 비타협 원칙)

### 10.1 원칙 목록 (Claude Code 필수 준수)

| 번호 | 원칙명 | 내용 | 위반 시 |
|------|--------|------|--------|
| **P1** | 감성제로 | `sentiment` 가중치 0% 고정. 사실 기반 이벤트 + 토픽 트렌드만 사용 | 즉시 코드 수정 |
| **P2** | 스키마 버전 | 알 수 없는 스키마 변이 → 자동 처리 금지 → 명시적 에러 + Telegram 알림 | crash-loud |
| **P3** | 자동화 투명성 | 모든 에러·알림 = 한국어 설명 + 행동 지침 1가지만. 영어 기술 스택 트레이스 노출 금지 | 메시지 재작성 |
| **P4** | 증거 체인 | 모든 섹터 방향 결론에 근거 신호 번호 2–3개 필수 첨부. 신호 없이 결론만 출력 금지 | 리포트 생성 차단 |
| **P5** | crash-loud | 스키마 검증 실패, pSST 범위 초과 → 즉시 중단 + 에러 알림. 묵음 실패 허용 안 함 | 설계 위반 |
| **P6** | graceful 분리 | 한 소스 데이터 부재 → 부분 리포트 계속. 파싱 실패 20% 이상 시만 전체 중단 | 정상 동작 |
| **P7** | 한국 독립성 | 글로벌 신호를 한국 시장에 직접 적용 금지. 모든 글로벌 신호는 `korea_signal_layer.py` 필수 통과 | 즉시 코드 수정 |

---

### 10.2 코딩 패턴 (7가지)

| 번호 | 패턴 |
|------|------|
| **CP1** | `frozen=True, slots=True` dataclass — 모든 데이터 객체 (PipelineState만 mutable) |
| **CP2** | `StrEnum` — 모든 카테고리 값 |
| **CP3** | 명시적 `scale` 파라미터 — auto-detection 절대 금지 |
| **CP4** | 방어적 `.get()` + 문서화된 기본값 (0.5, NOT 0.0) |
| **CP5** | crash-loud on contract violations / graceful on operational issues |
| **CP6** | JSON checkpoint for pipeline state |
| **CP7** | Direction + 명시적 불확실성 (`source_count` + `uncertainty_reason`) |

---

### 10.3 핵심 타임프레임 명시 (리포트 필수 포함)

모든 주간 리포트의 **첫 번째 섹션**에 고정 출력한다. 생략 불가.

> **분석 타임프레임 안내**
> 이 신호는 **4–12주 방향성**입니다. 2–4주 단기 변동과 다를 수 있습니다.
> 글로벌 신호는 한국 시장에 **4–8주 지연 전이**될 수 있습니다.
> 이 리포트는 투자 권고가 아닌 데이터 기반 방향성 참고 자료입니다.

---

<a id="section-11"></a>
## Section 11: 에러 복구 + 한국어 알림 명세

### 11.1 에러 분류 및 대응

| 에러 유형 | 처리 방식 | Telegram 알림 내용 |
|---------|---------|----------------|
| EnvironmentScan database.json 없음 | crash-loud 중단 | "EnvironmentScan 데이터를 찾을 수 없습니다. EnvironmentScan을 먼저 실행해주세요." |
| GlobalNews parquet 없음 | graceful 계속 | "GlobalNews 데이터 없이 EnvScan만으로 리포트를 생성합니다. (신뢰도 하락)" |
| 스키마 변이 감지 | crash-loud 중단 | "새로운 데이터 형식이 감지되었습니다. Claude Code와 함께 업데이트가 필요합니다." |
| 20% 이상 파싱 실패 | crash-loud 중단 | "신호 파싱 오류가 많습니다. Claude Code에게 오류 내역을 보여주세요." |
| 1개 소스 데이터 부재 | graceful 계속 | "일부 데이터 없이 리포트를 생성합니다. 데이터: EnvScan ✅ GlobalNews ⚠️" |
| launchd 월요일 08:00 미완료 | 강제 알림 | "이번 주 리포트 생성에 실패했습니다. [원인 1줄] [해결 방법 1가지]" |
| 파이프라인 재시도 3회 초과 | 사용자 알림 | "시스템 오류가 지속됩니다. Claude Code에게 오류 로그를 보여주세요." |

---

### 11.2 한국어 에러 메시지 원칙

**절대 규칙: 영어 기술 메시지 출력 금지**

| 금지 (영어 기술 메시지) | 허용 (한국어 사용자 메시지) |
|----------------------|--------------------------|
| `KeyError: 'preliminary_category'` | "신호 분류 정보를 읽지 못했습니다. EnvironmentScan을 다시 실행해주세요." |
| `FileNotFoundError: database.json` | "EnvironmentScan 데이터 파일이 없습니다. EnvironmentScan을 먼저 실행해주세요." |
| `SchemaValidationError: unexpected field` | "데이터 구조가 변경된 것 같습니다. Claude Code에게 오류 내역을 보여주세요." |

---

### 11.3 자동화 헬스체크 대시보드 (weekly_dashboard.html)

매 파이프라인 실행 완료 직후 자동 생성. 저장 경로: `output/dashboard/weekly_dashboard.html`

```
[InvestScan 헬스체크 대시보드]
마지막 성공 실행: 2026-03-23 (일) 22:14  ✅
이번 주 실행 상태: 2/2 완료 (100%)
최근 에러 (1건): ⚠️ GlobalNews 파일 없음 — graceful 모드로 계속 실행
섹터별 데이터 완전성:
  반도체 ✅ / IT ⚠️ (부분) / 바이오 ❌
다음 실행 예정: 2026-03-29 (일) 20:00
```

---

### 11.4 파이프라인 데드라인 관리

```
일요일 20:00 → launchd 파이프라인 자동 시작
월요일 08:00 → 완료 데드라인
미완료 감지  → Telegram 강제 알림 발송 (리포트 없어도 알림 필수)
```

---

### 11.5 설정 이력 자동 저장 (investscan.yaml)

```yaml
_config_history:
  - "2026-03-28: investment_style=conservative (초기값)"
  - "2026-04-05: investment_style=aggressive (사용자 변경)"
```

"이전 설정으로 돌아가줘" 자연어 명령으로 복구 가능.

---

### 11.6 MacBook 전원 꺼짐 침묵 실패 대비

> **위험:** launchd는 MacBook이 꺼져 있으면 실행되지 않는다. 일요일 밤 전원이 꺼지면 월요일 08:00에 watchdog도 침묵한다 — 아무 알림도 오지 않는다.

**대응 전략 — 2단계:**

**1단계: 사용자 루틴 안내 (Day 0 설치 시 명시)**

```
📌 일요일 체크리스트 (실행방법.txt에 자동 포함)
  □ 저녁 8시 이전: MacBook 전원 어댑터 연결
  □ 덮개 열어두기 (절전 모드 방지)
  □ 화면 보호기만 켜둬도 됨 (종료 ❌)
  □ 월요일 아침: Telegram 메시지 확인
```

**2단계: 월요일 수동 확인 트리거 (침묵 감지용)**

`watchdog.py`는 월요일 08:00 실행이 목표지만, MacBook이 꺼져 있으면 실행 자체가 불가하다. 이를 보완하기 위해:

- MacBook이 다시 켜지는 순간 launchd 미실행 여부를 감지하는 **지연 실행 감지** 로직을 구현한다:

```python
# watchdog.py — 지연 실행 감지 추가
last_run_file = Path("~/.investscan/last_successful_run.txt").expanduser()
if last_run_file.exists():
    last_run = datetime.fromisoformat(last_run_file.read_text().strip())
    days_since = (datetime.now() - last_run).days
    if days_since >= 8:  # 8일 이상 미실행 = 전주 누락
        send_telegram("⚠️ 지난주 리포트가 생성되지 않았습니다. MacBook이 꺼져 있었던 것 같습니다. 수동으로 실행하시겠어요?")
```

**선택적 백업: 스마트폰 캘린더 알림**

완전 자동화 대안이 어려울 경우, Day 0 설치 시 Claude Code가 안내:
> "매주 일요일 저녁 8시에 '📊 InvestScan — MacBook 전원 켜두기' 반복 알림을 스마트폰 캘린더에 추가해두시면 좋습니다."

---

<a id="section-12"></a>
## Section 12: 외부 연동

### 12.1 Green Zone 연동 (M1 필수)

| 연동 | 방식 | 목적 | 비고 |
|------|------|------|------|
| FinanceDataReader (FDR) | `pip install finance-datareader` | 한국 종목 가격 + 외국인 수급 데이터 | $0 오픈소스 |
| Telegram Bot API | HTTP POST (단방향) | 주간 요약 + 에러 알림 발송 | Bot Token Keychain 저장 |
| launchd | macOS 내장 | 일요일 20:00 자동 실행 | plist 파일 1개 (12.3 참조) |
| macOS Keychain | macOS 내장 | API 키 안전 저장 | 평문 저장 절대 금지 |
| **FRED API** | `pip install fredapi` | 미국 핵심 경제 지표 10개 (CPI·고용·GDP·금리·VIX) | $0 무료 API — M1 포함 **(M2에서 승격)** |
| **DART OpenAPI** | `pip install dart-fss` | 한국 기업 실적 공시 (매출·영업이익·PER 기초) | $0 무료 API — M1 포함 **(신규 추가)** |
| **pykrx** | `pip install pykrx` | 한국 주식 팩터 (PER/PBR/ROE) + 기관/외국인 수급 | $0 오픈소스 — M1 포함 **(M2에서 승격)** |

**FRED API 수집 대상 경제 지표 (10개 고정):**
`CPI`, `FEDFUNDS` (기준금리), `UNRATE` (실업률), `GDP`, `DGS10` (10년물 금리),
`VIXCLS` (VIX), `DCOILWTICO` (WTI 유가), `DEXKOUS` (USD/KRW 공식 환율),
`INDPRO` (산업생산지수), `UMCSENT` (소비자심리지수)

**DART OpenAPI 수집 대상:** 분기 실적 요약 (매출·영업이익·당기순이익) — 워치리스트 종목에 한정

---

### 12.2 Telegram 연동 상세

**발송 방향:** 시스템 → 사용자 단방향 (M1)

**기술 명세:**

| 항목 | 값 |
|------|-----|
| `parse_mode` | `MarkdownV2` |
| Telegram 메시지 최대 길이 | 300자 이내 (5줄 요약 기준) |
| 이모지 규칙 | 섹터 방향에만 사용 (🟢/⚪/🔴) — 그 외 이모지 최소화 |
| 발송 실패 재시도 | 최대 3회 (지수 백오프: 1분, 5분, 15분) |
| 발송 실패 3회 후 | 로컬 에러 로그 기록 + 다음 실행 시 알림 |

**MarkdownV2 이스케이프 필수 문자:** `. - ( ) ! # + =` — 리포트 내 해당 문자 앞에 `\` 자동 삽입

**피드백 수신 (M1 단방향):**
```
사용자 Telegram 답장: "반도체 맞았어요"
시스템 자동 응답: "W18 리포트 기준으로 기록했습니다. ✅ (결정 저널 #23)"
→ 5분 무응답: 가장 최근 리포트 기준으로 자동 저장
```

**피드백 경로**: Telegram 답장 → `telegram_notifier.py` 수신 → `data/journal/` JSONL 저장 (M1에서는 단방향. 자동 가중치 조정은 M2.)

**Bot Token 보안:** macOS Keychain만. `.env`, `investscan.yaml`, 소스 코드 내 평문 저장 절대 금지.

---

### 12.3 launchd 설정

| 항목 | 값 |
|------|-----|
| plist 파일 경로 | `~/Library/LaunchAgents/com.investscan.weekly.plist` |
| 실행 시각 | 일요일 20:00 |
| 완료 데드라인 | 월요일 08:00 |
| 로그 경로 | `~/Library/Logs/investscan/pipeline.log` |

⚠️ macOS 메이저 업데이트 이후 launchd 에이전트 비활성화 가능. 업데이트 직후 활성 여부 확인 필수.

**launchd plist 파일 예시** (`com.investscan.weekly.plist` — Claude Code가 Day 0에 자동 생성):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.investscan.weekly</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/python3</string>
    <string>/Users/USERNAME/investscan/run_m1.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>0</integer>  <!-- 0 = 일요일 -->
    <key>Hour</key><integer>20</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/USERNAME/Library/Logs/investscan/pipeline.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/USERNAME/Library/Logs/investscan/pipeline_error.log</string>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
```

설치: `launchctl load ~/Library/LaunchAgents/com.investscan.weekly.plist`
확인: `launchctl list | grep investscan`
비활성화: `launchctl unload ~/Library/LaunchAgents/com.investscan.weekly.plist`

---

### 12.4 Yellow Zone 연동 (M2+ 조건부)

| 연동 | 도입 조건 |
|------|---------|
| 멀티모델 AI | M3 이후, 단일 모델 한계 명확 시 |
| 실시간 뉴스 스트리밍 | M3 이후, 주중 돌발 이벤트 대응 필요 시 |

> FRED API / DART OpenAPI / pykrx는 M1으로 승격됨 (Yellow Zone에서 제거)

---

<a id="section-13"></a>
## Section 13: 검증 프레임워크

### 13.1 핵심 검증 지표

| 지표 | 측정 방법 | 기준 |
|------|---------|------|
| 섹터 방향 적중률 | 예측 방향 vs 실제 가격 변동 (4주 후 FDR) | Month 6 ≥ 55% |
| **Naive Baseline 초과율** | InvestScan 적중률 vs "항상 Bullish" 전략 적중률 비교 | Month 6: InvestScan > Always-Bullish + 5%p |
| 주관 유용성 점수 | Telegram: "이 리포트가 내 판단에 도움이 됐나?" 0-5점 | Month 6 평균 ≥ 3.5 |
| 파이프라인 성공률 | 성공 횟수 / 전체 실행 횟수 | 상시 ≥ 90% |

> **Naive Baseline ("항상 Bullish") 정의:** 모든 섹터를 매주 Bullish로 예측하는 가장 단순한 전략. 상승장에서는 자연히 높은 적중률을 보인다. InvestScan이 이 단순 전략보다 유의미하게 낫지 않다면, 시스템 가치가 없다는 신호다.
>
> `accuracy_tracker.py`는 매월 `Always-Bullish` 가상 전략 적중률을 함께 계산하여 월간 정확도 리포트에 비교 표시한다.

---

### 13.2 예측 기록 방식

저장 경로: `data/accuracy/predictions.jsonl`

저장 항목: 리포트 주차, 섹터명, 예측 방향, 신뢰도, 근거 신호 ID 목록, 생성 시각

4주 후 FDR 가격 데이터로 자동 결과 대조 → `accuracy_summary.json` 갱신

---

### 13.3 Month 2 Kill Switch (**SOT — Section 4.2는 이 섹션을 참조**)

| # | 유형 | 조건 |
|---|------|------|
| KS-1 | 정량 | 섹터 방향 적중률 < 40% (누적 **8회** 이상) |
| KS-2 | 정성 | "이 리포트가 도움이 됐나요? (1-5점)" 평균 < 2.5/5 (4주 연속) |
| KS-3 | 기술 | 파이프라인 완전 실패 3회 연속 (**pause_weeks 제외 후** 계산) |

Kill Switch 발동 시: Telegram 알림 발송 + 대시보드 표시 (강제 중단 아님, 사용자 판단에 위임)

> **KS-3 `pause_weeks` 제외 로직:** `investscan.yaml`의 `pause_weeks` 목록에 포함된 날짜는 KS-3 연속 실패 카운트에서 제외한다. 예: `pause_weeks: ["2026-07-20"]`이면 해당 주 미실행은 KS-3 카운트 0으로 처리. 재개 첫 주부터 카운트 재시작. *(구현: `weekly_orchestrator.py`에서 실행 전 해당 날짜 확인)*

---

### 13.3.1 정확도 판정 기준 (KS-1 세부)

| 항목 | 기준 |
|------|------|
| 벤치마크 ETF | KODEX 반도체(091160), KODEX IT(098560), KODEX 헬스케어(266410) — 섹터별 1개 고정 |
| 측정 윈도우 | **28일** (리포트 발행일 기준) |
| 적중 판정 임계값 | 예측 방향 vs ETF 실제 변동 ±2% 이내 동일 방향 = 적중 |
| 측정 방법 | `accuracy_tracker.py`가 FDR로 28일 후 가격 자동 조회 |
| 적중/미적중 | Bullish → +2% 초과 ✅ / Bearish → -2% 미만 ✅ / Neutral → ±2% 이내 ✅ |

---

### 13.4 월간 정확도 리포트 (자동 생성)

생성 시점: 매월 첫째 주 월요일

```
[월간 정확도 리포트 — 2026년 3월]

• 반도체 Bullish → 실제 +3.2%  ✅ 적중
• IT Bearish     → 실제 +0.8%  ❌ 미적중 (과소평가 요인: 국내 AI 수요 급증)
• 바이오 Neutral → 실제 -0.3%  ✅ 적중

월간 적중률: 2/3 (66.7%)

신뢰도 조정 제안:
• IT 섹터 신호 가중치 -5%
```

---

### 13.5 Month 1-6 품질 게이트

| 월 | 정량 기준 | 정성 기준 |
|----|---------|---------|
| M1 | 파이프라인 정상 실행, STEEPs 분포 합리적 | "시스템이 데이터를 정상 수집하고 있는가?" |
| M2 | 적중률 > 45% 또는 Kill Switch 미발동 | "다음 주에도 계속 실행하겠는가?" |
| M3 | 적중률 > 50% | "어느 리포트가 실제 투자 포지션 생각을 바꾸었는가?" |
| M6 | 적중률 ≥ 55%, 주관 평점 ≥ 3.5 | "InvestScan이 멈추면 그리울 것인가?" |

---

### 13.6 HITL (Human-in-the-Loop) 게이트

Claude Code는 다음 3개 게이트에서 **반드시 사용자 확인을 받은 후** 다음 단계로 진행한다.

| 게이트 | 시점 | Claude Code의 질문 | 진행 조건 |
|-------|------|----------------|---------|
| **HITL-1** | Day 0 설치 완료 후 | "설치가 완료됐습니다. `investscan.yaml` 설정을 확인해 주세요. 수정할 항목이 있나요?" | 사용자 "OK" 또는 수정 완료 후 |
| **HITL-2** | M0.5 Done Gate 통과 후 | "Telegram 메시지를 받으셨나요? 내용이 이해되시나요? (OK / 수정 필요)" | "OK" 응답 후 M1 개발 시작 |
| **HITL-3** | M1 Phase 4 완료 후 | "첫 번째 완전한 리포트입니다. 투자 결정에 도움이 될 것 같으신가요? (1–5점)" | 3점 이상 시 자동화 활성화. 미만 시 개선 세션 진행 |

HITL-3 점수 < 3점 시: "어떤 부분이 부족하셨나요?"를 묻고 구체적 개선 후 재검토.

---

### 13.7 M1 최종 인수 기준

자동화 활성화 전 다음 기준을 모두 통과해야 한다.

| 기준 | 확인 방법 | 합격 기준 |
|------|---------|---------|
| 첫 2회 리포트 사용자 평점 | HITL-3 응답 | 2회 평균 ≥ 3/5점 |
| 7-point 자가검증 충족률 | 발송 로그 | ≥ 5/7 충족 (첫 2회 평균) |
| Telegram 수신 성공률 | 발송 로그 | 100% (첫 2회 기준) |
| 빈 템플릿 변수 잔존 없음 | `{{ variable }}` 검색 | 0건 |
| 면책 조항 포함 | 리포트 하단 확인 | 모든 리포트 포함 |

모든 기준 통과 시 launchd 자동화 활성화. 미통과 항목은 Claude Code와 개선 후 재검토.

---

<a id="section-14"></a>
## Section 14: M2 백로그 (PRD 범위 밖, 참고용)

### 14.1 M2 기능 목록 (~800 LOC 추가 예상)

| 기능 | 설명 |
|------|------|
| 정확도 추적 자동화 심화 | 경로 B/C 추가 (신호 단위 정확도 추적) |
| 개인화 P2 | CLI wizard, 관심 섹터 자동 학습 |
| 피드백 루프 개선 | Telegram 피드백 → 섹터 신호 가중치 자동 반영 |
| 포트폴리오 관련성 레이어 | 사용자 보유 종목 기준 리포트 재정렬 |
| WF4 + 나머지 포맷 normalizer | 추가 포맷 대응 |

### 14.2 영구 제외 (Red Zone)

| 기능 | 제외 이유 |
|------|---------|
| 자동 주문 실행 | 투자자문업 해당 가능성, 금전적 손실 리스크 |
| SaaS 배포 | 설계 원칙 위반 (100% 로컬) |
| 실시간 알림 (초당 단위) | 불필요한 복잡도 |
| 소셜 기능 | 설계 범위 이탈 |

---

<a id="section-15"></a>
## Section 15: 한국 법적 컴플라이언스

### 15.1 투자자문업 비해당 3가지 근거

1. **특정인 대상 아님** (자본시장법 제7조 예외): 불특정 다수 대상이 아닌 단일 사용자의 로컬 환경
2. **계속적 계약 없음**: 구독 서비스 없음, 서비스 계약 없음
3. **보수 수취 없음**: InvestScan 리포트 생성에 대한 유료 청구 없음

---

### 15.2 금지 표현 + 안전 대안

| 금지 표현 | 안전 대안 |
|---------|---------|
| "매수 추천합니다" | "관찰 대상으로 분류되었습니다" |
| "~% 수익 예상" | "4-12주 방향성: 긍정 신호" |
| "지금 사세요" | "이번 주 행동 참고 사항" |
| "투자 조언" | "데이터 기반 관찰 목록" |
| "종목 추천" | "종목 관찰 워치리스트" |
| "확실한 상승" | "신호 강도: High (불확실성 포함)" |

---

### 15.3 필수 면책 조항 (리포트 하단 고정)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  투자 위험 고지

이 리포트는 투자 권고가 아닌 데이터 기반 정보 제공 목적입니다.
모든 투자 결정은 본인 책임이며, 이 시스템의 분석 결과를
참고 자료로만 활용하세요.
과거 신호 방향성이 미래 수익을 보장하지 않습니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Telegram 요약 단축 버전: `⚠️ 이 정보는 투자 참고용이며 권고가 아닙니다. 모든 투자 결정은 본인 책임입니다.`

---

### 15.4 개인정보 처리

| 데이터 유형 | 저장 위치 | 외부 전송 |
|-----------|---------|---------|
| 시장 신호 데이터 | 로컬 `data/` | 없음 |
| 투자 결정 저널 | 로컬 `data/journal/` JSONL | 없음 |
| Telegram Bot Token | macOS Keychain | 없음 (런타임 조회만) |
| 정확도 추적 데이터 | 로컬 `data/accuracy/` | 없음 |

**절대 금지:** `.env`, `investscan.yaml`, 소스 코드 내 API 토큰 평문 저장.

---

*PRD v1.2 — InvestScan | 2026-03-28 | final-research.md R1-R10 기반 | 황금 원칙 6가지 적용 | Round 1+2 성찰 6개 에이전트 권장사항 전체 반영*
