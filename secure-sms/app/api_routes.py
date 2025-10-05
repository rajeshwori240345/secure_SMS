from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
import hmac
from .models import User, Student, Teacher
from . import db
from .encryption import decrypt_text

api_bp = Blueprint("api", __name__)

@api_bp.post("/login")
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username","").strip()
    password = data.get("password","")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        token = create_access_token(identity=user.id, additional_claims={"role": user.role, "username": user.username})
        return jsonify(access_token=token, role=user.role), 200
    return jsonify(msg="Invalid credentials"), 401

def role_required_api(*roles):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in roles:
                return jsonify(msg="Forbidden"), 403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

@api_bp.get("/students")
@jwt_required()
@role_required_api("admin","teacher")
def api_students():
    out = []
    for s in Student.query.all():
        out.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "address": decrypt_text(s.address_encrypted),
            "grade": s.grade
        })
    return jsonify(out), 200

@api_bp.post("/students")
@jwt_required()
@role_required_api("admin","teacher")
def api_students_create():
    data = request.get_json(silent=True) or {}
    s = Student(name=data.get("name","").strip(), email=data.get("email","").strip(), grade=data.get("grade"))
    from .encryption import encrypt_text
    s.address_encrypted = encrypt_text(data.get("address",""))
    db.session.add(s)
    db.session.commit()
    return jsonify(msg="created", id=s.id), 201
