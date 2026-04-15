# Scope

## MVP Scope — What Is Built

| Component | Description | Status |
|---|---|---|
| Data pipeline | Load UCI Online Retail II Excel → SQLite | ✅ |
| Bayesian A/B engine | Beta-Binomial conjugate model, no MCMC | ✅ |
| CUPED variance reduction | Linear covariate adjustment | ✅ |
| Cohort retention heatmap | Weekly retention by acquisition cohort | ✅ |
| Conversion funnel | 3-stage funnel with variant comparison | ✅ |
| dbt metric registry | Canonical YAML definitions + SQL models | ✅ |
| Decision memo generator | Google Gemini 1.5 Flash integration | ✅ |
| Streamlit dashboard | 5-page dark-themed interactive app | ✅ |
| pytest suite | 20 tests across 3 test files | ✅ |
| GitHub Actions CI | Test suite runs on every push | ✅ |
| Metric governance gate | Blocks unapproved metric changes | ✅ |
| Hugging Face deployment | Live public URL, free hosting | ✅ |

## Out of Scope for MVP

| Feature | Reason excluded | Where it goes |
|---|---|---|
| PostgreSQL | Zero-setup SQLite is sufficient for portfolio | Future work |
| Docker | Adds complexity without portfolio value | Future work |
| Sequential testing | Significant added complexity | docs/future_work.md |
| DoWhy causal inference | Separate project track | Future work |
| R statistical analysis | Python sufficient for all methods | Not needed |
| Power BI / Tableau | Streamlit + Plotly is portfolio-grade | Not needed |
| User authentication | Not required for demo purposes | Production only |

## Design Decisions

### Why SQLite over PostgreSQL?
SQLite is built into Python — zero setup, zero dependencies,
runs identically on every machine and on Hugging Face Spaces.
The SQL is 100% portable to PostgreSQL with no changes.

### Why Beta-Binomial conjugate over PyMC MCMC?
The Beta-Binomial conjugate model gives exact posteriors
for binary conversion metrics (converted / not converted).
MCMC sampling adds 30-60 seconds of computation per test
for no improvement in accuracy for this specific use case.
The conjugate approach runs in milliseconds.

### Why UCI Online Retail II over synthetic data?
Real data has real distribution shapes, real seasonal patterns,
real outliers, and real class imbalances that synthetic data
cannot replicate. The resulting charts and statistics are
genuinely interesting rather than artificially clean.

### Why dbt-sqlite over raw SQL?
dbt adds version control, documentation, lineage tracking,
and automated testing to SQL transforms. It mirrors
the toolchain used by Stripe, DoorDash, and Airbnb.
The dbt project structure is directly transferable to
a PostgreSQL or Snowflake backend.
