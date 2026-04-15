import pytest
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.cuped import CUPEDAnalysis

@pytest.fixture
def cuped():
    return CUPEDAnalysis()

@pytest.fixture
def correlated_data():
    """Pre and post metrics that are strongly correlated"""
    np.random.seed(42)
    pre  = np.random.normal(100, 20, 1000)
    post = pre * 0.85 + np.random.normal(50, 10, 1000)
    return pre, post

@pytest.fixture
def uncorrelated_data():
    """Pre and post metrics with no correlation"""
    np.random.seed(42)
    pre  = np.random.normal(100, 20, 1000)
    post = np.random.normal(150, 20, 1000)
    return pre, post

class TestCUPEDAnalysis:

    def test_theta_is_finite(self, cuped, correlated_data):
        """Theta must be a finite number"""
        pre, post = correlated_data
        theta = cuped.compute_theta(pre, post)
        assert np.isfinite(theta)

    def test_theta_positive_for_positive_correlation(self, cuped, correlated_data):
        """Theta should be positive when pre and post are positively correlated"""
        pre, post = correlated_data
        theta = cuped.compute_theta(pre, post)
        assert theta > 0

    def test_variance_reduced_with_correlated_data(self, cuped, correlated_data):
        """CUPED must reduce variance when data is correlated"""
        pre, post = correlated_data
        theta    = cuped.compute_theta(pre, post)
        adjusted = cuped.adjust_metric(post, pre, theta)
        assert np.var(adjusted) < np.var(post)

    def test_variance_not_increased_with_uncorrelated_data(self, cuped, uncorrelated_data):
        """CUPED should not significantly inflate variance for uncorrelated data"""
        pre, post = uncorrelated_data
        theta    = cuped.compute_theta(pre, post)
        adjusted = cuped.adjust_metric(post, pre, theta)
        # Allow max 10% increase for uncorrelated data
        assert np.var(adjusted) <= np.var(post) * 1.10

    def test_adjusted_metric_same_mean(self, cuped, correlated_data):
        """CUPED adjustment should preserve the mean"""
        pre, post = correlated_data
        theta    = cuped.compute_theta(pre, post)
        adjusted = cuped.adjust_metric(post, pre, theta)
        assert abs(np.mean(adjusted) - np.mean(post)) < 1e-6

    def test_adjusted_metric_same_length(self, cuped, correlated_data):
        """Output length must equal input length"""
        pre, post = correlated_data
        theta    = cuped.compute_theta(pre, post)
        adjusted = cuped.adjust_metric(post, pre, theta)
        assert len(adjusted) == len(post)

    def test_sample_size_reduced(self, cuped, correlated_data):
        """CUPED required sample size must be less than original"""
        pre, post = correlated_data
        result = cuped.run_analysis("data/events.db") \
            if os.path.exists("data/events.db") \
            else None
        if result:
            assert result["cuped_required_n"] < result["original_required_n"]

    def test_variance_reduction_pct_between_0_and_100(self, cuped, correlated_data):
        """Variance reduction percentage must be between 0 and 100"""
        pre, post = correlated_data
        theta    = cuped.compute_theta(pre, post)
        adjusted = cuped.adjust_metric(post, pre, theta)
        reduction = (1 - np.var(adjusted)/np.var(post)) * 100
        assert 0 <= reduction <= 100
