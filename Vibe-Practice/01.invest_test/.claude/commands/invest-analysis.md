---
description: "투자분석을 시작하자' 명령 시 실행. EnvironmentScan → GlobalNews → 5인 에이전트 토론 → 마스터 종합 → PDF 리포트."
---

# 투자분석 멀티에이전트 파이프라인

## 이 커맨드의 역할

사용자가 **"투자분석을 시작하자"** (또는 유사 표현)를 입력하면 이 커맨드가 실행된다.
아래 6개 Phase를 순서대로 실행하여 최종 PDF 리포트를 생성한다.

---

## Phase 0 — 현황 확인

```bash
python3 -m investscan.pipeline_tracker --reset
python3 -m investscan.pipeline_tracker --phase phase_0 --status running
python3 -m investscan.orchestrate --status
python3 -m investscan.pipeline_tracker --phase phase_0 --status completed
```

데이터 신선도 자동 판단 (아래 명령 실행):
```bash
python3 -m investscan.orchestrate --needs-refresh
```

**분기 규칙 (반드시 준수):**
- 출력이 `FRESH` → "기존 데이터를 사용합니다 (3일 이내)" 출력 후 **Phase 2로 바로 점프** (Phase 1 건너뜀)
- 출력이 `STALE` → "최신 데이터 수집을 시작합니다" 출력 후 **Phase 1 실행**

---

## Phase 1 — 데이터 수집

**EnvironmentScan 실행** (bash로 직접 실행):
```bash
python3 -m investscan.pipeline_tracker --phase phase_1_envscan --status running
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/EnvironmentScan-system-main-v4-main/env-scanning && python3 scripts/run_multi_source_scan.py --days-back 7
python3 -m investscan.pipeline_tracker --phase phase_1_envscan --status completed
```

완료 후 **GlobalNews 실행**:
```bash
python3 -m investscan.pipeline_tracker --phase phase_1_gnews --status running
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/GlobalNews-Crawling-AgenticWorkflow && .venv/bin/python main.py --mode full --sites donga,yna,chosun,mk,hankyung,mt
python3 -m investscan.pipeline_tracker --phase phase_1_gnews --status completed
```

> 소요 시간 안내: "EnvironmentScan 약 10-20분, GlobalNews 약 30-90분 소요됩니다."
> 실패 시: 기존 데이터로 계속 진행 (경고만 출력). 실패 시 status를 failed로 기록:
> `python3 -m investscan.pipeline_tracker --phase phase_1_envscan --status failed`

---

## Phase 2 — 컨텍스트 준비

```bash
python3 -m investscan.orchestrate --prepare-only
```

> `orchestrate.py`가 내부적으로 phase_2 running/completed를 기록함.

`output/temp/agent_context_{DATE}.json` 생성 확인.

---

## Phase 3 — Round 1: 병렬 분석 (5인 에이전트 동시 실행)

Phase 3 진입 시 상태 기록:
```bash
python3 -m investscan.pipeline_tracker --phase phase_3 --status running
```

아래 5개 에이전트를 **모두 동시에** background로 실행한다.
각 에이전트 실행 전 running, 완료 후 completed를 기록하도록 prompt에 포함한다:

