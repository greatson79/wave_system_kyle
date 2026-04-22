# InvestScan Orchestration: Two Implementation Analyses

**Branch 2.1**: Evolutionary (Shell -> Python growth)
**Branch 2.2**: Big Bang (Full CLI from day 1)
**Date**: 2026-03-27
**Context**: Solo dev, MacBook M5 Max 64GB, cron/launchd scheduling

---

## Branch 2.1: EVOLUTIONARY Orchestration (Shell -> Python growth)

### Philosophy

Start with the simplest possible orchestrator -- a shell script -- that calls existing systems and new Python modules sequentially. Replace it with a Python CLI only when the shell script's limitations become painful (typically Month 3-4 when checkpoint/resume, config management, and structured logging become necessary).

This mirrors how most successful batch pipelines actually evolve in practice.

---

### Month 1-2: Shell Script (`run.sh`)

```bash
#!/usr/bin/env bash
# ============================================================
# InvestScan Pipeline Orchestrator v0.1 (Shell Phase)
# Usage: ./run.sh [YYYY-MM-DD]
# ============================================================
set -euo pipefail

# ── Configuration ──────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
ENVSCAN_ROOT="$(cd "$PROJECT_ROOT/../EnvironmentScan-system-main-v4-main" && pwd)"
GNEWS_ROOT="$(cd "$PROJECT_ROOT/../GlobalNews-Crawling-AgenticWorkflow" && pwd)"

RUN_DATE="${1:-$(date +%Y-%m-%d)}"
OUTPUT_DIR="$PROJECT_ROOT/output/$RUN_DATE"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/investscan-${RUN_DATE}.log"

# ── Helpers ────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

log() {
    local level="$1"; shift
    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$ts] [$level] $*" | tee -a "$LOG_FILE"
}

fail() {
    log "FATAL" "$1"
    echo "PIPELINE FAILED at step: $CURRENT_STEP" >> "$OUTPUT_DIR/status.txt"
    exit "${2:-1}"
}

check_exit() {
    local code=$?
    local step_name="$1"
    if [ $code -ne 0 ]; then
        fail "$step_name exited with code $code" $code
    fi
    log "INFO" "$step_name completed successfully (exit 0)"
}

write_status() {
    echo "$1" > "$OUTPUT_DIR/status.txt"
}

CURRENT_STEP="init"

# ── Pre-flight Checks ─────────────────────────────────────
log "INFO" "========== InvestScan Pipeline Start =========="
log "INFO" "Run date: $RUN_DATE"
log "INFO" "Output:   $OUTPUT_DIR"

# Verify source system directories exist
[ -d "$ENVSCAN_ROOT" ] || fail "EnvScan directory not found: $ENVSCAN_ROOT"
[ -d "$GNEWS_ROOT" ]   || fail "GlobalNews directory not found: $GNEWS_ROOT"

# Verify Python environments exist
[ -f "$GNEWS_ROOT/.venv/bin/python" ] || fail "GlobalNews .venv not found"

# Check disk space (need at least 2GB free)
FREE_KB=$(df -k "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
[ "$FREE_KB" -gt 2097152 ] || fail "Insufficient disk space: ${FREE_KB}KB free, need 2GB"

log "INFO" "Pre-flight checks passed"

# ── Step 1: Run EnvironmentScan ────────────────────────────
CURRENT_STEP="envscan"
write_status "running:envscan"
log "INFO" "[Step 1/5] Starting EnvironmentScan quad scan..."
ENVSCAN_START=$(date +%s)

cd "$ENVSCAN_ROOT"
# EnvScan uses Claude Code slash commands internally.
# From shell, we invoke its Python orchestrator directly.
if [ -f "env-scanning/orchestrator.py" ]; then
    python env-scanning/orchestrator.py --mode quad --date "$RUN_DATE" \
        >> "$LOG_FILE" 2>&1
    check_exit "EnvironmentScan"
elif [ -f "run_scan.py" ]; then
    python run_scan.py --quad --date "$RUN_DATE" \
        >> "$LOG_FILE" 2>&1
    check_exit "EnvironmentScan"
else
    log "WARN" "EnvScan entry point not found. Checking for existing output..."
    # Graceful degradation: if EnvScan has recent output, continue
    if [ -f "env-scanning/signals/database.json" ]; then
        log "WARN" "Using existing EnvScan signals (may be stale)"
    else
        fail "No EnvScan entry point and no existing signals"
    fi
fi

ENVSCAN_END=$(date +%s)
log "INFO" "EnvScan completed in $(( ENVSCAN_END - ENVSCAN_START ))s"

# ── Step 2: Run GlobalNews ─────────────────────────────────
CURRENT_STEP="globalnews"
write_status "running:globalnews"
log "INFO" "[Step 2/5] Starting GlobalNews crawl + analysis..."
GNEWS_START=$(date +%s)

cd "$GNEWS_ROOT"
"$GNEWS_ROOT/.venv/bin/python" main.py --mode full --date "$RUN_DATE" \
    >> "$LOG_FILE" 2>&1
check_exit "GlobalNews"

GNEWS_END=$(date +%s)
log "INFO" "GlobalNews completed in $(( GNEWS_END - GNEWS_START ))s"

# ── Step 3: Signal Normalization ───────────────────────────
CURRENT_STEP="normalize"
write_status "running:normalize"
log "INFO" "[Step 3/5] Normalizing signals..."
NORM_START=$(date +%s)

cd "$PROJECT_ROOT"
python -m invest_pipeline.normalize_signals \
    --date "$RUN_DATE" \
    --envscan-root "$ENVSCAN_ROOT" \
    --gnews-root "$GNEWS_ROOT" \
    --output "$OUTPUT_DIR/unified_signals.json" \
    >> "$LOG_FILE" 2>&1
check_exit "Signal Normalization"

# Validate output exists and is non-empty
[ -s "$OUTPUT_DIR/unified_signals.json" ] || fail "Normalization produced empty output"

NORM_END=$(date +%s)
log "INFO" "Normalization completed in $(( NORM_END - NORM_START ))s"

# ── Step 4: Investment Synthesis ───────────────────────────
CURRENT_STEP="synthesize"
write_status "running:synthesize"
log "INFO" "[Step 4/5] Synthesizing investment signals..."
SYNTH_START=$(date +%s)

python -m invest_pipeline.synthesize_investment \
    --date "$RUN_DATE" \
    --input "$OUTPUT_DIR/unified_signals.json" \
    --output "$OUTPUT_DIR/investment_synthesis.json" \
    >> "$LOG_FILE" 2>&1
check_exit "Investment Synthesis"

[ -s "$OUTPUT_DIR/investment_synthesis.json" ] || fail "Synthesis produced empty output"

SYNTH_END=$(date +%s)
log "INFO" "Synthesis completed in $(( SYNTH_END - SYNTH_START ))s"

# ── Step 5: Report Generation ─────────────────────────────
CURRENT_STEP="report"
write_status "running:report"
log "INFO" "[Step 5/5] Generating investment report..."
REPORT_START=$(date +%s)

python -m invest_pipeline.generate_report \
    --date "$RUN_DATE" \
    --input "$OUTPUT_DIR/investment_synthesis.json" \
    --output-en "$OUTPUT_DIR/invest-report-${RUN_DATE}.md" \
    --output-ko "$OUTPUT_DIR/invest-report-${RUN_DATE}-ko.md" \
    >> "$LOG_FILE" 2>&1
check_exit "Report Generation"

REPORT_END=$(date +%s)
log "INFO" "Report generated in $(( REPORT_END - REPORT_START ))s"

# ── Summary ────────────────────────────────────────────────
TOTAL_END=$(date +%s)
TOTAL_ELAPSED=$(( TOTAL_END - ENVSCAN_START ))

write_status "completed"

log "INFO" "========== InvestScan Pipeline Complete =========="
log "INFO" "Total runtime: ${TOTAL_ELAPSED}s ($(( TOTAL_ELAPSED / 60 ))m)"
log "INFO" "Report: $OUTPUT_DIR/invest-report-${RUN_DATE}.md"
log "INFO" "Signals: $(python -c "import json; d=json.load(open('$OUTPUT_DIR/unified_signals.json')); print(len(d.get('signals',d if isinstance(d,list) else [])))" 2>/dev/null || echo 'unknown') unified signals"

echo ""
echo "=== InvestScan Complete ==="
echo "Report: $OUTPUT_DIR/invest-report-${RUN_DATE}.md"
echo "Log:    $LOG_FILE"
```

