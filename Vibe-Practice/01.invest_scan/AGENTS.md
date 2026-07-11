# AgenticWorkflow — Common AI Agent Instructions

> This file contains rules that **all AI agents** working on this project must follow, regardless of model or tool.
> These rules apply regardless of which tool is used — Claude Code, Cursor, Copilot, Codex, or any other.

---

## 1. Project Definition

An agent-based workflow automation project. The purpose is to design complex tasks as systematic workflows and then actually implement and operate those workflows.

### Final Goal — 2-Phase Process

| Phase | Artifact | Nature |
|-------|----------|--------|
| **Phase 1: Workflow Design** | `workflow.md` | Intermediate artifact (blueprint) |
| **Phase 2: Workflow Implementation** | A system where agents, scripts, and automation actually operate | **Final artifact** |

> Creating `workflow.md` is only half the work. **The final goal is for the content described within it to actually operate.**

### Raison d'être — DNA Inheritance

AgenticWorkflow is a **parent organism** that gives birth to child agentic workflow systems. Regardless of domain, each child structurally inherits the parent's complete genome.

| Genome Component | How It Is Embedded in Children |
|-----------------|-------------------------------|
| 3 Absolute Standards | workflow.md `Inherited DNA` section — contextualized per domain |
| SOT pattern | `state.yaml` — single file + single write point |
| 3-phase structure | Research → Planning → Implementation structural constraint |
| 4-layer verification | L0 Anti-Skip → L1 Verification → L1.5 pACS → L2 Review |
| P1 containment | Python deterministic validation scripts |
| Safety Hook | Dangerous command blocking + TDD Guard |
| Adversarial Review | `@reviewer` + `@fact-checker` Generator-Critic pattern |
| Decision Log | Recording rationale for auto-approved decisions |
| Context Preservation | Cross-session memory preservation + Knowledge Archive + RLM pattern |

> Inheritance is not a choice but a **structure**. Children do not "reference" the parent's DNA — they **embed** it. Details: `soul.md §0`.

> **12→9 Mapping**: Of the 12 components in soul.md §0, the 9 above are structurally embedded in children as `inherited_dna`. The remaining 3 — Design Principles P1-P4 (included in Absolute Standards), Sisyphus/Error→Resolution (behavioral patterns, not structure), RLM theory (theoretical foundation, not structure) — are implicitly reflected in children as internal mechanisms of the parent organism, but are not separated as distinct `inherited_dna` items. soul.md itself is a meta-document (the definition of inheritance) and is therefore not subject to inheritance.

### Basic Workflow Structure

All workflows consist of 3 phases:

1. **Research** — Information gathering and analysis
2. **Planning** — Planning, structuring, human review/approval
3. **Implementation** — Actual execution and artifact generation

Each phase must explicitly specify:
- Task to be performed
- Responsible agent
- Data pre-processing/post-processing
- Output artifact
- Human intervention point (if applicable)

---

## 2. Absolute Standards

> **These are the highest-level rules applied to all design, implementation, and modification decisions in this project.**
> They supersede all principles, guidelines, and conventions below.
> If any principle conflicts with an Absolute Standard, the Absolute Standard wins.

### Absolute Standard 1: Quality of the Final Artifact

> **Speed, token cost, workload, and length limits are completely ignored.**
> The sole criterion for all decisions is **the quality of the final artifact**.
> Rather than reducing steps to produce something faster, choose the direction of adding steps to improve quality.

Application examples:
- If adding more workflow steps improves quality → add steps
- If using more agents raises quality → add agents
- If repeating verification steps improves the artifact → allow repetition

### Absolute Standard 2: Single-File SOT + Hierarchical Memory Structure

> **Under a single-file SOT (Single Source of Truth) + hierarchical memory structure design, dozens of agents can operate simultaneously without data inconsistency.**

Design rules:
- **State centralization**: All shared state of the workflow is concentrated in a **single file** (e.g., `state.json`, `state.yaml`). Do not scatter state across multiple files.
- **Single write point**: Only the Orchestrator (or a designated single agent) has write access to the SOT file. Other agents access it read-only and produce their own results as separate output files.
- **Conflict prevention**: Do not design structures where multiple agents modify the same file simultaneously.

```
Bad:  Agent A → directly modifies state.json
      Agent B → directly modifies state.json  → data conflict

Good: Agent A → creates output-a.md → reports to Orchestrator
      Agent B → creates output-b.md → reports to Orchestrator
      Orchestrator → merges into state.json  → single write point
```

### Absolute Standard 3: Code Change Protocol (CCP)

> **Before writing, modifying, adding, or deleting code, the following 3 steps must be performed internally.**
> Skipping this protocol is a violation of the Absolute Standards.

If Absolute Standard 1 (quality) defines "what to optimize" and Absolute Standard 2 (SOT) defines "how to structure data," then Absolute Standard 3 defines **"how to behave when changing code."** High-quality code emerges from a rigorous process that analyzes dependencies, coupling, and change ripple effects in advance.

#### Coding Anchor Points (CAP-1~4)

If CCP defines "what to perform" (procedure), CAP defines **"with what mindset to perform it"** (attitude). All CCP steps are performed with the following 4 anchor points internalized.

- **CAP-1: Think Before Coding** — Do not assume. Do not modify before reading the code. Surface trade-offs and ask questions when unclear.
- **CAP-2: Simplicity First** — Write only the minimum code that satisfies the current requirement. Do not create speculative features, premature abstractions, or unnecessary helpers.
- **CAP-3: Goal-Based Execution** — Define success criteria before implementation and verify after implementation (e.g., tests, manual confirmation).
- **CAP-4: Surgical Changes** — Perform only the requested change. Do not "improve" unrelated code, and do not add comments, types, or documentation to code that was not touched.

> CAP is a subordinate attitude norm of CCP, so when it conflicts with Absolute Standard 1 (quality), quality wins. Example: when CAP-2 (simplicity) undermines quality — complexity necessary for quality is allowed.

**Step 1 — Understand Intent:**
- Have you accurately understood what the user has asked to implement? You must be able to explain it clearly in 1-2 sentences.
- Have you accurately understood the purpose of the change (bug fix, refactoring, performance, feature addition, etc.) and constraints (backward compatibility, technology stack, etc.)?

**Step 2 — Ripple Effect Analysis:**

Investigate the impact that writing new code or modifying existing code has on the entire codebase:
- **Direct dependencies**: The function/class/module/file where the modification target is defined
- **Call relationships**: Other code that calls this code, or that this code calls
- **Structural relationships**: Inheritance/implementation, composition/aggregation, association/reference
- **Data models/schemas**: Types/fields/validation logic that must change together
- **Test code**: Unit tests, integration tests, snapshot tests, etc.
- **Configuration/environment/build**: config, DI settings, routing, dependency injection, etc.
- **Documentation/comments/API specs**: Comments, README, API documentation, type definitions, etc.

Investigate at an expert level "where the ripple effects of this change can reach." If there are highly-coupled areas (tight coupling, change coupling, potential shotgun surgery), you **must** notify the user in advance and consult with them.

**Step 3 — Change Plan:**
- Before updating the actual related code, propose a step-by-step change plan:
  - Step 1: Which file/class/function to modify first
  - Step 2: How to propagate changes to downstream dependencies/callers
  - Step 3: How to update tests/documentation/configuration accordingly
- If a refactoring opportunity toward a better structure in terms of reduced coupling / increased cohesion is visible, propose it together (execution only after user approval).

**Proportionality Rule — Always perform the protocol, but the depth of analysis is proportional to the scope of the change:**

| Change Scale | Criteria | Application Depth |
|-------------|----------|------------------|
| **Minor** | Typos, comments, formatting, etc. — changes unrelated to logic | Step 1 only — confirm "no ripple effect" in 1 sentence, then execute immediately |
| **Standard** | Function/logic changes, file additions/deletions | Perform all 3 steps |
| **Large-scale** | Architecture, public API, cross-cutting changes | All 3 steps + **mandatory** user approval in advance |

Application examples:

```
Bad:  "User requests function modification → modify only that function → 6 callers get runtime errors"
Good: "User requests function modification → check 6 call sites → notify of impact scope → propose step-by-step change plan → execute after approval"
```

**Communication Rules:**
- Avoid unnecessarily verbose theoretical explanations; focus on practical code and concrete steps.
- Add a brief rationale to important design choices.
- Even when there are ambiguities, do not avoid the task — explicitly state a "reasonable assumption" and propose the best design.

### Priority Among Absolute Standards

> **Absolute Standard 1 (quality) is the highest. Absolute Standards 2 (SOT) and 3 (CCP) are co-equal means for ensuring quality.**

```
Absolute Standard 1 (Quality) — Highest. The reason for existence of all standards.
  ├── Absolute Standard 2 (SOT) — Means for ensuring data integrity
  └── Absolute Standard 3 (CCP) — Means for ensuring code change quality
```

Absolute Standards 2 (SOT) and 3 (CCP) operate in different dimensions, so direct conflicts are unlikely. If either standard conflicts with Absolute Standard 1 (quality), quality wins. Both SOT and CCP are **means** to ensure quality, not **ends** that constrain quality.

