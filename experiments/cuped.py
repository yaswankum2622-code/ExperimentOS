import sqlite3

import numpy as np
import scipy.stats as stats


class CUPEDAnalysis:
    """Variance reduction for experiments using pre-period behavior."""

    def compute_theta(self, pre_metric, post_metric) -> float:
        pre_metric = np.asarray(pre_metric, dtype=float)
        post_metric = np.asarray(post_metric, dtype=float)
        self._validate_metric_shapes(pre_metric, post_metric)

        pre_variance = np.var(pre_metric)
        if pre_variance == 0:
            return 0.0

        covariance = np.cov(post_metric, pre_metric, ddof=0)[0, 1]
        return float(covariance / pre_variance)

    def adjust_metric(self, post_metric, pre_metric, theta) -> np.array:
        pre_metric = np.asarray(pre_metric, dtype=float)
        post_metric = np.asarray(post_metric, dtype=float)
        self._validate_metric_shapes(pre_metric, post_metric)

        return post_metric - theta * (pre_metric - np.mean(pre_metric))

    def run_analysis(self, db_path: str) -> dict:
        pre_metric, post_metric = self._load_user_metrics(db_path)

        theta = self.compute_theta(pre_metric, post_metric)
        adjusted = self.adjust_metric(post_metric, pre_metric, theta)

        original_variance = float(np.var(post_metric))
        cuped_variance = float(np.var(adjusted))
        variance_reduction_pct = self._pct_reduction(
            original_variance,
            cuped_variance,
        )

        z_alpha = round(stats.norm.ppf(0.975), 2)
        z_beta = round(stats.norm.ppf(0.80), 2)
        mde = 0.10
        original_n = self._required_sample_size(original_variance, z_alpha, z_beta, mde)
        cuped_n = self._required_sample_size(cuped_variance, z_alpha, z_beta, mde)
        sample_size_reduction_pct = self._pct_reduction(original_n, cuped_n)
        days_saved = (original_n - cuped_n) / 500

        return {
            "theta": float(theta),
            "original_variance": original_variance,
            "cuped_variance": cuped_variance,
            "variance_reduction_pct": float(variance_reduction_pct),
            "original_required_n": int(original_n),
            "cuped_required_n": int(cuped_n),
            "sample_size_reduction_pct": float(sample_size_reduction_pct),
            "days_saved": float(days_saved),
        }

    def _load_user_metrics(self, db_path: str) -> tuple[np.ndarray, np.ndarray]:
        cutoff_sql = """
        SELECT timestamp
        FROM events
        WHERE event_type = 'purchase'
        ORDER BY timestamp
        """

        with sqlite3.connect(db_path) as conn:
            timestamps = [row[0] for row in conn.execute(cutoff_sql).fetchall()]
            if not timestamps:
                raise ValueError("No purchase events found in events table.")

            cutoff = timestamps[len(timestamps) // 2]
            metrics_sql = """
            SELECT
                user_id,
                SUM(CASE WHEN timestamp <= ? THEN revenue ELSE 0 END) AS pre_metric,
                SUM(CASE WHEN timestamp > ? THEN revenue ELSE 0 END)  AS post_metric
            FROM events
            WHERE event_type = 'purchase'
            GROUP BY user_id
            ORDER BY user_id
            """
            rows = conn.execute(metrics_sql, (cutoff, cutoff)).fetchall()

        metrics = np.asarray(
            [
                (
                    0.0 if pre_metric is None else pre_metric,
                    0.0 if post_metric is None else post_metric,
                )
                for _, pre_metric, post_metric in rows
            ],
            dtype=float,
        )
        return metrics[:, 0], metrics[:, 1]

    @staticmethod
    def _validate_metric_shapes(pre_metric: np.ndarray, post_metric: np.ndarray) -> None:
        if pre_metric.shape != post_metric.shape:
            raise ValueError("pre_metric and post_metric must have the same shape.")
        if pre_metric.size == 0:
            raise ValueError("pre_metric and post_metric cannot be empty.")

    @staticmethod
    def _required_sample_size(
        variance: float,
        z_alpha: float,
        z_beta: float,
        mde: float,
    ) -> int:
        sample_size = 2 * (((z_alpha + z_beta) / mde) ** 2) * variance
        return int(np.ceil(sample_size))

    @staticmethod
    def _pct_reduction(original: float, reduced: float) -> float:
        if original == 0:
            return 0.0
        return (1 - reduced / original) * 100
