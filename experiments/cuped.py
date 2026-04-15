import sqlite3

import numpy as np
import scipy.stats as stats


class CUPEDAnalysis:
    """Reduce metric variance with pre-experiment user behavior."""

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
        import sqlite3

        import pandas as pd
        from scipy import stats

        conn = sqlite3.connect(db_path)
        mid = pd.read_sql(
            "SELECT DATE(AVG(JULIANDAY(timestamp))) as mid FROM events",
            conn,
        ).iloc[0]["mid"]

        df = pd.read_sql(
            f"""
            SELECT
                user_id,
                MAX(CASE WHEN DATE(timestamp) < '{mid}'
                    AND event_type='purchase' THEN 1 ELSE 0 END) AS pre,
                MAX(CASE WHEN DATE(timestamp) >= '{mid}'
                    AND event_type='purchase' THEN 1 ELSE 0 END) AS post
            FROM events
            GROUP BY user_id
            """,
            conn,
        )
        conn.close()

        pre = df["pre"].values.astype(float)
        post = df["post"].values.astype(float)

        theta = self.compute_theta(pre, post)
        adjusted = self.adjust_metric(post, pre, theta)

        orig_var = float(np.var(post))
        cuped_var = float(np.var(adjusted))
        reduction = float((1 - cuped_var / orig_var) * 100) if orig_var > 0 else 0

        baseline = float(np.mean(post))
        mde = 0.10 * baseline
        if mde == 0:
            mde = 0.01
        z_alpha, z_beta = 1.96, 0.84

        def required_n(variance):
            if variance <= 0:
                return 1000
            return int(2 * ((z_alpha + z_beta) / mde) ** 2 * variance)

        orig_n = required_n(orig_var)
        cuped_n = required_n(cuped_var)

        orig_n = min(orig_n, 50000)
        cuped_n = min(cuped_n, 50000)

        n_reduction = orig_n - cuped_n
        days_saved = round(min(n_reduction / 300, 60), 1)
        pct_reduction = round((1 - cuped_n / orig_n) * 100, 1) if orig_n > 0 else 0

        return {
            "theta": round(float(theta), 4),
            "original_variance": round(orig_var, 6),
            "cuped_variance": round(cuped_var, 6),
            "variance_reduction_pct": round(reduction, 1),
            "original_required_n": orig_n,
            "cuped_required_n": cuped_n,
            "sample_size_reduction_pct": pct_reduction,
            "days_saved": days_saved,
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
