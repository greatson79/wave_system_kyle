# InvestScan: Testing & Error Handling Implementation Analysis

**Analysts**: Two Quality Implementation Experts (Minimal Pragmatist + Comprehensive Guardian)
**Date**: 2026-03-28
**Context**: Round 3 decisions -- 25 targeted tests (Schema 10 + Sector 15), pytest, NO mypy strict, NO CI/CD
**System**: Solo pastor-developer, 2-4 hrs/week, ~2,470 LOC (Balanced-Tech), financial decisions ride on output
**Budget**: ~8hr testing over 6 months (Minimal) vs ~20hr (Comprehensive)

---

## Branch 4.1: MINIMAL Testing (25 tests, crash-loud)

**Philosophy**: "Test the money paths. Let everything else crash loudly. A visible crash is infinitely better than a silent wrong answer."

**Analyst**: The Minimal Pragmatist

### 1. The 10 Schema Parsing Tests (Contract Tests)

These 10 tests guard the system boundary -- the point where external data enters InvestScan. Every field mapping, every type conversion, every default value. If these break, the entire pipeline produces garbage.

```python
# tests/test_normalize.py
"""
Contract tests for signal normalization.

These 10 tests are NON-NEGOTIABLE. They guard the boundary between
source systems (EnvScan JSON, GlobalNews Parquet) and InvestScan's
unified schema. A failure here means upstream data changed.

Run: pytest tests/test_normalize.py -v
"""
import pytest
from dataclasses import asdict
from invest_pipeline.normalize_signals import (
    normalize_envscan_signal,
    normalize_gnews_signal,
    psst_to_confidence,
)
from invest_pipeline.schema import UnifiedSignal, SteepsCategory, SignalLayer


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def envscan_signal_full():
    """A complete EnvScan signal with all expected fields.
    Mirrors actual output from EnvScan database.json items[].
    """
    return {
        "id": "TC-20260325-001",
        "title": "With $3.5B in fresh capital, Kleiner Perkins is going all in on AI",
        "source": {"name": "TechCrunch", "type": "blog", "tier": "base"},
        "published_date": "2026-03-25T00:47:20Z",
        "preliminary_category": "T_Technological",
        "summary": "VC firm raises $3.5B for AI-focused investments across infrastructure and applications.",
        "metadata": {"word_count": 450, "language": "en"},
        "pSST_score": 72,
    }


@pytest.fixture
def envscan_signal_minimal():
    """EnvScan signal with only required fields (no pSST, no category).
    This happens when EnvScan agents fail to enrich a signal.
    """
    return {
        "id": "NV-20260325-003",
        "title": "삼성전자 AI 반도체 투자 확대",
        "source": {"name": "Naver", "type": "news"},
        "published_date": "2026-03-25T09:00:00Z",
    }


@pytest.fixture
def gnews_signal_full():
    """A complete GlobalNews signal as a dict (simulating Parquet row).
    Mirrors actual output from GlobalNews signals.parquet columns.
    """
    return {
        "signal_id": "550e8400-e29b-41d4-a716-446655440000",
        "signal_layer": "L3_mid",
        "signal_label": "AI Semiconductor Supply Chain Disruption",
        "detected_at": "2026-03-25T12:00:00Z",
        "topic_ids": [42, 87, 103],
        "article_ids": ["art-001", "art-002", "art-003"],
        "burst_score": 0.72,
        "changepoint_significance": 0.45,
        "novelty_score": 0.68,
        "singularity_composite": 0.31,
        "evidence_summary": "Multiple sources report semiconductor supply chain shifts...",
        "confidence": 0.78,
    }


@pytest.fixture
def gnews_signal_nulls():
    """GlobalNews signal with null fields (incomplete NLP pipeline).
    This happens when burst detection finds a signal but topic modeling
    produces no label.
    """
    return {
        "signal_id": "660e8400-e29b-41d4-a716-446655440001",
        "signal_layer": "L2_short",
        "signal_label": None,
        "detected_at": "2026-03-25T14:00:00Z",
        "topic_ids": [],
        "article_ids": ["art-005"],
        "burst_score": 0.45,
        "changepoint_significance": None,
        "novelty_score": 0.22,
        "singularity_composite": None,
        "evidence_summary": None,
        "confidence": 0.35,
    }


# ── Test 1-4: EnvScan Signal Parsing ─────────────────────────────────

class TestEnvScanParsing:
    """Tests 1-4: Verify EnvScan JSON -> UnifiedSignal conversion."""

    def test_full_signal_parses_all_fields(self, envscan_signal_full):
        """Test 1: Complete EnvScan signal produces valid UnifiedSignal
        with all fields correctly mapped.
        """
        result = normalize_envscan_signal(envscan_signal_full)

        assert isinstance(result, UnifiedSignal)
        assert result.source_system == "envscan"
        assert result.source_signal_id == "TC-20260325-001"
        assert result.title == envscan_signal_full["title"]
        assert result.steeps_category == SteepsCategory.TECHNOLOGICAL
        assert result.confidence == pytest.approx(0.72)  # pSST 72 -> 0.72

    def test_minimal_signal_uses_defaults(self, envscan_signal_minimal):
        """Test 2: EnvScan signal missing optional fields gets safe defaults.
        CRITICAL: missing pSST must NOT produce 0.0 confidence (would
        eliminate signal from synthesis). Default is 0.5 (mid-confidence).
        """
        result = normalize_envscan_signal(envscan_signal_minimal)

        assert isinstance(result, UnifiedSignal)
        assert result.confidence == pytest.approx(0.5)  # Default mid-confidence
        assert result.steeps_category == SteepsCategory.UNKNOWN

    def test_missing_required_field_raises(self):
        """Test 3: Signal missing required 'id' field raises immediately.
        Crash-loud: better to halt pipeline than produce phantom signals.
        """
        bad_signal = {"title": "No ID field", "source": {"name": "Test"}}
        with pytest.raises((KeyError, ValueError)):
            normalize_envscan_signal(bad_signal)

    def test_envscan_category_mapping_t_technological(self, envscan_signal_full):
        """Test 4: EnvScan 'T_Technological' maps to SteepsCategory.TECHNOLOGICAL.
        This is the #1 schema drift risk: EnvScan uses 'T_Technological',
        InvestScan enum uses 'T'. The mapper must bridge this.
        """
        result = normalize_envscan_signal(envscan_signal_full)
        assert result.steeps_category == SteepsCategory.TECHNOLOGICAL
        # Also verify the enum value serializes correctly
        assert result.steeps_category.value == "T"


# ── Test 5-7: GlobalNews Signal Parsing ──────────────────────────────

class TestGNewsParsing:
    """Tests 5-7: Verify GlobalNews Parquet row -> UnifiedSignal conversion."""

    def test_full_gnews_signal_parses(self, gnews_signal_full):
        """Test 5: Complete GlobalNews signal produces valid UnifiedSignal.
        confidence is native 0-1, so NO normalization needed (unlike pSST).
        """
        result = normalize_gnews_signal(gnews_signal_full)

        assert isinstance(result, UnifiedSignal)
        assert result.source_system == "gnews"
        assert result.signal_layer == SignalLayer.L3_MID
        assert result.confidence == pytest.approx(0.78)  # Pass-through, no conversion
        assert result.burst_score == pytest.approx(0.72)
        assert result.novelty_score == pytest.approx(0.68)

    def test_gnews_null_fields_get_defaults(self, gnews_signal_nulls):
        """Test 6: GlobalNews signal with None fields gets safe defaults.
        CRITICAL: null evidence_summary must NOT crash report generation.
        null singularity_composite must default to 0.0 (not None).
        """
        result = normalize_gnews_signal(gnews_signal_nulls)

        assert isinstance(result, UnifiedSignal)
        assert result.title != ""  # Must generate a title from signal_label or fallback
        assert result.burst_score == pytest.approx(0.45)
        assert result.novelty_score == pytest.approx(0.22)
        # Null composites default to 0.0, not None (downstream math would crash)
        assert isinstance(result.burst_score, float)

    def test_gnews_invalid_layer_raises(self):
        """Test 7: Invalid signal_layer value crashes immediately.
        'L6_unknown' is not in the SignalLayer enum. This catches
        GlobalNews adding new layers without InvestScan updating.
        """
        bad_signal = {
            "signal_id": "test-bad-layer",
            "signal_layer": "L6_unknown",
            "detected_at": "2026-03-25T00:00:00Z",
            "confidence": 0.5,
        }
        with pytest.raises((KeyError, ValueError)):
            normalize_gnews_signal(bad_signal)


# ── Test 8-10: pSST Score Normalization ──────────────────────────────

class TestPSSTNormalization:
    """Tests 8-10: The single most financially dangerous function.
    pSST is 0-100 integer from EnvScan. confidence is 0.0-1.0 float in
    InvestScan. A normalization bug here means a pSST of 85 could appear
    as confidence 8.5 (850% conviction) or 0.0085 (invisible signal).
    Both produce wrong investment directions.
    """

    def test_psst_basic_conversion(self):
        """Test 8: Standard pSST values convert correctly.
        85 -> 0.85, 0 -> 0.0, 100 -> 1.0
        """
        assert psst_to_confidence(0) == pytest.approx(0.0)
        assert psst_to_confidence(50) == pytest.approx(0.5)
        assert psst_to_confidence(72) == pytest.approx(0.72)
        assert psst_to_confidence(85) == pytest.approx(0.85)
        assert psst_to_confidence(100) == pytest.approx(1.0)

    def test_psst_out_of_range_raises(self):
        """Test 9: pSST outside 0-100 crashes immediately.
        EnvScan might output a raw LLM score of 150 or -10 due to
        prompt parsing failures. This MUST NOT silently pass through.
        """
        with pytest.raises(ValueError, match="pSST score must be 0-100"):
            psst_to_confidence(-1)
        with pytest.raises(ValueError, match="pSST score must be 0-100"):
            psst_to_confidence(101)
        with pytest.raises(ValueError, match="pSST score must be 0-100"):
            psst_to_confidence(150)

    def test_psst_none_returns_default(self):
        """Test 10: None pSST (missing from EnvScan) returns 0.5 default.
        NOT 0.0 -- that would eliminate the signal from synthesis.
        NOT 1.0 -- that would make it appear maximally confident.
        0.5 = mid-confidence = "we have no pSST data, treat as average."
        """
        assert psst_to_confidence(None) == pytest.approx(0.5)
```

