#!/usr/bin/env python3
"""
make_fixtures.py — TDD Fixture Generator for InvestScan
Creates test fixture files required before Phase C TDD can begin.

Usage:
    python make_fixtures.py              # Generate all fixtures
    python make_fixtures.py --verify     # Verify generated fixtures exist
    python make_fixtures.py --clean      # Remove generated fixtures

Output:
    tests/fixtures/envscan_sample.json   — EnvScan normalizers TDD fixture
    tests/fixtures/fred_sample.json      — FRED synthesize_macro TDD fixture
    tests/fixtures/gnews_sample.parquet  — GlobalNews signal_bridge TDD fixture
"""
import argparse
import json
import sys
from pathlib import Path

FIXTURES_DIR = Path("tests/fixtures")

# EnvScan database.json sample — simulates actual EnvironmentScan output schema
ENVSCAN_SAMPLE = {
    "metadata": {
        "generated_at": "2026-03-29T00:00:00Z",
        "source": "EnvironmentScan WF-1",
        "version": "1.0",
    },
    "entries": [
        {
            "steeps_category": "T",          # Technology
            "pSST": 72.5,                    # scale: 0-100
            "summary": "AI semiconductor demand surge driven by LLM training infrastructure buildout.",
            "sector": "technology",
            "confidence": 0.85,
            "date": "2026-03-28",
        },
        {
            "steeps_category": "E_env",      # Environmental
            "pSST": 45.2,
            "summary": "Carbon regulation tightening — ESG compliance cost rising for manufacturing.",
            "sector": "industrials",
            "confidence": 0.72,
            "date": "2026-03-28",
        },
        {
            "steeps_category": "S",          # Social
            "pSST": 61.8,
            "summary": "Aging population driving healthcare demand in Korea — bio/pharma sector tailwind.",
            "sector": "healthcare",
            "confidence": 0.78,
            "date": "2026-03-28",
        },
        {
            "steeps_category": "s",          # sector-specific (lowercase s — different from S)
            "pSST": 58.3,
            "summary": "반도체 업황 회복 — 메모리 재고 정상화 진행 중.",
            "sector": "semiconductor",
            "confidence": 0.81,
            "date": "2026-03-28",
        },
        {
            "steeps_category": "P",          # Political
            "pSST": 38.9,
            "summary": "US-China trade tensions escalating — export restriction risk for chip makers.",
            "sector": "technology",
            "confidence": 0.68,
            "date": "2026-03-28",
        },
        {
            "steeps_category": "E",          # Economic
            "pSST": 55.1,
            "summary": "Fed rate cut expectations rising — 2-3 cuts priced in for 2026.",
            "sector": "financials",
            "confidence": 0.76,
            "date": "2026-03-28",
        },
    ],
    "schema": {
        "steeps_field": "steeps_category",
        "psst_field": "pSST",
        "summary_field": "summary",
        "score_scale": "0-100",
    },
}