**LOC**: ~140 lines (pure orchestration, no business logic)

**What this shell script does well**:
- Single-command execution: `./run.sh` or `./run.sh 2026-03-27`
- Exit code propagation from every step
- Timestamped logging to file + stdout
- Pre-flight checks (directories, disk space, Python envs)
- Graceful degradation if EnvScan entry point is missing but signals exist
- Status file for external monitoring (`output/{date}/status.txt`)
- Runtime measurement per step

**What it cannot do** (triggers migration to Python):
- Checkpoint/resume (if GlobalNews fails, must re-run EnvScan)
- Config file loading (paths are hardcoded or env vars)
- Structured error handling (just exit codes, no categorization)
- Retry with backoff for individual steps
- Parallel execution of EnvScan + GlobalNews (possible but brittle in bash)

---

### Month 3-4: Python CLI Migration (`cli.py`)

The migration trigger: you want `--resume` to skip already-completed steps, or you want configurable paths, or the shell script's error handling is too coarse.

```python
#!/usr/bin/env python3
"""
InvestScan CLI v0.2 (Python Phase)
Evolutionary replacement for run.sh.

Usage:
    python -m investscan run --date 2026-03-27
    python -m investscan run --resume          # skip completed steps
    python -m investscan status                # show last run
    python -m investscan report --date 2026-03-27  # regenerate report only
"""
import sys
import json
import time
import logging
import subprocess
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional

import click  # pip install click

# ── Configuration ──────────────────────────────────────────

@dataclass
class PipelineConfig:
    """Loaded from config/pipeline.yaml or defaults."""
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    envscan_root: Path = field(default=None)
    gnews_root: Path = field(default=None)
    output_base: Path = field(default=None)
    log_dir: Path = field(default=None)

    def __post_init__(self):
        if self.envscan_root is None:
            self.envscan_root = self.project_root.parent / "EnvironmentScan-system-main-v4-main"
        if self.gnews_root is None:
            self.gnews_root = self.project_root.parent / "GlobalNews-Crawling-AgenticWorkflow"
        if self.output_base is None:
            self.output_base = self.project_root / "output"
        if self.log_dir is None:
            self.log_dir = self.project_root / "logs"

    @classmethod
    def from_yaml(cls, path: Path) -> "PipelineConfig":
        """Load config from YAML, falling back to defaults."""
        if path.exists():
            import yaml  # pip install pyyaml
            with open(path) as f:
                data = yaml.safe_load(f) or {}
            return cls(
                project_root=Path(data.get("project_root", cls().project_root)),
                envscan_root=Path(data["envscan_root"]) if "envscan_root" in data else None,
                gnews_root=Path(data["gnews_root"]) if "gnews_root" in data else None,
            )
        return cls()


# ── Pipeline Step Definitions ──────────────────────────────

class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepResult:
    name: str
    status: StepStatus
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    elapsed_seconds: float = 0.0
    error: Optional[str] = None
    output_files: list = field(default_factory=list)


@dataclass
class PipelineState:
    """Checkpoint file: output/{date}/pipeline_state.json"""
    run_date: str
    started_at: str
    steps: dict[str, dict] = field(default_factory=dict)  # name -> StepResult dict
    overall_status: str = "running"

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, default=str)

    @classmethod
    def load(cls, path: Path) -> Optional["PipelineState"]:
        if path.exists():
            with open(path) as f:
                data = json.load(f)
            return cls(**data)
        return None

    def step_completed(self, name: str) -> bool:
        step = self.steps.get(name, {})
        return step.get("status") == StepStatus.COMPLETED.value


# ── Step Execution Engine ──────────────────────────────────

logger = logging.getLogger("investscan")


def run_subprocess(
    cmd: list[str],
    cwd: Path,
    log_file: Path,
    timeout: int = 10800,  # 3 hours default
) -> tuple[int, str]:
    """Run a subprocess, tee output to log file, return (exit_code, stderr)."""
    logger.info(f"Executing: {' '.join(cmd)}")
    logger.info(f"  cwd: {cwd}")

    with open(log_file, "a") as lf:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=lf,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    return proc.returncode, proc.stderr


def execute_step(
    name: str,
    cmd: list[str],
    cwd: Path,
    log_file: Path,
    state: PipelineState,
    state_path: Path,
    output_files: list[Path] = None,
    resume: bool = False,
    timeout: int = 10800,
) -> StepResult:
    """Execute a single pipeline step with checkpoint support."""

    # Resume: skip if already completed
    if resume and state.step_completed(name):
        logger.info(f"[SKIP] {name} -- already completed (resume mode)")
        return StepResult(name=name, status=StepStatus.SKIPPED)

    logger.info(f"[START] {name}")
    result = StepResult(
        name=name,
        status=StepStatus.RUNNING,
        started_at=datetime.now().isoformat(),
    )
    state.steps[name] = asdict(result)
    state.save(state_path)

    start = time.monotonic()
    try:
        exit_code, stderr = run_subprocess(cmd, cwd, log_file, timeout=timeout)
        elapsed = time.monotonic() - start

        if exit_code != 0:
            result.status = StepStatus.FAILED
            result.error = stderr[:2000] if stderr else f"Exit code {exit_code}"
            logger.error(f"[FAIL] {name} after {elapsed:.0f}s: {result.error[:200]}")
        else:
            # Validate output files exist
            if output_files:
                missing = [f for f in output_files if not f.exists() or f.stat().st_size == 0]
                if missing:
                    result.status = StepStatus.FAILED
                    result.error = f"Missing/empty output files: {[str(m) for m in missing]}"
                    logger.error(f"[FAIL] {name}: {result.error}")
                else:
                    result.status = StepStatus.COMPLETED
                    result.output_files = [str(f) for f in output_files]
                    logger.info(f"[DONE] {name} in {elapsed:.0f}s")
            else:
                result.status = StepStatus.COMPLETED
                logger.info(f"[DONE] {name} in {elapsed:.0f}s")

        result.elapsed_seconds = elapsed

    except subprocess.TimeoutExpired:
        result.status = StepStatus.FAILED
        result.error = f"Timeout after {timeout}s"
        result.elapsed_seconds = timeout
        logger.error(f"[TIMEOUT] {name}")

    except Exception as e:
        result.status = StepStatus.FAILED
        result.error = str(e)
        result.elapsed_seconds = time.monotonic() - start
        logger.error(f"[ERROR] {name}: {e}")

    result.finished_at = datetime.now().isoformat()
    state.steps[name] = asdict(result)
    state.save(state_path)
    return result


# ── CLI ────────────────────────────────────────────────────

@click.group()
@click.pass_context
def cli(ctx):
    """InvestScan -- Investment Signal Pipeline Orchestrator."""
    ctx.ensure_object(dict)
    config_path = Path(__file__).parent.parent / "config" / "pipeline.yaml"
    ctx.obj["config"] = PipelineConfig.from_yaml(config_path)


@cli.command()
@click.option("--date", "run_date", default=None, help="YYYY-MM-DD (default: today)")
@click.option("--resume", is_flag=True, help="Skip already-completed steps")
@click.option("--step", type=str, default=None, help="Run single step only (envscan|globalnews|normalize|synthesize|report)")
@click.pass_context
def run(ctx, run_date: Optional[str], resume: bool, step: Optional[str]):
    """Run the full InvestScan pipeline."""
    cfg: PipelineConfig = ctx.obj["config"]

    if run_date is None:
        run_date = date.today().isoformat()

    output_dir = cfg.output_base / run_date
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = cfg.log_dir / f"investscan-{run_date}.log"
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / "pipeline_state.json"

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file),
        ],
    )

    # Load or create pipeline state
    if resume:
        state = PipelineState.load(state_path) or PipelineState(
            run_date=run_date, started_at=datetime.now().isoformat()
        )
        logger.info(f"Resuming pipeline for {run_date}")
    else:
        state = PipelineState(run_date=run_date, started_at=datetime.now().isoformat())
        logger.info(f"Starting fresh pipeline for {run_date}")

    # ── Pre-flight checks ──
    preflight_errors = []
    if not cfg.envscan_root.is_dir():
        preflight_errors.append(f"EnvScan root not found: {cfg.envscan_root}")
    if not cfg.gnews_root.is_dir():
        preflight_errors.append(f"GlobalNews root not found: {cfg.gnews_root}")
    gnews_python = cfg.gnews_root / ".venv" / "bin" / "python"
    if not gnews_python.exists():
        preflight_errors.append(f"GlobalNews .venv python not found: {gnews_python}")

    if preflight_errors:
        for err in preflight_errors:
            logger.error(f"Pre-flight: {err}")
        raise click.Abort()

    # ── Define pipeline steps ──
    unified_signals = output_dir / "unified_signals.json"
    investment_synthesis = output_dir / "investment_synthesis.json"
    report_en = output_dir / f"invest-report-{run_date}.md"
    report_ko = output_dir / f"invest-report-{run_date}-ko.md"

    steps = [
        {
            "name": "envscan",
            "cmd": ["python", "env-scanning/orchestrator.py", "--mode", "quad", "--date", run_date],
            "cwd": cfg.envscan_root,
            "timeout": 9000,  # 2.5 hours
            "output_files": [],  # EnvScan output is checked by normalization
        },
        {
            "name": "globalnews",
            "cmd": [str(gnews_python), "main.py", "--mode", "full", "--date", run_date],
            "cwd": cfg.gnews_root,
            "timeout": 7200,  # 2 hours
            "output_files": [],
        },
        {
            "name": "normalize",
            "cmd": [
                sys.executable, "-m", "invest_pipeline.normalize_signals",
                "--date", run_date,
                "--envscan-root", str(cfg.envscan_root),
                "--gnews-root", str(cfg.gnews_root),
                "--output", str(unified_signals),
            ],
            "cwd": cfg.project_root,
            "timeout": 300,  # 5 min
            "output_files": [unified_signals],
        },
        {
            "name": "synthesize",
            "cmd": [
                sys.executable, "-m", "invest_pipeline.synthesize_investment",
                "--date", run_date,
                "--input", str(unified_signals),
                "--output", str(investment_synthesis),
            ],
            "cwd": cfg.project_root,
            "timeout": 600,  # 10 min
            "output_files": [investment_synthesis],
        },
        {
            "name": "report",
            "cmd": [
                sys.executable, "-m", "invest_pipeline.generate_report",
                "--date", run_date,
                "--input", str(investment_synthesis),
                "--output-en", str(report_en),
                "--output-ko", str(report_ko),
            ],
            "cwd": cfg.project_root,
            "timeout": 600,  # 10 min
            "output_files": [report_en],
        },
    ]

    # Filter to single step if requested
    if step:
        steps = [s for s in steps if s["name"] == step]
        if not steps:
            logger.error(f"Unknown step: {step}")
            raise click.Abort()

    # ── Execute ──
    failed = False
    for s in steps:
        result = execute_step(
            name=s["name"],
            cmd=s["cmd"],
            cwd=s["cwd"],
            log_file=log_file,
            state=state,
            state_path=state_path,
            output_files=[Path(f) for f in s.get("output_files", [])],
            resume=resume,
            timeout=s.get("timeout", 10800),
        )
        if result.status == StepStatus.FAILED:
            failed = True
            state.overall_status = f"failed:{s['name']}"
            state.save(state_path)
            logger.error(f"Pipeline stopped at {s['name']}. Use --resume to continue after fixing.")
            break

    if not failed:
        state.overall_status = "completed"
        state.save(state_path)
        logger.info("=" * 60)
        logger.info("InvestScan pipeline completed successfully")
        logger.info(f"Report: {report_en}")
        logger.info("=" * 60)


@cli.command()
@click.option("--date", "run_date", default=None, help="YYYY-MM-DD (default: latest)")
@click.pass_context
def status(ctx, run_date: Optional[str]):
    """Show pipeline status for a given date."""
    cfg: PipelineConfig = ctx.obj["config"]

    if run_date is None:
        # Find latest output directory
        output_dirs = sorted(cfg.output_base.glob("????-??-??"), reverse=True)
        if not output_dirs:
            click.echo("No pipeline runs found.")
            return
        run_date = output_dirs[0].name

    state_path = cfg.output_base / run_date / "pipeline_state.json"
    state = PipelineState.load(state_path)

    if state is None:
        click.echo(f"No pipeline state found for {run_date}")
        return

    click.echo(f"\n{'=' * 50}")
    click.echo(f"InvestScan Pipeline Status: {run_date}")
    click.echo(f"{'=' * 50}")
    click.echo(f"Overall: {state.overall_status}")
    click.echo(f"Started: {state.started_at}")
    click.echo()

    for name, step_data in state.steps.items():
        status_icon = {
            "completed": "[OK]",
            "failed": "[FAIL]",
            "running": "[...]",
            "skipped": "[SKIP]",
            "pending": "[--]",
        }.get(step_data.get("status", "pending"), "[??]")

        elapsed = step_data.get("elapsed_seconds", 0)
        elapsed_str = f"{elapsed:.0f}s" if elapsed else "--"
        click.echo(f"  {status_icon} {name:15s}  {elapsed_str:>8s}")

        if step_data.get("error"):
            click.echo(f"       Error: {step_data['error'][:100]}")

    click.echo()


@cli.command()
@click.option("--date", "run_date", required=True, help="YYYY-MM-DD")
@click.option("--format", "fmt", default="md", type=click.Choice(["md", "json"]))
@click.pass_context
def report(ctx, run_date: str, fmt: str):
    """Regenerate report from existing synthesis data."""
    cfg: PipelineConfig = ctx.obj["config"]
    output_dir = cfg.output_base / run_date
    synthesis_file = output_dir / "investment_synthesis.json"

    if not synthesis_file.exists():
        click.echo(f"No synthesis data found for {run_date}. Run the pipeline first.")
        return

    # Re-run only the report step
    ctx.invoke(run, run_date=run_date, resume=False, step="report")


if __name__ == "__main__":
    cli()
```