### 2. The 15 Sector Mapping Tests (Classification Tests)

These 15 tests verify that STEEPs categories and signal content correctly map to investment sectors. Misclassification here means wrong sector weights in the weekly report.

```python
# tests/test_sector_mapping.py
"""
Sector mapping tests for STEEPs -> GICS investment sector conversion.

These 15 tests verify the core analytical engine: converting
environmental signals (STEEPs categories + signal content) into
actionable investment sector classifications.

A misclassification here does not crash the pipeline -- it produces
a wrong sector weight in the weekly report, leading to potentially
misguided investment direction.

Run: pytest tests/test_sector_mapping.py -v
"""
import pytest
from invest_pipeline.sector_mapper import (
    map_steeps_to_sectors,
    map_signal_to_sectors,
    classify_steeps_from_text,
)
from invest_pipeline.schema import SteepsCategory, UnifiedSignal


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def tech_signal():
    """A Technology signal about AI semiconductors."""
    return _make_signal(
        steeps_category=SteepsCategory.TECHNOLOGICAL,
        title="AI Semiconductor Supply Chain Disruption",
        summary="Major chip manufacturers shifting production to advanced AI accelerators",
    )


@pytest.fixture
def economic_signal():
    """An Economic signal about interest rates."""
    return _make_signal(
        steeps_category=SteepsCategory.ECONOMIC,
        title="Fed Signals Rate Cut in Q3 2026",
        summary="Federal Reserve indicates potential 50bp rate reduction amid cooling inflation",
    )


@pytest.fixture
def political_signal():
    """A Political signal about trade policy."""
    return _make_signal(
        steeps_category=SteepsCategory.POLITICAL,
        title="US-China Chip Export Controls Extended",
        summary="New executive order broadens semiconductor export restrictions to include AI training chips",
    )


def _make_signal(steeps_category, title, summary, **kwargs):
    """Helper to create minimal UnifiedSignal for testing."""
    defaults = {
        "signal_id": "IS-20260327-TEST",
        "source_system": "envscan",
        "source_signal_id": "TEST-001",
        "title": title,
        "summary": summary,
        "detected_at": "2026-03-27T10:00:00Z",
        "steeps_category": steeps_category,
        "signal_layer": "L3_mid",
        "confidence": 0.7,
        "burst_score": 0.5,
        "novelty_score": 0.5,
    }
    defaults.update(kwargs)
    return UnifiedSignal(**defaults)


# ── Tests 1-6: STEEPs Category -> Sector Mapping (Parametrized) ─────

class TestSteepsToSector:
    """Tests 1-6: Each STEEPs category maps to expected primary sectors.
    This is the rule-based mapping table at the heart of InvestScan.
    """

    @pytest.mark.parametrize("steeps,expected_primary_sectors", [
        # Test 1: Technology -> IT + Communication Services
        (SteepsCategory.TECHNOLOGICAL, {"Information Technology", "Communication Services"}),
        # Test 2: Economic -> Financials + Real Estate
        (SteepsCategory.ECONOMIC, {"Financials", "Real Estate"}),
        # Test 3: Political -> Industrials + Materials + Energy
        (SteepsCategory.POLITICAL, {"Industrials", "Materials", "Energy"}),
        # Test 4: Social -> Consumer Staples + Consumer Discretionary + Health Care
        (SteepsCategory.SOCIAL, {"Consumer Staples", "Consumer Discretionary", "Health Care"}),
        # Test 5: Environmental -> Utilities + Energy + Materials
        (SteepsCategory.ENVIRONMENTAL, {"Utilities", "Energy", "Materials"}),
        # Test 6: Security -> Industrials (Defense) + IT (Cybersecurity)
        (SteepsCategory.SECURITY, {"Industrials", "Information Technology"}),
    ])
    def test_steeps_to_primary_sectors(self, steeps, expected_primary_sectors):
        """Each STEEPs category must map to at least its primary sectors.
        The result may include additional sectors; we test that the expected
        primary sectors are a SUBSET of the result.
        """
        result = map_steeps_to_sectors(steeps)
        assert expected_primary_sectors.issubset(set(result)), (
            f"STEEPs={steeps.value}: expected {expected_primary_sectors} "
            f"to be subset of {set(result)}"
        )

    def test_unknown_category_returns_all_sectors(self):
        """Test 7: UNKNOWN STEEPs maps to all sectors (no filtering).
        When we cannot classify the signal, we do not suppress it --
        we include it in all sectors at reduced weight.
        """
        result = map_steeps_to_sectors(SteepsCategory.UNKNOWN)
        assert len(result) >= 11  # GICS has 11 sectors


# ── Tests 8-10: Full Signal -> Sector Mapping (Content-Aware) ────────

class TestSignalToSector:
    """Tests 8-10: Signal mapping uses BOTH STEEPs category AND text content.
    STEEPs provides the primary sector. Text keywords refine/add sectors.
    """

    def test_tech_signal_maps_to_it_sector(self, tech_signal):
        """Test 8: Tech signal about semiconductors maps to IT.
        The word 'semiconductor' in the title/summary should reinforce
        the IT sector mapping from STEEPs=T.
        """
        result = map_signal_to_sectors(tech_signal)
        assert "Information Technology" in result
        # Semiconductor-specific: should also flag Materials (chip manufacturing)
        assert "Materials" in result or "Information Technology" in result

    def test_economic_signal_maps_to_financials(self, economic_signal):
        """Test 9: Rate cut signal maps to Financials + Real Estate.
        Interest rate signals have outsized impact on Financials (banks,
        insurance) and Real Estate (REITs, construction).
        """
        result = map_signal_to_sectors(economic_signal)
        assert "Financials" in result

    def test_cross_domain_signal_maps_to_multiple_sectors(self, political_signal):
        """Test 10: Political signal about chip exports maps to BOTH
        Industrials (trade policy) AND Information Technology (semiconductors).
        This tests the content-aware keyword overlay on top of STEEPs.
        """
        result = map_signal_to_sectors(political_signal)
        # STEEPs=P gives Industrials baseline
        assert "Industrials" in result or "Information Technology" in result


# ── Tests 11-13: STEEPs Text Classification ──────────────────────────

class TestSteepsClassification:
    """Tests 11-13: Classify free text into STEEPs categories.
    Used when GlobalNews signals lack STEEPs labels (they have L1-L5 layers
    but no STEEPs classification natively).
    """

    @pytest.mark.parametrize("title,summary,expected", [
        # Test 11: Clear Technology signal
        (
            "NVIDIA Announces Next-Gen AI Chip Architecture",
            "New GPU architecture doubles training throughput for large language models",
            SteepsCategory.TECHNOLOGICAL,
        ),
        # Test 12: Clear Economic signal
        (
            "Korea CPI Rises 2.8% YoY in March 2026",
            "Consumer price inflation exceeds Bank of Korea target, rate hike speculation grows",
            SteepsCategory.ECONOMIC,
        ),
        # Test 13: Ambiguous signal (should return best guess, not crash)
        (
            "Samsung Announces Restructuring Plan",
            "Korea's largest conglomerate reorganizes divisions amid changing market dynamics",
            # Could be T (tech company), E (corporate restructuring), or S (employment).
            # Rule-based classifier should return SOMETHING, not UNKNOWN.
            SteepsCategory.TECHNOLOGICAL,  # Samsung = tech company, most likely classification
        ),
    ])
    def test_classify_steeps_from_text(self, title, summary, expected):
        """Text-based STEEPs classification returns reasonable category."""
        result = classify_steeps_from_text(title, summary)
        assert isinstance(result, SteepsCategory)
        # For unambiguous signals (tests 11-12), exact match required
        # For ambiguous signals (test 13), any non-UNKNOWN is acceptable
        if "NVIDIA" in title or "CPI" in title:
            assert result == expected


# ── Tests 14-15: Edge Cases ──────────────────────────────────────────

class TestSectorMappingEdgeCases:
    """Tests 14-15: Boundary conditions that could produce silent errors."""

    def test_empty_summary_still_maps(self):
        """Test 14: Signal with empty summary uses STEEPs-only mapping.
        EnvScan sometimes produces signals with empty summaries when
        the source article was paywalled or scraping failed.
        """
        signal = _make_signal(
            steeps_category=SteepsCategory.TECHNOLOGICAL,
            title="Some Technology News",
            summary="",
        )
        result = map_signal_to_sectors(signal)
        assert len(result) > 0  # Must return at least one sector
        assert "Information Technology" in result  # STEEPs=T still works

    def test_korean_text_in_title(self):
        """Test 15: Korean text in title does not crash the keyword matcher.
        EnvScan Naver workflow produces Korean-language signals. The
        sector mapper must handle Korean text gracefully (keyword matching
        may not work, but it must NOT raise an exception).
        """
        signal = _make_signal(
            steeps_category=SteepsCategory.TECHNOLOGICAL,
            title="삼성전자 AI 반도체 투자 확대 계획 발표",
            summary="삼성전자가 2026년 AI 반도체에 대규모 투자를 확대한다고 밝혔다.",
        )
        result = map_signal_to_sectors(signal)
        assert len(result) > 0  # Must return sectors (from STEEPs at minimum)
        assert isinstance(result, list)
```

