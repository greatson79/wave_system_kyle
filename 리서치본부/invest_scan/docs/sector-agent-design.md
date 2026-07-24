# InvestScan 섹터 전문 에이전트 설계서

**작성일**: 2026-05-27  
**버전**: v1.0  
**설계 원칙**: 클러스터 기반 (관련 섹터를 하나의 에이전트가 담당)

---

## 1. 현황 분석

### 기존 5개 에이전트 역할 매핑

| 에이전트 | 역할 | 담당 섹터 (20개 중) |
|---------|------|-------------------|
| `analyst-tech` | 반도체·AI 전문 | semiconductor, semiconductor_equipment, ai_platform, technology, optical_network |
| `analyst-korea` | 한국 전체 시장 수급 | 전체 (섹터 비특화 — 수급·외국인 동향 중심) |
| `analyst-macro` | 글로벌 거시경제 | 전체 (금리·환율·인플레이션 중심) |
| `analyst-valuation` | 종목 밸류에이션 | 전체 (PER·PBR·EPS 기반) |
| `analyst-risk` | 지정학·규제 리스크 | cybersecurity, defense (부분적), geopolitical 이벤트 |

### 커버리지 갭 (현재 미전문 섹터)

```
power_infrastructure  ← 전력인프라·변압기·해저케이블
nuclear               ← 원전·SMR
energy                ← 신재생에너지·수소
battery_ev            ← 배터리·전기차
automotive            ← 자동차·자율주행
shipbuilding          ← 조선·해양플랜트
defense               ← 방산·항공
steel_materials       ← 철강·소재
chemicals             ← 석유화학·정밀화학
biotech               ← 바이오·제약·의료기기
consumer              ← 소비재·유통·내수
entertainment         ← 엔터·미디어
financials            ← 금융 (korea 에이전트가 부분 커버)
```

---

## 2. 신규 섹터 에이전트 설계 (+4명)

사용자 선택: 에너지전환 / 방산·조선 / 바이오·헬스케어 / 소비재·내수  
설계 원칙: 시장 드라이버가 유사한 섹터를 클러스터링

---

### Agent 6: `analyst-energy` — 에너지전환·전력인프라 전문가

**담당 섹터 클러스터**:

| 섹터 키 | 내용 | 주요 종목 예시 |
|---------|------|-------------|
| `power_infrastructure` | 변압기·전력기기·해저케이블 | HD현대일렉트릭, 효성중공업, LS Electric |
| `nuclear` | 원전·SMR·핵연료 | 두산에너빌리티, 한전기술, 우리기술투자 |
| `energy` | 신재생에너지·수소·ESS | SK E&S, 한화솔루션 |
| `battery_ev` | 배터리셀·소재·전기차부품 | LG에너지솔루션, 삼성SDI, 에코프로 |

**공통 드라이버**: 글로벌 전력 수요 증가, AI 데이터센터 전력 인프라, 에너지 전환 정책, IRA 보조금, 원전 르네상스

**전문 데이터 소스**:
- EIA(미 에너지정보청) 전력 수요 데이터
- 한전 전력통계 월보
- IEA 신재생에너지 설비 데이터
- 글로벌 원전 건설 파이프라인 (IAEA)

**Round 1 출력 템플릿** (round1_energy_{DATE}.json):
```json
{
  "agent": "analyst-energy",
  "sector_adjustments": {
    "power_infrastructure": 0.0~0.30,
    "nuclear": 0.0~0.30,
    "energy": -0.30~0.30,
    "battery_ev": -0.30~0.30
  },
  "cluster_thesis": "에너지전환 클러스터 핵심 주장 (2-3문장)",
  "key_signals": ["신호1", "신호2", "신호3"],
  "risk_factors": ["리스크1", "리스크2"],
  "sector_adjustment_rationale": "각 섹터 조정 근거"
}
```

---

### Agent 7: `analyst-defense` — 방산·조선·소재 전문가

**담당 섹터 클러스터**:

