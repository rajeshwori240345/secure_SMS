import importlib


def test_import_app():
    mod = importlib.import_module("secure-sms.app.__init__")
    assert mod is not None
    if hasattr(mod, "app"):
        assert mod.app is not None
