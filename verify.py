import subprocess
import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

checks = []

def ok(msg):  print(f"  ✓  {msg}"); checks.append(True)
def fail(msg): print(f"  ✗  {msg}"); checks.append(False)

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print(" ExperimentOS — End-to-End Verify")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# 1. Install packages
print("[1/6] Installing packages...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r",
     "requirements.txt", "--quiet"],
    capture_output=True
)
if result.returncode == 0: ok("All packages installed")
else: fail(f"pip install failed:\n{result.stderr.decode()}")

# 2. Check data file
print("\n[2/6] Checking data file...")
if os.path.exists("data/online_retail_II.xlsx"):
    ok("online_retail_II.xlsx found")
else:
    fail("online_retail_II.xlsx NOT found")
    print("      Download from:")
    print("      https://archive.ics.uci.edu/dataset/502/online+retail+ii")
    sys.exit(1)

# 3. Generate database
print("\n[3/6] Generating database...")
result = subprocess.run(
    [sys.executable, "data/loader.py"],
    capture_output=True, text=True
)
print("     ", result.stdout.strip())
if os.path.exists("data/events.db"): ok("events.db created")
else: fail("events.db was NOT created — check loader.py")

# 4. Test imports
print("\n[4/6] Testing imports...")
modules = [
    ("experiments.bayesian_ab",    "BayesianABTest"),
    ("experiments.cuped",          "CUPEDAnalysis"),
    ("analytics.cohort_retention", "compute_retention"),
    ("analytics.funnel_analysis",  "compute_funnel"),
    ("memo.decision_memo",         "generate_memo"),
    ("database.db",                "get_connection"),
]
for module, obj in modules:
    try:
        mod = __import__(module, fromlist=[obj])
        getattr(mod, obj)
        ok(f"{module}.{obj}")
    except Exception as e:
        fail(f"{module} — {e}")

# 5. Core logic
print("\n[5/6] Core logic verification...")
try:
    from experiments.bayesian_ab import BayesianABTest
    ab = BayesianABTest()
    r = ab.run_test(150, 1000, 180, 1000)
    assert 0 <= r["prob_treatment_better"] <= 100
    ok(f"Bayesian test — P(B>A) = {r['prob_treatment_better']:.1f}%")
except Exception as e:
    fail(f"Bayesian test failed — {e}")

try:
    from experiments.cuped import CUPEDAnalysis
    import numpy as np
    c = CUPEDAnalysis()
    pre  = np.random.normal(10, 2, 500)
    post = pre * 0.8 + np.random.normal(5, 1, 500)
    theta = c.compute_theta(pre, post)
    assert np.isfinite(theta)
    ok(f"CUPED theta = {theta:.4f}")
except Exception as e:
    fail(f"CUPED failed — {e}")

try:
    from analytics.funnel_analysis import compute_funnel
    fig, stats = compute_funnel("data/events.db")
    assert stats["viewers"] >= stats["cart_adders"] >= stats["purchasers"]
    ok(f"Funnel — {stats['viewers']:,} viewers → "
       f"{stats['purchasers']:,} purchasers "
       f"({stats['overall_conversion_rate']:.1f}% conversion)")
except Exception as e:
    fail(f"Funnel failed — {e}")

try:
    from analytics.cohort_retention import compute_retention
    fig = compute_retention("data/events.db")
    ok("Cohort retention heatmap generated")
except Exception as e:
    fail(f"Cohort retention failed — {e}")

try:
    from database.db import get_experiment_summary
    summary = get_experiment_summary()
    assert len(summary) == 2
    a = next(s for s in summary if s["variant"] == "A")
    b = next(s for s in summary if s["variant"] == "B")
    ok(f"DB summary — A: {a['conversion_rate']}% | "
       f"B: {b['conversion_rate']}%")
except Exception as e:
    fail(f"DB summary failed — {e}")

# 6. Syntax check
print("\n[6/6] Syntax check...")
result = subprocess.run(
    [sys.executable, "-m", "py_compile", "dashboard/app.py"],
    capture_output=True
)
if result.returncode == 0: ok("dashboard/app.py — no syntax errors")
else: fail(f"Syntax error in app.py:\n{result.stderr.decode()}")

# Final result
passed = sum(checks)
total  = len(checks)
print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
if all(checks):
    print(f" ALL {total} CHECKS PASSED ✓")
    print(" Run: streamlit run dashboard/app.py")
else:
    print(f" {passed}/{total} checks passed")
    print(" Fix the ✗ items above then re-run")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

if not all(checks):
    sys.exit(1)
