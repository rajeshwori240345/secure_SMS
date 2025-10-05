"""Database models for the Secure SMS application.

This module defines the SQLAlchemy models used throughout the
application: ``User``, ``Student`` and ``Teacher``.  Each model
provides the fields necessary for user authentication and CRUD
operations on students and teachers.  Passwords are stored using
bcrypt hashes.
"""

from datetime import datetime
from flask_login import UserMixin
from . import db, bcrypt


class User(db.Model, UserMixin):
    """User model for authentication and authorization.

    Attributes:
        id: Primary key.
        username: Unique username for login.
        email: Unique email address.
        password_hash: Bcrypt-hashed password.
        role: Role of the user (e.g. ``student``, ``teacher``, ``admin``).
        created_at: Timestamp of account creation.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")  # 'admin', 'teacher', 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash and store a plaintext password.

        Args:
            password: The plaintext password provided by the user.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Check a plaintext password against the stored hash.

        Args:
            password: Plaintext password to verify.

        Returns:
            True if ``password`` matches the stored hash, else False.
        """
        from flask_bcrypt import check_password_hash as _check
        return _check(self.password_hash, password)


class Student(db.Model):
    """Student model representing a student record."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address_encrypted = db.Column(db.LargeBinary, nullable=True)
    grade = db.Column(db.String(2), nullable=True)  # e.g. A, B, C, D, F
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Teacher(db.Model):
    """Teacher model representing a teacher record."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)