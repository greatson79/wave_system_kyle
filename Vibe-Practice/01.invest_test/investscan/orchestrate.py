"""
investscan/orchestrate.py — Data collection + context preparation for Claude Code Agent workflow.

Runs EnvironmentScan and GlobalNews as subprocesses, then builds a unified
agent_context JSON that all 5 analyst agents consume.

Usage:
    python3 -m investscan.orchestrate               # full pipeline
    python3 -m investscan.orchestrate --skip-envscan
    python3 -m investscan.orchestrate --skip-gnews
    python3 -m investscan.orchestrate --prepare-only  # context prep only
    python3 -m investscan.orchestrate --status        # data freshness check
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from investscan import pipeline_tracker as _tracker

# ── External system paths ──────────────────────────────────────────────────────
ENVSCAN_DIR    = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/EnvironmentScan-system-main-v4-main/env-scanning")
ENVSCAN_OUT    = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/EnvironmentScan-system-main-v4-main/env-scanning/raw")

GNEWS_DIR      = Path("/Users/kylechoi/Desktop/Ai_works/Vibe-Practice"
                      "/GlobalNews-Crawling-AgenticWorkflow")
GNEWS_PYTHON   = GNEWS_DIR / ".venv/bin/python"
GNEWS_RAW_BASE = GNEWS_DIR / "data/raw"

TEMP_DIR = Path("output/temp")
SECTOR_MAP_PATH = Path("config/sector_stock_map.yaml")

# ── STEEPs → sector mapping (for dynamic stock selection) ─────────────────────
_STEEPS_TO_SECTORS: dict[str, list[str]] = {
    "T":     ["technology", "semiconductor", "semiconductor_equipment",
               "ai_platform", "optical_network", "cybersecurity", "telecom"],
    "S":     ["biotech", "consumer", "entertainment"],
    "E":     ["financials", "consumer", "energy", "power_infrastructure"],
    "P":     ["defense", "shipbuilding", "cybersecurity"],
    "s":     ["technology", "ai_platform"],
    # Environment variants (EnvScan outputs mixed capitalization)
    "E_ENV": ["energy", "nuclear", "power_infrastructure", "steel_materials", "chemicals"],
    "EENV":  ["energy", "nuclear", "power_infrastructure", "steel_materials", "chemicals"],
    "ENV":   ["energy", "nuclear", "power_infrastructure"],
}

# Sector theme keywords for GlobalNews article scoring
_SECTOR_THEME_KW: dict[str, list[str]] = {
    "semiconductor":           ["semiconductor", "chip", "HBM", "DRAM", "NAND", "fab", "wafer",
                                 "반도체", "파운드리", "칩", "웨이퍼", "삼성전자", "하이닉스"],
    "semiconductor_equipment": ["ASML", "AMAT", "Lam Research", "KLA", "etch", "deposition",
                                 "한미반도체", "원익IPS", "피에스케이", "반도체 장비", "노광"],
    "ai_platform":             ["ChatGPT", "LLM", "AI platform", "NAVER AI", "Kakao AI",
                                 "인공지능 플랫폼", "AI 서비스", "네이버", "하이퍼클로바", "클로바"],
    "technology":              ["AI", "software", "cloud", "platform", "digital", "tech",
                                 "기술", "인공지능", "소프트웨어", "클라우드", "디지털", "플랫폼"],
    "optical_network":         ["optical fiber", "DWDM", "coherent", "optical transceiver",
                                 "광통신", "쏠리드", "오이솔루션", "광케이블", "인피니그루", "광모듈"],
    "cybersecurity":           ["cybersecurity", "ransomware", "hacking", "zero-day", "malware",
                                 "보안", "사이버", "안랩", "방화벽", "악성코드", "취약점"],
    "power_infrastructure":    ["grid", "transformer", "HVDC", "substation", "power grid",
                                 "전력", "변압기", "전력망", "HD현대일렉트릭", "LS Electric", "효성중공업"],
    "nuclear":                 ["nuclear", "SMR", "small modular reactor", "uranium",
                                 "원전", "원자력", "소형모듈원자로", "두산에너빌리티", "우라늄"],
    "energy":                  ["energy", "oil", "gas", "solar", "wind", "renewable",
                                 "에너지", "태양광", "석유", "가스", "발전", "재생에너지"],
    "battery_ev":              ["battery", "LFP", "NMC", "EV", "electric vehicle", "cathode",
                                 "배터리", "전기차", "LG에너지솔루션", "삼성SDI", "SK이노베이션", "양극재"],
    "automotive":              ["automotive", "Hyundai", "Kia", "autonomous", "ADAS",
                                 "자동차", "현대차", "기아", "자율주행", "부품"],
    "shipbuilding":            ["shipbuilding", "LNG carrier", "VLCC", "container ship",
                                 "조선", "HD한국조선해양", "한화오션", "삼성중공업", "LNG선"],
    "defense":                 ["defense", "military", "K2 tank", "K9 howitzer", "aerospace", "weapon",
                                 "방산", "방위", "무기", "한화에어로스페이스", "항공우주", "K방산"],
    "steel_materials":         ["steel", "POSCO", "blast furnace", "hot rolled", "iron ore",
                                 "철강", "포스코홀딩스", "현대제철", "고로", "열연"],
    "chemicals":               ["chemical", "petrochemical", "LG화학", "롯데케미칼", "ethylene",
                                 "화학", "석유화학", "나프타", "에틸렌", "스프레드"],
    "financials":              ["bank", "insurance", "fintech", "credit", "interest rate", "fed",
                                 "은행", "보험", "금융", "핀테크", "대출", "금리"],
    "biotech":                 ["pharma", "drug", "biotech", "medical", "vaccine", "clinical",
                                 "바이오", "제약", "의료", "신약", "임상", "셀트리온"],
    "telecom":                 ["telecom", "5G", "6G", "network", "mobile", "communication",
                                 "통신", "네트워크", "이동통신", "모바일", "KT", "SKT"],
    "entertainment":           ["K-pop", "K-content", "HYBE", "SM", "JYP", "webtoon",
                                 "엔터", "하이브", "콘텐츠", "케이팝", "드라마", "넷플릭스"],
    "consumer":                ["retail", "e-commerce", "consumer", "fashion", "food",
                                 "소비", "유통", "패션", "식품", "음료", "쿠팡"],
}

# Broad investment-relevant keywords for GlobalNews article pre-filter
# (Replaces semiconductor-biased list — covers all sectors evenly)
_BROAD_INVEST_KW: frozenset[str] = frozenset({
    # Finance / macro
    "stock", "market", "invest", "trade", "equity", "fund", "bond",
    "rate", "gdp", "inflation", "recession", "growth", "tariff", "sanction",
    "증시", "주식", "투자", "시장", "금리", "관세", "경제", "성장", "증권",
    # Tech (broad)
    "AI", "technology", "software", "cloud", "data", "cyber", "digital",
    "기술", "인공지능", "소프트웨어", "클라우드", "디지털", "플랫폼",
    # Energy
    "energy", "oil", "gas", "nuclear", "solar", "battery",
    "에너지", "원전", "태양광", "석유", "가스", "배터리",
    # Healthcare
    "pharma", "biotech", "medical", "drug", "바이오", "제약", "의료",
    # Industrial / Auto / Defense
    "automotive", "shipbuilding", "robot", "defense", "aerospace",
    "자동차", "조선", "방산", "로봇", "제조",
    # Semiconductor (present but not dominating)
    "semiconductor", "chip", "HBM", "반도체", "파운드리",
    # Korean market
    "kospi", "kosdaq", "코스피", "코스닥", "한국", "korea",
})


# ── Dynamic sector & stock selection ─────────────────────────────────────────

def _score_sectors(
    signals: list[dict],
    articles: list[dict],
    sectors: dict,
) -> dict[str, float]:
    """
    Score each sector based on EnvScan STEEPs signals and GlobalNews article themes.
    EnvScan signal = 1.0 pt, GlobalNews article match = 0.5 pt per sector.
    Returns {sector_name: score}.
    """
    scores: dict[str, float] = {name: 0.0 for name in sectors}

    # 1. EnvScan STEEPs → sector weight
    for s in signals:
        cat = (s.get("category") or "").strip()
        # Try raw, UPPER, and common variants
        for variant in (cat, cat.upper(), cat.replace("-", "_").upper()):
            mapped = _STEEPS_TO_SECTORS.get(variant, [])
            if mapped:
                for sec in mapped:
                    if sec in scores:
                        scores[sec] += 1.0
                break

    # 2. GlobalNews article themes → sector weight
    for a in articles:
        text = ((a.get("title") or "") + " " + (a.get("body") or "")[:200]).lower()
        for sec, kws in _SECTOR_THEME_KW.items():
            if sec in scores and any(kw.lower() in text for kw in kws):
                scores[sec] += 0.5

    return scores


def _select_dynamic_watchlist(
    signals: list[dict],
    articles: list[dict],
    max_stocks: int = 12,
) -> tuple[dict[str, str], dict[str, float]]:
    """
    Dynamically select Korean stocks based on active sectors detected from
    EnvScan STEEPs signals and GlobalNews article themes.

    Algorithm:
      1. Score all sectors (EnvScan STEEPs counts + GlobalNews keyword matches).
      2. Pick top-N sectors (min 3, at most 6).
      3. Pull sample_stocks from sector_stock_map.yaml for each sector.
      4. Return deduplicated watchlist (up to max_stocks) + raw sector scores.

    Returns ({ticker_code: company_name}, {sector_name: score}).
    The sector scores are forwarded to agent_context.json for M2 bridge
    (synthesize_macro external_scores).
    """
    if not SECTOR_MAP_PATH.exists():
        print(f"  WARN: {SECTOR_MAP_PATH} 없음 — 빈 watchlist 반환")
        return {}, {}

    try:
        import yaml  # pyyaml is in requirements.txt
        data = yaml.safe_load(SECTOR_MAP_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"  WARN: sector_stock_map.yaml 파싱 실패: {exc}")
        return {}, {}

    sectors: dict = data.get("sectors", {})
    if not sectors:
        return {}, {}

    scores = _score_sectors(signals, articles, sectors)
    sorted_secs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Pick top sectors: always at least 3, up to 6 active ones
    positive = [s for s, sc in sorted_secs if sc > 0]
    n_pick = max(3, min(len(positive), 6))
    top_secs = [s for s, _ in sorted_secs[:n_pick]]

    print(f"  [섹터 점수] {[(s, round(sc, 1)) for s, sc in sorted_secs[:8]]}")
    print(f"  [활성 섹터] top-{n_pick}: {top_secs}")

    seen: set[str] = set()
    watchlist: dict[str, str] = {}
    for sec in top_secs:
        for stock in sectors.get(sec, {}).get("sample_stocks", []):
            code = str(stock.get("code", "")).strip()
            name = stock.get("name", "").strip()
            if code and code not in seen:
                seen.add(code)
                watchlist[code] = name
            if len(watchlist) >= max_stocks:
                break
        if len(watchlist) >= max_stocks:
            break

    print(f"  [동적 watchlist] {len(watchlist)}개: {list(watchlist.values())}")
    return watchlist, scores


# ── Phase A: EnvironmentScan ───────────────────────────────────────────────────

def run_envscan(days_back: int = 7) -> bool:
    """Run EnvironmentScan multi-source scan as subprocess. Returns success."""
    print("=" * 60)
    print("Phase A: EnvironmentScan 실행 중...")
    print("=" * 60)
    try:
        _tracker.update_phase("phase_1_envscan", "running")
    except Exception:
        pass
    if not ENVSCAN_DIR.exists():
        print(f"  ERROR: EnvironmentScan 디렉터리 없음: {ENVSCAN_DIR}")
        try:
            _tracker.update_phase("phase_1_envscan", "failed")
        except Exception:
            pass
        return False

    cmd = [sys.executable, "scripts/run_multi_source_scan.py", "--days-back", str(days_back)]
    result = subprocess.run(cmd, cwd=str(ENVSCAN_DIR), capture_output=False)
    if result.returncode != 0:
        print(f"  ERROR: EnvironmentScan 실패 (exit {result.returncode})")
        try:
            _tracker.update_phase("phase_1_envscan", "failed")
        except Exception:
            pass
        return False
    print("  EnvironmentScan 완료")
    try:
        _tracker.update_phase("phase_1_envscan", "completed")
    except Exception:
        pass
    return True


# ── Phase B: GlobalNews ────────────────────────────────────────────────────────

def run_gnews() -> bool:
    """Run GlobalNews full crawl via .venv Python. Returns success."""
    print("=" * 60)
    print("Phase B: GlobalNews 크롤링 시작...")
    print("  (116개 사이트 크롤링 — 30~90분 소요)")
    print("=" * 60)
    try:
        _tracker.update_phase("phase_1_gnews", "running")
    except Exception:
        pass
    if not GNEWS_PYTHON.exists():
        print(f"  ERROR: GlobalNews .venv 없음: {GNEWS_PYTHON}")
        try:
            _tracker.update_phase("phase_1_gnews", "failed")
        except Exception:
            pass
        return False

    # --mode full --sites: RSS-only sites to avoid Patchright browser (SIGSEGV exit 139)
    cmd = [str(GNEWS_PYTHON), "main.py", "--mode", "full",
           "--sites", "donga,yna,chosun,mk,hankyung,mt"]
    result = subprocess.run(cmd, cwd=str(GNEWS_DIR), capture_output=False)
    if result.returncode != 0:
        print(f"  ERROR: GlobalNews 실패 (exit {result.returncode})")
        try:
            _tracker.update_phase("phase_1_gnews", "failed")
        except Exception:
            pass
        return False
    print("  GlobalNews 크롤링 완료")
    try:
        _tracker.update_phase("phase_1_gnews", "completed")
    except Exception:
        pass
    return True


# ── Phase C: Context preparation ───────────────────────────────────────────────

def _load_envscan_signals() -> list[dict]:
    """Load signals from EnvironmentScan daily-scan-*.json output files.
    Supports both formats:
      - daily-scan-*.json: {"scan_metadata": {...}, "items": [...]}
      - WF*.json (legacy): list or {"signals": [...]}
    Loads the most recent 7 days of files.
    """
    from datetime import date, timedelta
    signals: list[dict] = []

    # Collect candidate files: daily-scan-*.json (primary) + WF*.json (legacy)
    candidate_files: list[Path] = []
    cutoff = date.today() - timedelta(days=7)
    for f in sorted(ENVSCAN_OUT.glob("daily-scan-*.json")):
        # Extract date from filename e.g. daily-scan-2026-04-05.json
        stem = f.stem  # "daily-scan-2026-04-05"
        parts = stem.split("-")
        if len(parts) >= 4:
            try:
                file_date = date(int(parts[2]), int(parts[3]), int(parts[4]))
                if file_date >= cutoff:
                    candidate_files.append(f)
            except (ValueError, IndexError):
                candidate_files.append(f)
    # Fallback: WF*.json legacy format
    for f in sorted(ENVSCAN_OUT.glob("WF*.json")):
        candidate_files.append(f)

    for scan_file in candidate_files:
        try:
            raw = json.loads(scan_file.read_text(encoding="utf-8"))
            # Format 1: {"scan_metadata": {...}, "items": [...]} — daily-scan format
            if isinstance(raw, dict) and "items" in raw:
                for s in raw["items"]:
                    src = s.get("source", {})
                    signals.append({
                        "source_file": scan_file.name,
                        "title":       s.get("title", ""),
                        "summary":     s.get("content", {}).get("abstract", ""),
                        "category":    s.get("preliminary_category", ""),
                        "date":        src.get("published_date", ""),
                        "url":         src.get("url", ""),
                    })
            # Format 2: raw list — WF1 legacy
            elif isinstance(raw, list):
                for s in raw:
                    signals.append({
                        "source_file": scan_file.name,
                        "title":       s.get("title", ""),
                        "summary":     s.get("summary", ""),
                        "category":    s.get("preliminary_category", ""),
                        "date":        s.get("published_date", ""),
                        "url":         s.get("url", ""),
                    })
            # Format 3: {"signals": [...]} — WF2/WF3 legacy
            elif isinstance(raw, dict) and "signals" in raw:
                entries = raw["signals"]
                if isinstance(entries, list):
                    for s in entries:
                        signals.append({
                            "source_file": scan_file.name,
                            "title":       s.get("title", ""),
                            "summary":     s.get("abstract_summary", s.get("summary", "")),
                            "category":    s.get("preliminary_category", s.get("steeps_category", "")),
                            "date":        s.get("published_date", ""),
                            "url":         s.get("url", ""),
                        })
        except Exception as e:
            print(f"  WARN: {scan_file.name} 로드 실패: {e}")
    return signals


def _load_gnews_articles(top_n: int = 200) -> list[dict]:
    """Load most recent GlobalNews articles, filter for investment relevance.
    Uses broad cross-sector keywords (not semiconductor-biased).
    """
    articles: list[dict] = []
    raw_dirs = sorted(GNEWS_RAW_BASE.glob("????-??-??"), reverse=True)
    # Find latest directory that actually has articles (skip empty dirs)
    jsonl_file = None
    for d in raw_dirs:
        candidate = d / "all_articles.jsonl"
        if candidate.exists() and candidate.stat().st_size > 0:
            jsonl_file = candidate
            break
    if jsonl_file is None:
        return []

    for line in jsonl_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            a = json.loads(line)
            title = (a.get("title") or "").lower()
            body  = (a.get("body") or "")[:300].lower()
            combined = title + " " + body
            if any(kw.lower() in combined for kw in _BROAD_INVEST_KW):
                articles.append({
                    "title":      a.get("title", ""),
                    "body":       (a.get("body") or "")[:400],
                    "source":     a.get("source_name", ""),
                    "language":   a.get("language", ""),
                    "date":       a.get("published_at", "")[:10],
                    "category":   a.get("category", ""),
                })
        except Exception:
            continue
        if len(articles) >= top_n:
            break
    return articles


def _load_naver_finance(tickers: dict[str, str] | None = None) -> dict[str, dict]:
    """Fetch real-time stock data from Naver Finance for dynamically selected tickers."""
    try:
        from investscan.naver_finance import fetch_stocks
        return fetch_stocks(tickers=tickers, delay=0.5)
    except Exception as e:
        print(f"  WARN: Naver Finance 수집 실패: {e}")
        return {}


def _load_market_indices() -> dict:
    """Fetch current KOSPI and KOSDAQ index values from Naver Finance."""
    try:
        from investscan.naver_finance import fetch_kospi_index
        kospi  = fetch_kospi_index("KOSPI")
        kosdaq = fetch_kospi_index("KOSDAQ")
        return {
            "kospi":      dict(kospi)  if kospi  else {"current": "N/A"},
            "kosdaq":     dict(kosdaq) if kosdaq else {"current": "N/A"},
            "fetched_at": datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"  WARN: 시장 지수 수집 실패: {e}")
        return {"kospi": {"current": "N/A"}, "kosdaq": {"current": "N/A"}}


def prepare_context(run_date: str | None = None) -> Path:
    """
    Build unified agent_context JSON from all available data sources.
    Returns path to written context file.
    """
    today = run_date or date.today().isoformat()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    out_path = TEMP_DIR / f"agent_context_{today}.json"

    print("=" * 60)
    print("Phase C: 에이전트 컨텍스트 준비 중...")
    print("=" * 60)
    try:
        _tracker.update_phase("phase_2", "running")
    except Exception:
        pass

    # Load signals and articles first — needed for dynamic sector detection
    envscan_signals = _load_envscan_signals()
    gnews_articles  = _load_gnews_articles(top_n=150)

    # Dynamically select watchlist from active sectors (no hardcoded tickers)
    # Returns (watchlist, scores) — scores forwarded to context for M2 bridge
    watchlist, scores = _select_dynamic_watchlist(envscan_signals, gnews_articles, max_stocks=12)

    # Fetch Naver Finance prices for dynamically selected stocks
    stock_data = _load_naver_finance(tickers=watchlist if watchlist else None)

    # Fetch current market index levels (KOSPI / KOSDAQ) — agents must use these, not training data
    market_indices = _load_market_indices()

    # Summarise EnvScan by category
    cat_dist = dict(Counter(s["category"] for s in envscan_signals))

    # Convert stock StockInfo TypedDicts to plain dicts
    stocks_plain = {k: dict(v) for k, v in stock_data.items()}

    context = {
        "run_date":   today,
        "created_at": datetime.now().isoformat(),
        "market_indices": market_indices,  # KOSPI/KOSDAQ current levels — agents MUST use these
        "envscan": {
            "total":              len(envscan_signals),
            "category_breakdown": cat_dist,
            "signals":            envscan_signals,
        },
        "gnews": {
            "total":    len(gnews_articles),
            "articles": gnews_articles,
        },
        "naver_finance": {
            "fetched_at": datetime.now().isoformat(),
            "stocks":     stocks_plain,
        },
        "watchlist": watchlist,      # dynamically derived from EnvScan + GlobalNews
        "sector_scores": scores,     # M2 bridge: raw scores → synthesize_macro external_scores
    }

    out_path.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    kospi_val = market_indices.get("kospi", {}).get("current", "N/A")
    kosdaq_val = market_indices.get("kosdaq", {}).get("current", "N/A")
    print(f"  시장 지수: KOSPI {kospi_val} | KOSDAQ {kosdaq_val}")
    print(f"  EnvScan 신호: {len(envscan_signals)}건 | Category: {cat_dist}")
    print(f"  GlobalNews:   {len(gnews_articles)}건 (광역 섹터 필터)")
    print(f"  Naver Finance: {len(stocks_plain)}개 종목 (동적 선정)")
    print(f"  Context 저장: {out_path}")
    try:
        _tracker.update_phase("phase_2", "completed")
    except Exception:
        pass
    return out_path


# ── Data freshness check ───────────────────────────────────────────────────────

def check_needs_refresh(max_age_days: int = 3) -> bool:
    """
    Returns True if any data source is stale (age >= max_age_days).
    Used by invest-analysis.md to decide whether to skip Phase 1.
    """
    # Check EnvScan: daily-scan-*.json (primary) or WF*.json (legacy)
    scan_files = (sorted(ENVSCAN_OUT.glob("daily-scan-*.json")) or
                  sorted(ENVSCAN_OUT.glob("WF*.json")))
    if not scan_files:
        return True
    mtime = datetime.fromtimestamp(scan_files[-1].stat().st_mtime)
    if (datetime.now() - mtime).days >= max_age_days:
        return True

    # Check GlobalNews: most recent date-subdirectory in data/raw/
    raw_dirs = sorted(GNEWS_RAW_BASE.glob("????-??-??"), reverse=True)
    if not raw_dirs:
        return True
    try:
        gnews_age = (date.today() - date.fromisoformat(raw_dirs[0].name)).days
    except Exception:
        return True
    return gnews_age >= max_age_days


# ── Status report ──────────────────────────────────────────────────────────────

def show_status() -> None:
    """Print data freshness status for all sources."""
    print("=" * 60)
    print("InvestScan 데이터 현황")
    print("=" * 60)

    # EnvScan
    scan_files = sorted(ENVSCAN_OUT.glob("daily-scan-*.json")) or sorted(ENVSCAN_OUT.glob("WF*.json"))
    if scan_files:
        latest_wf = scan_files[-1]
        mtime = datetime.fromtimestamp(latest_wf.stat().st_mtime)
        age = (datetime.now() - mtime).days
        print(f"  EnvironmentScan: {latest_wf.name}  ({age}일 전)")
    else:
        print("  EnvironmentScan: 데이터 없음")

    # GlobalNews
    raw_dirs = sorted(GNEWS_RAW_BASE.glob("????-??-??"), reverse=True)
    if raw_dirs:
        latest_dir = raw_dirs[0]
        jsonl = latest_dir / "all_articles.jsonl"
        if jsonl.exists():
            lines = sum(1 for _ in jsonl.open())
            age_days = (date.today() - date.fromisoformat(latest_dir.name)).days
            print(f"  GlobalNews:      {latest_dir.name}  ({lines}건, {age_days}일 전)")
        else:
            print(f"  GlobalNews:      {latest_dir.name} — articles 없음")
    else:
        print("  GlobalNews:      데이터 없음")

    # Context files
    contexts = sorted(TEMP_DIR.glob("agent_context_*.json")) if TEMP_DIR.exists() else []
    if contexts:
        print(f"  Agent context:   {contexts[-1].name}")
    else:
        print("  Agent context:   없음 (--prepare-only 실행 필요)")
    print("=" * 60)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan 데이터 수집 오케스트레이터")
    parser.add_argument("--skip-envscan",   action="store_true", help="EnvironmentScan 실행 건너뜀")
    parser.add_argument("--skip-gnews",     action="store_true", help="GlobalNews 실행 건너뜀")
    parser.add_argument("--prepare-only",   action="store_true", help="컨텍스트 준비만 (수집 없음)")
    parser.add_argument("--status",         action="store_true", help="데이터 현황만 출력")
    parser.add_argument("--needs-refresh",  action="store_true",
                        help="데이터 신선도 확인: 3일 이상 오래됐으면 STALE, 아니면 FRESH 출력")
    parser.add_argument("--date",           help="실행 날짜 YYYY-MM-DD (기본: 오늘)")
    args = parser.parse_args()

    if args.needs_refresh:
        stale = check_needs_refresh()
        print("STALE" if stale else "FRESH")
        return 0

    if args.status:
        show_status()
        return 0

    if not args.prepare_only:
        if not args.skip_envscan:
            if not run_envscan():
                print("  WARNING: EnvironmentScan 실패 — 기존 데이터로 계속 진행")
        if not args.skip_gnews:
            if not run_gnews():
                print("  WARNING: GlobalNews 실패 — 기존 데이터로 계속 진행")

    ctx_path = prepare_context(run_date=args.date)
    print(f"\n  컨텍스트 파일 준비 완료: {ctx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
