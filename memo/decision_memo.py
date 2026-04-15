def generate_memo(experiment_results: dict) -> str:
    import os

    import google.generativeai as genai
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_memo(experiment_results)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prob = experiment_results.get("prob_treatment_better", 50)
        lift = experiment_results.get("expected_lift_pct", 0)
        ctrl_rate = experiment_results.get("control_rate", 0)
        trt_rate = experiment_results.get("treatment_rate", 0)
        rec = experiment_results.get("recommendation", "Inconclusive")
        n_ctrl = experiment_results.get("control_n", 0)
        n_trt = experiment_results.get("treatment_n", 0)
        ci_low = experiment_results.get("ci_low", 0)
        ci_high = experiment_results.get("ci_high", 0)
        total_users = n_ctrl + n_trt

        if prob > 90:
            confidence_context = (
                f"The evidence is strong. With {prob:.1f}% probability "
                f"that B outperforms A, this crosses the 90% threshold "
                f"we use for shipping decisions."
            )
            action_context = "recommend shipping Variant B immediately"
        elif prob > 80:
            confidence_context = (
                f"The evidence is moderately strong at {prob:.1f}% probability. "
                f"This crosses our 80% threshold for a shipping decision, "
                f"though the team should monitor the guardrail metrics closely "
                f"in the first week after rollout."
            )
            action_context = "recommend shipping Variant B with close monitoring"
        elif prob > 60:
            confidence_context = (
                f"At {prob:.1f}% probability, the signal exists but is not "
                f"strong enough to act on confidently. The 95% credible interval "
                f"still includes near-zero effects, meaning the true lift "
                f"could be minimal."
            )
            action_context = "recommend extending the experiment by 1-2 weeks"
        else:
            confidence_context = (
                f"At {prob:.1f}% probability, this is statistically "
                f"indistinguishable from a coin flip. There is no meaningful "
                f"evidence that either variant is better."
            )
            action_context = (
                "recommend running the experiment longer or revisiting the hypothesis"
            )

        prompt = f"""
You are a senior data scientist at a product company writing a
formal experiment decision memo. Write this memo for the product
team and stakeholders — people who understand business impact
but not necessarily statistical theory.

EXPERIMENT DATA:
- Total users in experiment: {total_users:,}
  ({n_ctrl:,} control, {n_trt:,} treatment)
- Control (A) conversion rate: {ctrl_rate:.2%}
- Treatment (B) conversion rate: {trt_rate:.2%}
- Observed lift: {lift:+.2f} percentage points
- 95% Bayesian credible interval: [{ci_low:+.1f}pp, {ci_high:+.1f}pp]
- Probability B outperforms A: {prob:.1f}%
- Statistical recommendation: {rec}
- Confidence context: {confidence_context}
- Recommended action: {action_context}

MEMO REQUIREMENTS:
Write a proper decision memo with these exact 5 sections.
Each section must be substantive — minimum 3-4 sentences each.
Use the actual numbers throughout. Do not be generic.

---

**Experiment Summary**

What we tested, how many users were involved, and how long the
data covers. Mention the actual user counts and the conversion
metric we were measuring.

**Results**

The specific numbers — control rate, treatment rate, the lift in
percentage points, and what the credible interval means in plain
English. Explain what {prob:.1f}% probability means to someone
who has never heard of Bayesian statistics.

**Statistical Interpretation**

What the 95% credible interval of [{ci_low:+.1f}pp, {ci_high:+.1f}pp]
actually tells us about the range of true effect sizes.
Explain the difference between what we observed ({lift:+.2f}pp)
and what the true effect could be. Be honest about uncertainty.

**Business Impact Assessment**

If the lift of {lift:+.2f}pp holds at full rollout, what does
that mean for the business? Translate the conversion rate
difference into something concrete. If the experiment was
inconclusive, explain what business risk that creates.

**Decision and Next Steps**

Based on {prob:.1f}% probability and the credible interval,
state the recommendation clearly: {rec}.
Give 2-3 specific next steps with enough detail that a PM
can act on them tomorrow morning.

---

TONE: Direct and professional. Write like a real analyst,
not a chatbot. Use "we" throughout. No bullet points anywhere.
No markdown headers with # symbols — use bold text with ** only.
Each section should flow into the next naturally.
Minimum total length: 400 words.
"""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1200,
                top_p=0.9,
            ),
        )

        memo = response.text.strip()
        header = (
            f"EXPERIMENT DECISION MEMO\n"
            f"{'─' * 40}\n"
            f"Generated: {__import__('datetime').date.today()}\n"
            f"Dataset: UCI Online Retail II\n"
            f"Platform: ExperimentOS v1.0\n"
            f"{'─' * 40}\n\n"
        )

        return header + memo

    except Exception:
        return fallback_memo(experiment_results)


