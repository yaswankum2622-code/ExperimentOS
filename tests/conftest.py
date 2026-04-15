import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to path so all imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def pytest_configure(config):
    """Print ExperimentOS test header"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(" ExperimentOS — Test Suite")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    except UnicodeEncodeError:
        print("\n------------------------------------")
        print(" ExperimentOS - Test Suite")
        print("------------------------------------")
