import os
from importlib import util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
init_path = os.path.join(BASE_DIR, "secure-sms", "app", "__init__.py")

if not os.path.exists(init_path):
    raise FileNotFoundError(f"Expected Flask app at: {init_path}")

spec = util.spec_from_file_location("secure_sms_app", init_path)
module = util.module_from_spec(spec)
assert spec and spec.loader, "Unable to load app module spec"
spec.loader.exec_module(module)

# Prefer a module-level `app` if present; otherwise call `create_app()`
app = getattr(module, "app", None)
if app is None:
    factory = getattr(module, "create_app", None)
    if factory is None:
        raise RuntimeError("Neither 'app' nor 'create_app()' found in secure-sms/app/__init__.py")
    app = factory()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)\n