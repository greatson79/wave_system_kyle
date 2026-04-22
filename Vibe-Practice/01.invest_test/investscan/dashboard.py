"""
investscan/dashboard.py — Real-time terminal dashboard for InvestScan pipeline.

Mirrors the GlobalNews CLI Monitor visual style — rich.Live full-screen,
bright_blue panels, numbered pipeline circles, horizontal bar charts.

Usage:
    python3 -m investscan.dashboard            # live mode (3s refresh)
    python3 -m investscan.dashboard --once     # one-shot snapshot
    python3 -m investscan.dashboard --watch N  # N-second refresh interval

Data sources (read-only):
    output/temp/pipeline_status.json  — phase/agent execution state
    .claude/state.yaml                — library, TDD, translations
    output/reports/                   — latest report filename
    EnvironmentScan / GlobalNews dirs — data freshness (mtime)
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
STATUS_FILE    = Path("output/temp/pipeline_status.json")
STATE_YAML     = Path(".claude/state.yaml")
REPORTS_DIR    = Path("output/reports")
TEMP_DIR       = Path("output/temp")
ENVSCAN_OUT    = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/EnvironmentScan-system-main-v4-main/output")
GNEWS_RAW_BASE = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/GlobalNews-Crawling-AgenticWorkflow/data/raw")

# ── Phase / Agent config ─────────────────────────────────────────────────────
PHASES_ORDERED = [
    "phase_0", "phase_1_envscan", "phase_1_gnews",
    "phase_2", "phase_3", "phase_4", "phase_5", "phase_6",
]

PHASE_SHORT = {
    "phase_0":         "상태확인",
    "phase_1_envscan": "EnvScan",
    "phase_1_gnews":   "GNews",
    "phase_2":         "컨텍스트",
    "phase_3":         "R1 분석",
    "phase_4":         "R2 토론",
    "phase_5":         "종합",
    "phase_6":         "PDF",
}

AGENT_NAMES = ["macro", "tech", "korea", "valuation", "risk"]

AGENT_LABELS = {
    "macro":     "거시경제",
    "tech":      "기술·AI",
    "korea":     "한국시장",
    "valuation": "밸류에이션",
    "risk":      "리스크",
}

AGENT_COLORS = {
    "macro":     "bright_cyan",
    "tech":      "bright_green",
    "korea":     "bright_yellow",
    "valuation": "bright_magenta",
    "risk":      "bright_red",
}


# ── Data Loaders ──────────────────────────────────────────────────────────────

def _load_pipeline_status() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_state() -> dict:
    if STATE_YAML.exists():
        try:
            return yaml.safe_load(STATE_YAML.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    return {}


def _data_freshness() -> dict:
    result: dict = {}

    wf_files = sorted(ENVSCAN_OUT.glob("WF*.json")) if ENVSCAN_OUT.exists() else []
    if wf_files:
        mtime = datetime.fromtimestamp(wf_files[-1].stat().st_mtime)
        age = (datetime.now() - mtime).days
        result["envscan"] = {"label": wf_files[-1].name[:20], "age_days": age, "ok": age <= 3}
    else:
        result["envscan"] = {"label": "없음", "age_days": None, "ok": False}

    raw_dirs = (
        sorted(GNEWS_RAW_BASE.glob("????-??-??"), reverse=True)
        if GNEWS_RAW_BASE.exists() else []
    )
    if raw_dirs:
        latest = raw_dirs[0]
        age = (date.today() - date.fromisoformat(latest.name)).days
        has = (latest / "all_articles.jsonl").exists()
        result["gnews"] = {"label": latest.name, "age_days": age, "ok": age <= 3 and has}
    else:
        result["gnews"] = {"label": "없음", "age_days": None, "ok": False}

    contexts = sorted(TEMP_DIR.glob("agent_context_*.json")) if TEMP_DIR.exists() else []
    if contexts:
        mtime = datetime.fromtimestamp(contexts[-1].stat().st_mtime)
        age = (datetime.now() - mtime).days
        result["context"] = {"label": contexts[-1].name[:20], "age_days": age, "ok": age == 0}
    else:
        result["context"] = {"label": "없음", "age_days": None, "ok": False}

    return result


def _latest_report() -> Optional[str]:
    if REPORTS_DIR.exists():
        reports = sorted(REPORTS_DIR.glob("weekly-report-*.md"), reverse=True)
        if reports:
            return reports[0].name
    return None


# ── Derived metrics ───────────────────────────────────────────────────────────

def _compute_metrics(ps: dict) -> dict:
    phases = ps.get("phases", {})
    total = len(PHASES_ORDERED)
    done = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") == "completed")
    running = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") == "running")
    failed = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") in ("failed", "partial_failed"))

    agents_total = 0
    agents_done = 0
    agents_running = 0
    for rnd in ("phase_3", "phase_4"):
        ag = phases.get(rnd, {}).get("agents", {})
        agents_total += len(ag)
        agents_done += sum(1 for s in ag.values() if s == "completed")
        agents_running += sum(1 for s in ag.values() if s == "running")

    started = ps.get("started_at")
    if started:
        try:
            elapsed_sec = (datetime.now() - datetime.fromisoformat(started)).total_seconds()
        except Exception:
            elapsed_sec = 0
    else:
        elapsed_sec = 0

    # Total processing time (sum of completed phase durations)
    proc_sec = sum(phases.get(p, {}).get("duration_sec", 0) or 0 for p in PHASES_ORDERED)

    if done > 0 and done < total:
        rate = elapsed_sec / done
        eta_sec = (total - done) * rate
    else:
        eta_sec = 0

    return {
        "phases_total": total,
        "phases_done": done,
        "phases_running": running,
        "phases_failed": failed,
        "agents_total": agents_total,
        "agents_done": agents_done,
        "agents_running": agents_running,
        "elapsed_sec": elapsed_sec,
        "proc_sec": proc_sec,
        "eta_sec": eta_sec,
    }


def _fmt_duration(sec: float) -> str:
    if sec <= 0:
        return "--:--"
    m, s = divmod(int(sec), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ── Panel Builders ────────────────────────────────────────────────────────────

def _build_header(elapsed_sec: float):
    from rich.text import Text
    from rich.table import Table

    t = Table.grid(expand=True)
    t.add_column(ratio=1)
    t.add_column(justify="right", min_width=12)

    title = Text()
    title.append(" ● ", style="bold bright_red")
    title.append("InvestScan Pipeline Monitor", style="bold white")

    time_str = _fmt_duration(elapsed_sec)
    t.add_row(title, Text(time_str, style="dim white"))
    return t


def _build_progress_panel(ps: dict, metrics: dict):
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress_bar import ProgressBar
    from rich.table import Table

    done = metrics["phases_done"]
    total = metrics["phases_total"]
    pct = round(done / total * 100) if total else 0

    grid = Table.grid(padding=(0, 1), expand=True)
    grid.add_column(ratio=1)

    # Progress bar row
    bar_t = Table.grid(expand=True, padding=(0, 1))
    bar_t.add_column(min_width=10)
    bar_t.add_column(ratio=1)
    bar_t.add_column(min_width=16, justify="right")

    current = ps.get("current_phase", "")
    current_label = PHASE_SHORT.get(current, current)
    bar_label = Text(current_label, style="bold cyan") if current else Text("대기", style="dim")

    bar = ProgressBar(total=total, completed=done, width=None,
                      complete_style="bar.complete", finished_style="bar.finished")
    bar_t.add_row(bar_label, bar, Text(f"{done}/{total} · {pct}%", style="white"))
    grid.add_row(bar_t)

    # Running phase indicators (► green)
    phases = ps.get("phases", {})
    running_names = [
        PHASE_SHORT.get(p, p)
        for p in PHASES_ORDERED
        if phases.get(p, {}).get("status") == "running"
    ]
    if running_names:
        run_text = Text("  ")
        for name in running_names:
            run_text.append("► ", style="bright_green")
            run_text.append(name + "  ", style="white")
        grid.add_row(run_text)

    # Running agent indicators
    for rnd_label, rnd_key in [("R1", "phase_3"), ("R2", "phase_4")]:
        ag = phases.get(rnd_key, {}).get("agents", {})
        running_agents = [n for n, s in ag.items() if s == "running"]
        if running_agents:
            ag_text = Text("  ")
            for name in running_agents:
                label = AGENT_LABELS.get(name, name)
                ag_text.append("► ", style="bright_green")
                ag_text.append(f"{rnd_label}:{label}  ", style="white")
            grid.add_row(ag_text)

    return Panel(grid, title="[bold bright_blue]파이프라인 진행률[/bold bright_blue]",
                 border_style="bright_blue", padding=(1, 2))


def _build_metrics_panel(metrics: dict):
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    t = Table.grid(expand=True, padding=(1, 2))
    for _ in range(5):
        t.add_column(justify="center", ratio=1)

    elapsed_str = _fmt_duration(metrics["elapsed_sec"])
    eta_str = _fmt_duration(metrics["eta_sec"])
    proc_str = _fmt_duration(metrics["proc_sec"])
    pct = round(metrics["phases_done"] / metrics["phases_total"] * 100) if metrics["phases_total"] else 0
    pct_style = "bold bright_green" if pct >= 50 else "bold bright_red"
    err_style = "bold bright_green" if metrics["phases_failed"] == 0 else "bold bright_red"

    # Values
    t.add_row(
        Text(f"{metrics['phases_done']}/{metrics['phases_total']}", style="bold bright_green", justify="center"),
        Text(f"{metrics['agents_done']}/{metrics['agents_total']}", style="bold bright_green", justify="center"),
        Text(f"{pct}%", style=pct_style, justify="center"),
        Text(elapsed_str, style="bold bright_green", justify="center"),
        Text(str(metrics["phases_failed"]), style=err_style, justify="center"),
    )

    # Labels
    t.add_row(
        Text("단계 완료", style="dim", justify="center"),
        Text("에이전트", style="dim", justify="center"),
        Text("진행률", style="dim", justify="center"),
        Text("경과 시간", style="dim", justify="center"),
        Text("오류", style="dim", justify="center"),
    )

    # Sub-info
    running_sub = Text(f"{metrics['agents_running']}개 실행중", style="bright_cyan", justify="center") if metrics["agents_running"] else Text("R1+R2 합산", style="dim", justify="center")
    eta_sub = Text(f"잔여 {eta_str}", style="dim", justify="center") if metrics["eta_sec"] > 0 else Text("", justify="center")
    proc_sub = Text(f"처리 {proc_str}", style="dim", justify="center") if metrics["proc_sec"] > 0 else Text("", justify="center")
    err_sub = Text("이상 없음", style="dim", justify="center") if metrics["phases_failed"] == 0 else Text("확인 필요", style="bright_red", justify="center")

    t.add_row(Text("", justify="center"), running_sub, proc_sub, eta_sub, err_sub)

    return Panel(t, title="[bold bright_blue]핵심 지표[/bold bright_blue]",
                 border_style="bright_blue", padding=(1, 1))


def _build_pipeline_flow(ps: dict):
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    phases = ps.get("phases", {})

    t = Table.grid(expand=True, padding=(0, 0))
    for _ in range(8):
        t.add_column(justify="center", ratio=1)

    # Row 1: numbered circles with connectors
    row1 = []
    for idx, phase in enumerate(PHASES_ORDERED):
        status = phases.get(phase, {}).get("status", "pending")
        num = idx + 1
        cell = Text(justify="center")

        if status == "completed":
            cell.append(f" {num} ", style="bold white on green")
        elif status == "running":
            cell.append(f" {num} ", style="bold white on bright_blue")
        elif status in ("failed", "partial_failed"):
            cell.append(f" {num} ", style="bold white on red")
        else:
            cell.append(f" {num} ", style="dim")

        if idx < 7:
            next_status = phases.get(PHASES_ORDERED[idx + 1], {}).get("status", "pending")
            if status == "completed" and next_status in ("completed", "running"):
                cell.append(" ─", style="green")
            elif status == "completed":
                cell.append(" ─", style="green")
            else:
                cell.append(" ─", style="dim")

        row1.append(cell)
    t.add_row(*row1)

    # Row 2: labels
    row2 = [Text(PHASE_SHORT[p], style="dim white", justify="center") for p in PHASES_ORDERED]
    t.add_row(*row2)

    # Row 3: duration
    row3 = []
    for phase in PHASES_ORDERED:
        dur = phases.get(phase, {}).get("duration_sec")
        if dur is not None:
            row3.append(Text(f"{dur}s", style="dim", justify="center"))
        else:
            row3.append(Text("", justify="center"))
    t.add_row(*row3)

    return Panel(t, title="[bold bright_blue]분석 파이프라인[/bold bright_blue]",
                 border_style="bright_blue", padding=(1, 2))


def _build_agents_chart(ps: dict):
    """Horizontal bar chart for agent status — mirrors GlobalNews group chart style."""
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    phases = ps.get("phases", {})
    BAR_MAX = 40

    t = Table.grid(padding=(0, 1), expand=True)
    t.add_column(min_width=4, justify="center")   # round tag
    t.add_column(min_width=12, justify="right")    # agent label
    t.add_column(ratio=1)                          # bar
    t.add_column(min_width=8, justify="right")     # status text

    for rnd_num, rnd_key in [(1, "phase_3"), (2, "phase_4")]:
        agents = phases.get(rnd_key, {}).get("agents", {})
        phase_status = phases.get(rnd_key, {}).get("status", "pending")

        for name in AGENT_NAMES:
            status = agents.get(name, "pending")
            label = AGENT_LABELS.get(name, name)
            color = AGENT_COLORS.get(name, "white")

            # Round tag
            if phase_status == "completed":
                tag = Text(f"R{rnd_num}", style="bold green")
            elif phase_status == "running":
                tag = Text(f"R{rnd_num}", style="bold bright_blue")
            else:
                tag = Text(f"R{rnd_num}", style="dim")

            # Label
            label_text = Text(label, style="dim white")

            # Bar
            if status == "completed":
                bar_width = BAR_MAX
                bar_text = Text("█" * bar_width, style=color)
                status_text = Text("완료", style=color)
            elif status == "running":
                bar_width = BAR_MAX // 2
                bar_text = Text("█" * bar_width + "░" * (BAR_MAX - bar_width), style=color)
                status_text = Text("분석중", style="bold " + color)
            elif status == "failed":
                bar_text = Text("█" * BAR_MAX, style="bright_red")
                status_text = Text("실패", style="bright_red")
            else:
                bar_text = Text("░" * BAR_MAX, style="dim")
                status_text = Text("대기", style="dim")

            t.add_row(tag, label_text, bar_text, status_text)

    return Panel(t, title="[bold bright_blue]에이전트 분석[/bold bright_blue]",
                 border_style="bright_blue", padding=(1, 2))


def _build_data_health_panel(freshness: dict, state: dict):
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    t = Table.grid(expand=True, padding=(0, 2))
    t.add_column(ratio=1)
    t.add_column(ratio=1)

    # ── Left: Data Freshness ──
    left = Table.grid(padding=(0, 1), expand=True)
    left.add_column(min_width=18)
    left.add_column(min_width=10, justify="right")
    left.add_column(min_width=3, justify="center")

    left.add_row(
        Text("데이터 신선도", style="bold bright_blue"),
        Text(""),
        Text(""),
    )
    left.add_row(Text(""), Text(""), Text(""))

    rows = [
        ("🔍 EnvironmentScan", freshness.get("envscan", {})),
        ("📰 GlobalNews",      freshness.get("gnews",   {})),
        ("📋 Agent Context",   freshness.get("context", {})),
    ]
    for label, info in rows:
        age = info.get("age_days")
        ok = info.get("ok", False)
        age_str = f"{age}일 전" if age is not None else "없음"
        icon = Text("●", style="bright_green") if ok else Text("●", style="bright_red")
        left.add_row(Text(f" {label}", style="white"), Text(age_str, style="dim"), icon)

    # ── Right: System Health ──
    right = Table.grid(padding=(0, 1), expand=True)
    right.add_column(min_width=18)
    right.add_column(min_width=10, justify="right")
    right.add_column(min_width=3, justify="center")

    right.add_row(
        Text("시스템 건강도", style="bold bright_blue"),
        Text(""),
        Text(""),
    )
    right.add_row(Text(""), Text(""), Text(""))

    lib = state.get("library_availability", {})
    for name, key in [("📦 FDR", "fdr"), ("📦 pykrx", "pykrx"), ("📦 dart_fss", "dart_fss")]:
        info = lib.get(key, {})
        rate = info.get("rolling_4w_rate")
        if rate is None:
            val = Text("미확인", style="dim")
            icon = Text("○", style="dim")
        elif rate >= 0.8:
            val = Text(f"{rate*100:.0f}%", style="bright_green")
            icon = Text("●", style="bright_green")
        else:
            val = Text(f"{rate*100:.0f}%", style="bright_red")
            icon = Text("●", style="bright_red")
        right.add_row(Text(f" {name}", style="white"), val, icon)

    tdd = state.get("tdd_status", {})
    tdd_total = len(tdd)
    tdd_pass = sum(1 for v in tdd.values() if v == "passing")
    tdd_icon = Text("●", style="bright_green") if tdd_pass == tdd_total and tdd_total > 0 else Text("●", style="bright_yellow")
    right.add_row(Text(" 🧪 TDD", style="white"), Text(f"{tdd_pass}/{tdd_total}", style="bright_green" if tdd_pass == tdd_total else "bright_yellow"), tdd_icon)

    trans = state.get("translations", {})
    tr_done = sum(1 for v in trans.values() if isinstance(v, dict) and v.get("status") == "completed")
    tr_total = len(trans)
    right.add_row(Text(" 🌐 번역", style="white"), Text(f"{tr_done}/{tr_total}", style="dim"), Text(""))

    t.add_row(left, right)

    return Panel(t, title="[bold bright_blue]데이터 & 시스템[/bold bright_blue]",
                 border_style="bright_blue", padding=(1, 2))


# ── Main Layout ───────────────────────────────────────────────────────────────

def _build_layout():
    from rich.table import Table

    ps = _load_pipeline_status()
    state = _load_state()
    freshness = _data_freshness()
    report = _latest_report()
    metrics = _compute_metrics(ps)

    root = Table.grid(padding=(0, 0), expand=True)

    # Header
    root.add_row(_build_header(metrics["elapsed_sec"]))
    root.add_row("")

    # Progress bar
    root.add_row(_build_progress_panel(ps, metrics))

    # Key metrics
    root.add_row(_build_metrics_panel(metrics))

    # Pipeline flow
    root.add_row(_build_pipeline_flow(ps))

    # Agents chart
    root.add_row(_build_agents_chart(ps))

    # Data & Health
    root.add_row(_build_data_health_panel(freshness, state))

    # Footer
    report_str = report or "없음"
    root.add_row(
        f"  [dim]📄 리포트: {report_str}   │   Ctrl+C 종료   │   자동 갱신 중[/dim]"
    )

    return root


# ── Entry Points ──────────────────────────────────────────────────────────────

def run_once() -> None:
    from rich.console import Console
    Console().print(_build_layout())


def run_dashboard(interval: int = 3) -> None:
    from rich.console import Console
    from rich.live import Live

    console = Console()

    with Live(_build_layout(), console=console, refresh_per_second=2, screen=True) as live:
        last_refresh = time.time()
        try:
            while True:
                time.sleep(0.3)
                if time.time() - last_refresh >= interval:
                    live.update(_build_layout())
                    last_refresh = time.time()
        except KeyboardInterrupt:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="InvestScan Pipeline Monitor — real-time terminal dashboard"
    )
    parser.add_argument("--once", action="store_true", help="Print one snapshot and exit")
    parser.add_argument("--watch", type=int, default=3, metavar="SEC",
                        help="Refresh interval in seconds (default: 3)")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_dashboard(interval=args.watch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
