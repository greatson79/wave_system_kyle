# Branch 5: workflow.md Integration Analysis — TWO Approaches

**Analysts**: Integration Implementation Expert A (Deep) + Expert B (Simple)
**Date**: 2026-03-28
**Context**: InvestScan Scenario B (BALANCED) implementation
**Constraint**: Solo dev, pastor, 2-4 hrs/week, MacBook M5 Max 64GB

---

## Factual Basis: What Actually Exists Right Now

Before designing integration, we must be precise about the actual filesystem layout, output formats, and invocation methods.

### Source System 1: EnvironmentScan

| Property | Actual Value |
|----------|-------------|
| **Root path** | `../EnvironmentScan-system-main-v4-main/` (sibling directory) |
| **Invocation** | Claude Code slash command: `/env-scan:run` (context: fork, invokes `master-orchestrator`) |
| **Primary signal output** | `env-scanning/signals/database.json` (509 signals, 833KB, cumulative) |
| **Daily output** | `output/WF{1,2,3}_*_signals_{date}.json` (per-workflow JSON arrays) |
| **Integrated reports** | `env-scanning/integrated/reports/daily/integrated-scan-{date}.md` |
| **Integrated analysis** | `env-scanning/integrated/analysis/*.json` (cross-workflow) |
| **Signal schema** | `{id, title, url, source: {name, type, tier}, published_date, preliminary_category, summary}` |
| **Classification** | STEEPs: T_Technological, P_Political, E_Economic, S_Social, E_Environmental, s_Values |
| **Scoring** | pSST (0-100) |
| **Human checkpoints** | 9 total across WF1-WF4 + Integration |
| **Runtime** | ~120 min (Claude API dependent) |
| **Orchestration** | Claude Code agents (37 agents, LLM-driven) -- NOT scriptable via shell |

### Source System 2: GlobalNews-Crawling

| Property | Actual Value |
|----------|-------------|
| **Root path** | `../GlobalNews-Crawling-AgenticWorkflow/` (sibling directory) |
| **Invocation** | `.venv/bin/python main.py --mode full --date YYYY-MM-DD` |
| **Raw data** | `data/raw/{date}/all_articles.jsonl` (~2MB/run) |
| **Processed output** | `data/output/` (currently minimal: `run_metadata.json` only) |
| **Expected outputs** | `data/output/signals.parquet`, `data/output/analysis.parquet`, `data/output/topics.parquet`, `data/output/index.sqlite` |
| **Signal schema** | Parquet: `{signal_id, signal_layer (L1-L5), burst_score, novelty_score, singularity_composite, confidence}` |
| **Classification** | 5-Layer: L1_fad through L5_singularity |
| **Processing** | 8-stage local ML pipeline (SBERT, BERTopic, Prophet, PCMCI) |
| **Runtime** | ~98 min (53 crawl + 45 analyze) |
| **Orchestration** | Pure Python CLI -- fully scriptable |

### InvestScan Target Location

| Property | Value |
|----------|-------|
| **Root path** | `./01.invest_test/` (current project) |
| **workflow.md** | To be created at project root |
| **New Python modules** | `investscan/` package directory |
| **Output directory** | `output/{date}/` |
| **Config** | `config/investscan.yaml` or `~/.investscan/config.yaml` |

---

## BRANCH 5.1: DEEP workflow.md Integration

### The Full workflow.md Structure

