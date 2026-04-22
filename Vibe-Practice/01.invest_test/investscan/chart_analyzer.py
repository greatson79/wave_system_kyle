"""
chart_analyzer.py — Stock chart generator using pykrx + mplfinance.

Generates candlestick + MA(5/20) + volume charts for Korean stocks,
saves as PNG, and provides embed helpers for the PDF exporter.

Output:
  output/charts/{TICKER}_{DATE}.png

Usage:
    python3 -m investscan.chart_analyzer              # default watchlist
    python3 -m investscan.chart_analyzer --ticker 005930 000660
    python3 -m investscan.chart_analyzer --ticker 005930 --dry-run
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", "Glyph")          # Korean glyph fallback warnings
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

import matplotlib
matplotlib.use("Agg")   # non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import matplotlib.patches as mpatches

CHARTS_DIR = Path("output/charts")
_FONT_CACHE = Path.home() / ".cache" / "investscan" / "fonts"


def _setup_korean_font() -> None:
    """Register Apple SD Gothic Neo for matplotlib (suppresses Korean glyph warnings)."""
    regular = _FONT_CACHE / "AppleSDGothicNeo_regular.ttf"
    if not regular.exists():
        # Extract from system TTC if not yet cached
        try:
            from fontTools.ttLib import TTCollection
            _FONT_CACHE.mkdir(parents=True, exist_ok=True)
            ttc = TTCollection("/System/Library/Fonts/AppleSDGothicNeo.ttc")
            ttc[0].save(str(regular))
        except Exception:
            return
    fm.fontManager.addfont(str(regular))
    prop = fm.FontProperties(fname=str(regular))
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False


_setup_korean_font()

# Default watchlist: 종목코드 → 한글명
DEFAULT_TICKERS: dict[str, str] = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "042700": "한미반도체",
}

CHART_PERIOD_DAYS = 30   # 최근 N일


# ── data fetch ────────────────────────────────────────────────────────────────

def fetch_ohlcv(ticker: str, days: int = CHART_PERIOD_DAYS):
    """Fetch OHLCV DataFrame from pykrx. Returns None if unavailable."""
    try:
        from pykrx import stock
        import pandas as pd

        end   = date.today()
        start = end - timedelta(days=days + 10)   # buffer for weekends/holidays

        df = stock.get_market_ohlcv(
            start.strftime("%Y%m%d"),
            end.strftime("%Y%m%d"),
            ticker,
        )
        if df is None or df.empty:
            return None

        df.index.name = "Date"
        df.columns = ["Open", "High", "Low", "Close", "Volume", "Change"]
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df = df[df["Volume"] > 0]                # remove non-trading days
        df = df.tail(days)                        # keep last N trading days
        return df

    except Exception as e:
        print(f"  ⚠  {ticker} 데이터 수집 실패: {e}")
        return None


# ── chart generation ──────────────────────────────────────────────────────────

def _draw_chart(df, ticker: str, name: str, out_path: Path) -> None:
    """Draw candlestick + MA + volume chart and save to PNG."""
    import mplfinance as mpf
    import pandas as pd

    # Add moving averages
    df = df.copy()
    df["MA5"]  = df["Close"].rolling(5).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    # Custom style — clean dark-on-white
    mc = mpf.make_marketcolors(
        up="#E74C3C",    down="#3498DB",   # Korean convention: red=up, blue=down
        edge="inherit",
        wick={"up": "#E74C3C", "down": "#3498DB"},
        volume={"up": "#FFAAAA", "down": "#AACCFF"},
    )
    style = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle="--",
        gridcolor="#EEEEEE",
        facecolor="white",
        figcolor="white",
        y_on_right=False,
    )

    # Addplots: MA lines
    addplots = []
    if df["MA5"].notna().any():
        addplots.append(mpf.make_addplot(df["MA5"],  color="#FF8C00", width=1.2, label="MA5"))
    if df["MA20"].notna().any():
        addplots.append(mpf.make_addplot(df["MA20"], color="#6A0DAD", width=1.2, label="MA20"))

    # Last close info for subtitle
    last_close  = int(df["Close"].iloc[-1])
    prev_close  = int(df["Close"].iloc[-2]) if len(df) > 1 else last_close
    change_pct  = (last_close - prev_close) / prev_close * 100
    sign        = "+" if change_pct >= 0 else ""
    subtitle    = f"종가 {last_close:,}원  ({sign}{change_pct:.2f}%)  |  MA5/MA20 포함"

    fig, axes = mpf.plot(
        df,
        type="candle",
        volume=True,
        addplot=addplots if addplots else None,
        style=style,
        figsize=(11, 6.5),
        title=f"\n{name} ({ticker})  —  최근 {len(df)}거래일",
        returnfig=True,
        warn_too_much_data=1000,
    )

    # Subtitle below main title
    axes[0].set_xlabel("")
    fig.text(0.5, 0.935, subtitle, ha="center", fontsize=9, color="#555555")

    # MA legend
    if addplots:
        handles = [
            mpatches.Patch(color="#FF8C00", label="MA5"),
            mpatches.Patch(color="#6A0DAD", label="MA20"),
        ]
        axes[0].legend(handles=handles, loc="upper left", fontsize=8, framealpha=0.8)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _mock_chart(ticker: str, name: str, out_path: Path) -> None:
    """Generate a simple placeholder chart for dry-run testing."""
    import numpy as np

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6.5),
                                   gridspec_kw={"height_ratios": [3, 1]})
    np.random.seed(hash(ticker) % (2**31))
    days   = 20
    prices = 60000 + np.cumsum(np.random.randn(days) * 500)
    vol    = np.random.randint(10_000_000, 40_000_000, days)
    xs     = range(days)

    ax1.plot(xs, prices, color="#E74C3C", linewidth=1.5)
    ax1.fill_between(xs, prices, alpha=0.1, color="#E74C3C")
    ax1.set_title(f"{name} ({ticker})  —  dry-run placeholder", fontsize=12, pad=10)
    ax1.set_ylabel("주가 (원)", fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.4)

    ax2.bar(xs, vol, color="#AACCFF", width=0.8)
    ax2.set_ylabel("거래량", fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.3)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out_path), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ── public API ────────────────────────────────────────────────────────────────

def generate_chart(
    ticker: str,
    name: str | None = None,
    out_dir: Path = CHARTS_DIR,
    dry_run: bool = False,
) -> Path | None:
    """
    Generate a chart PNG for the given ticker.
    Returns the output path on success, None on failure.
    """
    label    = name or DEFAULT_TICKERS.get(ticker, ticker)
    today    = date.today().isoformat()
    out_path = out_dir / f"{ticker}_{today}.png"

    if out_path.exists():
        return out_path   # use cached chart

    if dry_run:
        _mock_chart(ticker, label, out_path)
        return out_path

    df = fetch_ohlcv(ticker)
    if df is None or len(df) < 5:
        print(f"  ⚠  {ticker}: 데이터 부족 → 차트 스킵")
        return None

    try:
        _draw_chart(df, ticker, label, out_path)
    except Exception as e:
        print(f"  ⚠  {ticker} 차트 생성 실패: {e}")
        return None

    return out_path


def generate_charts(
    tickers: dict[str, str] | None = None,
    out_dir: Path = CHARTS_DIR,
    dry_run: bool = False,
) -> dict[str, Path]:
    """Generate charts for multiple tickers. Returns {ticker: path}."""
    watchlist = tickers or DEFAULT_TICKERS
    results: dict[str, Path] = {}
    for ticker, name in watchlist.items():
        path = generate_chart(ticker, name, out_dir, dry_run)
        if path:
            results[ticker] = path
            print(f"  ✅ 차트 생성: {name} ({ticker}) → {path.name}")
    return results


def format_chart_section(charts: dict[str, Path]) -> str:
    """Return markdown annotation lines for chart images (for report injection)."""
    if not charts:
        return ""
    lines = ["## 주요 종목 차트 (최근 30거래일)", ""]
    for ticker, path in charts.items():
        name = DEFAULT_TICKERS.get(ticker, ticker)
        lines.append(f"### {name} ({ticker})")
        lines.append(f"![{name} 캔들차트]({path})")
        lines.append("")
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan 차트 분석기")
    parser.add_argument("--ticker",  nargs="*", help="종목 코드 (기본: 워치리스트)")
    parser.add_argument("--dry-run", action="store_true", help="mock 차트 생성 (pykrx 불필요)")
    parser.add_argument("--out-dir", default=str(CHARTS_DIR))
    args = parser.parse_args()

    mode = "dry-run" if args.dry_run else "라이브 데이터"
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
차트 분석 — {mode}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    out_dir = Path(args.out_dir)
    if args.ticker:
        tickers = {t: DEFAULT_TICKERS.get(t, t) for t in args.ticker}
    else:
        tickers = None

    charts = generate_charts(tickers=tickers, out_dir=out_dir, dry_run=args.dry_run)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
완료 — {len(charts)}개 차트 생성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