| 섹터 키 | 내용 | 주요 종목 예시 |
|---------|------|-------------|
| `defense` | 방산·항공우주·무기체계 | 한화에어로스페이스, LIG넥스원, 현대로템 |
| `shipbuilding` | 조선·해양플랜트·LNG선 | HD현대중공업, 삼성중공업, 한화오션 |
| `steel_materials` | 철강·특수강·소재 | POSCO홀딩스, 현대제철 |
| `chemicals` | 석유화학·방산소재·정밀화학 | 롯데케미칼, 금호석유 |

**공통 드라이버**: 지정학적 긴장, 글로벌 국방비 증가, LNG 수요·에너지 전환 조선 수요, 방산 수출 사이클

**전문 데이터 소스**:
- SIPRI 글로벌 군비지출 데이터
- 클락슨 리서치 조선 수주·수주잔고 (주간)
- 한국 방위사업청 수출 계약 공시
- LME(런던금속거래소) 철강·원자재 가격

**Round 1 출력 템플릿** (round1_defense_{DATE}.json):
```json
{
  "agent": "analyst-defense",
  "sector_adjustments": {
    "defense": -0.30~0.30,
    "shipbuilding": -0.30~0.30,
    "steel_materials": -0.30~0.30,
    "chemicals": -0.30~0.30
  },
  "cluster_thesis": "방산·조선 클러스터 핵심 주장",
  "geopolitical_triggers": ["트리거1", "트리거2"],
  "order_backlog_signal": "클락슨 수주잔고 방향성",
  "sector_adjustment_rationale": "조정 근거"
}
```

---

### Agent 8: `analyst-biotech` — 바이오·헬스케어 전문가

**담당 섹터 클러스터**:

| 섹터 키 | 내용 | 주요 종목 예시 |
|---------|------|-------------|
| `biotech` | 제약·바이오·의료기기·CRO | 삼성바이오로직스, 셀트리온, 유한양행 |

> **참고**: biotech 단일 섹터이지만 내부 서브클러스터가 넓음  
> — 임상 파이프라인 (Phase 1-3), 위탁생산(CMO/CDMO), 의료기기, 헬스케어IT

**서브클러스터 분류**:
- **CMO/CDMO**: 삼성바이오로직스, SK바이오사이언스 (글로벌 위탁생산)
- **혁신 신약**: 유한양행 (레이저티닙), 한미약품 (GLP-1), 셀트리온 (항체의약품)
- **의료기기**: 레이, 바텍, 인바디
- **디지털헬스**: 에임메드, 뷰노

**전문 데이터 소스**:
- FDA 신약 허가 캘린더 (PDUFA 날짜)
- 임상시험 데이터베이스 (clinicaltrials.gov)
- 한국 식약처 승인 현황
- 글로벌 Big Pharma 기술수출 계약 공시

**Round 1 출력 템플릿** (round1_biotech_{DATE}.json):
```json
{
  "agent": "analyst-biotech",
  "sector_adjustments": {
    "biotech": -0.30~0.30
  },
  "sub_cluster_view": {
    "cmo_cdmo": "outlook",
    "innovative_drug": "outlook + key catalysts",
    "medical_device": "outlook",
    "digital_health": "outlook"
  },
  "fda_catalysts": ["PDUFA 날짜 이벤트"],
  "clinical_risk": "임상 실패 위험 평가",
  "sector_adjustment_rationale": "조정 근거"
}
```

---

### Agent 9: `analyst-consumer` — 소비재·내수·엔터 전문가

**담당 섹터 클러스터**:

| 섹터 키 | 내용 | 주요 종목 예시 |
|---------|------|-------------|
| `consumer` | 소비재·유통·식품·내수 | BGF리테일, 농심, CJ제일제당, 이마트 |
| `entertainment` | K-콘텐츠·미디어·OTT·게임 | HYBE, 카카오엔터, 넷마블 |
| `automotive` | 자동차·부품·전동화 부품 | 현대차, 기아, 현대모비스 |

**공통 드라이버**: 내수 소비 심리, 금리 인하 사이클 (소비 회복), K-컬처 글로벌 확산, 전기차 전환 속도