```markdown
# InvestScan Weekly Intelligence Pipeline

One-command execution of multi-source macro signal scanning, normalization,
investment synthesis, and Korean weekly report generation.

## Overview

- **Input**: EnvironmentScan signal database + GlobalNews-Crawling Parquet output
- **Output**: Korean weekly investment direction report with STEEPs classification
- **Frequency**: Weekly (Sunday evening batch)
- **Autopilot**: enabled — human checkpoints auto-approved with rationale logging
- **pACS**: enabled

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.

**Constitutional Principles**:

1. **Quality Absolutism** — Report quality is the sole metric. A report that
   generates one insight the user would not have found manually justifies the
   entire pipeline. Speed, token cost, execution time are irrelevant.
2. **Single-File SOT** — `.claude/state.yaml` tracks pipeline state, step
   completion, output paths, and error history. Only Orchestrator writes.
3. **Code Change Protocol** — All investscan/ module changes follow CCP 3-step.

**Domain-Specific Gene Expression**:
- P1 (Data Refinement) STRONGLY expressed: Signal normalization layer is the
  core value proposition. Noise removal from 500+ signals to actionable
  investment direction.
- P2 (Expert Delegation) expressed: Separate agents for data collection,
  synthesis, and report generation.

---

## Phase 1: Data Collection

### Step 1.1: Health Check
- **Agent**: `@investscan-orchestrator`
- **Command**: `python3 -m investscan health-check`
- **Verification**:
  - [ ] EnvironmentScan project directory exists and signals/database.json is present
  - [ ] GlobalNews-Crawling project directory exists and .venv/bin/python is functional
  - [ ] InvestScan output directory writable
  - [ ] Config file loaded and all paths resolved
- **Task**: Validate all prerequisites before pipeline execution
- **Output**: `verification-logs/step-1.1-health.md`
- **Translation**: none

### Step 1.2: Collect EnvironmentScan Data
- **Pre-processing**: Check if EnvScan ran within the last 7 days by reading
  `output/WF*_signals_*.json` modification dates
- **Agent**: `@envscan-collector`
- **Command**: Read latest signals from EnvScan output directory
  ```bash
  # If fresh data exists (< 7 days old):
  python3 -m investscan collect-envscan --date {date}
  # If stale: prompt user to run /env-scan:run in EnvironmentScan project
  ```
- **Verification**:
  - [ ] At least one WF*_signals_{date}.json file found within 7-day window
  - [ ] signals/database.json readable and contains >= 50 signals
  - [ ] All signals have required fields: id, title, source, preliminary_category
- **Task**: Read and validate EnvironmentScan output files
- **Output**: `output/{date}/raw/envscan-signals.json` (copy of relevant signals)
- **Translation**: none
- **Checkpoint**: Step 1.2 complete — EnvScan data collected

### Step 1.3: Collect GlobalNews-Crawling Data
- **Pre-processing**: Check if GlobalNews ran within the last 7 days by reading
  `data/raw/{date}/` directory existence
- **Agent**: `@gnews-collector`
- **Command**:
  ```bash
  # If fresh data exists:
  python3 -m investscan collect-gnews --date {date}
  # If stale: run GlobalNews pipeline
  cd ../GlobalNews-Crawling-AgenticWorkflow
  .venv/bin/python main.py --mode full --date {date}
  ```
- **Verification**:
  - [ ] data/raw/{date}/all_articles.jsonl exists and size > 100KB
  - [ ] data/output/run_metadata.json shows exit_code 0
  - [ ] If Parquet outputs exist: signals.parquet readable
- **Task**: Read and validate GlobalNews output files
- **Output**: `output/{date}/raw/gnews-articles.jsonl` (copy of relevant data)
- **Translation**: none
- **Checkpoint**: Step 1.3 complete — GlobalNews data collected

### Step 1.4: (human) Data Freshness Review
- **Action**: Confirm both data sources are sufficiently recent for this week's report
- **Command**: `/investscan:review-data`
- **Autopilot Decision**: Auto-approve if both sources < 7 days old

---

## Phase 2: Signal Processing & Synthesis

### Step 2.1: Signal Normalization
- **Pre-processing**: Load raw data from Step 1.2 and 1.3 outputs
- **Agent**: `@signal-normalizer`
- **Command**:
  ```bash
  python3 -m investscan normalize --date {date}
  ```
- **Verification**:
  - [ ] unified_signals.json contains signals from BOTH sources
  - [ ] Each signal has: id, title, source_system, steeps_category, confidence,
        signal_layer, original_source
  - [ ] Cross-source deduplication applied (title similarity > 0.85 removed)
  - [ ] Signal count >= 30 after dedup
- **Task**: Harmonize EnvScan JSON and GlobalNews JSONL/Parquet into unified schema
- **Output**: `output/{date}/normalized/unified_signals.json`
- **Translation**: none

### Step 2.2: STEEPs Classification
- **Pre-processing**: Read unified signals from Step 2.1
- **Agent**: `@steeps-classifier`
- **Command**:
  ```bash
  python3 -m investscan classify-steeps --date {date}
  ```
- **Verification**:
  - [ ] All signals have steeps_primary and steeps_secondary fields
  - [ ] STEEPs distribution: at least 3 of 6 categories represented
  - [ ] GlobalNews signals (which lack native STEEPs) classified with
        confidence >= 0.6
- **Task**: Assign STEEPs categories to all signals (EnvScan: use native;
  GlobalNews: keyword-based classification)
- **Output**: `output/{date}/classified/steeps_signals.json`
- **Translation**: none

### Step 2.3: Investment Synthesis
- **Pre-processing**: Read classified signals from Step 2.2
- **Agent**: `@investment-synthesizer`
- **Command**:
  ```bash
  python3 -m investscan synthesize --date {date}
  ```
- **Verification**:
  - [ ] Sector direction calls generated for >= 5 KOSPI/KOSDAQ sectors
  - [ ] Each direction call has: sector, direction (bull/bear/neutral),
        conviction (0-100), evidence_signals (list of signal IDs)
  - [ ] Multi-timeframe analysis: short (1-4wk), mid (1-6mo), long (6mo+)
  - [ ] Cross-source convergence signals identified and scored higher
- **Task**: Map signals to Korean market sectors, compute directional conviction,
  detect cross-source convergence
- **Output**: `output/{date}/synthesis/investment_direction.json`
- **Translation**: none

### Step 2.4: (human) Synthesis Review
- **Action**: Review investment direction calls and evidence chains
- **Command**: `/investscan:review-synthesis`
- **Autopilot Decision**: Auto-approve if >= 5 sectors covered and all
  directions have >= 2 supporting signals

---

## Phase 3: Report Generation

### Step 3.1: Generate Weekly Report
- **Pre-processing**: Load synthesis from Step 2.3, load previous week's
  report (if exists) for comparison
- **Agent**: `@report-generator` (model: opus)
- **Verification**:
  - [ ] Report contains all required sections: Executive Summary, STEEPs Table,
        Sector Direction, Risk Radar, Weak Signal Watch, Evidence Chains
  - [ ] All sector direction calls cite specific source signals
  - [ ] Korean language quality: natural, professional financial terminology
  - [ ] Report length: 2,000-5,000 words
- **Task**: Generate Korean weekly investment direction report
- **Output**: `output/{date}/reports/weekly-report-{date}.md`
- **Translation**: none (report is natively Korean)
- **Review**: `@reviewer` — Enhanced L2 review for factual accuracy

### Step 3.2: (human) Final Report Approval
- **Action**: Read the weekly report, decide if it provides actionable insight
- **Command**: `/investscan:approve-report`
- **Autopilot Decision**: Auto-approve if L2 review passes and pACS >= 70

---

## Claude Code Configuration

### Sub-agents

```yaml
agents:
  investscan-orchestrator:
    description: "InvestScan pipeline orchestration and health monitoring"
    model: sonnet
    tools: Read, Bash, Glob, Grep
    maxTurns: 50
    memory: project

  envscan-collector:
    description: "Read and validate EnvironmentScan output data"
    model: haiku
    tools: Read, Bash, Glob
    maxTurns: 10
    memory: local

  gnews-collector:
    description: "Read and validate GlobalNews-Crawling output data"
    model: haiku
    tools: Read, Bash, Glob
    maxTurns: 15
    memory: local

  signal-normalizer:
    description: "Harmonize multi-source signals into unified schema"
    model: sonnet
    tools: Read, Bash
    maxTurns: 10
    memory: local

  steeps-classifier:
    description: "Assign STEEPs categories to signals lacking native classification"
    model: sonnet
    tools: Read, Bash
    maxTurns: 10
    memory: local

  investment-synthesizer:
    description: "Map signals to market sectors and compute investment direction"
    model: opus
    tools: Read, Bash
    maxTurns: 20
    memory: project

  report-generator:
    description: "Generate Korean weekly investment direction report"
    model: opus
    tools: Read, Write, Bash
    maxTurns: 30
    memory: project
    skills:
      - doctoral-writing