Conflict scenarios and resolutions:
- SOT single write point creates information bottleneck, causing agents to work with stale data → **Allow direct artifact reference between agents** (adjust SOT structure)
- Adding steps to improve quality increases SOT state complexity → **Accept it** (Absolute Standard 1 > 2)
- In completely independent parallel tasks (no shared state between agents), SOT is unnecessary → **Allow SOT lightweighting** (document the rationale)
- Full CCP analysis creates excessive overhead for trivial changes → **Apply proportionality rule** (minor changes use Step 1 only)

---

## 3. Design Principles

Subordinate principles under the Absolute Standards.

### P1. Data Refinement for Accuracy

Passing large data directly to AI degrades accuracy due to noise.

- Explicitly specify **pre-processing** at each step: remove noise before passing to agents
- Explicitly specify **post-processing** at each step: refine artifacts before passing to the next step
- Pre-compute correlations that can be deterministically computed in code → AI focuses on judgment and analysis

```
Bad:  "Pass collected full webpage HTML to agent"
Good: "Extract body text only with Python script → pass only key text to agent"
```

### P2. Expertise-Based Delegation Structure

Delegate each task to the specialized agent best suited to perform it, maximizing quality. The Orchestrator coordinates overall quality, while specialized agents focus deeply on their own domains.

```
Orchestrator (quality coordination + flow management)
  ├→ Agent A: specialized research (optimized for the domain)
  ├→ Agent B: in-depth analysis (focused solely on analysis)
  └→ Agent C: verification and quality gate
```

#### Orchestrator Role Definition

**Orchestrator = the main Claude session**. The main session that executes the workflow — not a separate agent file — performs the Orchestrator role. In `(team)` steps, **the Orchestrator concurrently serves as Team Lead**.

| Role | Subject | SOT Write | Start Point |
|------|---------|-----------|-------------|
| Orchestrator | Main Claude session | **Can write** (only one) | When workflow starts |
| Team Lead | Orchestrator (concurrent) | **Can write** | When entering a `(team)` step |
| Sub-agent | Created via `Task` tool | **Read-only** | When Orchestrator calls |
| Teammate | Created via `Task` + `TeamCreate` | **Read-only** | When Team Lead assigns |

#### Sub-agent Invocation Protocol

Standard protocol when the Orchestrator invokes Sub-agents (`@translator`, `@reviewer`, `@fact-checker`):

**1. Invocation method**: Specify agent name via `subagent_type` parameter of the `Task` tool
```
Task(subagent_type="translator", prompt="...", ...)
```

**2. Context that must be included in the prompt**:
- Workflow step number (step N)
- Input artifact file path (absolute path)
- Verification criteria for that step (if applicable)
- SOT `outputs.step-N` path (where artifact will be stored)
- Reference file paths (glossary.yaml, previous step artifacts, etc.)

**3. Receiving results**: The `Task` tool returns results when the Sub-agent terminates.
- Orchestrator confirms that the artifact file was created on disk
- Run P1 validation scripts (validate_review.py, validate_translation.py, etc.)
- Record the path in SOT `outputs.step-N` (performed by the Orchestrator)

**4. `(team)` Step Task Lifecycle**:
```
Team Lead (=Orchestrator)
  1. TeamCreate → record SOT active_team
  2. TaskCreate (subject, description, owner=@teammate)
  3. Task(subagent_type, team_name, ...) → create Teammate
  4. Teammate: perform task → L1 self-verification → L1.5 pACS self-rating
  5. Teammate: SendMessage (report + pACS score) → TaskUpdate (completed)
  6. Team Lead: receive report → L2 comprehensive verification → update SOT
  7. TeamDelete → move SOT active_team → completed_teams
```

**Dense Checkpoint Pattern (DCP)**: For Tasks with turn count > 10, insert intermediate checkpoints (CP-1/2/3). Details: `references/claude-code-patterns.md §DCP`

### P3. Resource Accuracy

For steps that require images, files, or external resources, explicitly specify the exact path. Missing placeholders are not allowed.

### P4. Question Design Rules

When asking questions to the user:
- Maximum 4 questions
- Provide approximately 3 options per question
- Proceed without asking when there are no ambiguities

### P5. English-First Execution

All internal agent/skill/hook logic must be written in English.

- **Why**: Korean consumes 2-3× more tokens; English is the primary training language of LLMs
- **Scope**: Agent specs, skill references, hook scripts, verification criteria, SOT field names
- **Exception**: User-facing output (reports, notifications, HITL messages) may be Korean

### P6. Python-First Judgment

> **"Python is the judge, LLM is the narrator."**

All deterministic judgments — classification thresholds, validation rules, pACS arithmetic — must be executed in Python code. LLM handles narration only.

- **Why**: LLMs hallucinate numeric thresholds and self-reported scores drift from reality
- **How**: Pre-compute all classifiable values before passing to LLM context
- **Examples**:
  - Direction classification: `get_direction(return_4w)` in `stock_selector.py`
  - Translation pACS: `pacs_calculator.py` computes Ft/Ct/Nt from actual text (not AI self-report)
  - SOT step validation: `advance_step()` enforces monotonic increment (`new_step == current_step + 1`)
  - Category A vs B: `classify_category()` uses numeric guards, never LLM judgment
- **Enforcement**: PA8 validation (`validate_pacs.py`) catches divergence between AI self-report and Python pACS ≥ 15 points

---

## 4. Project Structure

