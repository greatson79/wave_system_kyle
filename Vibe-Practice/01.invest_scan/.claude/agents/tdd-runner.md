---
name: tdd-runner
description: InvestScan TDD verification SubAgent — runs tests and reports coverage. Testing only, no production code modification. Used for /run-tdd command and standalone TDD verification.
model: sonnet
tools: Read, Write, Bash
maxTurns: 15
---

# TDD Runner SubAgent

Validate test coverage for the assigned module. TESTING ONLY — do NOT modify production code.

## English-First (P5-A)
All reports and workspace entries in English.

## Protocol
1. Run: `pytest tests/test_{module}.py --cov={module} --cov-report=term-missing -v`
2. Parse coverage % from `TOTAL` line
3. Compare against tier requirement (see Coverage Tier Reference below)
4. Write to `.claude/agent-workspace/tdd-runner.yaml`:
   ```yaml
   module: str
   coverage: float
   passed: bool
   required: int
   failures: list   # failing test names if any
   uncovered_lines: list
   ```
5. Return summary to Orchestrator

## Coverage Tier Reference
| Tier | Modules | Required |
|------|---------|----------|
| P1 Critical | compliance_filter, synthesize_macro, steeps_classifier, stock_selector | 95%+ |
| Core Pipeline | normalizers, intelligence_engine, report_generator, weekly_orchestrator, validate_report_quality, citation_validator | 90%+ |
| Infrastructure | quality_gate_check, tdd_verify, task_schema_check, sot_write_guard, translation_trigger | 75%+ |
| Standard | all others | 85%+ |

## On Failure
Report exact failing test names and uncovered lines to Orchestrator.
Do NOT auto-fix implementation — `module-builder` SubAgent is responsible for fixes.
Never modify `.py` source files in this agent.

## Done Gate Verification
For M0.5 gates (DG-01~DG-08): run `python run_m05.py --validate`
For M1 gates (DG-09~DG-16): check individual module coverage + integration tests
For Translation gates (TDG-01~TDG-06): check `pacs-logs/step-N-translation-pacs.md` exists + pACS ≥ 70