```

### Slash Commands

```yaml
commands:
  /investscan:run:
    description: "Execute full InvestScan pipeline (collect → normalize → synthesize → report)"

  /investscan:health:
    description: "Check pipeline prerequisites and source system availability"

  /investscan:review-data:
    description: "Review collected data freshness and quality"

  /investscan:review-synthesis:
    description: "Review investment synthesis results before report generation"

  /investscan:approve-report:
    description: "Final approval of weekly report"
```

### SOT (State Management)

```yaml
# .claude/state.yaml
workflow:
  name: "investscan-weekly"
  current_step: "1.1"
  status: "in_progress"
  date: "2026-03-28"
  outputs:
    step-1.2: "output/2026-03-28/raw/envscan-signals.json"
    step-1.3: "output/2026-03-28/raw/gnews-articles.jsonl"
    step-2.1: "output/2026-03-28/normalized/unified_signals.json"
    step-2.2: "output/2026-03-28/classified/steeps_signals.json"
    step-2.3: "output/2026-03-28/synthesis/investment_direction.json"
    step-3.1: "output/2026-03-28/reports/weekly-report-2026-03-28.md"
  autopilot:
    enabled: true
    log_directory: "autopilot-logs/"
  source_freshness:
    envscan_latest: "2026-03-25"
    gnews_latest: "2026-03-25"
  errors: []
```

### Hooks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/block_destructive_commands.py",
          "timeout": 10
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [{
          "type": "command",
          "command": "python3 -c \"import json,sys; d=json.loads(sys.stdin.read()); p=d.get('tool_input',{}).get('file_path',''); print('OK' if 'output/' in p or '.claude/' in p else 'WARN: writing outside expected directories')\"",
          "timeout": 5
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/scripts/generate_context_summary.py",
          "timeout": 30
        }]
      }
    ]
  }
}
```

### Configuration Management

