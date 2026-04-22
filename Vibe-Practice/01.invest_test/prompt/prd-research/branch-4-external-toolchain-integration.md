# Branch 4: External Tool Chain Integration Analysis

> **Analysts**: Two External Tool Chain Integration Experts (Full Toolchain Architect + Minimal Pragmatist)
> **Date**: 2026-03-28
> **Context**: InvestScan -- LOCAL AI investment system on MacBook M5 Max 64GB, orchestrated by Claude Code, solo pastor-developer 2-4 hrs/week
> **Input**: 10 completed Phase 1 research branches, Round 3/4 technology and implementation decisions
> **Scope**: Everything OUTSIDE the investscan/ Python package -- tooling, scheduling, backup, version control, Claude Code ecosystem

---

## BRANCH 4.1: FULL Toolchain (Comprehensive)

**Philosophy**: "InvestScan is a long-lived financial intelligence system. Investment decisions ride on its output. Every tool choice should maximize reliability, observability, and recoverability. Build the infrastructure once; never worry about it again."

---

### A. Claude Code Ecosystem Integration

InvestScan lives within the AgenticWorkflow framework. The parent system already provides context preservation, destructive command blocking, secret filtering, and quality gates. InvestScan inherits this entire genome. The question is: what InvestScan-specific extensions does the Claude Code ecosystem need?

#### A.1 Custom Agents (`.claude/agents/`)

Three InvestScan-specific agents, alongside the inherited `translator.md`, `reviewer.md`, and `fact-checker.md`:

**Agent 1: `investscan-orchestrator.md`**

```markdown
# InvestScan Pipeline Orchestrator

You are the orchestrator for InvestScan's weekly investment intelligence pipeline.

## Role
- Execute the 5-step pipeline: Health Check -> Data Collection -> Normalization -> Synthesis -> Report
- Manage checkpoint/resume state via `.claude/state.yaml`
- Only YOU write to SOT files (Absolute Standard 2)

## Pipeline Steps
1. Health check: Verify EnvScan/GlobalNews directories, Python envs, disk space
2. Data collection: Read latest signals from both source systems
3. Normalization: Invoke `python3 -m investscan normalize --date {date}`
4. Synthesis: Invoke `python3 -m investscan synthesize --date {date}`
5. Report: Invoke `python3 -m investscan report --date {date}`

## Error Handling
- On step failure: Log error to `output/{date}/pipeline-error.log`, record failed step in state
- On checkpoint resume: Skip completed steps, restart from last failed step
- NEVER retry a failed step more than twice (Bounded Retry)

## Financial Safety
- NEVER modify source system data (EnvScan/GlobalNews outputs are read-only)
- ALWAYS validate signal counts before/after normalization (drop > 20% = abort)
- Report generation MUST include disclaimer: "AI-generated analysis, not financial advice"
```

**Agent 2: `signal-analyst.md`**

```markdown
# Signal Analyst

You analyze normalized signals to produce investment direction assessments.

## Role
- Read UnifiedSignal data from the normalization stage
- Apply STEEPs-to-GICS sector mapping
- Score directional conviction per sector
- Detect cross-source signal convergence

## Constraints
- You read data; you NEVER write to upstream stages
- All direction calls must include evidence chains (minimum 2 sources)
- Conviction scores are 0.0-1.0; NEVER output unbounded scores
- Mark single-source signals with lower confidence ceiling (max 0.6)
```

**Agent 3: `report-reviewer.md`**

```markdown
# Report Reviewer (InvestScan)

You are an adversarial reviewer for weekly investment reports.

## Review Checklist
1. Does every directional call (bullish/bearish/neutral) cite at least 2 evidence sources?
2. Are conviction scores proportional to evidence strength?
3. Does the report contain the mandatory disclaimer?
4. Are there any sectors with contradictory signals that were not flagged as "mixed"?
5. Is the Korean translation accurate (spot-check 3 random sentences)?

## Output
- PASS/FAIL with specific line references
- If FAIL: regenerate report with corrections
```

#### A.2 Slash Commands (`.claude/commands/`)

**Command 1: `investscan-run.md`**

```markdown
# /investscan-run

Execute the InvestScan weekly pipeline.

## Usage
/investscan-run              # Run for current week
/investscan-run 2026-03-27   # Run for specific date

## Behavior
1. Read `config/investscan.yaml` for paths and settings
2. Invoke @investscan-orchestrator with pipeline context
3. Auto-approve human checkpoints (Autopilot mode)
4. Write final status to `output/{date}/pipeline-status.json`

## Prerequisites
- EnvironmentScan must have run within the last 7 days
- GlobalNews-Crawling must have run within the last 7 days
- If neither has fresh data: prompt user to run source systems first
```

**Command 2: `investscan-status.md`**

```markdown
# /investscan-status

Show the current state of the InvestScan pipeline.

## Behavior
1. Read `output/` directory for latest run date
2. Read `output/{latest}/pipeline-status.json`
3. Display: last run date, step completion, signal counts, report path
4. If last run > 7 days ago: warn "Stale data"
```

**Command 3: `investscan-journal.md`**

```markdown
# /investscan-journal

Manage the investment decision journal.

## Usage
/investscan-journal add       # Add a new decision entry (interactive)
/investscan-journal review    # Review past decisions with signal retrospective
/investscan-journal export    # Export journal to Markdown

## Journal Entry Fields
- date, sector, direction, conviction, rationale
- linked_signals: which report signals informed this decision
- outcome (filled retroactively): actual market movement
```

#### A.3 Hooks (`.claude/hooks/`)

InvestScan inherits ALL parent hooks (see CLAUDE.md Hook table). Two InvestScan-specific additions:

**Hook 1: `validate_investscan_output.py` (PostToolUse on Write)**

Purpose: When the pipeline writes a report file, validate that mandatory sections exist (Executive Summary, Sector Direction, Evidence Chains, Disclaimer). Exit 2 (block) if the disclaimer is missing.

