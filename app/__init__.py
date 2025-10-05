import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import logging
from .logging_config import setup_logging

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
jwt = JWTManager()

def _ensure_log_dir(app):
    log_dir = app.config.get("LOG_DIR", "logs")
    os.makedirs(log_dir, exist_ok=True)
    audit_path = os.path.join(log_dir, "audit.log")
    if not os.path.exists(audit_path):
        open(audit_path, "a").close()
    # basic logging setup
    logger = logging.getLogger("audit")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(audit_path, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    app.audit_logger = logger

def create_app():
    load_dotenv()
    # Centralized logging
    setup_logging(app)
    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sms.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_dev_key")
    app.config["LOG_DIR"] = "logs"

    # Mail config
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "localhost")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "25"))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    default_sender = os.getenv("MAIL_DEFAULT_SENDER")
    if default_sender:
        app.config["MAIL_DEFAULT_SENDER"] = default_sender

    # init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    login_manager.login_view = "auth.login"

    _ensure_log_dir(app)

    # blueprints
    from .auth_routes import auth_bp
    from .main_routes import main_bp
    from .admin_routes import admin_bp
    from .api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # create db
    with app.app_context():
        db.create_all()

        # ---- Enhanced logging (non-intrusive) ----
    try:
        from .logging_setup import init_logging
        init_logging(app)
    except Exception as e:
        # Do not fail app startup if logging init has issues
        pass

    return app
