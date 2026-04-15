import sqlite3

import numpy as np
import plotly.graph_objects as go
from scipy.stats import beta as beta_dist


class BayesianABTest:
    """Run Bayesian A/B test on two conversion rate variants."""

    def __init__(self, n_draws: int = 100_000, random_seed: int | None = 42) -> None:
        self.n_draws = n_draws
        self.random_seed = random_seed
        self._posterior_params: dict[str, tuple[float, float]] | None = None

    def run_test(
        self,
        control_conv: int,
        control_n: int,
        treatment_conv: int,
        treatment_n: int,
    ) -> dict:
        self._validate_counts(control_conv, control_n, "control")
        self._validate_counts(treatment_conv, treatment_n, "treatment")

        alpha_a = 1 + control_conv
        beta_a = 1 + control_n - control_conv
        alpha_b = 1 + treatment_conv
        beta_b = 1 + treatment_n - treatment_conv
        self._posterior_params = {
            "A": (alpha_a, beta_a),
            "B": (alpha_b, beta_b),
        }

        rng = np.random.default_rng(self.random_seed)
        samples_a = rng.beta(alpha_a, beta_a, self.n_draws)
        samples_b = rng.beta(alpha_b, beta_b, self.n_draws)

        prob_b_better = np.mean(samples_b > samples_a) * 100
        lift_samples = ((samples_b - samples_a) / samples_a) * 100
        expected_loss = np.mean(np.maximum(samples_a - samples_b, 0))

        return {
            "prob_treatment_better": float(prob_b_better),
            "expected_lift_pct": float(np.median(lift_samples)),
            "ci_low": float(np.percentile(lift_samples, 2.5)),
            "ci_high": float(np.percentile(lift_samples, 97.5)),
            "expected_loss": float(expected_loss),
            "control_rate": float(control_conv / control_n),
            "treatment_rate": float(treatment_conv / treatment_n),
            "control_conversions": int(control_conv),
            "control_n": int(control_n),
            "treatment_conversions": int(treatment_conv),
            "treatment_n": int(treatment_n),
            "recommendation": self._recommend(prob_b_better),
        }

    def plot_posteriors(self, results: dict) -> go.Figure:
        alpha_a = 1 + results["control_conversions"]
        beta_a = 1 + results["control_n"] - results["control_conversions"]
        alpha_b = 1 + results["treatment_conversions"]
        beta_b = 1 + results["treatment_n"] - results["treatment_conversions"]

        mean_a = alpha_a / (alpha_a + beta_a)
        mean_b = alpha_b / (alpha_b + beta_b)
        std_a = (
            alpha_a
            * beta_a
            / ((alpha_a + beta_a) ** 2 * (alpha_a + beta_a + 1))
        ) ** 0.5
        std_b = (
            alpha_b
            * beta_b
            / ((alpha_b + beta_b) ** 2 * (alpha_b + beta_b + 1))
        ) ** 0.5

        x_min = max(0.001, min(mean_a, mean_b) - 5 * max(std_a, std_b))
        x_max = min(0.999, max(mean_a, mean_b) + 5 * max(std_a, std_b))
        if x_max - x_min < 0.02:
            center = (mean_a + mean_b) / 2
            x_min, x_max = max(0, center - 0.05), min(1, center + 0.05)

        x = np.linspace(x_min, x_max, 500)
        pdf_a = beta_dist.pdf(x, alpha_a, beta_a)
        pdf_b = beta_dist.pdf(x, alpha_b, beta_b)
        prob = results["prob_treatment_better"]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=pdf_a,
                mode="lines",
                name="Control (A)",
                line=dict(color="#534AB7", width=2),
                fill="tozeroy",
                fillcolor="rgba(83,74,183,0.12)",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=pdf_b,
                mode="lines",
                name="Treatment (B)",
                line=dict(color="#1D9E75", width=2),
                fill="tozeroy",
                fillcolor="rgba(29,158,117,0.12)",
            )
        )

        fig.add_vline(x=mean_a, line_color="#534AB7", line_dash="dash")
        fig.add_vline(x=mean_b, line_color="#1D9E75", line_dash="dash")

        fig.update_layout(
            title=f"Posterior Distributions — P(B > A) = {prob:.1f}%",
            xaxis_title="Conversion Rate",
            yaxis_title="Probability Density",
            legend_title_text="",
            template="plotly_white",
        )
        fig.update_xaxes(range=[x_min, x_max])

        return fig

    def load_from_db(self, db_path: str) -> dict:
        sql = """
        SELECT
            variant,
            COUNT(DISTINCT user_id) AS total_users,
            COUNT(DISTINCT CASE WHEN event_type='purchase' THEN user_id END) AS converters
        FROM events
        GROUP BY variant
        """

        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(sql).fetchall()

        return {
            variant: {"total": total_users, "converters": converters}
            for variant, total_users, converters in rows
        }

    @staticmethod
    def _validate_counts(conversions: int, total: int, label: str) -> None:
        if total <= 0:
            raise ValueError(f"{label}_n must be greater than 0.")
        if conversions < 0:
            raise ValueError(f"{label}_conv cannot be negative.")
        if conversions > total:
            raise ValueError(f"{label}_conv cannot exceed {label}_n.")

    @staticmethod
    def _recommend(prob_b_better: float) -> str:
        if prob_b_better > 95:
            return "Ship B — Strong evidence"
        if prob_b_better > 80:
            return "Ship B — Moderate evidence"
        if prob_b_better < 20:
            return "Keep A — B is worse"
        return "Run longer — Inconclusive"
