
import os
import json
import logging
import uuid
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request
from flask_login import current_user

class RequestContextFilter(logging.Filter):
    """Inject request-scoped fields into log records when available."""
    def filter(self, record):
        record.request_id = getattr(record, "request_id", None) or str(uuid.uuid4())[:8]
        if has_request_context():
            record.remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
            record.method = request.method
            record.path = request.path
        else:
            record.remote_addr = None
            record.method = None
            record.path = None
        try:
            uid = getattr(current_user, "id", None) if has_request_context() else None
            uname = getattr(current_user, "email", None) if has_request_context() else None
        except Exception:
            uid = None
            uname = None
        record.user_id = uid
        record.user = uname
        return True

class JSONFormatter(logging.Formatter):
    """Lightweight JSON formatter without external deps."""
    def format(self, record):
        base = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            "user": getattr(record, "user", None),
            "remote_addr": getattr(record, "remote_addr", None),
            "method": getattr(record, "method", None),
            "path": getattr(record, "path", None),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(app):
    """Configure app.logger and an audit logger with optional JSON output.",
    """
    log_dir = app.config.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Settings via env with safe defaults
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "text").lower()  # 'text' or 'json'
    max_mb = int(os.getenv("LOG_ROTATE_MB", "5"))
    backups = int(os.getenv("LOG_BACKUPS", "5"))

    # Core app logger -> logs/app.log
    app_log_path = os.path.join(log_dir, "app.log")
    app_handler = RotatingFileHandler(app_log_path, maxBytes=max_mb * 1024 * 1024, backupCount=backups, encoding="utf-8")
    ctx_filter = RequestContextFilter()
    app_handler.addFilter(ctx_filter)

    if fmt == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(request_id)s %(remote_addr)s %(method)s %(path)s %(message)s")
    app_handler.setFormatter(formatter)

    app.logger.setLevel(getattr(logging, level, logging.INFO))
    # Avoid duplicate handlers if reloaded
    if not any(isinstance(h, RotatingFileHandler) for h in app.logger.handlers):
        app.logger.addHandler(app_handler)

    # Audit logger -> logs/audit.log
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(getattr(logging, level, logging.INFO))
    audit_path = os.path.join(log_dir, "audit.log")
    audit_handler = RotatingFileHandler(audit_path, maxBytes=max_mb * 1024 * 1024, backupCount=backups, encoding="utf-8")
    audit_handler.addFilter(ctx_filter)
    audit_handler.setFormatter(formatter)
    if not any(isinstance(h, RotatingFileHandler) for h in audit_logger.handlers):
        audit_logger.addHandler(audit_handler)

    # Expose on app for convenience
    app.audit_logger = audit_logger

    # Basic request logging hooks (safe if registered twice due to unique names)
    @app.before_request
    def _log_request():
        try:
            app.logger.info("REQUEST start")
        except Exception:
            pass

    @app.after_request
    def _log_response(response):
        try:
            app.logger.info("RESPONSE end -> %s", response.status_code)
        except Exception:
            pass
        return response