**LOC**: ~310 lines

**Migration path from run.sh to cli.py**:

| Week | Action | Coexistence |
|------|--------|-------------|
| Month 1-2 | Use `run.sh` exclusively | `cli.py` does not exist yet |
| Month 3 W1 | Create `cli.py` with `run` command only, wrapping same subprocess calls | Both exist; `run.sh` is primary |
| Month 3 W2 | Add `--resume` and `pipeline_state.json` checkpointing to `cli.py` | `cli.py` becomes primary |
| Month 3 W3 | Add `status` command | Delete `run.sh` |
| Month 4 | Add `report --format`, `journal add` | Python CLI is sole orchestrator |

**Key difference from run.sh**: The Python CLI introduces `pipeline_state.json` -- a checkpoint file that records which steps completed. This enables `--resume` to skip expensive steps (EnvScan: 2hr, GlobalNews: 1.5hr) when only a downstream step fails.

---

### workflow.md Integration (Evolutionary)

The workflow.md for Claude Code orchestration wraps the shell/Python CLI. Claude Code does not need to understand the pipeline internals -- it delegates to the script.

```markdown
# InvestScan Daily Pipeline

Automated investment signal synthesis from EnvironmentScan + GlobalNews.

## Overview

- **Input**: Raw signals from EnvScan (17+ sources) + GlobalNews (116 sites)
- **Output**: Investment direction report (EN + KO) with sector heat map
- **Frequency**: daily (6:00 AM KST via launchd)
- **Autopilot**: enabled
- **pACS**: enabled

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.

**Constitutional Principles**:

1. **Quality Absolutism** -- Investment direction accuracy and evidence completeness
2. **Single-File SOT** -- `.claude/state.yaml` for workflow state; `pipeline_state.json` for step tracking
3. **Code Change Protocol** -- Any modification to invest_pipeline/ follows CCP 3-step

**Domain-Specific Gene Expression**:
P1 (Data Precision) is the dominant gene. Financial signals have zero tolerance for hallucination.
P2 (Expert Delegation) expressed via 5-step sequential pipeline with specialized modules.

---

## Implementation

### 1. Pre-flight Health Check
- **Agent**: Orchestrator
- **Verification**:
  - [ ] EnvScan directory exists and has signals from within 48 hours
  - [ ] GlobalNews directory exists and .venv is functional
  - [ ] Disk space > 2GB free
  - [ ] Previous run's pipeline_state.json reviewed for failures
- **Task**: Validate all upstream dependencies before committing 4 hours of compute
- **Output**: Health check pass/fail logged

### 2. Execute Pipeline
- **Agent**: Orchestrator
- **Task**: Run the InvestScan pipeline via CLI
- **Command**:
  ```bash
  # Month 1-2 (shell phase):
  cd /path/to/01.invest_test && ./run.sh

  # Month 3+ (Python phase):
  cd /path/to/01.invest_test && python -m investscan run --date $(date +%Y-%m-%d)
  ```
- **Verification**:
  - [ ] `output/{date}/pipeline_state.json` shows `overall_status: completed`
  - [ ] `output/{date}/unified_signals.json` has > 50 signals
  - [ ] `output/{date}/invest-report-{date}.md` exists and is > 5KB
- **Output**: Complete pipeline run with all artifacts

### 3. Report Quality Review
- **Agent**: `@reviewer`
- **Verification**:
  - [ ] Every directional call (bull/bear) has >= 2 source signals in evidence chain
  - [ ] Conviction levels are conservative (no "high conviction" without 3+ corroborating sources)
  - [ ] Korean market sector mappings are plausible
  - [ ] No hallucinated source names or signal IDs
- **Task**: Adversarial review of generated investment report
- **Output**: Review pass/fail with specific issues listed

### 4. (human) Final Review
- **Action**: User reviews investment report before any action
- **Command**: Read `output/{date}/invest-report-{date}.md`

### 5. Translation
- **Agent**: `@translator`
- **Task**: Translate final reviewed report to Korean
- **Translation**: `@translator` -> invest-report-{date}-ko.md
- **Output**: Korean language investment report
```

