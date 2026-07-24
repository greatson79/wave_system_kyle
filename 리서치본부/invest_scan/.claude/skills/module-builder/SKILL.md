---
name: module-builder
description: InvestScan TDD-first module builder skill. Use when building any InvestScan Python module. Enforces Red→Green TDD cycle with tier-based coverage requirements.
---

# Module Builder Skill

Build InvestScan modules using strict TDD. English-First execution (P5-A mandatory).

## Protocol

### Step 1: Load Context (English)
```python
# Required reads before starting any implementation
state = yaml.safe_load(Path(".claude/state.yaml").read_text())
convention = Path("docs/code-convention.md").read_text()
schema = state.get("discovered_schema", {})
```

### Step 2: Write Tests First (Red phase — English)
```python
# tests/test_{module}.py structure
"""
Test suite for {module}.py — InvestScan
All test descriptions and assertions in English.
"""
import pytest
from {module} import ...

class Test{Module}HappyPath:
    def test_basic_functionality(self): ...

class Test{Module}EdgeCases:
    def test_empty_input(self): ...
    def test_boundary_conditions(self): ...

class Test{Module}Sentinel:
    def test_sentiment_weight_is_zero(self, module_instance):
        assert module_instance.sentiment_weight == 0.0  # absolute sentinel
```
Run: `pytest tests/test_{module}.py` → MUST see `FAILED` (if all pass → tests too weak)

### Step 3: Implement Module (Green phase — English)
```python
# {module}.py structure
"""
{Module description} — InvestScan
All code, comments, and docstrings in English (P5-A).
"""
from dataclasses import dataclass, field
from typing import ...

@dataclass(frozen=True)  # immutable for shared dataclasses
class {Module}Result:
    sentiment_weight: float = 0.0  # absolute sentinel — never modify
    ...
```
Run: `pytest tests/test_{module}.py` → MUST see `PASSED`

### Step 4: Verify Coverage
```bash
pytest tests/test_{module}.py --cov={module} --cov-report=term-missing
```
Required coverage by tier:
- P1 Critical: 95%+ (compliance_filter, synthesize_macro, steeps_classifier, stock_selector)
- Core Pipeline: 90%+ (normalizers, intelligence_engine, report_generator, weekly_orchestrator, validate_report_quality, citation_validator)
- Standard: 85%+ (all others)
- Infrastructure: 75%+ (hook scripts)

### Step 5: Report to Lead
```python
# Write to workspace — all English
workspace = {
    "status": "completed",
    "module": "{module}",
    "coverage": float,
    "tests_passed": True,
    "loc": int,  # lines of code
}
Path(".claude/agent-workspace/{fork-id}.yaml").write_text(yaml.dump(workspace))
# Then call TaskUpdate with step metadata
```

## Python-First Principle (P6)
- Classification decisions → Python constants + functions (NO LLM)
- Threshold values → Python constants (never hardcoded inline)
- sentinel: `sentiment_weight == 0.0` → frozen dataclass or assertion

## English-First Examples
```python
# ✅ Correct (English)
def normalize_score(raw_value: float, scale: str) -> float:
    """Normalize raw score to [0.0, 1.0] range based on detected scale."""
    ...

# ❌ Wrong (Korean in code)
def 점수_정규화(원시값: float) -> float:
    """점수를 0-1 범위로 정규화합니다."""
    ...
```