**전문 데이터 소스**:
- 통계청 소매판매지수 (월간)
- 소비자심리지수 (한국은행)
- 한국 관광·엔터 수출 통계
- 글로벌 EV 판매 데이터 (EV-volumes.com)

**Round 1 출력 템플릿** (round1_consumer_{DATE}.json):
```json
{
  "agent": "analyst-consumer",
  "sector_adjustments": {
    "consumer": -0.30~0.30,
    "entertainment": -0.30~0.30,
    "automotive": -0.30~0.30
  },
  "domestic_cycle": "내수 사이클 단계 평가",
  "k_culture_signal": "K-콘텐츠 글로벌 트렌드",
  "ev_transition_pace": "전동화 전환 속도 평가",
  "sector_adjustment_rationale": "조정 근거"
}
```

---

## 3. 섹터 커버리지 완전 매핑

9명 체제 완성 후 20개 섹터 전담 현황:

| # | 섹터 키 | 담당 에이전트 |
|---|---------|-------------|
| 1 | semiconductor | **analyst-tech** |
| 2 | semiconductor_equipment | **analyst-tech** |
| 3 | ai_platform | **analyst-tech** |
| 4 | technology | **analyst-tech** |
| 5 | optical_network | **analyst-tech** |
| 6 | cybersecurity | **analyst-risk** (+ tech 보조) |
| 7 | power_infrastructure | ✅ **analyst-energy** (신규) |
| 8 | nuclear | ✅ **analyst-energy** (신규) |
| 9 | energy | ✅ **analyst-energy** (신규) |
| 10 | battery_ev | ✅ **analyst-energy** (신규) |
| 11 | automotive | ✅ **analyst-consumer** (신규) |
| 12 | shipbuilding | ✅ **analyst-defense** (신규) |
| 13 | defense | ✅ **analyst-defense** (신규) |
| 14 | steel_materials | ✅ **analyst-defense** (신규) |
| 15 | chemicals | ✅ **analyst-defense** (신규) |
| 16 | financials | **analyst-korea** |
| 17 | biotech | ✅ **analyst-biotech** (신규) |
| 18 | telecom | **analyst-korea** |
| 19 | entertainment | ✅ **analyst-consumer** (신규) |
| 20 | consumer | ✅ **analyst-consumer** (신규) |

**결과**: 20/20 섹터 전담 완전 커버 달성

---

## 4. 에이전트 가중치 재설계

### 기존 5명 가중치 (기준점)

```
tech: 0.35 / korea: 0.25 / valuation: 0.20 / macro: 0.15 / risk: 0.05
```

### 9명 체제 — 레짐별 가중치 테이블

**설계 원칙**:
- valuation·macro·risk는 횡단면(cross-cutting) 역할 → 비율 유지
- 신규 4개 에이전트는 "섹터 심도" 역할 → 레짐에 따라 활성화
- 모든 테이블 합계 = 1.00

#### `tech_cycle` (반도체·AI 주도 시장)

| 에이전트 | 기존 | 신규 | 변경 |
|---------|------|------|------|
| analyst-tech | 0.35 | **0.28** | -0.07 |
| analyst-korea | 0.25 | **0.18** | -0.07 |
| analyst-valuation | 0.20 | **0.18** | -0.02 |
| analyst-macro | 0.15 | **0.12** | -0.03 |
| analyst-risk | 0.05 | **0.05** | 0 |
| analyst-energy | — | **0.07** | +신규 |
| analyst-defense | — | **0.03** | +신규 |
| analyst-biotech | — | **0.05** | +신규 |
| analyst-consumer | — | **0.04** | +신규 |
| **합계** | **1.00** | **1.00** | ✅ |

#### `macro_cycle` (금리·인플레이션 레짐)

