# Context Data Completeness Fix — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Python이 계산한 섹터 방향(`sector_directions`), 핵심 액션(`action_item`), 체크리스트(`action_checklist`), 매크로 요약(`macro_summary`)을 LLM 프롬프트까지 완전히 전달하고, 신호 텍스트에 psst_score를 포함시킨다.

**Architecture:** `weekly_orchestrator.py`의 context_data 딕셔너리에 현재 누락된 `InvestmentMeta` 필드를 추가하고, `intelligence_engine.py`의 `_build_user_prompt`에 해당 필드를 렌더링하는 섹션을 추가한다. 신호는 `str` 대신 `"title (score=NN)" 형식`으로 변환하여 LLM이 신뢰도를 파악할 수 있게 한다.

**Tech Stack:** Python 3.12, pytest, investscan.schema.InvestmentMeta, anthropic SDK (LLM 호출)

---

## 수정 대상 파일 요약

| 파일 | 변경 유형 | 변경 내용 |
|------|---------|---------|
| `investscan/weekly_orchestrator.py` | Modify | context_data에 `sector_directions`, `action_item`, `action_checklist`, `macro_summary` 추가; 신호에 psst_score 포함 |
| `investscan/intelligence_engine.py` | Modify | `_build_user_prompt`에 `## Sector Directions`, `## Action Guidance` 섹션 추가 |
| `tests/test_intelligence_engine.py` | Modify | `CONTEXT_A`, `CONTEXT_B` fixture에 새 필드 추가; 프롬프트 내용 검증 테스트 추가 |
| `tests/test_weekly_orchestrator.py` | 변경 없음 | (weekly_orchestrator 테스트는 _build_context_data를 직접 단위 테스트하지 않음) |

---

## Task 1: `weekly_orchestrator.py` — context_data 확장

**Files:**
- Modify: `investscan/weekly_orchestrator.py:362-378`

### 변경 전 (현재 코드)

```python
return {
    "category": category,
    "stock_code": stock_code,
    "stock_name": stock_name,
    "analysis_date": date.today().isoformat(),
    "yoy_revenue_growth": _val(financials.yoy_revenue_growth),
    "yoy_op_income_growth": _val(financials.yoy_op_income_growth),
    "latest_quarter": financials.latest_quarter or DATA_UNAVAILABLE,
    "per_current": _val(financials.per_current),
    "per_sector_avg": _val(financials.per_sector_avg),
    "foreign_flow_4w": _val(financials.foreign_flow_4w),
    "rate_direction": meta.rate_direction,
    "inflation_trend": meta.inflation_trend,
    "risk_appetite": meta.risk_appetite,
    "usd_strength": meta.usd_strength,
    "top_signals": top_signals,
}
```

### 변경 후

```python
return {
    "category": category,
    "stock_code": stock_code,
    "stock_name": stock_name,
    "analysis_date": date.today().isoformat(),
    "yoy_revenue_growth": _val(financials.yoy_revenue_growth),
    "yoy_op_income_growth": _val(financials.yoy_op_income_growth),
    "latest_quarter": financials.latest_quarter or DATA_UNAVAILABLE,
    "per_current": _val(financials.per_current),
    "per_sector_avg": _val(financials.per_sector_avg),
    "foreign_flow_4w": _val(financials.foreign_flow_4w),
    "rate_direction": meta.rate_direction,
    "inflation_trend": meta.inflation_trend,
    "risk_appetite": meta.risk_appetite,
    "usd_strength": meta.usd_strength,
    "sector_directions": meta.sector_directions,        # {"technology": "bullish", ...}
    "macro_summary": meta.macro_summary or DATA_UNAVAILABLE,
    "action_item": meta.action_item or DATA_UNAVAILABLE,
    "action_checklist": meta.action_checklist,          # list[str]
    "top_signals": top_signals,
}
```

### 신호 문자열 생성 함수 수정 (psst_score 포함)

`_load_top_signals_from_envscan` 함수의 타이틀 생성 부분을 수정하여 점수를 포함시킨다.

**변경 전 (`weekly_orchestrator.py:395-400`):**
```python
top = sorted(signals, key=lambda s: s["psst_score"], reverse=True)[:top_n]
titles = []
for s in top:
    title = (s.get("title") or s["summary"]).split(".")[0].strip()[:80]
    if title:
        titles.append(title)
```

