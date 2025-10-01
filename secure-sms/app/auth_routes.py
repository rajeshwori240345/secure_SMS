import secrets, time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegisterForm, OTPForm
from .models import User
from . import db
from .utils import send_email

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter((User.username==form.username.data)|(User.email==form.email.data)).first():
            flash("Username or email already exists.", "danger")
            return render_template("register.html", form=form)
        user = User(username=form.username.data.strip(), email=form.email.data.strip(), role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        current_app.audit_logger.info(f'User registered: {user.username} ({user.role})')
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            # Stage 1 OK - put in session and ask OTP
            session["preauth_user_id"] = user.id
            # Generate OTP
            code = f"{secrets.randbelow(10**6):06d}"
            session["otp_code"] = code
            session["otp_expires"] = (datetime.utcnow() + timedelta(minutes=5)).timestamp()
            # Send email (and always print)
            send_email("Your Secure SMS OTP Code", [user.email], f"Your OTP code is: {code}\nIt expires in 5 minutes.")
            current_app.audit_logger.info(f'OTP code issued for user {user.username}')
            flash("An OTP code has been sent to your email (also printed to console).", "info")
            return redirect(url_for("auth.otp"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)

@auth_bp.route("/otp", methods=["GET","POST"])
def otp():
    if "preauth_user_id" not in session:
        return redirect(url_for("auth.login"))
    form = OTPForm()
    if form.validate_on_submit():
        code = form.code.data.strip()
        real = session.get("otp_code")
        exp = session.get("otp_expires", 0)
        if real and str(code) == str(real) and datetime.utcnow().timestamp() <= exp:
            # All good -> log the user in and go to biometric
            user = User.query.get(session["preauth_user_id"])
            login_user(user)
            session.pop("otp_code", None)
            session.pop("otp_expires", None)
            session["2fa_ok"] = True
            current_app.audit_logger.info(f'2FA success for user {user.username}')
            return redirect(url_for("auth.biometric"))
        else:
            current_app.audit_logger.warning(f'2FA failure for preauth user id {session.get("preauth_user_id")}')
            flash("Invalid or expired code. Please try again.", "danger")
    return render_template("otp.html", form=form)

@auth_bp.route("/biometric", methods=["GET","POST"])
@login_required
def biometric():
    # Simulated biometric verification step
    if not session.get("2fa_ok"):
        return redirect(url_for("auth.login"))
    # On POST, mark biometric passed
    if request.method == "POST":
        session["bio_ok"] = True
        current_app.audit_logger.info(f'Biometric simulated OK for user {current_user.username}')
        return redirect(url_for("main.dashboard"))
    return render_template("biometric.html")

@auth_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    current_app.audit_logger.info(f'User logged out: {username}')
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
