import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.bayesian_ab import BayesianABTest
import numpy as np

@pytest.fixture
def ab():
    return BayesianABTest()

class TestBayesianABTest:

    def test_probability_between_0_and_100(self, ab):
        """P(B>A) must always be between 0 and 100"""
        result = ab.run_test(100, 1000, 120, 1000)
        assert 0 <= result["prob_treatment_better"] <= 100

    def test_clearly_better_variant_wins(self, ab):
        """When B is clearly better, P(B>A) must be > 95"""
        result = ab.run_test(50, 1000, 400, 1000)
        assert result["prob_treatment_better"] > 95

    def test_clearly_worse_variant_loses(self, ab):
        """When B is clearly worse, P(B>A) must be < 5"""
        result = ab.run_test(400, 1000, 50, 1000)
        assert result["prob_treatment_better"] < 5

    def test_equal_variants_near_50(self, ab):
        """Equal variants should give ~50% probability"""
        result = ab.run_test(100, 1000, 100, 1000)
        assert 30 <= result["prob_treatment_better"] <= 70

    def test_recommendation_is_valid_string(self, ab):
        """Recommendation must be a non-empty string"""
        result = ab.run_test(100, 1000, 120, 1000)
        assert isinstance(result["recommendation"], str)
        assert len(result["recommendation"]) > 0

    def test_lift_positive_when_b_better(self, ab):
        """Expected lift must be positive when B converts more"""
        result = ab.run_test(100, 1000, 200, 1000)
        assert result["expected_lift_pct"] > 0

    def test_lift_negative_when_b_worse(self, ab):
        """Expected lift must be negative when B converts less"""
        result = ab.run_test(200, 1000, 100, 1000)
        assert result["expected_lift_pct"] < 0

    def test_ci_low_less_than_ci_high(self, ab):
        """Credible interval must be correctly ordered"""
        result = ab.run_test(100, 1000, 120, 1000)
        assert result["ci_low"] < result["ci_high"]

    def test_expected_loss_non_negative(self, ab):
        """Expected loss must never be negative"""
        result = ab.run_test(100, 1000, 110, 1000)
        assert result["expected_loss"] >= 0

    def test_ship_recommendation_when_clearly_better(self, ab):
        """Should recommend ship when P(B>A) > 95%"""
        result = ab.run_test(50, 1000, 400, 1000)
        assert "Ship" in result["recommendation"]

    def test_posterior_plot_returns_figure(self, ab):
        """plot_posteriors must return a Plotly Figure"""
        import plotly.graph_objects as go
        result = ab.run_test(100, 1000, 120, 1000)
        fig = ab.plot_posteriors(result)
        assert isinstance(fig, go.Figure)

    def test_large_sample_sizes(self, ab):
        """Should handle large sample sizes without error"""
        result = ab.run_test(15000, 100000, 16000, 100000)
        assert 0 <= result["prob_treatment_better"] <= 100

    def test_minimum_sample_size(self, ab):
        """Should handle very small samples without crash"""
        result = ab.run_test(1, 10, 2, 10)
        assert isinstance(result["recommendation"], str)
