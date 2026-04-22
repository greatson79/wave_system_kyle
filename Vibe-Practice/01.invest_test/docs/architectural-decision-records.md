# InvestScan Architectural Decision Records

> ADR index for the InvestScan workflow (workflow-coding.md v3.6).
> Parent project ADRs (ADR-001~ADR-050) are in the root `DECISION-LOG.md`.
> This file covers InvestScan-specific decisions: ADR-013~ADR-017.

---

## ADR-013: English-First Execution (P5-A)

- **Status**: Accepted
- **Date**: 2026-03-29
- **Context**: AI reasoning quality peaks in English. The quality absolute criterion (P4) requires maximizing output quality at every stage. Using Korean in agent prompts and intermediate data imposes a measurable reasoning penalty.
- **Decision**: All agent prompts, intermediate outputs, code variables/comments, and config values are written in English.
- **Consequences**:
  - `CATEGORY_A/B_SYSTEM_PROMPT` in `intelligence_engine.py` must be English-authored (content requirements from workflow.md Step 5 preserved 100% — only language changed).
  - `NarrativeOutput.text` is English.
  - HITL prompts and Telegram delivery remain Korean (user-facing channels exempt).
- **NOT affected**: HITL guidance messages, Telegram notifications, final `.ko.md` files produced by `@translator`.
- **Related**: P5 in workflow-coding.md §2, `docs/code-convention.md`

---

## ADR-014: @translator Korean Pair (P5-B)

- **Status**: Accepted
- **Date**: 2026-03-29
- **Context**: English-First execution means users receive English outputs by default. Korean translation pairs are required for complete user experience without sacrificing AI reasoning quality.
- **Decision**: Six Steps (2, 4, 5, 11, 12, 15) automatically trigger `@translator` SubAgent spawn after English output is confirmed complete.
- **Mechanism**:
  1. `translation_trigger.py` (PostToolUse(TaskUpdate) Hook) detects Step completion
  2. Writes `.claude/agent-workspace/translation-pending.yaml`
  3. Orchestrator reads pending signal → spawns `@translator`
  4. `tdd_verify.py` validates pACS score from `pacs-logs/` directory
  5. SOT: `state.yaml` `translations` section is the single source of truth for translation status
- **Fallback**: Translation is enrichment, not blocking. If translation fails, English original remains usable.
- **Infinite-loop guard**: `translation_trigger.py` checks `task_type == "translation"` — translator task completion does NOT re-trigger the hook.
- **Related**: `translation_trigger.py`, `tdd_verify.py` (CR-2), `state.yaml` translations section

---

## ADR-015: sot_write_guard 2nd Defense Line Principle (v3.1 CR-3)

- **Status**: Accepted
- **Date**: 2026-03-29
- **Context**: Claude Code SubAgent execution environment does not guarantee `CLAUDE_AGENT_ID` or similar env variables. Relying solely on env-based Agent ID detection for SOT protection is insufficient. Prior implementation used `lstrip()` for path comparison which produced false negatives when paths had common prefixes.
- **Decision**:
  - **1st defense (primary)**: Orchestrator prompt explicitly instructs each SubAgent to write only to its own workspace YAML — this is the effective protection.
  - **2nd defense (secondary)**: `sot_write_guard.py` — blocks when SubAgent env var is detected; allows with warning when env var is absent (cannot distinguish SubAgent from Orchestrator).
  - **Path comparison**: Uses `Path.resolve()` for absolute path normalization (eliminates `lstrip` bug).
- **Consequence**: SubAgents without env var set cannot be detected by the hook → 1st defense (prompt instruction) carries the critical responsibility.
- **Related**: `sot_write_guard.py`, `.claude/agents/investscan-orchestrator.md`

---

## ADR-016: Python-First Decision Architecture (v3.4 P6)

- **Status**: Accepted
- **Date**: 2026-03-29
- **Context**: LLMs are non-deterministic — identical inputs can produce different classifications across calls. Allowing LLM judgment in classification/validation functions (`steeps_classifier`, `stock_selector`, `compliance_filter`) creates a 6-step hallucination chain: wrong classification → wrong sector weight → wrong narrative → wrong recommendation → wrong user action → legal risk.
- **Decision**:
  - All classification, validation, and threshold judgments = **Python code (deterministic)**
  - LLM role = **NarrativeOutput text generation only**
  - Principle: "Python is the judge, LLM is the narrator."