# FRED API response sample — simulates 10 series_id responses
FRED_SAMPLE = {
    "metadata": {
        "fetched_at": "2026-03-29T00:00:00Z",
        "source": "FRED API",
        "series_count": 10,
    },
    "series": {
        "DFF": {           # Federal Funds Rate
            "series_id": "DFF",
            "name": "Federal Funds Effective Rate",
            "value": 5.25,
            "unit": "Percent",
            "date": "2026-03-28",
            "available": True,
        },
        "FEDFUNDS": {      # Federal Funds Rate (monthly)
            "series_id": "FEDFUNDS",
            "name": "Federal Funds Rate",
            "value": 5.25,
            "unit": "Percent",
            "date": "2026-03-01",
            "available": True,
        },
        "UNRATE": {        # Unemployment Rate
            "series_id": "UNRATE",
            "name": "Unemployment Rate",
            "value": 3.9,
            "unit": "Percent",
            "date": "2026-03-01",
            "available": True,
        },
        "CPIAUCSL": {      # CPI
            "series_id": "CPIAUCSL",
            "name": "Consumer Price Index for All Urban Consumers",
            "value": 2.8,
            "unit": "Percent Change from Year Ago",
            "date": "2026-03-01",
            "available": True,
        },
        "T10YIE": {        # 10-Year Breakeven Inflation Rate
            "series_id": "T10YIE",
            "name": "10-Year Breakeven Inflation Rate",
            "value": 2.31,
            "unit": "Percent",
            "date": "2026-03-28",
            "available": True,
        },
        "GS10": {          # 10-Year Treasury Yield
            "series_id": "GS10",
            "name": "Market Yield on U.S. Treasury Securities at 10-Year Maturity",
            "value": 4.21,
            "unit": "Percent",
            "date": "2026-03-01",
            "available": True,
        },
        "DTWEXBGS": {      # USD Broad Index
            "series_id": "DTWEXBGS",
            "name": "Nominal Broad U.S. Dollar Index",
            "value": 106.8,
            "unit": "Index",
            "date": "2026-03-28",
            "available": True,
        },
        "VIXCLS": {        # VIX
            "series_id": "VIXCLS",
            "name": "CBOE Volatility Index",
            "value": 18.42,
            "unit": "Index",
            "date": "2026-03-28",
            "available": True,
        },
        "BAMLH0A0HYM2": {  # High-Yield OAS
            "series_id": "BAMLH0A0HYM2",
            "name": "ICE BofA US High Yield Index Option-Adjusted Spread",
            "value": 3.21,
            "unit": "Percent",
            "date": "2026-03-28",
            "available": True,
        },
        "CSUSHPISA": {     # Case-Shiller Home Price Index
            "series_id": "CSUSHPISA",
            "name": "S&P/Case-Shiller U.S. National Home Price Index",
            "value": 315.2,
            "unit": "Index",
            "date": "2025-12-01",
            "available": True,
        },
    },
    "macro_summary": {
        "rate_direction": "hold",         # cut | hold | hike
        "inflation_trend": "cooling",     # rising | cooling | stable
        "risk_appetite": "moderate",      # low | moderate | high
        "usd_strength": "strong",         # weak | neutral | strong
    },
}

# GlobalNews signals.parquet sample — JSON representation for reference
# The actual parquet fixture is generated using pyarrow if available
GNEWS_SAMPLE_SCHEMA = {
    "metadata": {
        "source": "GlobalNews",
        "date": "2026-03-29",
        "record_count": 5,
    },
    "columns": ["headline", "sector", "confidence", "steeps_tag", "date", "source"],
    "records": [
        {
            "headline": "Fed signals patience on rate cuts amid sticky inflation",
            "sector": "financials",
            "confidence": 0.88,
            "steeps_tag": "E",
            "date": "2026-03-28",
            "source": "Reuters",
        },
        {
            "headline": "Samsung Electronics posts record Q1 HBM chip orders",
            "sector": "technology",
            "confidence": 0.91,
            "steeps_tag": "T",
            "date": "2026-03-28",
            "source": "Bloomberg",
        },
        {
            "headline": "China imposes new rare earth export restrictions",
            "sector": "technology",
            "confidence": 0.79,
            "steeps_tag": "P",
            "date": "2026-03-27",
            "source": "FT",
        },
        {
            "headline": "Korea biotech sector receives WHO approval for new drug",
            "sector": "healthcare",
            "confidence": 0.83,
            "steeps_tag": "S",
            "date": "2026-03-27",
            "source": "Yonhap",
        },
        {
            "headline": "Global EV battery demand slowing — LFP oversupply emerging",
            "sector": "materials",
            "confidence": 0.74,
            "steeps_tag": "E_env",
            "date": "2026-03-26",
            "source": "WSJ",
        },
    ],
}


