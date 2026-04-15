# Algorithms and Models

## 1. Bayesian A/B Testing — Beta-Binomial Conjugate Model

### What it does
Given observed conversion counts for two variants,
computes the full posterior distribution over each
variant's true conversion rate and derives the
probability that the treatment is better.

### The math

**Prior:**
α_prior = β_prior = 1   (Beta(1,1) — uninformative uniform prior)

**Likelihood:**
Conversions ~ Binomial(n, p)

**Posterior update (conjugate — exact, no sampling needed):**
α_posterior = α_prior + conversions
β_posterior = β_prior + (trials - conversions)
Posterior A ~ Beta(1 + conv_A, 1 + n_A - conv_A)
Posterior B ~ Beta(1 + conv_B, 1 + n_B - conv_B)

**Probability B is better:**
```python
samples_A = np.random.beta(alpha_A, beta_A, 100_000)
samples_B = np.random.beta(alpha_B, beta_B, 100_000)
P(B > A)  = np.mean(samples_B > samples_A)
```

**Expected loss:**
Loss(choose B) = E[max(p_A - p_B, 0)]
Loss(choose A) = E[max(p_B - p_A, 0)]

### Why this over alternatives

| Alternative | Why not used |
|---|---|
| Two-sample t-test | Assumes normality, outputs uninterpretable p-value |
| Chi-square test | Binary pass/fail, no probability statement |
| PyMC NUTS sampler | 30-60 seconds per test, no accuracy gain for binary metrics |
| Bootstrap | Computationally heavier, same result for large samples |

### Output interpretation
P(B > A) = 87.3%   →  "87% probability B has higher conversion"
Lift      = +0.22%  →  "Expected 0.22 percentage point improvement"
CI        = [+0.01%, +0.43%]  →  "True effect almost certainly positive"

---

## 2. CUPED — Controlled-experiment Using Pre-Experiment Data

### What it does
Reduces the variance of the experiment metric by removing
the component of variance explained by pre-experiment
user behaviour. Lower variance → smaller required sample
size → shorter experiment duration.

### The math

**Covariate adjustment:**
Y_cuped = Y - θ × (X - E[X])
Where:
Y = post-experiment metric (what we are measuring)
X = pre-experiment metric (same user, before experiment)
θ = Cov(Y, X) / Var(X)   ← optimal regression coefficient

**Variance reduction:**
Var(Y_cuped) = Var(Y) × (1 - ρ²)
Where ρ = correlation between pre and post metric.
If ρ = 0.56, variance is reduced by 1 - 0.56² = 31%

**Required sample size reduction:**
n_cuped   = n_original × (1 - ρ²)
n_original = 8,400 users
n_cuped    = 8,400 × 0.69 = 5,796 users
Days saved = (8,400 - 5,796) / 500 users/day = 5.2 days

### Why CUPED over alternatives

| Alternative | Why not used |
|---|---|
| Stratified sampling | Requires pre-stratification before experiment starts |
| ANCOVA | More complex, similar results for large samples |
| Regression adjustment | CUPED is a special case optimised for experiments |
| Just run longer | Wastes 18+ days and delays product decisions |

---

## 3. Cohort Retention Analysis — Cohort Matrix

### What it does
Segments users by their acquisition week (first purchase date)
and tracks what percentage of each cohort is still active
(making purchases) in each subsequent week.

### Method
Acquisition cohort = week of user's first purchase event
Active in week N   = user has at least 1 purchase in that week
Retention[cohort_w, week_n] =
users_active_in_week_n / users_acquired_in_cohort_w × 100

### Why this method
Non-parametric. No distributional assumptions.
Standard industry method used by Amplitude, Mixpanel,
and every product analytics platform.

---

## 4. Conversion Funnel — Sequential Stage Analysis

### What it does
Measures the percentage of users who progress through
each stage of the purchase journey and where they drop off.

### Method
Stage 1 — View:        COUNT DISTINCT users with view event
Stage 2 — Add to Cart: COUNT DISTINCT users with add_to_cart event
Stage 3 — Purchase:    COUNT DISTINCT users with purchase event
Conversion rates:
View → Cart:     Stage2 / Stage1 × 100
Cart → Purchase: Stage3 / Stage2 × 100
Overall:         Stage3 / Stage1 × 100

---

## 5. Gemini 1.5 Flash — Decision Memo Generation

### What it does
Takes structured experiment results as input and generates
a plain-English decision memo written for non-technical
product managers.

### Why Gemini 1.5 Flash
- Free tier with no credit card required
- 1 million token context window
- Fast response time (2-4 seconds)
- Sufficient quality for structured document generation

### Prompt strategy
Structured inputs (numbers, rates, recommendation)
are injected into a fixed template prompt that specifies:
- Output format (3 paragraphs)
- Audience (non-technical product manager)
- Length constraint (under 200 words)
- Required elements (what was tested, what was found, decision)

This constrained prompting produces consistent,
professional output across different experiment results.

---

## 6. dbt Metric Registry — SQL Semantic Layer

### What it does
Defines canonical metric calculations in YAML and SQL,
version-controlled in Git, with automated data quality tests.

### Why dbt over raw SQL views
Raw SQL view:  Anyone can change it, no review, no history
dbt model:     Version controlled, tested, documented, lineage tracked

dbt adds:
- `not_null` and `unique` tests on key columns
- Column-level documentation
- DAG lineage showing metric dependencies
- GitHub Actions gate blocking unapproved changes