```
AgenticWorkflow/
├── CLAUDE.md          ← Claude Code-specific instructions
├── AGENTS.md          ← This file (model-agnostic common instructions)
├── README.md          ← Project introduction
├── AGENTICWORKFLOW-USER-MANUAL.md              ← User manual
├── AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md  ← Design philosophy and architecture overview
├── DECISION-LOG.md          ← Project design decision log (ADR)
├── COPYRIGHT.md          ← Copyright
├── .claude/
│   ├── settings.json          ← Hook settings (Setup + SessionEnd)
│   ├── agents/                ← Sub-agent definitions
│   │   ├── translator.md     (English→Korean translation specialist agent — glossary-based term consistency)
│   │   ├── reviewer.md       (Adversarial Review — critical analysis of code/artifacts, read-only)
│   │   └── fact-checker.md   (Adversarial Review — external fact verification, web access)
│   ├── commands/              ← Slash Commands
│   │   ├── install.md         (Setup Init validation result analysis — /install)
│   │   └── maintenance.md     (Setup Maintenance health check — /maintenance)
│   ├── hooks/scripts/         ← Context Preservation System + Setup Hooks + Safety Hooks
│   │   ├── context_guard.py   (Hook unified dispatcher — single entry point for 4 events)
│   │   ├── _context_lib.py    (shared library — parsing, generation, SOT capture, Smart Throttling, Autopilot state read/validate, ULW detect/compliance validate, trimming constants centralization, sot_paths() path unification, multi-phase transition detection, decision quality tag alignment, Error Taxonomy 12 patterns+Resolution matching, Success Patterns (Edit/Write→Bash success sequence extraction), IMMORTAL-aware compression+audit trail, E5 Guard centralization (is_rich_snapshot+update_latest_with_guard), Knowledge Archive integration (archive_and_index_session — partial failure isolation), path tag extraction (extract_path_tags), KI schema validation (_validate_session_facts — RLM required key guarantee), SOT schema validation (validate_sot_schema — workflow state.yaml structural integrity 8-item check: S1-S6 basic + S7 pacs 5 fields (dimensions, current_step_score, weak_dimension, history, pre_mortem_flag) + S8 active_team 5 fields (name, status(partial|all_completed), tasks_completed, tasks_pending, completed_summaries)), Adversarial Review P1 validation (validate_review_output R1-R5, parse_review_verdict, calculate_pacs_delta, validate_review_sequence), Translation P1 validation (validate_translation_output T1-T7, check_glossary_freshness T8, verify_pacs_arithmetic T9 generic, validate_verification_log V1a-V1c), Predictive Debugging P1 (aggregate_risk_scores+validate_risk_scores RS1-RS6+_RISK_WEIGHTS 13 weights+_RECENCY_DECAY_DAYS decay), pACS P1 validation (validate_pacs_output PA1-PA6 — pACS log structural integrity: file existence·minimum size·dimension scores·Pre-mortem·min() arithmetic·Color Zone), L0 Anti-Skip Guard (validate_step_output L0a-L0c — artifact file existence+minimum size+non-whitespace), Team Summaries KI archive (_extract_team_summaries — SOT active_team.completed_summaries → KI preservation), Abductive Diagnosis Layer (diagnose_failure_context pre-evidence collection + validate_diagnosis_log AD1-AD10 post-validation + _extract_diagnosis_patterns KA archiving + Fast-Path FP1-FP3 + hypothesis priority H1/H2/H3), module-level regex compilation (9+8+8+4+5 patterns — 1 time per process))
│   │   ├── save_context.py    (save engine)
│   │   ├── restore_context.py (restore — RLM pointer + completion/Git state + Predictive Debugging risk score cache generation)
│   │   ├── update_work_log.py (work log accumulation — 9 tools tracked)
│   │   ├── generate_context_summary.py (incremental snapshot + Knowledge Archive + E5 Guard + Autopilot Decision Log safety net + ULW Compliance safety net)
│   │   ├── setup_init.py      (Setup Init — infrastructure health validation + SOT write pattern validation (P1 hallucination containment), --init trigger)
│   │   ├── setup_maintenance.py (Setup Maintenance — periodic health check, --maintenance trigger)
│   │   ├── block_destructive_commands.py (PreToolUse Safety Hook — dangerous command blocking (P1 hallucination containment), exit code 2 block + Claude self-correction)
│   │   ├── block_test_file_edit.py  (PreToolUse TDD Guard — test file edit blocking (.tdd-guard toggle), exit code 2 block + redirect to implementation code modification)
│   │   ├── predictive_debug_guard.py (PreToolUse Predictive Debug — error history-based risky file warning, exit code 0 warning only)
│   │   ├── output_secret_filter.py  (PostToolUse secret detection — 3-tier extraction (tool_response→file read→transcript), 25+ regex patterns, 2-pass scan (raw+base64/URL), fcntl-locked audit log, exit code 0 warning only)
│   │   ├── security_sensitive_file_guard.py (PostToolUse security-sensitive file warning — .env/PEM/credentials/cloud/K8s/terraform etc. 12 patterns, session dedup, exit code 0 warning only)
│   │   ├── diagnose_context.py  (Abductive Diagnosis pre-evidence collection — generate evidence bundle on quality gate FAIL, Orchestrator manual invocation)
│   │   ├── query_workflow.py    (workflow observability — 4 modes: dashboard/weakest/retry/blocked, P1 SOT schema validation + context-aware pACS extraction)
│   │   ├── validate_pacs.py    (pACS P1 validation + L0 Anti-Skip Guard — PA1-PA7, standalone script, JSON output)
│   │   ├── validate_review.py (Adversarial Review P1 validation — R1-R5, standalone script, JSON output)
│   │   ├── validate_translation.py (Translation P1 validation — T1-T9 + glossary validation, JSON output)
│   │   ├── validate_verification.py (Verification Log P1 validation — V1a-V1c structural integrity, JSON output)
│   │   ├── validate_diagnosis.py (Abductive Diagnosis P1 post-validation — AD1-AD10, JSON output)
│   │   ├── validate_traceability.py (Cross-Step Traceability P1 validation — CT1-CT5, JSON output)
│   │   ├── validate_domain_knowledge.py (Domain Knowledge P1 validation — DK1-DK7, JSON output)
│   │   ├── validate_workflow.py (DNA inheritance P1 validation — W1-W8, JSON output)
│   │   ├── validate_retry_budget.py (Retry Budget P1 validation — RB1-RB3 retry budget determination (ULW-aware), JSON output)
│   │   ├── _test_secret_filter.py   (output_secret_filter tests — 44 tests)
│   │   ├── _test_sensitive_file_guard.py (security_sensitive_file_guard tests — 44 tests)
│   │   └── _test_block_destructive.py (block_destructive_commands tests — 43 tests)
│   ├── context-snapshots/     ← runtime snapshots (gitignored)
│   └── skills/
│       ├── workflow-generator/   ← workflow design and generation
│       │   ├── SKILL.md          (skill definition + Absolute Standards)
│       │   └── references/       (implementation patterns, templates, document analysis guide)
│       └── doctoral-writing/     ← doctoral-level academic writing
│           ├── SKILL.md          (skill definition + Absolute Standards)
│           └── references/       (checklists, common errors, correction examples, domain-specific guides)
├── prompt/              ← prompt materials
│   ├── crystalize-prompt.md      (prompt compression techniques)
│   ├── distill-partner.md        (essence extraction and optimization)
│   └── crawling-skill-sample.md  (crawling skill sample)
└── coding-resource/     ← reference materials
```

### Context Preservation System

An automatic save/restore system that prevents loss of work context when the context window is exhausted, session is cleared, or context is compacted.

**Core Principles:**
- RLM pattern applied: Persist work history as **external memory objects** (MD files) and restore pointer-based in new sessions
- P1 principle compliance: Transcript parsing and statistics calculation are performed deterministically by Python code. AI focuses only on semantic interpretation
- Absolute Standard 2 compliance: SOT file (`state.yaml`) accessed **read-only** only. Snapshots stored in a separate directory (`context-snapshots/`)
- **Knowledge Archive**: Cross-session knowledge accumulation — session facts are deterministically extracted and accumulated in `knowledge-index.jsonl`. Recorded in both Stop hook and SessionEnd/PreCompact to guarantee 100% session indexing. Each entry includes completion_summary (tool success/failure), git_summary (change state), session_duration_entries (session length), phase (session phase), phase_flow (multi-phase transition flow), primary_language (primary file extension), error_patterns (Error Taxonomy 12-pattern classification + resolution matching), tool_sequence (RLE-compressed tool sequence), final_status (success/incomplete/error/unknown), tags (path-based search tags — CamelCase/snake_case separation + extension mapping). AI performs programmatic exploration via Grep (RLM pattern)
- **Resume Protocol**: Snapshots include deterministic restore instructions — list of modified/referenced files, session metadata, completion state (tool success/failure), Git change state. **Dynamic RLM query hints**: Automatically generate session-specific Grep query examples based on tags extracted from modified file paths (`extract_path_tags()`) and error information. Ensures a baseline of restoration quality
- **Autopilot runtime reinforcement**: When Autopilot is active, include an Autopilot state section (IMMORTAL priority) in snapshots, and inject execution rules into context when restoring a session. Stop hook detects and supplements missing Decision Log entries
- **ULW mode detection and preservation**: `detect_ulw_mode()` detects the `ulw` keyword in the transcript using word-boundary regex. When active, include a ULW state section (IMMORTAL priority) in snapshots, and SessionStart injects 3 Intensifiers into context. `check_ulw_compliance()` deterministically verifies compliance. Tags `ulw_active: true` in Knowledge Archive
- **Decision quality tag alignment**: The "key design decisions" section of snapshots is sorted in the order `[explicit]` > `[decision]` > `[rationale]` > `[intent]`, so that high-signal decisions are prioritized in the 15 slots. Comparison, trade-off, and choice patterns are also extracted
- **IMMORTAL-aware compression**: When snapshot size exceeds limits, preserve IMMORTAL sections first and trim non-IMMORTAL content first. In extreme cases, preserve the beginning of IMMORTAL text. **Compression audit trail**: Each compression Phase records the number of characters removed as an HTML comment (`<!-- compression-audit: ... -->`) at the end of the snapshot (Phase 1~7 per-phase delta + final size)
- **Error Taxonomy**: Classifies tool errors into 12 patterns (file_not_found, permission, syntax, timeout, dependency, edit_mismatch, type_error, value_error, connection, memory, git_error, command_not_found). Uses negative lookahead and qualifier matching to prevent false positives. Recorded in the error_patterns field of Knowledge Archive. **Error→Resolution matching**: Detects successful tool calls within 5 entries after an error via file-aware matching and records them in the `resolution` field (tool name + file name). `Grep "resolution" knowledge-index.jsonl` enables cross-session exploration of resolution patterns
- **System command filtering**: Filters system commands such as `/clear`, `/help`, etc. from the "current task" section of snapshots, capturing only actual work intent
- **Crash-safe writes**: All file writes (snapshots, archive, log cleanup) use atomic write (temp → rename) pattern. Prevents partial writes on process crash
- **P1 Hallucination Prevention**: Enforces tasks that must be 100% accurate repeatedly using Python code. (1) **KI schema validation**: `_validate_session_facts()` guarantees the existence of RLM required keys (session_id, tags, final_status, etc. — 10 keys) immediately before knowledge-index writes — fills safe defaults if missing. (2) **Partial failure isolation**: In `archive_and_index_session()`, archive file write failure does not block knowledge-index updates — protecting the core RLM asset. (3) **SOT write pattern validation**: `setup_init.py`'s `_check_sot_write_safety()` detects co-occurrence of SOT filename + write patterns in Hook scripts using AST function-boundary analysis. (4) **SOT schema validation**: `validate_sot_schema()` validates structural integrity of workflow state.yaml across 8 items (S1-S6 basic + S7 pacs 5 fields + S8 active_team 5 fields). (5) **Adversarial Review P1 validation**: `validate_review_output()` R1-R5, `parse_review_verdict()`, `calculate_pacs_delta()`, `validate_review_sequence()` deterministically guarantee review quality

**Data Flow:**

