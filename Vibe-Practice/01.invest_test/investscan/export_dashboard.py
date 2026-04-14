"""
export_dashboard.py — InvestScan HTML dashboard generator.

Reads confirmed_watchlist_{DATE}.json + weekly-report-{DATE}.md,
fetches live prices via naver_finance, renders a self-contained HTML file.

Usage (via export_report):
    python3 -m investscan.export_report --date 2026-04-09 --formats html
    python3 -m investscan.export_report --date 2026-04-09 --formats html --no-live

Saves to:
    ~/Desktop/Ai_works/output/투자분析제안/{DATE}_주간투자분析_대시보드.html
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypedDict

from investscan.naver_finance import fetch_stocks, fetch_kospi_index

# ── paths ──────────────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).parent.parent
TEMP_DIR      = _PROJECT_ROOT / "output" / "temp"
REPORTS_DIR   = _PROJECT_ROOT / "output" / "reports"
OUTPUT_DIR    = Path.home() / "Desktop" / "Ai_works" / "output" / "투자분析제안"


# ── TypedDicts ─────────────────────────────────────────────────────────────────

class KospiForecast(TypedDict):
    low:  str   # "5,500"
    base: str   # "5,800~5,900"
    high: str   # "6,200~6,350"


class WatchlistData(TypedDict):
    date:                   str
    cat_a:                  list[str]
    cat_b:                  list[str]
    p6_not_passed:          list[str]
    agent_weights:          dict[str, float]
    base_sector_directions: dict[str, str]


class StockCard(TypedDict):
    ticker:     str
    name:       str
    current:    str   # "82,300" or "N/A"
    change_pct: str   # "+1.20%" or "N/A"
    direction:  str   # "up" | "down" | "flat" | "unknown"
    sector:     str
    confidence: str   # "0.74" or "N/A"
    target:     str   # always "N/A" in v1


class DashboardData(TypedDict):
    date:              str
    pipeline_version:  str
    kospi_current:     str
    kospi_change_pct:  str
    kospi_direction:   str
    kospi_forecast:    KospiForecast
    cat_a:             list[StockCard]
    cat_b:             list[StockCard]
    p6_not_passed:     list[StockCard]
    agent_weights:     dict[str, float]
    sector_directions: dict[str, str]


# ── data loaders ───────────────────────────────────────────────────────────────

def load_watchlist(
    date: str,
    temp_dir: Path = TEMP_DIR,
) -> WatchlistData:
    """Load confirmed_watchlist_{date}.json. Raises FileNotFoundError if missing."""
    path = temp_dir / f"confirmed_watchlist_{date}.json"
    if not path.exists():
        raise FileNotFoundError(f"Watchlist not found: {path}")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    p6_not_passed: list[str] = []
    rationale = raw.get("rationale", {})
    if isinstance(rationale, dict):
        p6_not_passed = rationale.get("p6_not_passed", [])

    return WatchlistData(
        date=raw.get("date", date),
        cat_a=raw.get("cat_a", []),
        cat_b=raw.get("cat_b", []),
        p6_not_passed=p6_not_passed,
        agent_weights=raw.get("agent_weights", {}),
        base_sector_directions=raw.get("base_sector_directions", {}),
    )


def load_kospi_forecast(
    date: str,
    reports_dir: Path = REPORTS_DIR,
) -> KospiForecast:
    """Parse KOSPI Low/Base/High from section 2.3 of the weekly report MD.

    Returns KospiForecast with "N/A" values if parsing fails or file missing.
    """
    path = reports_dir / f"weekly-report-{date}.md"
    empty = KospiForecast(low="N/A", base="N/A", high="N/A")
    if not path.exists():
        return empty

    text = path.read_text(encoding="utf-8")

    # Match the corrected-value column (last bold cell) in the 2.3 forecast table.
    # Pattern: **Low** ... **<value>** (last bold on that row)
    low_m  = re.search(r"\*\*Low\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    base_m = re.search(r"\*\*Base\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    high_m = re.search(r"\*\*High\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)

    def _extract(m: re.Match | None) -> str:
        if not m:
            return "N/A"
        raw = m.group(1).strip()
        # Strip parenthetical suffix like " (-5.2% from 5,800)"
        raw = re.sub(r"\s*\(.*?\)", "", raw).strip()
        return raw if raw else "N/A"

    return KospiForecast(
        low=_extract(low_m),
        base=_extract(base_m),
        high=_extract(high_m),
    )


# ── stock card builder ─────────────────────────────────────────────────────────

def _make_stock_card(
    ticker: str,
    live_data: dict,
    sector: str = "N/A",
    confidence: str = "N/A",
) -> StockCard:
    """Build a StockCard from live price data dict (may be empty on failure)."""
    info = live_data.get(ticker, {})
    return StockCard(
        ticker=ticker,
        name=info.get("name", ticker),
        current=info.get("current_price", "N/A"),
        change_pct=info.get("change_pct", "N/A"),
        direction=info.get("direction", "unknown"),
        sector=sector,
        confidence=confidence,
        target="N/A",
    )


# ── data assembler ─────────────────────────────────────────────────────────────

def assemble_dashboard_data(
    date: str,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
    live: bool = True,
) -> DashboardData:
    """Load all data sources and assemble DashboardData.

    live=False skips all network calls (for testing / --no-live mode).
    """
    wl       = load_watchlist(date, temp_dir=temp_dir)
    forecast = load_kospi_forecast(date, reports_dir=reports_dir)

    live_tickers = wl["cat_a"] + wl["cat_b"]
    live_tickers_dict = {t: t for t in live_tickers}  # fetch_stocks expects dict[ticker, name]
    live_data: dict = {}
    kospi_index = None

    if live and live_tickers:
        try:
            live_data = fetch_stocks(live_tickers_dict)
        except Exception as e:
            print(f"  ⚠  주가 조회 실패: {e}")
        try:
            kospi_index = fetch_kospi_index()
        except Exception as e:
            print(f"  ⚠  KOSPI 지수 조회 실패: {e}")

    cat_a_cards    = [_make_stock_card(t, live_data) for t in wl["cat_a"]]
    cat_b_cards    = [_make_stock_card(t, live_data) for t in wl["cat_b"]]
    p6_cards       = [_make_stock_card(t, {})        for t in wl["p6_not_passed"]]

    return DashboardData(
        date=date,
        pipeline_version="v4.0.0",
        kospi_current=kospi_index["current"]    if kospi_index else "N/A",
        kospi_change_pct=kospi_index["change_pct"] if kospi_index else "N/A",
        kospi_direction=kospi_index["direction"] if kospi_index else "unknown",
        kospi_forecast=forecast,
        cat_a=cat_a_cards,
        cat_b=cat_b_cards,
        p6_not_passed=p6_cards,
        agent_weights=wl["agent_weights"],
        sector_directions=wl["base_sector_directions"],
    )


# ── HTML rendering helpers ─────────────────────────────────────────────────────

def _direction_arrow(direction: str) -> str:
    return {"up": "▲", "down": "▼", "flat": "–"}.get(direction, "–")


def _direction_color(direction: str) -> str:
    return {"up": "var(--green)", "down": "var(--red)", "flat": "var(--text-dim)"}.get(
        direction, "var(--text-dim)"
    )


def _sector_badge(direction: str) -> str:
    colors = {"bullish": "#22c55e", "bearish": "#ef4444", "neutral": "#64748b"}
    labels = {"bullish": "BULL", "bearish": "BEAR", "neutral": "—"}
    color = colors.get(direction, "#64748b")
    label = labels.get(direction, direction.upper()[:4])
    return f'<span style="color:{color};font-weight:600;font-size:11px">{label}</span>'


def _stock_cards_html(cards: list) -> str:
    if not cards:
        return '<p style="color:var(--text-dim);padding:16px">해당 없음</p>'
    rows = []
    for c in cards:
        arrow = _direction_arrow(c["direction"])
        color = _direction_color(c["direction"])
        rows.append(f"""
        <div class="stock-card">
          <div class="sc-header">
            <span class="sc-name">{c['name']}</span>
            <span class="sc-ticker">{c['ticker']}</span>
          </div>
          <div class="sc-price" style="color:{color}">
            {c['current']} <span class="sc-arrow">{arrow}</span>
            <span class="sc-pct">{c['change_pct']}</span>
          </div>
          <div class="sc-meta">
            섹터 {c['sector']} &nbsp;|&nbsp; 신뢰도 {c['confidence']}
            &nbsp;|&nbsp; 목표가 <span style="color:var(--text-dim)">{c['target']}</span>
          </div>
        </div>""")
    return "\n".join(rows)


def _weights_js(weights: dict) -> str:
    labels = [f"'{k}'" for k in weights]
    values = list(weights.values())
    colors = ["'#f5c518'", "'#60a5fa'", "'#22c55e'", "'#f59e0b'", "'#ef4444'"]
    return (f"labels:[{','.join(labels)}],"
            f"data:[{','.join(str(v) for v in values)}],"
            f"backgroundColor:[{','.join(colors[:len(values)])}]")


def _sector_grid_html(directions: dict) -> str:
    cells = []
    for sector, direction in sorted(directions.items()):
        badge = _sector_badge(direction)
        cells.append(
            f'<div class="sector-cell"><span class="sector-name">{sector}</span>'
            f'<span class="sector-dir">{badge}</span></div>'
        )
    return "\n".join(cells)


def render_html(data: DashboardData) -> str:
    """Render DashboardData into a self-contained HTML string."""
    cat_a_html  = _stock_cards_html(data["cat_a"])
    cat_b_html  = _stock_cards_html(data["cat_b"])
    p6_html     = _stock_cards_html(data["p6_not_passed"])
    sector_html = _sector_grid_html(data["sector_directions"])
    weights_js  = _weights_js(data["agent_weights"])
    forecast    = data["kospi_forecast"]
    kospi_arrow = _direction_arrow(data["kospi_direction"])
    kospi_color = _direction_color(data["kospi_direction"])

    # Extract numeric values for Chart.js (strip commas, take upper bound of range)
    def _chart_val(s: str) -> str:
        if s == "N/A":
            return "0"
        upper = s.split("~")[-1].strip()
        return upper.replace(",", "")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InvestScan 대시보드 — {data['date']}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
  --bg:#06090f;--bg-2:#0c1220;--bg-3:#111827;
  --border:rgba(255,255,255,0.07);--border-hi:rgba(245,197,24,0.35);
  --gold:#f5c518;--gold-dim:#b38e10;
  --green:#22c55e;--red:#ef4444;--amber:#f59e0b;--blue:#60a5fa;
  --text:#e2e8f0;--text-dim:#64748b;--text-mid:#94a3b8;
  --mono:'DM Mono',monospace;--display:'Bebas Neue',sans-serif;--body:'Outfit',sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:var(--body);font-size:14px;line-height:1.6;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");pointer-events:none;z-index:0;opacity:0.6}}
.wrap{{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 32px 80px}}
.ticker{{background:var(--gold);color:#000;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.05em;padding:5px 0;overflow:hidden;white-space:nowrap;position:sticky;top:0;z-index:100}}
.ticker-inner{{display:inline-block;animation:ticker-scroll 24s linear infinite}}
.ticker-inner span{{margin:0 40px}}
@keyframes ticker-scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
.header{{padding:48px 0 32px;border-bottom:1px solid var(--border)}}
.header h1{{font-family:var(--display);font-size:48px;letter-spacing:.05em;color:var(--gold);line-height:1}}
.header .sub{{color:var(--text-mid);font-size:13px;margin-top:8px;font-family:var(--mono)}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}}
.card{{background:var(--bg-2);border:1px solid var(--border);border-radius:12px;padding:24px}}
.card-title{{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:16px}}
.tab-bar{{display:flex;gap:4px;margin-bottom:16px}}
.tab{{padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text-dim);font-family:var(--mono)}}
.tab.active{{background:var(--gold);color:#000;border-color:var(--gold);font-weight:600}}
.tab-content{{display:none}}.tab-content.active{{display:block}}
.stock-card{{background:var(--bg-3);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:10px}}
.sc-header{{display:flex;justify-content:space-between;margin-bottom:6px}}
.sc-name{{font-weight:600;font-size:14px}}
.sc-ticker{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.sc-price{{font-size:20px;font-weight:600;font-family:var(--mono);margin-bottom:4px}}
.sc-pct{{font-size:13px;margin-left:8px}}
.sc-meta{{font-size:11px;color:var(--text-dim)}}
.sector-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px}}
.sector-cell{{background:var(--bg-3);border:1px solid var(--border);border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}}
.sector-name{{font-size:12px;color:var(--text-mid);text-transform:capitalize}}
.forecast-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}}
.forecast-row:last-child{{border-bottom:none}}
.forecast-label{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.forecast-val{{font-family:var(--mono);font-size:14px;font-weight:600}}
</style>
</head>
<body>
<div class="ticker">
  <div class="ticker-inner">
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
  </div>
</div>
<div class="wrap">
  <div class="header">
    <h1>INVESTSCAN</h1>
    <div class="sub">주간 투자 분析 대시보드 &nbsp;|&nbsp; {data['date']} &nbsp;|&nbsp; {data['pipeline_version']}</div>
  </div>
  <div class="grid-2">
    <div class="card">
      <div class="card-title">P6 포트폴리오</div>
      <div class="tab-bar">
        <button class="tab active" onclick="showTab(event,'tab-a')">Cat A ({len(data['cat_a'])})</button>
        <button class="tab" onclick="showTab(event,'tab-b')">Cat B ({len(data['cat_b'])})</button>
        <button class="tab" onclick="showTab(event,'tab-p6')">P6미통과 ({len(data['p6_not_passed'])})</button>
      </div>
      <div id="tab-a" class="tab-content active">{cat_a_html}</div>
      <div id="tab-b" class="tab-content">{cat_b_html}</div>
      <div id="tab-p6" class="tab-content">{p6_html}</div>
    </div>
    <div class="card">
      <div class="card-title">KOSPI 4주 전망</div>
      <div style="font-family:var(--mono);font-size:32px;font-weight:600;color:{kospi_color};margin-bottom:24px">
        {data['kospi_current']} <span style="font-size:16px">{kospi_arrow} {data['kospi_change_pct']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">HIGH</span>
        <span class="forecast-val" style="color:var(--green)">{forecast['high']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">BASE</span>
        <span class="forecast-val" style="color:var(--gold)">{forecast['base']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">LOW</span>
        <span class="forecast-val" style="color:var(--red)">{forecast['low']}</span>
      </div>
      <canvas id="kospiChart" style="margin-top:24px;max-height:120px"></canvas>
    </div>
  </div>
  <div class="grid-2" style="margin-top:24px">
    <div class="card">
      <div class="card-title">에이전트 가중치</div>
      <canvas id="weightsChart" style="max-height:220px"></canvas>
    </div>
    <div class="card">
      <div class="card-title">섹터 방향</div>
      <div class="sector-grid">{sector_html}</div>
    </div>
  </div>
</div>
<script>
function showTab(e, id) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}}
new Chart(document.getElementById('weightsChart'), {{
  type: 'doughnut',
  data: {{ {weights_js} }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color: '#e2e8f0', font: {{ family: 'Outfit' }} }} }} }}
  }}
}});
new Chart(document.getElementById('kospiChart'), {{
  type: 'bar',
  data: {{
    labels: ['LOW', 'BASE', 'HIGH'],
    datasets: [{{
      data: [{_chart_val(forecast['low'])}, {_chart_val(forecast['base'])}, {_chart_val(forecast['high'])}],
      backgroundColor: ['#ef4444aa', '#f5c518aa', '#22c55eaa'],
      borderRadius: 4
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
      y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }}
    }}
  }}
}});
</script>
</body>
</html>"""


# ── public entry point ─────────────────────────────────────────────────────────

def generate(
    date: str,
    out_dir: Path = OUTPUT_DIR,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
    live: bool = True,
) -> Path:
    """Assemble data, render HTML, write file. Returns output Path."""
    data     = assemble_dashboard_data(date, temp_dir=temp_dir,
                                       reports_dir=reports_dir, live=live)
    html     = render_html(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{date}_주간투자분析_대시보드.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