```python
#!/usr/bin/env python3
"""
PostToolUse hook: Validates InvestScan report output.
Blocks report writes that are missing mandatory sections.
"""
import sys
import os
import json

def validate_report():
    """Check that a written report file contains mandatory sections."""
    tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
    file_path = tool_input.get("file_path", "")

    if "output/" not in file_path or not file_path.endswith(".md"):
        return 0  # Not an InvestScan report

    content = tool_input.get("content", "")

    mandatory_sections = [
        "핵심 요약",           # Executive Summary
        "섹터별 투자 방향",     # Sector Direction
        "증거 체인",           # Evidence Chains
        "주의 사항",           # Disclaimer
    ]

    missing = [s for s in mandatory_sections if s not in content]

    if missing:
        print(f"[INVESTSCAN GUARD] Report missing mandatory sections: {missing}")
        print("Blocked: All reports MUST include disclaimer and evidence chains.")
        return 2  # Block

    return 0

if __name__ == "__main__":
    sys.exit(validate_report())
```

**Hook 2: `validate_signal_count.py` (PostToolUse on Bash)**

Purpose: After normalization runs, check that signal count did not drop more than 20% from source data. A large drop indicates a parser bug that could produce misleading reports.

```python
#!/usr/bin/env python3
"""
PostToolUse hook: Validates signal count after normalization.
Warns (exit 0 with message) if signal loss exceeds 20%.
"""
import sys
import os
import json

def check_signal_count():
    tool_input = json.loads(os.environ.get("TOOL_INPUT", "{}"))
    command = tool_input.get("command", "")

    if "investscan normalize" not in command:
        return 0

    output = os.environ.get("TOOL_OUTPUT", "")

    # Parse signal counts from normalization output
    # Expected format: "Normalized: 187/234 signals (79.9%)"
    if "Normalized:" in output:
        try:
            parts = output.split("Normalized:")[1].split("signals")[0]
            normalized, total = parts.strip().split("/")
            ratio = int(normalized) / int(total)
            if ratio < 0.80:
                print(f"[INVESTSCAN WARNING] Signal loss {(1-ratio)*100:.1f}% exceeds 20% threshold.")
                print(f"  Normalized {normalized}/{total} signals. Check parser for regressions.")
        except (ValueError, IndexError, ZeroDivisionError):
            pass

    return 0  # Warning only, do not block

if __name__ == "__main__":
    sys.exit(check_signal_count())
```

#### A.4 Skills (`.claude/skills/`)

**Skill: `investscan-pipeline/SKILL.md`**

This skill encapsulates the entire InvestScan pipeline execution knowledge. It would be referenced by the workflow.md and invocable by the orchestrator agent.

```
.claude/skills/investscan-pipeline/
  SKILL.md                         # WHY: Pipeline execution philosophy + entry points
  references/
    pipeline-steps.md              # WHAT: Each step's input/output/validation
    schema-reference.md            # WHAT: UnifiedSignal schema + parser contracts
    sector-mapping-rules.md        # HOW: STEEPs-to-GICS mapping rules
    report-template-guide.md       # HOW: Jinja2 template variables and sections
    troubleshooting.md             # VERIFY: Common failure modes and recovery
```

#### A.5 MCP Servers

InvestScan can leverage MCP servers for specific tasks. The project already has `context7` and `playwright` available (confirmed from settings).

**context7 (Documentation Lookup)**

Use case: When implementing InvestScan modules, look up current API documentation for:
- `sentence-transformers` (BGE-M3 embedding model)
- `BERTopic` (topic modeling configuration)
- `pykrx` (Korean market data, Phase 2)
- `DuckDB` Python API (analytical queries, Month 3+)
- `Jinja2` template syntax
- `Click` CLI framework

Invocation pattern:
```
# Resolve library, then query specific API
mcp__context7__resolve-library-id("sentence-transformers")
mcp__context7__query-docs(libraryId, "BGE-M3 encode method")
```

**playwright (Web Data Verification)**

Use case: Spot-check that source system URLs in reports are still live. After report generation, verify that the top 3 evidence chain URLs return HTTP 200. This prevents citing dead links in investment reports.

Invocation pattern:
```
# Navigate to cited URL, check for content
mcp__playwright__browser_navigate(url)
mcp__playwright__browser_screenshot()  # Visual verification
```

Frequency: Optional post-report validation. Not every run -- only when reviewing report quality.

**Custom Financial Data MCP (Future, Phase 2+)**

A custom MCP server for Korean market data could wrap `pykrx` to provide:
- Current KOSPI/KOSDAQ index values
- Sector ETF prices (KODEX series)
- Market capitalization by sector

This is Phase 2 work. For Phase 1, `pykrx` is called directly from Python code.

Feasibility: MCP server is a simple FastAPI/stdio wrapper around `pykrx` calls. Estimated ~150 LOC. Value: enables Claude Code to query market data conversationally during analysis sessions, not just in batch pipeline runs.

#### A.6 Structuring InvestScan within AgenticWorkflow

The directory layout that integrates InvestScan as a first-class project within the AgenticWorkflow ecosystem:

```
01.invest_test/                          # AgenticWorkflow project root
├── CLAUDE.md                            # Inherited (parent genome)
├── AGENTS.md                            # Inherited
├── .claude/
│   ├── settings.json                    # Inherited hooks + InvestScan additions
│   ├── agents/
│   │   ├── translator.md               # Inherited
│   │   ├── reviewer.md                 # Inherited
│   │   ├── fact-checker.md             # Inherited
│   │   ├── investscan-orchestrator.md  # NEW
│   │   ├── signal-analyst.md           # NEW
│   │   └── report-reviewer.md          # NEW
│   ├── commands/
│   │   ├── install.md                  # Inherited
│   │   ├── maintenance.md              # Inherited
│   │   ├── investscan-run.md           # NEW
│   │   ├── investscan-status.md        # NEW
│   │   └── investscan-journal.md       # NEW
│   ├── hooks/scripts/
│   │   ├── (all inherited hooks)
│   │   ├── validate_investscan_output.py  # NEW
│   │   └── validate_signal_count.py       # NEW
│   └── skills/
│       ├── workflow-generator/          # Inherited
│       ├── doctoral-writing/            # Inherited
│       └── investscan-pipeline/         # NEW
│           ├── SKILL.md
│           └── references/
├── investscan/                          # NEW: Python package
│   ├── __init__.py
│   ├── __main__.py                      # Click CLI entry point
│   ├── schema.py                        # UnifiedSignal frozen dataclass
│   ├── normalize_signals.py             # 6 parsers
│   ├── synthesize_investment.py         # Sector mapping + direction scoring
│   ├── generate_report.py              # Jinja2 report generation
│   ├── decision_journal.py             # SQLite journal (Phase 1 P1)
│   └── config.py                        # YAML config loader
├── config/
│   └── investscan.yaml                  # Pipeline configuration
├── templates/
│   ├── weekly-report.md.j2             # Korean weekly report
│   └── weekly-report.html.j2           # HTML interactive (Phase 1 P1)
├── tests/
│   ├── test_normalize.py               # 10 contract tests
│   └── test_sector_mapping.py          # 15 sector mapping tests
├── output/                              # Per-run output (gitignored)
│   └── {YYYY-MM-DD}/
├── logs/                                # Pipeline logs (gitignored)
├── workflow.md                          # Pipeline workflow definition
├── research/                            # Research archive
└── prompt/                              # Prompt archive
```