**변경 후:**
```python
top = sorted(signals, key=lambda s: s["psst_score"], reverse=True)[:top_n]
titles = []
for s in top:
    title = (s.get("title") or s["summary"]).split(".")[0].strip()[:80]
    score = s.get("psst_score", 0)
    if title:
        titles.append(f"{title} (score={score})")
```

**GNews 신호도 동일하게 수정 (`weekly_orchestrator.py:423-424`):**

**변경 전:**
```python
summaries = [s["summary"][:80] for s in top if s.get("summary")]
```

**변경 후:**
```python
summaries = [
    f"{s['summary'][:80]} (score={s.get('psst_score', 0)})"
    for s in top if s.get("summary")
]
```

- [ ] **Step 1: context_data에 4개 필드 추가**

`investscan/weekly_orchestrator.py`의 `return {` 블록(362-378줄)에서 `"usd_strength"` 다음 줄에 아래 4줄을 추가한다:

```python
"sector_directions": meta.sector_directions,
"macro_summary": meta.macro_summary or DATA_UNAVAILABLE,
"action_item": meta.action_item or DATA_UNAVAILABLE,
"action_checklist": meta.action_checklist,
```

- [ ] **Step 2: EnvScan 신호에 psst_score 포함**

`_load_top_signals_from_envscan` 함수 내부(395-400줄)에서:
- `titles.append(title)` → `titles.append(f"{title} (score={score})")`
- `score = s.get("psst_score", 0)` 줄 추가

- [ ] **Step 3: GNews 신호에 psst_score 포함**

`_load_gnews_signals` 함수 내부(423-424줄)에서:
- `summaries = [s["summary"][:80] for s in top if s.get("summary")]`
- → `summaries = [f"{s['summary'][:80]} (score={s.get('psst_score', 0)})" for s in top if s.get("summary")]`

- [ ] **Step 4: 변경 후 기존 테스트 실행 확인**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python -m pytest tests/test_weekly_orchestrator.py -q --tb=short
```
Expected: 모든 기존 테스트 PASS

- [ ] **Step 5: commit**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
git add investscan/weekly_orchestrator.py
git commit -m "feat: add sector_directions, action fields, psst_score to context_data

- sector_directions, macro_summary, action_item, action_checklist now
  forwarded from InvestmentMeta to LLM context_data
- top_signals now include psst_score for LLM reliability awareness
- closes context data completeness gap identified in system audit"
```

---

## Task 2: `intelligence_engine.py` — 프롬프트 섹션 추가

**Files:**
- Modify: `investscan/intelligence_engine.py:130-171`

### 변경 전 (`_build_user_prompt` 현재 구조)

```
Stock: ... Category ...
Analysis date: ...

## Financial Context
YoY Revenue Growth: ...
YoY Op.Income Growth: ...
Latest Quarter: ...
PER Current: ...
PER Sector Avg: ...
Foreign Flow 4w: ...

## Macro Environment
Rate Direction: ...
Inflation Trend: ...
Risk Appetite: ...
USD Strength: ...

## STEEPs Signals
Top Signals: [...]
```

### 변경 후 (추가 섹션 2개)

```
Stock: ... Category ...
Analysis date: ...

## Financial Context
...동일...

## Macro Environment
Rate Direction: ...
Inflation Trend: ...
Risk Appetite: ...
USD Strength: ...
Macro Summary: ...                    ← 신규

## Sector Directions                  ← 신규 섹션
technology: bullish
semiconductor: bullish
energy: bearish
...

## Weekly Action Guidance             ← 신규 섹션
Action: ...이번 주 핵심 행동...
Checklist:
- ...
- ...

## STEEPs Signals
Top Signals: [...] (with scores)
```

- [ ] **Step 1: 실패 테스트 먼저 작성**

`tests/test_intelligence_engine.py` 파일의 `TestBuildPrompt` 클래스에 다음 테스트를 추가한다:

