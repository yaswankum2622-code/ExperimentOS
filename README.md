---
title: ExperimentOS
emoji: 🧪
colorFrom: indigo
colorTo: blue
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: false
license: mit
---

# ExperimentOS

ExperimentOS is a Bayesian experimentation platform for product teams. It loads the Online Retail II dataset, simulates funnel events, runs Bayesian A/B testing, applies CUPED variance reduction, visualizes retention and funnel metrics, and generates plain-English decision memos.

## Run Locally

```bash
python verify.py
streamlit run dashboard/app.py
```

## Hugging Face Spaces

The root `app.py` is the Spaces entry point. It generates `data/events.db` from `data/online_retail_II.xlsx` if the SQLite database is missing, then launches the Streamlit dashboard.
