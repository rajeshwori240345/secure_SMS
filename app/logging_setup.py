import os
import json
import uuid
import logging
from logging.handlers import RotatingFileHandler
from flask import has_request_context, request

try:
    from flask_login import current_user
except Exception:  # pragma: no cover
    current_user = None

class RequestContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, "request_id", None) or str(uuid.uuid4())[:8]
        if has_request_context():
            try:
                record.path = request.path
                record.method = request.method
                record.remote_addr = request.headers.get("X-Forwarded-For", request.remote_addr)
            except Exception:
                record.path = record.method = record.remote_addr = None
            try:
                if current_user and getattr(current_user, "is_authenticated", False):
                    record.user = getattr(current_user, "email", None) or getattr(current_user, "username", None)
                else:
                    record.user = None
            except Exception:
                record.user = None
        else:
            record.path = record.method = record.remote_addr = None
            record.user = None
        return True

class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "path": getattr(record, "path", None),
            "method": getattr(record, "method", None),
            "remote_addr": getattr(record, "remote_addr", None),
            "user": getattr(record, "user", None),
        }
        return json.dumps(payload, ensure_ascii=False)

def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path

def init_logging(app):
    level_name = str(app.config.get("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    to_console = str(app.config.get("LOG_TO_CONSOLE", "false")).lower() in {"1","true","yes","on"}

    # logs directory at project root
    project_root = os.path.abspath(os.path.join(app.root_path, os.pardir))
    log_dir = _ensure_dir(os.path.join(project_root, "logs"))

    ctx = RequestContextFilter()

    # App logger
    app.logger.setLevel(level)
    app_log_path = os.path.abspath(os.path.join(log_dir, "app.log"))
    app_fh = RotatingFileHandler(app_log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    app_fh.setLevel(level)
    app_fh.setFormatter(JSONFormatter())
    app_fh.addFilter(ctx)
    # avoid duplicates
    if not any(getattr(h, "baseFilename", None) == app_log_path for h in app.logger.handlers):
        app.logger.addHandler(app_fh)
    if to_console and not any(isinstance(h, logging.StreamHandler) for h in app.logger.handlers):
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(JSONFormatter())
        ch.addFilter(ctx)
        app.logger.addHandler(ch)

    # Audit logger
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(level)
    audit_path = os.path.abspath(os.path.join(log_dir, "audit.log"))
    audit_fh = RotatingFileHandler(audit_path, maxBytes=1_000_000, backupCount=10, encoding="utf-8")
    audit_fh.setLevel(level)
    audit_fh.setFormatter(JSONFormatter())
    audit_fh.addFilter(ctx)
    if not any(getattr(h, "baseFilename", None) == audit_path for h in audit_logger.handlers):
        audit_logger.addHandler(audit_fh)
    if to_console and not any(isinstance(h, logging.StreamHandler) for h in audit_logger.handlers):
        ch2 = logging.StreamHandler()
        ch2.setLevel(level)
        ch2.setFormatter(JSONFormatter())
        ch2.addFilter(ctx)
        audit_logger.addHandler(ch2)

    # attach for easy access
    app.audit_logger = audit_logger

    # Request lifecycle
    @app.before_request
    def _req_start():
        try:
            app.logger.info("REQUEST start")
        except Exception:
            pass

    @app.after_request
    def _req_end(resp):
        try:
            app.logger.info("RESPONSE end -> %s", resp.status_code)
        except Exception:
            pass
        return resp

    # Flask-Login signals (if available)
    try:
        from flask_login import user_logged_in, user_logged_out, user_login_failed
        @user_logged_in.connect_via(app)
        def _login_ok(sender, user):
            try:
                uid = getattr(user, "id", None)
                uname = getattr(user, "email", None) or getattr(user, "username", None)
                audit_logger.info(json.dumps({"event":"login_success","user":uname,"user_id":uid}, ensure_ascii=False))
            except Exception:
                audit_logger.info("login_success")
        @user_logged_out.connect_via(app)
        def _logout(sender, user):
            try:
                uid = getattr(user, "id", None)
                uname = getattr(user, "email", None) or getattr(user, "username", None)
                audit_logger.info(json.dumps({"event":"logout","user":uname,"user_id":uid}, ensure_ascii=False))
            except Exception:
                audit_logger.info("logout")
        @user_login_failed.connect_via(app)
        def _login_fail(sender, user):
            try:
                audit_logger.warning(json.dumps({"event":"login_failed","user":user}, ensure_ascii=False))
            except Exception:
                audit_logger.warning("login_failed")
    except Exception:
        pass

def audit(event: str, **kwargs):
    try:
        logging.getLogger("audit").info(json.dumps({"event": event, **kwargs}, ensure_ascii=False))
    except Exception:
        logging.getLogger("audit").info("%s %s", event, kwargs)
