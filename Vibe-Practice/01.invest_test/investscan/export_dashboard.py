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

# ── sector display name mapping (English key → Korean) ─────────────────────────

_SECTOR_KO: dict[str, str] = {
    "semiconductor":           "반도체",
    "semiconductor_equipment": "반도체 장비",
    "ai_platform":             "AI 플랫폼",
    "technology":              "기술",
    "optical_network":         "광통신",
    "cybersecurity":           "사이버보안",
    "power_infrastructure":    "전력 인프라",
    "nuclear":                 "원자력",
    "energy":                  "에너지",
    "battery_ev":              "배터리·EV",
    "automotive":              "자동차",
    "shipbuilding":            "조선",
    "defense":                 "방산",
    "steel_materials":         "철강·소재",
    "chemicals":               "화학",
    "financials":              "금융",
    "biotech":                 "바이오",
    "telecom":                 "통신",
    "entertainment":           "엔터",
    "consumer":                "소비재",
}


# ── TypedDicts ─────────────────────────────────────────────────────────────────

class KospiForecast(TypedDict):
    low:  str
    base: str
    high: str


class WatchlistData(TypedDict):
    date:                    str
    cat_a:                   list[str]
    cat_b:                   list[str]
    p6_not_passed:           list[str]
    agent_weights:           dict[str, float]
    base_sector_directions:  dict[str, str]
    final_sector_confidence: dict[str, float]


class RiskScenario(TypedDict):
    name:        str
    probability: int


class TargetScenario(TypedDict):
    price:  str   # "80,000원"
    upside: str   # "+32.7%"


class StockDetail(TypedDict):
    ticker:          str
    category:        str   # "Cat A" / "Cat B" / "P6 미통과"
    # Live or pipeline financial metrics
    per:             str
    pbr:             str
    roe:             str
    eps:             str
    market_cap:      str
    foreign_ratio:   str
    # Target price scenarios
    target_bull:     TargetScenario
    target_base:     TargetScenario
    target_bear:     TargetScenario
    # DCA entry prices
    dca_aggressive:  str
    dca_ideal:       str
    dca_conservative: str
    stop_loss:       str
    # Investment rationale (up to 4 bullets)
    key_rationale:   list[str]


class StockCard(TypedDict):
    ticker:     str
    name:       str
    current:    str
    change_pct: str
    direction:  str
    sector:     str
    confidence: str
    target:     str


class DashboardData(TypedDict):
    date:               str
    pipeline_version:   str
    kospi_current:      str
    kospi_change_pct:   str
    kospi_direction:    str
    kospi_forecast:     KospiForecast
    cat_a:              list[StockCard]
    cat_b:              list[StockCard]
    p6_not_passed:      list[StockCard]
    agent_weights:      dict[str, float]
    sector_directions:  dict[str, str]
    risk_scenarios:     list[RiskScenario]
    overall_bias:       str
    overall_confidence: str
    stock_details:      dict[str, StockDetail]
    sector_stocks:      dict[str, list[str]]   # sector_key → [ticker, ...]


# ── helper: sector/name lookup from YAML config ────────────────────────────────