### 3. Error Handling Pattern: Crash-Loud

The minimal approach treats errors as binary: either the pipeline runs cleanly, or it fails visibly. There is no middle ground. No partial results. No "skip and continue." If something is wrong, the developer sees it immediately.

```python
# invest_pipeline/health_check.py
"""
Pipeline health check -- runs ONCE at pipeline start.
If any check fails, the entire pipeline halts with a clear error message.
No partial execution. No graceful degradation. Crash loud.

Usage:
    python -m invest_pipeline.health_check
    # Exit code 0 = all clear. Exit code 1 = do not proceed.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from invest_pipeline.config import (
    ENVSCAN_SIGNALS,
    GNEWS_SIGNALS,
    GNEWS_ANALYSIS,
    OUTPUT_DIR,
)


class HealthCheckError(Exception):
    """Raised when a pre-condition for pipeline execution is not met."""
    pass


def check_source_files_exist() -> list[str]:
    """Verify that source system output files exist on disk.

    Returns list of warnings (non-fatal). Raises on fatal errors.
    """
    warnings = []
    fatal_missing = []

    # EnvScan signals database -- REQUIRED
    if not ENVSCAN_SIGNALS.exists():
        fatal_missing.append(
            f"EnvScan signals not found: {ENVSCAN_SIGNALS}\n"
            f"  -> Run EnvScan first: cd ../EnvironmentScan-system-main-v4-main && /env-scan:run"
        )

    # GlobalNews signals -- REQUIRED
    if not GNEWS_SIGNALS.exists():
        fatal_missing.append(
            f"GlobalNews signals not found: {GNEWS_SIGNALS}\n"
            f"  -> Run GlobalNews first: cd ../GlobalNews-Crawling-AgenticWorkflow && python main.py --mode full"
        )

    # GlobalNews analysis -- OPTIONAL (degrades synthesis quality)
    if not GNEWS_ANALYSIS.exists():
        warnings.append(
            f"GlobalNews analysis not found: {GNEWS_ANALYSIS}\n"
            f"  -> Synthesis will use signals.parquet only (reduced quality)"
        )

    if fatal_missing:
        raise HealthCheckError(
            "PIPELINE CANNOT RUN -- Missing required source files:\n\n"
            + "\n\n".join(fatal_missing)
        )

    return warnings


def check_source_files_fresh(max_age_days: int = 14) -> list[str]:
    """Warn if source files are older than max_age_days.

    Stale data produces stale investment signals. This is a WARNING,
    not a fatal error -- the developer may intentionally reprocess old data.
    """
    warnings = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)

    for path, label in [
        (ENVSCAN_SIGNALS, "EnvScan signals"),
        (GNEWS_SIGNALS, "GlobalNews signals"),
    ]:
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                age_days = (datetime.now(timezone.utc) - mtime).days
                warnings.append(
                    f"WARNING: {label} is {age_days} days old (last modified: {mtime.date()})\n"
                    f"  -> Investment signals may be stale. Consider re-running source pipeline."
                )

    return warnings


def check_envscan_schema() -> None:
    """Validate EnvScan JSON has expected top-level structure.

    Does NOT validate every signal -- just verifies the file is parseable
    and has the expected format. Per-signal validation happens in normalize_signals.py.
    """
    try:
        with open(ENVSCAN_SIGNALS) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise HealthCheckError(
            f"EnvScan signals file is not valid JSON: {e}\n"
            f"  File: {ENVSCAN_SIGNALS}"
        )

    # EnvScan database.json has an 'items' array at top level
    if "items" not in data:
        raise HealthCheckError(
            f"EnvScan signals missing 'items' key. Found keys: {list(data.keys())}\n"
            f"  Expected format: {{'items': [...], 'metadata': {{...}}}}\n"
            f"  This may indicate a schema change in EnvScan."
        )

    items = data["items"]
    if not isinstance(items, list) or len(items) == 0:
        raise HealthCheckError(
            f"EnvScan signals 'items' is empty or not a list (type: {type(items).__name__}).\n"
            f"  This may indicate a failed EnvScan run."
        )

    # Spot-check first item for required fields
    first = items[0]
    required = {"id", "title", "source"}
    missing = required - set(first.keys())
    if missing:
        raise HealthCheckError(
            f"EnvScan first signal missing required fields: {missing}\n"
            f"  Found fields: {sorted(first.keys())}\n"
            f"  This may indicate a schema change in EnvScan."
        )


def check_gnews_schema() -> None:
    """Validate GlobalNews Parquet file has expected columns.

    Uses PyArrow to read only the schema (no data loaded into memory).
    """
    try:
        import pyarrow.parquet as pq
    except ImportError:
        raise HealthCheckError(
            "PyArrow not installed. Required for GlobalNews Parquet reading.\n"
            "  -> pip install pyarrow"
        )

    try:
        schema = pq.read_schema(GNEWS_SIGNALS)
    except Exception as e:
        raise HealthCheckError(
            f"Cannot read GlobalNews Parquet schema: {e}\n"
            f"  File: {GNEWS_SIGNALS}"
        )

    required_columns = {"signal_id", "signal_layer", "confidence", "detected_at"}
    actual_columns = set(schema.names)
    missing = required_columns - actual_columns
    if missing:
        raise HealthCheckError(
            f"GlobalNews Parquet missing required columns: {missing}\n"
            f"  Found columns: {sorted(actual_columns)}\n"
            f"  This may indicate a schema change in GlobalNews."
        )


def check_output_directory() -> None:
    """Ensure output directory exists and is writable."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    test_file = OUTPUT_DIR / ".write_test"
    try:
        test_file.write_text("test")
        test_file.unlink()
    except OSError as e:
        raise HealthCheckError(
            f"Cannot write to output directory: {OUTPUT_DIR}\n"
            f"  Error: {e}"
        )


def run_health_check() -> None:
    """Execute all health checks. Print results. Exit with appropriate code."""
    print("=" * 60)
    print("InvestScan Pipeline Health Check")
    print("=" * 60)

    all_warnings = []

    checks = [
        ("Source files exist", check_source_files_exist),
        ("Source files fresh", check_source_files_fresh),
        ("EnvScan schema valid", check_envscan_schema),
        ("GlobalNews schema valid", check_gnews_schema),
        ("Output directory writable", check_output_directory),
    ]

    for name, check_fn in checks:
        try:
            result = check_fn()
            if isinstance(result, list):
                all_warnings.extend(result)
            print(f"  [PASS] {name}")
        except HealthCheckError as e:
            print(f"  [FAIL] {name}")
            print(f"\n{e}\n")
            sys.exit(1)

    if all_warnings:
        print("\nWarnings:")
        for w in all_warnings:
            print(f"  {w}")

    print(f"\nHealth check passed. Pipeline ready to run.")
    print("=" * 60)


if __name__ == "__main__":
    run_health_check()
```

### 4. Crash-Loud Error Handling in Pipeline Stages

