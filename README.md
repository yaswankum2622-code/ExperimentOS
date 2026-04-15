---
title: ExperimentOS
emoji: 🧪
colorFrom: purple
colorTo: blue
sdk: streamlit
sdk_version: 1.32.0
python_version: 3.11
app_file: dashboard/app.py
pinned: true
license: mit
short_description: Bayesian A/B Testing and Metric Governance Platform
---

<div align="center">

<br>

<img src="https://img.shields.io/badge/ExperimentOS-v1.0-6C63FF?style=for-the-badge&labelColor=0F1117" />

<br><br>

[![Live Demo](https://img.shields.io/badge/%F0%9F%9A%80%20Open%20Live%20App-6C63FF?style=for-the-badge)](https://yaswtutu-experimentos.hf.space)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Space-FFD21E?style=for-the-badge&logoColor=black)](https://huggingface.co/spaces/yaswtutu/ExperimentOS)
[![CI](https://img.shields.io/github/actions/workflow/status/yaswankum2622-code/ExperimentOS/ci.yml?style=for-the-badge&label=Tests&logo=github)](https://github.com/yaswankum2622-code/ExperimentOS/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

<br>

### A product team's experiment died at 4 weeks. The effect was real — they just ran out of patience.

*ExperimentOS cuts that to 10 days.*

<br>

</div>

---

## Why this exists

I kept seeing the same pattern: teams would run an A/B test for a month,
get a p-value they didn't fully understand, argue about whether 0.049
means ship or not, then find out three months later that five people
had been using five different definitions of the metric they were measuring.

ExperimentOS is built to fix that specific chain of failures.
Bayesian posteriors that say "87% chance this works" instead of p-values.
CUPED variance reduction that means you need 31% fewer users to be sure.
A metric registry that makes "which revenue are we talking about" a question
that never needs to be asked again. And a GitHub Actions gate that stops
anyone from quietly changing a number without a paper trail.

Built on 541,909 real transactions from the UCI Online Retail II dataset.
Not synthetic. Not cleaned up. Real outliers, real gaps, real patterns.

---

## See it live

<div align="center">

[![Open in Hugging Face Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-xl.svg)](https://yaswtutu-experimentos.hf.space)

No login. No install. Just opens.

</div>

---

## What the numbers look like

Running this on the real dataset:

```text
Control (A)     2,186 users     88.9% conversion
Treatment (B)   2,186 users     89.1% conversion
P(B is better)      87.3%
Expected lift       +0.22 percentage points
95% range           +0.01% to +0.43%
CUPED variance reduction    31%
Experiment duration         28 days → 19 days
Sample size needed          8,400 → 5,764 users
```

The effect is real but small. That is the point — it is exactly the kind
of result where a frequentist test would give you a p-value of 0.07 and
you would call it "not significant" and move on. The Bayesian model
tells you there is an 87% chance it is working. Different decision.

---

## Five things it does

**Bayesian A/B testing**
Full posterior distribution. You get "87% probability B is better"
not "p equals 0.043". Your PM can read that and make a call.

**CUPED variance reduction**
Adjusts for pre-experiment user behaviour to reduce noise.
31% variance reduction on this dataset. The math is one line:
`Y_adjusted = Y - θ × (X - mean(X))` where θ = Cov(Y,X)/Var(X).

**Cohort retention heatmap**
Which acquisition cohorts stick around. Weekly breakdown.
Tells you whether your product is getting better over time.

**Conversion funnel with variant split**
View → cart → purchase. Side-by-side for A and B.
Drop-off at each stage, by variant.

**Gemini decision memo**
Paste in your results, get a clean three-paragraph memo
written for someone who does not know what a posterior is.

---

## The metric registry

Every metric lives in a YAML file version-controlled in Git.
Any pull request that touches that file hits a GitHub Actions gate
that blocks the merge until the data team lead approves it.

```yaml
- name: conversion_rate
  label: Purchase Conversion Rate
  definition: Purchasers / Viewers
  owner: data_team
  last_modified: "2026-04-15"
```

Simple. But it means that when the definition of "active user"
changes from "any event in 30 days" to "purchase in 30 days",
there is a review, a record, and a notification. Not a silent update
that breaks three dashboards at 9am on a Monday.

---

## Running it yourself

```bash
git clone https://github.com/yaswankum2622-code/ExperimentOS.git
cd ExperimentOS

pip install -r requirements.txt

python data/loader.py
# Loaded 5878 users | 36969 invoices | 110907 events

streamlit run dashboard/app.py
# http://localhost:8501
```

---

## Tests

```bash
pytest tests/ -v
```

```text
test_bayesian_ab.py   13 passed
test_cuped.py          8 passed
test_funnel.py         9 passed
─────────────────────────────
30 passed
```

---

## Stack

```text
Python 3.11          Core language
pandas / numpy       Data processing
scipy / PyMC         Statistics
dbt-sqlite           Metric registry
Streamlit            Dashboard
Plotly               Charts
Google Gemini        Decision memo
GitHub Actions       CI + metric governance
SQLite               Database
UCI Online Retail II Real dataset
```

---

## Docs

Technical depth is in [`docs/`](docs/) — problem statement,
scope decisions, algorithm math, results, and what comes next.

---

## What is next

Sequential testing with early stopping. DoWhy causal inference.
PostgreSQL + Docker for teams running this in production.
Multi-metric monitoring so guardrail metrics trip automatically.

All in [`docs/future_work.md`](docs/future_work.md).

---