def _load_ticker_sector_map() -> dict[str, tuple[str, str]]:
    """Returns {ticker: (sector_key, yaml_display_name)} from sector_stock_map.yaml."""
    yaml_path = _PROJECT_ROOT / "config" / "sector_stock_map.yaml"
    if not yaml_path.exists():
        return {}
    try:
        import yaml
        with open(yaml_path, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        result: dict[str, tuple[str, str]] = {}
        for sector_key, sector_data in d.get("sectors", {}).items():
            for stock in sector_data.get("sample_stocks", []):
                code = stock.get("code", "")
                name = stock.get("name", "")
                if code:
                    result[code] = (sector_key, name)
        return result
    except Exception:
        return {}


def _extract_korean_name(yaml_name: str) -> str:
    m = re.search(r"\(([^)]+)\)", yaml_name)
    if m:
        korean = m.group(1)
        if any("\uAC00" <= c <= "\uD7A3" for c in korean):
            return korean
    return yaml_name


# ── agent context loader ───────────────────────────────────────────────────────

def _load_agent_context(date: str, temp_dir: Path = TEMP_DIR) -> dict:
    """Load agent_context_{date}.json for financial metrics. Returns {} on failure."""
    path = temp_dir / f"agent_context_{date}.json"
    if not path.exists():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ── stock detail parser ────────────────────────────────────────────────────────

def _parse_target_scenarios(section_text: str) -> dict[str, TargetScenario]:
    """Parse Bull/Base/Bear target price rows from a stock section."""
    results: dict[str, TargetScenario] = {}
    for scenario in ("Bull", "Base", "Bear"):
        m = re.search(
            rf"\|\s*\*\*{scenario}\*\*\s*\|([^|]+)\|([^|]+)\|",
            section_text,
        )
        if not m:
            results[scenario] = TargetScenario(price="N/A", upside="N/A")
            continue
        price_cell  = m.group(1)
        upside_cell = m.group(2)
        # Take the last "NNN원" occurrence (handles "X원 → **Y원**")
        prices = re.findall(r"[\d,]+원", price_cell)
        price  = prices[-1] if prices else "N/A"
        upside_m = re.search(r"([+\-][\d.]+%)", upside_cell)
        upside   = upside_m.group(1) if upside_m else "N/A"
        results[scenario] = TargetScenario(price=price, upside=upside)
    return results


def _parse_dca(section_text: str) -> tuple[str, str, str]:
    """Returns (aggressive, ideal, conservative) DCA prices."""
    def _find(label: str) -> str:
        m = re.search(rf"{label}:\s*(?:→\s*)?(?:\*\*)?([\d,]+원)", section_text)
        if not m:
            return "N/A"
        return m.group(1)

    agg  = _find("적극적\\s*매수")
    idl  = _find("이상적\\s*매수")
    cons = _find("보수적\\s*매수")
    # Fallback conservative to stop-loss
    if cons == "N/A":
        sl_m = re.search(r"스탑로스[^:]*:\s*(?:.*?→\s*)?(?:\*\*)?([\d,]+원)", section_text)
        cons = sl_m.group(1) if sl_m else "N/A"
    return agg, idl, cons


def _parse_rationale(section_text: str) -> list[str]:
    """Extract up to 4 key investment rationale bullets."""
    # Look for bullet-point sections
    bullets: list[str] = []
    for m in re.finditer(r"^[-*]\s+(.+)$", section_text, re.MULTILINE):
        line = m.group(1).strip()
        # Remove bold markers for cleaner display
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        # Skip very short or meta lines
        if len(line) < 15 or line.startswith("주의") or line.startswith("중요"):
            continue
        bullets.append(line)
        if len(bullets) >= 4:
            break
    return bullets


def _parse_stop_loss(section_text: str) -> str:
    m = re.search(r"스탑로스[^:]*:\s*(?:.*?→\s*)?(?:\*\*)?([\d,]+원)", section_text)
    return m.group(1) if m else "N/A"


def load_stock_details(
    date: str,
    temp_dir: Path = TEMP_DIR,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, StockDetail]:
    """Parse section 6 of the weekly report + agent_context for per-stock details.

    Returns empty dict on any failure.
    """
    report_path = reports_dir / f"weekly-report-{date}.md"
    if not report_path.exists():
        return {}
    try:
        report_text = report_path.read_text(encoding="utf-8")
    except Exception:
        return {}

    # Load financial metrics from agent_context
    ctx    = _load_agent_context(date, temp_dir=temp_dir)
    stocks_ctx: dict = ctx.get("naver_finance", {}).get("stocks", {})

    # Find section 6 start
    sec6_start = report_text.find("## 섹션 6:")
    if sec6_start < 0:
        sec6_start = 0
    sec6_text = report_text[sec6_start:]

    # Split into per-stock sections at #### headers
    raw_sections = re.split(r"\n(?=####\s)", sec6_text)

    # Determine category per ticker (from confirmed_watchlist for the date)
    wl_path = temp_dir / f"confirmed_watchlist_{date}.json"
    cat_a_set: set[str] = set()
    cat_b_set: set[str] = set()
    if wl_path.exists():
        try:
            raw_wl = json.loads(wl_path.read_text(encoding="utf-8"))
            cat_a_set = set(raw_wl.get("cat_a", []))
            cat_b_set = set(raw_wl.get("cat_b", []))
        except Exception:
            pass

    details: dict[str, StockDetail] = {}

    for section in raw_sections:
        # Extract ticker code from #### header
        header_m = re.match(
            r"####[^(]*\((?:[^,)]+,\s*)?(\d{5,6})",
            section,
        )
        if not header_m:
            continue
        ticker = header_m.group(1).strip()

        # Determine category
        if ticker in cat_a_set:
            category = "Cat A"
        elif ticker in cat_b_set:
            category = "Cat B"
        else:
            category = "P6 미통과"

        # Financial metrics: prefer agent_context (live data), else "N/A"
        sc = stocks_ctx.get(ticker, {})
        per           = sc.get("per",           "N/A") or "N/A"
        pbr           = sc.get("pbr",           "N/A") or "N/A"
        roe           = sc.get("roe",           "N/A") or "N/A"
        eps           = sc.get("eps",           "N/A") or "N/A"
        market_cap    = sc.get("market_cap",    "N/A") or "N/A"
        foreign_ratio = sc.get("foreign_ratio", "N/A") or "N/A"

        # Parse target scenarios
        targets = _parse_target_scenarios(section)

        # DCA prices
        dca_agg, dca_ideal, dca_cons = _parse_dca(section)

        # Stop-loss
        sl = _parse_stop_loss(section)

        # Key rationale
        rationale = _parse_rationale(section)

        details[ticker] = StockDetail(
            ticker=ticker,
            category=category,
            per=per,
            pbr=pbr,
            roe=roe,
            eps=eps,
            market_cap=market_cap,
            foreign_ratio=foreign_ratio,
            target_bull=targets["Bull"],
            target_base=targets["Base"],
            target_bear=targets["Bear"],
            dca_aggressive=dca_agg,
            dca_ideal=dca_ideal,
            dca_conservative=dca_cons,
            stop_loss=sl,
            key_rationale=rationale,
        )

    return details


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
        final_sector_confidence=raw.get("final_sector_confidence", {}),
    )


def load_kospi_forecast(
    date: str,
    reports_dir: Path = REPORTS_DIR,
) -> KospiForecast:
    path  = reports_dir / f"weekly-report-{date}.md"
    empty = KospiForecast(low="N/A", base="N/A", high="N/A")
    if not path.exists():
        return empty
    text   = path.read_text(encoding="utf-8")
    low_m  = re.search(r"\*\*Low\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    base_m = re.search(r"\*\*Base\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)
    high_m = re.search(r"\*\*High\*\*.*?\*\*([\d,~\-\s]+)\*\*", text)

    def _extract(m: re.Match | None) -> str:
        if not m:
            return "N/A"
        raw = m.group(1).strip()
        raw = re.sub(r"\s*\(.*?\)", "", raw).strip()
        return raw if raw else "N/A"

    return KospiForecast(low=_extract(low_m), base=_extract(base_m),
                         high=_extract(high_m))


def load_risk_scenarios(
    date: str,
    reports_dir: Path = REPORTS_DIR,
) -> list[RiskScenario]:
    path = reports_dir / f"weekly-report-{date}.md"
    if not path.exists():
        return []
    text    = path.read_text(encoding="utf-8")
    results: list[RiskScenario] = []
    header_re = re.compile(r"\*\*시나리오 \d+: .+?\*\*")
    for m in header_re.finditer(text):
        header = m.group(0)
        name_m = re.match(r"\*\*시나리오 \d+: (.+?)(?:\s*\(|$|\*\*$)", header)
        name   = name_m.group(1).strip() if name_m else header
        r2_m   = re.search(r"R2:\s*(\d+)%", header)
        base_m = re.search(r"확률\s*(\d+)%", header)
        prob   = int(r2_m.group(1)) if r2_m else (int(base_m.group(1)) if base_m else 0)
        results.append(RiskScenario(name=name, probability=prob))
    return results


def _parse_overall_bias(date: str, reports_dir: Path = REPORTS_DIR) -> tuple[str, str]:
    path = reports_dir / f"weekly-report-{date}.md"
    if not path.exists():
        return "N/A", "N/A"
    try:
        text   = path.read_text(encoding="utf-8")
        bias_m = re.search(r"전반적 방향: (\w+)", text)
        conf_m = re.search(r"가중 신뢰도: \*\*([\d.]+)\*\*", text)
        return (bias_m.group(1) if bias_m else "N/A",
                conf_m.group(1) if conf_m else "N/A")
    except Exception:
        return "N/A", "N/A"


