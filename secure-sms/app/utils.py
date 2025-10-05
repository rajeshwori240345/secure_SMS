from functools import wraps
from flask import abort, session, current_app
from flask_mail import Message
from . import mail

def role_required(*roles):
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

def send_email(subject, recipients, body):
    # Always log/print the email body to console for dev visibility
    current_app.logger.info(f"Email to {recipients}: {body}")
    print(f"[EMAIL DEV] Subject: {subject}\nTo: {recipients}\n{body}\n")
    try:
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.warning(f"Mail send failed: {e}")
        return False