```
Task in progress ─→ [PostToolUse] update_work_log.py ─→ work_log.jsonl accumulation (9 tools tracked)
                 ├→ [PostToolUse] output_secret_filter.py ─→ Bash|Read output secret detection (3-tier extraction, 25+ patterns, standalone)
                 └→ [PostToolUse] security_sensitive_file_guard.py ─→ Edit|Write sensitive file warning (standalone)
                                                         │ (when token > 75%)
                                                         ↓
Response complete ────→ [Stop] generate_context_summary.py ─→ latest.md saved (30-second throttling)
                                                         │        + knowledge-index.jsonl accumulated
                                                         │        + sessions/ archived
                                                         │        + E5 Empty Snapshot Guard
                                                         ↓
Session end/compact ─→ [SessionEnd/PreCompact] save_context.py ─→ latest.md saved
                                                         │        + knowledge-index.jsonl accumulated
                                                         │        + sessions/ archived
                                                         ↓
New session start ──→ [SessionStart] restore_context.py ───────→ pointer+summary+completion state+Git state output
                                                         AI reads in full via Read tool
```

---

## 5. Implementation Element Mapping

When designing workflows, combine the following implementation elements. The names differ by tool but the concepts are the same.

| Workflow Element | Concept | Selection Criteria |
|-----------------|---------|-------------------|
| **Specialized agent** | Single agent focused on a specific domain | When deep context maintenance is key to quality |
| **Agent group** | Multiple agents working independently in parallel | When multi-perspective analysis and cross-validation improves quality |
| **Human intervention point** | User interaction for review/approval/selection | When judgment that cannot be automated is required |
| **Automated verification** | Quality gate, format check, security check | When automating repetitive verification |
| **Reusable module** | Encapsulating domain knowledge and recurring patterns | When applying validated patterns consistently |
| **External integration** | API, DB, external service integration | When external data/functionality is needed |
| **Dynamic question collection** | Collecting information via structured questions to users during execution | Apply P4 rule. When options cannot be predefined and dynamic judgment is needed |
| **Task assignment and tracking** | When using agent groups: task creation, assignment, dependency, and progress tracking | Does not replace SOT. When coordination between agents is needed |

> **The sole criterion for agent selection is "which structure maximizes the quality of the final artifact."**
> Do not select an agent group just because parallel processing is faster.
> Do not select a single agent just because it uses fewer tokens.

#### Specialized Agent vs. Agent Group — Quality Judgment Matrix

Structure is determined by 5 quality factors. "Faster" and "cheaper" are not judgment criteria:

| Quality Factor | Specialized Agent Advantage | Agent Group Advantage | Judgment Question |
|---------------|----------------------------|----------------------|------------------|
| **Context depth** | When preceding step results must be deeply referenced | When each task requires independent expertise | "Does losing the nuance of the previous step degrade quality?" |
| **Cross-validation** | When a single perspective guarantees consistency | When multi-perspective analysis removes bias | "Does a different viewpoint improve result reliability?" |
| **Artifact consistency** | When uniformity of style/tone is important | When each artifact is independently complete | "Is tone inconsistency between artifacts a quality problem?" |
| **Error isolation** | When errors must be caught in the full context | When individual task failure should not affect other tasks | "Does one failure contaminate the whole?" |
| **Information transfer loss** | When risk of nuance loss during file handoff is high | When passing only structured data is sufficient | "Does passing via context summary cause information loss?" |

**Judgment Rules:**
1. If specialized agent advantage ≥ 3 of 5 factors → **Specialized agent**
2. If agent group advantage ≥ 3 → **Agent group**
3. If tied (2:2 + 1 undecidable) → **Context depth** factor is tiebreaker (maintaining context is generally safer)
4. If uncertain → **Specialized agent** (safe default — guarantees context maintenance)

#### Model Level Selection — Quality-Based Judgment

| Model Level | Selection Criteria | Suitable Tasks |
|------------|-------------------|----------------|
| **Top tier** | Core tasks — directly impacts final quality | Core analysis, final writing, strategic judgment, code architecture |
| **Stable tier** | Repetitive tasks — patterns are well-established | Data collection, format conversion, standardized classification |
| **Auxiliary tier** | Simple tasks — minimal judgment required | Format validation, simple filtering, label extraction |

**Judgment Procedure:**
1. How directly does this task impact the quality of the final artifact?
2. Is the quality difference between model levels significant?
   - If significant → higher model
   - If not significant → lower model allowed
3. If uncertain → **higher model** (quality assurance principle — Absolute Standard 1)

### 5.1 Autopilot Mode

A mode that auto-approves **human-in-the-loop** intervention points during workflow execution for uninterrupted operation.

**Core Principles:**
- Autopilot performs **auto-approval** of human intervention points only
- All workflow steps are **fully executed** — step skipping is prohibited
- All artifacts are produced at **full quality** — abbreviation is prohibited
- Automated verification (Hook exit code 2) **remains blocking** even in Autopilot

**Scope Distinction:**

| Mechanism | Autopilot Behavior | Rationale |
|-----------|-------------------|-----------|
| Human intervention point `(human)` | Auto-approve — select quality-maximizing default | AI acts on behalf of human judgment |
| Dynamic question collection | Auto-respond — select quality-maximizing option | AI acts on behalf of human choice |
| Automated verification `(hook)` exit code 2 | **No change — remains blocking** | Deterministic verification is not subject to human judgment substitution |

**Anti-Patterns:**
1. Autopilot ≠ step skipping: Execute all steps sequentially and completely
2. Autopilot ≠ abbreviated output: All agents produce artifacts of the same quality and volume as they would when reviewed by a human

**Anti-Skip Guard (runtime verification):**

Deterministic verification performed by the Orchestrator at each step completion:
1. Is the artifact file recorded as a path in SOT `outputs`?
2. Does that file exist on disk?
3. Is the file size at least 100 bytes or more? (ensures meaningful content)

> In Claude Code's Hook system, the `validate_step_output()` function in `_context_lib.py` performs this verification deterministically. In other tools, implement equivalent file validation logic.

**SOT Record:**
```yaml
workflow:
  name: "my-workflow"
  current_step: 3
  status: "running"
  outputs:
    step-1: "research/raw-contents.md"
    step-2: "analysis/insights-list.md"
  autopilot:
    enabled: true
    activated_at: "ISO-8601"
    auto_approved_steps: [3, 6]
```

- `autopilot.enabled`: Boolean — whether Autopilot is activated
- `autopilot.auto_approved_steps`: List of auto-approved step numbers
- `outputs`: Per-step artifact paths — verification target for the Anti-Skip Guard
- Auto-approval decisions are recorded in a separate log file (`autopilot-logs/step-N-decision.md`) (for transparency)
- Decision Log standard template: Refer to `references/autopilot-decision-template.md` in Claude Code

**Runtime Reinforcement (Claude Code implementation):**

| Layer | Mechanism | Reinforcement Content |
|-------|-----------|----------------------|
| **Hook** | SessionStart context injection | Inject Autopilot execution rules + previous step verification results into prompt at session start/restore |
| **Hook** | Snapshot Autopilot section | Preserve Autopilot state with IMMORTAL priority at session boundaries |
| **Hook** | Stop Decision Log safety net | Detect auto-approval patterns → supplement missing Decision Log |
| **Hook** | PostToolUse progress tracking | Record step progress in work_log with `autopilot_step` field |
| **Prompt** | Execution Checklist | List of required actions at start/execution/completion of each step as defined below (Claude Code details: `docs/protocols/autopilot-execution.md`) |

> The Hook layer accesses SOT in **read-only** mode only (Absolute Standard 2 compliance).

**Autopilot Execution Checklist (common to all tools):**

Required actions to perform at each step when executing a workflow in Autopilot mode with any tool:

| Timing | Required Action |
|--------|----------------|
| **Before step starts** | Check SOT `current_step`, verify previous step artifact file exists + is not empty, read `Verification` criteria |
| **During step execution** | Fully execute all tasks (no abbreviation — Absolute Standard 1), generate artifacts at full quality |
| **After step completes** | Save artifact to disk, self-verify against `Verification` criteria, re-execute only the failed part if failed (max 10 times, max 15 times when ULW is active — §5.1.1), record path in SOT `outputs`, increment `current_step` +1, generate Decision Log |
| **Absolutely prohibited** | Increment `current_step` by 2 or more at once, proceed without artifacts, "auto so brief it's abbreviated," proceed with Verification FAIL |

> **Claude Code details**: `docs/protocols/autopilot-execution.md` additionally defines Claude Code-specific checklists for `(team)` steps, translation, Hook integration, etc.

**Activation:** Default is inactive (interactive). Activated by `Autopilot: enabled` explicitly stated in workflow Overview or by user instruction during execution. Toggleable during execution.

### 5.1.1 ULW Mode (Claude Code)

**ULW (Ultrawork)** is a **thoroughness intensity overlay that is orthogonal to Autopilot**. Activated by including `ulw` in the prompt.

- **Autopilot** = automation axis (HOW) — skipping `(human)` approvals
- **ULW** = thoroughness axis (HOW THOROUGHLY) — complete execution without omissions, through to error resolution

**2x2 Matrix:**

|  | **ULW OFF** | **ULW ON** |
|---|---|---|
| **Autopilot OFF** | Standard interactive | Interactive + Sisyphus Persistence (3 tries) + mandatory task decomposition |
| **Autopilot ON** | Standard automated workflow | Automated workflow + Sisyphus reinforcement (3 retries) + team thoroughness |

