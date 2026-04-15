---
title: ExperimentOS
emoji: 🧪
colorFrom: purple
colorTo: indigo
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

```
███████╗██╗  ██╗██████╗ ███████╗██████╗ ██╗███╗   ███╗███████╗███╗   ██╗████████╗ ██████╗ ███████╗
██╔════╝╚██╗██╔╝██╔══██╗██╔════╝██╔══██╗██║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗██╔════╝
█████╗   ╚███╔╝ ██████╔╝█████╗  ██████╔╝██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║███████╗
██╔══╝   ██╔██╗ ██╔═══╝ ██╔══╝  ██╔══██╗██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║╚════██║
███████╗██╔╝ ██╗██║     ███████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ╚██████╔╝███████║
╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚══════╝
```

### The experimentation platform that tells your PM *"87% chance this works"*
### instead of a p-value nobody understands

<br>

[![Live App](https://img.shields.io/badge/🚀%20Open%20Live%20App-534AB7?style=for-the-badge&logoColor=white)](https://yaswtutu-experimentos.hf.space)
[![HF Space](https://img.shields.io/badge/🤗%20Hugging%20Face-Space-FFD21E?style=for-the-badge&logoColor=black)](https://huggingface.co/spaces/yaswtutu/ExperimentOS)
[![CI Tests](https://img.shields.io/github/actions/workflow/status/yaswankum2622-code/ExperimentOS/ci.yml?style=for-the-badge&label=Tests&logo=github&logoColor=white)](https://github.com/yaswankum2622-code/ExperimentOS/actions)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-1D9E75?style=for-the-badge)](LICENSE)

<br>

![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Bayesian](https://img.shields.io/badge/Stats-Bayesian%20A%2FB-534AB7?style=flat-square)
![CUPED](https://img.shields.io/badge/Method-CUPED-1D9E75?style=flat-square)
![dbt](https://img.shields.io/badge/Data-dbt%20Metric%20Registry-FF694A?style=flat-square&logo=dbt&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![UCI](https://img.shields.io/badge/Data-UCI%20Online%20Retail%20II-orange?style=flat-square)

</div>

---

## What is this

Product teams run A/B tests wrong.

They get a p-value. They misinterpret it. The experiment runs four weeks
because variance is high. Someone changes the definition of "revenue" halfway
through. The decision memo never gets written. Three months later nobody
remembers what shipped or why.

ExperimentOS fixes the entire chain.

Built on 541,909 real UK e-commerce transactions from the UCI Online Retail II
dataset. Not a toy demo. Real data, real drop-offs, real seasonal patterns.

---

## See it live

<div align="center">

[![Open in HF Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-xl.svg)](https://yaswtutu-experimentos.hf.space)

**No login · No install · Opens in browser · Free forever**

</div>

---

## What it does

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│   INPUT: Two variants of a product change                        │
│                                                                   │
│   ┌──────────────┐     ┌───────────────┐     ┌───────────────┐  │
│   │  Bayesian    │     │    CUPED       │     │  Metric       │  │
│   │  A/B Engine  │────▶│  Variance     │────▶│  Registry     │  │
│   │              │     │  Reduction    │     │  (dbt)        │  │
│   └──────────────┘     └───────────────┘     └───────────────┘  │
│          │                     │                     │           │
│          ▼                     ▼                     ▼           │
│   "87% B is better"    "18 days saved"      "Metric locked"     │
│                                                                   │
│                    ┌──────────────────┐                          │
│                    │  Gemini Decision │                          │
│                    │  Memo Generator  │                          │
│                    └──────────────────┘                          │
│                            │                                     │
│                            ▼                                     │
│                    Plain English memo                            │
│                    written for your PM                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## The numbers on real data

| | Control A | Treatment B | Δ |
|---|---|---|---|
| Users | 9,166 | 7,750 | — |
| Conversion | 32.0% | 38.0% | **+6.0pp** |
| Revenue | £8.63M | £9.11M | **+£480K** |
| P(B is better) | — | — | **100%** |
| CUPED sample reduction | — | — | **25%** |
| Experiment days saved | — | — | **4 days** |

---

## Five pages. One platform.

<table>
<tr>
<td width="20%" align="center">

**📊 A/B Engine**

Bayesian posteriors.
Not p-values.

</td>
<td width="20%" align="center">

**🔄 Cohort Retention**

Weekly heatmap.
Who stays and who leaves.

</td>
<td width="20%" align="center">

**🔽 Conversion Funnel**

View → Cart → Purchase.
Side-by-side A vs B.

</td>
<td width="20%" align="center">

**📋 Metric Registry**

One definition.
GitHub Actions gate.

</td>
<td width="20%" align="center">

**📝 Decision Memo**

Gemini writes it.
PM reads it. Ship.

</td>
</tr>
</table>

---

## Why Bayesian

```python
# What everyone does
p_value = 0.043
# "Is this significant?" — nobody actually knows

# What ExperimentOS does
prob_b_better = 100.0%
# "100% chance B is better" — your PM can act on this
```

Frequentist tests tell you the probability of seeing this data
if there were no effect. Nobody wants that.

Bayesian posteriors tell you the probability that the treatment
actually works. That is the question your team is asking.

---

## Why CUPED

Your experiment variance is killing your velocity.

```
Standard approach:
  Required sample:  4,718 users
  At 300 users/day: 15.7 days

With CUPED:
  Adjust for pre-experiment behaviour
  theta = Cov(Y, X) / Var(X)
  Required sample:  3,536 users
  At 300 users/day: 11.8 days

Saved: 4 days. Per experiment. Every experiment.
At 20 experiments/year: 80 days of faster product decisions.
```

Used in production at Airbnb, Netflix, LinkedIn, and Spotify.

---

## Why a metric registry

When five teams have five definitions of "revenue", every
experiment produces five different answers.

ExperimentOS puts metric definitions in YAML, version-controlled
in Git, with a GitHub Actions gate that blocks any PR modifying
them without data team approval.

```yaml
- name: conversion_rate
  label: Purchase Conversion Rate
  description: Viewers who complete a purchase
  owner: data_team
  last_modified: "2026-04-15"
```

Change it without approval? The PR fails. Automatically.

---

## Quick start

```bash
git clone https://github.com/yaswankum2622-code/ExperimentOS.git
cd ExperimentOS

pip install -r requirements.txt

python data/loader.py
# Loaded 16,916 users | 541,909 invoices | 1.6M events

streamlit run dashboard/app.py
# http://localhost:8501
```

---

## Dataset

**UCI Online Retail II**
541,909 real UK e-commerce transactions
Dec 2009 — Dec 2011 · 41 countries · 3,684 unique products

[Download from UCI ML Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

Place the downloaded file as `data/online_retail_II.xlsx`

---

## Run tests

```bash
pytest tests/ -v

# test_bayesian_ab.py   13 passed
# test_cuped.py          8 passed
# test_funnel.py         6 passed
# ──────────────────────────────
# 27 passed
```

---

## Stack

```
Language     Python 3.11
Statistics   PyMC · scipy · numpy · statsmodels
Data         pandas · SQLite · dbt-sqlite
Dashboard    Streamlit · Plotly
AI           Google Gemini 1.5 Flash
CI/CD        GitHub Actions
Hosting      Hugging Face Spaces (free)
Dataset      UCI Online Retail II (real data)
```

---

## Project structure

```
ExperimentOS/
│
├── data/
│   ├── online_retail_II.xlsx    real UCI dataset
│   └── loader.py                Excel → SQLite pipeline
│
├── experiments/
│   ├── bayesian_ab.py           Bayesian A/B engine
│   └── cuped.py                 CUPED variance reduction
│
├── analytics/
│   ├── cohort_retention.py      weekly retention heatmap
│   └── funnel_analysis.py       conversion funnel
│
├── memo/
│   └── decision_memo.py         Gemini memo generator
│
├── dbt_project/
│   └── models/metrics/          governed metric definitions
│
├── dashboard/
│   └── app.py                   Streamlit dashboard
│
├── tests/                       27 pytest tests
│
├── docs/
│   ├── problem_statement.md
│   ├── scope.md
│   ├── algorithms.md
│   ├── results.md
│   └── future_work.md
│
└── .github/workflows/
    ├── ci.yml                   tests on every push
    └── metric_gate.yml          blocks unapproved metric changes
```

---

## Documentation

| File | What is in it |
|---|---|
| [`docs/problem_statement.md`](docs/problem_statement.md) | The business problem and why it costs millions |
| [`docs/scope.md`](docs/scope.md) | What is in MVP, what is out, why |
| [`docs/algorithms.md`](docs/algorithms.md) | The math behind every method |
| [`docs/results.md`](docs/results.md) | What the real data produced |
| [`docs/future_work.md`](docs/future_work.md) | What comes next |

---

## What is next

- Sequential testing with O'Brien-Fleming early stopping
- DoWhy causal inference for experiment validation
- PostgreSQL + Docker for production teams
- Multi-metric guardrail monitoring
- Slack integration for experiment result notifications

All documented in [`docs/future_work.md`](docs/future_work.md)

---

<div align="center">

**Built by Yashwanth**
M.Tech CSE · Business Analytics · VIT Chennai · Bengaluru

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/YOUR_LINKEDIN)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat&logo=github&logoColor=white)](https://github.com/yaswankum2622-code)

<br>

*If this helped you — star the repo.*

⭐

</div>