---

## Branch 2.2: BIG BANG Orchestration (Full CLI from Day 1)

### Philosophy

Build the complete Python CLI upfront with all planned subcommands, checkpoint/resume, config management, structured logging, and health checks. Accept the higher upfront cost for a more robust system from the start. This front-loads design decisions but avoids the migration tax.

---

### Full Click CLI (`investscan/`)

**Project structure**:

```
01.invest_test/
├── investscan/
│   ├── __init__.py
│   ├── __main__.py          # Entry point: python -m investscan
│   ├── cli.py               # Click CLI definitions
│   ├── config.py            # Configuration management
│   ├── pipeline.py          # Pipeline engine (step execution, checkpointing)
│   ├── steps/
│   │   ├── __init__.py
│   │   ├── base.py          # Abstract PipelineStep
│   │   ├── envscan.py       # Step: run EnvironmentScan
│   │   ├── globalnews.py    # Step: run GlobalNews
│   │   ├── normalize.py     # Step: signal normalization
│   │   ├── synthesize.py    # Step: investment synthesis
│   │   └── report.py        # Step: report generation
│   ├── health.py            # Pre-flight health checks
│   ├── journal.py           # Decision journal management
│   └── state.py             # Pipeline state / checkpoint management
├── invest_pipeline/          # Business logic (same as Branch 2.1)
│   ├── normalize_signals.py
│   ├── synthesize_investment.py
│   ├── generate_report.py
│   ├── schema.py
│   ├── config.py
│   └── ...
├── config/
│   ├── pipeline.yaml        # Path configs, timeouts, retry policies
│   ├── sectors.yaml
│   └── korean_market.yaml
└── journal/
    └── decisions.jsonl       # Append-only decision log
```

**`investscan/__main__.py`**:

```python
"""Entry point: python -m investscan"""
from investscan.cli import cli

if __name__ == "__main__":
    cli()
```

**`investscan/config.py`**:

```python
"""Configuration management with YAML loading and validation."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class StepConfig:
    """Configuration for a single pipeline step."""
    timeout: int = 10800       # seconds
    retries: int = 0           # 0 = no retry
    retry_delay: int = 60      # seconds between retries
    enabled: bool = True


@dataclass
class Config:
    """Master configuration loaded from config/pipeline.yaml."""

    # Paths
    project_root: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    envscan_root: Optional[Path] = None
    gnews_root: Optional[Path] = None
    output_base: Optional[Path] = None
    log_dir: Optional[Path] = None
    journal_dir: Optional[Path] = None

    # Step-specific configs
    steps: dict[str, StepConfig] = field(default_factory=dict)

    # Behavior
    parallel_collection: bool = False  # EnvScan + GlobalNews in parallel
    stop_on_failure: bool = True       # Halt pipeline on step failure

    def __post_init__(self):
        self.envscan_root = self.envscan_root or (
            self.project_root.parent / "EnvironmentScan-system-main-v4-main"
        )
        self.gnews_root = self.gnews_root or (
            self.project_root.parent / "GlobalNews-Crawling-AgenticWorkflow"
        )
        self.output_base = self.output_base or self.project_root / "output"
        self.log_dir = self.log_dir or self.project_root / "logs"
        self.journal_dir = self.journal_dir or self.project_root / "journal"

        # Default step configs
        defaults = {
            "envscan":    StepConfig(timeout=9000, retries=1, retry_delay=120),
            "globalnews": StepConfig(timeout=7200, retries=1, retry_delay=60),
            "normalize":  StepConfig(timeout=300,  retries=0),
            "synthesize": StepConfig(timeout=600,  retries=0),
            "report":     StepConfig(timeout=600,  retries=0),
        }
        for name, default in defaults.items():
            if name not in self.steps:
                self.steps[name] = default

    def output_dir(self, run_date: str) -> Path:
        return self.output_base / run_date

    @classmethod
    def load(cls, path: Optional[Path] = None) -> Config:
        """Load from YAML file with environment variable overrides."""
        if path is None:
            path = Path(__file__).parent.parent / "config" / "pipeline.yaml"

        data = {}
        if path.exists():
            with open(path) as f:
                data = yaml.safe_load(f) or {}

        # Environment variable overrides (for CI/cron)
        env_overrides = {
            "INVESTSCAN_ENVSCAN_ROOT": "envscan_root",
            "INVESTSCAN_GNEWS_ROOT": "gnews_root",
            "INVESTSCAN_OUTPUT": "output_base",
        }
        for env_var, config_key in env_overrides.items():
            if env_var in os.environ:
                data[config_key] = os.environ[env_var]

        # Convert string paths to Path objects
        path_fields = ["project_root", "envscan_root", "gnews_root", "output_base", "log_dir"]
        for pf in path_fields:
            if pf in data and data[pf] is not None:
                data[pf] = Path(data[pf])

        # Parse step configs
        step_data = data.pop("steps", {})
        config = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        for step_name, step_vals in step_data.items():
            config.steps[step_name] = StepConfig(**step_vals)

        return config
```

**`investscan/state.py`**:

```python
"""Pipeline state management with checkpoint/resume support."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StepState:
    name: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    elapsed_seconds: float = 0.0
    attempt: int = 0
    error: Optional[str] = None
    output_files: list[str] = field(default_factory=list)

    def mark_running(self):
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now().isoformat()
        self.attempt += 1

    def mark_completed(self, output_files: list[Path] = None):
        self.status = StepStatus.COMPLETED
        self.finished_at = datetime.now().isoformat()
        if output_files:
            self.output_files = [str(f) for f in output_files]

    def mark_failed(self, error: str):
        self.status = StepStatus.FAILED
        self.finished_at = datetime.now().isoformat()
        self.error = error


@dataclass
class PipelineState:
    run_date: str
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    finished_at: Optional[str] = None
    overall_status: str = "pending"
    steps: dict[str, StepState] = field(default_factory=dict)

    # Metadata
    config_hash: Optional[str] = None   # Detect config changes between resume
    investscan_version: str = "0.1.0"

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        # Convert enums to strings
        for step_name, step_data in data["steps"].items():
            if isinstance(step_data.get("status"), StepStatus):
                step_data["status"] = step_data["status"].value
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load(cls, path: Path) -> Optional[PipelineState]:
        if not path.exists():
            return None
        with open(path) as f:
            data = json.load(f)
        # Reconstruct StepState objects
        steps_raw = data.pop("steps", {})
        state = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        for name, sdata in steps_raw.items():
            sdata["status"] = StepStatus(sdata.get("status", "pending"))
            state.steps[name] = StepState(**sdata)
        return state

    def is_step_done(self, name: str) -> bool:
        s = self.steps.get(name)
        return s is not None and s.status == StepStatus.COMPLETED

    def all_completed(self) -> bool:
        return all(s.status == StepStatus.COMPLETED for s in self.steps.values())

    def first_failure(self) -> Optional[str]:
        for name, s in self.steps.items():
            if s.status == StepStatus.FAILED:
                return name
        return None
```

**`investscan/steps/base.py`**:

```python
"""Abstract base class for pipeline steps."""
from __future__ import annotations

import logging
import subprocess
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from investscan.config import Config, StepConfig
from investscan.state import PipelineState, StepState, StepStatus

logger = logging.getLogger("investscan")


class PipelineStep(ABC):
    """Base class for all pipeline steps."""

    def __init__(self, config: Config, run_date: str, output_dir: Path):
        self.config = config
        self.run_date = run_date
        self.output_dir = output_dir
        self.step_config: StepConfig = config.steps.get(
            self.name, StepConfig()
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique step identifier."""

    @abstractmethod
    def build_command(self) -> tuple[list[str], Path]:
        """Return (command_args, working_directory)."""

    def expected_outputs(self) -> list[Path]:
        """Files that must exist after successful completion."""
        return []

    def pre_check(self) -> Optional[str]:
        """Return error message if step cannot run, None if OK."""
        return None

    def execute(
        self,
        state: PipelineState,
        state_path: Path,
        log_file: Path,
        resume: bool = False,
    ) -> StepState:
        """Execute this step with full lifecycle management."""

        step_state = state.steps.get(self.name, StepState(name=self.name))

        # Resume: skip completed
        if resume and step_state.status == StepStatus.COMPLETED:
            logger.info(f"[SKIP] {self.name} (resume -- already completed)")
            return step_state

        # Disabled: skip
        if not self.step_config.enabled:
            step_state.status = StepStatus.SKIPPED
            logger.info(f"[SKIP] {self.name} (disabled in config)")
            state.steps[self.name] = step_state
            state.save(state_path)
            return step_state

        # Pre-check
        pre_error = self.pre_check()
        if pre_error:
            step_state.mark_failed(f"Pre-check failed: {pre_error}")
            state.steps[self.name] = step_state
            state.save(state_path)
            return step_state

        # Execute with retry
        max_attempts = 1 + self.step_config.retries
        cmd, cwd = self.build_command()

        for attempt in range(max_attempts):
            step_state.mark_running()
            state.steps[self.name] = step_state
            state.save(state_path)

            logger.info(f"[START] {self.name} (attempt {attempt + 1}/{max_attempts})")
            start = time.monotonic()

            try:
                with open(log_file, "a") as lf:
                    lf.write(f"\n{'='*60}\n[{self.name}] attempt {attempt+1} at {step_state.started_at}\n{'='*60}\n")
                    proc = subprocess.run(
                        cmd,
                        cwd=str(cwd),
                        stdout=lf,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=self.step_config.timeout,
                    )

                elapsed = time.monotonic() - start
                step_state.elapsed_seconds = elapsed

                if proc.returncode != 0:
                    error = proc.stderr[:2000] if proc.stderr else f"Exit code {proc.returncode}"
                    logger.warning(f"[FAIL] {self.name} after {elapsed:.0f}s (attempt {attempt+1}): {error[:200]}")

                    if attempt < max_attempts - 1:
                        logger.info(f"  Retrying in {self.step_config.retry_delay}s...")
                        time.sleep(self.step_config.retry_delay)
                        continue
                    else:
                        step_state.mark_failed(error)
                else:
                    # Validate outputs
                    expected = self.expected_outputs()
                    missing = [f for f in expected if not f.exists() or f.stat().st_size == 0]
                    if missing:
                        error = f"Missing outputs: {[str(m) for m in missing]}"
                        if attempt < max_attempts - 1:
                            logger.warning(f"  {error}. Retrying...")
                            time.sleep(self.step_config.retry_delay)
                            continue
                        step_state.mark_failed(error)
                    else:
                        step_state.mark_completed(expected)
                        logger.info(f"[DONE] {self.name} in {elapsed:.0f}s")

                break  # Success or final failure

            except subprocess.TimeoutExpired:
                step_state.elapsed_seconds = self.step_config.timeout
                if attempt < max_attempts - 1:
                    logger.warning(f"[TIMEOUT] {self.name}. Retrying...")
                    time.sleep(self.step_config.retry_delay)
                    continue
                step_state.mark_failed(f"Timeout after {self.step_config.timeout}s")
                break

            except Exception as e:
                step_state.elapsed_seconds = time.monotonic() - start
                step_state.mark_failed(str(e))
                break

        state.steps[self.name] = step_state
        state.save(state_path)
        return step_state
```

**`investscan/steps/envscan.py`** (example concrete step):

```python
"""EnvironmentScan pipeline step."""
from pathlib import Path
from typing import Optional

from investscan.config import Config
from investscan.steps.base import PipelineStep


class EnvScanStep(PipelineStep):
    @property
    def name(self) -> str:
        return "envscan"

    def pre_check(self) -> Optional[str]:
        if not self.config.envscan_root.is_dir():
            return f"EnvScan root not found: {self.config.envscan_root}"
        # Check for entry point
        orch = self.config.envscan_root / "env-scanning" / "orchestrator.py"
        alt = self.config.envscan_root / "run_scan.py"
        if not orch.exists() and not alt.exists():
            # Check if stale signals exist (graceful degradation)
            signals = self.config.envscan_root / "env-scanning" / "signals" / "database.json"
            if signals.exists():
                return None  # Will use stale signals
            return f"No EnvScan entry point found in {self.config.envscan_root}"
        return None

    def build_command(self) -> tuple[list[str], Path]:
        orch = self.config.envscan_root / "env-scanning" / "orchestrator.py"
        if orch.exists():
            return (
                ["python", str(orch), "--mode", "quad", "--date", self.run_date],
                self.config.envscan_root,
            )
        return (
            ["python", "run_scan.py", "--quad", "--date", self.run_date],
            self.config.envscan_root,
        )
```

**`investscan/health.py`**:

```python
"""Pre-flight health checks for the InvestScan pipeline."""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from investscan.config import Config


@dataclass
class HealthReport:
    checks: list[tuple[str, bool, str]]  # (name, passed, detail)

    @property
    def all_passed(self) -> bool:
        return all(passed for _, passed, _ in self.checks)

    def summary(self) -> str:
        lines = []
        for name, passed, detail in self.checks:
            icon = "[OK]" if passed else "[FAIL]"
            lines.append(f"  {icon} {name}: {detail}")
        return "\n".join(lines)


def run_health_checks(config: Config) -> HealthReport:
    """Run all pre-flight health checks."""
    checks = []

    # 1. EnvScan directory
    exists = config.envscan_root.is_dir()
    checks.append((
        "EnvScan directory",
        exists,
        str(config.envscan_root) if exists else f"NOT FOUND: {config.envscan_root}",
    ))

    # 2. GlobalNews directory
    exists = config.gnews_root.is_dir()
    checks.append((
        "GlobalNews directory",
        exists,
        str(config.gnews_root) if exists else f"NOT FOUND: {config.gnews_root}",
    ))

    # 3. GlobalNews venv
    gnews_python = config.gnews_root / ".venv" / "bin" / "python"
    exists = gnews_python.exists()
    checks.append((
        "GlobalNews Python venv",
        exists,
        str(gnews_python) if exists else "NOT FOUND",
    ))

    # 4. Disk space (need 2GB free)
    usage = shutil.disk_usage(str(config.project_root))
    free_gb = usage.free / (1024 ** 3)
    checks.append((
        "Disk space",
        free_gb > 2.0,
        f"{free_gb:.1f} GB free",
    ))

    # 5. Config file
    config_path = config.project_root / "config" / "pipeline.yaml"
    checks.append((
        "Config file",
        config_path.exists(),
        str(config_path) if config_path.exists() else "Using defaults (no pipeline.yaml)",
    ))

    # 6. Output directory writable
    try:
        test_dir = config.output_base / ".health_check"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / "test"
        test_file.write_text("ok")
        test_file.unlink()
        test_dir.rmdir()
        checks.append(("Output writable", True, str(config.output_base)))
    except Exception as e:
        checks.append(("Output writable", False, str(e)))

    # 7. Recent EnvScan signals (within 48 hours)
    signals_db = config.envscan_root / "env-scanning" / "signals" / "database.json"
    if signals_db.exists():
        import time
        age_hours = (time.time() - signals_db.stat().st_mtime) / 3600
        checks.append((
            "EnvScan signals freshness",
            age_hours < 48,
            f"{age_hours:.1f} hours old",
        ))
    else:
        checks.append(("EnvScan signals freshness", False, "No signals database found"))

    return HealthReport(checks=checks)
```

**`investscan/journal.py`**:

```python
"""Decision journal for tracking investment reasoning over time."""
from __future__ import annotations

import json
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class JournalEntry:
    date: str
    category: str          # "signal_override" | "sector_adjustment" | "conviction_note" | "methodology"
    title: str
    body: str
    related_signals: list[str] = None  # Signal IDs
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.related_signals is None:
            self.related_signals = []


class Journal:
    """Append-only decision journal (JSONL format)."""

    def __init__(self, journal_dir: Path):
        self.journal_dir = journal_dir
        self.journal_file = journal_dir / "decisions.jsonl"
        self.journal_dir.mkdir(parents=True, exist_ok=True)

    def add(self, entry: JournalEntry):
        with open(self.journal_file, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")

    def list_entries(self, limit: int = 20, category: Optional[str] = None) -> list[JournalEntry]:
        if not self.journal_file.exists():
            return []
        entries = []
        with open(self.journal_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                entry = JournalEntry(**data)
                if category and entry.category != category:
                    continue
                entries.append(entry)
        return entries[-limit:]

    def search(self, query: str) -> list[JournalEntry]:
        query_lower = query.lower()
        return [
            e for e in self.list_entries(limit=1000)
            if query_lower in e.title.lower() or query_lower in e.body.lower()
        ]
```

**`investscan/cli.py`** (Full Big Bang CLI):

```python
"""
InvestScan CLI -- Full-featured pipeline orchestrator.

Usage:
    python -m investscan run --date 2026-03-27
    python -m investscan run --resume
    python -m investscan status
    python -m investscan report --date 2026-03-27 --format md
    python -m investscan journal add --title "Override: bearish semiconductors"
    python -m investscan journal list
    python -m investscan health
"""
from __future__ import annotations

import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import click

from investscan.config import Config
from investscan.state import PipelineState, StepStatus
from investscan.health import run_health_checks
from investscan.journal import Journal, JournalEntry
from investscan.steps.envscan import EnvScanStep
from investscan.steps.globalnews import GlobalNewsStep
from investscan.steps.normalize import NormalizeStep
from investscan.steps.synthesize import SynthesizeStep
from investscan.steps.report import ReportStep

logger = logging.getLogger("investscan")


def setup_logging(log_file: Path, verbose: bool = False):
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file),
    ]
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        handlers=handlers,
    )


@click.group()
@click.option("--config", "config_path", default=None, type=click.Path(exists=False),
              help="Path to pipeline.yaml")
@click.option("--verbose", is_flag=True, help="Enable debug logging")
@click.pass_context
def cli(ctx, config_path: Optional[str], verbose: bool):
    """InvestScan -- Investment Signal Pipeline Orchestrator."""
    ctx.ensure_object(dict)
    path = Path(config_path) if config_path else None
    ctx.obj["config"] = Config.load(path)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("--date", "run_date", default=None, help="YYYY-MM-DD (default: today)")
@click.option("--resume", is_flag=True, help="Skip already-completed steps")
@click.option("--step", type=click.Choice(["envscan", "globalnews", "normalize", "synthesize", "report"]),
              default=None, help="Run single step only")
@click.option("--skip-collection", is_flag=True, help="Skip EnvScan + GlobalNews (use existing data)")
@click.pass_context
def run(ctx, run_date: Optional[str], resume: bool, step: Optional[str], skip_collection: bool):
    """Run the InvestScan pipeline."""
    config: Config = ctx.obj["config"]
    run_date = run_date or date.today().isoformat()

    output_dir = config.output_dir(run_date)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_file = config.log_dir / f"investscan-{run_date}.log"
    state_path = output_dir / "pipeline_state.json"

    setup_logging(log_file, ctx.obj.get("verbose", False))

    # Pre-flight health check
    if not resume:
        health = run_health_checks(config)
        if not health.all_passed:
            logger.warning("Health check warnings:")
            click.echo(health.summary())
            # Non-blocking: log but continue (some checks are advisory)

    # Load or create state
    if resume:
        state = PipelineState.load(state_path)
        if state is None:
            logger.info("No previous state found. Starting fresh.")
            state = PipelineState(run_date=run_date)
        else:
            logger.info(f"Resuming from: {state.overall_status}")
            failed = state.first_failure()
            if failed:
                logger.info(f"Previous failure at: {failed}")
    else:
        state = PipelineState(run_date=run_date)

    state.overall_status = "running"
    state.save(state_path)

    # Build step instances
    all_steps = [
        EnvScanStep(config, run_date, output_dir),
        GlobalNewsStep(config, run_date, output_dir),
        NormalizeStep(config, run_date, output_dir),
        SynthesizeStep(config, run_date, output_dir),
        ReportStep(config, run_date, output_dir),
    ]

    # Filter steps
    if step:
        all_steps = [s for s in all_steps if s.name == step]
    elif skip_collection:
        all_steps = [s for s in all_steps if s.name not in ("envscan", "globalnews")]

    # Execute
    logger.info(f"{'='*60}")
    logger.info(f"InvestScan Pipeline -- {run_date}")
    logger.info(f"Steps: {[s.name for s in all_steps]}")
    logger.info(f"Resume: {resume}")
    logger.info(f"{'='*60}")

    failed = False
    for pipeline_step in all_steps:
        result = pipeline_step.execute(
            state=state,
            state_path=state_path,
            log_file=log_file,
            resume=resume,
        )
        if result.status == StepStatus.FAILED:
            failed = True
            state.overall_status = f"failed:{pipeline_step.name}"
            state.finished_at = datetime.now().isoformat()
            state.save(state_path)
            logger.error(f"Pipeline halted at {pipeline_step.name}")
            logger.error(f"Fix the issue and run: python -m investscan run --date {run_date} --resume")
            sys.exit(1)

    if not failed:
        state.overall_status = "completed"
        state.finished_at = datetime.now().isoformat()
        state.save(state_path)
        logger.info(f"{'='*60}")
        logger.info("Pipeline completed successfully")
        report_path = output_dir / f"invest-report-{run_date}.md"
        if report_path.exists():
            logger.info(f"Report: {report_path}")
        logger.info(f"{'='*60}")


@cli.command()
@click.option("--date", "run_date", default=None, help="YYYY-MM-DD (default: latest)")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def status(ctx, run_date: Optional[str], as_json: bool):
    """Show pipeline status for a given date."""
    config: Config = ctx.obj["config"]

    if run_date is None:
        output_dirs = sorted(config.output_base.glob("????-??-??"), reverse=True)
        if not output_dirs:
            click.echo("No pipeline runs found.")
            return
        run_date = output_dirs[0].name

    state_path = config.output_dir(run_date) / "pipeline_state.json"
    state = PipelineState.load(state_path)

    if state is None:
        click.echo(f"No pipeline state for {run_date}")
        return

    if as_json:
        import json
        from dataclasses import asdict
        click.echo(json.dumps(asdict(state), indent=2, default=str))
        return

    click.echo(f"\n{'='*55}")
    click.echo(f" InvestScan Pipeline Status: {run_date}")
    click.echo(f"{'='*55}")
    click.echo(f" Status:  {state.overall_status}")
    click.echo(f" Started: {state.started_at}")
    if state.finished_at:
        click.echo(f" Ended:   {state.finished_at}")
    click.echo(f"{'─'*55}")

    step_order = ["envscan", "globalnews", "normalize", "synthesize", "report"]
    for name in step_order:
        s = state.steps.get(name)
        if s is None:
            click.echo(f"  [--]   {name:15s}  not started")
            continue

        icon_map = {
            StepStatus.COMPLETED: "[OK]  ",
            StepStatus.FAILED:    "[FAIL]",
            StepStatus.RUNNING:   "[... ]",
            StepStatus.SKIPPED:   "[SKIP]",
            StepStatus.PENDING:   "[--]  ",
        }
        icon = icon_map.get(s.status, "[??]  ")
        elapsed = f"{s.elapsed_seconds:.0f}s" if s.elapsed_seconds else "--"
        attempts = f" (attempt {s.attempt})" if s.attempt > 1 else ""
        click.echo(f"  {icon} {name:15s}  {elapsed:>8s}{attempts}")

        if s.error:
            click.echo(f"         Error: {s.error[:80]}")

    click.echo(f"{'='*55}\n")


@cli.command()
@click.option("--date", "run_date", required=True, help="YYYY-MM-DD")
@click.option("--format", "fmt", default="md", type=click.Choice(["md", "json"]))
@click.pass_context
def report(ctx, run_date: str, fmt: str):
    """Regenerate report from existing synthesis data."""
    config: Config = ctx.obj["config"]
    synthesis_file = config.output_dir(run_date) / "investment_synthesis.json"

    if not synthesis_file.exists():
        click.echo(f"No synthesis data for {run_date}. Run the full pipeline first.")
        sys.exit(1)

    click.echo(f"Regenerating report for {run_date}...")
    ctx.invoke(run, run_date=run_date, resume=False, step="report")


@cli.command()
@click.pass_context
def health(ctx):
    """Run pre-flight health checks."""
    config: Config = ctx.obj["config"]
    report = run_health_checks(config)

    click.echo(f"\n{'='*50}")
    click.echo(" InvestScan Health Check")
    click.echo(f"{'='*50}")
    click.echo(report.summary())
    click.echo()

    if report.all_passed:
        click.echo("All checks passed. Pipeline is ready to run.")
    else:
        click.echo("Some checks failed. Review before running pipeline.")
        sys.exit(1)


# ── Journal subcommand group ───────────────────────────────

@cli.group()
@click.pass_context
def journal(ctx):
    """Manage the investment decision journal."""
    pass


@journal.command("add")
@click.option("--date", "entry_date", default=None, help="YYYY-MM-DD (default: today)")
@click.option("--category", type=click.Choice([
    "signal_override", "sector_adjustment", "conviction_note", "methodology",
]), required=True)
@click.option("--title", required=True, help="Brief title")
@click.option("--body", required=True, help="Full reasoning")
@click.option("--signals", multiple=True, help="Related signal IDs")
@click.pass_context
def journal_add(ctx, entry_date, category, title, body, signals):
    """Add a decision journal entry."""
    config: Config = ctx.obj["config"]
    j = Journal(config.journal_dir)
    entry = JournalEntry(
        date=entry_date or date.today().isoformat(),
        category=category,
        title=title,
        body=body,
        related_signals=list(signals),
    )
    j.add(entry)
    click.echo(f"Journal entry added: [{category}] {title}")


@journal.command("list")
@click.option("--limit", default=20, help="Number of entries to show")
@click.option("--category", default=None, help="Filter by category")
@click.pass_context
def journal_list(ctx, limit, category):
    """List recent journal entries."""
    config: Config = ctx.obj["config"]
    j = Journal(config.journal_dir)
    entries = j.list_entries(limit=limit, category=category)

    if not entries:
        click.echo("No journal entries found.")
        return

    for e in entries:
        click.echo(f"[{e.date}] [{e.category}] {e.title}")
        click.echo(f"  {e.body[:100]}{'...' if len(e.body) > 100 else ''}")
        if e.related_signals:
            click.echo(f"  Signals: {', '.join(e.related_signals)}")
        click.echo()


@journal.command("search")
@click.argument("query")
@click.pass_context
def journal_search(ctx, query):
    """Search journal entries."""
    config: Config = ctx.obj["config"]
    j = Journal(config.journal_dir)
    entries = j.search(query)

    if not entries:
        click.echo(f"No entries matching '{query}'")
        return

    click.echo(f"Found {len(entries)} entries:")
    for e in entries:
        click.echo(f"  [{e.date}] [{e.category}] {e.title}")
```