---

### B. Python Ecosystem

#### B.1 Virtual Environment Management

**Recommendation: `venv` (standard library), NOT conda**

Rationale:
- InvestScan is a pure Python project. No Fortran/C compiled packages that conda uniquely handles.
- Both source systems (EnvScan and GlobalNews-Crawling) already use `venv`.
- conda adds 3-5 GB base installation and introduces a second dependency resolution path.
- `venv` is part of the Python standard library -- zero additional installation.
- The M5 Max hardware eliminates the only strong conda argument (GPU driver management for CUDA) since Apple Silicon uses MPS/Metal natively.

Setup:
```bash
cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test
python3 -m venv .venv
source .venv/bin/activate
```

Activation in pipeline scripts:
```bash
# In run.sh or launchd environment
INVESTSCAN_PYTHON="/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/.venv/bin/python"
$INVESTSCAN_PYTHON -m investscan run --date "$RUN_DATE"
```

#### B.2 Dependency Pinning

**Recommendation: `pyproject.toml` + `requirements.lock`**

`pyproject.toml` is the modern standard (PEP 621). It defines the project metadata AND dependencies in one file. `requirements.txt` is legacy but still useful as a lock file for reproducible installs.

Workflow:
1. `pyproject.toml` defines abstract dependencies (e.g., `sentence-transformers>=3.0`)
2. `pip freeze > requirements.lock` captures exact versions after verified working install
3. Fresh install: `pip install -r requirements.lock` (reproducible)
4. Upgrade cycle: Edit `pyproject.toml`, `pip install -e .`, test, re-freeze

