"""
news_crawler.py — RSS-based Korean financial news crawler.

Collects headlines from major Korean financial news RSS feeds,
filters by sector/stock keywords, and produces investment signals.

Output:
  output/news/{DATE}_news_signals.json

Usage:
    python3 -m investscan.news_crawler              # crawl all feeds
    python3 -m investscan.news_crawler --dry-run    # offline test with mock data
    python3 -m investscan.news_crawler --date 2026-03-30
"""
from __future__ import annotations

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import TypedDict
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ── output path ───────────────────────────────────────────────────────────────

NEWS_DIR = Path("output/news")

# ── RSS feed registry ─────────────────────────────────────────────────────────
# 검증된 공개 RSS 피드만 포함. 접근 불가 시 자동 스킵.

RSS_FEEDS: list[dict] = [
    {
        "name": "한국경제",
        "url": "https://www.hankyung.com/rss/all.xml",
        "category": "economy",
        "lang": "ko",
    },
    {
        "name": "매일경제",
        "url": "https://www.mk.co.kr/rss/30000001.xml",
        "category": "economy",
        "lang": "ko",
    },
    {
        "name": "연합뉴스 경제",
        "url": "https://www.yonhapnewstv.co.kr/rss/economy.xml",
        "category": "economy",
        "lang": "ko",
    },
    {
        "name": "Reuters Business",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "category": "global",
        "lang": "en",
    },
]

# ── sector keyword map ────────────────────────────────────────────────────────

SECTOR_KEYWORDS: dict[str, list[str]] = {
    "반도체·IT": [
        "반도체", "삼성전자", "SK하이닉스", "HBM", "메모리", "DRAM", "낸드",
        "엔비디아", "TSMC", "AI칩", "파운드리", "semiconductor", "memory chip",
    ],
    "AI·소프트웨어": [
        "인공지능", "AI", "LLM", "대형언어모델", "챗GPT", "클라우드",
        "NAVER", "카카오", "artificial intelligence", "ChatGPT", "cloud",
    ],
    "에너지·원자력": [
        "원전", "원자력", "두산에너빌리티", "SMR", "탄소중립", "전력",
        "nuclear", "energy", "renewable", "power grid",
    ],
    "헬스케어·바이오": [
        "바이오", "제약", "삼성바이오로직스", "셀트리온", "임상", "FDA",
        "healthcare", "pharma", "biotech", "clinical",
    ],
    "금융": [
        "금리", "Fed", "연준", "FOMC", "기준금리", "인플레이션", "채권",
        "interest rate", "Fed rate", "inflation", "bond",
    ],
    "소재·화학": [
        "철강", "화학", "POSCO", "LG화학", "2차전지", "배터리", "리튬",
        "steel", "chemical", "battery", "lithium",
    ],
    "소비재·유통": [
        "소비자", "유통", "이마트", "쿠팡", "소비심리", "retail",
        "consumer", "e-commerce",
    ],
    "매크로": [
        "GDP", "물가", "CPI", "PPI", "달러", "원달러", "환율", "무역",
        "관세", "tariff", "dollar", "yuan", "macro",
    ],
}

BEARISH_WORDS = [
    "하락", "급락", "폭락", "우려", "위기", "충격", "손실", "적자", "감소",
    "축소", "downgrade", "decline", "fall", "drop", "risk", "concern",
    "loss", "cut", "reduce",
]

BULLISH_WORDS = [
    "상승", "급등", "호황", "성장", "증가", "흑자", "수주", "매수",
    "upgrade", "rise", "rally", "growth", "profit", "beat", "surge",
    "record", "expand",
]


# ── type definitions ──────────────────────────────────────────────────────────

class NewsItem(TypedDict):
    title: str
    link: str
    pub_date: str
    source: str
    sectors: list[str]
    sentiment: str          # "bullish" | "bearish" | "neutral"
    score: float            # 0.0 – 1.0 relevance score


class NewsSummary(TypedDict):
    crawl_date: str
    total_items: int
    sector_counts: dict[str, int]
    sector_sentiment: dict[str, str]
    top_signals: list[NewsItem]
    items: list[NewsItem]


# ── RSS parser ─────────────────────────────────────────────────────────────────