```yaml
# config/investscan.yaml — path configuration
paths:
  envscan_root: "../EnvironmentScan-system-main-v4-main"
  gnews_root: "../GlobalNews-Crawling-AgenticWorkflow"
  output_root: "./output"

  # EnvScan specific outputs
  envscan_signals_db: "{envscan_root}/env-scanning/signals/database.json"
  envscan_daily_output: "{envscan_root}/output/"
  envscan_integrated: "{envscan_root}/env-scanning/integrated/"

  # GlobalNews specific outputs
  gnews_raw: "{gnews_root}/data/raw/{date}/"
  gnews_output: "{gnews_root}/data/output/"
  gnews_python: "{gnews_root}/.venv/bin/python"

thresholds:
  dedup_similarity: 0.85          # TF-IDF cosine threshold for dedup
  steeps_min_confidence: 0.6      # minimum confidence for keyword-based STEEPs
  min_signals_per_report: 30      # minimum unified signals
  min_sectors: 5                  # minimum sectors in synthesis
  data_freshness_days: 7          # max age of source data

steeps_to_sectors:
  T_Technological: ["IT", "반도체", "바이오", "인터넷"]
  E_Economic: ["금융", "건설", "유통", "운송"]
  P_Political: ["방산", "공기업", "규제 산업"]
  S_Social: ["헬스케어", "교육", "미디어", "소비재"]
  E_Environmental: ["에너지", "화학", "신재생에너지"]
  s_Values: ["ESG 관련 전 섹터"]
```

### Parameter Passing Between Steps

State flows through the SOT (`state.yaml`) and file system:

```
Step 1.2 writes → output/{date}/raw/envscan-signals.json
Step 1.3 writes → output/{date}/raw/gnews-articles.jsonl
         ↓
Step 2.1 reads both → writes output/{date}/normalized/unified_signals.json
Step 2.2 reads 2.1  → writes output/{date}/classified/steeps_signals.json
Step 2.3 reads 2.2  → writes output/{date}/synthesis/investment_direction.json
         ↓
Step 3.1 reads 2.3  → writes output/{date}/reports/weekly-report-{date}.md

SOT tracks all output paths in outputs.step-N.N
Each step reads the SOT to find its input file paths.
```

### Task API for Progress Tracking

```
Pipeline execution tracked via Claude Code Task API:

TaskCreate("Health Check", "Validate all prerequisites", @investscan-orchestrator)
TaskCreate("Collect EnvScan", "Read latest signals", @envscan-collector)
TaskCreate("Collect GlobalNews", "Read latest articles", @gnews-collector)
TaskCreate("Normalize", "Harmonize schemas", @signal-normalizer)
TaskCreate("Classify STEEPs", "Assign categories", @steeps-classifier)
TaskCreate("Synthesize", "Generate investment direction", @investment-synthesizer)
TaskCreate("Report", "Generate Korean weekly report", @report-generator)

Each task: in_progress → completed (or failed → retry)
Progress visible via TaskList at any time.
```

### Error Handling

```yaml
error_handling:
  on_envscan_stale:
    action: warn_user
    message: "EnvScan data is > 7 days old. Run /env-scan:run first, or proceed with stale data?"
    fallback: proceed_with_stale

  on_gnews_missing:
    action: run_gnews
    command: "cd {gnews_root} && .venv/bin/python main.py --mode full --date {date}"
    timeout: 7200  # 2 hours
    fallback: gnews_only_report

  on_normalization_failure:
    action: retry_with_feedback
    max_attempts: 3
    escalation: human

  on_synthesis_failure:
    action: retry_with_feedback
    max_attempts: 3
    escalation: human

  on_single_source_only:
    action: generate_degraded_report
    message: "Only one source available. Report generated with reduced confidence."
```

### LOC Estimate for Deep Integration

| Component | Files | LOC |
|-----------|-------|-----|
| `workflow.md` | 1 | ~400 |
| `.claude/agents/*.md` (7 agents) | 7 | ~350 |
| `.claude/commands/*.md` (5 commands) | 5 | ~250 |
| `config/investscan.yaml` | 1 | ~80 |
| `.claude/state.yaml` (template) | 1 | ~30 |
| Hook scripts (new) | 2 | ~100 |
| **workflow.md integration layer** | **17** | **~1,210** |
| `investscan/__init__.py` | 1 | ~20 |
| `investscan/__main__.py` (CLI) | 1 | ~150 |
| `investscan/config.py` | 1 | ~100 |
| `investscan/schema.py` | 1 | ~150 |
| `investscan/health_check.py` | 1 | ~120 |
| `investscan/collect_envscan.py` | 1 | ~200 |
| `investscan/collect_gnews.py` | 1 | ~200 |
| `investscan/normalize_signals.py` | 1 | ~400 |
| `investscan/classify_steeps.py` | 1 | ~300 |
| `investscan/synthesize_investment.py` | 1 | ~500 |
| `investscan/sector_mapper.py` | 1 | ~300 |
| `investscan/generate_report.py` | 1 | ~500 |
| `investscan/utils.py` | 1 | ~150 |
| **Python pipeline** | **13** | **~3,090** |
| **TOTAL** | **30** | **~4,300** |

---