```toml
# pyproject.toml
[project]
name = "investscan"
version = "0.1.0"
description = "Weekly investment macro intelligence from environmental scanning + global news"
requires-python = ">=3.12"
dependencies = [
    # ── Core Pipeline ──
    "click>=8.1",                    # CLI framework
    "pyyaml>=6.0",                   # Configuration
    "jinja2>=3.1",                   # Report templates

    # ── Data Processing ──
    "pandas>=2.2",                   # DataFrame operations
    "pyarrow>=15.0",                 # Parquet read/write
    "numpy>=1.26",                   # Numerical operations

    # ── NLP / ML ──
    "sentence-transformers>=3.0",    # BGE-M3 embeddings (cross-source dedup)
    "scikit-learn>=1.4",             # TF-IDF, cosine similarity
    "kiwipiepy>=0.17",              # Korean morphological analysis

    # ── Visualization ──
    "matplotlib>=3.8",               # Sector heatmap (static)
    "rich>=13.0",                    # CLI progress bars, tables

    # ── Storage ──
    # SQLite is stdlib -- no pip package needed
    # DuckDB deferred to Month 3+
]

[project.optional-dependencies]
phase2 = [
    "duckdb>=1.0",                   # Analytical queries (Month 3+)
    "pykrx>=1.0",                    # Korean market data (Month 4+)
    "plotly>=5.18",                  # Interactive HTML charts (Month 4+)
]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.3",                     # Linting (replaces flake8+black+isort)
]

[project.scripts]
investscan = "investscan.__main__:cli"

[build-system]
requires = ["setuptools>=69.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### B.3 Complete Dependency List with Versions

**Phase 1 (Month 1-4) -- Core Pipeline:**

| Package | Version | Size (disk) | RAM Impact | Purpose |
|---------|---------|-------------|------------|---------|
| `click` | 8.1.7 | 0.4 MB | Negligible | CLI framework |
| `pyyaml` | 6.0.1 | 0.3 MB | Negligible | Config loading |
| `jinja2` | 3.1.4 | 1.1 MB | Negligible | Report templates |
| `pandas` | 2.2.2 | 65 MB | ~200 MB runtime | Signal DataFrame operations |
| `pyarrow` | 16.1.0 | 120 MB | ~100 MB runtime | Parquet read (GlobalNews) |
| `numpy` | 1.26.4 | 35 MB | ~50 MB runtime | Numerical operations |
| `sentence-transformers` | 3.0.1 | 15 MB | -- | Embedding framework |
| `torch` (dep of above) | 2.3.1 | ~800 MB | ~1.5 GB runtime | ML backend for BGE-M3 |
| `transformers` (dep) | 4.42.0 | 45 MB | -- | Model loading |
| `BAAI/bge-m3` (model) | -- | 2.2 GB (downloaded) | 2.2 GB runtime | Cross-source dedup embeddings |
| `scikit-learn` | 1.5.0 | 35 MB | ~100 MB runtime | TF-IDF + cosine similarity |
| `kiwipiepy` | 0.17.1 | 85 MB (with model) | ~200 MB runtime | Korean morphological analysis |
| `matplotlib` | 3.9.0 | 40 MB | ~100 MB runtime | Sector heatmap |
| `rich` | 13.7.1 | 3 MB | Negligible | CLI formatting |
| `ruff` (dev) | 0.4.4 | 15 MB | -- | Linting |
| `pytest` (dev) | 8.2.0 | 2 MB | -- | Testing |

**Total disk**: ~1.3 GB (dominated by PyTorch)
**Total RAM at peak**: ~4.5 GB (BGE-M3 + pandas + PyTorch)
**RAM headroom on 64 GB**: 59.5 GB free -- ample for concurrent source system runs

**Phase 2 (Month 5-6) -- Optional Additions:**

| Package | Version | Size | Purpose |
|---------|---------|------|---------|
| `duckdb` | 1.0.0 | 45 MB | Analytical queries on accumulated signals |
| `pykrx` | 1.0.49 | 2 MB | Korean market data (KOSPI, KOSDAQ, sector ETFs) |
| `plotly` | 5.22.0 | 20 MB | Interactive HTML charts |
| `kaleido` | 0.2.1 | 90 MB | Plotly static image export |

#### B.4 Dependency Overlap with Source Systems

Critical consideration: InvestScan shares packages with both source systems. Version conflicts are a real risk.

| Package | EnvScan | GlobalNews | InvestScan | Conflict Risk |
|---------|---------|------------|------------|---------------|
| `pandas` | 2.1.x | 2.2.x | 2.2.x | LOW (minor version) |
| `sentence-transformers` | Not used | 3.0.x (MiniLM) | 3.0.x (BGE-M3) | NONE (same package, different model) |
| `kiwipiepy` | 0.17.x | Not used | 0.17.x | NONE |
| `torch` | Not used | 2.3.x | 2.3.x (via s-t) | NONE |
| `pyarrow` | Not used | 15.x | 16.x | LOW (InvestScan reads, GlobalNews writes) |

**Mitigation**: Each system uses its own `.venv`. InvestScan NEVER imports directly from source system Python environments. It reads their FILE outputs (JSON, Parquet) only.

---

### C. Scheduling & Automation

#### C.1 macOS `launchd` plist (Recommended)

`launchd` is macOS's native service manager. It is superior to `cron` on macOS because:
- Apple has formally deprecated cron on macOS (still functional but unsupported)
- `launchd` handles "machine was asleep" natively via `StartCalendarInterval` + catch-up
- Integrates with macOS Unified Logging (`os_log`)
- Manages process lifecycle (restart on crash, resource limits)

**Plist File: `~/Library/LaunchAgents/com.investscan.weekly.plist`**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>

    <!-- Unique identifier -->
    <key>Label</key>
    <string>com.investscan.weekly</string>

    <!-- What to run -->
    <key>ProgramArguments</key>
    <array>
        <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/.venv/bin/python</string>
        <string>-m</string>
        <string>investscan</string>
        <string>run</string>
        <string>--scheduled</string>
    </array>

    <!-- Working directory -->
    <key>WorkingDirectory</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test</string>

    <!-- When to run: Every Sunday at 20:00 (8 PM) -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>0</integer>  <!-- 0 = Sunday -->
        <key>Hour</key>
        <integer>20</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <!-- Environment variables -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>INVESTSCAN_CONFIG</key>
        <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/config/investscan.yaml</string>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>

    <!-- Logging -->
    <key>StandardOutPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stderr.log</string>

    <!-- Process management -->
    <key>Nice</key>
    <integer>10</integer>  <!-- Lower priority than interactive work -->

    <!-- CRITICAL: Run if the Mac was asleep at scheduled time -->
    <!-- launchd automatically runs missed StartCalendarInterval jobs on wake -->
    <!-- No special flag needed -- this is the default behavior -->

    <!-- Prevent multiple instances -->
    <key>AbandonProcessGroup</key>
    <false/>

    <!-- Keep loaded (but only fires on schedule) -->
    <key>KeepAlive</key>
    <false/>

    <!-- Timeout: 4 hours max (pipeline typically takes ~3.5 hours) -->
    <key>TimeOut</key>
    <integer>14400</integer>

    <!-- Throttle: Don't run more often than every 3600 seconds -->
    <key>ThrottleInterval</key>
    <integer>3600</integer>

</dict>
</plist>
```

**Installation and management:**

```bash
# Install (load the plist)
cp com.investscan.weekly.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.investscan.weekly.plist

# Verify loaded
launchctl list | grep investscan
# Expected: -  0  com.investscan.weekly

# Manual trigger (for testing)
launchctl start com.investscan.weekly

# Check last run status
launchctl list com.investscan.weekly
# The second column is the last exit code (0 = success)

# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.investscan.weekly.plist

# View logs
tail -f ~/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stdout.log

# Debug issues
log show --predicate 'process == "investscan"' --last 1h
```

#### C.2 cron Alternative (for comparison)

```bash
# crontab -l
# InvestScan weekly run: Sunday 8 PM
0 20 * * 0 cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test && .venv/bin/python -m investscan run --scheduled >> logs/cron.log 2>&1
```

#### C.3 launchd vs cron Comparison

| Feature | launchd | cron |
|---------|---------|------|
| **macOS native** | Yes (recommended) | Deprecated (functional but unsupported) |
| **Sleep recovery** | Automatic: runs missed jobs on wake | NO: missed jobs are simply skipped |
| **Logging** | Integrated with `os_log`, separate stdout/stderr paths | Manual (redirect to file) |
| **Process management** | Timeout, throttle, nice priority, restart policy | None |
| **Configuration** | XML plist (verbose but structured) | One-liner (concise but limited) |
| **Debugging** | `launchctl list`, `log show` | `grep CRON /var/log/system.log` |
| **Environment** | Explicit in plist (full control) | Minimal (often breaks PATH) |
| **Multiple instances** | Prevented by default | No protection |

**Verdict**: launchd wins on every dimension that matters for a long-running financial pipeline. The XML verbosity is a one-time cost.

#### C.4 Handling Mac Sleep During Scheduled Run

This is the most critical scheduling concern for a solo MacBook-based system.

**Scenario**: InvestScan is scheduled for Sunday 8 PM. The user closes the MacBook lid at 7 PM (church evening service) and opens it Monday 7 AM.

**launchd behavior**: `StartCalendarInterval` jobs are automatically executed when the system wakes up if they were missed during sleep. The job runs at 7 AM Monday. No configuration needed -- this is default behavior.

**cron behavior**: The Sunday 8 PM job is permanently missed. No catch-up mechanism exists in cron.

