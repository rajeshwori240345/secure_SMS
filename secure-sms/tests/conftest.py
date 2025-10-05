from pathlib import Path
import sys


# Ensure repository root is importable so 'from run import app' works
# __file__ -> secure-sms/tests/conftest.py
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
