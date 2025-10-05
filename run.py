from importlib import util
import os
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INIT_PATH = os.path.join(BASE_DIR, "secure-sms", "app", "__init__.py")

if not os.path.exists(INIT_PATH):
    raise FileNotFoundError(f"Expected Flask app source here: {INIT_PATH}")

spec = util.spec_from_file_location("secure_sms_app", INIT_PATH)
module: Any = util.module_from_spec(spec)
assert spec and spec.loader, "Unable to load app module spec for secure_sms_app"
spec.loader.exec_module(module)  # type: ignore[attr-defined]

# Prefer module-level `app`; otherwise construct via `create_app()`
app = getattr(module, "app", None)
if app is None:
    factory = getattr(module, "create_app", None)
    if callable(factory):
        # Make tests hermetic
        os.environ.setdefault("FLASK_ENV", "testing")
        os.environ.setdefault("TESTING", "1")
        # Use in-memory SQLite by default to avoid file/permission errors
        os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")
        os.environ.setdefault("MAIL_SUPPRESS_SEND", "1")
        os.environ.setdefault("WTF_CSRF_ENABLED", "0")
        app = factory()
    else:
        raise RuntimeError("Neither 'app' nor 'create_app()' found in secure-sms/app/__init__.py")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
