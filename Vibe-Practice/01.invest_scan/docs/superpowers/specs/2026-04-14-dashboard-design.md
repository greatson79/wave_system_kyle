# InvestScan HTML 대시보드 설계 스펙

**작성일:** 2026-04-14  
**상태:** 승인됨  
**구현 대상:** `investscan/export_dashboard.py` (신규) + `investscan/export_report.py` (수정)

---

## 1. 목표

InvestScan 분석 파이프라인 완료 후, 기존 TXT/PDF/MD 보고서와 함께 단일 자체완결 HTML 대시보드를 자동 생성한다. 수치·시각화가 포함된 인터랙티브 대시보드로 빠른 의사결정을 지원한다.

---

## 2. 아키텍처

```
python3 -m investscan.export_report --date {DATE} --formats html
                    │
                    ▼
          export_report.py (기존, 수정 최소화)
          └── formats에 "html" 포함 시
              └── export_dashboard.generate(date) 호출
                            │
              ┌─────────────┼──────────────────┐
              ▼             ▼                  ▼
    load_watchlist()   load_kospi_forecast()  fetch_live_prices()
    confirmed_         weekly-report-         naver_finance.py
    watchlist_{D}.json {DATE}.md (regex)      (Cat A+B 종목만)
              │             │                  │
              └─────────────┴──────────────────┘
                            │
                    render_html(data)
                            │
                            ▼
    output/투자분析제안/{DATE}_주간투자분析_대시보드.html
```

### 모듈 구성

| 파일 | 역할 | 변경 유형 |
|------|------|----------|
| `investscan/export_dashboard.py` | 데이터 로딩 + HTML 렌더링 전담 | **신규** |
| `investscan/export_report.py` | `--formats html` 플래그 + `export_dashboard` 호출 | **수정 (최소)** |

기존 TXT/PDF/MD 생성 로직은 변경하지 않는다.

---

## 3. 대시보드 레이아웃

```
┌─────────────────────────────────────────────────────┐
│  TICKER BAR: KOSPI 현재가·등락률 | 날짜 | 버전        │  실시간
├─────────────────────────────────────────────────────┤
│  HEADER: InvestScan 주간 투자 분析  {DATE}            │
├──────────────────────┬──────────────────────────────┤
│  P6 포트폴리오 카드  │  KOSPI 4주 전망 게이지          │
│  탭: Cat A / Cat B   │  Low / Base / High 범위        │
│      / P6 미통과     │  (Chart.js 수평 게이지)         │
│  종목카드:           │                                │
│  - 종목명 (코드)     │                                │
│  - 현재가 · 등락률   │                                │
│  - 섹터 · 신뢰도     │                                │
│  - 목표가: —         │                                │
├──────────────────────┴──────────────────────────────┤
│  에이전트 가중치 도넛     │  리스크 시나리오 수평 바       │
│  tech/korea/val/macro/risk│  시나리오별 확률 시각화       │
├────────────────────────────────────────────────────┤
│  섹터 방향 그리드                                    │
│  bullish 🟢 / neutral ⚪ / bearish 🔴               │
└─────────────────────────────────────────────────────┘
```

---

## 4. 데이터 소스 매핑

| 화면 요소 | 데이터 소스 | 파싱 방법 |
|-----------|------------|----------|
| KOSPI 현재가·등락률 (ticker) | `naver_finance.py` → `fetch_kospi_index()` 신규 함수 추가 | Naver Finance 지수 URL 스크래핑 |
| Cat A/B/미통과 종목 목록 | `output/temp/confirmed_watchlist_{D}.json` | JSON |
| 종목명·현재가·등락률 | `naver_finance.py` | 실시간 조회 (Cat A+B만) |
| KOSPI Low/Base/High 범위 | `output/reports/weekly-report-{D}.md` | 정규식 (섹션 2.3 테이블) |
| 에이전트 가중치 | `confirmed_watchlist_{D}.json` → `.agent_weights` | JSON |
| 리스크 시나리오 | `output/reports/weekly-report-{D}.md` | 정규식 (섹션 5) |
| 섹터 방향 | `confirmed_watchlist_{D}.json` → `.base_sector_directions` | JSON |
| 파이프라인 버전 | `output/reports/weekly-report-{D}.md` 헤더 | 정규식 |

### 목표가·DCA 진입가

이번 버전에서 `—`로 표시한다. 향후 `extract_targets.py` 파이프라인 단계 추가 후 연동 예정.

---

## 5. 실행 인터페이스

```bash
# HTML만 생성
python3 -m investscan.export_report --date 2026-04-09 --formats html

# 전체 포맷 (기존 + 신규)
python3 -m investscan.export_report --date 2026-04-09 --formats txt,pdf,html

# 실시간 조회 생략 (테스트·오프라인용)
python3 -m investscan.export_report --date 2026-04-09 --formats html --no-live
```

**출력 경로:**
```
~/Desktop/Ai_works/output/투자분析제안/
├── {DATE}_주간투자분析.txt        (기존)
├── {DATE}_주간투자분析.pdf        (기존)
└── {DATE}_주간투자분析_대시보드.html  (신규)
```

---

## 6. 에러 처리

| 상황 | 처리 방식 |
|------|----------|
| `confirmed_watchlist_{D}.json` 없음 | 즉시 중단 + 명확한 에러 메시지 |
| `naver_finance.py` 네트워크 실패 (종목 또는 KOSPI 지수) | 해당 항목 `—` 표시, 나머지 정상 생성 |
| `weekly-report.md` 정규식 매칭 실패 | KOSPI 게이지 섹션 `데이터 없음` 배지로 대체 |
| 리스크 시나리오 파싱 실패 | 해당 섹션 완전 제거 (빈 카드 없음) |
| 특정 종목 실시간 조회 실패 | 해당 종목만 `—`, 나머지 정상 표시 |

**원칙:** 데이터 일부가 없어도 대시보드는 항상 생성된다.

---

## 7. 디자인 시스템

기존 `output/reports/2026-04-09-system-audit-report.html` 팔레트 이식:

```css
--bg:      #06090f
--bg-2:    #0c1220
--gold:    #f5c518
--green:   #22c55e
--red:     #ef4444
--text:    #e2e8f0
--display: 'Bebas Neue'
--body:    'Outfit'
--mono:    'DM Mono'
```

효과: 노이즈 오버레이, 스캔라인, 골드 ticker bar

**기술 스택:** 순수 HTML/CSS/JavaScript + Chart.js CDN — 단일 자체완결 파일, 외부 의존성 없음 (CDN 제외)

---

## 8. 범위 외 (이번 버전)

- 목표가·DCA 진입가 자동 추출 (`extract_targets.py`)
- Streamlit 또는 서버 기반 대시보드
- 히스토리 비교 (주차별 추이)
