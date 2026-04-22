# Quality Gates & P1 Validation

> This document is the detailed specification for the 4-layer quality assurance architecture and P1 hallucination containment.
> Separated from CLAUDE.md — reference when designing, debugging, or extending quality gates.

## 4-Layer Quality Assurance Architecture (L0 → L1 → L1.5 → L2)

The Orchestrator increments `current_step` sequentially only. To proceed, each step must pass up to 4 validation layers:

1. **L0 Anti-Skip Guard** (deterministic) — artifact file exists + minimum size (100 bytes). Performed by `validate_step_output()` in the Hook layer.
2. **L1 Verification Gate** (semantic) — agent self-verification that the artifact meets `Verification` criteria 100%. On failure, re-execute only the failing portion (up to 10 times). Recorded in `verification-logs/step-N-verify.md`.
3. **L1.5 pACS Self-Rating** (confidence) — perform Pre-mortem Protocol, then score on F/C/L 3 dimensions. Recorded in `pacs-logs/step-N-pacs.md`. RED (< 50) → rework.
4. **[L2 Calibration]** (optional) — separate `@verifier` agent cross-validates pACS score. High-risk steps only.

> Steps without a `Verification` field proceed with Anti-Skip Guard only (backward compatible). Details: `AGENTS.md §5.3`, `§5.4`

---

## P1 Hallucination Containment

Tasks requiring 100% accuracy on repetition are enforced via Python code.

### (1) KI Schema Validation
`_validate_session_facts()` ensures the 11 required RLM keys (session_id, tags, final_status, diagnosis_patterns, etc.) exist before writing to knowledge-index — fills safe defaults when missing.

### (2) Partial Failure Isolation
In `archive_and_index_session()`, failure to write an archive file does not block knowledge-index update — protects the core RLM asset.

### (3) SOT Write Pattern Validation
`_check_sot_write_safety()` in `setup_init.py` detects SOT filename + write pattern co-existence within AST function boundaries in Hook scripts (Tier 1: block SOT references in non-SOT scripts, Tier 2: per-function write pattern check in SOT-aware scripts).

### (4) SOT Schema Validation
`validate_sot_schema()` verifies structural integrity of workflow state.yaml across 8 items:
- **S1-S6**: current_step type/range, outputs type/key format, future-step artifact detection, workflow_status valid values, auto_approved_steps consistency
- **S7**: Validate 5 pACS fields (S7a dimensions F/C/L 0-100, S7b current_step_score 0-100, S7c weak_dimension F/C/L, S7d history dict→{score, weak}, S7e pre_mortem_flag string)
- **S8**: Validate 5 active_team fields (S8a name string, S8b status partial|all_completed, S8c tasks_completed list, S8d tasks_pending list, S8e completed_summaries dict→dict)

Runs at both SessionStart and Stop hooks.

### (5) Adversarial Review P1 Validation
`validate_review_output()` verifies structural integrity of review reports:
- R1: file exists
- R2: minimum size
- R3: 4 required sections
- R4: explicit PASS/FAIL extraction
- R5: issue table ≥ 1 row

`parse_review_verdict()` — extract issue severity counts via regex.
`calculate_pacs_delta()` — Generator-Reviewer pACS difference (Delta ≥ 15 → recalibrate).
`validate_review_sequence()` — enforce Review PASS → Translation order via file timestamps.
Standalone script: `validate_review.py`.

### (6) Translation P1 Validation
`validate_translation_output()` validates translation artifacts across 7 items:
- T1: file exists, T2: minimum size, T3: English source exists, T4: .ko.md extension, T5: non-whitespace, T6: heading count ±20%, T7: code block count match

`check_glossary_freshness()` — glossary timestamp freshness (T8).
`verify_pacs_arithmetic()` — min() arithmetic accuracy for all pACS logs (T9 — general purpose).
`validate_verification_log()` — verification log V1a-V1c.
`validate_translation.py` requires review verdict=PASS check.
Standalone script: `validate_translation.py`.

### (7) pACS P1 Validation
`validate_pacs_output()` validates pACS logs across 6 items:
- PA1: file exists, PA2: minimum size 50 bytes, PA3: dimension scores ≥ 3 (0-100 range), PA4: Pre-mortem section present, PA5: min() arithmetic accuracy, PA7: RED block (pACS < 50 → FAIL)
- PA6 (optional): score-color zone consistency

Standalone script: `validate_pacs.py`.

### (8) L0 Anti-Skip Guard Code Implementation
`validate_step_output()` — 3 L0 validation items:
- L0a: file exists at SOT outputs.step-N path
- L0b: file size ≥ MIN_OUTPUT_SIZE (100 bytes)
- L0c: non-whitespace confirmation

`validate_pacs.py --check-l0` enables simultaneous pACS + L0 validation.

### (9) Predictive Debugging P1 Validation
`validate_risk_scores()` — risk-scores.json 6 items:
- RS1: required keys, RS2: data_sessions integer, RS3: risk_score range, RS4: error_count arithmetic consistency, RS5: resolution_rate range, RS6: top_risk_files sorted + exists

### (10) Retry Budget P1 Validation
`validate_retry_budget.py` — deterministic retry budget verdict:
- RB1: read counter file, RB2: detect ULW active, RB3: compare budget (`retries_used < max_retries`)
- `max_retries`: 3 when ULW active, 2 when inactive
- `--increment` mode for atomic write counter increment

### (11) Abductive Diagnosis P1 Validation
`validate_diagnosis_log()` — diagnosis log 10 items:
- AD1: file exists, AD2: minimum size 100 bytes, AD3: Gate field match, AD4: selected hypothesis present, AD5: evidence ≥ 1, AD6: Action Plan present, AD7: no forward references, AD8: hypotheses ≥ 2, AD9: selected hypothesis consistency, AD10: reference to prior diagnosis (retry > 0)

`diagnose_failure_context()` — pre-evidence collection (retry_history, upstream_evidence, hypothesis_priority, fast_path, raw_evidence). Fast-Path (FP1-FP3) for deterministic shortcuts.
Standalone scripts: `diagnose_context.py` (pre-analysis), `validate_diagnosis.py` (post-validation).

### (12) Cross-Step Traceability P1 Validation
`validate_cross_step_traceability()` — 5 traceability items:
- CT1: trace marker present, CT2: referenced step artifact exists, CT3: section ID resolved (Warning), CT4: minimum density ≥ 3, CT5: no forward references

Standalone script: `validate_traceability.py`.

### (13) Domain Knowledge Structure P1 Validation
`validate_domain_knowledge()` — domain-knowledge.yaml 7 items:
- DK1: file exists + YAML valid, DK2: metadata required keys, DK3: entities structure, DK4: relations referential integrity, DK5: constraints structure, DK6: artifact DKS reference resolution, DK7: no constraint violations

Standalone script: `validate_domain_knowledge.py`. Optional — not required by all workflows.

### (14) Workflow.md DNA Inheritance P1 Validation
`validate_workflow_md()` — 8 items:
- W1: file exists, W2: minimum size 500 bytes, W3: `## Inherited DNA` header, W4: Inherited Patterns table ≥ 3 rows, W5: Constitutional Principles section, W6: CAP reference, W7: CT Verification-Validator consistency, W8: DKS Verification-Validator consistency

Standalone script: `validate_workflow.py`. Call manually after workflow-generator completes.