- **Implementation**:
  - `steeps_classifier.py`: `KEYWORD_LOOKUP` table + `classify()` function (Python)
  - `stock_selector.py`: Numeric threshold constants + `classify_category()` function (Python)
  - `compliance_filter.py`: `PROHIBITION_PATTERNS` regex constants + `scan()` function (Python)
  - `validate_report_quality.py`: 8-criterion Python regex (1st pass) → LLM scoring (2nd pass only)
  - `citation_validator.py`: Python cross-validation of `NarrativeOutput` figures vs `context_data`
- **NOT affected**: `NarrativeOutput.text` generation (LLM remains), `@translator` Korean translation (LLM remains).
- **TDD implication**: These 4 modules are P1 Critical (95% coverage) — deterministic Python logic is fully testable.
- **Related**: `p1-critical-builder.md`, workflow-coding.md §19

---

## ADR-017: Adversarial Reflection Architecture Decisions (v3.6)

- **Status**: Accepted
- **Date**: 2026-03-29
- **Context**: 5 adversarial agents (Skeptic, Statistician, TechCritic, LegalWatchdog, UXInquisitor) attacked prd.md → identified 13 design flaws, bugs, and measurement errors. These decisions collectively address those findings.
- **Decisions**:

  | ID | Decision | Rationale |
  |----|----------|-----------|
  | I-1 | M0.0 milestone: Telegram Hello on Day 0 | Immediate validation that delivery pipeline works before any data collection |
  | I-3 | `accuracy_tracker` dual window: 4-week (preliminary) + 8-week (final, KS-1 basis) | Single window insufficient — 4-week median too volatile; 8-week reflects actual investment horizon |
  | I-4 | Bullish threshold relaxed: +2% → +1% | +2% is too strict for macro-driven weeks; +1% better reflects signal vs noise |
  | I-5 | KS-1 label: "Month 2" → "Month 3 data basis" | Measurement lag in Korean market data means Month 2 label is misleading |
  | I-6 | FDR/pykrx/dart-fss availability tracking + explicit fallback chain | Library installation failure silent until runtime; explicit tracking required |
  | I-7 | Category B `or 1` zero-guard → triple safety net (MIN_WEEKS_TRACKED / MIN_ABS_COUNT / AVG_COUNT guard) | Single `or 1` creates category inflation; triple guard prevents false Category B assignments |
  | I-9 | Legal non-applicability rationale reordered: no contract → no compensation → self-determination | Logical priority order: strongest argument (no contract) leads |
  | I-10 | Continuous relationship guardrails | Repeated use does not constitute advisory relationship — explicit guard required |
  | I-11 | Portfolio context: `state.yaml` portfolio section | Users need portfolio context to assess recommendations — missing was a blind spot |
  | I-12 | Bear Case section moved to bottom (above disclaimer) | Front-loaded Bear Case causes decision paralysis in onboarding phase |
  | I-13 | Naive Baseline 3 strategies: Always-Bullish + Momentum + Random | Single baseline insufficient for statistical validity of KS-1 measurement |

- **Consequence**: §20 in workflow-coding.md contains full Python spec for I-7, I-8, I-9, I-10, I-11, I-12, I-13. ADR-001~ADR-016 remain valid and unaffected.
- **Related**: workflow-coding.md §20, `state.yaml` portfolio section, `accuracy_tracker.py`

---

## Reference: Parent Project ADRs

InvestScan inherits the full parent ADR set (ADR-001~ADR-050 in `DECISION-LOG.md`). Key parent decisions that directly affect InvestScan:

| ADR | Title | InvestScan Impact |
|-----|-------|-------------------|
| ADR-001 | Workflow is intermediate, working system is final | Phase B→C→D→E implementation order |
| ADR-002 | 3 absolute criteria hierarchy | Quality > SOT > CCP applies to all InvestScan code |
| ADR-038 | DNA Inheritance | InvestScan inherits all 6 absolute criteria from parent |
| ADR-043 | ULW Mode (orthogonal thoroughness overlay) | ULW applies to this build session |
| ADR-050 | Security Hardening (4-layer defense) | Hooks + SOT guard active in InvestScan |