**Additional safeguards in InvestScan CLI**:

```python
# investscan/__main__.py (partial)
@cli.command()
@click.option("--scheduled", is_flag=True, help="Invoked by launchd/cron")
def run(scheduled: bool):
    """Execute the weekly pipeline."""
    if scheduled:
        # Check if source data is fresh enough
        envscan_age = check_data_freshness("envscan")
        gnews_age = check_data_freshness("gnews")

        if envscan_age > timedelta(days=10):
            logger.warning(f"EnvScan data is {envscan_age.days} days old. "
                          f"Report may use stale signals.")
            # Still proceed -- a report with stale data is better than no report

        if gnews_age > timedelta(days=10):
            logger.warning(f"GlobalNews data is {gnews_age.days} days old.")

        # Log the actual execution time vs scheduled time
        now = datetime.now()
        expected_sunday = last_sunday_8pm()
        delay = now - expected_sunday
        if delay > timedelta(hours=12):
            logger.info(f"Delayed execution: running {delay} after scheduled time "
                       f"(likely sleep recovery)")
```

#### C.5 Log Rotation for Long-Running System

InvestScan generates logs that accumulate over months. Without rotation, log files grow unbounded.

**Strategy 1: Python `logging.handlers.RotatingFileHandler`** (Recommended)

```python
# investscan/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: Path):
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        log_dir / "investscan.log",
        maxBytes=10 * 1024 * 1024,   # 10 MB per file
        backupCount=12,               # Keep 12 rotated files (~6 months at weekly runs)
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))

    logger = logging.getLogger("investscan")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
```

**Strategy 2: macOS `newsyslog.conf`** (Alternative for launchd logs)

```
# /etc/newsyslog.d/investscan.conf
# logfilename                                              [owner:group] mode count size when  flags
/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stdout.log  644  12  10240  *  J
/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stderr.log  644  12  10240  *  J
```

**Recommended approach**: Use RotatingFileHandler for application logs (pipeline execution) and let launchd stdout/stderr logs be managed by the application itself (the Python logger handles this). launchd stdout/stderr files are fallback-only for startup errors.

---

### D. Version Control Integration

#### D.1 Git for InvestScan Code

InvestScan code lives in the current repository (`01.invest_test/`). The `investscan/` package, `config/`, `templates/`, `tests/`, `workflow.md`, and `pyproject.toml` are all version-controlled.

**Branch strategy**: Simple trunk-based development on `main`. Solo developer does not need feature branches unless experimenting with risky changes (e.g., swapping BGE-M3 for a different model).

**Commit convention**:
```
feat(normalize): add WF4 evolution state parser
fix(sector): correct GICS mapping for E_Environmental signals
test(contract): add pSST scale detection edge case
docs(workflow): update pipeline step 3 validation checklist
```

#### D.2 Git for Output Versioning

**Should reports be committed?**

**Arguments FOR committing reports:**
- Reports are the primary deliverable. Version history shows how the system's analysis evolves.
- Enables `git diff` between weekly reports to see what changed.
- Acts as implicit backup.

**Arguments AGAINST committing reports:**
- Reports contain generated content that can be regenerated from source data.
- Weekly reports accumulate: 52 per year, each ~50-100 KB = ~5 MB/year of Markdown.
- Binary outputs (matplotlib PNGs, HTML with embedded Plotly) bloat the repo.
- Git is designed for source code, not generated artifacts.

**Recommendation: Do NOT commit reports to the main code repo.**

Instead:
- Reports live in `output/{date}/` which is gitignored.
- A separate `investscan-archive` repo (optional) can store reports if long-term versioning is desired.
- Time Machine handles backup (see section E).
- The decision journal (SQLite) is small and stable -- it CAN be committed or synced.

#### D.3 .gitignore Design

```gitignore
# ── InvestScan Runtime Output ──
output/
logs/

# ── Python ──
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/

# ── ML Models (large, downloaded on demand) ──
models/
*.bin
*.safetensors

# ── Data Files ──
*.parquet
*.sqlite
*.sqlite-journal
*.sqlite-wal
*.sqlite-shm

# ── macOS ──
.DS_Store

# ── IDE ──
.vscode/
.idea/

# ── Decision Journal (EXPLICIT INCLUDE) ──
# The journal is small and valuable -- track it
!data/decision-journal.sqlite

# ── Config (EXPLICIT INCLUDE) ──
# Config is code -- track it
!config/

# ── Inherited AgenticWorkflow ──
.claude/context-snapshots/
verification-logs/
autopilot-logs/
pacs-logs/
review-logs/
diagnosis-logs/
.tdd-guard
.claude/hooks/*.log
```

#### D.4 Configuration Change Tracking

The `config/investscan.yaml` file IS committed to git. Every configuration change produces a commit with rationale:

```yaml
# config/investscan.yaml
version: "1.0"

paths:
  envscan_root: "../EnvironmentScan-system-main-v4-main"
  gnews_root: "../GlobalNews-Crawling-AgenticWorkflow"
  output_dir: "output"
  log_dir: "logs"

pipeline:
  data_freshness_max_days: 7
  signal_loss_threshold: 0.20    # Abort if >20% signals lost in normalization
  min_signals_for_report: 50     # Don't generate report with <50 signals

normalization:
  dedup_similarity_threshold: 0.85  # TF-IDF cosine similarity for dedup
  psst_scale_override:              # Explicit scale per source (no auto-detect)
    wf4_database: "0-100"
    wf4_priority: "0-10"
    gnews: "0-1"

synthesis:
  direction_confidence_threshold: 0.40  # Minimum conviction to declare bull/bear
  convergence_bonus: 0.15               # Bonus for signals from both sources
  single_source_cap: 0.60              # Max conviction for single-source signals

report:
  language: "ko"
  top_signals_count: 10
  evidence_chains_count: 5
  include_disclaimer: true

scheduling:
  day: "sunday"
  hour: 20
  minute: 0
```

---

### E. Backup & Recovery

#### E.1 Signal Database Backup Strategy

InvestScan reads from source system signal databases. These are the crown jewels -- months of accumulated scanning data.