**3 Intensifiers:**
1. **I-1. Sisyphus Persistence** — Maximum 3 retries, each attempt uses a different approach. 100% completion or report reason for impossibility
2. **I-2. Mandatory Task Decomposition** — TaskCreate → TaskUpdate → TaskList required
3. **I-3. Bounded Retry Escalation** — No more than 3 retries on the same target (quality gates have separate budget), escalate to user if exceeded

**Deterministic reinforcement:** Python Hook deterministically verifies compliance with 3 Intensifiers (Compliance Guard). Records warnings in snapshot IMMORTAL section on violation.

> **Combination rule**: ULW **reinforces** Autopilot — raises quality gate retry limit from 10→15. Safety Hook blocking is always respected.

Details: `docs/protocols/ulw-mode.md`

### 5.2 English-First Execution and Translation Protocol

During workflow **execution**, all agents **work in English** and **produce artifacts in English**. Since AI performs at its highest level in English, English-first execution is a direct implementation of **Absolute Standard 1 (quality)**.

#### Language Boundaries

| Activity | Language | Rationale |
|----------|----------|-----------|
| Workflow design (workflow-generator skill) | Korean | Conversation with the user |
| Agent definitions (`.claude/agents/*.md`) | English | Maximize agent prompt quality |
| Workflow execution (agent tasks) | **English** | Maximize AI performance |
| Artifact translation | English→Korean | `@translator` specialized Sub-agent |
| SOT records | Language-agnostic | Structural data: paths, numbers, etc. |

> **Design documents (`workflow.md`) remain in Korean**. They are blueprints read and reviewed by users, so the user's language is used. Language switching occurs at the **design→execution** boundary.

#### Translation Scope Determination

Not every step requires translation:

| Artifact Type | Translate? | Example |
|--------------|-----------|---------|
| Text content (analysis, reports, summaries) | **Translate** | `.md`, `.txt` |
| Code files | Do not translate | `.py`, `.js`, `.ts` |
| Data files | Do not translate | `.json`, `.csv` |
| Configuration files | Do not translate | `.yaml` config, `.env` |

When designing a workflow, specify `Translation: @translator` or `Translation: none` for each step to determine whether translation applies.

#### Translation Execution Protocol

**Sub-agent selection rationale**: Since term consistency and context accumulation are key to translation quality, a **specialized agent (Sub-agent)** has a quality advantage over an agent group (based on the "context depth" + "artifact consistency" factors in the §5 quality matrix).

**Execution sequence**:

```
Step N English artifact complete
  → Record SOT outputs.step-N + Anti-Skip Guard validation
  → Call @translator Sub-agent (only for steps with Translation: @translator)
    ① Read translations/glossary.yaml (terminology — RLM external persistent state)
    ② Read full English original
    ③ Complete translation using established terms (no abbreviation — Absolute Standard 1)
    ④ Self-review: compare with source, verify term consistency
    ⑤ Update glossary.yaml (add new terms)
    ⑥ Generate *.ko.md file
  → Record SOT outputs.step-N-ko
  → Confirm translation file exists + is not empty
  → P1 validation: python3 .claude/hooks/scripts/validate_translation.py --step N --project-dir . --check-pacs --check-sequence
  → Proceed to Step N+1
```

#### Terminology Glossary

`translations/glossary.yaml` is the translation agent's **persistent external memory** (RLM pattern). Together with `memory: project` (ADR-051), it forms a 2-layer memory: glossary.yaml = explicit term mappings, persistent memory = implicit style/tone pattern accumulation.

```yaml
# translations/glossary.yaml
terms:
  "Single Source of Truth": "단일 소스 오브 트루스(Single Source of Truth)"
  "Anti-Skip Guard": "Anti-Skip Guard"  # preserved in English
  "workflow step": "워크플로우 단계"
```

**Architectural compatibility**:
- glossary is **not SOT** — it is the translation agent's local working file
- Not managed by the Orchestrator — managed by the translation agent itself
- No concurrent write risk — translation executes sequentially (once after each step completes)
- Hierarchical memory: glossary.yaml (explicit terminology dictionary) + `memory: project` (implicit experience accumulation) — 2 layers (ADR-051)

#### SOT Record Rules

```yaml
outputs:
  step-1: "research/raw-contents.md"          # English original
  step-1-ko: "research/raw-contents.ko.md"    # Korean translation
  step-2: "data/processed.json"               # no translation needed → no -ko
  step-3: "analysis/report.md"
  step-3-ko: "analysis/report.ko.md"
```

- `step-N-ko` keys follow the suffix rule: automatically skipped by the Anti-Skip Guard's `.isdigit()` guard
- Anti-Skip Guard validates only `step-N` (English original) → translation validation is performed in the Orchestrator checklist
- Steps without translation do not generate a `-ko` key

#### `(team)` Step Translation

Translation targets in agent group steps are **only official artifacts recorded in SOT `outputs.step-N`**:

1. Team Lead merges all Teammate artifacts
2. Record SOT `outputs.step-N` + Anti-Skip Guard validation
3. Team Lead calls `@translator` (for the merged official artifact)
4. Record SOT `outputs.step-N-ko`

> Individual Teammate artifacts are intermediate work products (not recorded in SOT) and are not translated.

#### Independent Translation Verification (optional — for final deliverables)

By default, the translation agent's **self-review** is sufficient. For steps where quality is particularly critical, such as final deliverables, an independent verification Sub-agent can be added:

```
@translator → output.ko.md
  → @translation-verifier (separate Sub-agent)
    ① Read English original and Korean translation simultaneously
    ② Verify accuracy, completeness, term consistency, naturalness
    ③ Pass/Fail verdict + feedback
  → On Fail: request re-translation from @translator with feedback
```

This pattern is applied optionally when designing the workflow.

### 5.3 Verification Protocol (Task Verification)

A protocol for verifying whether the artifact of each workflow step has **100% achieved its functional goal**.

**Core Principle:**
> **"Declare the definition of completion first, verify after execution, and re-execute on failure."**

The Anti-Skip Guard (file existence + 100 bytes or more) guarantees **physical existence**, and the Verification Protocol guarantees **content completeness**. The two layers operate independently, and both must pass before proceeding to the next step.

```
Quality assurance layer structure:

  Anti-Skip Guard (Hook — deterministic)
    "Does the file exist and have a meaningful size?"
      ↓ PASS
  Verification Gate (Agent — semantic)
    "Was the functional goal 100% achieved?"
      ↓ PASS
  SOT update + proceed to next step
```

#### Declaring Verification Criteria

Define a `Verification` field for each step of the workflow. **Place it before the Task** so that the agent starts work already aware of "what completion means."

```markdown
### N. [Step Name]
- **Verification**:
  - [ ] [Specific, measurable criterion]
  - [ ] [Specific, measurable criterion]
- **Task**: [task description]
```

#### Verification Criteria Types (5 types)

| Type | Verification Target | Good Example | Bad Example |
|------|--------------------|-----------|-----------|
| **Structural completeness** | Internal structure of artifact | "All 5 sections included (Intro, Analysis, Comparison, Recommendation, References)" | "Well-structured" |
| **Functional goal** | Task goal achievement | "Each competitor's pricing data includes 3+ tiers + exact amounts" | "Has pricing information" |
| **Data consistency** | Data accuracy | "All URLs are valid with no placeholder/example.com" | "Links confirmed" |
| **Pipeline connectivity** | Input compatibility with next step | "Includes competitor_name, pricing_tiers, feature_list fields needed by Step 4 analysis agent" | "Compatible with next step" |
| **Cross-step traceability** | Logically derived from previous step data | "80%+ of analysis claims traceable via [trace:step-N] markers" | "Data-based" |

> **Criteria writing rules**: Each criterion must be **mechanically determinable as true or false by a third party**. Subjective judgments ("good quality," "sufficient depth") are not used as criteria. Subjective quality judgment is handled by existing `(human)` checkpoints.

#### Domain Knowledge Structure (DKS)

A pattern for validating the soundness of domain-specific reasoning. Build `domain-knowledge.yaml` in the Research phase and use it as validation criteria in the Implementation phase. Optional — not all domains require it. Validation script: `validate_domain_knowledge.py` (DK1-DK7).

**DKS necessity judgment criteria**:

| Domain | DKS Necessity | Reason |
|--------|--------------|--------|
| Medical/clinical, legal | High | Need to validate soundness of domain-specific reasoning (symptoms→disease, case law→principle) |
| Competitive analysis, market research | Medium | Quality improves when structuring relationships between entities (dominance, competition) |
| Blog/content, code generation | Low | Type system/tests substitute it, or domain reasoning is not needed |

#### Execution Protocol

```
1. Read verification criteria — agent first recognizes the definition of "100% complete"
2. Execute step — generate artifact at full quality (Absolute Standard 1)
3. Anti-Skip Guard — file existence + ≥ 100 bytes (deterministic)
4. Verification Gate — self-verify artifact against each criterion (semantic)
   ├─ All criteria PASS → generate verification-logs/step-N-verify.md → update SOT → proceed
   └─ 1 or more FAIL:
       ├─ Identify failure cause + re-execute only that part (not full rework)
       ├─ Re-verify (max 10 retries)
       └─ Still FAIL after 10 tries → escalate to user
5. Update SOT — record outputs, current_step +1
```