```python
def test_contains_sector_directions(self):
    ctx = {**CONTEXT_A, "sector_directions": {"technology": "bullish", "energy": "bearish"}}
    prompt = build_prompt(ctx)
    assert "Sector Directions" in prompt
    assert "technology: bullish" in prompt
    assert "energy: bearish" in prompt

def test_contains_action_item(self):
    ctx = {**CONTEXT_A, "action_item": "IT 섹터 외국인 수급 확인 후 비중 조절"}
    prompt = build_prompt(ctx)
    assert "Action:" in prompt
    assert "IT 섹터" in prompt

def test_contains_action_checklist(self):
    ctx = {**CONTEXT_A, "action_checklist": ["FOMC 일정 확인", "VIX 모니터링"]}
    prompt = build_prompt(ctx)
    assert "Checklist:" in prompt
    assert "FOMC 일정 확인" in prompt

def test_contains_macro_summary(self):
    ctx = {**CONTEXT_A, "macro_summary": "Rate hold, moderate risk appetite, USD strong"}
    prompt = build_prompt(ctx)
    assert "Macro Summary:" in prompt
    assert "Rate hold" in prompt

def test_empty_sector_directions_skipped(self):
    ctx = {**CONTEXT_A, "sector_directions": {}}
    prompt = build_prompt(ctx)
    # 빈 섹터 딕셔너리면 섹션 생략
    assert "Sector Directions" not in prompt

def test_empty_action_checklist_skipped(self):
    ctx = {**CONTEXT_A, "action_checklist": []}
    prompt = build_prompt(ctx)
    assert "Checklist:" not in prompt
```

- [ ] **Step 2: 테스트 실행 → FAIL 확인**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python -m pytest tests/test_intelligence_engine.py::TestBuildPrompt::test_contains_sector_directions -v
```
Expected: FAIL — "Sector Directions" not in prompt

- [ ] **Step 3: `_build_user_prompt` 구현 수정**

`investscan/intelligence_engine.py`의 `_build_user_prompt` 함수에서 `## Macro Environment` 섹션 직후, `## STEEPs Signals` 직전에 다음을 삽입한다:

현재:
```python
prompt_lines = [
    ...
    "## Macro Environment",
    f"Rate Direction: {context_data.get('rate_direction', 'N/A')}",
    f"Inflation Trend: {context_data.get('inflation_trend', 'N/A')}",
    f"Risk Appetite: {context_data.get('risk_appetite', 'N/A')}",
    f"USD Strength: {context_data.get('usd_strength', 'N/A')}",
    "",
    "## STEEPs Signals",
    f"Top Signals: {context_data.get('top_signals', [])}",
]
```

변경 후:
```python
prompt_lines = [
    ...
    "## Macro Environment",
    f"Rate Direction: {context_data.get('rate_direction', 'N/A')}",
    f"Inflation Trend: {context_data.get('inflation_trend', 'N/A')}",
    f"Risk Appetite: {context_data.get('risk_appetite', 'N/A')}",
    f"USD Strength: {context_data.get('usd_strength', 'N/A')}",
    f"Macro Summary: {context_data.get('macro_summary', 'N/A')}",
]

# Sector Directions (조건부 — 비어 있으면 섹션 생략)
sector_dirs: dict = context_data.get("sector_directions") or {}
if sector_dirs:
    prompt_lines += ["", "## Sector Directions"]
    for sector_name, direction in sector_dirs.items():
        prompt_lines.append(f"{sector_name}: {direction}")

# Weekly Action Guidance (조건부)
action_item: str = context_data.get("action_item") or ""
action_checklist: list = context_data.get("action_checklist") or []
if action_item and action_item != "DATA_UNAVAILABLE":
    prompt_lines += ["", "## Weekly Action Guidance", f"Action: {action_item}"]
    if action_checklist:
        prompt_lines.append("Checklist:")
        for item in action_checklist:
            prompt_lines.append(f"- {item}")

prompt_lines += [
    "",
    "## STEEPs Signals",
    f"Top Signals: {context_data.get('top_signals', [])}",
]
```

- [ ] **Step 4: 테스트 실행 → PASS 확인**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python -m pytest tests/test_intelligence_engine.py -q --tb=short
```
Expected: 모든 테스트 PASS (기존 + 신규 6개)

- [ ] **Step 5: commit**

```bash
git add investscan/intelligence_engine.py tests/test_intelligence_engine.py
git commit -m "feat: add sector_directions and action guidance sections to LLM prompt

- _build_user_prompt now renders ## Sector Directions and
  ## Weekly Action Guidance sections when data is present
