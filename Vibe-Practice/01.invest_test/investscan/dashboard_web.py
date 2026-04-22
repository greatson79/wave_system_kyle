"""
investscan/dashboard_web.py — Streamlit web dashboard for InvestScan pipeline monitoring.

Launch:
    streamlit run investscan/dashboard_web.py

Auto-refreshes every 5 seconds. Read-only — never modifies state files.
English-First (P5-A).

Data sources:
    output/temp/pipeline_status.json  — phase/agent execution state
    .claude/state.yaml                — library availability, TDD, translations
    output/reports/                   — latest report filename
    EnvironmentScan output dir        — WF*.json mtime
    GlobalNews raw dir                — latest date directory
"""
from __future__ import annotations

import json
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import streamlit as st
import yaml

# ── Paths ──────────────────────────────────────────────────────────────────────
STATUS_FILE    = Path("output/temp/pipeline_status.json")
STATE_YAML     = Path(".claude/state.yaml")
REPORTS_DIR    = Path("output/reports")
TEMP_DIR       = Path("output/temp")
ENVSCAN_OUT    = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/EnvironmentScan-system-main-v4-main/output")
GNEWS_RAW_BASE = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/GlobalNews-Crawling-AgenticWorkflow/data/raw")

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

PHASE_LABELS = {
    "phase_0":         "Phase 0 — 상태 확인",
    "phase_1_envscan": "Phase 1a — EnvScan",
    "phase_1_gnews":   "Phase 1b — GlobalNews",
    "phase_2":         "Phase 2 — 컨텍스트 준비",
    "phase_3":         "Phase 3 — Round 1 분석",
    "phase_4":         "Phase 4 — Round 2 토론",
    "phase_5":         "Phase 5 — 마스터 종합",
    "phase_6":         "Phase 6 — PDF 생성",
}

AGENT_NAMES = ["macro", "tech", "korea", "valuation", "risk"]
AGENT_DISPLAY = {
    "macro":     ("거시경제", "📈"),
    "tech":      ("기술/AI", "🤖"),
    "korea":     ("한국시장", "🇰🇷"),
    "valuation": ("밸류에이션", "💰"),
    "risk":      ("리스크", "⚡"),
}

# ── Colors ─────────────────────────────────────────────────────────────────────
C_BG        = "#0E1117"
C_CARD      = "#1B2332"
C_CARD_BORDER = "#2D3748"
C_GREEN     = "#00D26A"
C_BLUE      = "#3B82F6"
C_YELLOW    = "#FBBF24"
C_RED       = "#EF4444"
C_GRAY      = "#4A5568"
C_GRAY_TEXT = "#8899AA"
C_WHITE     = "#E2E8F0"


# ── Data loaders ───────────────────────────────────────────────────────────────