def _fetch_rss(url: str, timeout: int = 8) -> str | None:
    """Fetch RSS feed content as string. Returns None on failure."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; InvestScan/1.0; "
            "+https://github.com/investscan)"
        )
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            encoding = resp.headers.get_content_charset("utf-8")
            return raw.decode(encoding, errors="replace")
    except (URLError, HTTPError, Exception):
        return None


def _parse_feed(xml_content: str, source_name: str) -> list[dict]:
    """Parse RSS/Atom XML into a list of raw items."""
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return []

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "media": "http://search.yahoo.com/mrss/",
    }

    # RSS 2.0
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el  = item.find("link")
        date_el  = item.find("pubDate")
        items.append({
            "title":    title_el.text.strip()  if title_el  is not None and title_el.text  else "",
            "link":     link_el.text.strip()   if link_el   is not None and link_el.text   else "",
            "pub_date": date_el.text.strip()   if date_el   is not None and date_el.text   else "",
            "source":   source_name,
        })

    # Atom
    if not items:
        for entry in root.findall(".//atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            link_el  = entry.find("atom:link",  ns)
            date_el  = entry.find("atom:updated", ns)
            link = (link_el.get("href", "") if link_el is not None else "")
            items.append({
                "title":    title_el.text.strip() if title_el is not None and title_el.text else "",
                "link":     link,
                "pub_date": date_el.text.strip()  if date_el  is not None and date_el.text  else "",
                "source":   source_name,
            })

    return items


# ── signal scoring ─────────────────────────────────────────────────────────────

def _detect_sectors(text: str) -> list[str]:
    """Return list of sectors matching keywords in text."""
    text_lower = text.lower()
    matched = []
    for sector, kws in SECTOR_KEYWORDS.items():
        if any(kw.lower() in text_lower for kw in kws):
            matched.append(sector)
    return matched or ["매크로"]


def _detect_sentiment(text: str) -> str:
    text_lower = text.lower()
    bull = sum(1 for w in BULLISH_WORDS if w.lower() in text_lower)
    bear = sum(1 for w in BEARISH_WORDS if w.lower() in text_lower)
    if bull > bear:
        return "bullish"
    if bear > bull:
        return "bearish"
    return "neutral"


def _score_relevance(title: str, sectors: list[str]) -> float:
    """0.0–1.0 relevance score based on sector specificity + keyword density."""
    total_kws = sum(
        sum(1 for kw in SECTOR_KEYWORDS[s] if kw.lower() in title.lower())
        for s in sectors
    )
    base = min(total_kws * 0.2, 0.8)
    sector_bonus = min(len(sectors) * 0.1, 0.2)
    return round(min(base + sector_bonus, 1.0), 2)


def _enrich_item(raw: dict) -> NewsItem:
    title    = raw["title"]
    sectors  = _detect_sectors(title)
    sentiment = _detect_sentiment(title)
    score    = _score_relevance(title, sectors)
    return NewsItem(
        title=title,
        link=raw["link"],
        pub_date=raw["pub_date"],
        source=raw["source"],
        sectors=sectors,
        sentiment=sentiment,
        score=score,
    )


# ── aggregation ───────────────────────────────────────────────────────────────

def _aggregate(items: list[NewsItem]) -> NewsSummary:
    """Build sector-level signal summary from enriched items."""
    sector_counts: dict[str, int] = {}
    sector_bull:   dict[str, int] = {}
    sector_bear:   dict[str, int] = {}

    for item in items:
        for s in item["sectors"]:
            sector_counts[s] = sector_counts.get(s, 0) + 1
            if item["sentiment"] == "bullish":
                sector_bull[s] = sector_bull.get(s, 0) + 1
            elif item["sentiment"] == "bearish":
                sector_bear[s] = sector_bear.get(s, 0) + 1

    sector_sentiment: dict[str, str] = {}
    for s in sector_counts:
        bull = sector_bull.get(s, 0)
        bear = sector_bear.get(s, 0)
        if bull > bear * 1.3:
            sector_sentiment[s] = "bullish"
        elif bear > bull * 1.3:
            sector_sentiment[s] = "bearish"
        else:
            sector_sentiment[s] = "neutral"

    top = sorted(items, key=lambda x: x["score"], reverse=True)[:10]

    return NewsSummary(
        crawl_date=date.today().isoformat(),
        total_items=len(items),
        sector_counts=dict(sorted(sector_counts.items(), key=lambda x: -x[1])),
        sector_sentiment=sector_sentiment,
        top_signals=top,
        items=items,
    )


# ── mock data for dry-run ──────────────────────────────────────────────────────

def _mock_items() -> list[NewsItem]:
    """Return mock news items for offline testing."""
    raw_titles = [
        "삼성전자, HBM3E 엔비디아 공급 확대…메모리 사이클 회복 기대",
        "Fed, 기준금리 동결 결정…시장 안도",
        "SK하이닉스, 1분기 영업이익 컨센서스 상회 전망",
        "두산에너빌리티, 체코 원전 계약 본계약 임박",
        "AI 인프라 투자 사이클 가속화…반도체 수요 견조",
        "미중 무역갈등 재점화 우려…수출주 부담",
        "NAVER, AI 검색 서비스 확대…광고 매출 성장 기대",
        "원달러 환율 1400원 돌파…수출 대형주 환차익",
        "삼성바이오로직스, FDA 승인 지연 우려로 주가 하락",
        "LG화학, 배터리 수요 부진으로 실적 눈높이 하향",
    ]
    items = []
    for i, title in enumerate(raw_titles):
        pub_date = (date.today() - timedelta(days=i % 3)).isoformat()
        raw = {"title": title, "link": "#", "pub_date": pub_date, "source": "mock"}
        items.append(_enrich_item(raw))
    return items


# ── public API ────────────────────────────────────────────────────────────────

def crawl(dry_run: bool = False, max_items_per_feed: int = 30) -> NewsSummary:
    """
    Crawl RSS feeds and return a NewsSummary.
    If dry_run=True, uses mock data instead of live HTTP.
    """
    if dry_run:
        items = _mock_items()
        return _aggregate(items)

    all_items: list[NewsItem] = []
    for feed in RSS_FEEDS:
        xml_content = _fetch_rss(feed["url"])
        if not xml_content:
            print(f"  ⚠  {feed['name']}: 접속 실패 (스킵)")
            continue
        raw_items = _parse_feed(xml_content, feed["name"])
        enriched  = [_enrich_item(r) for r in raw_items if r["title"]]
        enriched  = enriched[:max_items_per_feed]
        all_items.extend(enriched)
        print(f"  ✅ {feed['name']}: {len(enriched)}건")

    return _aggregate(all_items)


def crawl_and_save(
    dry_run: bool = False,
    report_date: str | None = None,
    out_dir: Path = NEWS_DIR,
) -> Path:
    """Crawl, aggregate, and save JSON. Returns output path."""
    rd = report_date or date.today().isoformat()
    summary = crawl(dry_run=dry_run)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{rd}_news_signals.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    return out_path


def format_news_section(summary: NewsSummary) -> str:
    """Format NewsSummary as markdown section for injection into weekly report."""
    lines: list[str] = []
    lines.append("## 뉴스 크롤링 주요 신호")
    lines.append("")
    lines.append(f"> **수집 일자**: {summary['crawl_date']} | **총 {summary['total_items']}건 수집**")
    lines.append("")

    # Sector sentiment table
    lines.append("### 섹터별 뉴스 방향성")
    lines.append("")
    lines.append("| 섹터 | 뉴스 건수 | 방향성 |")
    lines.append("|------|-----------|--------|")
    sentiment_icon = {"bullish": "📈 긍정", "bearish": "📉 부정", "neutral": "➡ 중립"}
    for sector, count in summary["sector_counts"].items():
        sent = summary["sector_sentiment"].get(sector, "neutral")
        icon = sentiment_icon.get(sent, "➡ 중립")
        lines.append(f"| {sector} | {count} | {icon} |")

    lines.append("")
    lines.append("### 상위 투자 신호 (관련도 순)")
    lines.append("")
    for item in summary["top_signals"][:5]:
        sent_tag = {"bullish": "[긍정]", "bearish": "[부정]", "neutral": "[중립]"}.get(
            item["sentiment"], "[중립]"
        )
        sectors_str = ", ".join(item["sectors"][:2])
        lines.append(f"- **{sent_tag}** {item['title']}")
        lines.append(f"  - 섹터: {sectors_str} | 출처: {item['source']}")
    lines.append("")

    return "\n".join(lines)


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="InvestScan 뉴스 크롤러")
    parser.add_argument("--dry-run", action="store_true", help="오프라인 mock 데이터 사용")
    parser.add_argument("--date",    help="저장 날짜 YYYY-MM-DD (기본: 오늘)")
    parser.add_argument("--out-dir", default=str(NEWS_DIR), help="출력 디렉터리")
    args = parser.parse_args()

    mode = "dry-run (오프라인)" if args.dry_run else "라이브 크롤링"
    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
뉴스 크롤링 — {mode}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━""")

    out_dir = Path(args.out_dir)
    out_path = crawl_and_save(dry_run=args.dry_run,
                               report_date=args.date,
                               out_dir=out_dir)

    summary: NewsSummary = json.loads(out_path.read_text(encoding="utf-8"))
    print(f"\n  수집 건수  : {summary['total_items']}건")
    print(f"  상위 섹터  : {', '.join(list(summary['sector_counts'].keys())[:4])}")
    print(f"  저장 경로  : {out_path}")
    print(f"\n{format_news_section(summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