| 에이전트 | 가중치 | 근거 |
|---------|------|------|
| analyst-macro | **0.28** | 금리·환율 주도 |
| analyst-valuation | **0.22** | 할인율 변화 중요 |
| analyst-korea | **0.15** | 수급 참조 |
| analyst-energy | **0.12** | 에너지 가격 → 전력 인프라 직결 |
| analyst-consumer | **0.10** | 소비 회복 싸이클 |
| analyst-tech | **0.06** | 성장주 압축 |
| analyst-defense | **0.04** | 방산 예산 변동 |
| analyst-biotech | **0.02** | 낮은 금리 민감도 |
| analyst-risk | **0.01** | 최소 |
| **합계** | **1.00** | ✅ |

#### `geopolitical` (지정학 위기 레짐)

| 에이전트 | 가중치 | 근거 |
|---------|------|------|
| analyst-risk | **0.22** | 지정학 리스크 주도 |
| analyst-defense | **0.20** | 방산·조선 수혜 직접 |
| analyst-macro | **0.18** | 매크로 여파 |
| analyst-energy | **0.15** | 에너지 공급망 충격 |
| analyst-tech | **0.10** | 반도체 수출통제 |
| analyst-korea | **0.08** | 한국 지정학 노출 |
| analyst-valuation | **0.05** | 밸류에이션 압축 |
| analyst-consumer | **0.01** | 소비 위축 |
| analyst-biotech | **0.01** | 비방어적 |
| **합계** | **1.00** | ✅ |

#### `risk_off` (약세장·전반 매도 레짐)

| 에이전트 | 가중치 | 근거 |
|---------|------|------|
| analyst-risk | **0.32** | 리스크 최우선 |
| analyst-macro | **0.25** | 경기침체 신호 |
| analyst-valuation | **0.18** | 안전마진 중요 |
| analyst-defense | **0.08** | 방어적 섹터 |
| analyst-biotech | **0.06** | 비시클리컬 |
| analyst-korea | **0.05** | 수급 방어 |
| analyst-consumer | **0.03** | 필수소비재 부분 방어 |
| analyst-energy | **0.02** | 제한적 방어 |
| analyst-tech | **0.01** | 위험 최소화 |
| **합계** | **1.00** | ✅ |

---

## 5. Round 2 비용 비교

| 구성 | 에이전트 수 | Round 2 읽기 수 | Round 2 LLM 호출 | 상대 비용 |
|-----|-----------|----------------|-----------------|---------|
| 기존 5명 | 5 | 5×4 = 20 reads | 5 calls | 1.0× |
| **신규 9명** | **9** | **9×8 = 72 reads** | **9 calls** | **~3.5×** |
| 참고: 10명 | 10 | 10×9 = 90 reads | 10 calls | 4.5× |

**비용 절감 옵션** (선택적):
- Round 2에서 섹터 전문 에이전트는 "연관 레짐의 기존 에이전트 결과만" 선택 읽기
  - 예: `analyst-biotech`는 Round 2에서 macro·valuation·risk 결과만 읽음 (tech·korea 스킵)
  - 읽기 수: 5×4 + 4×3 = 32 (20→32, +60% vs 기존 대비 3.5× 감소 가능)

---

## 6. 기존 에이전트와의 역할 경계

| 항목 | 기존 에이전트 역할 | 섹터 에이전트 역할 |
|-----|-------------------|------------------|
| 전력인프라 (power_infra) | macro가 "금리 하락 → 유틸리티 유리" 수준 언급 | energy가 HD현대일렉트릭 수주잔고·변압기 리드타임 데이터 분석 |
| 방산 (defense) | risk가 "지정학 긴장 상승" 신호 | defense가 클락슨 수주잔고·SIPRI 국방비 데이터 분석 |
| 바이오 (biotech) | korea가 바이오 업종 수급 언급 | biotech이 PDUFA 날짜·임상 결과 촉매 분석 |
| 소비재 (consumer) | korea가 내수 수급 언급 | consumer가 소비자심리지수·소매판매 데이터 분석 |

**충돌 방지 규칙** (Round 2 교차 검토 시 명시):
- 섹터 에이전트의 sector_adjustments가 기존 에이전트와 ±0.15 이상 차이 → 반드시 rationale 제공
- 최종 가중 평균은 Python agent_consensus.py가 결정 (P6)

---

## 7. 구현 로드맵