> **Scope of self-verification**: Verification in this protocol is a **completeness** check — "Was what needed to be done actually done?" Subjective **quality judgment** is handled by existing `(human)` checkpoints, and the Verification Protocol does not replace them.

#### Verification Log Format

Recorded in `verification-logs/step-N-verify.md`:

```markdown
# Verification Report — Step {N}: {Step Name}

## Criteria Check
| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [criterion text] | PASS | [specific evidence confirmed in artifact] |
| 2 | [criterion text] | FAIL→PASS | [initial failure reason] → [evidence after re-execution] |

## Result: PASS (retry: 1)
## Verified Output: research/insights.md (2,847 bytes)
```

#### (team) Step 3-Layer Verification

In agent group steps, 3-layer verification is performed:

| Layer | Performer | Verification Target | SOT Write |
|-------|-----------|--------------------|-----------|
| **L1** | Teammate (self-verification) | Verification criteria of own Task | **None** — completed within session |
| **L1.5** | Teammate (pACS) | Confidence of own Task artifact | **None** — include score in report message |
| **L2** | Team Lead (comprehensive verification + step pACS) | Verification criteria for the entire step | **Yes** — update SOT outputs + pacs |

```
Teammate: Execute task → self-verify (L1) → pACS self-rate (L1.5)
            → Report to Team Lead on PASS + GREEN/YELLOW (with pACS score included)
            → Self-correct and re-verify/re-rate on FAIL or RED

Team Lead: Receive Teammate artifact + pACS score
            → Comprehensive verification against step criteria (L2)
            → Step pACS = min(each Teammate pACS) — min-score principle applied
            → On PASS: update SOT (outputs + pacs)
            → On FAIL: specific feedback via SendMessage + re-execution instruction
```

> **SOT compatibility**: Teammates still only generate artifact files and do not write to SOT. Self-verification and pACS self-rating are completed within the Teammate's session and transmitted to the Team Lead via a report message (Absolute Standard 2 compliance). Only Team Lead records to `pacs-logs/` and updates SOT.

#### Backward Compatibility

| Situation | Behavior |
|-----------|----------|
| `Verification` field **present** | Verification Gate active — verify against criteria before proceeding |
| `Verification` field **absent** | Existing behavior maintained — proceed with Anti-Skip Guard only |

When generating new workflows, the `Verification` field must be included. Existing workflows can add it incrementally.

#### SOT Impact

**None.** The Verification Protocol is an agent execution protocol (prompt layer) and does not change the SOT structure. Progression of `current_step` already implicitly means verification is complete, and verification details are recorded in `verification-logs/` files.

### 5.4 pACS — predicted Agent Confidence Score (Self-Confidence Assessment)

A protocol where agents **structurally self-assess the confidence of their own artifacts** during workflow execution. Inspired by AlphaFold's pLDDT (predicted Local Distance Difference Test).

**Core Principle:**
> **"Before scoring, state your weaknesses first."** (Pre-mortem Protocol)

If the Verification Protocol (§5.3) verifies "completeness" — was what needed to be done actually done — then pACS quantifies **"confidence" — how much can the execution result be trusted**. The two protocols guarantee quality in different dimensions and operate independently.

#### 3 Evaluation Dimensions (Orthogonal Dimensions)

| Dimension | What Is Measured | Low Score Indicators |
|-----------|-----------------|---------------------|
| **F — Factual Grounding** | Robustness of factual basis | Unknown sources, memory-based reasoning, unverified assumptions |
| **C — Completeness** | No omissions relative to requirements | Some items skipped, insufficient analysis depth |
| **L — Logical Coherence** | Internal consistency of argumentation/structure | Contradictions, leaps in logic, mismatch between evidence and conclusion |

> **Reason for limiting to 3 dimensions**: Agent self-assessment is a subjective estimate without calibration data. More dimensions increase the illusion of precision and inter-dimension confounding. 3 orthogonal dimensions are the practical upper limit.

#### Min-Score Principle

> **pACS = min(F, C, L)**

Weighted averages are not used. If one dimension is low, overall confidence is low. The weakest link determines overall quality.

#### Pre-mortem Protocol (mandatory — perform before scoring)

A mechanism that structurally prevents score inflation. Before scoring, agents must answer the following 3 questions:

1. **"What is the most uncertain part of this artifact?"** — Areas with unverified sources, unknown recency, or relying on estimation
2. **"What is most likely to have been omitted?"** — Partially unmet requirements, unconsidered edge cases, data gaps
3. **"Where is the weakest link in this argument?"** — Evidence→conclusion leaps, insufficient premise verification, unexplored alternatives

If serious problems are revealed in the Pre-mortem responses, a high score cannot be assigned to that dimension.

#### Action Triggers

| Grade | Score Range | Action | Rationale |
|-------|-------------|--------|-----------|
| **GREEN** | pACS ≥ 70 | Auto-proceed | Agent has high confidence — normal quality |
| **YELLOW** | 50 ≤ pACS < 70 | Proceed but flag weakness | Partial uncertainty — subject to post-review |
| **RED** | pACS < 50 | Rework or escalate | Not trustworthy — must re-execute that part |

#### Quality Assurance Layer Structure (4 layers)

```
L0  Anti-Skip Guard (Hook — deterministic)
      "Does the file exist and have a meaningful size?"
        ↓ PASS
L1  Verification Gate (Agent — semantic)
      "Was the functional goal 100% achieved?"
        ↓ PASS
L1.5  pACS Self-Rating (Agent — confidence)
        Pre-mortem → F, C, L scoring → min(F,C,L) = pACS
        ↓ GREEN/YELLOW: proceed (YELLOW is flagged)
        ↓ RED: rework or escalate
L2    Adversarial Review (Enhanced — steps with Review: field specified)
        @reviewer/@fact-checker independently adversarially reviews artifact (§5.5)
```

> **Relationship between L1 and L1.5**: Verification Gate is "checklist item PASS/FAIL" — binary judgment. pACS is "overall confidence 0-100" — continuous self-assessment. Even if Verification passes all items, pACS can be low (e.g., all items covered but source quality is poor).

#### SOT Record

```yaml
workflow:
  # ... existing fields ...
  pacs:
    current_step_score: 72          # current step pACS
    dimensions: {F: 72, C: 85, L: 78}
    weak_dimension: "F"             # min-score dimension
    pre_mortem_flag: "Step 3: 2 data sources unverified"
    history:                        # per-step history
      step-1: {score: 85, weak: "C"}
      step-2: {score: 72, weak: "F"}
```

- `pacs` field is **append-only** to the existing SOT schema — independent from existing `workflow`, `autopilot`, `outputs`, `active_team` fields
- SOT without `pacs` operates normally (backward compatible)
- Hook's `capture_sot()` includes the entire SOT in the snapshot, so `pacs` field is automatically preserved at session boundaries

#### Translation pACS (for translated artifacts)

Additional 3 dimensions for translation artifacts produced by the `@translator` Sub-agent:

| Dimension | What Is Measured | Low Score Indicators |
|-----------|-----------------|---------------------|
| **Ft — Fidelity** | Accurate conveyance of source meaning | Excessive paraphrasing, meaning distortion, term inconsistency |
| **Ct — Translation Completeness** | No omissions relative to source | Paragraph/sentence/footnote omissions |
| **Nt — Naturalness** | Natural Korean, not a translation artifact | Direct translation of English word order, translation-ese |

Translation pACS = min(Ft, Ct, Nt). Action triggers: GREEN ≥ 85, YELLOW 70–84, RED < 70.

> **P6 Python-First**: After the `@translator` Sub-agent produces a translation, the Orchestrator runs `pacs_calculator.py` to independently compute Ft/Ct/Nt from the actual text. **Python's score is authoritative.** The translator's self-scored Ft/Ct/Nt serve only as a pre-mortem self-audit.

**PA8 3-Tier Verification** (enforced by `validate_pacs.py`):

| Tier | Condition | Action |
|------|-----------|--------|
| **FAIL** | Python pACS < 50 (system RED) | Block — re-translate (hard stop) |
| **WARN** | Python pACS 50–69 (quality RED) | Log warning — do not block, but flag |
| **Delta** | Python pACS ≥ 70 and \|AI − Python\| > 15 | Log divergence warning |

CLI usage:
```bash
python3 investscan/pacs_calculator.py --source report.md --target report.ko.md [--glossary translations/glossary.yaml]
# Exit 0 = GREEN/YELLOW; Exit 1 = RED (grade == "RED", pACS < 70)
```

#### L2 Adversarial Review (Enhanced — steps with Review: field specified)

An enhanced quality verification layer that replaces the existing L2 Calibration. `@reviewer` (critical analysis of code/artifacts, read-only) and `@fact-checker` (external fact verification, web access) independently review artifacts. Review results are deterministically quality-guaranteed via P1 validation (`validate_review.py`).

