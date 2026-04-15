import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analytics.funnel_analysis import compute_funnel
from analytics.cohort_retention import compute_retention
import plotly.graph_objects as go

DB_PATH = "data/events.db"
DB_EXISTS = os.path.exists(DB_PATH)

@pytest.mark.skipif(not DB_EXISTS, reason="Run loader.py first")
class TestFunnel:

    def test_funnel_stages_monotonically_decreasing(self):
        """Each funnel stage must have <= users than previous"""
        _, stats = compute_funnel(DB_PATH)
        assert stats["viewers"]     >= stats["cart_adders"]
        assert stats["cart_adders"] >= stats["purchasers"]

    def test_conversion_rates_between_0_and_100(self):
        """All conversion rates must be valid percentages"""
        _, stats = compute_funnel(DB_PATH)
        assert 0 <= stats["view_to_cart_rate"]      <= 100
        assert 0 <= stats["cart_to_purchase_rate"]  <= 100
        assert 0 <= stats["overall_conversion_rate"] <= 100

    def test_purchasers_never_exceed_viewers(self):
        """Purchasers can never exceed viewers"""
        _, stats = compute_funnel(DB_PATH)
        assert stats["purchasers"] <= stats["viewers"]

    def test_variant_a_funnel_returns_figure(self):
        """Variant A funnel must return a Plotly figure"""
        fig, _ = compute_funnel(DB_PATH, variant="A")
        assert isinstance(fig, go.Figure)

    def test_variant_b_funnel_returns_figure(self):
        """Variant B funnel must return a Plotly figure"""
        fig, _ = compute_funnel(DB_PATH, variant="B")
        assert isinstance(fig, go.Figure)

    def test_variant_stats_are_subsets_of_overall(self):
        """Variant A + Variant B users should sum close to overall"""
        _, stats_all = compute_funnel(DB_PATH)
        _, stats_a   = compute_funnel(DB_PATH, variant="A")
        _, stats_b   = compute_funnel(DB_PATH, variant="B")
        total = stats_a["viewers"] + stats_b["viewers"]
        assert abs(total - stats_all["viewers"]) <= 10

    def test_overall_conversion_consistent_with_stages(self):
        """Overall conversion must equal purchasers/viewers"""
        _, stats = compute_funnel(DB_PATH)
        expected = stats["purchasers"] / stats["viewers"] * 100
        assert abs(stats["overall_conversion_rate"] - expected) < 0.1


@pytest.mark.skipif(not DB_EXISTS, reason="Run loader.py first")
class TestCohortRetention:

    def test_returns_plotly_figure(self):
        """compute_retention must return a Plotly Figure"""
        fig = compute_retention(DB_PATH)
        assert isinstance(fig, go.Figure)

    def test_figure_has_data(self):
        """Retention heatmap must have at least one trace"""
        fig = compute_retention(DB_PATH)
        assert len(fig.data) > 0