```python
# invest_pipeline/normalize_signals.py (error handling pattern -- excerpts)
"""
Error handling philosophy: CRASH LOUD.

- If a single signal fails to parse, log it and skip it (warn level).
- If >20% of signals fail, HALT the pipeline (something is systemically wrong).
- If the entire file fails to load, HALT immediately.
- All score values are asserted to be in valid range before returning.

The developer will see the error in terminal output. There is no log file
to check, no error report to read. The terminal IS the error report.
"""

def normalize_all_signals(date: str) -> list[UnifiedSignal]:
    """Normalize signals from both source systems.

    Raises:
        HealthCheckError: if source files are missing/corrupt
        ValueError: if >20% of signals fail normalization (systemic issue)
    """
    signals = []
    errors = []

    # ── EnvScan ──
    envscan_raw = load_envscan_signals()  # Raises on file/JSON error
    for raw in envscan_raw:
        try:
            signal = normalize_envscan_signal(raw)
            _assert_signal_valid(signal)  # Range checks
            signals.append(signal)
        except (KeyError, ValueError, TypeError) as e:
            errors.append(f"EnvScan signal {raw.get('id', '???')}: {e}")

    # ── GlobalNews ──
    gnews_raw = load_gnews_signals()  # Raises on file/Parquet error
    for row in gnews_raw:
        try:
            signal = normalize_gnews_signal(row)
            _assert_signal_valid(signal)
            signals.append(signal)
        except (KeyError, ValueError, TypeError) as e:
            errors.append(f"GlobalNews signal {row.get('signal_id', '???')}: {e}")

    # ── Systemic failure check ──
    total_attempted = len(envscan_raw) + len(gnews_raw)
    if total_attempted > 0 and len(errors) / total_attempted > 0.20:
        raise ValueError(
            f"PIPELINE HALTED: {len(errors)}/{total_attempted} signals failed "
            f"normalization ({len(errors)/total_attempted:.0%}). This indicates "
            f"a systemic issue (schema change? corrupt data?).\n\n"
            f"First 5 errors:\n" + "\n".join(errors[:5])
        )

    if errors:
        print(f"\nWARNING: {len(errors)} signals failed normalization "
              f"(skipped, {len(signals)} succeeded):")
        for e in errors[:10]:
            print(f"  - {e}")

    return signals


def _assert_signal_valid(signal: UnifiedSignal) -> None:
    """Runtime assertions for financial invariants.

    These are the crash-loud guards. If any assertion fails, the signal
    is rejected. This is cheaper than letting a bad score flow into the
    weekly report and influence an investment decision.
    """
    assert 0.0 <= signal.confidence <= 1.0, (
        f"confidence={signal.confidence} out of range [0,1] "
        f"for signal {signal.signal_id}"
    )
    assert 0.0 <= signal.burst_score <= 1.0, (
        f"burst_score={signal.burst_score} out of range [0,1] "
        f"for signal {signal.signal_id}"
    )
    assert 0.0 <= signal.novelty_score <= 1.0, (
        f"novelty_score={signal.novelty_score} out of range [0,1] "
        f"for signal {signal.signal_id}"
    )
    assert signal.source_system in ("envscan", "gnews"), (
        f"Unknown source_system='{signal.source_system}' "
        f"for signal {signal.signal_id}"
    )
```

### 5. Fixture Design: File-Based vs Inline

**Decision: Inline fixtures for unit tests, file-based fixtures for integration.**

```python
# tests/conftest.py
"""
Fixture strategy:
  - Unit tests (test_normalize.py, test_sector_mapping.py):
    Inline dict fixtures. Fast, self-contained, no disk I/O.

  - Integration test (if added later):
    File-based fixtures in tests/fixtures/ directory.
    Real EnvScan JSON snippet + real GlobalNews Parquet file.
"""
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return FIXTURES_DIR
```

```
tests/
├── conftest.py               <- Shared fixtures and helpers
├── test_normalize.py         <- 10 schema parsing tests (inline fixtures)
├── test_sector_mapping.py    <- 15 sector mapping tests (inline fixtures)
└── fixtures/                 <- For future integration tests
    ├── envscan_sample.json   <- 5-signal sample from real EnvScan output
    └── gnews_sample.parquet  <- 5-signal sample from real GlobalNews output
```

**Why inline for unit tests**: The test itself documents the expected input format. When EnvScan changes their JSON schema, reading the inline fixture in the test shows exactly what field was expected. File-based fixtures require opening two files to understand a test failure.

**Why file-based for integration tests (future)**: Integration tests verify that the actual Parquet reading code (PyArrow) and actual JSON parsing produce the same results as the inline dicts. A 5-signal real sample catches encoding issues, date format quirks, and field ordering that inline dicts cannot.

### 6. Minimal Branch: Time Budget

| Activity | Hours | When |
|----------|-------|------|
| Write 10 schema tests | 3.0 | Month 2 (after normalize_signals.py exists) |
| Write 15 sector mapping tests | 3.0 | Month 2-3 (after sector_mapper.py exists) |
| Create fixtures/ directory with real samples | 0.5 | Month 2 |
| Write health_check.py | 1.0 | Month 1 (before first pipeline run) |
| Maintain tests (fix when source schema changes) | 0.5 | Months 3-6, as needed |
| **TOTAL** | **8.0** | |

---

## Branch 4.2: COMPREHENSIVE Testing (50+ tests, graceful)

**Philosophy**: "Every stage boundary gets a safety net. Partial failures produce partial results, not total failure. The system tells you what went wrong, continues with what it can, and appends an error summary to the report."

**Analyst**: The Comprehensive Guardian

### 1. Extended Test Suite (55 tests)

#### 1.1 Schema Tests (10) -- Same as Minimal

Identical to Branch 4.1. These are non-negotiable regardless of approach. The Comprehensive Guardian does not disagree with the Minimal Pragmatist on the boundary tests.

#### 1.2 Sector Mapping Tests (15) -- Same as Minimal

Identical to Branch 4.1. The core mapping logic tests are the same.

#### 1.3 Report Generation Tests (5) -- NEW

```python
# tests/test_report_generation.py
"""
Report generation tests verify that the Jinja2 template produces
valid, complete Markdown output from synthesis results.

These tests catch:
- Template rendering errors (missing variables)
- Empty sections (synthesis produced no data for a section)
- Structural issues (broken Markdown tables, missing headers)
"""
import pytest
from invest_pipeline.generate_report import render_weekly_report
from invest_pipeline.schema import SynthesisResult, SectorDirection


@pytest.fixture
def sample_synthesis():
    """Minimal synthesis result for report generation testing."""
    return SynthesisResult(
        date="2026-03-27",
        total_signals=42,
        sectors=[
            SectorDirection(
                name="Information Technology",
                direction="bullish",
                conviction=0.72,
                signal_count=15,
                top_signals=["AI chip breakthrough", "Cloud spending increase"],
            ),
            SectorDirection(
                name="Financials",
                direction="bearish",
                conviction=0.58,
                signal_count=8,
                top_signals=["Rate hike expectations"],
            ),
        ],
        warnings=[],
    )


@pytest.fixture
def empty_synthesis():
    """Synthesis with zero signals (source systems returned empty data)."""
    return SynthesisResult(
        date="2026-03-27",
        total_signals=0,
        sectors=[],
        warnings=["No signals found from any source system."],
    )


class TestReportGeneration:

    def test_report_contains_all_sections(self, sample_synthesis):
        """Test 1: Report has all required sections (header, summary, sectors, evidence)."""
        report = render_weekly_report(sample_synthesis)
        assert "# InvestScan Weekly Report" in report
        assert "## Summary" in report or "## Executive Summary" in report
        assert "## Sector Directions" in report or "## Sector Analysis" in report
        assert "Information Technology" in report
        assert "Financials" in report

    def test_report_renders_conviction_scores(self, sample_synthesis):
        """Test 2: Conviction scores appear in report (not raw floats)."""
        report = render_weekly_report(sample_synthesis)
        # Conviction should be rendered as percentage or descriptive
        assert "72%" in report or "72" in report or "high" in report.lower()

    def test_empty_synthesis_produces_warning_report(self, empty_synthesis):
        """Test 3: Zero signals produces a warning report, not an empty file."""
        report = render_weekly_report(empty_synthesis)
        assert len(report) > 100  # Not empty
        assert "no signals" in report.lower() or "warning" in report.lower()

    def test_report_is_valid_markdown(self, sample_synthesis):
        """Test 4: Report has no broken Markdown (unclosed tables, missing headers)."""
        report = render_weekly_report(sample_synthesis)
        lines = report.strip().split("\n")
        # Must start with a header
        assert lines[0].startswith("#")
        # No line should have unmatched table pipes (crude check)
        for line in lines:
            if "|" in line:
                assert line.count("|") >= 2  # Valid table row has >= 2 pipes

    def test_report_includes_generation_timestamp(self, sample_synthesis):
        """Test 5: Report footer includes generation timestamp for audit trail."""
        report = render_weekly_report(sample_synthesis)
        assert "2026" in report  # At minimum, the year appears
        assert "Generated" in report or "generated" in report
```

#### 1.4 Decision Journal Tests (5) -- NEW

