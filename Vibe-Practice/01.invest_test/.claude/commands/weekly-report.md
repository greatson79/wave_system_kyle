# /weekly-report — Generate Weekly Investment Report

Generate the weekly InvestScan report with full quality pipeline:
English NarrativeOutput → Reflect-Revise loop → @translator → Korean .ko.md → Telegram.

## Prerequisites
- `context_[date].json` must exist in the project root
- `hitl_1.completed: true` in `state.yaml`
- `m05.dg_01_to_08_passed: true` in `state.yaml`

## Execution Flow (P5-A: English execution, P5-B: Korean translation pair)

```
1. Verify context_[date].json (English fields check)
   → Load context_data: dict for citation_validator input

2. intelligence_engine.build_prompt() [English prompt]

3. build_narrative_with_retry(max_retries=3):  [v3.5 CR-5-4]
   LOOP (retry_count = 0..2):
     a. Claude LLM → NarrativeOutput (English — M0.5)
     b. validate_report_quality.python_validate_first(narrative)
        → FAIL: retry_count += 1 + attach failure context → LOOP
        → PASS: continue
     c. compliance_filter 10 patterns (Python regex — H-1)
        → FAIL: retry_count += 1 → LOOP
        → PASS: continue
     d. @reviewer: 8-criteria LLM check (L2 adversarial)
        → FAIL: retry_count += 1 → LOOP
        → PASS: continue
   LOOP END (3 failures → save best_attempt + HITL escalation)

4. citation_validator.validate_citations(narrative.text, context_data)  [H-5]
   → False: log warning + flag @reviewer (non-blocking — pipeline continues)

5. content_gate: NarrativeOutput 8-criteria final check  [Q8]

6. report_generator Jinja2 rendering → weekly-report-[date].md  [English]

7. [P5-B] Translation trigger:
   → TaskUpdate(status="completed", metadata={"step": 12, "task_type": "implementation"})
   → translation_trigger.py detects → writes translation-pending.yaml
   → Orchestrator spawns @translator SubAgent
   → @translator: glossary.yaml load → English→Korean translation → pACS scoring
   → weekly-report-[date].ko.md + pacs-logs/step-12-translation-pacs.md

8. pACS verification (GREEN ≥ 70)
   → RED (<50): re-translate → /translate 12
   → YELLOW (50-69): proceed with warning

9. HITL-3: Present Korean report to user for review
   (Korean message: "리포트 번역 완료. 검토 후 /approve-hitl 3으로 승인해주세요.")

10. Telegram dispatch (Korean 5-line summary):
    Line 1: 📊 [종목명]([종목코드]) — Category [A|B]
    Line 2: 💹 YoY 매출 +X% / 영업이익 +X% (최신 분기)   [A only]
             또는: [테마명] 시장 규모 $Xbn, CAGR X%        [B only]
    Line 3: 🎯 [Positive momentum maintained | Neutral — monitor | Risk zone]
    Line 4: ⚠️ 핵심 리스크: [downside_risk or dissolution_risk — 1 sentence]
    Line 5: 📅 다음 확인: [catalyst date or next report schedule]
    + short disclaimer variant
```

## Bear Case UX (v3.6 I-12)
- Bear Case section: positioned AFTER watchlist, BEFORE disclaimer (bottom of report)
- Bear Case title: "⚠️ 이 방향이 틀릴 수 있는 상황 (참고용)"
- Bear Case NOT included in Telegram summary
- `onboarding_mode=true`: include pre-text explanation before Bear Case

## Output Files
- `output/reports/weekly-report-[date].md` (English original)
- `output/reports/weekly-report-[date].ko.md` (Korean translation — @translator)
- `pacs-logs/step-12-translation-pacs.md` (translation quality log)
- `review-logs/step-12-review.md` (@reviewer verdict)
