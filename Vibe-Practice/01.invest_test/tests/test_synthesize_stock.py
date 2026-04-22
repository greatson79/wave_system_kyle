"""
tests/test_synthesize_stock.py — Tests for synthesize_stock.py.
Standard 85% coverage. English-First (P5-A).
"""
from __future__ import annotations

import pytest
from investscan.synthesize_stock import (
    StockFinancials,
    synthesize_stock_data,
    _mock_stock_financials,
)


DRY_RUN_CONFIG = {"mode": "dry-run"}
LIVE_CONFIG = {"mode": "live"}


class TestStockFinancialsDataclass:
    def test_fields_exist(self):
        sf = StockFinancials(
            stock_code="005930",
            stock_name="Samsung Electronics",
            category="A",
            yoy_revenue_growth=0.083,
            yoy_op_income_growth=0.342,
            latest_quarter="2025Q4",
            per_current=10.2,
            per_sector_avg=14.2,
            foreign_flow_4w=380.0,
        )
        assert sf.stock_code == "005930"
        assert sf.yoy_revenue_growth == pytest.approx(0.083)

    def test_is_frozen(self):
        sf = StockFinancials(
            stock_code="005930",
            stock_name="Test",
            category="A",
            yoy_revenue_growth=0.05,
            yoy_op_income_growth=0.08,
            latest_quarter="2025Q3",
            per_current=15.0,
            per_sector_avg=15.0,
            foreign_flow_4w=0.0,
        )
        with pytest.raises((AttributeError, TypeError)):
            sf.stock_code = "000660"  # type: ignore

    def test_data_source_default_partial(self):
        sf = StockFinancials(
            stock_code="005930",
            stock_name="Test",
            category="A",
            yoy_revenue_growth=None,
            yoy_op_income_growth=None,
            latest_quarter="",
            per_current=None,
            per_sector_avg=None,
            foreign_flow_4w=None,
        )
        assert sf.data_source == "partial"


class TestSynthesizeStockDataDryRun:
    def test_dry_run_returns_stock_financials(self):
        result = synthesize_stock_data(
            stock_code="005930",
            stock_name="Samsung Electronics",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert isinstance(result, StockFinancials)

    def test_dry_run_samsung_values(self):
        result = synthesize_stock_data(
            stock_code="005930",
            stock_name="Samsung Electronics",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert result.yoy_revenue_growth == pytest.approx(0.083)
        assert result.yoy_op_income_growth == pytest.approx(0.342)
        assert result.per_current == pytest.approx(10.2)

    def test_dry_run_unknown_stock_uses_defaults(self):
        result = synthesize_stock_data(
            stock_code="999999",
            stock_name="Unknown Co",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert result.yoy_revenue_growth is not None

    def test_dry_run_data_source_is_mock(self):
        result = synthesize_stock_data(
            stock_code="005930",
            stock_name="Samsung Electronics",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert result.data_source == "mock"

    def test_dry_run_preserves_category(self):
        result = synthesize_stock_data(
            stock_code="035420",
            stock_name="NAVER",
            category="B",
            config=DRY_RUN_CONFIG,
        )
        assert result.category == "B"

    def test_dry_run_never_raises(self):
        # Even with invalid inputs, dry-run should not raise
        result = synthesize_stock_data(
            stock_code="",
            stock_name="",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert isinstance(result, StockFinancials)

    def test_hynix_mock_values(self):
        result = synthesize_stock_data(
            stock_code="000660",
            stock_name="SK Hynix",
            category="A",
            config=DRY_RUN_CONFIG,
        )
        assert result.yoy_op_income_growth == pytest.approx(0.891)


class TestMockStockFinancials:
    def test_mock_samsung_foreign_flow(self):
        result = _mock_stock_financials("005930", "Samsung", "A")
        assert result.foreign_flow_4w == pytest.approx(380.0)

    def test_mock_naver_per_premium(self):
        result = _mock_stock_financials("035420", "NAVER", "B")
        assert result.per_current > result.per_sector_avg  # NAVER trades at premium
