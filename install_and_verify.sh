#!/bin/bash

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ExperimentOS — Install and Verify"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1 — Install all packages
echo "[ 1/6 ] Installing packages..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
  echo "       ✗ Package installation failed"
  exit 1
fi
echo "       ✓ Packages installed"
echo ""

# Step 2 — Verify data file exists
echo "[ 2/6 ] Checking data file..."
if [ -f "data/online_retail_II.xlsx" ]; then
  echo "       ✓ online_retail_II.xlsx found"
else
  echo "       ✗ ERROR: data/online_retail_II.xlsx not found"
  echo "         Download from: https://archive.ics.uci.edu/dataset/502/online+retail+ii"
  exit 1
fi
echo ""

# Step 3 — Generate SQLite database
echo "[ 3/6 ] Generating database..."
python data/loader.py
if [ -f "data/events.db" ]; then
  echo "       ✓ events.db created successfully"
else
  echo "       ✗ ERROR: events.db was not created"
  exit 1
fi
echo ""

# Step 4 — Verify all Python modules import correctly
echo "[ 4/6 ] Verifying module imports..."
python -c "
import sys
errors = []

modules = [
    ('experiments.bayesian_ab',    'BayesianABTest'),
    ('experiments.cuped',          'CUPEDAnalysis'),
    ('analytics.cohort_retention', 'compute_retention'),
    ('analytics.funnel_analysis',  'compute_funnel'),
    ('memo.decision_memo',         'generate_memo'),
    ('database.db',                'get_connection'),
]

for module, obj in modules:
    try:
        mod = __import__(module, fromlist=[obj])
        getattr(mod, obj)
        print(f'       ✓ {module}.{obj}')
    except Exception as e:
        print(f'       ✗ {module}: {e}')
        errors.append(module)

if errors:
    print(f'\n       FAILED: {len(errors)} import(s) failed')
    sys.exit(1)
else:
    print(f'\n       All imports successful')
"
echo ""

# Step 5 — Run core logic verification
echo "[ 5/6 ] Running core logic checks..."
python -c "
import sys, os
sys.path.insert(0, os.getcwd())

# Test 1: Bayesian A/B
from experiments.bayesian_ab import BayesianABTest
ab = BayesianABTest()
result = ab.run_test(150, 1000, 180, 1000)
assert 0 <= result['prob_treatment_better'] <= 100, 'Probability out of range'
assert isinstance(result['recommendation'], str), 'Recommendation not a string'
print('       ✓ BayesianABTest.run_test() — OK')

# Test 2: CUPED
from experiments.cuped import CUPEDAnalysis
import numpy as np
cuped = CUPEDAnalysis()
pre  = np.random.normal(10, 2, 500)
post = pre * 0.8 + np.random.normal(5, 1, 500)
theta = cuped.compute_theta(pre, post)
assert np.isfinite(theta), 'Theta is not finite'
print('       ✓ CUPEDAnalysis.compute_theta() — OK')

# Test 3: Funnel from real DB
from analytics.funnel_analysis import compute_funnel
fig, stats = compute_funnel('data/events.db')
assert stats['viewers'] >= stats['cart_adders'] >= stats['purchasers']
print('       ✓ compute_funnel() — OK')

# Test 4: Cohort retention
from analytics.cohort_retention import compute_retention
fig = compute_retention('data/events.db')
assert fig is not None
print('       ✓ compute_retention() — OK')

# Test 5: DB connection
from database.db import get_connection, get_experiment_summary
summary = get_experiment_summary()
assert len(summary) == 2, 'Should have 2 variants'
print('       ✓ get_experiment_summary() — OK (2 variants found)')

print('')
print('       All core logic checks passed')
"
echo ""

# Step 6 — Streamlit syntax check
echo "[ 6/6 ] Checking Streamlit app syntax..."
python -m py_compile dashboard/app.py
if [ $? -eq 0 ]; then
  echo "       ✓ dashboard/app.py — No syntax errors"
else
  echo "       ✗ dashboard/app.py has syntax errors"
  exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ALL CHECKS PASSED"
echo " Run: streamlit run dashboard/app.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
