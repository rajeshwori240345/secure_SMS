import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()

# --- Flask-Login user loader & unauthorized handler ---
@login_manager.user_loader
def load_user(user_id):
    # Import here to avoid circular imports
    try:
        from .models import User
        return db.session.get(User, int(user_id))
    except Exception:
        return None

@login_manager.unauthorized_handler
def _unauthorized():
    # Lazy import to avoid circular references
    from flask import redirect, url_for, flash
    flash("Please log in to continue.", "warning")
    return redirect(url_for("auth.login"))

bcrypt = Bcrypt()
mail = Mail()
jwt = JWTManager()

def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)

    # Core config
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-key"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///sms.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        LOG_TO_CONSOLE=os.getenv("LOG_TO_CONSOLE", "false"),
        MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", "25")),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "false").lower() in {"1","true","yes","on"},
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    )

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # Blueprints
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .main_routes import main_bp
    from .api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Configure login_manager
    login_manager.login_view = "auth.login"

    # Logging (after app object exists)
    try:
        from .logging_setup import init_logging
        init_logging(app)
    except Exception:
        # Never block startup due to logging
        pass

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app