**EnvScan signal database** (`signals/database.json`):
- Format: JSON (833 KB currently, grows ~100 KB/month)
- Strategy: Copy to `backup/envscan/database-{date}.json` before each InvestScan run
- Retention: Keep 12 weekly backups (rolling)

**GlobalNews Parquet/SQLite**:
- Format: Parquet (ZSTD compressed) + SQLite FTS5
- Strategy: Copy to `backup/gnews/{date}/` before each run
- Retention: Keep 12 weekly backups (rolling)

**Backup script integrated into pipeline**:

```python
# investscan/backup.py
"""Pre-run backup of source system data."""
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("investscan.backup")

def backup_source_data(config: dict, run_date: str):
    """Copy source system signal databases before pipeline run."""
    backup_root = Path(config["paths"]["output_dir"]).parent / "backup"

    # EnvScan backup
    envscan_db = Path(config["paths"]["envscan_root"]) / "env-scanning/signals/database.json"
    if envscan_db.exists():
        dest = backup_root / "envscan" / f"database-{run_date}.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(envscan_db, dest)
        logger.info(f"Backed up EnvScan database: {dest} ({dest.stat().st_size / 1024:.1f} KB)")

    # GlobalNews backup
    gnews_output = Path(config["paths"]["gnews_root"]) / "data/output"
    if gnews_output.exists():
        dest = backup_root / "gnews" / run_date
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(gnews_output, dest)
        logger.info(f"Backed up GlobalNews output: {dest}")

    # Rotate: keep only last 12 backups
    _rotate_backups(backup_root / "envscan", max_count=12)
    _rotate_backups(backup_root / "gnews", max_count=12)

def _rotate_backups(backup_dir: Path, max_count: int):
    """Remove oldest backups beyond max_count."""
    if not backup_dir.exists():
        return

    items = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in items[max_count:]:
        if old.is_file():
            old.unlink()
            logger.info(f"Rotated old backup: {old.name}")
        elif old.is_dir():
            shutil.rmtree(old)
            logger.info(f"Rotated old backup dir: {old.name}")
```

#### E.2 Decision Journal Backup

The decision journal is a SQLite file (~100 KB after a year of weekly entries). It is the most personally valuable data InvestScan produces -- it records investment reasoning and outcomes.

**Strategy**: Just copy it. SQLite files are safe to copy when no write is in progress. Since InvestScan runs are sequential (not concurrent), this is always safe.

```python
# In the pipeline, after journal updates:
shutil.copy2("data/decision-journal.sqlite", f"backup/journal/decision-journal-{run_date}.sqlite")
```

**Additional**: The journal should be exported to JSONL weekly as a human-readable backup:

```python
# investscan/decision_journal.py (export method)
def export_jsonl(self, output_path: Path):
    """Export all journal entries to JSONL for backup and portability."""
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in self.query_all():
            f.write(json.dumps(asdict(entry), ensure_ascii=False, default=str) + "\n")
```

#### E.3 SQLite/Parquet Corruption Recovery

**SQLite corruption** (decision journal, GlobalNews index):

SQLite corruption is rare but possible (power loss during write, disk failure). Recovery steps:

1. **`.recover` command** (SQLite 3.29+): `sqlite3 corrupted.db ".recover" | sqlite3 recovered.db`
   This reconstructs the database by scanning the raw B-tree pages. It recovers most data even from severely corrupted files.

2. **WAL mode** (Write-Ahead Logging): Configure all SQLite databases to use WAL mode:
   ```python
   conn = sqlite3.connect("data/decision-journal.sqlite")
   conn.execute("PRAGMA journal_mode=WAL")
   ```
   WAL mode survives most crash scenarios because writes go to a separate log file first.

3. **Fallback to backup**: If `.recover` fails, restore from the most recent `backup/journal/` copy.

**Parquet corruption** (GlobalNews output):

Parquet files are immutable once written. Corruption only happens from incomplete writes or disk failure.

1. **Validation on read**: pyarrow raises `ArrowInvalid` on corrupt Parquet. InvestScan should catch this and fall back to the previous week's backup.
   ```python
   try:
       df = pd.read_parquet(gnews_signals_path)
   except (pyarrow.lib.ArrowInvalid, OSError) as e:
       logger.error(f"Corrupt Parquet file: {e}. Falling back to backup.")
       df = pd.read_parquet(backup_path)
   ```

2. **Re-crawl**: GlobalNews-Crawling can re-generate Parquet from raw JSONL (`data/raw/{date}/all_articles.jsonl`). The raw data is the true source of truth.

#### E.4 Time Machine Integration (macOS Native)

Time Machine is already running on the MacBook (standard macOS setup). It provides:

- Hourly backups for the last 24 hours
- Daily backups for the last month
- Weekly backups for all previous months

**What Time Machine covers for InvestScan:**
- All source code (investscan/, config/, templates/, tests/)
- All output reports (output/{date}/)
- All signal databases (EnvScan JSON, GlobalNews Parquet)
- Decision journal
- Configuration files
- ML model weights (if stored locally in models/)

**What Time Machine does NOT cover:**
- Files excluded in Time Machine preferences (check System Settings > Time Machine > Options)
- Files on external/network drives not in the backup scope
- Recovery speed: restoring a single file is fast, but restoring the entire project requires Time Machine UI navigation

**Recommendation**: Time Machine is the **last resort** backup. The application-level backups (Section E.1-E.2) are the primary recovery mechanism because:
1. They are automated (part of pipeline execution)
2. They are fast to restore (simple file copy)
3. They have known retention policy (12 weekly backups)
4. Time Machine supplements these with full-system coverage

**Verification command** (add to `/maintenance` health check):
```bash
# Check Time Machine is active and recent
tmutil latestbackup
# Expected: something within the last 24 hours
```

---

## BRANCH 4.2: MINIMAL Toolchain

**Philosophy**: "Every tool you add is a tool you maintain. A pastor with 2-4 hours per week cannot afford to debug launchd plists, MCP servers, and custom hooks. Use the absolute minimum that produces a useful weekly report."

---

### A. Python Environment

