"""API routes providing JSON endpoints secured by JWT.

These routes allow programmatic access to login and CRUD operations on
students.  They use ``flask_jwt_extended`` for authentication and
check user roles in the JWT claims.  Only admins and teachers may
list or create students via the API.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from .models import User, Student
from . import db
from .encryption import decrypt_text, encrypt_text


api_bp = Blueprint("api", __name__)


@api_bp.post("/login")
def api_login():
    """Authenticate via API and return a JWT token."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role, "username": user.username},
        )
        return jsonify(access_token=token, role=user.role), 200
    return jsonify(msg="Invalid credentials"), 401


def role_required_api(*roles):
    """Decorator to restrict API access to users with specified roles."""

    def decorator(fn):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify(msg="Forbidden"), 403
            return fn(*args, **kwargs)

        # Preserve original function name for Flask routing
        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator


@api_bp.get("/students")
@jwt_required()
@role_required_api("admin", "teacher")
def api_students():
    """Return a list of all students (admin/teacher only)."""
    out = []
    for s in Student.query.all():
        out.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "address": decrypt_text(s.address_encrypted),
            "grade": s.grade,
        })
    return jsonify(out), 200


@api_bp.post("/students")
@jwt_required()
@role_required_api("admin", "teacher")
def api_students_create():
    """Create a new student via API (admin/teacher only)."""
    data = request.get_json(silent=True) or {}
    s = Student(
        name=data.get("name", "").strip(),
        email=data.get("email", "").strip(),
        grade=data.get("grade"),
    )
    s.address_encrypted = encrypt_text(data.get("address", ""))
    db.session.add(s)
    db.session.commit()
    return jsonify(msg="created", id=s.id), 201