Apply to steps where `Review: @reviewer` or `Review: @reviewer + @fact-checker` is specified when designing the workflow. The default is self-assessment (L1.5) only.

Details: See §5.5 Adversarial Review.

#### pACS Log Format

Recorded in `pacs-logs/step-N-pacs.md`:

```markdown
# pACS Report — Step {N}: {Step Name}

## Pre-mortem
1. **Most uncertain**: [uncertain part]
2. **Likely omission**: [potential omission]
3. **Weakest link**: [weakest argument connection]

## Scores
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| F (Factual Grounding) | {0-100} | [specific basis] |
| C (Completeness) | {0-100} | [specific basis] |
| L (Logical Coherence) | {0-100} | [specific basis] |

## Result: pACS = {min(F,C,L)} → {GREEN|YELLOW|RED}
## Weak Dimension: {F|C|L} — {weakness description}
```

#### pACS in Autopilot

- pACS GREEN → auto-proceed
- pACS YELLOW → auto-proceed + record weak dimension in Decision Log
- pACS RED → auto-rework (max 10 times). If still RED after rework → escalate to user
- Add `pacs_score`, `weak_dimension` fields to Autopilot Decision Log

#### Backward Compatibility

| Situation | Behavior |
|-----------|----------|
| No pACS reference in workflow | Proceed with existing L0+L1 only |
| No `pacs` field in SOT | Normal operation — both Hook and agents ignore it |
| pACS without Verification | Not allowed — pACS is performed after passing Verification Gate |

> **Design decision**: Using pACS alone without Verification is prohibited. Doing confidence assessment (L1.5) without completeness verification (L1) makes a contradictory state possible: "omitted everything but high confidence."

### 5.5 Adversarial Review (Enhanced L2 — Adversarial Review)

An enhanced quality verification layer that replaces the existing L2 Calibration. Reviews artifacts independently using the Generator-Critic pattern.

#### Quality Layer Architecture

```
L0   Anti-Skip Guard (Hook — deterministic)
L1   Verification Gate (Agent self-check)
L1.5 pACS Self-Rating (Agent confidence)
L2   Adversarial Review (Enhanced L2) ← this section
       ├── Content critical analysis (LLM — @reviewer / @fact-checker)
       ├── Independent pACS scoring (LLM → Python validates)
       └── P1 deterministic validation (Python — validate_review.py)
```

#### Agent Definitions

| Agent | Tools | Role | Model |
|-------|-------|------|-------|
| `@reviewer` | Read, Glob, Grep (read-only) | Critical analysis of code/artifacts — defects, logical gaps, completeness review | opus |
| `@fact-checker` | Read, Glob, Grep, WebSearch, WebFetch | Fact verification — claim-by-claim confirmation against independent sources | opus |

- **Tool separation rationale (P2)**: `@reviewer` only needs to read to review the internal logic of code/documents. `@fact-checker` needs web access for external fact verification. Principle of least privilege.
- **Sub-agent selection rationale**: Single reviewer = Sub-agent (synchronous feedback loop). Since review results must be reflected immediately, more efficient than Agent Team asynchronous pattern.

#### Execution Protocol

1. Generator produces artifact → passes L0/L1/L1.5
2. Orchestrator calls the agent specified in the `Review:` field as a Sub-agent
3. Review agent generates review report (returned via stdout)
4. Orchestrator saves report to `review-logs/step-N-review.md`
5. P1 validation: `python3 .claude/hooks/scripts/validate_review.py --step N --project-dir .`
6. Proceed based on verdict:

```
PASS → Translation (if applicable) → SOT update → next step
FAIL → Rework (max 10 times) → Re-review
       ↓ exceed 10 times
       User escalation
```

#### Review Field Syntax

Specified as `Review:` attribute on each step in the workflow:

```markdown
### Step 3: Analysis Report (agent)
- Agent: @analyst
- Review: @reviewer          ← code/artifact review
- Translation: @translator
- Verification:
  - [ ] ...
```

| Review Value | Behavior |
|-------------|----------|
| `@reviewer` | Critical analysis of code/artifact |
| `@fact-checker` | Fact verification (against external sources) |
| `@reviewer + @fact-checker` | Both run (for high-risk steps) |
| `none` or not specified | Skip review (L1.5 only) |

#### Rubber-stamp Prevention (4-layer defense)

| Defense Layer | Mechanism |
|--------------|-----------|
| 1. Adversarial Persona | "critic, not validator" identity embedded in agent definition |
| 2. Pre-mortem | Must write 3 failure hypotheses before analysis — prevents confirmation bias |
| 3. Minimum 1 Issue | P1 validation automatically rejects reviews with 0 issues (R5 check) |
| 4. Independent pACS | Reviewer independently scores → compared with Generator (Delta ≥ 15 → mediation) |

#### P1 Hallucination Prevention

5 tasks in the review system that must be 100% accurate are enforced by Python code:

| Validation | Function | Location |
|-----------|----------|----------|
| R1: Review file exists | `validate_review_output()` | `_context_lib.py` |
| R2: Minimum size (100 bytes) | `validate_review_output()` | `_context_lib.py` |
| R3: 4 required sections exist | `validate_review_output()` | `_context_lib.py` |
| R4: PASS/FAIL explicitly extracted | `parse_review_verdict()` | `_context_lib.py` |
| R5: Issues table ≥ 1 row | `validate_review_output()` | `_context_lib.py` |
| pACS Delta calculation | `calculate_pacs_delta()` | `_context_lib.py` |
| Review→Translation sequence | `validate_review_sequence()` | `_context_lib.py` |

Standalone script: `python3 .claude/hooks/scripts/validate_review.py --step N --project-dir .`
Output: JSON `{"valid": true, "verdict": "PASS", "critical_count": 0, ...}`

#### Translation P1 Hallucination Prevention

9 tasks in translation artifacts that must be 100% accurate are enforced by Python code:

| Validation | Function | Location |
|-----------|----------|----------|
| T1: Translation file exists | `validate_translation_output()` | `_context_lib.py` |
| T2: Minimum size (100 bytes) | `validate_translation_output()` | `_context_lib.py` |
| T3: English original exists | `validate_translation_output()` | `_context_lib.py` |
| T4: .ko.md extension | `validate_translation_output()` | `_context_lib.py` |
| T5: Non-whitespace content | `validate_translation_output()` | `_context_lib.py` |
| T6: Heading count ±20% | `validate_translation_output()` | `_context_lib.py` |
| T7: Code block count match | `validate_translation_output()` | `_context_lib.py` |
| T8: glossary timestamp freshness | `check_glossary_freshness()` | `_context_lib.py` |
| T9: pACS min() arithmetic accuracy (generic) | `verify_pacs_arithmetic()` | `_context_lib.py` |

Standalone script: `python3 .claude/hooks/scripts/validate_translation.py --step N --project-dir . --check-pacs --check-sequence`
Output: JSON `{"valid": true, "checks": {"T1": true, ...}, "pacs_valid": true}`

#### Verification Log P1 Hallucination Prevention

Structural integrity of verification logs enforced by Python code across 3 items:

| Validation | Function | Location |
|-----------|----------|----------|
| V1a: Verification log file exists | `validate_verification_log()` | `_context_lib.py` |
| V1b: Per-criterion PASS/FAIL explicitly stated | `validate_verification_log()` | `_context_lib.py` |
| V1c: Logical consistency (cannot be overall PASS if any FAIL exists) | `validate_verification_log()` | `_context_lib.py` |

Standalone script: `python3 .claude/hooks/scripts/validate_verification.py --step N --project-dir .`
Output: JSON `{"valid": true, "checks": {"V1a": true, "V1b": true, "V1c": true}}`

#### Issue Severity Classification

| Severity | Definition | Verdict Impact |
|----------|------------|---------------|
| **Critical** | Factual errors, missing required content, logical flaws, security vulnerabilities | → FAIL |
| **Warning** | Incomplete coverage, weak arguments, style inconsistency, minor inaccuracies | → PASS (recorded) |
| **Suggestion** | Improvement opportunities, alternative approaches, readability enhancements | → PASS (optional) |

#### Review Report Format

Recorded in `review-logs/step-N-review.md`:

```markdown
# Adversarial Review — Step {N}: {Step Name}
Reviewer: @{reviewer|fact-checker}

## Pre-mortem (MANDATORY — before analysis)
1. **Most likely critical flaw**: [...]
2. **Most likely factual error**: [...]
3. **Most likely logical weakness**: [...]

## Issues Found
| # | Severity | Location | Problem | Suggested Fix |
|---|----------|----------|---------|---------------|
| 1 | Critical | file:line | [...] | [...] |

## Independent pACS (Reviewer's Assessment)
| Dimension | Score | Rationale |
|-----------|-------|-----------|
| F | {0-100} | [...] |
| C | {0-100} | [...] |
| L | {0-100} | [...] |

Reviewer pACS = min(F,C,L) = {score}
Generator pACS = {score}
Delta = |Reviewer - Generator| = {N}

## Verdict: {PASS|FAIL}
```

#### Adversarial Review in Autopilot