## BRANCH 5.2: SIMPLE Integration (Shell Script + Minimal workflow.md)

### The Shell Script: `investscan-run.sh`

```bash
#!/bin/bash
# investscan-run.sh — Complete InvestScan pipeline, called by workflow.md
# Exit on any error, treat unset variables as errors
set -euo pipefail

# ============================================================
# Configuration
# ============================================================
DATE="${1:-$(date +%Y-%m-%d)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Sibling project paths (relative to Vibe-Practice directory)
VIBE_ROOT="$(dirname "$PROJECT_ROOT")"
ENVSCAN_ROOT="$VIBE_ROOT/EnvironmentScan-system-main-v4-main"
GNEWS_ROOT="$VIBE_ROOT/GlobalNews-Crawling-AgenticWorkflow"

# Output structure
OUTPUT_DIR="$PROJECT_ROOT/output/$DATE"
RAW_DIR="$OUTPUT_DIR/raw"
NORMALIZED_DIR="$OUTPUT_DIR/normalized"
SYNTHESIS_DIR="$OUTPUT_DIR/synthesis"
REPORT_DIR="$OUTPUT_DIR/reports"

# ============================================================
# Helper functions
# ============================================================
log() { echo "[$(date '+%H:%M:%S')] $1"; }
die() { echo "FATAL: $1" >&2; exit 1; }

check_dir() {
    [ -d "$1" ] || die "Directory not found: $1"
}

check_file() {
    [ -f "$1" ] || die "File not found: $1"
}

file_age_days() {
    # Returns age of file in days (macOS compatible)
    local file="$1"
    local now=$(date +%s)
    local mod=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null)
    echo $(( (now - mod) / 86400 ))
}

# ============================================================
# Step 0: Prerequisites
# ============================================================
log "Step 0: Checking prerequisites..."

check_dir "$ENVSCAN_ROOT"
check_dir "$GNEWS_ROOT"
check_file "$GNEWS_ROOT/.venv/bin/python"

# Create output directories
mkdir -p "$RAW_DIR" "$NORMALIZED_DIR" "$SYNTHESIS_DIR" "$REPORT_DIR"

log "  EnvScan root:  $ENVSCAN_ROOT"
log "  GlobalNews root: $GNEWS_ROOT"
log "  Output:          $OUTPUT_DIR"

# ============================================================
# Step 1: Collect EnvironmentScan data
# ============================================================
log "Step 1: Collecting EnvironmentScan data..."

ENVSCAN_DB="$ENVSCAN_ROOT/env-scanning/signals/database.json"
ENVSCAN_OUTPUT="$ENVSCAN_ROOT/output"

if [ -f "$ENVSCAN_DB" ]; then
    AGE=$(file_age_days "$ENVSCAN_DB")
    if [ "$AGE" -gt 7 ]; then
        log "  WARNING: database.json is ${AGE} days old (> 7 days)"
        log "  Consider running /env-scan:run in EnvironmentScan project"
    fi
    cp "$ENVSCAN_DB" "$RAW_DIR/envscan-database.json"
    log "  Copied database.json ($(wc -c < "$ENVSCAN_DB" | tr -d ' ') bytes)"
else
    log "  WARNING: No database.json found. EnvScan data will be empty."
fi

# Copy latest daily signal files
LATEST_WF_FILES=$(find "$ENVSCAN_OUTPUT" -name "WF*_signals_*.json" -mtime -7 2>/dev/null | sort -r | head -4)
if [ -n "$LATEST_WF_FILES" ]; then
    for f in $LATEST_WF_FILES; do
        cp "$f" "$RAW_DIR/"
        log "  Copied $(basename "$f")"
    done
else
    log "  WARNING: No recent WF signal files found"
fi

# ============================================================
# Step 2: Collect GlobalNews data
# ============================================================
log "Step 2: Collecting GlobalNews data..."

# Check if GlobalNews has recent data
GNEWS_RAW="$GNEWS_ROOT/data/raw"
RECENT_GNEWS=$(find "$GNEWS_RAW" -maxdepth 1 -type d -name "2026-*" -mtime -7 2>/dev/null | sort -r | head -1)

if [ -n "$RECENT_GNEWS" ]; then
    ARTICLES="$RECENT_GNEWS/all_articles.jsonl"
    if [ -f "$ARTICLES" ]; then
        cp "$ARTICLES" "$RAW_DIR/gnews-articles.jsonl"
        ARTICLE_COUNT=$(wc -l < "$ARTICLES" | tr -d ' ')
        log "  Copied all_articles.jsonl ($ARTICLE_COUNT articles)"
    fi
else
    log "  No recent GlobalNews data. Running crawl..."
    cd "$GNEWS_ROOT"
    .venv/bin/python main.py --mode full --date "$DATE" || {
        log "  WARNING: GlobalNews crawl failed. Continuing with EnvScan only."
    }
    cd "$PROJECT_ROOT"

    # Retry collection
    ARTICLES="$GNEWS_RAW/$DATE/all_articles.jsonl"
    if [ -f "$ARTICLES" ]; then
        cp "$ARTICLES" "$RAW_DIR/gnews-articles.jsonl"
    fi
fi

# Copy Parquet outputs if they exist
for pfile in signals.parquet analysis.parquet topics.parquet; do
    SRC="$GNEWS_ROOT/data/output/$pfile"
    if [ -f "$SRC" ]; then
        cp "$SRC" "$RAW_DIR/"
        log "  Copied $pfile"
    fi
done

# ============================================================
# Step 3: Normalize signals
# ============================================================
log "Step 3: Normalizing signals..."

cd "$PROJECT_ROOT"
python3 investscan/normalize_signals.py \
    --envscan-db "$RAW_DIR/envscan-database.json" \
    --envscan-daily "$RAW_DIR/" \
    --gnews-articles "$RAW_DIR/gnews-articles.jsonl" \
    --output "$NORMALIZED_DIR/unified_signals.json" \
    --date "$DATE" \
    || die "Signal normalization failed"

SIGNAL_COUNT=$(python3 -c "import json; print(len(json.load(open('$NORMALIZED_DIR/unified_signals.json'))))")
log "  Unified signals: $SIGNAL_COUNT"

# ============================================================
# Step 4: STEEPs classification
# ============================================================
log "Step 4: Classifying STEEPs..."

python3 investscan/classify_steeps.py \
    --input "$NORMALIZED_DIR/unified_signals.json" \
    --output "$NORMALIZED_DIR/steeps_signals.json" \
    || die "STEEPs classification failed"

log "  STEEPs classification complete"

# ============================================================
# Step 5: Investment synthesis
# ============================================================
log "Step 5: Synthesizing investment direction..."

python3 investscan/synthesize_investment.py \
    --input "$NORMALIZED_DIR/steeps_signals.json" \
    --output "$SYNTHESIS_DIR/investment_direction.json" \
    --config "$PROJECT_ROOT/config/investscan.yaml" \
    || die "Investment synthesis failed"

SECTOR_COUNT=$(python3 -c "import json; d=json.load(open('$SYNTHESIS_DIR/investment_direction.json')); print(len(d.get('sectors',[])))")
log "  Sectors analyzed: $SECTOR_COUNT"

# ============================================================
# Step 6: Generate report
# ============================================================
log "Step 6: Generating weekly report..."

python3 investscan/generate_report.py \
    --synthesis "$SYNTHESIS_DIR/investment_direction.json" \
    --signals "$NORMALIZED_DIR/steeps_signals.json" \
    --output "$REPORT_DIR/weekly-report-$DATE.md" \
    --date "$DATE" \
    || die "Report generation failed"

REPORT_SIZE=$(wc -c < "$REPORT_DIR/weekly-report-$DATE.md" | tr -d ' ')
log "  Report generated: $REPORT_SIZE bytes"

# ============================================================
# Summary
# ============================================================
echo ""
echo "========================================"
echo "InvestScan Pipeline Complete"
echo "========================================"
echo "Date:    $DATE"
echo "Signals: $SIGNAL_COUNT unified"
echo "Sectors: $SECTOR_COUNT analyzed"
echo "Report:  $REPORT_DIR/weekly-report-$DATE.md"
echo "========================================"
```

