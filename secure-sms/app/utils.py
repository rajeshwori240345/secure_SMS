"""Utility functions and decorators for the Secure SMS application."""

from functools import wraps
from flask import abort, session, current_app
from flask_mail import Message
from . import mail


def role_required(*roles):
    """Decorator to restrict access to users with specific roles.

    When applied to a view function, the current user must be
    authenticated and their ``role`` attribute must be one of the
    supplied roles; otherwise a 401 or 403 error is raised.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask_login import current_user
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def send_email(subject: str, recipients: list[str], body: str) -> bool:
    """Send an email using Flask-Mail and log/print it for development.

    Args:
        subject: Email subject line.
        recipients: List of recipient email addresses.
        body: Plaintext body of the email.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    # Always log/print the email body to console for dev visibility
    current_app.logger.info(f"Email to {recipients}: {body}")
    print(f"[EMAIL DEV] Subject: {subject}\nTo: {recipients}\n{body}\n")
    try:
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
        return True
    except Exception as e:  # pragma: no cover - logging only
        current_app.logger.warning(f"Mail send failed: {e}")
        return False