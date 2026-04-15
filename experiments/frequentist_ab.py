"""
Frequentist A/B test using chi-square test.
Used as comparison baseline alongside Bayesian results.
"""

import numpy as np
from scipy import stats


class FrequentistABTest:
    """Chi-square test for conversion rate comparison."""

    def run_test(
        self,
        control_conversions: int,
        control_n: int,
        treatment_conversions: int,
        treatment_n: int,
    ) -> dict:
        """
        Run chi-square test on two conversion rate variants.
        Returns p-value, relative lift, and interpretation.
        """
        control_non = control_n - control_conversions
        treatment_non = treatment_n - treatment_conversions

        contingency = np.array(
            [
                [control_conversions, control_non],
                [treatment_conversions, treatment_non],
            ]
        )

        chi2, p_value, dof, _ = stats.chi2_contingency(contingency)

        control_rate = control_conversions / control_n
        treatment_rate = treatment_conversions / treatment_n
        relative_lift = (treatment_rate - control_rate) / control_rate * 100

        if p_value < 0.01:
            significance = "Highly significant (p < 0.01)"
        elif p_value < 0.05:
            significance = "Significant (p < 0.05)"
        elif p_value < 0.10:
            significance = "Marginal (p < 0.10)"
        else:
            significance = "Not significant (p >= 0.10)"

        return {
            "p_value": round(float(p_value), 6),
            "chi2_statistic": round(float(chi2), 4),
            "degrees_of_freedom": int(dof),
            "control_rate": round(control_rate, 6),
            "treatment_rate": round(treatment_rate, 6),
            "relative_lift_pct": round(relative_lift, 2),
            "significance": significance,
            "reject_null": bool(p_value < 0.05),
        }
