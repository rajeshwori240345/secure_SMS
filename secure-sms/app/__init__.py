"""Flask application factory and extension initialization.

This module defines the ``create_app`` function used to construct
and configure the Flask application.  It initializes extensions
(SQLAlchemy, Flask-Login, Bcrypt, Mail, JWT) and registers
blueprints for the various parts of the Secure SMS application.  It
also configures logging and creates the SQLite database on startup.
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Instantiate extensions without an app.  They will be initialized
# with the application instance in ``create_app``.
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
jwt = JWTManager()


def _ensure_log_dir(app: Flask) -> None:
    """Ensure the log directory and audit log file exist and set up logging.

    Creates a ``logs`` directory (or the value of ``LOG_DIR`` in
    ``app.config``) if it doesn't exist and prepares a file handler
    for the audit logger.  Attaches the logger to ``app.audit_logger``.
    """
    log_dir = app.config.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    audit_path = os.path.join(log_dir, "audit.log")
    # Touch the file if it doesn't exist
    if not os.path.exists(audit_path):
        open(audit_path, "a").close()
    # Configure a logger for audit events
    logger = logging.getLogger("audit")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(audit_path, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    # Expose the audit logger via the Flask app for easy access
    app.audit_logger = logger


def create_app() -> Flask:
    """Application factory for the Secure SMS Flask project.

    Loads environment variables, configures the Flask app and all
    extensions, registers blueprints and ensures the database exists.

    Returns:
        Configured Flask application instance.
    """
    # Load environment variables from a .env file if present
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Core configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sms.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_dev_key")
    app.config["LOG_DIR"] = "logs"

    # Mail configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "localhost")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "25"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    default_sender = os.getenv("MAIL_DEFAULT_SENDER")
    if default_sender:
        app.config["MAIL_DEFAULT_SENDER"] = default_sender

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # Import models so that they are registered with SQLAlchemy before
    # creating tables.  Otherwise SQLAlchemy may not know about them.
    from .models import User  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        """Flask-Login user loader callback.

        Args:
            user_id: The primary key of the user to load.

        Returns:
            The ``User`` instance corresponding to ``user_id`` or ``None``.
        """
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    # Prepare the audit logger and log directory
    _ensure_log_dir(app)

    # Register blueprints
    from .auth_routes import auth_bp
    from .main_routes import main_bp
    from .admin_routes import admin_bp
    from .api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app