def _parse_p6_from_report(date: str, reports_dir: Path = REPORTS_DIR) -> list[tuple[str, str]]:
    path = reports_dir / f"weekly-report-{date}.md"
    if not path.exists():
        return []
    try:
        text    = path.read_text(encoding="utf-8")
        pattern = re.compile(r"P6 미통과\s*\|([^|]+)\|\s*(\d{5,6})\s*\|[^|]*\|")
        seen: dict[str, str] = {}
        for m in pattern.finditer(text):
            name   = m.group(1).strip()
            ticker = m.group(2).strip()
            if ticker not in seen:
                seen[ticker] = name
        return list(seen.items())
    except Exception:
        return []


# ── stock card builder ─────────────────────────────────────────────────────────

def _make_stock_card(
    ticker: str,
    live_data: dict,
    sector: str = "N/A",
    confidence: str = "N/A",
    fallback_name: str = "",
) -> StockCard:
    info = live_data.get(ticker, {})
    name = info.get("name", "") or fallback_name or ticker
    return StockCard(
        ticker=ticker,
        name=name,
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
    wl       = load_watchlist(date, temp_dir=temp_dir)
    forecast = load_kospi_forecast(date, reports_dir=reports_dir)

    risk_scenarios                = load_risk_scenarios(date, reports_dir=reports_dir)
    overall_bias, overall_confidence = _parse_overall_bias(date, reports_dir=reports_dir)
    stock_details                 = load_stock_details(date, temp_dir=temp_dir, reports_dir=reports_dir)

    ticker_sector_map  = _load_ticker_sector_map()
    sector_confidences = wl["final_sector_confidence"]

    def _sector_info(ticker: str) -> tuple[str, str, str]:
        if ticker not in ticker_sector_map:
            return "N/A", "N/A", ""
        sector_key, yaml_name = ticker_sector_map[ticker]
        ko_name   = _extract_korean_name(yaml_name)
        sector_ko = _SECTOR_KO.get(sector_key, sector_key)
        conf_raw  = sector_confidences.get(sector_key, "")
        conf_str  = f"{float(conf_raw):.4f}" if conf_raw else "N/A"
        return sector_ko, conf_str, ko_name

    live_tickers      = wl["cat_a"] + wl["cat_b"]
    live_tickers_dict = {t: t for t in live_tickers}
    live_data: dict   = {}
    kospi_index       = None

    if live and live_tickers:
        try:
            live_data = fetch_stocks(live_tickers_dict)
        except Exception as e:
            print(f"  ⚠  주가 조회 실패: {e}")
        try:
            kospi_index = fetch_kospi_index()
        except Exception as e:
            print(f"  ⚠  KOSPI 지수 조회 실패: {e}")

    def _make(ticker: str, ld: dict) -> StockCard:
        sec, conf, ko = _sector_info(ticker)
        return _make_stock_card(ticker, ld, sector=sec, confidence=conf, fallback_name=ko)

    cat_a_cards = [_make(t, live_data) for t in wl["cat_a"]]
    cat_b_cards = [_make(t, live_data) for t in wl["cat_b"]]

    p6_tickers = wl["p6_not_passed"]
    p6_names: dict[str, str] = {}
    if not p6_tickers:
        p6_parsed = _parse_p6_from_report(date, reports_dir=reports_dir)
        if p6_parsed:
            for tk, nm in p6_parsed:
                p6_tickers = p6_tickers + [tk]
                p6_names[tk] = nm
    p6_cards = []
    for t in p6_tickers:
        sec, conf, ko = _sector_info(t)
        fb = p6_names.get(t, ko)
        p6_cards.append(_make_stock_card(t, {}, sector=sec, confidence=conf, fallback_name=fb))

    # Build sector → tickers map for sector modal
    sector_stocks: dict[str, list[str]] = {}
    all_tickers = wl["cat_a"] + wl["cat_b"] + p6_tickers
    for t in all_tickers:
        if t in ticker_sector_map:
            sk = ticker_sector_map[t][0]
            sector_stocks.setdefault(sk, []).append(t)

    return DashboardData(
        date=date,
        pipeline_version="v4.0.0",
        kospi_current=kospi_index["current"]      if kospi_index else "N/A",
        kospi_change_pct=kospi_index["change_pct"] if kospi_index else "N/A",
        kospi_direction=kospi_index["direction"]   if kospi_index else "unknown",
        kospi_forecast=forecast,
        cat_a=cat_a_cards,
        cat_b=cat_b_cards,
        p6_not_passed=p6_cards,
        agent_weights=wl["agent_weights"],
        sector_directions=wl["base_sector_directions"],
        risk_scenarios=risk_scenarios,
        overall_bias=overall_bias,
        overall_confidence=overall_confidence,
        stock_details=stock_details,
        sector_stocks=sector_stocks,
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
    icons  = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}
    color  = colors.get(direction, "#64748b")
    label  = labels.get(direction, direction.upper()[:4])
    icon   = icons.get(direction, "")
    return (f'<span style="color:{color};font-weight:600;font-size:11px">'
            f'{icon} {label}</span>')


def _stock_cards_html(cards: list, category: str = "") -> str:
    if not cards:
        return '<p style="color:var(--text-dim);padding:16px">해당 없음</p>'
    rows = []
    for c in cards:
        arrow = _direction_arrow(c["direction"])
        color = _direction_color(c["direction"])
        rows.append(f"""
        <div class="stock-card" onclick="showStockModal('{c['ticker']}')" tabindex="0" onkeydown="if(event.key==='Enter')showStockModal('{c['ticker']}')">
          <div class="sc-header">
            <span class="sc-name">{c['name']}</span>
            <span class="sc-ticker">{c['ticker']} <span class="sc-click-hint">↗</span></span>
          </div>
          <div class="sc-price" style="color:{color}">
            {c['current']} <span class="sc-arrow">{arrow}</span>
            <span class="sc-pct">{c['change_pct']}</span>
          </div>
          <div class="sc-meta">
            <span class="sc-tag">{c['sector']}</span>
            신뢰도 <strong>{c['confidence']}</strong>
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


def _sector_grid_html(directions: dict, sector_stocks: dict) -> str:
    cells = []
    for sector, direction in sorted(directions.items()):
        badge   = _sector_badge(direction)
        ko      = _SECTOR_KO.get(sector, sector)
        n_stocks = len(sector_stocks.get(sector, []))
        badge_count = f' <span style="color:var(--text-dim);font-size:10px">({n_stocks})</span>' if n_stocks else ""
        cells.append(
            f'<div class="sector-cell" onclick="showSectorModal(\'{sector}\')" tabindex="0" '
            f'onkeydown="if(event.key===\'Enter\')showSectorModal(\'{sector}\')">'
            f'<span class="sector-name">{ko}{badge_count}</span>'
            f'<span class="sector-dir">{badge}</span></div>'
        )
    return "\n".join(cells)


def _risk_scenarios_js(scenarios: list) -> tuple[str, str]:
    visible = sorted([s for s in scenarios if s["probability"] > 0],
                     key=lambda s: s["probability"], reverse=True)

    def _shorten(name: str, max_len: int = 14) -> str:
        return name if len(name) <= max_len else name[:max_len] + "…"

    labels = [f"'{_shorten(s['name'])}'" for s in visible]
    data   = [str(s["probability"]) for s in visible]
    return f"[{','.join(labels)}]", f"[{','.join(data)}]"


def _bias_color(bias: str) -> str:
    return {"BULLISH": "#22c55e", "BEARISH": "#ef4444", "NEUTRAL": "#f5c518"}.get(
        bias.upper(), "#94a3b8"
    )


def _stock_details_json(
    details: dict[str, StockDetail],
    all_cards: list[StockCard],
    ticker_sector_map: dict[str, tuple[str, str]],
) -> str:
    """Serialize stock details + card info into a JavaScript-safe JSON string."""
    merged: dict[str, dict] = {}
    # Index cards by ticker for name/current/change_pct lookup
    card_index: dict[str, StockCard] = {c["ticker"]: c for c in all_cards}

    for ticker, d in details.items():
        card = card_index.get(ticker, {})
        merged[ticker] = {
            "ticker":         ticker,
            "name":           card.get("name", ticker) if card else ticker,
            "category":       d["category"],
            "sector":         card.get("sector", "N/A") if card else "N/A",
            "confidence":     card.get("confidence", "N/A") if card else "N/A",
            "current":        card.get("current", "N/A") if card else "N/A",
            "change_pct":     card.get("change_pct", "N/A") if card else "N/A",
            "direction":      card.get("direction", "unknown") if card else "unknown",
            "per":            d["per"],
            "pbr":            d["pbr"],
            "roe":            d["roe"],
            "eps":            d["eps"],
            "market_cap":     d["market_cap"],
            "foreign_ratio":  d["foreign_ratio"],
            "target_bull_price":  d["target_bull"]["price"],
            "target_bull_upside": d["target_bull"]["upside"],
            "target_base_price":  d["target_base"]["price"],
            "target_base_upside": d["target_base"]["upside"],
            "target_bear_price":  d["target_bear"]["price"],
            "target_bear_upside": d["target_bear"]["upside"],
            "dca_aggressive":    d["dca_aggressive"],
            "dca_ideal":         d["dca_ideal"],
            "dca_conservative":  d["dca_conservative"],
            "stop_loss":         d["stop_loss"],
            "key_rationale":     d["key_rationale"],
        }
    return json.dumps(merged, ensure_ascii=False)


def _sector_details_json(
    directions: dict[str, str],
    confidences: dict[str, float],
    sector_stocks: dict[str, list[str]],
    all_cards: list[StockCard],
) -> str:
    """Serialize sector details for sector modals."""
    card_index: dict[str, StockCard] = {c["ticker"]: c for c in all_cards}
    result: dict[str, dict] = {}
    for sector_key, direction in directions.items():
        tickers = sector_stocks.get(sector_key, [])
        stocks_info = []
        for t in tickers:
            card = card_index.get(t, {})
            stocks_info.append({
                "ticker":   t,
                "name":     card.get("name", t) if card else t,
                "category": card.get("confidence", "N/A") if card else "N/A",
                "current":  card.get("current", "N/A") if card else "N/A",
            })
        conf_val = confidences.get(sector_key, 0)
        result[sector_key] = {
            "key":        sector_key,
            "name_ko":    _SECTOR_KO.get(sector_key, sector_key),
            "direction":  direction,
            "confidence": f"{conf_val:.4f}" if conf_val else "N/A",
            "stocks":     stocks_info,
        }
    return json.dumps(result, ensure_ascii=False)


def render_html(data: DashboardData) -> str:
    """Render DashboardData into a self-contained HTML string."""
    stock_details    = data.get("stock_details", {})      # type: ignore[union-attr]
    sector_stocks    = data.get("sector_stocks", {})       # type: ignore[union-attr]
    risk_scenarios   = data.get("risk_scenarios", [])      # type: ignore[union-attr]
    overall_bias     = data.get("overall_bias", "N/A")     # type: ignore[union-attr]
    overall_confidence = data.get("overall_confidence", "N/A")  # type: ignore[union-attr]

    all_cards     = data["cat_a"] + data["cat_b"] + data["p6_not_passed"]
    cat_a_html    = _stock_cards_html(data["cat_a"],        "Cat A")
    cat_b_html    = _stock_cards_html(data["cat_b"],        "Cat B")
    p6_html       = _stock_cards_html(data["p6_not_passed"],"P6 미통과")
    sector_html   = _sector_grid_html(data["sector_directions"], sector_stocks)
    weights_js    = _weights_js(data["agent_weights"])
    forecast      = data["kospi_forecast"]
    kospi_arrow   = _direction_arrow(data["kospi_direction"])
    kospi_color   = _direction_color(data["kospi_direction"])
    bias_color    = _bias_color(str(overall_bias))

    # Risk scenarios
    has_risk        = any(s["probability"] > 0 for s in risk_scenarios)
    risk_labels_js, risk_data_js = _risk_scenarios_js(risk_scenarios)
    n_risk          = len([s for s in risk_scenarios if s["probability"] > 0])

    # Counts
    n_a  = len(data["cat_a"])
    n_b  = len(data["cat_b"])
    n_p6 = len(data["p6_not_passed"])

    # KOSPI chart value helper
    def _chart_val(s: str) -> str:
        if s == "N/A":
            return "0"
        return s.split("~")[-1].strip().replace(",", "")

    # Build stock details + sector details JSON for JS
    ticker_sector_map = _load_ticker_sector_map()
    stock_details_js  = _stock_details_json(stock_details, all_cards, ticker_sector_map)
    sector_details_js = _sector_details_json(
        data["sector_directions"],
        data.get("final_sector_confidence", {}),  # type: ignore[union-attr]
        sector_stocks,
        all_cards,
    )

    risk_chart_js = ""
    if has_risk:
        risk_chart_js = f"""
new Chart(document.getElementById('riskChart'), {{
  type: 'bar',
  data: {{
    labels: {risk_labels_js},
    datasets: [{{
      data: {risk_data_js},
      backgroundColor: 'rgba(239,68,68,0.65)',
      borderColor: 'rgba(239,68,68,0.9)',
      borderWidth: 1,
      borderRadius: 4,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ callbacks: {{ label: (ctx) => ' ' + ctx.parsed.x + '%' }} }}
    }},
    scales: {{
      x: {{ min:0, max:50, ticks:{{ color:'#94a3b8', callback:(v)=>v+'%' }}, grid:{{ color:'rgba(255,255,255,0.05)' }} }},
      y: {{ ticks:{{ color:'#e2e8f0', font:{{ family:'DM Mono', size:11 }} }}, grid:{{ display:false }} }}
    }}
  }}
}});"""

    risk_card_html = (
        f'<div class="card"><div class="card-title">리스크 시나리오 ({n_risk}개)</div>'
        f'<canvas id="riskChart" style="max-height:300px"></canvas></div>'
        if has_risk else
        '<div class="card"><div class="card-title">리스크 시나리오</div>'
        '<p style="color:var(--text-dim);padding:24px 0">데이터 없음</p></div>'
    )

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
  --bg:#06090f;--bg-2:#0c1220;--bg-3:#111827;--bg-4:#1a2235;
  --border:rgba(255,255,255,0.07);--border-hi:rgba(245,197,24,0.35);
  --gold:#f5c518;--gold-dim:#b38e10;
  --green:#22c55e;--red:#ef4444;--amber:#f59e0b;--blue:#60a5fa;
  --text:#e2e8f0;--text-dim:#64748b;--text-mid:#94a3b8;
  --mono:'DM Mono',monospace;--display:'Bebas Neue',sans-serif;--body:'Outfit',sans-serif;
  --radius:12px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:var(--body);font-size:14px;line-height:1.6;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");pointer-events:none;z-index:0;opacity:0.6}}
.wrap{{position:relative;z-index:1;max-width:1300px;margin:0 auto;padding:0 32px 80px}}
/* Ticker bar */
.ticker{{background:var(--gold);color:#000;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.05em;padding:5px 0;overflow:hidden;white-space:nowrap;position:sticky;top:0;z-index:100}}
.ticker-inner{{display:inline-block;animation:ticker-scroll 30s linear infinite}}
.ticker-inner span{{margin:0 40px}}
@keyframes ticker-scroll{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
/* Header */
.header{{padding:48px 0 24px;border-bottom:1px solid var(--border)}}
.header h1{{font-family:var(--display);font-size:52px;letter-spacing:.05em;color:var(--gold);line-height:1}}
.header .sub{{color:var(--text-mid);font-size:13px;margin-top:8px;font-family:var(--mono)}}
/* Stats pills */
.stats-row{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0 0}}
.stat-pill{{background:var(--bg-2);border:1px solid var(--border);border-radius:8px;padding:10px 18px;display:flex;flex-direction:column;gap:2px}}
.stat-label{{font-family:var(--mono);font-size:10px;letter-spacing:.1em;color:var(--text-dim);text-transform:uppercase}}
.stat-val{{font-family:var(--mono);font-size:18px;font-weight:600}}
/* Layout */
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:32px}}
.grid-full{{margin-top:24px}}
.card{{background:var(--bg-2);border:1px solid var(--border);border-radius:var(--radius);padding:24px}}
.card-title{{font-family:var(--mono);font-size:11px;letter-spacing:.1em;color:var(--gold);text-transform:uppercase;margin-bottom:16px}}
/* Tabs */
.tab-bar{{display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap}}
.tab{{padding:6px 14px;border-radius:6px;font-size:12px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--text-dim);font-family:var(--mono);transition:all .15s}}
.tab.active{{background:var(--gold);color:#000;border-color:var(--gold);font-weight:600}}
.tab-content{{display:none}}.tab-content.active{{display:block}}
/* Cat legend */
.cat-legend{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:14px;font-size:11px;color:var(--text-mid);padding:8px 0;border-bottom:1px solid var(--border)}}
.cat-badge{{display:inline-flex;align-items:center;gap:4px;font-family:var(--mono);font-weight:600;font-size:10px;padding:2px 8px;border-radius:4px;border:1px solid}}
.cat-badge.a{{color:#22c55e;border-color:rgba(34,197,94,.3);background:rgba(34,197,94,.08)}}
.cat-badge.b{{color:#f59e0b;border-color:rgba(245,158,11,.3);background:rgba(245,158,11,.08)}}
.cat-badge.p{{color:#64748b;border-color:rgba(100,116,139,.3);background:rgba(100,116,139,.08)}}
.cat-desc{{color:var(--text-dim)}}
/* Stock cards */
.stock-card{{background:var(--bg-3);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:10px;cursor:pointer;transition:border-color .15s,transform .1s;position:relative}}
.stock-card:hover{{border-color:rgba(245,197,24,.4);transform:translateY(-1px)}}
.sc-header{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}}
.sc-name{{font-weight:600;font-size:14px}}
.sc-ticker{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.sc-click-hint{{color:var(--gold);font-size:10px;opacity:0;transition:opacity .15s}}
.stock-card:hover .sc-click-hint{{opacity:1}}
.sc-price{{font-size:20px;font-weight:600;font-family:var(--mono);margin-bottom:6px}}
.sc-pct{{font-size:13px;margin-left:8px}}
.sc-meta{{font-size:11px;color:var(--text-dim);display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.sc-tag{{background:rgba(255,255,255,0.06);border:1px solid var(--border);border-radius:4px;padding:1px 7px;font-size:10px;color:var(--text-mid)}}
/* KOSPI forecast */
.forecast-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}}
.forecast-row:last-child{{border-bottom:none}}
.forecast-label{{font-family:var(--mono);font-size:11px;color:var(--text-dim)}}
.forecast-val{{font-family:var(--mono);font-size:15px;font-weight:600}}
/* Sector grid */
.sector-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(165px,1fr));gap:8px}}
.sector-cell{{background:var(--bg-3);border:1px solid var(--border);border-radius:6px;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;cursor:pointer;transition:border-color .15s}}
.sector-cell:hover{{border-color:rgba(245,197,24,.4)}}
.sector-name{{font-size:12px;color:var(--text-mid)}}

/* ── MODAL ─────────────────────────────────────────────────── */
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:1000;justify-content:center;align-items:flex-start;padding:60px 20px;overflow-y:auto}}
.modal-overlay.active{{display:flex}}
.modal-box{{background:var(--bg-2);border:1px solid var(--border-hi);border-radius:16px;width:100%;max-width:620px;overflow:hidden;animation:modal-in .2s ease}}
@keyframes modal-in{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
.modal-head{{display:flex;justify-content:space-between;align-items:flex-start;padding:24px 24px 16px;border-bottom:1px solid var(--border)}}
.modal-title{{font-size:22px;font-weight:700;margin-bottom:4px}}
.modal-subtitle{{font-family:var(--mono);font-size:12px;color:var(--text-mid);display:flex;align-items:center;gap:10px}}
.modal-cat{{font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;font-family:var(--mono)}}
.modal-close{{background:none;border:none;color:var(--text-dim);font-size:20px;cursor:pointer;padding:4px 8px;border-radius:6px;transition:color .15s;flex-shrink:0}}
.modal-close:hover{{color:var(--text)}}
.modal-body{{padding:20px 24px 24px;display:flex;flex-direction:column;gap:20px}}
/* Price headline */
.modal-price-row{{display:flex;align-items:baseline;gap:12px}}
.modal-price{{font-family:var(--mono);font-size:30px;font-weight:700}}
.modal-price-change{{font-family:var(--mono);font-size:16px}}
/* Section labels */
.modal-section{{display:flex;flex-direction:column;gap:8px}}
.modal-section-label{{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-dim);padding-bottom:4px;border-bottom:1px solid var(--border)}}
/* Metrics grid */
.metrics-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.metric-cell{{background:var(--bg-3);border-radius:8px;padding:10px 12px}}
.metric-label{{font-size:10px;color:var(--text-dim);font-family:var(--mono);display:block;margin-bottom:2px}}
.metric-value{{font-family:var(--mono);font-size:14px;font-weight:600}}
/* Target prices */
.target-rows{{display:flex;flex-direction:column;gap:6px}}
.target-row{{display:flex;align-items:center;gap:0;background:var(--bg-3);border-radius:8px;overflow:hidden}}
.target-label{{font-family:var(--mono);font-size:11px;font-weight:700;padding:10px 14px;min-width:60px}}
.target-price{{font-family:var(--mono);font-size:14px;font-weight:600;flex:1;padding:10px 0}}
.target-upside{{font-family:var(--mono);font-size:13px;font-weight:600;padding:10px 14px}}
/* DCA grid */
.dca-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}}
.dca-cell{{background:var(--bg-3);border-radius:8px;padding:10px 12px;text-align:center}}
.dca-label{{font-size:10px;color:var(--text-dim);font-family:var(--mono);display:block;margin-bottom:2px}}
.dca-value{{font-family:var(--mono);font-size:13px;font-weight:600}}
/* Rationale list */
.rationale-list{{display:flex;flex-direction:column;gap:8px;padding-left:0;list-style:none}}
.rationale-item{{font-size:13px;color:var(--text-mid);line-height:1.5;padding:8px 12px;background:var(--bg-3);border-radius:6px;border-left:2px solid var(--gold)}}
/* Sector modal stocks */
.sector-stocks-list{{display:flex;flex-direction:column;gap:6px}}
.sector-stock-row{{display:flex;justify-content:space-between;padding:8px 12px;background:var(--bg-3);border-radius:6px;font-family:var(--mono);font-size:12px}}
</style>
</head>
<body>

<!-- Ticker bar -->
<div class="ticker">
  <div class="ticker-inner">
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
    <span>바이어스 {overall_bias} — 합의 신뢰도 {overall_confidence}</span>
    <span>KOSPI <strong>{data['kospi_current']}</strong> {kospi_arrow} {data['kospi_change_pct']}</span>
    <span>InvestScan {data['pipeline_version']}</span>
    <span>기준일 {data['date']}</span>
    <span>바이어스 {overall_bias} — 합의 신뢰도 {overall_confidence}</span>
  </div>
</div>

<div class="wrap">
  <!-- Header + stats -->
  <div class="header">
    <h1>INVESTSCAN</h1>
    <div class="sub">주간 투자 분析 대시보드 &nbsp;|&nbsp; {data['date']} &nbsp;|&nbsp; {data['pipeline_version']}</div>
    <div class="stats-row">
      <div class="stat-pill">
        <span class="stat-label">전체 바이어스</span>
        <span class="stat-val" style="color:{bias_color}">{overall_bias}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">에이전트 합의</span>
        <span class="stat-val">{overall_confidence}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Cat A 종목</span>
        <span class="stat-val" style="color:var(--green)">{n_a}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Cat B 종목</span>
        <span class="stat-val" style="color:var(--amber)">{n_b}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">P6 미통과</span>
        <span class="stat-val" style="color:var(--text-dim)">{n_p6}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">리스크 시나리오</span>
        <span class="stat-val" style="color:var(--red)">{n_risk}</span>
      </div>
    </div>
  </div>

  <!-- Row 1: P6 Portfolio + KOSPI Forecast -->
  <div class="grid-2">
    <div class="card">
      <div class="card-title">P6 포트폴리오</div>
      <div class="cat-legend">
        <span><span class="cat-badge a">● Cat A</span>&nbsp;<span class="cat-desc">신뢰도 ≥0.65 · 즉시 매수 권장</span></span>
        <span><span class="cat-badge b">● Cat B</span>&nbsp;<span class="cat-desc">신뢰도 0.50~0.65 · 테마 포지션</span></span>
        <span><span class="cat-badge p">● P6 미통과</span>&nbsp;<span class="cat-desc">임계값 미달 · 서사적 이해만</span></span>
      </div>
      <div class="tab-bar">
        <button class="tab active" onclick="showTab(event,'tab-a')">Cat A ({n_a})</button>
        <button class="tab" onclick="showTab(event,'tab-b')">Cat B ({n_b})</button>
        <button class="tab" onclick="showTab(event,'tab-p6')">P6미통과 ({n_p6})</button>
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
        <span class="forecast-label">▲ HIGH 시나리오</span>
        <span class="forecast-val" style="color:var(--green)">{forecast['high']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">◆ BASE 시나리오</span>
        <span class="forecast-val" style="color:var(--gold)">{forecast['base']}</span>
      </div>
      <div class="forecast-row">
        <span class="forecast-label">▼ LOW 시나리오</span>
        <span class="forecast-val" style="color:var(--red)">{forecast['low']}</span>
      </div>
      <canvas id="kospiChart" style="margin-top:24px;max-height:120px"></canvas>
    </div>
  </div>

  <!-- Row 2: Agent Weights + Risk Scenarios -->
  <div class="grid-2">
    <div class="card">
      <div class="card-title">에이전트 가중치</div>
      <canvas id="weightsChart" style="max-height:240px"></canvas>
    </div>
    {risk_card_html}
  </div>

  <!-- Row 3: Sector Direction Grid -->
  <div class="grid-full">
    <div class="card">
      <div class="card-title">섹터 방향 <span style="font-size:10px;color:var(--text-dim);font-weight:400;font-family:var(--body)">(클릭하여 섹터 상세 보기)</span></div>
      <div class="sector-grid">{sector_html}</div>
    </div>
  </div>
</div>

<!-- ── Stock detail modal ──────────────────────────────────── -->
<div class="modal-overlay" id="stockModal" onclick="closeStockModal(event)">
  <div class="modal-box" id="stockModalBox">
    <div class="modal-head">
      <div>
        <div class="modal-title" id="md-name">—</div>
        <div class="modal-subtitle">
          <span id="md-ticker" style="color:var(--text-dim)"></span>
          <span class="modal-cat" id="md-cat"></span>
          <span id="md-sector" style="color:var(--text-mid)"></span>
        </div>
      </div>
      <button class="modal-close" onclick="document.getElementById('stockModal').classList.remove('active')">✕</button>
    </div>
    <div class="modal-body">
      <!-- Current price -->
      <div class="modal-price-row">
        <span class="modal-price" id="md-price">—</span>
        <span class="modal-price-change" id="md-change">—</span>
      </div>
      <!-- Financial metrics -->
      <div class="modal-section">
        <div class="modal-section-label">재무 지표</div>
        <div class="metrics-grid">
          <div class="metric-cell"><span class="metric-label">PER</span><span class="metric-value" id="md-per">—</span></div>
          <div class="metric-cell"><span class="metric-label">PBR</span><span class="metric-value" id="md-pbr">—</span></div>
          <div class="metric-cell"><span class="metric-label">ROE</span><span class="metric-value" id="md-roe">—</span></div>
          <div class="metric-cell"><span class="metric-label">EPS</span><span class="metric-value" id="md-eps">—</span></div>
          <div class="metric-cell"><span class="metric-label">시가총액</span><span class="metric-value" id="md-mktcap">—</span></div>
          <div class="metric-cell"><span class="metric-label">외국인</span><span class="metric-value" id="md-foreign">—</span></div>
        </div>
      </div>
      <!-- Target prices -->
      <div class="modal-section">
        <div class="modal-section-label">목표주가 (5인 에이전트 합의)</div>
        <div class="target-rows">
          <div class="target-row">
            <span class="target-label" style="background:rgba(34,197,94,.15);color:#22c55e">BULL</span>
            <span class="target-price" id="md-bull-price">—</span>
            <span class="target-upside" id="md-bull-up" style="color:#22c55e">—</span>
          </div>
          <div class="target-row">
            <span class="target-label" style="background:rgba(245,197,24,.15);color:#f5c518">BASE</span>
            <span class="target-price" id="md-base-price">—</span>
            <span class="target-upside" id="md-base-up" style="color:#f5c518">—</span>
          </div>
          <div class="target-row">
            <span class="target-label" style="background:rgba(239,68,68,.15);color:#ef4444">BEAR</span>
            <span class="target-price" id="md-bear-price">—</span>
            <span class="target-upside" id="md-bear-up" style="color:#ef4444">—</span>
          </div>
        </div>
      </div>
      <!-- DCA prices -->
      <div class="modal-section" id="md-dca-section">
        <div class="modal-section-label">DCA 분할매수 진입가</div>
        <div class="dca-grid">
          <div class="dca-cell"><span class="dca-label">적극 매수</span><span class="dca-value" id="md-dca-agg">—</span></div>
          <div class="dca-cell"><span class="dca-label">이상 진입</span><span class="dca-value" id="md-dca-ideal" style="color:var(--gold)">—</span></div>
          <div class="dca-cell"><span class="dca-label">보수적/스탑로스</span><span class="dca-value" id="md-dca-cons" style="color:var(--red)">—</span></div>
        </div>
      </div>
      <!-- Key rationale -->
      <div class="modal-section" id="md-rationale-section">
        <div class="modal-section-label">핵심 투자 논거</div>
        <ul class="rationale-list" id="md-rationale"></ul>
      </div>
    </div>
  </div>
</div>

<!-- ── Sector modal ──────────────────────────────────────── -->
<div class="modal-overlay" id="sectorModal" onclick="closeSectorModal(event)">
  <div class="modal-box" id="sectorModalBox" style="max-width:480px">
    <div class="modal-head">
      <div>
        <div class="modal-title" id="sm-name">—</div>
        <div class="modal-subtitle"><span id="sm-conf" style="color:var(--text-mid)"></span></div>
      </div>
      <button class="modal-close" onclick="document.getElementById('sectorModal').classList.remove('active')">✕</button>
    </div>
    <div class="modal-body">
      <div class="modal-section">
        <div class="modal-section-label">방향</div>
        <div id="sm-direction" style="font-size:18px;font-weight:700"></div>
      </div>
      <div class="modal-section" id="sm-stocks-section">
        <div class="modal-section-label">감시 종목</div>
        <div class="sector-stocks-list" id="sm-stocks"></div>
      </div>
    </div>
  </div>
</div>

<script>
// ── Data ─────────────────────────────────────────────────────
const STOCK_DETAILS  = {stock_details_js};
const SECTOR_DETAILS = {sector_details_js};

// ── Tab switching ─────────────────────────────────────────────
function showTab(e, id) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  e.target.classList.add('active');
  document.getElementById(id).classList.add('active');
}}

// ── Stock modal ───────────────────────────────────────────────
function showStockModal(ticker) {{
  const d = STOCK_DETAILS[ticker];
  if (!d) return;

  const dirColors = {{ up:'#22c55e', down:'#ef4444', flat:'#94a3b8', unknown:'#94a3b8' }};
  const catStyle  = {{ 'Cat A':'color:#22c55e;background:rgba(34,197,94,.15);border:1px solid rgba(34,197,94,.3)',
                       'Cat B':'color:#f59e0b;background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3)',
                       'P6 미통과':'color:#64748b;background:rgba(100,116,139,.1);border:1px solid rgba(100,116,139,.3)' }};

  const $ = (id) => document.getElementById(id);
  $('md-name').textContent    = d.name || ticker;
  $('md-ticker').textContent  = d.ticker;
  $('md-cat').textContent     = d.category;
  $('md-cat').style.cssText   = catStyle[d.category] || '';
  $('md-sector').textContent  = d.sector;

  const priceColor = dirColors[d.direction] || '#e2e8f0';
  $('md-price').textContent  = d.current !== 'N/A' ? d.current : '—';
  $('md-price').style.color  = priceColor;
  $('md-change').textContent = d.change_pct !== 'N/A' ? d.change_pct : '—';
  $('md-change').style.color = priceColor;

  $('md-per').textContent    = d.per;
  $('md-pbr').textContent    = d.pbr;
  $('md-roe').textContent    = d.roe;
  $('md-eps').textContent    = d.eps;
  $('md-mktcap').textContent = d.market_cap;
  $('md-foreign').textContent= d.foreign_ratio;

  $('md-bull-price').textContent = d.target_bull_price;
  $('md-bull-up').textContent    = d.target_bull_upside;
  $('md-base-price').textContent = d.target_base_price;
  $('md-base-up').textContent    = d.target_base_upside;
  $('md-bear-price').textContent = d.target_bear_price;
  $('md-bear-up').textContent    = d.target_bear_upside;

  $('md-dca-agg').textContent   = d.dca_aggressive;
  $('md-dca-ideal').textContent = d.dca_ideal;
  $('md-dca-cons').textContent  = d.dca_conservative;

  const ul = $('md-rationale');
  ul.innerHTML = '';
  (d.key_rationale || []).forEach(r => {{
    const li = document.createElement('li');
    li.className = 'rationale-item';
    li.textContent = r;
    ul.appendChild(li);
  }});
  $('md-rationale-section').style.display = d.key_rationale?.length ? '' : 'none';

  document.getElementById('stockModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function closeStockModal(event) {{
  if (event && event.target !== document.getElementById('stockModal')) return;
  document.getElementById('stockModal').classList.remove('active');
  document.body.style.overflow = '';
}}

// ── Sector modal ──────────────────────────────────────────────
function showSectorModal(sectorKey) {{
  const d = SECTOR_DETAILS[sectorKey];
  if (!d) return;

  const dirColors = {{ bullish:'#22c55e', bearish:'#ef4444', neutral:'#f5c518' }};
  const dirLabels = {{ bullish:'🟢 BULLISH — 강세', bearish:'🔴 BEARISH — 약세', neutral:'⚪ NEUTRAL — 중립' }};

  const $ = (id) => document.getElementById(id);
  $('sm-name').textContent = d.name_ko;
  $('sm-conf').textContent = `섹터 신뢰도 ${{d.confidence}}`;
  $('sm-direction').textContent = dirLabels[d.direction] || d.direction;
  $('sm-direction').style.color = dirColors[d.direction] || '#e2e8f0';

  const stocksEl = $('sm-stocks');
  stocksEl.innerHTML = '';
  (d.stocks || []).forEach(s => {{
    const row = document.createElement('div');
    row.className = 'sector-stock-row';
    row.innerHTML = `<span>${{s.name}}</span><span style="color:var(--text-dim)">${{s.ticker}}</span><span style="color:var(--text-dim)">${{s.current}}</span>`;
    stocksEl.appendChild(row);
  }});
  $('sm-stocks-section').style.display = d.stocks?.length ? '' : 'none';

  document.getElementById('sectorModal').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function closeSectorModal(event) {{
  if (event && event.target !== document.getElementById('sectorModal')) return;
  document.getElementById('sectorModal').classList.remove('active');
  document.body.style.overflow = '';
}}

// Keyboard close
document.addEventListener('keydown', (e) => {{
  if (e.key === 'Escape') {{
    document.getElementById('stockModal').classList.remove('active');
    document.getElementById('sectorModal').classList.remove('active');
    document.body.style.overflow = '';
  }}
}});

// ── Charts ────────────────────────────────────────────────────
new Chart(document.getElementById('weightsChart'), {{
  type: 'doughnut',
  data: {{ {weights_js} }},
  options: {{
    responsive: true,
    plugins: {{
      legend: {{
        position: 'right',
        labels: {{ color:'#e2e8f0', font:{{ family:'Outfit', size:12 }}, padding:14 }}
      }}
    }}
  }}
}});

new Chart(document.getElementById('kospiChart'), {{
  type: 'bar',
  data: {{
    labels: ['LOW', 'BASE', 'HIGH'],
    datasets: [{{ data: [{_chart_val(forecast['low'])}, {_chart_val(forecast['base'])}, {_chart_val(forecast['high'])}],
      backgroundColor: ['#ef4444aa', '#f5c518aa', '#22c55eaa'], borderRadius: 4 }}]
  }},
  options: {{
    indexAxis: 'y', responsive: true,
    plugins: {{ legend: {{ display: false }} }},
    scales: {{
      x: {{ ticks:{{ color:'#94a3b8', callback:(v)=>(v/1000).toFixed(0)+'K' }}, grid:{{ color:'rgba(255,255,255,0.05)' }} }},
      y: {{ ticks:{{ color:'#94a3b8' }}, grid:{{ display:false }} }}
    }}
  }}
}});

{risk_chart_js}
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
