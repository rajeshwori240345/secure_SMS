
import os
import json
import uuid
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

from flask import request, g
from flask import has_request_context

# ---- Helpers ----

class RequestContextFilter(logging.Filter):
    """Inject request-scoped fields into log records when available."""
    def filter(self, record):
        record.request_id = getattr(g, "request_id", None)
        if has_request_context():
            record.remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
            record.method = request.method
            record.path = request.path
            try:
                # Avoid importing flask_login globally if not installed
                from flask_login import current_user
                record.user = getattr(current_user, "email", None) or getattr(current_user, "id", None)
            except Exception:
                record.user = None
        else:
            record.remote_addr = None
            record.method = None
            record.path = None
            record.user = None
        return True

class JSONFormatter(logging.Formatter):
    """Simple JSON formatter"""
    def format(self, record):
        base = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "remote_addr": getattr(record, "remote_addr", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
            "user": getattr(record, "user", None),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def _ensure_log_dir(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)

def init_logging(app):
    """
    Initializes robust logging without breaking existing handlers.
    - Adds structured JSON logs at logs/structured.jsonl
    - Adds/ensures audit logger at logs/audit.log (rotating)
    - Adds request_id on each request + response
    Config via env:
      LOG_LEVEL=INFO|DEBUG|WARNING
      LOG_JSON=true|false (json structured logs enabled anyway in structured.jsonl)
      LOG_TO_CONSOLE=true|false
    """
    log_dir = app.config.get("LOG_DIR", "logs")
    _ensure_log_dir(log_dir)

    # ---- Base levels ----
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # ---- Keep existing app.logger handlers; just add structured one ----
    app.logger.setLevel(level)

    # Request context filter to enrich records
    ctx_filter = RequestContextFilter()

    # Structured JSON file
    json_path = os.path.join(log_dir, "structured.jsonl")
    json_handler = RotatingFileHandler(json_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    json_handler.setLevel(level)
    json_handler.setFormatter(JSONFormatter())
    json_handler.addFilter(ctx_filter)
    # Avoid duplicate if already added
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", "") == os.path.abspath(json_path) for h in app.logger.handlers):
        app.logger.addHandler(json_handler)

    # Optional console
    if os.getenv("LOG_TO_CONSOLE", "false").lower() in ("1", "true", "yes"):
        console = logging.StreamHandler()
        console.setLevel(level)
        # Keep console human-readable
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(request_id)s] %(message)s"))
        console.addFilter(ctx_filter)
        app.logger.addHandler(console)

    # ---- Audit logger ----
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(level)
    audit_path = os.path.join(log_dir, "audit.log")
    audit_handler = RotatingFileHandler(audit_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    audit_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    audit_logger.addHandler(audit_handler)
    audit_logger.addFilter(ctx_filter)
    app.audit_logger = audit_logger

    # ---- Request/Response correlation ----
    @app.before_request
    def _assign_request_id():
        # Only set if not already present
        if not hasattr(g, "request_id") or g.request_id is None:
            g.request_id = str(uuid.uuid4())
        app.logger.info("REQUEST start")

    @app.after_request
    def _log_response(resp):
        try:
            app.logger.info("RESPONSE end -> %s", resp.status_code)
        except Exception:
            # Never break the response because of logging
            pass
        return resp

    @app.errorhandler(Exception)
    def _log_exception(e):
        app.logger.exception("Unhandled exception")
        # Let Flask handle rendering default error pages
        return e, getattr(e, "code", 500)

def audit(event: str, **kwargs):
    """
    Convenience function to write structured audit events, e.g.:
      audit("login_success", user=email)
      audit("student_update", student_id=123)
    """
    logger = logging.getLogger("audit")
    payload = {"event": event, **kwargs}
    try:
        logger.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        # fallback
        logger.info("%s %s", event, kwargs)