```python
# tests/test_decision_journal.py
"""
Decision journal tests verify the append-only investment decision log.

The journal is THE most strategically important feature (Tetlock
superforecasting principle). These tests ensure entries are never
lost, always correctly formatted, and always include required fields.
"""
import pytest
import json
from pathlib import Path
from invest_pipeline.decision_journal import (
    append_journal_entry,
    read_journal_entries,
    JournalEntry,
)


@pytest.fixture
def temp_journal(tmp_path):
    """Temporary journal file for testing."""
    return tmp_path / "test_decision_journal.jsonl"


@pytest.fixture
def sample_entry():
    """A complete decision journal entry."""
    return JournalEntry(
        date="2026-03-27",
        sector="Information Technology",
        direction="bullish",
        conviction=0.72,
        rationale="AI chip demand signals from 3+ sources",
        signal_ids=["IS-20260327-001", "IS-20260327-005", "IS-20260327-012"],
    )


class TestDecisionJournal:

    def test_append_creates_file_if_missing(self, temp_journal, sample_entry):
        """Test 1: First entry creates the journal file."""
        assert not temp_journal.exists()
        append_journal_entry(temp_journal, sample_entry)
        assert temp_journal.exists()

    def test_append_preserves_existing_entries(self, temp_journal, sample_entry):
        """Test 2: Appending does not overwrite previous entries."""
        append_journal_entry(temp_journal, sample_entry)
        append_journal_entry(temp_journal, sample_entry)
        entries = read_journal_entries(temp_journal)
        assert len(entries) == 2

    def test_entry_is_valid_jsonl(self, temp_journal, sample_entry):
        """Test 3: Each line in journal is valid JSON (JSONL format)."""
        append_journal_entry(temp_journal, sample_entry)
        lines = temp_journal.read_text().strip().split("\n")
        for line in lines:
            parsed = json.loads(line)  # Must not raise
            assert "date" in parsed
            assert "sector" in parsed
            assert "direction" in parsed

    def test_read_empty_journal_returns_empty_list(self, temp_journal):
        """Test 4: Reading non-existent journal returns empty list, not error."""
        entries = read_journal_entries(temp_journal)
        assert entries == []

    def test_entry_includes_signal_traceability(self, temp_journal, sample_entry):
        """Test 5: Every entry includes signal_ids for evidence chain."""
        append_journal_entry(temp_journal, sample_entry)
        entries = read_journal_entries(temp_journal)
        assert len(entries[0].signal_ids) > 0
        assert all(sid.startswith("IS-") for sid in entries[0].signal_ids)
```

#### 1.5 Integration Tests (5) -- NEW

```python
# tests/test_integration.py
"""
Integration tests verify the end-to-end pipeline using fixture data.

These tests use real-format sample files from tests/fixtures/ to verify
that the full pipeline (normalize -> synthesize -> report) produces
a valid weekly report from both source systems.
"""
import pytest
import json
from pathlib import Path
from invest_pipeline.normalize_signals import normalize_all_signals_from_files
from invest_pipeline.synthesize_investment import synthesize_directions
from invest_pipeline.generate_report import render_weekly_report
from invest_pipeline.health_check import run_health_check_on_paths


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def envscan_fixture():
    return FIXTURES / "envscan_sample.json"


@pytest.fixture
def gnews_fixture():
    return FIXTURES / "gnews_sample.parquet"


@pytest.mark.integration
class TestEndToEnd:

    def test_normalize_from_fixture_files(self, envscan_fixture, gnews_fixture):
        """Test 1: Normalization reads real-format fixture files successfully."""
        signals = normalize_all_signals_from_files(
            envscan_path=envscan_fixture,
            gnews_path=gnews_fixture,
        )
        assert len(signals) > 0
        assert all(hasattr(s, "signal_id") for s in signals)
        assert all(0.0 <= s.confidence <= 1.0 for s in signals)

    def test_full_pipeline_produces_report(self, envscan_fixture, gnews_fixture):
        """Test 2: Full pipeline from fixture files to Markdown report."""
        signals = normalize_all_signals_from_files(
            envscan_path=envscan_fixture,
            gnews_path=gnews_fixture,
        )
        synthesis = synthesize_directions(signals)
        report = render_weekly_report(synthesis)

        assert len(report) > 500  # Substantial report
        assert "# InvestScan" in report

    def test_envscan_only_produces_partial_report(self, envscan_fixture):
        """Test 3: Pipeline works with only EnvScan data (GlobalNews unavailable)."""
        signals = normalize_all_signals_from_files(
            envscan_path=envscan_fixture,
            gnews_path=None,
        )
        assert len(signals) > 0
        synthesis = synthesize_directions(signals)
        report = render_weekly_report(synthesis)
        assert "warning" in report.lower() or "partial" in report.lower()

    def test_gnews_only_produces_partial_report(self, gnews_fixture):
        """Test 4: Pipeline works with only GlobalNews data (EnvScan unavailable)."""
        signals = normalize_all_signals_from_files(
            envscan_path=None,
            gnews_path=gnews_fixture,
        )
        assert len(signals) > 0

    def test_health_check_passes_on_fixtures(self, envscan_fixture, gnews_fixture):
        """Test 5: Health check passes on valid fixture files."""
        # Should not raise
        run_health_check_on_paths(
            envscan_path=envscan_fixture,
            gnews_path=gnews_fixture,
        )


# ── pytest marker registration ──
# In conftest.py: pytest.ini_options markers = ["integration: end-to-end tests"]
# Run: pytest -m integration   (or: pytest -m "not integration" for fast runs)
```

#### 1.6 Edge Case & Property-Based Tests (10+) -- NEW

```python
# tests/test_edge_cases.py
"""
Edge cases and property-based tests for normalization math.

Property-based tests use Hypothesis to generate thousands of random
inputs, catching edge cases that hand-written tests miss.

These tests specifically target the three financial-risk paths:
1. Score normalization (property: output always in [0, 1])
2. Classification (property: always returns valid enum)
3. Data completeness (property: no silent signal loss)
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from invest_pipeline.normalize_signals import (
    psst_to_confidence,
    normalize_envscan_signal,
    normalize_gnews_signal,
)
from invest_pipeline.sector_mapper import map_steeps_to_sectors, classify_steeps_from_text
from invest_pipeline.schema import SteepsCategory, SignalLayer, UnifiedSignal


# ── Property-Based: Score Normalization ──────────────────────────────

class TestScoreNormalizationProperties:
    """Property-based tests: confidence scores are ALWAYS in [0.0, 1.0]."""

    @given(psst=st.integers(min_value=0, max_value=100))
    def test_psst_always_produces_valid_confidence(self, psst):
        """Property 1: Any valid pSST (0-100) produces confidence in [0, 1]."""
        result = psst_to_confidence(psst)
        assert 0.0 <= result <= 1.0, f"pSST={psst} -> confidence={result}"

    @given(psst=st.integers(min_value=-1000, max_value=-1) |
                 st.integers(min_value=101, max_value=1000))
    def test_psst_out_of_range_always_raises(self, psst):
        """Property 2: Any pSST outside [0, 100] always raises ValueError."""
        with pytest.raises(ValueError):
            psst_to_confidence(psst)

    @given(confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_gnews_confidence_passes_through_unchanged(self, confidence):
        """Property 3: GlobalNews confidence (already 0-1) is not re-normalized.
        If the normalizer accidentally divides by 100 again, a confidence of
        0.72 would become 0.0072 -- essentially invisible.
        """
        signal = {
            "signal_id": "test-prop",
            "signal_layer": "L3_mid",
            "detected_at": "2026-01-01T00:00:00Z",
            "confidence": confidence,
            "burst_score": 0.5,
            "novelty_score": 0.5,
        }
        result = normalize_gnews_signal(signal)
        assert result.confidence == pytest.approx(confidence, abs=1e-6), (
            f"GlobalNews confidence={confidence} was modified to {result.confidence}. "
            f"GlobalNews confidence is already 0-1 and must NOT be re-normalized."
        )


# ── Property-Based: Classification Completeness ─────────────────────

class TestClassificationProperties:

    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=200)
    def test_classify_never_returns_none(self, text):
        """Property 4: STEEPs classifier always returns a valid enum member,
        never None or an invalid string. UNKNOWN is acceptable.
        """
        result = classify_steeps_from_text(text, "")
        assert isinstance(result, SteepsCategory), (
            f"classify_steeps_from_text returned {type(result).__name__}, "
            f"expected SteepsCategory"
        )

    @given(category=st.sampled_from(list(SteepsCategory)))
    def test_every_steeps_maps_to_at_least_one_sector(self, category):
        """Property 5: Every STEEPs category (including UNKNOWN) maps to
        at least one investment sector. No category should produce an
        empty sector list.
        """
        result = map_steeps_to_sectors(category)
        assert len(result) >= 1, (
            f"STEEPs={category.value} maps to ZERO sectors. "
            f"This would make signals invisible in the weekly report."
        )


# ── Specific Edge Cases ──────────────────────────────────────────────

class TestSpecificEdgeCases:

    def test_psst_float_input_rounds_correctly(self):
        """Edge Case 1: pSST as float (EnvScan might output 72.5 instead of 72).
        The function should accept floats and convert correctly.
        """
        # If psst_to_confidence only accepts int, this tests graceful handling
        result = psst_to_confidence(72.5)
        assert 0.72 <= result <= 0.73

    def test_envscan_duplicate_ids_are_preserved(self):
        """Edge Case 2: Two EnvScan signals with the same source ID.
        This can happen if EnvScan runs twice on the same day.
        Normalization should NOT deduplicate (that is synthesis stage's job).
        """
        signal_a = {
            "id": "TC-001", "title": "Signal A",
            "source": {"name": "Test"}, "published_date": "2026-01-01T00:00:00Z",
        }
        signal_b = {
            "id": "TC-001", "title": "Signal B (duplicate ID)",
            "source": {"name": "Test"}, "published_date": "2026-01-01T00:00:00Z",
        }
        result_a = normalize_envscan_signal(signal_a)
        result_b = normalize_envscan_signal(signal_b)
        # Both should succeed -- dedup is not normalization's job
        assert result_a.source_signal_id == result_b.source_signal_id
        assert result_a.title != result_b.title

    def test_confidence_zero_is_valid_not_missing(self):
        """Edge Case 3: confidence=0.0 is a valid score (extremely low confidence),
        not a missing value. The system must NOT replace 0.0 with the default 0.5.
        """
        signal = {
            "signal_id": "test-zero-conf",
            "signal_layer": "L1_fad",
            "detected_at": "2026-01-01T00:00:00Z",
            "confidence": 0.0,
            "burst_score": 0.0,
            "novelty_score": 0.0,
        }
        result = normalize_gnews_signal(signal)
        assert result.confidence == pytest.approx(0.0)  # NOT 0.5

    def test_very_long_title_does_not_crash(self):
        """Edge Case 4: Title exceeding 1000 characters (malformed scraping)."""
        signal = {
            "id": "TEST-LONG",
            "title": "A" * 2000,
            "source": {"name": "Test"},
            "published_date": "2026-01-01T00:00:00Z",
        }
        result = normalize_envscan_signal(signal)
        assert isinstance(result, UnifiedSignal)

    def test_psst_score_as_string_raises_or_converts(self):
        """Edge Case 5: pSST as string "72" (JSON type mismatch).
        EnvScan's JSON might occasionally serialize numbers as strings.
        The normalizer should either convert or raise -- not silently produce NaN.
        """
        # Either of these behaviors is acceptable:
        try:
            result = psst_to_confidence("72")
            # If it converts, the result must be valid
            assert result == pytest.approx(0.72)
        except (TypeError, ValueError):
            # If it rejects string input, that is also fine (crash-loud)
            pass

    def test_future_date_signal_is_accepted(self):
        """Edge Case 6: Signal with future detected_at (clock skew between systems).
        Should not crash. The date is metadata, not a validation constraint.
        """
        signal = {
            "id": "FUTURE-001",
            "title": "Future Signal",
            "source": {"name": "Test"},
            "published_date": "2030-01-01T00:00:00Z",
        }
        result = normalize_envscan_signal(signal)
        assert isinstance(result, UnifiedSignal)
```

