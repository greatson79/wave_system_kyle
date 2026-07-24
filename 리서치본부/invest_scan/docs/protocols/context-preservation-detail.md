# Context Preservation System — Detailed Specification

> This document is the detailed specification of the internal mechanisms of the Context Preservation System.
> Separated from CLAUDE.md — reference when modifying, debugging, or extending Hook scripts.

## How Claude Uses This System

- When `[CONTEXT RECOVERY]` is displayed at session start, **read the file at the indicated path using the Read tool** to restore prior context.
- Snapshots are stored at `.claude/context-snapshots/latest.md`.
- **Knowledge Archive**: `knowledge-index.jsonl` is a structured index that accumulates across sessions. Recorded at both Stop hook and SessionEnd/PreCompact. Each entry includes: completion_summary (tool success/failure), git_summary (change status), session_duration_entries (session length), phase (overall session phase), phase_flow (multi-phase transition flow, e.g., `research → implementation`), primary_language (dominant file extension), error_patterns (Error Taxonomy 12-pattern classification + resolution matching), success_patterns (Edit/Write→Bash success sequences), tool_sequence (RLE-compressed tool sequence), final_status (success/incomplete/error/unknown), tags (path-based search tags). Programmatic exploration is possible via Grep tool (RLM pattern).
- **Resume Protocol**: The "restore instructions" section in snapshots deterministically provides the list of modified/referenced files and session info. The `[CONTEXT RECOVERY]` output also shows completion status (tool success/failure) and git change status. **Dynamic RLM query hints**: automatically generates session-specific Grep query examples based on tags extracted from modified file paths (`extract_path_tags()`) and error information.
- Hook scripts access SOT (`state.yaml`) **read-only** (Absolute Standard 2 compliance). SOT file paths are centrally managed via the `sot_paths()` helper, derived from the `SOT_FILENAMES` constant (`state.yaml`, `state.yml`, `state.json`).

## Truncation Constants Centralization

10 truncation constants are centrally defined in `_context_lib.py`:
- `EDIT_PREVIEW_CHARS=1000` — Edit preview preserves edit intent/context at 5 lines × 1000 chars
- `ERROR_RESULT_CHARS=3000` — Error messages preserved at 3000 chars to retain full stack trace
- `MIN_OUTPUT_SIZE=100` — Minimum artifact size

## Multi-Phase Transition Detection

The `detect_phase_transitions()` function uses a sliding window (20 tools, 50% overlap) to deterministically detect phase transitions within a session (research → planning → implementation, etc.). Recorded in the Knowledge Archive's `phase_flow` field.

## Decision Quality Tag Sorting

The "key design decisions" section (IMMORTAL priority) in snapshots is sorted by quality tags — `[explicit]` > `[decision]` > `[rationale]` > `[intent]` order fills 15 slots, preventing everyday intent declarations (`I will do...` patterns) from displacing actual design decisions.

## IMMORTAL-aware Compression

When snapshot size exceeds limits, Phase 7 hard truncate preserves IMMORTAL sections first. Non-IMMORTAL content is truncated first; even in extreme cases, the beginning of IMMORTAL text is preserved.

**Compression audit trail**: Each compression Phase records the number of characters removed as an HTML comment (`<!-- compression-audit: ... -->`) at the end of the snapshot (per-phase delta Phase 1~7 + final size).

## Error Taxonomy

Tool errors classified into 12 patterns:
`file_not_found`, `permission`, `syntax`, `timeout`, `dependency`, `edit_mismatch`, `type_error`, `value_error`, `connection`, `memory`, `git_error`, `command_not_found`

Recorded in the Knowledge Archive's error_patterns field, reducing "unknown" classification to ~30%. Negative lookahead and qualifier matching applied to prevent false positives.

**Error→Resolution Matching**: Successful tool calls within 5 entries after an error are detected via file-aware matching and recorded in the `resolution` field. Cross-session exploration: `Grep "resolution" knowledge-index.jsonl`.

## Quality Gate State IMMORTAL Preservation

The `_extract_quality_gate_state()` function extracts the latest quality gate results from `pacs-logs/`, `review-logs/`, `verification-logs/` and preserves them as IMMORTAL sections in the snapshot.

## Phase Transition Snapshot Header

In sessions where multi-phase transitions are detected, the snapshot header displays the transition flow in the format `Phase flow: research(12) → implementation(25)`.

## Error→Resolution Auto-Surfacing

The `_extract_recent_error_resolutions()` function in `restore_context.py` reads error_patterns from recent sessions in the Knowledge Archive and displays up to 3 error→resolution patterns directly in SessionStart output.

## Runtime Directory Auto-Creation

The `_check_runtime_dirs()` function in `setup_init.py` automatically creates 6 directories — `verification-logs/`, `pacs-logs/`, `review-logs/`, `autopilot-logs/`, `translations/`, `diagnosis-logs/` — when the SOT file is present.

## System Command Filtering

The "current work" section in snapshots automatically filters out system commands such as `/clear`, `/help`, capturing only actual user work intent.