```
Agent("analyst-macro",      name="macro",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent macro --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 거시경제 분석을 output/temp/round1_macro_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent macro --status completed` 실행.")
Agent("analyst-tech",       name="tech",       run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent tech --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 기술섹터 분석을 output/temp/round1_tech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent tech --status completed` 실행.")
Agent("analyst-korea",      name="korea",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent korea --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 한국시장 분석을 output/temp/round1_korea_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent korea --status completed` 실행.")
Agent("analyst-valuation",  name="valuation",  run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent valuation --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 밸류에이션 분석을 output/temp/round1_valuation_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent valuation --status completed` 실행.")
Agent("analyst-risk",       name="risk",       run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent risk --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 리스크 분석을 output/temp/round1_risk_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent risk --status completed` 실행.")
```

5개 모두 완료될 때까지 대기.

---

## Phase 4 — Round 2: 교차 검토 토론 (5인 에이전트 동시 실행)

Round 1 결과물 5개가 모두 존재하는지 확인:
```bash
ls output/temp/round1_*_{DATE}.json
python3 -m investscan.pipeline_tracker --phase phase_4 --status running
```

확인 후 Round 2 실행 (각 에이전트가 다른 에이전트들의 Round 1 결과를 읽고 반론/동의/수정):

```
Agent("analyst-macro",     name="macro-r2",     run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent macro --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_macro_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent macro --status completed` 실행.")
Agent("analyst-tech",      name="tech-r2",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent tech --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_tech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent tech --status completed` 실행.")
Agent("analyst-korea",     name="korea-r2",     run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent korea --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_korea_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent korea --status completed` 실행.")
Agent("analyst-valuation", name="valuation-r2", run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent valuation --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_valuation_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent valuation --status completed` 실행.")
Agent("analyst-risk",      name="risk-r2",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent risk --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_risk_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent risk --status completed` 실행.")
```

5개 모두 완료될 때까지 대기.

---

## Phase 4.5 — Python 종목 확정 (P6 판정 단계)

Round 2 완료 즉시 실행. LLM이 아닌 Python이 최종 종목 유니버스를 결정한다.

```bash
python3 -m investscan.pipeline_tracker --phase phase_4 --status completed
python3 -m investscan.agent_consensus --date {DATE}
```

`output/temp/confirmed_watchlist_{DATE}.json` 생성을 확인한다.
생성 실패 시: "⚠️ confirmed_watchlist 생성 실패 — Phase 5에서 종목 추천 전면 보류"

---

## Phase 5 — 마스터 종합 (Claude Code 직접 수행)

```bash
python3 -m investscan.pipeline_tracker --phase phase_5 --status running
```

**종목 제약 규칙 (절대 기준 — P6):**
먼저 confirmed_watchlist를 읽는다:
```bash
python3 -c "
import json
from pathlib import Path
from datetime import date
wl = Path(f'output/temp/confirmed_watchlist_{date.today().isoformat()}.json')
if wl.exists():
    data = json.loads(wl.read_text())
    print('Cat A:', data['cat_a'])
    print('Cat B:', data['cat_b'])
    print('Sector confidence:', json.dumps(data['final_sector_confidence'], indent=2))
else:
    print('WARN: confirmed_watchlist not found')
"
```

- **Cat A 종목만** 리포트 주요 추천으로 기재 가능
- **Cat B 종목**은 "테마 관심 종목"으로 기재 가능
- **confirmed_watchlist 외 종목**을 추천할 경우 반드시 명시:
  `"⚠️ 비확정 종목 — Python 임계값 미달, 서사적 언급만 (P6 미통과)"`
- 이 규칙 위반 = P6 원칙 위반으로 간주

Round 2 결과물 5개를 모두 읽는다:
```bash
python3 -c "
import json
from pathlib import Path
from datetime import date
today = date.today().isoformat()
results = {}
for f in Path('output/temp').glob(f'round2_*_{today}.json'):
    agent = f.stem.replace(f'round2_','').replace(f'_{today}','')
    results[agent] = json.loads(f.read_text())
print(json.dumps(results, ensure_ascii=False, indent=2))
"
```

5인의 토론 결과를 종합하여 다음 구조의 리포트 마크다운을 `output/reports/weekly-report-{DATE}.md`에 작성한다:

### 리포트 구조

1. **Executive Summary** — 토론 합의점 + 핵심 투자 방향 (3-5줄)
2. **거시환경 분석 + 4주 전망** — macro 에이전트 Round 2 기반
3. **기술·AI 섹터 심층 분석** — tech 에이전트 Round 2 기반
4. **한국 시장 수급 분석** — korea 에이전트 Round 2 기반
5. **리스크 시나리오** — risk 에이전트 Round 2 기반
6. **종목별 밸류에이션** — valuation 에이전트 Round 2 기반 + Naver Finance 실시간가
7. **에이전트 토론 요약** — 주요 의견 불일치 및 합의 과정
8. **핵심 예측 3가지** — 날짜·수치 명시, 근거 포함
9. **분할매수 진입 가격대** — DCA 테이블
10. **면책 조항**

---

## Phase 6 — PDF 생성

리포트 작성 완료 후:
```bash
python3 -m investscan.pipeline_tracker --phase phase_5 --status completed
python3 -m investscan.pipeline_tracker --phase phase_6 --status running
python3 -m investscan.export_report --date {DATE} --enrich
python3 -m investscan.pipeline_tracker --phase phase_6 --status completed
```

완료 후 사용자에게 경로 안내:
```
분석 완료:
  PDF: ~/Desktop/Ai_works/output/투자분석제안/{DATE}_주간투자분석.pdf
  MD:  output/reports/weekly-report-{DATE}.md
```

---

## 오류 처리 규칙

- Phase 1 실패 → 기존 데이터로 Phase 2부터 계속
- Phase 3/4 에이전트 중 1개 실패 → 나머지 4개로 계속 (실패 에이전트 결과는 "분석 불가"로 표시)
- Phase 5 종합 시 Round 2 파일 없으면 Round 1 파일 사용