```bash
# One-time setup
python3 -m venv .venv
source .venv/bin/activate
pip install click pyyaml jinja2 pandas pyarrow sentence-transformers kiwipiepy matplotlib rich
pip install pytest  # dev only
pip freeze > requirements.txt
```

That is it. No `pyproject.toml`. No `[project.optional-dependencies]`. No build system. `pip install -r requirements.txt` reproduces the environment.

**Why not pyproject.toml?**: InvestScan is not a distributable package. It is a personal tool that runs on exactly one machine. The overhead of PEP 621 project metadata, build backends, and entry points is unjustified when `python -m investscan` works identically with a simple `__main__.py`.

### B. Scheduling

```bash
# crontab -e
# InvestScan: Sunday 8 PM
0 20 * * 0 cd /Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test && .venv/bin/python -m investscan run --scheduled >> logs/cron.log 2>&1
```

**Sleep problem**: Yes, cron misses jobs during sleep. The pragmatic solution: run InvestScan manually on Monday morning if the cron log shows no Sunday run. The pipeline has a `--date` flag for specifying any date.

**Why this is acceptable**: The user reads the report Monday morning over coffee. If it did not auto-generate, running `investscan run` manually takes 10 seconds of typing. The 3.5-hour pipeline runs in the background while the user does other work. The convenience loss is negligible for a weekly cadence.

### C. No MCP, No Custom Agents, No Custom Hooks

**MCP servers**: Not needed. `context7` is useful for library documentation during development, but InvestScan's runtime pipeline does not need MCP. The developer can use context7 ad-hoc during coding sessions without any InvestScan-specific configuration.

**Custom agents**: The pipeline is a Python CLI. It does not need Claude Code agents to execute. The developer invokes `investscan run` and reads the output report. Agent definitions are useful documentation but add no runtime value for a sequential batch pipeline.

**Custom hooks**: The inherited AgenticWorkflow hooks (destructive command blocking, secret filtering, context preservation) already provide safety. InvestScan-specific hooks (report validation, signal count checking) can be done as assertions inside the Python code itself:

```python
# Inside generate_report.py, not as a hook
assert "주의 사항" in rendered_report, "Report missing disclaimer section"
assert signal_count >= config.min_signals_for_report, f"Too few signals: {signal_count}"
```

This is simpler, easier to debug, and runs in the same process. Hooks are for cross-cutting concerns; business logic validation belongs in the business logic.

### D. Git for Code Only

```gitignore
# Simple .gitignore
output/
logs/
backup/
.venv/
__pycache__/
*.pyc
.DS_Store
models/
*.parquet
*.sqlite
```

No reports committed. No output versioning. No archive repository. Git tracks:
- `investscan/*.py` (source code)
- `config/investscan.yaml` (configuration)
- `templates/*.j2` (report templates)
- `tests/*.py` (test code)
- `requirements.txt` (dependencies)
- `workflow.md` (pipeline definition)

Everything else is either generated (reports, logs) or large (models, data).

### E. Time Machine Handles All Backup

No application-level backup scripts. No `backup/` directory. No rotation logic.

Time Machine already backs up the entire MacBook:
- Hourly for 24 hours
- Daily for a month
- Weekly thereafter

If the decision journal corrupts: `tmutil restore /path/to/decision-journal.sqlite`.
If EnvScan database is lost: Time Machine or re-run EnvScan.
If a report needs to be re-read from 3 months ago: Time Machine.

**The tradeoff**: Recovery is slightly slower (navigate Time Machine UI vs. `cp backup/latest`). But no backup code needs to be written, tested, debugged, or maintained. For a solo developer with 2-4 hours/week, the maintenance saved is worth the occasional 2-minute Time Machine recovery.

---

## COMPARISON: Full vs. Minimal Toolchain

### Side-by-Side Feature Matrix

| Dimension | Full (4.1) | Minimal (4.2) | Winner for Solo Dev |
|-----------|-----------|---------------|---------------------|
| **Python env** | venv + pyproject.toml + requirements.lock | venv + requirements.txt | **Minimal** -- pyproject.toml adds zero value for a single-machine personal tool |
| **Dependency pinning** | Abstract deps + lock file + phase2 extras | Flat requirements.txt | **Minimal** -- lock file discipline is overkill when there is one machine and one developer |
| **Scheduling** | launchd plist with XML config | cron one-liner | **Full** -- sleep recovery is worth the one-time XML setup for a Sunday evening pipeline |
| **Sleep recovery** | Automatic (launchd native) | Manual Monday morning run | **Full** -- this is the single strongest argument for launchd |
| **Custom agents** | 3 agent definitions | None | **Minimal** -- agents document intent but add no runtime value for a Python CLI pipeline |
| **Custom hooks** | 2 InvestScan-specific hooks | In-code assertions | **Minimal** -- assertions inside Python are easier to debug than hook scripts in a separate process |
| **MCP servers** | context7 + playwright + future financial MCP | None (use context7 ad-hoc) | **Minimal** -- MCP is useful during development, not during pipeline execution |
| **Slash commands** | 3 InvestScan commands | None | **Toss-up** -- commands are nice UX but not essential when `python -m investscan run` works |
| **Skills** | Full skill definition with references | None | **Minimal** -- skills are for reusable cross-project patterns; InvestScan is one project |
| **Git strategy** | Code + config; reports separate | Code + config; reports gitignored | **Tie** -- same effective strategy |
| **.gitignore** | Detailed with explicit includes | Simple blanket exclusions | **Tie** -- both work |
| **Source data backup** | Automated pre-run copy + 12-week rotation | Time Machine only | **Full** -- but the margin is thin for 2-4 hrs/week |
| **Journal backup** | SQLite copy + JSONL export | Time Machine only | **Full** -- the journal is irreplaceable personal data |
| **Corruption recovery** | WAL mode + .recover + fallback chain | Time Machine restore | **Full** -- WAL mode is 1 line of code with significant crash safety benefit |
| **Log rotation** | RotatingFileHandler (12 files, 10 MB each) | Manual (check log size occasionally) | **Full** -- RotatingFileHandler is 10 lines of code that prevents a 500 MB log file in year 2 |
| **Config tracking** | Committed YAML with change rationale | Committed YAML | **Tie** |
| **Total setup time** | ~8-12 hours | ~2-3 hours | **Minimal** |
| **Annual maintenance** | ~4-6 hours | ~1-2 hours | **Minimal** |

