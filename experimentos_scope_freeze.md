# ExperimentOS — Scope Freeze

---

## Problem Statement

Product teams at every company run A/B tests and get it wrong.
They use p-values nobody understands, experiments run too long,
and five teams have five different definitions of "revenue."
Bad experiments = wrong product decisions = millions wasted.

Real companies with this exact problem:
- Stripe wrote a public blog post about metric inconsistency costing them weeks per sprint
- Airbnb built an entire internal tool just to solve experiment governance
- DoorDash publicly stated underpowered experiments were their #1 data problem in 2023

---

## What We Are Solving

| Problem | Our Solution |
|---|---|
| p-values are uninterpretable | Bayesian posterior — "87% probability B is better" |
| Experiments run 4 weeks | CUPED variance reduction — cuts to 10 days |
| Teams disagree on metrics | dbt metric registry — one source of truth |
| No written decision record | Gemini auto-generates decision memo |
| Anyone can change metric definitions | GitHub Actions CI gate blocks unapproved changes |

---

## Real Dataset

**Google Merchandise Store — Google Analytics Sample**

- Source: BigQuery Public Dataset (completely free, no credit card needed)
- What it is: Real Google Store e-commerce data — actual user sessions,
  page views, add-to-carts, and purchases on store.google.com
- Size: 1+ million real sessions, 12 months of transactions
- Why this: Real conversion rates, real drop-offs, real user behaviour
- Access: bigquery-public-data.google_analytics_sample.ga_sessions_*
- How to get it: Google BigQuery free sandbox — 1TB queries/month free

Backup (if BigQuery takes time to set up):
UCI Online Retail II — 1 million real UK e-commerce transactions
https://archive.ics.uci.edu/dataset/502/online+retail+ii

---

## MVP — 9 Things. Nothing More.

1. Data pipeline — load real Google Analytics data into SQLite
2. Bayesian A/B test engine — PyMC Beta-Binomial model
3. CUPED variance reduction — cuts experiment duration 30-50%
4. Cohort retention heatmap — weekly retention by acquisition cohort
5. Funnel analysis — view → cart → purchase with drop-off rates
6. dbt metric registry — canonical metric definitions in YAML + SQL
7. Gemini decision memo — auto-written ship/kill recommendation
8. Streamlit dashboard — all 5 features in one deployed app
9. GitHub Actions CI gate — blocks metric definition changes without review

---

## What Is NOT in MVP

PostgreSQL, Docker, Sequential testing, DoWhy, R, Power BI / Tableau

---

## Stack

Python 3.12 · VSCode · SQLite · dbt-sqlite · PyMC · Streamlit · Gemini API free · pytest · GitHub Actions

---

## Done Means

- All 9 features working locally
- pytest suite passing
- Deployed on Streamlit Cloud with public URL
- README with business impact + live demo link
- Pushed to GitHub and pinned