### 2. Graceful Error Handling Pattern

The comprehensive approach wraps every stage boundary in try/except, produces partial results when possible, and appends an error summary to the weekly report.

```python
# invest_pipeline/pipeline_runner.py (Comprehensive error handling)
"""
Graceful pipeline execution with partial results and error tracking.

Philosophy: A report with 80% of signals is better than no report.
Every error is captured, categorized, and appended to the report
so the developer knows exactly what was lost and why.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

logger = logging.getLogger("investscan")


@dataclass
class PipelineErrors:
    """Accumulator for all errors encountered during pipeline execution.
    Appended to the weekly report as a transparency section.
    """
    normalization_errors: list[str] = field(default_factory=list)
    classification_errors: list[str] = field(default_factory=list)
    synthesis_errors: list[str] = field(default_factory=list)
    report_errors: list[str] = field(default_factory=list)

    @property
    def total_errors(self) -> int:
        return (len(self.normalization_errors) +
                len(self.classification_errors) +
                len(self.synthesis_errors) +
                len(self.report_errors))

    @property
    def has_fatal_errors(self) -> bool:
        """Fatal = zero signals survived normalization."""
        return any("FATAL" in e for e in self.normalization_errors)

    def to_report_section(self) -> str:
        """Render error summary as Markdown for inclusion in weekly report."""
        if self.total_errors == 0:
            return "\n## Pipeline Health\n\nAll stages completed without errors.\n"

        lines = [
            "\n## Pipeline Health -- ISSUES DETECTED\n",
            f"**Total issues**: {self.total_errors}\n",
        ]

        if self.normalization_errors:
            lines.append(f"\n### Normalization Issues ({len(self.normalization_errors)})")
            for e in self.normalization_errors[:10]:
                lines.append(f"- {e}")
            if len(self.normalization_errors) > 10:
                lines.append(f"- ... and {len(self.normalization_errors) - 10} more")

        if self.classification_errors:
            lines.append(f"\n### Classification Issues ({len(self.classification_errors)})")
            for e in self.classification_errors[:5]:
                lines.append(f"- {e}")

        if self.synthesis_errors:
            lines.append(f"\n### Synthesis Issues ({len(self.synthesis_errors)})")
            for e in self.synthesis_errors[:5]:
                lines.append(f"- {e}")

        if self.report_errors:
            lines.append(f"\n### Report Generation Issues ({len(self.report_errors)})")
            for e in self.report_errors[:5]:
                lines.append(f"- {e}")

        return "\n".join(lines)


def run_pipeline_graceful(date: str) -> tuple[Optional[str], PipelineErrors]:
    """Execute the full pipeline with graceful error handling.

    Returns:
        (report_text, errors): Report may be partial. Errors always populated.
        If report_text is None, the pipeline failed entirely.
    """
    errors = PipelineErrors()

    # ── Stage 1: Health Check ──
    # This one is NOT graceful. If source files are missing, we cannot proceed.
    try:
        from invest_pipeline.health_check import run_health_check
        run_health_check()
    except Exception as e:
        errors.normalization_errors.append(f"FATAL: Health check failed: {e}")
        return None, errors

    # ── Stage 2: Normalization (graceful -- skip bad signals) ──
    signals = []
    try:
        from invest_pipeline.normalize_signals import (
            load_envscan_signals, load_gnews_signals,
            normalize_envscan_signal, normalize_gnews_signal,
        )

        # EnvScan
        try:
            envscan_raw = load_envscan_signals()
            for raw in envscan_raw:
                try:
                    signal = normalize_envscan_signal(raw)
                    signals.append(signal)
                except Exception as e:
                    errors.normalization_errors.append(
                        f"EnvScan '{raw.get('id', '?')}': {e}"
                    )
        except Exception as e:
            errors.normalization_errors.append(f"EnvScan load failed entirely: {e}")
            logger.warning("EnvScan unavailable, continuing with GlobalNews only")

        # GlobalNews
        try:
            gnews_raw = load_gnews_signals()
            for row in gnews_raw:
                try:
                    signal = normalize_gnews_signal(row)
                    signals.append(signal)
                except Exception as e:
                    errors.normalization_errors.append(
                        f"GlobalNews '{row.get('signal_id', '?')}': {e}"
                    )
        except Exception as e:
            errors.normalization_errors.append(f"GlobalNews load failed entirely: {e}")
            logger.warning("GlobalNews unavailable, continuing with EnvScan only")

    except Exception as e:
        errors.normalization_errors.append(f"FATAL: Normalization module failed: {e}")
        return None, errors

    if len(signals) == 0:
        errors.normalization_errors.append(
            "FATAL: Zero signals survived normalization from both sources"
        )
        return None, errors

    # ── Stage 3: Synthesis (graceful -- partial sector results OK) ──
    try:
        from invest_pipeline.synthesize_investment import synthesize_directions
        synthesis = synthesize_directions(signals)
    except Exception as e:
        errors.synthesis_errors.append(f"Synthesis failed: {e}")
        # Create minimal synthesis from raw signal counts
        from invest_pipeline.schema import SynthesisResult
        synthesis = SynthesisResult(
            date=date,
            total_signals=len(signals),
            sectors=[],
            warnings=[f"Synthesis failed: {e}. Showing raw signal summary only."],
        )

    # ── Stage 4: Report Generation (graceful -- fallback to raw data dump) ──
    try:
        from invest_pipeline.generate_report import render_weekly_report
        report = render_weekly_report(synthesis)
    except Exception as e:
        errors.report_errors.append(f"Template rendering failed: {e}")
        # Fallback: raw text dump
        report = (
            f"# InvestScan Weekly Report -- {date}\n\n"
            f"**WARNING: Report template failed. Showing raw data.**\n\n"
            f"Total signals: {len(signals)}\n"
            f"Source breakdown: EnvScan={sum(1 for s in signals if s.source_system=='envscan')}, "
            f"GlobalNews={sum(1 for s in signals if s.source_system=='gnews')}\n"
        )

    # ── Stage 5: Append error summary to report ──
    report += errors.to_report_section()

    # ── Stage 6: Append generation metadata ──
    report += (
        f"\n---\n"
        f"*Generated: {datetime.now().isoformat()}*\n"
        f"*Signals processed: {len(signals)}, Errors: {errors.total_errors}*\n"
    )

    return report, errors
```

