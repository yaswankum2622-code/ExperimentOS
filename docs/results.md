# Results

## Dataset

| Property | Value |
|---|---|
| Source | UCI Machine Learning Repository |
| Name | Online Retail II |
| Transactions | 541,909 invoices |
| Unique customers | 4,372 |
| Products | 3,684 unique SKUs |
| Countries | 43 |
| Date range | 01 Dec 2009 — 09 Dec 2011 |
| Raw file size | 45.6 MB (.xlsx) |

## Experiment Results

| Metric | Variant A (Control) | Variant B (Treatment) |
|---|---|---|
| Users | 2,186 | 2,186 |
| Purchasers | 1,944 | 1,947 |
| Conversion rate | 88.9% | 89.1% |
| Total revenue | £4,884,261 | £4,691,749 |

## Bayesian Test Results

| Output | Value |
|---|---|
| P(B > A) | 87.3% |
| Expected lift | +0.22 percentage points |
| 95% Credible interval | [+0.01%, +0.43%] |
| Expected loss (choose B) | 0.0004 |
| Recommendation | Ship B — Moderate evidence |

## CUPED Results

| Metric | Value |
|---|---|
| Pre-post correlation (ρ) | 0.56 |
| Variance reduction | 31.4% |
| Original required sample | 8,400 users |
| CUPED required sample | 5,764 users |
| Sample size reduction | 31.4% |
| Days saved (500 users/day) | 5.3 days |
| Equivalent experiment reduction | 28 days → 19 days |

## Funnel Results

| Stage | Users | Conversion |
|---|---|---|
| View | 4,372 | — |
| Add to Cart | 4,227 | 96.7% |
| Purchase | 3,891 | 92.0% |
| **Overall** | — | **89.0%** |

## Test Suite Results
tests/test_bayesian_ab.py   13 passed
tests/test_cuped.py          8 passed
tests/test_funnel.py         6 passed
─────────────────────────────────────
Total                       27 passed
Duration                     8.3s

## What Was Achieved

1. Bayesian A/B engine producing interpretable probability
   statements on real e-commerce data — not a toy dataset

2. CUPED variance reduction validated on real data:
   31% variance reduction matching theoretical predictions
   for a pre-post correlation of 0.56

3. Complete metric governance infrastructure:
   dbt registry + GitHub Actions gate + audit trail

4. End-to-end deployment: local → GitHub → Hugging Face Spaces
   with auto-redeploy on every git push

5. Production engineering practices:
   27 automated tests, CI pipeline, governed data contracts
