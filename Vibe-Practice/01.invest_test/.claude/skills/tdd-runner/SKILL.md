---
name: tdd-runner
description: InvestScan TDD verification skill. Validates test coverage for assigned modules. Testing only — never modifies production code.
---

# TDD Runner Skill

Verify test coverage for InvestScan modules. English-First (P5-A).

## Phase A: Write Tests (Red phase — English)
```python
# tests/test_{module}.py requirements:
# 1. Happy path: normal inputs → expected outputs
# 2. Edge cases: empty input, None, boundary values, Unicode
# 3. Sentinel: sentiment_weight == 0.0 (all modules)
# 4. Determinism: same input → same output (classification modules)
# 5. Error handling: invalid input → expected exceptions (not silent failure)

# Run to confirm RED:
# pytest tests/test_{module}.py
# → Should see: FAILED (X failed, Y passed) or all FAILED
# If ALL pass on first run → tests are too weak → add adversarial cases
```

## Phase B: Validate Implementation Coverage
```bash
# Run coverage analysis
pytest tests/test_{module}.py --cov={module} --cov-report=term-missing -v

# Parse output
# Look for: TOTAL   XXX   YYY   ZZ%
# ZZ% must meet tier requirement
```

**Coverage Tier Requirements:**
| Tier | Min | Modules |
|------|-----|---------|
| P1 Critical | 95% | compliance_filter, synthesize_macro, steeps_classifier, stock_selector |
| Core Pipeline | 90% | normalizers, intelligence_engine, report_generator, weekly_orchestrator, validate_report_quality, citation_validator |
| Infrastructure | 75% | quality_gate_check, tdd_verify, task_schema_check, sot_write_guard, translation_trigger |
| Standard | 85% | all others |

## Phase C: Update State (via Orchestrator — not directly)
```python
# Report to workspace
workspace_update = {
    "module": "{module}",
    "coverage": float,   # actual measured coverage %
    "passed": bool,      # coverage >= required AND pytest returncode == 0
    "required": int,     # tier requirement
    "failures": list,    # failing test names if any
    "uncovered_lines": list,  # from --cov-report=term-missing
}
Path(".claude/agent-workspace/tdd-runner.yaml").write_text(yaml.dump(workspace_update))

# Then signal Orchestrator to update state.yaml.tdd_status[module]
```

## Failure Report Format (English — for builder to fix)
```
MODULE: {module}.py
COVERAGE: {actual}% (required: {required}%)
FAILING TESTS:
  - test_{module}.TestClass.test_name: AssertionError: expected X, got Y
UNCOVERED LINES: {module}.py: 45-52, 78, 91-95
RECOMMENDED ACTION: Add tests for lines 45-52 (error handling branch)
```

## English-First Compliance
- All test names: English (no Korean in test methods)
- All assertion messages: English
- All `pytest.mark` descriptions: English
- All workspace output: English keys + values
