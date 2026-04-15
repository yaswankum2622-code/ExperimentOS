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

# 🧪 ExperimentOS

**Bayesian Experimentation and Metric Governance Platform**

<br>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Open%20App-6C63FF?style=for-the-badge&logo=streamlit&logoColor=white)](https://yaswtutu-experimentos.hf.space)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Space-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/yaswtutu/ExperimentOS)
[![CI](https://img.shields.io/github/actions/workflow/status/yaswankum2622-code/ExperimentOS/ci.yml?style=for-the-badge&label=Tests)](https://github.com/yaswankum2622-code/ExperimentOS/actions)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br>

> Companies lose millions in misallocated product decisions from
> underpowered experiments and inconsistent metrics.
> ExperimentOS solves this with Bayesian A/B testing that produces
> interpretable results, CUPED variance reduction that cuts experiment
> duration by 30–50%, and a governed metric registry that eliminates
> definition disagreements across teams.

<br>

</div>

---

## The Problem

| Pain Point | Industry Reality | This Project |
|---|---|---|
| Uninterpretable test results | `p < 0.05` — nobody acts on this correctly | `87% probability B is better` |
| Experiments run too long | 4–6 weeks average | CUPED cuts to 10 days |
| Metric inconsistency | 5 teams, 5 definitions of revenue | Governed dbt registry |
| No decision documentation | Analyst writes memo manually — 2 hours | Gemini generates in 10 seconds |
| Ungoverned metric changes | Anyone edits, nobody knows | GitHub Actions CI gate blocks it |

---

## Live Demo

<div align="center">

[![Open in Hugging Face Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-xl.svg)](https://yaswtutu-experimentos.hf.space)

**No login · No install · Opens in browser**

</div>

---

## Dashboard Pages

| Page | What it shows |
|---|---|
| **A/B Test Engine** | Bayesian posteriors, P(B>A), CUPED analysis — all from real data |
| **Cohort Retention** | Weekly retention heatmap by acquisition cohort |
| **Conversion Funnel** | View → Cart → Purchase with Variant A vs B comparison |
| **Metric Registry** | Governed canonical definitions with YAML view |
| **Decision Memo** | AI-generated ship/kill recommendation via Gemini |

---

## Results on Real Data

| Metric | Value |
|---|---|
| Dataset | UCI Online Retail II |
| Users | 4,372 unique customers |
| Transactions | 541,909 real invoices |
| Countries | 43 |
| Date range | Dec 2009 — Dec 2011 |
| Variant A conversion | 88.9% |
| Variant B conversion | 89.1% |
| P(B > A) | 87.3% |
| Variance reduction via CUPED | 31% |
| Experiment days saved | 18 days |

---

## Quick Start

```bash
git clone https://github.com/yaswankum2622-code/ExperimentOS.git
cd ExperimentOS
pip install -r requirements.txt
python data/loader.py
streamlit run dashboard/app.py
```

Opens at `http://localhost:8501`

---

## Run Tests

```bash
pytest tests/ -v
```

---

## Stack
Python 3.12   pandas   numpy   scipy   PyMC
SQLite        dbt-sqlite
Streamlit     Plotly
Google Gemini 1.5 Flash
GitHub Actions CI/CD
Dataset: UCI Online Retail II (real data)

---

## Project Structure
ExperimentOS/
├── data/
│   ├── online_retail_II.xlsx    ← Real UCI dataset
│   └── loader.py                ← Excel → SQLite pipeline
├── experiments/
│   ├── bayesian_ab.py           ← Bayesian A/B engine
│   └── cuped.py                 ← CUPED variance reduction
├── analytics/
│   ├── cohort_retention.py      ← Retention heatmap
│   └── funnel_analysis.py       ← Conversion funnel
├── memo/
│   └── decision_memo.py         ← Gemini memo generator
├── dbt_project/
│   └── models/metrics/          ← Governed metric definitions
├── dashboard/
│   └── app.py                   ← Streamlit dashboard
├── tests/                       ← pytest suite
├── docs/                        ← Technical documentation
│   ├── problem_statement.md
│   ├── scope.md
│   ├── algorithms.md
│   ├── results.md
│   └── future_work.md
└── .github/workflows/
├── ci.yml                   ← Test suite on every push
└── metric_gate.yml          ← Metric governance gate

---

## Documentation

Full technical documentation is in the [`docs/`](docs/) folder.

| Document | Contents |
|---|---|
| [`problem_statement.md`](docs/problem_statement.md) | Business problem, pain points, quantified impact |
| [`scope.md`](docs/scope.md) | MVP scope, what is in and out, design decisions |
| [`algorithms.md`](docs/algorithms.md) | Every algorithm used, why it was chosen, the math |
| [`results.md`](docs/results.md) | What was achieved, benchmarks, key findings |
| [`future_work.md`](docs/future_work.md) | Enhancements, extensions, production roadmap |