## Autopilot Runtime Reinforcement

When Autopilot is active: SessionStart injects execution rules into context, the snapshot includes an Autopilot state section (IMMORTAL priority), and the Stop hook detects and supplements missing Decision Logs.

## ULW Mode Detection and Preservation

The `detect_ulw_mode()` function detects the `ulw` keyword in transcripts via word-boundary regex. **Implicit deactivation**: In new sessions (`source=startup`), ULW rules are not injected even if prior snapshots contain ULW state — only `clear`/`compact`/`resume` sources carry ULW forward.

## Predictive Debugging

`aggregate_risk_scores()` aggregates error_patterns from the Knowledge Archive per file to derive risk scores (weight × decay). Runs once at SessionStart to generate the `risk-scores.json` cache; `predictive_debug_guard.py` reads the cache at each Edit/Write and outputs warnings when the threshold is exceeded.

**Startup trade-off**: The SessionStart matcher is `clear|compact|resume`, so the cache is not generated on the initial startup (ADR-036).

**Basename merge**: When bare names and relative paths coexist, entries with the same basename are automatically merged to prevent risk score underestimation.

---

## Hook Configuration Location

All Hooks are integrated in **Project** (`.claude/settings.json`). Hook infrastructure is automatically applied with `git clone` only.

- Stop → `context_guard.py --mode=stop` → `generate_context_summary.py`
- PostToolUse → `context_guard.py --mode=post-tool` → `update_work_log.py` (matcher: `Edit|Write|Bash|Task|NotebookEdit|TeamCreate|SendMessage|TaskCreate|TaskUpdate`)
- PreCompact → `context_guard.py --mode=pre-compact` → `save_context.py --trigger precompact`
- SessionStart → `context_guard.py --mode=restore` → `restore_context.py` (matcher: `clear|compact|resume`)
- **PreToolUse** → `block_destructive_commands.py` (matcher: `Bash`, standalone — preserves exit code 2)
- **PreToolUse** → `block_test_file_edit.py` (matcher: `Edit|Write`, standalone — `.tdd-guard` toggle)
- **PreToolUse** → `predictive_debug_guard.py` (matcher: `Edit|Write`, standalone — warning only)
- **PostToolUse** → `output_secret_filter.py` (matcher: `Bash|Read`, standalone — secret detection, exit 0 warning)
- **PostToolUse** → `security_sensitive_file_guard.py` (matcher: `Edit|Write`, standalone — sensitive file warning, exit 0)
- SessionEnd → `save_context.py --trigger sessionend` (matcher: `clear`)
- Setup (init) → `setup_init.py` — infrastructure health validation (`claude --init`)
- Setup (maintenance) → `setup_maintenance.py` — periodic health check (`claude --maintenance`)

### Hook Design Decisions

> **`if test -f; then; fi` pattern unification**: All Hook commands use the `if test -f; then; fi` pattern. Eliminates the previous `|| true` pattern (a latent bug that swallowed exit code 2 blocking signals).
> **Rationale for standalone PreToolUse Safety Hooks**: `block_destructive_commands.py` and `block_test_file_edit.py` are in a different domain from context preservation. Since exit code 2 preservation is critical, they run directly without going through `context_guard.py`.
> **Rationale for standalone PostToolUse Security Hooks (ADR-050)**: `output_secret_filter.py` and `security_sensitive_file_guard.py` are in the security domain, independent from context preservation (`update_work_log.py`). They use their own data sources (direct transcript JSONL reading, session deduplication), so they run directly without going through the `context_guard.py` dispatcher.

### D-7 Intentional Duplicate Instances

| # | Instance | Location A | Location B |
|---|---------|--------|--------|
| 1 | `REQUIRED_SCRIPTS` (20 items) | `setup_init.py` | `setup_maintenance.py` |
| 2 | `RISK_THRESHOLD`/`MIN_SESSIONS` | `predictive_debug_guard.py` | `_context_lib.py` |
| 3 | `ERROR_TAXONOMY` type names (12 items) | `_classify_error_patterns()` | `_RISK_WEIGHTS` (13 items) |
| 4 | ULW detection pattern | `_gather_retry_history()` | `validate_retry_budget.py` + `restore_context.py` |
| 5 | Retry limit constants | `validate_retry_budget.py` | `_context_lib.py` + `restore_context.py` |
| 6 | `SOT_FILENAMES` tuple | `_context_lib.py` `SOT_FILENAMES` | `setup_init.py` + `query_workflow.py` `_SOT_FILENAMES` |

Each D-7 instance has a cross-reference comment in the code; when one side changes, the corresponding side must also be synchronized.

**Automatic verification**: `_check_doc_code_sync()` in `setup_maintenance.py` deterministically verifies DC-1~DC-5:
- DC-1: Retry limit documentation ↔ code
- DC-2: Risk constant synchronization
- DC-3: ULW detection pattern synchronization
- DC-4: Retry limit constant synchronization
- DC-5: SOT_FILENAMES 3-party synchronization (`_context_lib.py` ↔ `setup_init.py` ↔ `query_workflow.py`)