**LOC for Big Bang approach**:

| File | LOC |
|------|-----|
| `__main__.py` | 4 |
| `config.py` | 95 |
| `state.py` | 110 |
| `steps/base.py` | 115 |
| `steps/envscan.py` | 40 |
| `steps/globalnews.py` | 35 |
| `steps/normalize.py` | 35 |
| `steps/synthesize.py` | 35 |
| `steps/report.py` | 40 |
| `health.py` | 75 |
| `journal.py` | 65 |
| `cli.py` | 230 |
| **Total orchestration** | **~880** |

---

### workflow.md Integration (Big Bang)

```markdown
# InvestScan Daily Investment Signal Pipeline

Automated investment intelligence synthesis integrating EnvironmentScan (17+ sources,
LLM-driven analysis) with GlobalNews-Crawling (116 sites, 56 NLP techniques) into
actionable Korean market investment direction reports.

## Overview

- **Input**: Raw signals from EnvScan + GlobalNews upstream systems
- **Output**: Investment direction report (EN + KO) with sector heat map, evidence chains
- **Frequency**: daily (6:00 AM KST via launchd)
- **Autopilot**: enabled
- **pACS**: enabled
- **CLI**: `python -m investscan run --date YYYY-MM-DD`

---

## Inherited DNA (Parent Genome)

> This workflow inherits the complete genome of AgenticWorkflow.
> Purpose varies by domain; the genome is identical. See `soul.md S0`.

**Constitutional Principles** (adapted to investment intelligence):

1. **Quality Absolutism** -- Every directional call must have traceable evidence chains.
   No signal without provenance. No conviction without corroboration. A wrong investment
   direction is worse than no direction at all.
2. **Single-File SOT** -- `output/{date}/pipeline_state.json` is the sole state file per run.
   `config/pipeline.yaml` is the sole configuration source. No shadow state.
3. **Code Change Protocol** -- Modifications to `invest_pipeline/` or `investscan/` follow
   CCP 3-step. Sector mapping rules are especially sensitive (impact propagates to all reports).

**Inherited Patterns**:

| DNA Component | Inherited Form |
|--------------|---------------|
| 3-Phase Structure | Collection -> Normalization+Synthesis -> Report+Review |
| SOT Pattern | `pipeline_state.json` per run, `pipeline.yaml` for config |
| 4-Layer QA | L0: pre-flight health -> L1: output validation -> L1.5: signal quality -> L2: adversarial review |
| P1 Hallucination Prevention | Output validation in every step (file existence, non-empty, schema conformance) |
| P2 Expert Delegation | 5-step pipeline, each step is a specialized module |
| Safety Hooks | `health.py` pre-flight, exit-code propagation, checkpoint/resume |
| Decision Log | `journal/decisions.jsonl` for investment reasoning |

**Domain-Specific Gene Expression**:
P1 (Data Precision) is the **dominant gene**. Financial signals have zero tolerance for
hallucination. Every directional claim must trace to a specific source signal with a specific
detection date. P2 (Expert Delegation) expresses as the 5-step sequential pipeline with
per-step specialization. Safety DNA expresses as the checkpoint/resume architecture -- never
lose 3.5 hours of upstream computation to a downstream failure.

---

## Research

### 1. Health Check + Pre-flight Validation
- **Agent**: Orchestrator
- **Verification**:
  - [ ] `python -m investscan health` reports all checks passed
  - [ ] EnvScan signals database exists and is < 48 hours old
  - [ ] GlobalNews .venv is functional
  - [ ] Disk space > 2GB free
  - [ ] Previous run's `pipeline_state.json` reviewed (if failed run exists)
- **Task**: Validate all upstream dependencies before committing compute time
- **Output**: Health check pass (logged) or specific failure messages
- **Translation**: none

### 2. Data Collection -- EnvironmentScan
- **Agent**: Orchestrator (delegates to EnvScan's internal orchestrator)
- **Verification**:
  - [ ] `pipeline_state.json` step "envscan" status = "completed"
  - [ ] `env-scanning/signals/database.json` updated with today's date
  - [ ] At least 4 workflow tracks (WF1-WF4) produced output
- **Task**: Execute EnvironmentScan quad scan (arXiv, RSS, Naver, MultiGlobal)
- **Output**: Updated signal database + daily markdown reports
- **Translation**: none

### 3. Data Collection -- GlobalNews
- **Agent**: Orchestrator (delegates to GlobalNews CLI)
- **Verification**:
  - [ ] `pipeline_state.json` step "globalnews" status = "completed"
  - [ ] `data/output/signals.parquet` exists and has rows for today
  - [ ] 8-stage analysis pipeline completed (check stage 8 output)
- **Task**: Execute GlobalNews full crawl + 8-stage analysis pipeline
- **Output**: Parquet signals + SQLite index + DuckDB verification
- **Translation**: none

---

## Planning

### 4. Signal Normalization
- **Pre-processing**: Schema validation of both upstream outputs (JSON + Parquet)
- **Agent**: Orchestrator
- **Verification**:
  - [ ] `unified_signals.json` contains signals from BOTH sources
  - [ ] Signal count > 50 (typical: 500+ EnvScan + GlobalNews combined)
  - [ ] All signals have both STEEPs category AND signal layer assigned
  - [ ] Confidence scores normalized to 0.0-1.0 range
  - [ ] No duplicate signals (cross-source dedup by title similarity)
- **Task**: Read EnvScan JSON + GlobalNews Parquet, harmonize into UnifiedSignal schema
- **Output**: `output/{date}/unified_signals.json`
- **Translation**: none

### 5. Investment Synthesis
- **Pre-processing**: Load sector mapping rules from `config/sectors.yaml`
- **Agent**: Orchestrator
- **Verification**:
  - [ ] Every directional call (bull/bear) links to >= 2 source signals
  - [ ] Conviction levels follow conservative thresholds (no "high" without 3+ corroborations)
  - [ ] GICS sector assignments are plausible for signal content
  - [ ] Korean market relevance scores are populated
  - [ ] Pipeline connection: unified_signals.json signal_ids appear in evidence chains
- **Task**: Map signals to sectors, compute directional conviction, build evidence chains
- **Output**: `output/{date}/investment_synthesis.json`
- **Translation**: none

### 6. (human) Signal Override Review
- **Action**: Review synthesis output. Add journal entries for any manual overrides.
- **Command**: `python -m investscan journal add --category signal_override --title "..." --body "..."`

---

## Implementation

### 7. Report Generation
- **Agent**: Orchestrator
- **Verification**:
  - [ ] Report contains all GICS sectors with non-zero signal count
  - [ ] Sector heat map is present (or text equivalent if visualization disabled)
  - [ ] Evidence trail section links every direction to specific signals
  - [ ] Multi-horizon synthesis (short/mid/long) is populated
  - [ ] Report size > 5KB (non-trivial content)
  - [ ] Cross-step traceability: signal IDs in report trace back to unified_signals.json
- **Task**: Generate markdown investment report with sector analysis and evidence chains
- **Output**: `output/{date}/invest-report-{date}.md`
- **Translation**: `@translator` -> `invest-report-{date}-ko.md`
- **Post-processing**: `@reviewer` adversarial review of report quality

### 8. Report Quality Gate
- **Agent**: `@reviewer`
- **Verification**:
  - [ ] No hallucinated source names (every source in report exists in upstream data)
  - [ ] No contradictory directional calls within same sector
  - [ ] Uncertainty language present for low-conviction calls (< 0.5)
  - [ ] No actionable "buy/sell" language (InvestScan provides direction signals, not trading advice)
- **Task**: Independent adversarial review of the generated investment report
- **Output**: Review pass/fail with specific issues

### 9. (human) Final Review + Decision Journal
- **Action**: Review final report. Record investment reasoning in decision journal.
- **Command**: `python -m investscan journal add --category conviction_note --title "..." --body "..."`

---

## Claude Code Configuration

### Sub-agents

```yaml
# .claude/agents/investscan-reviewer.md
---
name: investscan-reviewer
description: "Review investment signal reports for accuracy and evidence quality"
model: opus
tools: Read,Grep,Glob
maxTurns: 10
memory: project
---

