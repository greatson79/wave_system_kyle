---
description: "투자분석을 시작하자' 명령 시 실행. EnvironmentScan → GlobalNews → 9인 에이전트 다회차 토론 → 마스터 종합 → PDF 리포트."
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

## Phase 3 — Round 1: 병렬 분석 (9인 에이전트 동시 실행)

Phase 3 진입 시 상태 기록:
```bash
python3 -m investscan.pipeline_tracker --phase phase_3 --status running
```

아래 9개 에이전트를 **모두 동시에** background로 실행한다 (5인 횡단면 + 4인 섹터 전문).
각 에이전트 실행 전 running, 완료 후 completed를 기록하도록 prompt에 포함한다:

```
Agent("analyst-macro",      name="macro",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent macro --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 거시경제 분석을 output/temp/round1_macro_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent macro --status completed` 실행.")
Agent("analyst-tech",       name="tech",       run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent tech --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 기술섹터 분석을 output/temp/round1_tech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent tech --status completed` 실행.")
Agent("analyst-korea",      name="korea",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent korea --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 한국시장 분석을 output/temp/round1_korea_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent korea --status completed` 실행.")
Agent("analyst-valuation",  name="valuation",  run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent valuation --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 밸류에이션 분석을 output/temp/round1_valuation_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent valuation --status completed` 실행.")
Agent("analyst-risk",       name="risk",       run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent risk --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 리스크 분석을 output/temp/round1_risk_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent risk --status completed` 실행.")
Agent("analyst-energy",     name="energy",     run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent energy --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 에너지전환·전력인프라 분석을 output/temp/round1_energy_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent energy --status completed` 실행.")
Agent("analyst-defense",    name="defense",    run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent defense --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 방산·조선·소재 분석을 output/temp/round1_defense_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent defense --status completed` 실행.")
Agent("analyst-biotech",    name="biotech",    run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent biotech --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 바이오·헬스케어 분석을 output/temp/round1_biotech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent biotech --status completed` 실행.")
Agent("analyst-consumer",   name="consumer",   run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent consumer --status running` 실행. output/temp/agent_context_{DATE}.json을 읽고 Round 1 소비재·내수·엔터·자동차 분석을 output/temp/round1_consumer_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_3 --agent consumer --status completed` 실행.")
```

9개 모두 완료될 때까지 대기.

---

## Phase 4 — Round 2/3: 다회차 교차 검토 토론 (9인 에이전트)

Round 1 결과물 9개가 모두 존재하는지 확인:
```bash
ls output/temp/round1_*_{DATE}.json
python3 -m investscan.pipeline_tracker --phase phase_4 --status running
```

### Round 2 (각 에이전트가 다른 에이전트들의 Round 1 결과를 읽고 반론/동의/수정)

```
Agent("analyst-macro",     name="macro-r2",     run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent macro --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_macro_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent macro --status completed` 실행.")
Agent("analyst-tech",      name="tech-r2",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent tech --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_tech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent tech --status completed` 실행.")
Agent("analyst-korea",     name="korea-r2",     run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent korea --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_korea_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent korea --status completed` 실행.")
Agent("analyst-valuation", name="valuation-r2", run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent valuation --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_valuation_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent valuation --status completed` 실행.")
Agent("analyst-risk",      name="risk-r2",      run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent risk --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 다른 에이전트들의 관점을 검토하여 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_risk_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent risk --status completed` 실행.")
Agent("analyst-energy",    name="energy-r2",    run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent energy --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_energy_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent energy --status completed` 실행.")
Agent("analyst-defense",   name="defense-r2",   run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent defense --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_defense_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent defense --status completed` 실행.")
Agent("analyst-biotech",   name="biotech-r2",   run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent biotech --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_biotech_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent biotech --status completed` 실행.")
Agent("analyst-consumer",  name="consumer-r2",  run_in_background=True, prompt="먼저 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent consumer --status running` 실행. output/temp/round1_*.json 파일을 모두 읽고, 자신의 분석을 수정하거나 반론을 제기한 후 output/temp/round2_consumer_{DATE}.json에 작성. 완료 후 `python3 -m investscan.pipeline_tracker --phase phase_4 --agent consumer --status completed` 실행.")
```

9개 모두 완료될 때까지 대기.

### Round 3 수렴 판정 (P6 — Python이 결정)

Round 2 완료 후, Python이 토론 수렴 여부를 판정한다:
```bash
python3 -m investscan.debate_convergence --date {DATE} --current-round 2
```

출력 토큰에 따라 **결정론적 분기**:
- `CONVERGED` 출력 → 토론 종료. **Round 3 건너뛰고 Phase 4.5로 진행.** (의견이 충분히 안정됨)
- `CONTINUE` 출력 → **아래 Round 3 실행.**
- `DIVERGED` 출력 → 발산 감지. Python이 round_final 댐핑 파일을 작성함. **Round 3 건너뛰고 Phase 4.5로 진행.**

### Round 3 (CONTINUE인 경우만 — 각 에이전트가 다른 에이전트들의 Round 2 결과를 읽고 재수정)

```
Agent("analyst-macro",     name="macro-r3",     run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고, 다른 에이전트들의 수정된 입장을 검토하여 재수정한 후 output/temp/round3_macro_{DATE}.json에 작성.")
Agent("analyst-tech",      name="tech-r3",      run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_tech_{DATE}.json에 작성.")
Agent("analyst-korea",     name="korea-r3",     run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_korea_{DATE}.json에 작성.")
Agent("analyst-valuation", name="valuation-r3", run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_valuation_{DATE}.json에 작성.")
Agent("analyst-risk",      name="risk-r3",      run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_risk_{DATE}.json에 작성.")
Agent("analyst-energy",    name="energy-r3",    run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_energy_{DATE}.json에 작성.")
Agent("analyst-defense",   name="defense-r3",   run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_defense_{DATE}.json에 작성.")
Agent("analyst-biotech",   name="biotech-r3",   run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_biotech_{DATE}.json에 작성.")
Agent("analyst-consumer",  name="consumer-r3",  run_in_background=True, prompt="output/temp/round2_*.json 파일을 모두 읽고 재수정한 후 output/temp/round3_consumer_{DATE}.json에 작성.")
```

9개 모두 완료 후, 최종 수렴 상태 기록 (진단용, 분기 없음):
```bash
python3 -m investscan.debate_convergence --date {DATE} --current-round 3
```

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

9인 에이전트의 최종 라운드 결과(round_final > round3 > round2 우선)와 토론 수렴 상태를 모두 읽는다:
```bash
python3 -c "
import json
from pathlib import Path
from datetime import date
today = date.today().isoformat()
agents = ['tech','korea','valuation','macro','risk','energy','defense','biotech','consumer']
results = {}
for a in agents:
    for tag in ['round_final','round3','round2','round1']:
        f = Path('output/temp')/f'{tag}_{a}_{today}.json'
        if f.exists():
            results[a] = {'_source': tag, **json.loads(f.read_text())}
            break
# 토론 수렴 상태 + 미해결 충돌
ds = Path('output/temp')/f'debate_status_{today}.json'
debate = json.loads(ds.read_text()) if ds.exists() else {}
print(json.dumps({'agents': results, 'debate_status': debate}, ensure_ascii=False, indent=2))
"
```

9인의 다회차 토론 결과를 종합하여 다음 구조의 리포트 마크다운을 `output/reports/weekly-report-{DATE}.md`에 작성한다:

### 리포트 구조

1. **Executive Summary** — 토론 합의점 + 핵심 투자 방향 (3-5줄)
2. **거시환경 분석 + 4주 전망** — macro 에이전트 최종 라운드 기반
3. **기술·AI 섹터 심층 분석** — tech 에이전트 최종 라운드 기반
4. **섹터 전문 분석** — energy(에너지전환·전력인프라), defense(방산·조선), biotech(바이오), consumer(소비·엔터·자동차) 에이전트 최종 라운드 기반
5. **한국 시장 수급 + 리스크 시나리오** — korea + risk 에이전트 최종 라운드 기반
6. **종목별 밸류에이션** — valuation 에이전트 기반 + Naver Finance 실시간가
7. **에이전트 토론 요약** — `debate_status.unresolved_conflicts`의 의견 불일치(±0.15 이상 차이 섹터)와 수렴 과정을 명시
8. **핵심 예측 3가지** — 날짜·수치 명시, 근거 포함
9. **분할매수 진입 가격대** — DCA 테이블 (Cat A 종목)
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
- Phase 3/4 에이전트 중 일부 실패 → 나머지로 계속. agent_consensus가 정족수(quorum, 가중치 60% 미만 시 경고)를 판정하며, 누락 에이전트는 0.0 기여로 보수적 처리됨 (재정규화 안 함 — 단일 에이전트 독재 방지)
- Phase 5 종합 시 최종 라운드 우선순위: round_final > round3 > round2 > round1 (에이전트별 사용 가능한 최신 라운드)
- Round 3는 조건부 — debate_convergence가 CONVERGED/DIVERGED 판정 시 생략됨