- Review PASS → auto-proceed (including Translation)
- Review FAIL → auto-rework (max 10 times, escalate to user if exceeded)
- pACS Delta ≥ 15 → record in Decision Log + recommend recalibration
- Review Decision Log: include review results in `autopilot-logs/step-N-decision.md`

#### Execution Sequence Constraint

```
Task → L0 → L1 → L1.5 → Review(L2) → PASS → Translation → SOT update
```

- Translation executes only after Review PASS (P1 `validate_review_sequence()` enforced)
- Translation execution prohibited in Review FAIL state
- Steps with unspecified Review (`none`) can go directly to Translation after L1.5

#### Backward Compatibility

| Situation | Behavior |
|-----------|----------|
| `Review:` not specified in workflow | Proceed with existing L0+L1+L1.5 only |
| `review-logs/` does not exist | Normal operation — P1 functions fail gracefully |
| `@reviewer`/`@fact-checker` agents not defined | Escalate to user on Sub-agent call failure |

> **Design decision**: Position Adversarial Review as an Enhanced version of the existing L2 Calibration. Strengthen the "cross-validation" of L2 Calibration to "adversarial review," while leaving the existing L0/L1/L1.5 layers completely unchanged. Steps without a `Review:` field behave identically to before.

---

### 5.6 Abductive Diagnosis Protocol

When a quality gate (Verification Gate, pACS, Adversarial Review) fails, instead of immediately retrying, go through a **3-step diagnosis** to improve retry quality. The existing 4-layer QA (L0→L1→L1.5→L2) is not changed — it is an additional layer inserted **between** FAIL and retry.

#### 3-Step Process

| Step | Performer | Input | Output | Nature |
|------|-----------|-------|--------|--------|
| **Step A — P1 pre-evidence collection** | `diagnose_context.py` | SOT, log files, retry history | Structured evidence bundle (JSON) | Deterministic |
| **Step B — LLM diagnosis** | Orchestrator (Claude) | Evidence bundle + hypothesis priority | Diagnosis log (`diagnosis-logs/step-N-gate-timestamp.md`) | Judgmental |
| **Step C — P1 post-validation** | `validate_diagnosis.py` | Diagnosis log | AD1-AD10 structural integrity (JSON) | Deterministic |

#### Hypothesis Framework (H1/H2/H3/H4)

| Hypothesis | Label | Priority Determination Criteria |
|-----------|-------|-------------------------------|
| **H1** | Upstream data quality issue | Highest priority when previous step artifact is missing or inadequate |
| **H2** | Current step execution gap | Default highest priority (most frequent) |
| **H3** | Criteria interpretation error | Priority elevated at Review gate |
| **H4** | Capability gap — missing tool/script/infrastructure | Automatically escalated when H2 fails to resolve after 2 repetitions |

#### Fast-Path (FP1-FP3)

Deterministic shortcuts that skip LLM diagnosis:

| ID | Condition | Diagnosis | Action |
|----|-----------|-----------|--------|
| **FP1** | Artifact file absent | "File not generated" | Immediate re-execution |
| **FP2** | Artifact size < 100B | "Incomplete generation" | Immediate re-execution |
| **FP3** | Same hypothesis selected 2 consecutive times | "Approach fixation" | User escalation |

#### P1 Post-Validation (AD1-AD10)

| Validation | Description |
|-----------|-------------|
| AD1 | Diagnosis log file exists |
| AD2 | Minimum size ≥ 100 bytes |
| AD3 | Gate field matches |
| AD4 | Selected hypothesis exists (H1/H2/H3/H4) |
| AD5 | Evidence items ≥ 1 |
| AD6 | Action Plan section exists |
| AD7 | No forward step references |
| AD8 | Hypotheses ≥ 2 (alternative consideration) |
| AD9 | Selected hypothesis is one of the listed hypotheses |
| AD10 | References previous diagnosis (when retry > 0) |

#### Backward Compatibility

| Situation | Behavior |
|-----------|----------|
| `diagnosis-logs/` does not exist | Existing behavior unchanged — retry without diagnosis |
| Retry executed without diagnosis | Normal operation — safety net outputs stderr warning only |
| Fast-Path applicable | LLM diagnosis skipped — immediate judgment with P1 pre-evidence only |

> **Design decision**: Abductive Diagnosis is an additional layer that does not change the existing 4-layer QA. Diagnosis results are recorded only in `diagnosis-logs/` and SOT is not modified. Archived as `diagnosis_patterns` in Knowledge Archive, enabling cross-session learning.

---

## 6. Skill System

### workflow-generator

A skill for designing and generating workflow definition files (`workflow.md`).

- **Trigger**: "Make me a workflow," "design an automation pipeline," "define a task flow"
- **Entry point**: `.claude/skills/workflow-generator/SKILL.md`
- **Two cases**: (1) Only an idea exists → conversational questions, (2) Explanatory document exists → document analysis first

### doctoral-writing

A writing skill with the academic rigor and clarity of doctoral-level dissertations.

- **Trigger**: "Write in paper style," "academic writing," "refine sentences for a paper"
- **Entry point**: `.claude/skills/doctoral-writing/SKILL.md`
- **Core principles**: Clarity, conciseness, academic rigor, logical flow

---

## 7. Skill Development Rules

When creating a new skill or modifying an existing one:

1. **All Absolute Standards must be included** — applied contextualized to the relevant domain (Absolute Standard 3 may be N/A for non-code-change domains)
2. **Clear role division between files** — skill definition (WHY), reference materials (WHAT/HOW/VERIFY)
3. **Explicitly specify conflict scenarios between Absolute Standards** — practical judgment criteria, not abstract rules
4. **Reflect after modification** — do not just add wording; check for conflicts with existing content

---

## 8. Language and Style

- **Framework documents and user conversations**: Korean
- **Workflow execution**: English (maximize AI performance — Absolute Standard 1 basis). Details: §5.2
- **Final artifacts**: English original + Korean translation pair
- **Technical terms**: Preserved in English (SOT, Agent, Orchestrator, Hooks, etc.)
- **Visualization**: Mermaid diagrams preferred
- **Narrative depth**: Prefer comprehensive, data-driven description over brief summaries
- **Code comments**: Korean (framework code) / English (workflow execution code)

---

## 9. Universal System Prompt Architecture (Hub-and-Spoke)

This project is designed so that the same methodology is automatically applied regardless of which AI CLI tool is used.

### Architecture

```
                AGENTS.md (Hub — methodology SOT)
               /    |    |    \    \     \
          CLAUDE  GEMINI .cursor  .github/
          .md     .md    /rules   copilot-
                         (Spoke)  instructions.md
```

- **Hub (AGENTS.md)**: The sole definition point for Absolute Standards, design principles, and workflow structure
- **Spoke (per-tool files)**: Provide implementation mapping suited to each tool's unique features while referencing the Hub

### Per-Tool File Mapping

| AI CLI Tool | System Prompt File | Auto-read | AGENTS.md Recognition |
|------------|-------------------|-----------|----------------------|
| **Claude Code** | `CLAUDE.md` | Yes | Separate file |
| **Gemini CLI** | `GEMINI.md` | Yes | Added via configuration |
| **Codex CLI** | `AGENTS.md` (directly) | Yes | Native |
| **Copilot CLI** | `.github/copilot-instructions.md` | Yes | Auto-recognized |
| **Cursor** | `.cursor/rules/agenticworkflow.mdc` | Yes (alwaysApply) | Recognized |

### Spoke File Principles

1. **Absolute Standards inline + detailed reference**: Each Spoke includes the core definition (1-2 sentences) of the Absolute Standards inline, and delegates detailed content to `AGENTS.md §2` by reference.
2. **Per-tool implementation mapping**: Explicitly specify the correspondence between each tool's unique features (Hook, Agent, Plugin, etc.) and AgenticWorkflow concepts.
3. **Context preservation alternative**: For tools that cannot use Claude Code's Context Preservation System, provide guidance on alternatives available in that tool.

### Conflict Resolution

> **AGENTS.md's Absolute Standards take precedence over all Spokes.** If a tool-specific implementation conflicts with a principle, the principle wins.

---

## 10. InvestScan Report Output

InvestScan pipeline produces reports in three formats saved to a dedicated user folder.

| Item | Value |
|------|-------|
| **Formats** | TXT (plain text) + PDF (fpdf2) + MD (source copy) |
| **Output path** | `~/Desktop/Ai_works/output/투자분석제안/` |
| **Filename pattern** | `{YYYY-MM-DD}_주간투자분석.{txt,pdf,md}` |
| **Export command** | `python3 -m investscan.export_report` |
| **ADR** | ADR-056 in `DECISION-LOG.md` |

**Path separation**: Pipeline intermediate artifacts (`output/reports/*.md`) are separate from user-facing final outputs (`투자분석제안/`). Agents must not conflate these two paths.

### Synchronization on Absolute Standard Changes

When Absolute Standards in AGENTS.md change, the inline copies in all Spoke files must also be synchronized:
- `CLAUDE.md`, `GEMINI.md` — edit directly
- `.cursor/rules/` — edit inline portions
- `.github/copilot-instructions.md` — edit inline portions