### The Minimal workflow.md

```markdown
# InvestScan Weekly Intelligence Pipeline

Weekly macro signal scanning and investment direction synthesis.

## Overview

- **Input**: EnvironmentScan signals + GlobalNews articles
- **Output**: Korean weekly investment direction report
- **Frequency**: Weekly
- **Autopilot**: enabled

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.

- **Quality Gene**: Report insight quality is the sole metric
- **SOT Gene**: `.claude/state.yaml` tracks run history
- **Strongly Expressed**: P1 (signal-to-noise refinement from 500+ signals)

---

## Phase 1: Pipeline Execution

### Step 1: Run InvestScan Pipeline
- **Agent**: `@investscan-orchestrator`
- **Command**:
  ```bash
  bash investscan-run.sh {date}
  ```
- **Verification**:
  - [ ] Exit code 0
  - [ ] `output/{date}/reports/weekly-report-{date}.md` exists and size > 2KB
  - [ ] `output/{date}/synthesis/investment_direction.json` has >= 5 sectors
  - [ ] `output/{date}/normalized/unified_signals.json` has >= 30 signals
- **Task**: Execute complete pipeline: collect, normalize, classify, synthesize, report
- **Output**: `output/{date}/reports/weekly-report-{date}.md`
- **Translation**: none

### Step 2: (human) Report Review
- **Action**: Read weekly report. "Does this contain at least one insight
  I would not have found manually?"
- **Command**: `/investscan:review`

---

## Phase 2: Report Refinement (Optional)

### Step 3: AI-Enhanced Report Narrative
- **Agent**: `@report-enhancer` (model: opus)
- **Verification**:
  - [ ] Enhanced report maintains all factual claims from Step 1 output
  - [ ] Korean language quality improved (natural, professional)
  - [ ] Evidence chains preserved (signal IDs still traceable)
- **Task**: Read the generated report and improve narrative quality,
  add executive summary, strengthen evidence language
- **Output**: `output/{date}/reports/weekly-report-{date}-enhanced.md`
- **Translation**: none

---

## Claude Code Configuration

### Sub-agents

investscan-orchestrator (sonnet): Pipeline health and execution
report-enhancer (opus): Korean narrative quality improvement

### Slash Commands

/investscan:run — Execute full pipeline
/investscan:review — Review weekly report
/investscan:health — Check prerequisites

### SOT

- **SOT file**: `.claude/state.yaml`
- **Writer**: investscan-orchestrator only
- **Pattern**: Minimal — just tracks run dates and status

### Error Handling

on_pipeline_failure:
  action: Show error from investscan-run.sh stderr
  fallback: Manual troubleshooting via /investscan:health
```