### Phase A: 에이전트 정의 파일 생성 (즉시 가능)

```
.claude/agents/
├── analyst-energy.md    ← 新 에이전트 정의
├── analyst-defense.md   ← 新
├── analyst-biotech.md   ← 新
└── analyst-consumer.md  ← 新
```

### Phase B: agent_consensus.py 확장

1. `AGENT_WEIGHTS` 및 `REGIME_WEIGHTS`에 4개 에이전트 추가
2. `load_round2_results()` 함수: 9개 파일 로드로 확장
3. 가중치 테이블 4개 (tech_cycle/macro_cycle/geopolitical/risk_off) 업데이트

### Phase C: invest-analysis.md 커맨드 업데이트

Phase 3/4 에이전트 실행 리스트에 4개 에이전트 추가

### Phase D: context 파일 업데이트

`output/temp/agent_context_{DATE}.json`에 에너지전환·방산·바이오·소비재 섹터 데이터 소스 추가

---

## 8. 결정 사항 요약

| 항목 | 결정 |
|-----|------|
| 신규 에이전트 수 | **+4명** (총 9명) |
| 에이전트 명칭 | analyst-energy / analyst-defense / analyst-biotech / analyst-consumer |
| 클러스터 원칙 | 공통 시장 드라이버 기준 묶음 |
| 섹터 커버리지 | 20/20 완전 커버 |
| 가중치 합계 | 모든 레짐에서 1.00 |
| Round 2 비용 | 기존 대비 약 3.5× (최적화 옵션 적용 시 약 1.6×) |
| P6 원칙 | 불변 — 최종 판단은 Python agent_consensus.py |

---

**다음 단계**: Phase A → 4개 에이전트 .md 파일 생성 후 Phase B → agent_consensus.py 확장

---

## 9. 점검 결과 — 발견된 12개 문제 (2026-05-27 2차/3차 점검)

### 토론 메커니즘 실체 규명

현재 구조는 **단일 패스 교차 검토**였음 (진정한 토론 아님):
- Round 2는 다른 에이전트의 **round1만** 읽음 (수정된 입장 미공유)
- 모순은 Python 가중 평균으로만 처리 (해소 로직 없음)
- 토론이 no-op일 수 있음 (round1 복사 검증 없음)

→ **사용자 결정: 다회차 토론으로 확장** (아래 §11)

### 발견된 12개 문제 + 처리 결정

| # | 문제 | 심각도 | 결정 |
|---|------|-------|------|
| Bug1 | "5개 완료 대기" 하드코딩 | MEDIUM | Phase 3+4 양쪽 "9개"로 수정 |
| Bug2 | AGENT_WEIGHTS fallback 미갱신 | MEDIUM | 신규 4명 추가 (tech_cycle와 동일) |
| Edge1 | Cat B 캡 3개 포화 | LOW | 캡 3→5 확장 |
| Edge2 | 레짐 감지 blind spot | LOW(수정쉬움) | `detect_market_regime` 섹터 리스트 config 확장 |
| Edge3 | battery_ev↔automotive 반대 신호 | MEDIUM | 다회차 토론 + 모순 탐지로 완화 |
| Edge4 | risk↔defense defense 중복 제출 | MEDIUM | analyst-risk는 defense=0.0 명시 |
| **P1** | **hint=B 종목이 Cat A 확정 가능** | **HIGH** | **Cat A는 hint=A만; hint=A 없는 섹터는 Cat B 강등** |
| P2 | 에이전트 누락 시 가중치 미정규화 | MEDIUM | active_sum으로 재정규화 |
| Miss1 | 기존 5명이 미지 도메인 round 읽음 | HIGH | 기존 5개 .md에 도메인 경계 지침 추가 |
| Miss2 | hint=A 0개 섹터 Cat A 공백 | (P1로 해결) | Cat B 강등으로 흡수 |
| Miss4 | 신규 4명 Round 2/3 지침 누락 | — | Debate round 섹션 포함 |
| Miss5 | Phase 3+4 양쪽 launch 갱신 | — | 4줄씩 추가 |

---

