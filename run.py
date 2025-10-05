import os
import sys
from importlib import util

# Load the Flask app defined in secure-sms/app/__init__.py without relying on an importable package name
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
init_path = os.path.join(BASE_DIR, "secure-sms", "app", "__init__.py")

if not os.path.exists(init_path):
    raise FileNotFoundError(f"Expected Flask app at: {init_path}")

spec = util.spec_from_file_location("secure_sms_app", init_path)
module = util.module_from_spec(spec)
assert spec and spec.loader, "Unable to load app module spec"
spec.loader.exec_module(module)

# Expose WSGI application for tests and gunicorn
app = getattr(module, "app", None)
if app is None:
    raise RuntimeError("Flask 'app' not found in secure-sms/app/__init__.py")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