### Verdict: The Hybrid Recommendation

Neither extreme is optimal. The correct answer for a solo pastor-developer with 2-4 hours/week building a financial intelligence tool is:

**Take from FULL (4.1):**

1. **launchd scheduling** (not cron). The sleep recovery alone justifies the one-time XML setup. Sunday evening scheduling on a MacBook that might be asleep is a real scenario that happens every week. Estimated setup: 30 minutes.

2. **RotatingFileHandler**. Ten lines of Python that prevent a future problem. Estimated effort: 15 minutes.

3. **WAL mode for SQLite**. One line of code (`PRAGMA journal_mode=WAL`) that dramatically reduces corruption risk for the decision journal. Estimated effort: 5 minutes.

4. **Decision journal JSONL export**. The journal is irreplaceable personal data that records investment reasoning over months/years. A weekly JSONL export (10 lines of Python) provides a human-readable backup independent of SQLite binary format. Estimated effort: 20 minutes.

5. **Pre-run source data copy** (simplified). Not the full rotation system, but a simple "copy database.json and latest Parquet before pipeline runs." If something corrupts during the run, the pre-run copy is 30 seconds old. Estimated effort: 30 minutes.

**Take from MINIMAL (4.2):**

1. **`requirements.txt` instead of `pyproject.toml`**. InvestScan is a personal tool, not a distributable package. The simplicity of `pip install -r requirements.txt` outweighs the elegance of PEP 621.

2. **In-code assertions instead of custom hooks**. Business logic validation (report sections, signal counts) belongs in the Python code where it can be debugged with `print()` and `pdb`, not in a separate hook process that communicates via exit codes.

3. **No custom agents for pipeline execution**. The pipeline is `python -m investscan run`. Agent definitions are documentation, not execution infrastructure. Write them later if Claude Code is used interactively for signal analysis.

4. **No custom MCP server**. Use `context7` ad-hoc during development. Build a financial data MCP server in Phase 2 only if the need becomes concrete.

5. **No slash commands initially**. `python -m investscan run` is already a one-command execution. Slash commands add value only when running InvestScan interactively within a Claude Code session -- which is a Phase 2 workflow.

6. **Time Machine as backup foundation**. Application-level backups (pre-run copy + journal JSONL) are the primary recovery mechanism. Time Machine is the safety net for everything else.

**The Hybrid Toolchain -- Final Stack:**

```
SCHEDULING:    launchd plist (Sunday 8 PM, sleep recovery)      [from Full]
PYTHON ENV:    venv + requirements.txt                          [from Minimal]
LOGGING:       RotatingFileHandler (10 MB x 12 files)           [from Full]
SQLITE:        WAL mode on all databases                        [from Full]
BACKUP:        Pre-run source copy + journal JSONL + Time Machine [Hybrid]
VALIDATION:    In-code assertions                               [from Minimal]
AGENTS:        None initially (add in Phase 2 if needed)        [from Minimal]
HOOKS:         Inherited only (no InvestScan-specific)          [from Minimal]
MCP:           context7 ad-hoc (no custom server)               [from Minimal]
COMMANDS:      None initially                                   [from Minimal]
GIT:           Code + config only, reports gitignored           [Tie]
```

**Total incremental setup time**: ~2 hours beyond the Minimal baseline.
**Annual maintenance**: ~2-3 hours (primarily launchd plist updates if paths change).

### The Decision Framework

The rule is simple: **add a tool only if the cost of NOT having it is greater than the cost of maintaining it.**

| Tool | Cost of NOT Having | Cost of Maintaining | Include? |
|------|-------------------|-------------------|----------|
| launchd | Missed weekly runs when Mac sleeps (frequent) | Occasional plist edits (rare) | **YES** |
| RotatingFileHandler | 500 MB log file in year 2 (certain) | 0 (set and forget) | **YES** |
| WAL mode | Potential journal corruption on crash (rare but devastating) | 0 (one PRAGMA statement) | **YES** |
| Journal JSONL export | Journal locked in SQLite binary format (inconvenient) | 0 (runs automatically) | **YES** |
| Pre-run data copy | Source data corruption during run (rare) | Disk space for 12 copies (~15 MB) | **YES** |
| pyproject.toml | Slightly less elegant pip install | Understanding PEP 621 build system | **NO** |
| Custom agents | Manual pipeline invocation | Writing and updating 3 agent docs | **NO** (Phase 2) |
| Custom hooks | Report validation is in-process instead of pre/post | Debugging cross-process hook failures | **NO** |
| Custom MCP | No conversational market data queries | Building a stdio MCP server | **NO** (Phase 2) |
| Slash commands | Typing `python -m investscan run` instead of `/investscan-run` | Command file maintenance | **NO** (Phase 2) |
| Output git repo | No version-controlled report history | Another repo to manage | **NO** |
| conda | None (no C/Fortran deps, no CUDA) | 3-5 GB installation + environment.yml | **NO** |

---

### Implementation Priority (within Month 1)

| Order | Task | Time | When |
|-------|------|------|------|
| 1 | Create `.venv` and install dependencies | 15 min | Day 1 |
| 2 | `pip freeze > requirements.txt` | 1 min | Day 1 |
| 3 | Write `config/investscan.yaml` | 20 min | Day 1 |
| 4 | Write `.gitignore` | 10 min | Day 1 |
| 5 | Add `RotatingFileHandler` to logging setup | 15 min | Week 1 |
| 6 | Add `PRAGMA journal_mode=WAL` to SQLite init | 5 min | Week 1 |
| 7 | Add pre-run backup function | 30 min | Week 2 |
| 8 | Add journal JSONL export | 20 min | Week 4 (when journal exists) |
| 9 | Create and install launchd plist | 30 min | Week 4 (after first manual pipeline success) |
| **Total** | | **~2.5 hours** | |

This timeline integrates with the Week 1-8 shipping schedule from the Implementation Guide (Phase 2-3-4). The toolchain is built incrementally alongside the pipeline code, never ahead of it. No tool is installed before the code that uses it exists.