def load_pipeline_status() -> dict:
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def load_state() -> dict:
    if STATE_YAML.exists():
        try:
            return yaml.safe_load(STATE_YAML.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
    return {}


def data_freshness() -> dict:
    result: dict = {}

    wf_files = sorted(ENVSCAN_OUT.glob("WF*.json")) if ENVSCAN_OUT.exists() else []
    if wf_files:
        mtime = datetime.fromtimestamp(wf_files[-1].stat().st_mtime)
        age = (datetime.now() - mtime).days
        result["envscan"] = {"label": wf_files[-1].name, "age_days": age, "ok": age <= 3}
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
        result["context"] = {"label": contexts[-1].name, "age_days": age, "ok": age == 0}
    else:
        result["context"] = {"label": "없음", "age_days": None, "ok": False}

    return result


def latest_report() -> Optional[str]:
    if REPORTS_DIR.exists():
        reports = sorted(REPORTS_DIR.glob("weekly-report-*.md"), reverse=True)
        if reports:
            return reports[0].name
    return None


# ── Computed metrics ───────────────────────────────────────────────────────────

def compute_metrics(ps: dict) -> dict:
    phases = ps.get("phases", {})
    completed = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") == "completed")
    running = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") == "running")
    failed = sum(1 for p in PHASES_ORDERED if phases.get(p, {}).get("status") in ("failed", "partial_failed"))
    total = len(PHASES_ORDERED)

    # Agent counts
    agents_done = 0
    agents_total = 0
    for ph in ("phase_3", "phase_4"):
        ag = phases.get(ph, {}).get("agents", {})
        agents_total += len(ag)
        agents_done += sum(1 for s in ag.values() if s == "completed")

    # Elapsed
    started = ps.get("started_at")
    elapsed_sec = 0
    if started:
        try:
            elapsed_sec = int((datetime.now() - datetime.fromisoformat(started)).total_seconds())
        except Exception:
            pass

    # Total duration of completed phases
    total_dur = sum(phases.get(p, {}).get("duration_sec", 0) or 0 for p in PHASES_ORDERED)

    progress_pct = int(completed / total * 100) if total else 0

    return {
        "completed": completed,
        "running": running,
        "failed": failed,
        "total": total,
        "agents_done": agents_done,
        "agents_total": agents_total,
        "elapsed_sec": elapsed_sec,
        "total_dur": total_dur,
        "progress_pct": progress_pct,
    }


# ── CSS ────────────────────────────────────────────────────────────────────────

CUSTOM_CSS = f"""
<style>
/* Global dark theme overrides */
.stApp {{
    background-color: {C_BG};
}}
.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 0;
    max-width: 1200px;
}}

/* Hide default Streamlit header/footer */
header[data-testid="stHeader"] {{
    background: {C_BG} !important;
}}
.stDeployButton {{ display: none; }}

/* Card styling */
.metric-card {{
    background: {C_CARD};
    border: 1px solid {C_CARD_BORDER};
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    transition: transform 0.2s;
}}
.metric-card:hover {{
    transform: translateY(-2px);
    border-color: {C_BLUE};
}}
.metric-value {{
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
}}
.metric-label {{
    font-size: 0.8rem;
    color: {C_GRAY_TEXT};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
}}
.metric-sub {{
    font-size: 0.75rem;
    color: {C_GRAY_TEXT};
    margin-top: 4px;
}}

/* Section titles */
.section-title {{
    color: {C_WHITE};
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid {C_CARD_BORDER};
    letter-spacing: 0.02em;
}}

/* Pipeline flow */
.pipeline-container {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    padding: 24px 8px;
    overflow-x: auto;
}}
.phase-node {{
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 72px;
}}
.phase-circle {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    color: #fff;
    position: relative;
    z-index: 2;
}}
.phase-circle.completed {{
    background: {C_GREEN};
    box-shadow: 0 0 12px {C_GREEN}44;
}}
.phase-circle.running {{
    background: {C_BLUE};
    box-shadow: 0 0 16px {C_BLUE}66;
    animation: pulse 2s ease-in-out infinite;
}}
.phase-circle.failed {{
    background: {C_RED};
    box-shadow: 0 0 12px {C_RED}44;
}}
.phase-circle.pending {{
    background: {C_GRAY};
    opacity: 0.5;
}}
.phase-label {{
    font-size: 0.7rem;
    color: {C_GRAY_TEXT};
    margin-top: 8px;
    text-align: center;
    max-width: 80px;
    line-height: 1.3;
}}
.phase-dur {{
    font-size: 0.65rem;
    color: {C_GRAY};
    margin-top: 2px;
}}
.phase-connector {{
    width: 28px;
    height: 3px;
    background: {C_GRAY};
    opacity: 0.4;
    margin: 0 2px;
    margin-bottom: 28px;
    border-radius: 2px;
}}
.phase-connector.active {{
    background: {C_GREEN};
    opacity: 0.8;
}}

@keyframes pulse {{
    0%, 100% {{ box-shadow: 0 0 8px {C_BLUE}44; }}
    50% {{ box-shadow: 0 0 24px {C_BLUE}88; }}
}}

/* Agent bars */
.agent-row {{
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    gap: 10px;
}}
.agent-name {{
    width: 90px;
    font-size: 0.82rem;
    color: {C_GRAY_TEXT};
    text-align: right;
    font-weight: 600;
    flex-shrink: 0;
}}
.agent-bar-bg {{
    flex: 1;
    height: 28px;
    background: {C_CARD_BORDER}88;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
}}
.agent-bar-fill {{
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s ease;
    display: flex;
    align-items: center;
    padding-left: 10px;
    font-size: 0.72rem;
    font-weight: 700;
    color: #fff;
}}
.agent-bar-fill.completed {{
    background: linear-gradient(90deg, {C_GREEN}, #10B981);
}}
.agent-bar-fill.running {{
    background: linear-gradient(90deg, {C_BLUE}, #60A5FA);
    animation: barPulse 1.5s ease-in-out infinite;
}}
.agent-bar-fill.failed {{
    background: linear-gradient(90deg, {C_RED}, #F87171);
}}
.agent-bar-fill.pending {{
    background: {C_GRAY};
    opacity: 0.3;
}}
.agent-round-tag {{
    font-size: 0.65rem;
    color: {C_GRAY_TEXT};
    padding: 2px 8px;
    background: {C_CARD_BORDER};
    border-radius: 4px;
    flex-shrink: 0;
}}

@keyframes barPulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.7; }}
}}

/* Freshness / Health items */
.info-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: {C_CARD};
    border: 1px solid {C_CARD_BORDER};
    border-radius: 8px;
    margin-bottom: 8px;
}}
.info-row-label {{
    font-size: 0.85rem;
    color: {C_WHITE};
    font-weight: 600;
}}
.info-row-sub {{
    font-size: 0.72rem;
    color: {C_GRAY_TEXT};
}}
.info-row-value {{
    font-size: 0.85rem;
    font-weight: 700;
}}
.info-row-value.ok {{ color: {C_GREEN}; }}
.info-row-value.warn {{ color: {C_YELLOW}; }}
.info-row-value.bad {{ color: {C_RED}; }}

/* Progress bar override */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {C_GREEN}, #10B981) !important;
    border-radius: 8px !important;
}}
.stProgress > div > div > div {{
    background: {C_CARD_BORDER} !important;
    border-radius: 8px !important;
}}

/* Title bar */
.title-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}}
.title-main {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {C_WHITE};
    display: flex;
    align-items: center;
    gap: 10px;
}}
.title-main .icon {{
    font-size: 1.4rem;
}}
.title-meta {{
    text-align: right;
    font-size: 0.8rem;
    color: {C_GRAY_TEXT};
    line-height: 1.5;
}}
.title-meta b {{
    color: {C_WHITE};
}}
.status-running {{
    display: inline-block;
    background: {C_BLUE}22;
    color: {C_BLUE};
    border: 1px solid {C_BLUE}55;
    border-radius: 12px;
    padding: 2px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    animation: pulse 2s ease-in-out infinite;
}}
.status-done {{
    display: inline-block;
    background: {C_GREEN}22;
    color: {C_GREEN};
    border: 1px solid {C_GREEN}55;
    border-radius: 12px;
    padding: 2px 12px;
    font-size: 0.75rem;
    font-weight: 700;
}}

/* Hide Streamlit metric styling, use custom cards */
[data-testid="stMetricValue"] {{ display: none; }}
</style>
"""


# ── HTML builders ──────────────────────────────────────────────────────────────

def _fmt_elapsed(sec: int) -> str:
    if sec < 60:
        return f"{sec}초"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"{m}분 {s}초"
    h, m = divmod(m, 60)
    return f"{h}시간 {m}분"


def _fmt_dur(dur: Optional[int]) -> str:
    if dur is None:
        return ""
    if dur < 60:
        return f"{dur}s"
    return f"{dur // 60}m {dur % 60}s"


def build_metric_card(value: str, label: str, sub: str = "", color: str = C_WHITE) -> str:
    sub_html = f'<div class="metric-sub">{sub}</div>' if sub else ""
    return (
        f'<div class="metric-card">'
        f'<div class="metric-value" style="color:{color}">{value}</div>'
        f'<div class="metric-label">{label}</div>'
        f'{sub_html}'
        f'</div>'
    )


def build_pipeline_flow(ps: dict) -> str:
    phases = ps.get("phases", {})
    nodes_html = []

    for i, ph in enumerate(PHASES_ORDERED):
        p = phases.get(ph, {})
        status = p.get("status", "pending")
        dur = p.get("duration_sec")
        label = PHASE_SHORT.get(ph, ph)

        if status == "completed":
            css_class = "completed"
            icon = "✓"
        elif status == "running":
            css_class = "running"
            icon = "⟳"
        elif status in ("failed", "partial_failed"):
            css_class = "failed"
            icon = "✗"
        else:
            css_class = "pending"
            icon = str(i)

        dur_str = _fmt_dur(dur) if dur else ""
        dur_html = f'<div class="phase-dur">{dur_str}</div>' if dur_str else ""

        nodes_html.append(
            f'<div class="phase-node">'
            f'<div class="phase-circle {css_class}">{icon}</div>'
            f'<div class="phase-label">{label}</div>'
            f'{dur_html}'
            f'</div>'
        )

        if i < len(PHASES_ORDERED) - 1:
            conn_class = "active" if status == "completed" else ""
            nodes_html.append(f'<div class="phase-connector {conn_class}"></div>')

    return f'<div class="pipeline-container">{"".join(nodes_html)}</div>'


def build_agent_bars(ps: dict) -> str:
    phases = ps.get("phases", {})
    rows_html = []

    for round_num, phase_key in [(1, "phase_3"), (2, "phase_4")]:
        agents = phases.get(phase_key, {}).get("agents", {})
        phase_status = phases.get(phase_key, {}).get("status", "pending")

        tag_color = C_GREEN if phase_status == "completed" else (C_BLUE if phase_status == "running" else C_GRAY)

        for agent_name in AGENT_NAMES:
            display_name, emoji = AGENT_DISPLAY.get(agent_name, (agent_name, ""))
            status = agents.get(agent_name, "pending")

            if status == "completed":
                width = 100
                css = "completed"
                bar_label = "완료"
            elif status == "running":
                width = 60
                css = "running"
                bar_label = "분석중..."
            elif status == "failed":
                width = 100
                css = "failed"
                bar_label = "실패"
            else:
                width = 5
                css = "pending"
                bar_label = ""

            rows_html.append(
                f'<div class="agent-row">'
                f'<div class="agent-round-tag" style="color:{tag_color}">R{round_num}</div>'
                f'<div class="agent-name">{emoji} {display_name}</div>'
                f'<div class="agent-bar-bg">'
                f'<div class="agent-bar-fill {css}" style="width:{width}%">{bar_label}</div>'
                f'</div>'
                f'</div>'
            )

    return "".join(rows_html)


def build_freshness_rows(freshness: dict) -> str:
    items = [
        ("🔍 EnvironmentScan", freshness.get("envscan", {})),
        ("📰 GlobalNews", freshness.get("gnews", {})),
        ("📋 Agent Context", freshness.get("context", {})),
    ]
    rows = []
    for label, info in items:
        age = info.get("age_days")
        ok = info.get("ok", False)
        file_label = info.get("label", "")

        if ok:
            val_class = "ok"
            val_str = f"✓ {age}일 전" if age is not None else "✓ 최신"
        elif age is not None:
            val_class = "warn" if age <= 7 else "bad"
            val_str = f"⚠ {age}일 전"
        else:
            val_class = "bad"
            val_str = "✗ 없음"

        rows.append(
            f'<div class="info-row">'
            f'<div>'
            f'<div class="info-row-label">{label}</div>'
            f'<div class="info-row-sub">{file_label}</div>'
            f'</div>'
            f'<div class="info-row-value {val_class}">{val_str}</div>'
            f'</div>'
        )
    return "".join(rows)


def build_health_rows(state: dict) -> str:
    lib = state.get("library_availability", {})
    tdd = state.get("tdd_status", {})
    trans = state.get("translations", {})

    rows = []

    # Libraries
    for name, key in [("FDR", "fdr"), ("pykrx", "pykrx"), ("dart_fss", "dart_fss")]:
        info = lib.get(key, {})
        rate = info.get("rolling_4w_rate")
        if rate is None:
            val_class = "warn"
            val_str = "미확인"
        elif rate >= 0.8:
            val_class = "ok"
            val_str = f"{rate*100:.0f}%"
        else:
            val_class = "bad"
            val_str = f"{rate*100:.0f}%"

        rows.append(
            f'<div class="info-row">'
            f'<div class="info-row-label">📦 {name}</div>'
            f'<div class="info-row-value {val_class}">{val_str}</div>'
            f'</div>'
        )

    # TDD
    tdd_total = len(tdd)
    tdd_pass = sum(1 for v in tdd.values() if v == "passing")
    tdd_class = "ok" if tdd_pass == tdd_total and tdd_total > 0 else "warn"
    rows.append(
        f'<div class="info-row">'
        f'<div class="info-row-label">🧪 TDD 테스트</div>'
        f'<div class="info-row-value {tdd_class}">{tdd_pass}/{tdd_total} 통과</div>'
        f'</div>'
    )

    # Translation
    trans_done = sum(1 for v in trans.values() if isinstance(v, dict) and v.get("status") == "completed")
    trans_total = len(trans)
    trans_class = "ok" if trans_done == trans_total and trans_total > 0 else "warn"
    rows.append(
        f'<div class="info-row">'
        f'<div class="info-row-label">🌐 번역 진행</div>'
        f'<div class="info-row-value {trans_class}">{trans_done}/{trans_total} 완료</div>'
        f'</div>'
    )

    return "".join(rows)


# ── Main app ───────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title="InvestScan Pipeline Monitor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Load data ──────────────────────────────────────────────────────────────
    ps        = load_pipeline_status()
    state     = load_state()
    freshness = data_freshness()
    report    = latest_report()
    m         = compute_metrics(ps)

    now_str   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current   = ps.get("current_phase", "—") if ps else "—"
    current_label = PHASE_LABELS.get(current, current)

    # Determine overall pipeline status
    if m["completed"] == m["total"]:
        overall_status_html = f'<span class="status-done">✓ 완료</span>'
    elif m["running"] > 0:
        overall_status_html = f'<span class="status-running">● 실행 중</span>'
    elif m["failed"] > 0:
        overall_status_html = f'<span class="status-done" style="color:{C_RED};border-color:{C_RED}55;background:{C_RED}22;">✗ 오류</span>'
    else:
        overall_status_html = f'<span class="status-done" style="color:{C_GRAY_TEXT};border-color:{C_GRAY}55;background:{C_GRAY}22;">— 대기</span>'

    # ── Title Bar ──────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="title-bar">'
        f'<div class="title-main">'
        f'<span class="icon">📊</span> InvestScan Pipeline Monitor'
        f'&nbsp;&nbsp;{overall_status_html}'
        f'</div>'
        f'<div class="title-meta">'
        f'🕐 {now_str}<br>'
        f'현재: <b>{current_label}</b> &nbsp;│&nbsp; '
        f'경과: <b>{_fmt_elapsed(m["elapsed_sec"])}</b>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if report:
        st.markdown(
            f'<div style="font-size:0.78rem;color:{C_GRAY_TEXT};margin-top:-4px;margin-bottom:12px;">'
            f'📄 최근 리포트: {report}</div>',
            unsafe_allow_html=True,
        )

    # ── Progress Bar ───────────────────────────────────────────────────────────
    progress_frac = m["completed"] / m["total"] if m["total"] else 0
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-bottom:4px;">'
        f'<span style="color:{C_GRAY_TEXT};font-size:0.82rem;font-weight:600;">'
        f'파이프라인 진행률</span>'
        f'<span style="color:{C_WHITE};font-size:0.82rem;font-weight:700;">'
        f'{m["completed"]}/{m["total"]}단계 &nbsp;&nbsp; {m["progress_pct"]}%</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.progress(progress_frac)

    # ── Key Metrics Row ────────────────────────────────────────────────────────
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    metrics = [
        (f'{m["completed"]}/{m["total"]}', "단계 완료",
         f'{m["running"]}개 진행중' if m["running"] else "전체 완료" if m["completed"] == m["total"] else "",
         C_GREEN if m["completed"] == m["total"] else C_BLUE),
        (f'{m["agents_done"]}/{m["agents_total"]}', "에이전트",
         "R1 + R2 합산", C_GREEN if m["agents_done"] == m["agents_total"] else C_BLUE),
        (f'{m["progress_pct"]}%', "진행률", "", C_GREEN if m["progress_pct"] == 100 else C_YELLOW),
        (_fmt_elapsed(m["elapsed_sec"]), "경과 시간",
         f'처리: {_fmt_elapsed(m["total_dur"])}' if m["total_dur"] else "", C_WHITE),
        (str(m["failed"]), "오류",
         "이상 없음" if m["failed"] == 0 else "확인 필요",
         C_GREEN if m["failed"] == 0 else C_RED),
    ]

    for col, (val, label, sub, color) in zip(cols, metrics):
        col.markdown(build_metric_card(val, label, sub, color), unsafe_allow_html=True)

    # ── Pipeline Flow ──────────────────────────────────────────────────────────
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔄 파이프라인 단계</div>', unsafe_allow_html=True)
    st.markdown(build_pipeline_flow(ps), unsafe_allow_html=True)

    # ── Two-column layout: Agents | Data+Health ────────────────────────────────
    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.markdown('<div class="section-title">🤖 에이전트 분석 현황</div>', unsafe_allow_html=True)
        st.markdown(build_agent_bars(ps), unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">📡 데이터 신선도</div>', unsafe_allow_html=True)
        st.markdown(build_freshness_rows(freshness), unsafe_allow_html=True)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🛡️ 시스템 건강도</div>', unsafe_allow_html=True)
        st.markdown(build_health_rows(state), unsafe_allow_html=True)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="text-align:center;color:{C_GRAY};font-size:0.72rem;'
        f'margin-top:24px;padding:12px 0;border-top:1px solid {C_CARD_BORDER};">'
        f'5초마다 자동 갱신 &nbsp;·&nbsp; Ctrl+C로 서버 종료 &nbsp;·&nbsp; '
        f'InvestScan v1.0</div>',
        unsafe_allow_html=True,
    )

    # ── Auto-refresh ───────────────────────────────────────────────────────────
    time.sleep(5)
    st.rerun()


if __name__ == "__main__":
    main()
