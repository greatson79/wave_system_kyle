# InvestScan Completion Definition
**Step 4 Output** | Generated: 2026-03-29 | Language: English (P5-A)

---

## What "Done" Means for InvestScan

### M0.0: Day 0 Installation Complete (DG-00)
- [ ] `personalizer.py --hello-test` sends Telegram "설치 완료" message within 10 minutes
- [ ] Telegram Bot Token + chat_id verified functional

### M0.5: Core Pipeline Ready (DG-01~08)
- [ ] `DG-01`: config.py loads investscan.yaml + API keys from keyring
- [ ] `DG-02`: normalizers.py converts database.json → UnifiedSignal (actual field names)
- [ ] `DG-03`: synthesize_macro.py produces InvestmentMeta + sector directions
- [ ] `DG-04`: sentinel passes — `assert sentiment_weight == 0.0` everywhere
- [ ] `DG-05`: compliance_filter.py replaces/detects all 10 prohibition patterns
- [ ] `DG-06`: telegram_notifier.py works in `--dry-run` mode
- [ ] `DG-07`: `run_m05.py --dry-run` completes full pipeline without error
- [ ] `DG-08`: state.yaml records `milestones.m05.dg_01_to_08_passed: true`

### M1: Full Pipeline Ready (DG-09~16)
- [ ] `DG-09`: dedup.py performs content-hash dedup with source field included
- [ ] `DG-10`: steeps_classifier.py uses keyword lookup for all 6 STEEPs + lowercase s/S distinction
- [ ] `DG-11`: signal_bridge.py routes E_env → industrials/materials, lowercase s → sector field
- [ ] `DG-12`: synthesize_stock.py integrates DART financials + pykrx with graceful skip
- [ ] `DG-13`: intelligence_engine.py produces NarrativeOutput >= 1000 bytes in English
- [ ] `DG-14`: validate_report_quality.py Python regex 8-criteria PASS + citation_validator.py PASS
- [ ] `DG-15`: `weekly_orchestrator.py --mode full-auto` end-to-end success
- [ ] `DG-16`: accuracy_tracker.py records PredictionRecord + updates state.yaml
- [ ] `DG-17`: portfolio context — state.yaml portfolio.holdings updatable, report_generator comparison verified

### Translation Done Gates (TDG-01~06)
- [ ] `TDG-01`: schema-mapping.ko.md exists, pACS >= 70
- [ ] `TDG-02`: completion-definition.ko.md exists, pACS >= 70
- [ ] `TDG-03`: blueprint.ko.md exists, pACS >= 70
- [ ] `TDG-04`: narrative_{date}.ko.json exists, pACS >= 70
- [ ] `TDG-05`: weekly-report-{date}.ko.md exists, pACS >= 70 (Fd dimension included)
- [ ] `TDG-06`: watchlist-{date}.ko.md exists, pACS >= 70

---

## Quality Thresholds

| Tier | Modules | Coverage |
|------|---------|----------|
| P1 Critical | compliance_filter, synthesize_macro, steeps_classifier, stock_selector | 95%+ |
| Core Pipeline | normalizers, intelligence_engine, report_generator, weekly_orchestrator, validate_report_quality, citation_validator | 90%+ |
| Standard | All others | 85%+ |
| Infrastructure | Hooks, scripts | 75%+ |

---

## User-Ready Criteria (Phase E)

A system is "user-ready" when:
1. `run_m05.py --dry-run` → exit 0 (all DG-01~08 pass)
2. `python3 -m pytest tests/ -q` → all pass, coverage thresholds met
3. Translation Done Gates TDG-01~06 all GREEN (pACS >= 70)
4. `/weekly-report` command → English report + Korean .ko.md pair generated
5. Telegram delivery works in --dry-run mode
6. Portfolio context (DG-17) functional

---

*This document is the binding completion contract. Any task marked "done" must satisfy its corresponding Done Gate before state.yaml milestone is set to true.*
