"""Routes for the main dashboard and index."""

from collections import Counter
from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required
from .models import Student


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Redirect the root path to the login page."""
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Render a dashboard showing grade distribution.

    Access is restricted to authenticated users who have completed
    biometric verification (see ``auth_routes.biometric``).  The
    grade distribution is computed from all students in the database.
    """
    # Require biometric completion
    if not session.get("bio_ok"):
        return redirect(url_for("auth.biometric"))
    # Compute grade distribution
    grades = [s.grade for s in Student.query.all() if s.grade]
    counts = Counter(grades)
    labels = ["A", "B", "C", "D", "F"]
    data = [counts.get(k, 0) for k in labels]
    return render_template("dashboard.html", labels=labels, data=data)