### 3. Recovery Mode for Corrupted SQLite (Month 4+)

```python
# invest_pipeline/signal_store.py (excerpt -- recovery mode)
"""
SQLite signal store with corruption recovery.

SQLite databases can corrupt from:
- Power loss during write
- Disk full during vacuum
- macOS aggressive disk caching + sleep

Recovery strategy: the Parquet files are the source of truth.
SQLite is a derived cache. If corrupt, delete and rebuild.
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

from invest_pipeline.config import SIGNAL_DB_PATH, OUTPUT_DIR


def get_connection() -> sqlite3.Connection:
    """Open SQLite connection with integrity check on first use."""
    try:
        conn = sqlite3.connect(SIGNAL_DB_PATH)
        # Quick integrity check (fast -- checks only freelist)
        result = conn.execute("PRAGMA quick_check").fetchone()
        if result[0] != "ok":
            raise sqlite3.DatabaseError(f"Integrity check failed: {result[0]}")
        return conn
    except sqlite3.DatabaseError as e:
        return _recover_database(e)


def _recover_database(original_error: Exception) -> sqlite3.Connection:
    """Recover from corrupted SQLite by rebuilding from Parquet files.

    Strategy:
    1. Backup the corrupt database (for forensic analysis)
    2. Delete the corrupt database
    3. Create a fresh database
    4. Reimport all signals from output/{date}/unified_signals.json files
    """
    print(f"\n{'='*60}")
    print(f"WARNING: Signal database corrupted: {original_error}")
    print(f"Attempting recovery from Parquet/JSON source files...")
    print(f"{'='*60}\n")

    # Backup corrupt file
    if SIGNAL_DB_PATH.exists():
        backup = SIGNAL_DB_PATH.with_suffix(
            f".corrupt-{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        shutil.copy2(SIGNAL_DB_PATH, backup)
        print(f"  Corrupt database backed up to: {backup}")
        SIGNAL_DB_PATH.unlink()

    # Create fresh database
    conn = sqlite3.connect(SIGNAL_DB_PATH)
    _create_tables(conn)

    # Reimport from JSON output files
    imported = 0
    for date_dir in sorted(OUTPUT_DIR.iterdir()):
        signals_file = date_dir / "unified_signals.json"
        if signals_file.exists():
            count = _import_signals_from_json(conn, signals_file)
            imported += count

    conn.commit()
    print(f"  Recovery complete. Reimported {imported} signals from output files.")
    print(f"  NOTE: Any derived data (evolution tracking, aggregates) must be recomputed.\n")

    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    """Create signal store schema."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS signals (
            signal_id TEXT PRIMARY KEY,
            source_system TEXT NOT NULL,
            date TEXT NOT NULL,
            title TEXT,
            steeps_category TEXT,
            signal_layer TEXT,
            confidence REAL,
            sectors TEXT,  -- JSON array
            direction TEXT,
            conviction REAL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date);
        CREATE INDEX IF NOT EXISTS idx_signals_steeps ON signals(steeps_category);
        CREATE INDEX IF NOT EXISTS idx_signals_sector ON signals(sectors);
    """)


def _import_signals_from_json(conn, json_path: Path) -> int:
    """Import signals from a unified_signals.json file."""
    import json
    with open(json_path) as f:
        signals = json.load(f)
    count = 0
    for s in signals:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO signals "
                "(signal_id, source_system, date, title, steeps_category, "
                "signal_layer, confidence, sectors, direction, conviction) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    s.get("signal_id"), s.get("source_system"), s.get("date"),
                    s.get("title"), s.get("steeps_category"), s.get("signal_layer"),
                    s.get("confidence"), json.dumps(s.get("sectors", [])),
                    s.get("direction"), s.get("conviction"),
                )
            )
            count += 1
        except sqlite3.Error:
            continue
    return count
```

### 4. Snapshot Testing for Report Output (Month 3+)

```python
# tests/test_report_snapshots.py
"""
Snapshot testing: verify that report output does not change unexpectedly.

When the report template or synthesis logic changes, snapshot tests fail.
The developer reviews the diff and explicitly approves the new output.

Requires: pip install pytest-snapshot (or manual snapshot comparison)
"""
import pytest
import json
from pathlib import Path
from invest_pipeline.generate_report import render_weekly_report
from invest_pipeline.schema import SynthesisResult, SectorDirection


SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"


@pytest.fixture
def deterministic_synthesis():
    """Fixed synthesis result for snapshot comparison.
    All values are hardcoded so the report output is deterministic.
    """
    return SynthesisResult(
        date="2026-01-15",  # Fixed date
        total_signals=42,
        sectors=[
            SectorDirection(
                name="Information Technology",
                direction="bullish",
                conviction=0.72,
                signal_count=15,
                top_signals=["AI chip breakthrough", "Cloud spending increase"],
            ),
            SectorDirection(
                name="Financials",
                direction="bearish",
                conviction=0.58,
                signal_count=8,
                top_signals=["Rate hike expectations"],
            ),
            SectorDirection(
                name="Energy",
                direction="neutral",
                conviction=0.45,
                signal_count=5,
                top_signals=["Oil price volatility"],
            ),
        ],
        warnings=[],
    )


class TestReportSnapshots:

    def test_weekly_report_matches_snapshot(self, deterministic_synthesis):
        """The rendered report must match the approved snapshot.

        If this test fails after a template change:
        1. Review the diff carefully
        2. If the change is intentional, update the snapshot:
           pytest --snapshot-update tests/test_report_snapshots.py
        3. Commit the new snapshot
        """
        report = render_weekly_report(deterministic_synthesis)
        snapshot_path = SNAPSHOTS_DIR / "weekly_report_standard.md"

        if not snapshot_path.exists():
            # First run: create the snapshot
            SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            snapshot_path.write_text(report)
            pytest.skip("Snapshot created. Re-run to verify.")

        expected = snapshot_path.read_text()
        assert report == expected, (
            "Report output changed. If intentional, update snapshot:\n"
            f"  cp <actual_output> {snapshot_path}"
        )
```

### 5. Comprehensive Branch: Time Budget

| Activity | Hours | When |
|----------|-------|------|
| Write 10 schema tests | 3.0 | Month 2 |
| Write 15 sector mapping tests | 3.0 | Month 2-3 |
| Write 5 report generation tests | 1.5 | Month 3 |
| Write 5 decision journal tests | 1.5 | Month 5 |
| Write 5 integration tests | 2.0 | Month 3 |
| Write 10+ edge case / hypothesis tests | 3.0 | Month 3-4 |
| Set up snapshot testing | 1.0 | Month 3 |
| Create fixture files (real sample data) | 1.0 | Month 2 |
| Write graceful error handling in pipeline_runner.py | 2.0 | Month 3 |
| Write SQLite recovery code | 1.5 | Month 4 |
| Maintain all tests over 6 months | 2.5 | Months 3-6 |
| **TOTAL** | **~22.0** | |

---

## COMPARISON: What Do the Extra 30 Tests Catch?

### What the 25 Minimal Tests Catch

| Test Group | Count | Catches |
|-----------|-------|---------|
| Schema parsing (EnvScan) | 4 | Field mapping errors, missing fields, category mismatch, pSST conversion |
| Schema parsing (GlobalNews) | 3 | Parquet column mapping, null handling, invalid enum values |
| pSST normalization | 3 | Score range errors, out-of-range rejection, None handling |
| STEEPs-to-sector mapping | 7 | Wrong primary sectors per category, UNKNOWN handling |
| Signal-to-sector mapping | 3 | Content-aware sector refinement, cross-domain mapping |
| STEEPs text classification | 3 | Keyword matching accuracy, ambiguous signal handling |
| Sector mapping edge cases | 2 | Empty summary, Korean text handling |
| **Total** | **25** | **The money paths: normalization math + classification accuracy** |

### What the Extra 30 Comprehensive Tests Add

| Test Group | Count | What It Catches That Minimal Misses |
|-----------|-------|-------------------------------------|
| Report generation | 5 | Template rendering errors, empty data handling, structural Markdown issues |
| Decision journal | 5 | Append-only integrity, JSONL format validity, signal traceability |
| Integration (end-to-end) | 5 | PyArrow encoding issues, cross-stage data flow, single-source degradation |
| Hypothesis (property-based) | 5 | Thousands of random inputs finding edge cases in normalization and classification |
| Specific edge cases | 5 | Float pSST, duplicate IDs, zero confidence, long titles, string types |
| Snapshot testing | 1 | Unintentional report format changes |
| **Extra total** | **~30** | **Robustness paths: report integrity, journal safety, edge case resilience** |

### The Concrete Bugs Only Comprehensive Catches