def fallback_memo(results: dict) -> str:
    """
    Returns a detailed fallback memo when Gemini API is unavailable.
    Uses actual experiment numbers — never generic placeholder text.
    """
    prob = results.get("prob_treatment_better", 50)
    lift = results.get("expected_lift_pct", 0)
    ctrl_rate = results.get("control_rate", 0)
    trt_rate = results.get("treatment_rate", 0)
    rec = results.get("recommendation", "Inconclusive")
    n_ctrl = results.get("control_n", 0)
    n_trt = results.get("treatment_n", 0)
    ci_low = results.get("ci_low", 0)
    ci_high = results.get("ci_high", 0)
    today = __import__("datetime").date.today()

    if prob > 80:
        decision_text = (
            f"Based on {prob:.1f}% probability that Treatment B outperforms "
            f"Control A, we have sufficient evidence to ship. The observed "
            f"{lift:+.2f}pp improvement in conversion rate represents a "
            f"meaningful business impact that justifies full rollout."
        )
        next_steps = (
            f"We recommend shipping Variant B to 100% of users. "
            f"Set up monitoring dashboards to track conversion rate and "
            f"revenue per user for the first 14 days post-launch. "
            f"Schedule a retrospective in 30 days to confirm the lift "
            f"sustained at full traffic."
        )
    else:
        decision_text = (
            f"With only {prob:.1f}% probability that B outperforms A, "
            f"we do not have sufficient evidence to make a shipping "
            f"decision. The {lift:+.2f}pp observed lift falls within "
            f"a credible interval of [{ci_low:+.1f}pp, {ci_high:+.1f}pp], "
            f"meaning the true effect could be near zero."
        )
        next_steps = (
            f"We recommend extending the experiment by 14 days to collect "
            f"more data. Alternatively, revisit the hypothesis — if the "
            f"treatment change was too subtle to move conversion meaningfully, "
            f"a bolder intervention may be needed. Do not ship based on "
            f"current evidence."
        )

    interval_text = (
        "does not include zero, which supports a real positive effect."
        if ci_low > 0
        else "includes zero, meaning we cannot rule out that there is no real effect."
    )
    impact_text = (
        f"A {lift:+.2f}pp improvement in conversion rate, sustained at full "
        f"traffic, translates directly to higher revenue per marketing pound "
        f"spent. Every 1pp improvement in conversion at this scale means "
        f"meaningfully more completed purchases without any additional "
        f"acquisition cost."
        if lift > 0
        else "The near-zero lift suggests this particular intervention did not "
        "move the needle on purchase behaviour. The business cost of shipping "
        "an ineffective change is low, but the opportunity cost of not finding "
        "a genuinely effective change is high."
    )

    return f"""EXPERIMENT DECISION MEMO
{'─' * 40}
Generated: {today}
Dataset: UCI Online Retail II
Platform: ExperimentOS v1.0
{'─' * 40}

**Experiment Summary**

We ran a controlled experiment across {n_ctrl + n_trt:,} users split
between Control A ({n_ctrl:,} users) and Treatment B ({n_trt:,} users).
The primary success metric was purchase conversion rate — the percentage
of users who completed at least one purchase during the experiment window.
The data comes from the UCI Online Retail II dataset covering real UK
e-commerce transactions. We are using this conversion metric because it is
the cleanest decision metric for this workflow: the user either purchased
or did not purchase, and that outcome can be compared directly across the
two variants without relying on subjective engagement proxies.

**Results**

Control A achieved a conversion rate of {ctrl_rate:.2%}. Treatment B
achieved {trt_rate:.2%}. The observed difference is {lift:+.2f} percentage
points in favour of {'Treatment B' if lift > 0 else 'Control A'}.
Our Bayesian model puts the probability that B is genuinely better
at {prob:.1f}% — meaning if we ran this experiment 100 times, we
would expect B to win approximately {prob:.0f} of them. That probability
is more useful for the product team than a p-value because it answers the
actual launch question: how likely is it that the treatment is better than
the current experience?

**Statistical Interpretation**

The 95% Bayesian credible interval for the true lift is
[{ci_low:+.1f}pp, {ci_high:+.1f}pp]. This means the actual effect,
if it exists, is most likely somewhere in that range. The interval
{interval_text} We observed {lift:+.2f}pp in this sample, but at scale
the true effect could be anywhere within the credible bounds above.
That distinction matters because the observed lift is only one estimate
from one sample of users. The interval gives us the range of effects we
should plan around when deciding whether the upside is worth the rollout
risk.

**Business Impact Assessment**

{impact_text}
For the business, the main value is that the conversion gain comes from
existing traffic rather than additional acquisition spend. If this result
holds after rollout, the same marketing budget and product surface would
produce more completed purchases. We should still monitor revenue per user
and refund-sensitive metrics because a conversion lift is only valuable if
it does not come from lower-quality orders or downstream churn.

**Decision and Next Steps**

{decision_text} {next_steps} The owner for this rollout should publish
the decision, update the experiment log, and make sure the metric registry
continues to define conversion consistently for future comparisons. We
should also keep this experiment as a reference case because it shows how
Bayesian decision thresholds, credible intervals, and governed metrics work
together in a real product decision.
"""