## 10. P1 종목 선정 수정 — category_hint 필터

### 현재 버그 (select_confirmed_stocks)

`category_hint`를 **전혀 읽지 않고** sample_stocks 순서대로 최대 5개 선택.
→ cybersecurity Cat A 진입 시 안랩(A) 다음 파수·이글루·지니언스(B) 소형주가 Cat A 주요 추천으로 확정.

### 수정 규칙 (사용자 결정: Cat B 강등)

```
Cat A 종목 선정:
  - sector_confidence >= 0.65 인 섹터에서
  - category_hint == 'A' 종목만 선택
  - hint=A 종목이 0개인 섹터 → 해당 섹터의 hint=B 종목은 Cat B 풀로 강등

Cat B 종목 선정:
  - sector_confidence >= 0.50 (& < 0.65) 섹터의 모든 종목 +
  - 위에서 강등된 hint=B 종목
  - category_hint 무관 (Cat B는 테마/관심이므로)
```

**검증**: optical_network(5종목 전부 hint=B)가 Cat A 신뢰도여도 → Cat A 종목 0개 기여, hint=B 5종목은 Cat B 후보로 강등. Cat A 공백 안전 처리됨.

---

## 11. 다회차 토론 아키텍처 (사용자 결정 반영)

### 구조 변경

```
Round 1: 독립 분석           → round1_{agent}_{DATE}.json
Round 2: 다른 에이전트 round1 읽고 수정  → round2_{agent}_{DATE}.json
Round 3: 다른 에이전트 round2 읽고 재수정 → round3_{agent}_{DATE}.json   ← 신규
[조기 종료] 수렴 시 Round 3 생략
```

agent_consensus는 **마지막 라운드 우선 로드**: round3 → round2 → round1 fallback

### 수렴/정지 조건 (P6 — Python이 판정)

신규 모듈 `debate_convergence.py`:

```
정지 조건 (둘 중 하나 충족 시 토론 종료):
  1. 수렴: max(|round_N[sector] - round_{N-1}[sector]|) < 0.03  (모든 에이전트·섹터)
  2. 하드 캡: N >= 3  (R1 + R2 + R3 = 최대 3라운드)

발산 가드:
  - 라운드 간 delta가 직전보다 커지면(진동) → 즉시 정지
  - 최종값 = 마지막 두 라운드의 평균 (오실레이션 댐핑)
```

### 입장 고수 규칙 (drift 방지 — 모든 에이전트 .md에 명시)

```
- 당신의 주담당 섹터(클러스터): 다른 에이전트가 반대해도
  당신이 더 강한 1차 데이터 근거를 가지면 입장 유지.
- 비주담당 섹터: 해당 전문 에이전트의 의견을 우선 반영.
- 입장 변경 시 sector_adjustment_rationale에 "누구의 어떤 근거로 수정했는지" 명시.
- 단순 동조(herding) 금지 — 근거 없는 입장 변경은 무효.
```

### 모순 탐지 (Edge3·Edge4 완화)

`debate_convergence.py`가 각 라운드 후 검사:
```
같은 섹터에 대해 두 에이전트의 adjustment 차이가 ±0.15 이상이면
→ "unresolved_conflict" 플래그 + 리포트 §7에 "의견 불일치" 명시
→ 다음 라운드에서 두 에이전트가 반드시 해당 섹터 재검토
```

### 비용 영향

| 구성 | 라운드 | 총 LLM 호출 | 총 읽기 | 상대 비용 |
|-----|-------|-----------|--------|---------|
| 기존 5명 2라운드 | R1+R2 | 10 | 20 | 1.0× |
| 9명 2라운드 | R1+R2 | 18 | 72 | ~3.5× |
| **9명 3라운드 (수렴 시 조기종료)** | R1+R2(+R3) | 18~27 | 72~144 | **3.5×~7×** |

> 절대 기준 1(품질 우선, 비용 무시)에 부합. 단 수렴 조기종료로 평균 비용 절감.

### 구현 추가 항목

