import os

from dotenv import load_dotenv


MODEL_NAME = "gemini-2.5-flash-lite"


def generate_memo(experiment_results: dict) -> str:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_key_here":
        return fallback_memo(experiment_results)

    control_rate = experiment_results["control_rate"]
    treatment_rate = experiment_results["treatment_rate"]
    prob = experiment_results["prob_treatment_better"]
    lift = experiment_results["expected_lift_pct"]
    ci_low = experiment_results.get("ci_low", 0.0)
    ci_high = experiment_results.get("ci_high", 0.0)
    recommendation = experiment_results["recommendation"]
    n_a = experiment_results["control_n"]
    n_b = experiment_results["treatment_n"]

    prompt = f"""
    You are a senior data scientist writing a decision memo
    for a non-technical product team.

    A/B Test Results:
    - Control (A) conversion rate: {control_rate:.2%}
    - Treatment (B) conversion rate: {treatment_rate:.2%}
    - Probability B is better than A: {prob:.1f}%
    - Expected lift: {lift:+.1f}%
    - 95% credible interval: [{ci_low:+.1f}%, {ci_high:+.1f}%]
    - Sample sizes: {n_a:,} control | {n_b:,} treatment
    - Statistical recommendation: {recommendation}

    Write exactly 3 short paragraphs:
    1. What we tested (1-2 sentences, plain English)
    2. What we found (use the numbers above, no jargon)
    3. Decision and next steps (clear action)

    Maximum 200 words total. No bullet points. No markdown headers.
    """

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        if not response.text:
            return fallback_memo(experiment_results)
        return response.text.strip()
    except Exception:
        return fallback_memo(experiment_results)


def fallback_memo(results: dict) -> str:
    control_rate = results["control_rate"]
    treatment_rate = results["treatment_rate"]
    prob = results["prob_treatment_better"]
    lift = results["expected_lift_pct"]
    ci_low = results.get("ci_low", 0.0)
    ci_high = results.get("ci_high", 0.0)
    recommendation = results["recommendation"]
    n_a = results["control_n"]
    n_b = results["treatment_n"]

    return (
        "We tested whether variant B improves conversion compared with the current "
        "variant A experience. The analysis compares users assigned to each version "
        f"across {n_a:,} control users and {n_b:,} treatment users.\n\n"
        f"Control converted at {control_rate:.2%}, while treatment converted at "
        f"{treatment_rate:.2%}. The probability that B is better than A is "
        f"{prob:.1f}%, with an expected lift of {lift:+.1f}% and a 95% credible "
        f"interval from {ci_low:+.1f}% to {ci_high:+.1f}%.\n\n"
        f"The recommended decision is: {recommendation}. Use this result to decide "
        "whether to ship B now, keep A, or continue the experiment until the evidence "
        "is strong enough for a product decision."
    )