- Sections are conditionally skipped when empty (no padding noise)
- 6 new tests verify prompt completeness"
```

---

## Task 3: 테스트 fixture 업데이트 — CONTEXT_A/B에 새 필드 반영

**Files:**
- Modify: `tests/test_intelligence_engine.py:25-53`

현재 `CONTEXT_A`와 `CONTEXT_B` fixture는 새 필드(`sector_directions`, `action_item` 등)가 없는 상태. 기존 테스트는 통과하지만, 누락 필드가 있는 fixture로 계속 사용하면 다른 테스트가 실제 동작을 검증 못 함.

- [ ] **Step 1: `CONTEXT_A` fixture에 새 필드 추가**

`tests/test_intelligence_engine.py`의 `CONTEXT_A` 딕셔너리에 아래를 추가한다:

```python
CONTEXT_A = {
    "category": "A",
    "stock_code": "005930",
    "stock_name": "Samsung Electronics",
    "analysis_date": "2026-03-29",
    "yoy_revenue_growth": 0.083,
    "yoy_op_income_growth": 0.342,
    "latest_quarter": "2025Q4",
    "per_current": 10.2,
    "per_sector_avg": 14.2,
    "foreign_flow_4w": 380.0,
    "rate_direction": "hold",
    "inflation_trend": "cooling",
    "risk_appetite": "moderate",
    "usd_strength": "strong",
    "sector_directions": {"technology": "bullish", "semiconductor": "bullish", "financials": "neutral"},
    "macro_summary": "Rate hold with moderate risk appetite; USD strong; tech bullish",
    "action_item": "semiconductor 섹터 외국인 수급 방향 확인 후 비중 조절 검토",
    "action_checklist": ["FOMC 의사록 확인", "VIX 20 이하 유지 여부 점검"],
    "top_signals": ["AI semiconductor demand surge (score=85)", "Fed patience on rate cuts (score=72)"],
}
```

- [ ] **Step 2: `CONTEXT_B` fixture에 새 필드 추가**

```python
CONTEXT_B = {
    "category": "B",
    "stock_code": "035420",
    "stock_name": "NAVER",
    "analysis_date": "2026-03-29",
    "rate_direction": "hold",
    "inflation_trend": "cooling",
    "risk_appetite": "moderate",
    "usd_strength": "strong",
    "sector_directions": {"technology": "bullish", "communication": "neutral"},
    "macro_summary": "Rate hold; tech theme intact",
    "action_item": "technology 섹터 외국인 수급 방향 확인 후 비중 조절 검토",
    "action_checklist": ["AI 테마 모멘텀 지속 여부 확인"],
    "top_signals": ["AI commerce theme (score=80)", "HyperCLOVA X integration (score=68)"],
}
```

- [ ] **Step 3: 전체 테스트 실행**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python -m pytest tests/test_intelligence_engine.py -q --tb=short
```
Expected: 전체 PASS

- [ ] **Step 4: commit**

```bash
git add tests/test_intelligence_engine.py
git commit -m "test: update CONTEXT_A/B fixtures with complete context_data fields

- Fixtures now include sector_directions, macro_summary, action_item,
  action_checklist, and psst_score-annotated top_signals
- Ensures all tests exercise the full context_data surface"
```

---

## Task 4: 통합 검증

- [ ] **Step 1: 전체 테스트 스위트 실행**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python -m pytest -q --tb=short
```
Expected: 전체 PASS (신규 테스트 포함)

- [ ] **Step 2: dry-run으로 실제 파이프라인 실행**

```bash
cd /Users/kylechoi/Desktop/Ai_works/vibe-practice/01.invest_test
python run_m05.py --dry-run 2>&1 | head -60
```
Expected: 오류 없이 실행, context_data에 sector_directions 포함된 로그 확인

- [ ] **Step 3: 프롬프트 내용 spot-check**

```bash
python -c "
from investscan.intelligence_engine import build_prompt
ctx = {
    'category': 'A', 'stock_code': '005930', 'stock_name': 'Samsung',
    'analysis_date': '2026-04-09',
    'rate_direction': 'hold', 'inflation_trend': 'cooling',
    'risk_appetite': 'moderate', 'usd_strength': 'strong',
    'sector_directions': {'technology': 'bullish', 'semiconductor': 'bullish'},
    'macro_summary': 'Rate hold, moderate risk',
    'action_item': 'tech 섹터 수급 확인',
    'action_checklist': ['FOMC 확인', 'VIX 모니터링'],
    'top_signals': ['AI demand (score=85)', 'Fed hold (score=72)'],
}
print(build_prompt(ctx))
"
```
Expected: 출력에 `## Sector Directions`, `technology: bullish`, `## Weekly Action Guidance`, `Action:` 포함

- [ ] **Step 4: final commit (필요시)**

```bash
git add -p
git commit -m "chore: final integration verification passed"
```
