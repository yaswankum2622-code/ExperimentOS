# Root app.py — Hugging Face Spaces entry point
import os
import subprocess
import sys


if not os.path.exists("data/events.db"):
    subprocess.run([sys.executable, "data/loader.py"])


from dashboard.app import *