```
investscan/debate_convergence.py   ← 신규: 수렴 판정 + 모순 탐지 + 발산 가드
.claude/commands/invest-analysis.md ← Phase 4에 Round 3 조건부 실행 블록 추가
agent_consensus.py                  ← load_agent_round2 → load_agent_latest (round3>2>1)
```

---

## 12. 최종 구현 순서 (회귀 검증 포함)

```
1. agent_consensus.py 수정
   - REGIME_WEIGHTS 4개 테이블에 신규 4명 추가 (합계 1.0 검증 완료)
   - AGENT_WEIGHTS fallback 갱신
   - select_confirmed_stocks: category_hint='A' 필터 + hint=B Cat B 강등
   - Cat B 캡 3→5
   - 가중치 정규화 (active_sum 보정)
   - load_agent_latest (round3>2>1 fallback)
2. debate_convergence.py 신규 작성 (수렴·모순·발산 가드)
3. detect_market_regime 섹터 리스트 config 확장 (Edge2)
4. 신규 4개 에이전트 .md 생성 (Round 1+2+3 지침 + 입장 고수 규칙)
5. 기존 5개 에이전트 .md에 도메인 경계 + 입장 고수 지침 추가 (Miss1)
   - analyst-risk: defense=0.0 명시 (Edge4)
6. invest-analysis.md: Phase 3+4 launch 9명 + Round 3 블록 + "9개 대기"
7. ★회귀 검증: 2026-05-27 데이터로 build_confirmed_watchlist 재실행
   - Cat A 5종목(SKT·KT·LGU+·HD현대일렉트릭·효성중공업) 유지 확인
   - 달라지면 원인 추적 후 재검토
```

---

## 13. 실제 통합 테스트 결과 (2026-05-28)

신규 4개 에이전트를 2026-05-27 컨텍스트로 실행 → 9인 consensus 통합 검증.

**성공:**
- 4개 에이전트 전부 valid round1 생성(20섹터). energy: power_infra +0.20, defense: shipbuilding +0.20/defense +0.17, consumer: entertainment +0.12, biotech: +0.08(보수적).
- 9/9 quorum(weight 1.00). debate_convergence delta 0.14 → CONTINUE.
- 불변식 6개 PASS. defense·power_infra가 신규 에이전트 덕에 Cat A 섹터 진입. 풀 쿼럼 시 Cat A는 원래 5종목으로 안정 수렴.

**테스트가 드러낸 버그 2건 (기존 코드, 전 에이전트 영향) — 수정 완료:**

| 버그 | 원인 | 수정 |
|------|------|------|
| BUG A | `sorted(glob('agent_context_*.json'))[-1]`가 no-dash 파일을 마지막으로 잘못 선택 ('-'<'0') → 구파일 읽음 | `investscan/agent_context.py` 신규 — run_date 기반 선택. 9개 에이전트 Step 1을 `load_latest_context()`로 교체 |
| BUG B | 구파일은 `steeps_category`, 신파일은 `category` 키 (스키마 드리프트) | 헬퍼가 `category` 키 자동 정규화 |

**부수 조치:** `agent_context_20260515.json` → `agent_context_2026-05-15.json` 리네임(명명 일관성).

**운영 주의:** 신규 에이전트 4개는 **세션 재시작 후** `subagent_type`으로 직접 호출 가능. watchlist 종목 유니버스(naver_finance 12종)에 에너지·방산·바이오 순수주 부족 — 종목 확장 검토 권고.

**신규/변경 파일 전체:**
```
investscan/agent_consensus.py      (수정)
investscan/debate_convergence.py   (신규)
investscan/agent_context.py        (신규 — BUG A/B 수정)
investscan/telegram_notifier.py    (send_document 추가)
.claude/agents/analyst-{energy,defense,biotech,consumer}.md  (신규)
.claude/agents/analyst-{tech,korea,macro,valuation,risk}.md  (보강 + Step1 수정)
.claude/commands/invest-analysis.md  (9인 + Round3)
.claude/hooks/scripts/notify_report_complete.py  (신규)
.claude/settings.json  (PostToolUse 알림 hook)
```

