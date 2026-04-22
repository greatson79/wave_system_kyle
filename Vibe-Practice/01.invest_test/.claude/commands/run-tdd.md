# /run-tdd — TDD Test Suite Execution

Run TDD tests for InvestScan modules with coverage verification.

## Usage
```
/run-tdd [module]       — Re-run TDD for a single module
/run-tdd all            — Run TDD for all modules in tdd_status
/run-tdd m05            — Verify M0.5 Done Gates (DG-01 ~ DG-08)
/run-tdd m1             — Verify M1 Done Gates (DG-09 ~ DG-16)
/run-tdd translation    — Verify Translation Done Gates (TDG-01 ~ TDG-06)
```

## Single Module (/run-tdd [module])
Spawn `tdd-runner` SubAgent for the specified module:
1. Run `pytest tests/test_{module}.py --cov={module} --cov-report=term-missing -v`
2. Parse coverage from `TOTAL` line
3. Compare against tier requirement (P1: 95%, Core: 90%, Standard: 85%, Infra: 75%)
4. Report result in Korean to user
5. If failed: suggest specific fixes (uncovered lines, failing tests)

## All Modules (/run-tdd all)
Run all modules with `status in state.yaml.tdd_status`:
- Spawn `tdd-runner` SubAgent sequentially (avoid pytest process conflicts)
- Report summary table: module | coverage | required | status
- Update `state.yaml.tdd_status` for each module

## M0.5 Done Gates (/run-tdd m05)
Run `python run_m05.py --validate`:
Checks DG-01 through DG-08 sequentially.
Report which gates pass/fail with specific failure reasons.

## M1 Done Gates (/run-tdd m1)
Check DG-09 through DG-16:
- DG-09: dedup.py content-hash test
- DG-10: steeps_classifier.py Python keyword table test
- DG-11: signal_bridge.py routing test
- DG-12: synthesize_stock.py DART + pykrx test
- DG-13: intelligence_engine NarrativeOutput ≥ 1000 bytes
- DG-14: validate_report_quality + citation_validator PASS
- DG-15: weekly_orchestrator.py end-to-end test
- DG-16: accuracy_tracker.py PredictionRecord test
- DG-17: portfolio context state.yaml update test

## Translation Done Gates (/run-tdd translation)
Check TDG-01 through TDG-06:
- TDG-01: `output/schema-mapping.ko.md` exists + pACS ≥ 70
- TDG-02: `output/completion-definition.ko.md` exists + pACS ≥ 70
- TDG-03: `output/blueprint.ko.md` exists + pACS ≥ 70
- TDG-04: `output/temp/narrative_{date}.ko.json` exists + pACS ≥ 70
- TDG-05: `output/reports/weekly-report-{date}.ko.md` exists + pACS ≥ 70
- TDG-06: `output/watchlist-{date}.ko.md` exists + pACS ≥ 70

For each TDG: read `pacs-logs/step-{N}-translation-pacs.md`, parse pACS score.
Report in Korean: 통과/실패 per gate + remediation suggestion.