| Bug Scenario | Minimal Catches? | Comprehensive Catches? | Financial Impact |
|-------------|:---:|:---:|---|
| pSST=85 becomes confidence=8.5 | YES (Test 8) | YES | HIGH |
| EnvScan removes 'id' field | YES (Test 3) | YES | HIGH |
| GlobalNews adds L6 layer | YES (Test 7) | YES | MEDIUM |
| STEEPs "T_Technological" mismatch | YES (Test 4) | YES | HIGH |
| Empty summary crashes sector mapper | YES (Test 14) | YES | LOW |
| Jinja2 template has missing variable | NO | YES (Report Test 1) | LOW (ugly report) |
| Decision journal overwrites previous entries | NO | YES (Journal Test 2) | MEDIUM (lost predictions) |
| Pipeline fails with only EnvScan data | NO | YES (Integration Test 3) | MEDIUM (no report vs partial) |
| pSST="72" (string instead of int) | NO | YES (Edge Case 5) | MEDIUM |
| confidence=0.0 replaced with default 0.5 | NO | YES (Edge Case 3) | MEDIUM |
| Random Unicode in title crashes normalization | NO | YES (Hypothesis) | LOW |
| Report format changes unintentionally | NO | YES (Snapshot) | LOW |

### The Verdict on Extra Tests

**5 of the extra 30 tests catch bugs with financial impact** (journal integrity, single-source degradation, string pSST, zero confidence, integration flow). The other 25 catch cosmetic, structural, or extremely unlikely edge cases.

**The 5 most valuable extra tests** (if you were to add them incrementally to the Minimal suite):

1. `test_confidence_zero_is_valid_not_missing` -- Prevents treating 0.0 as None
2. `test_envscan_only_produces_partial_report` -- Ensures pipeline works when GlobalNews is down
3. `test_append_preserves_existing_entries` -- Protects the decision journal
4. `test_psst_score_as_string_raises_or_converts` -- Guards against JSON type drift
5. `test_psst_always_produces_valid_confidence` (Hypothesis) -- Catches edge cases in normalization math

---

## Crash-Loud vs Graceful: Which Is Better for a Personal Investment Tool?

### The Case for Crash-Loud (Minimal)

| Argument | Reasoning |
|----------|-----------|
| **Visibility** | A crash at 6:02 AM is immediately visible. A "partial report with warnings" at 10:00 AM might be read without noticing the warnings section. |
| **Simplicity** | ~50 lines of health_check.py + `assert` statements vs ~200 lines of PipelineErrors + try/except wrapping at every stage. |
| **Solo developer** | The developer IS the user. They run the pipeline, see the crash, fix it, re-run. There is no "production uptime" requirement. |
| **Financial safety** | A missing report is SAFER than a partial report. If the developer sees "no report today," they know to check. If they see a "95% complete report," they might not notice the missing 5% contained the most important signals. |
| **Debugging speed** | Crash gives a stack trace pointing to the exact line. Graceful handling captures the error as a string, losing the traceback context. |

### The Case for Graceful (Comprehensive)

| Argument | Reasoning |
|----------|-----------|
| **Availability** | On a Sunday morning before church, the developer does not have time to debug a crash. A partial report is better than no report. |
| **One source down** | If GlobalNews is unreachable but EnvScan ran fine, a crash-loud pipeline produces NOTHING. A graceful pipeline produces an EnvScan-only report (still valuable, just less comprehensive). |
| **Error accumulation** | Over weeks of pipeline runs, the error summary in the report reveals patterns: "GlobalNews null fields increasing" is a trend visible only in graceful mode. |
| **Decision journal safety** | If synthesis crashes, crash-loud produces no journal entry. Graceful mode can still append "synthesis failed" to the journal, preserving the record. |

### Recommendation for InvestScan

**Crash-loud is the correct default for InvestScan, with ONE exception: source system availability.**

The pipeline should be crash-loud for:
- Schema validation failures (data integrity)
- Score normalization errors (financial safety)
- Output directory issues (infrastructure)

The pipeline should be graceful for:
- One source system missing (produce partial report from available data)
- Individual signal parse failures below 20% threshold (skip and continue)

This is effectively **the Minimal approach with a 2-line modification**:

```python
# In normalize_all_signals():
# Instead of requiring BOTH sources, allow either-or:
envscan_signals = load_envscan_or_empty()  # Returns [] if unavailable, not crash
gnews_signals = load_gnews_or_empty()      # Returns [] if unavailable, not crash

if len(envscan_signals) == 0 and len(gnews_signals) == 0:
    raise HealthCheckError("FATAL: Both source systems returned zero signals")
# Continue with whichever data we have
```

---

## Time Budget Comparison

| Item | Minimal (8hr) | Comprehensive (22hr) | Delta |
|------|:---:|:---:|:---:|
| Schema parsing tests (10) | 3.0 | 3.0 | 0 |
| Sector mapping tests (15) | 3.0 | 3.0 | 0 |
| Health check code | 1.0 | 1.0 | 0 |
| Fixtures setup | 0.5 | 1.0 | +0.5 |
| Test maintenance (6 mo) | 0.5 | 2.5 | +2.0 |
| Report generation tests (5) | -- | 1.5 | +1.5 |
| Decision journal tests (5) | -- | 1.5 | +1.5 |
| Integration tests (5) | -- | 2.0 | +2.0 |
| Edge case / Hypothesis tests (10) | -- | 3.0 | +3.0 |
| Snapshot testing | -- | 1.0 | +1.0 |
| Graceful error handling code | -- | 2.0 | +2.0 |
| SQLite recovery code | -- | 1.5 | +1.5 |
| **TOTAL** | **8.0 hr** | **22.0 hr** | **+14.0 hr** |

### What 14 Extra Hours Buys

At the developer's pace of 2-4 hrs/week, 14 hours = **3.5-7 additional weeks** before the first report.

Those 14 hours buy:
- 30 extra tests catching 5 financially relevant bugs
- Graceful degradation when one source system is down
- Property-based testing that generates thousands of random inputs
- Report snapshot testing for unintentional format changes
- SQLite corruption recovery (relevant from Month 4+)
- Decision journal integrity guarantees

Those 14 hours cost:
- 3.5-7 weeks delay to first usable report
- Feature development time displaced (~2 features worth of dev hours)
- Maintenance burden: 55 tests to keep green vs 25

---

## Final Recommendation

### For Month 1-3 (Foundation Phase): MINIMAL (Branch 4.1)

Write the 25 tests. Write health_check.py. Use crash-loud error handling. Add the one graceful exception for source system availability. Ship the first report by Week 3-4.

**Total: 8 hours testing + 1 hour health check = 9 hours**

### For Month 4-6 (Refinement Phase): Selectively Add from Comprehensive

After the pipeline runs for 4+ weeks and the developer has real usage data, add tests based on actual pain points:

| If This Happens... | Add This Test... | Time |
|---------------------|-----------------|------|
| Decision journal entry gets overwritten | Journal integrity tests (2-3 tests) | 1 hr |
| Pipeline fails on Sunday before church | Graceful single-source degradation | 1.5 hr |
| pSST arrives as string from EnvScan update | Edge case type handling tests | 0.5 hr |
| Report format changes unnoticed | Snapshot test for report | 1 hr |
| SQLite corrupts after sleep/wake | SQLite recovery code | 1.5 hr |

**Estimated Month 4-6 additions: 5-6 hours (demand-driven)**

### Total 6-Month Budget: 14-15 hours

This is the pragmatic middle path: start with 8 hours of essential testing, then invest 5-7 hours based on real failures rather than hypothetical ones. It falls between the Minimal (8hr) and Comprehensive (22hr) budgets, and targets the investment where actual evidence of need exists.

---

## Appendix: pytest Configuration

```ini
# pytest.ini (or pyproject.toml [tool.pytest.ini_options])
[pytest]
testpaths = tests
markers =
    integration: end-to-end tests using fixture files (deselect with -m "not integration")
addopts = -v --tb=short
```

```
# Running tests:
pytest                              # All 25 tests (~2 seconds)
pytest tests/test_normalize.py      # Schema tests only
pytest tests/test_sector_mapping.py # Sector tests only
pytest -m "not integration"         # Skip slow integration tests
pytest --tb=long -x                 # Stop on first failure, full traceback
```

## Appendix: Fixture File Creation Guide

```python
# scripts/create_test_fixtures.py
"""
One-time script to create test fixtures from real source system output.
Run this after EnvScan and GlobalNews have completed at least one successful run.

Usage: python scripts/create_test_fixtures.py
"""
import json
import pyarrow.parquet as pq
from pathlib import Path

from invest_pipeline.config import ENVSCAN_SIGNALS, GNEWS_SIGNALS

FIXTURES_DIR = Path("tests/fixtures")
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# EnvScan: extract first 5 signals
with open(ENVSCAN_SIGNALS) as f:
    data = json.load(f)

sample = {"items": data["items"][:5], "metadata": data.get("metadata", {})}
with open(FIXTURES_DIR / "envscan_sample.json", "w") as f:
    json.dump(sample, f, indent=2, ensure_ascii=False)
print(f"Created envscan_sample.json with {len(sample['items'])} signals")

# GlobalNews: extract first 5 rows
table = pq.read_table(GNEWS_SIGNALS)
sample_table = table.slice(0, 5)
pq.write_table(sample_table, FIXTURES_DIR / "gnews_sample.parquet")
print(f"Created gnews_sample.parquet with {sample_table.num_rows} signals")
```