### Path Management: `config/investscan.yaml`

```yaml
# config/investscan.yaml
# All paths relative to project root (01.invest_test/)
# The shell script resolves absolute paths at runtime using $(dirname $0)

source_systems:
  envscan:
    # Relative to Vibe-Practice/ parent directory
    root: "../EnvironmentScan-system-main-v4-main"
    signals_db: "env-scanning/signals/database.json"
    daily_output: "output/"
    integrated: "env-scanning/integrated/"

  gnews:
    root: "../GlobalNews-Crawling-AgenticWorkflow"
    python: ".venv/bin/python"
    main: "main.py"
    raw_data: "data/raw/"
    output: "data/output/"

output:
  root: "./output"
  structure: "{root}/{date}/{step}/"

freshness:
  max_age_days: 7
```

### LOC Estimate for Simple Integration

| Component | Files | LOC |
|-----------|-------|-----|
| `workflow.md` (minimal) | 1 | ~80 |
| `investscan-run.sh` | 1 | ~180 |
| `.claude/agents/*.md` (2 agents) | 2 | ~80 |
| `.claude/commands/*.md` (3 commands) | 3 | ~90 |
| `config/investscan.yaml` | 1 | ~30 |
| **workflow + integration layer** | **8** | **~460** |
| `investscan/normalize_signals.py` | 1 | ~400 |
| `investscan/classify_steeps.py` | 1 | ~300 |
| `investscan/synthesize_investment.py` | 1 | ~500 |
| `investscan/sector_mapper.py` | 1 | ~300 |
| `investscan/generate_report.py` | 1 | ~500 |
| `investscan/config.py` | 1 | ~80 |
| `investscan/schema.py` | 1 | ~150 |
| `investscan/utils.py` | 1 | ~100 |
| **Python pipeline** | **8** | **~2,330** |
| **TOTAL** | **16** | **~2,790** |

---

## COMPARISON: Deep vs. Simple

### Head-to-Head Feature Comparison

| Dimension | 5.1 DEEP | 5.2 SIMPLE | Verdict |
|-----------|----------|------------|---------|
| **Total LOC** | ~4,300 (30 files) | ~2,790 (16 files) | Simple: 35% less code |
| **workflow.md LOC** | ~400 | ~80 | Simple: 80% less orchestration |
| **Integration layer LOC** | ~1,210 | ~460 | Simple: 62% less glue code |
| **Python pipeline LOC** | ~3,090 | ~2,330 | Simple: 25% less (shared core logic) |
| **Agents to maintain** | 7 | 2 | Simple: 71% fewer agent definitions |
| **Commands to maintain** | 5 | 3 | Simple: 40% fewer |
| **Config files** | 3 (yaml + state + hooks) | 1 (yaml only) | Simple: 67% fewer |
| **HITL checkpoints** | 3 (data review + synthesis + report) | 1 (report review only) | Simple: fewer interruptions |
| **Autopilot support** | Full (with decision logging) | Minimal (run and review) | Deep: richer automation |
| **Progress tracking** | Task API + SOT + step-by-step | Shell stdout + exit codes | Deep: richer visibility |
| **Error granularity** | Per-step retry + fallback + escalation | Exit on first error + stderr | Deep: graceful degradation |
| **Resume capability** | SOT tracks current_step, can resume mid-pipeline | Restart from beginning | Deep: can recover from interruptions |
| **pACS integration** | Full (per-step self-rating) | None | Deep: quality confidence tracking |
| **L2 review** | @reviewer on report step | None (human only) | Deep: adversarial quality check |
| **Context preservation** | Full hook stack | None | Deep: survives session loss |

### What Breaks When Claude Code Updates?