def generate_all_fixtures() -> bool:
    """Generate all TDD fixture files. Returns True if all succeed."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    # 1. EnvScan sample JSON
    envscan_path = FIXTURES_DIR / "envscan_sample.json"
    try:
        envscan_path.write_text(json.dumps(ENVSCAN_SAMPLE, indent=2, ensure_ascii=False))
        results["envscan_sample.json"] = True
        print(f"✅ Generated: {envscan_path}")
    except Exception as e:
        results["envscan_sample.json"] = False
        print(f"❌ Failed envscan_sample.json: {e}")

    # 2. FRED sample JSON
    fred_path = FIXTURES_DIR / "fred_sample.json"
    try:
        fred_path.write_text(json.dumps(FRED_SAMPLE, indent=2, ensure_ascii=False))
        results["fred_sample.json"] = True
        print(f"✅ Generated: {fred_path}")
    except Exception as e:
        results["fred_sample.json"] = False
        print(f"❌ Failed fred_sample.json: {e}")

    # 3. GlobalNews sample — try pyarrow parquet, fallback to JSON
    gnews_path = FIXTURES_DIR / "gnews_sample.parquet"
    gnews_json_path = FIXTURES_DIR / "gnews_sample.json"
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        records = GNEWS_SAMPLE_SCHEMA["records"]
        table = pa.table({
            col: [r[col] for r in records]
            for col in GNEWS_SAMPLE_SCHEMA["columns"]
        })
        pq.write_table(table, gnews_path)
        results["gnews_sample.parquet"] = True
        print(f"✅ Generated: {gnews_path} (pyarrow)")
    except ImportError:
        # pyarrow not installed — write JSON representation as fallback
        gnews_json_path.write_text(json.dumps(GNEWS_SAMPLE_SCHEMA, indent=2, ensure_ascii=False))
        results["gnews_sample.parquet"] = "json_fallback"
        print(f"⚠️  pyarrow not found — wrote JSON fallback: {gnews_json_path}")
        print(f"   Install pyarrow: pip install pyarrow")
    except Exception as e:
        results["gnews_sample.parquet"] = False
        print(f"❌ Failed gnews_sample: {e}")

    all_passed = all(v is not False for v in results.values())
    print(f"\nFixture generation: {'✅ ALL PASS' if all_passed else '❌ SOME FAILED'}")
    return all_passed


def verify_fixtures() -> bool:
    """Verify all required fixtures exist."""
    required = [
        FIXTURES_DIR / "envscan_sample.json",
        FIXTURES_DIR / "fred_sample.json",
    ]
    all_exist = True
    for path in required:
        if path.exists():
            print(f"✅ {path}")
        else:
            print(f"❌ MISSING: {path}")
            all_exist = False

    # gnews: either .parquet or .json fallback acceptable
    gnews_ok = (FIXTURES_DIR / "gnews_sample.parquet").exists() or \
               (FIXTURES_DIR / "gnews_sample.json").exists()
    if gnews_ok:
        print(f"✅ tests/fixtures/gnews_sample (.parquet or .json)")
    else:
        print(f"❌ MISSING: tests/fixtures/gnews_sample (.parquet or .json)")
        all_exist = False

    return all_exist


def clean_fixtures() -> None:
    """Remove generated fixture files."""
    for pattern in ["envscan_sample.json", "fred_sample.json",
                    "gnews_sample.parquet", "gnews_sample.json"]:
        path = FIXTURES_DIR / pattern
        if path.exists():
            path.unlink()
            print(f"🗑️  Removed: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InvestScan TDD Fixture Generator")
    parser.add_argument("--verify", action="store_true", help="Verify fixtures exist")
    parser.add_argument("--clean", action="store_true", help="Remove generated fixtures")
    args = parser.parse_args()

    if args.clean:
        clean_fixtures()
    elif args.verify:
        success = verify_fixtures()
        sys.exit(0 if success else 1)
    else:
        success = generate_all_fixtures()
        sys.exit(0 if success else 1)
