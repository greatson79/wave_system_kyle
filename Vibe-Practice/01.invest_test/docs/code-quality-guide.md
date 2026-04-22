# InvestScan Code Quality Guide

> Version: v3.6 | Covers: @reviewer L2 checklist, TDD coverage tiers, quality gate logic

---

## 1. TDD Coverage Tiers

| Tier | Modules | Required Coverage |
|------|---------|-------------------|
| P1 Critical | `compliance_filter`, `synthesize_macro`, `steeps_classifier`, `stock_selector` | **95%** |
| Core Pipeline | `data_collector`, `intelligence_engine`, `report_generator`, `validate_report_quality`, `citation_validator` | **90%** |
| Standard | All other modules (default) | **85%** |
| Infrastructure | Hooks, scripts, commands | **75%** |

**Enforcement**: `tdd_verify.py` (PostToolUse(TaskUpdate) hook) blocks task completion when coverage is below tier threshold.

---

## 2. @reviewer Checklist (L2) — Full

### 2-1. P5 English-First Compliance

- [ ] All variable/function/class names are English
- [ ] All docstrings are written in English
- [ ] All log and exception messages are English
- [ ] `CATEGORY_A/B_SYSTEM_PROMPT` in `intelligence_engine.py` is implemented in English
- [ ] 5 required content items from workflow.md Step 5 are fully preserved (language changed to English only)

### 2-2. Translation Pair

- [ ] `intelligence_engine.py`: `NarrativeOutput` JSON field names are English
- [ ] `report_generator.py`: Uses English template (`weekly-report.md.j2`)
- [ ] Translation output (`.ko.md`) exists paired with English original for applicable Steps (2, 4, 5, 11, 12, 15)
- [ ] `pacs-logs/step-{N}-translation-pacs.md` exists with pACS score ≥ threshold (not RED)

### 2-3. Legal Compliance (v3.6 I-9/I-10)

- [ ] No prohibited expressions: "매수 추천", "목표가", "확실한 상승", "매도 권고"
- [ ] Disclaimer included verbatim (Section 15.3 text)
- [ ] Weight adjustment history requires HITL flag explicitly shown (no auto-apply code path)
- [ ] No legal warning about sharing report with others (not required in report body)

### 2-4. Bear Case UX Position (v3.6 I-12)

- [ ] Bear Case section is at bottom of report (immediately above disclaimer)
- [ ] Bear Case section title: `"⚠️ 이 방향이 틀릴 수 있는 상황 (참고용)"`
- [ ] When `onboarding_mode=True`, Bear Case section includes leading explanation:
      `"이 섹션은 예측이 틀렸을 때의 시나리오입니다. 결정에 반드시 고려할 필요는 없습니다."`
- [ ] Telegram 5-line summary does NOT include Bear Case (brevity)

### 2-5. Python-First Decision Architecture (P6)

- [ ] `steeps_classifier.py`: Classification uses `KEYWORD_LOOKUP` table + deterministic `classify()` — no LLM call in classification path
- [ ] `stock_selector.py`: Category decision uses `classify_category()` with numeric constants — no LLM call
- [ ] `compliance_filter.py`: Uses `PROHIBITION_PATTERNS` regex array — no LLM call in `scan()`
- [ ] `validate_report_quality.py`: Python regex 1st pass completed before any LLM evaluation call
- [ ] `citation_validator.py`: Figure cross-validation is Python-only (no LLM)
- [ ] `BULLISH_THRESHOLD = 0.01` (not 0.02 — I-4 correction)
- [ ] `NEUTRAL_BAND = 0.03`

### 2-6. Accuracy Tracker (v3.6 I-3)

- [ ] Dual measurement window implemented: `ACCURACY_WINDOW_PRELIMINARY = 4` weeks, `ACCURACY_WINDOW_FINAL = 8` weeks
- [ ] KS-1 reporting uses 8-week window basis
- [ ] KS-1 label reads "Month 3 data basis" (not "Month 2" — I-5 correction)
- [ ] Naive Baseline: 3 strategies present (Always-Bullish, Momentum, Random — I-13)

### 2-7. Category B Zero-Guard (v3.6 I-7)

- [ ] No single `or 1` guard pattern — replaced by triple safety net
- [ ] `MIN_WEEKS_TRACKED` check present
- [ ] `MIN_ABS_COUNT` check present
- [ ] Average count guard present
- [ ] No `or 1` anywhere in Category B assignment logic

### 2-8. Standard Quality Baseline (unchanged)

- [ ] Type hints on all functions
- [ ] `frozen=True, slots=True` on shared dataclasses
- [ ] `sentiment_weight == 0.0` (immutable — assert in tests)
- [ ] No API keys in plain text
- [ ] ADR-001~ADR-017 compliance

---

## 3. Quality Gate Logic

```
quality_gate_check.py (Stop hook):
  ├── Check state.yaml tdd_status → any "failing" module → exit 2 (block response)
  └── Check state.yaml translations → any pacs_grade == "RED" → exit 2 (block response)

tdd_verify.py (PostToolUse(TaskUpdate) hook):
  ├── Translation task branch:
  │     Parse pACS from pacs-logs/step-{N}-translation-pacs.md
  │     Grade RED → update SOT translations.{step}.pacs_grade = "RED"
  └── Implementation task branch:
        Run pytest --cov for module
        Coverage < tier threshold → update SOT tdd_status.{module} = "failing"
        Coverage ≥ threshold → tdd_status.{module} = "passing"
```

---

## 4. L0 Anti-Skip Guard

The L0 gate is enforced by `quality_gate_check.py`. It is **unconditional** — no task completion justification bypasses it.

Conditions that trigger L0 block:
1. Any TDD module in "failing" status
2. Any translation in pACS "RED" grade

Resolution path:
- TDD failing: Fix implementation → rerun coverage → confirm "passing" in SOT
- Translation RED: Respawn `@translator` with revised prompt → new pACS log → confirm grade ≥ threshold

---

## 5. pACS Score Reference (Translation Quality)

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| GREEN | ≥ 90 | Accepted — production ready |
| YELLOW | 75–89 | Accepted with minor issues noted |
| RED | < 75 | Blocked — must respawn `@translator` |

pACS dimensions: Fa (Accuracy), Fb (Fluency), Fc (Terminology), Fd (Register), Fe (Completeness)

`Fd` (Register) is required in Step 12 (weekly report) pACS log — formal investor register verification.

---

## 6. InvestScan-Specific Test Patterns

### P1 Critical Module Test Template

```python
class TestComplianceFilter:
    """95% coverage required — P1 Critical."""

    def test_prohibition_patterns_complete(self):
        """All 10 prohibited expressions are in PROHIBITION_PATTERNS."""
        ...

    def test_scan_returns_violations(self):
        """scan() returns list of matched patterns, not LLM judgment."""
        result = compliance_filter.scan("매수 추천합니다")
        assert len(result) > 0
        assert all(isinstance(v, str) for v in result)

    def test_scan_clean_text_returns_empty(self):
        result = compliance_filter.scan("현재 기술주 환경을 분석합니다")
        assert result == []
```

### Fixture Files

| Fixture | Path | Purpose |
|---------|------|---------|
| `envscan_sample.json` | `tests/fixtures/` | EnvironmentScan WF-1 output schema |
| `fred_sample.json` | `tests/fixtures/` | FRED API 10 series response |
| `gnews_sample.parquet` | `tests/fixtures/` | GlobalNews signal_bridge input |

Generate: `python make_fixtures.py` (requires `pyarrow` for parquet)