You are an adversarial reviewer for InvestScan investment direction reports.
Your job is to find:
1. Claims without evidence chains (signal IDs must trace to source)
2. Contradictions within the same sector
3. Implausible sector mappings (e.g., a food safety signal mapped to semiconductor sector)
4. Missing uncertainty language for low-conviction calls
5. Any language that could be construed as investment advice (we provide signals, not advice)

Be thorough. Flag everything. False negatives are worse than false positives.
```

### Scheduling (launchd)

```xml
<!-- ~/Library/LaunchAgents/com.investscan.daily.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.investscan.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>python3</string>
        <string>-m</string>
        <string>investscan</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>6</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/kylechoi/Desktop/Ai_works/Vibe-Practice/01.invest_test/logs/launchd-stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
```
```

---

## COMPARISON

### Quantitative Metrics

| Metric | Branch 2.1 (Evolutionary) | Branch 2.2 (Big Bang) |
|--------|--------------------------|----------------------|
| **LOC at Month 1** | 140 (run.sh only) | 880 (full CLI framework) |
| **LOC at Month 4** | ~350 (cli.py replaces run.sh) | 880 (same -- already built) |
| **Time to first working pipeline** | **2-3 hours** (write run.sh, test manually) | **2-3 days** (config, state, steps, CLI, health) |
| **Time to checkpoint/resume** | Month 3 (when cli.py is built) | **Day 1** |
| **Time to health checks** | Month 3 | **Day 1** |
| **Time to decision journal** | Month 4+ (if ever) | **Day 1** |
| **Files created** | 1 (run.sh) -> 2 (+ cli.py) -> delete run.sh | 12 files from start |
| **Dependencies** | None (Month 1) -> click, pyyaml (Month 3) | click, pyyaml from day 1 |
| **Migration cost** | ~1 week to port run.sh -> cli.py | $0 (no migration) |
| **Risk of "good enough" trap** | HIGH -- run.sh works, migration gets deprioritized | None |

### Qualitative Assessment

| Dimension | Branch 2.1 (Evolutionary) | Branch 2.2 (Big Bang) |
|-----------|--------------------------|----------------------|
| **First pipeline run** | Faster: shell script works in hours | Slower: must build framework first |
| **Robustness** | LOW initially (no resume, no retry) | HIGH from day 1 (resume, retry, health) |
| **Debugging** | Harder (shell error messages, no structured state) | Easier (pipeline_state.json, structured logs) |
| **workflow.md integration** | Simple initially (just bash calls), refactored later | Well-structured from start (step-level granularity) |
| **Solo dev cognitive load** | LOW initially, spike during migration | MEDIUM sustained (more code to maintain) |
| **Failure recovery** | Manual: re-run entire 4hr pipeline | Automatic: `--resume` skips completed steps |
| **cron/launchd readiness** | Month 6 (after hardening) | Month 1 (designed for unattended execution) |

### Risk Analysis

| Risk | Branch 2.1 | Branch 2.2 |
|------|-----------|-----------|
| Pipeline fails at Step 4 after 3.5hr | **Must re-run from scratch** (no checkpoint until Month 3) | **Resume from Step 4** (checkpoint from day 1) |
| EnvScan changes its output format | Shell script breaks silently (grep/jq) | Health check detects schema mismatch pre-run |
| run.sh works "well enough" and cli.py migration never happens | **LIKELY** -- this is the #1 risk of evolutionary approach | N/A |
| Over-engineering the CLI before business logic exists | N/A | **POSSIBLE** -- 880 LOC of orchestration before a single signal is normalized |
| Cron job fails silently at 6 AM | No structured error reporting until Month 3 | `pipeline_state.json` + log files from day 1 |

### The Critical Question: When Does the Upstream Pipeline ACTUALLY Fail?

The entire value of checkpoint/resume depends on *how often* the pipeline fails partway through.

- **Month 1-2**: You are debugging `normalize_signals.py` and `synthesize_investment.py`. These scripts will fail CONSTANTLY during development. The upstream EnvScan/GlobalNews steps succeed (they are mature systems). So the pattern is: 3.5 hours of collection succeed, 5 minutes of new code fails. **Checkpoint/resume is extremely valuable from day 1.**

- **Month 3+**: The new code stabilizes. Failures shift to upstream systems (API outages, site blocks). **Checkpoint/resume remains valuable** because these failures are unpredictable.

This analysis strongly favors **Branch 2.2** for the InvestScan use case specifically.

### VERDICT

| For InvestScan specifically | Recommendation |
|----------------------------|----------------|
| **If prototyping the business logic (normalize, synthesize, report) is the uncertainty** | Branch 2.2 -- you need checkpoint/resume while debugging the new modules |
| **If unsure whether the pipeline concept works at all** | Branch 2.1 -- get a shell script running in 2 hours and validate the concept |
| **Solo dev with cron scheduling requirement** | Branch 2.2 -- unattended execution demands structured error handling from day 1 |
| **If you have exactly 1 day to show a working pipeline** | Branch 2.1 -- ship run.sh, demo it, then build cli.py |

**For InvestScan's actual situation** (known pipeline architecture, 3.5hr upstream cost, cron scheduling, solo dev debugging new Python modules against mature upstream systems): **Branch 2.2 is recommended**. The upfront 2-3 day investment in the CLI framework pays for itself the first time you avoid re-running a 3.5-hour pipeline because `synthesize_investment.py` had a bug.

The one modification: **build the CLI framework in Branch 2.2, but implement the step classes incrementally**. Start with `NormalizeStep`, `SynthesizeStep`, and `ReportStep` as stubs that just call the underlying Python modules. `EnvScanStep` and `GlobalNewsStep` can initially just be subprocess wrappers. This gives you the checkpoint/resume architecture immediately while allowing incremental business logic development.