| Update Type | 5.1 DEEP Impact | 5.2 SIMPLE Impact |
|-------------|-----------------|-------------------|
| **Agent frontmatter schema changes** | 7 agent .md files to update | 2 agent .md files to update |
| **Task API changes** | Progress tracking breaks | No impact (does not use Task API) |
| **Hook event name changes** | 2+ hook scripts to update | No impact (no custom hooks) |
| **Slash command format changes** | 5 command .md files to update | 3 command .md files to update |
| **SOT/state.yaml format changes** | State tracking breaks, resume capability lost | No impact (minimal SOT usage) |
| **pACS protocol changes** | Logging breaks | No impact (no pACS) |
| **Sub-agent invocation changes** | 7 agents affected | 2 agents affected |
| **Python version changes** | No impact (independent) | No impact (independent) |
| **Bash changes** | No impact | Script may need updates (unlikely) |

**Summary**: Deep has 7 potential failure surfaces from Claude Code updates. Simple has 2. The Python pipeline modules are identical in both approaches and unaffected by Claude Code changes.

### Which Approach Matches the Context?

**Developer profile**: Solo, pastor, 2-4 hrs/week, MacBook M5 Max.

| Context Factor | Favors DEEP | Favors SIMPLE |
|----------------|-------------|---------------|
| 2-4 hrs/week budget | | **X** — Less maintenance burden |
| Solo developer (no team) | | **X** — Agent Teams add complexity with no collaboration benefit |
| Personal tool (not SaaS) | | **X** — No users to impress with progress tracking |
| Weekly cadence (not daily) | | **X** — Resume capability less important for weekly batch |
| Pastor with competing priorities | | **X** — Simpler mental model when returning after a week |
| Wants "one-command execution" | | **X** — `bash investscan-run.sh` is literally one command |
| Needs debugging capability | **X** — Per-step logs help | — Harder to isolate failures |
| Wants Claude Code integration learning | **X** — Full pattern demonstration | — Misses learning opportunity |
| AgenticWorkflow is the meta-framework | **X** — Should demonstrate own patterns | — Underuses the framework |

**Score**: DEEP 3, SIMPLE 6. Context strongly favors Simple.

### The Critical Insight: The Python Pipeline Is the Same

Both approaches require the same core Python modules:

- `normalize_signals.py` (~400 LOC)
- `classify_steeps.py` (~300 LOC)
- `synthesize_investment.py` (~500 LOC)
- `sector_mapper.py` (~300 LOC)
- `generate_report.py` (~500 LOC)
- `schema.py` (~150 LOC)
- `config.py` (~80-100 LOC)
- `utils.py` (~100-150 LOC)

This is ~2,330-3,090 LOC regardless of integration approach. The difference is ONLY in the orchestration layer:

| | DEEP Orchestration | SIMPLE Orchestration |
|--|-------------------|---------------------|
| LOC | ~1,210 | ~460 |
| Files | 17 | 8 |
| Maintenance surface | Large (agents, commands, hooks, SOT) | Small (1 shell script, minimal workflow.md) |
| Debug value | High (per-step visibility) | Low (binary pass/fail) |
| Learning value | High (demonstrates Claude Code patterns) | Low (standard bash) |

---

## RECOMMENDATION FOR SCENARIO B

### Start Simple, Upgrade to Deep When Triggers Fire

**Month 1-2 (M1)**: Use SIMPLE approach.
- Build the Python pipeline modules (the hard part)
- Wrap with `investscan-run.sh` (the easy part)
- Minimal workflow.md (3 steps: run, review, enhance)
- Focus ALL dev time on signal quality, not orchestration elegance

**Month 3-4 (M2)**: Evaluate upgrade triggers.
- Trigger: "I keep re-running individual steps" --> Add per-step invocation
- Trigger: "Pipeline fails mid-way and I lose progress" --> Add SOT resume
- Trigger: "I want to run without babysitting" --> Add full Autopilot
- Trigger: "Report quality varies and I cannot tell why" --> Add pACS + L2

**Month 5-6 (M3)**: Upgrade to Deep if 2+ triggers fired.
- The upgrade path is clean: shell script steps become workflow.md steps
- Agent definitions are additive (new .md files, nothing deleted)
- Python pipeline modules are UNCHANGED

**Why this order is correct**: The Python pipeline is the value. The orchestration is the convenience. Building convenience before value inverts the priority. A beautiful workflow.md that orchestrates a bad synthesis engine produces a bad report. A crude shell script that orchestrates a good synthesis engine produces a good report.

### The One Exception

If the user's explicit goal is to **demonstrate AgenticWorkflow patterns** (i.e., InvestScan is partly a showcase for the framework), then start with DEEP from Day 1. The extra 750 LOC of orchestration serves a pedagogical purpose even if it is not operationally necessary.

Given the PRD recommendation of Scenario B ("build for yourself first"), SIMPLE is the correct starting point. The workflow.md is the final deliverable, but it should grow organically from demonstrated need, not from anticipated elegance.
