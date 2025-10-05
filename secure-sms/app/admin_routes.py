"""Administrative routes for managing students, teachers and backups."""

import io
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required
from .utils import role_required
from .models import Student, Teacher
from .forms import StudentForm, TeacherForm
from . import db
from .encryption import encrypt_text, decrypt_text, get_fernet
from werkzeug.utils import secure_filename


admin_bp = Blueprint("admin", __name__)

# --- Students CRUD ---

@admin_bp.route("/students")
@login_required
@role_required("admin", "teacher")
def students_list():
    """List all students for admin/teacher roles."""
    students = Student.query.order_by(Student.id.desc()).all()
    # decrypt addresses for display
    for s in students:
        s.address_plain = decrypt_text(s.address_encrypted)
    return render_template("students_list.html", students=students)


@admin_bp.route("/students/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "teacher")
def students_new():
    """Create a new student record."""
    form = StudentForm()
    if form.validate_on_submit():
        st = Student(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            address_encrypted=encrypt_text(form.address.data.strip() if form.address.data else ""),
            grade=form.grade.data,
        )
        db.session.add(st)
        db.session.commit()
        current_app.audit_logger.info(f"Student created: {st.name} ({st.email})")
        flash("Student created.", "success")
        return redirect(url_for("admin.students_list"))
    return render_template("student_form.html", form=form, title="New Student")


@admin_bp.route("/students/<int:sid>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "teacher")
def students_edit(sid: int):
    """Edit an existing student record."""
    st = Student.query.get_or_404(sid)
    form = StudentForm(obj=st)
    if request.method == "GET":
        form.address.data = decrypt_text(st.address_encrypted)
    if form.validate_on_submit():
        st.name = form.name.data.strip()
        st.email = form.email.data.strip()
        st.address_encrypted = encrypt_text(form.address.data.strip() if form.address.data else "")
        st.grade = form.grade.data
        db.session.commit()
        current_app.audit_logger.info(f"Student updated: {st.id}")
        flash("Student updated.", "success")
        return redirect(url_for("admin.students_list"))
    return render_template("student_form.html", form=form, title=f"Edit Student #{sid}")


@admin_bp.route("/students/<int:sid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def students_delete(sid: int):
    """Delete a student record."""
    st = Student.query.get_or_404(sid)
    db.session.delete(st)
    db.session.commit()
    current_app.audit_logger.info(f"Student deleted: {sid}")
    flash("Student deleted.", "info")
    return redirect(url_for("admin.students_list"))

# --- Teachers CRUD ---

@admin_bp.route("/teachers")
@login_required
@role_required("admin")
def teachers_list():
    """List all teachers for admin role."""
    teachers = Teacher.query.order_by(Teacher.id.desc()).all()
    return render_template("teachers_list.html", teachers=teachers)


@admin_bp.route("/teachers/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def teachers_new():
    """Create a new teacher record."""
    form = TeacherForm()
    if form.validate_on_submit():
        t = Teacher(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            department=form.department.data.strip() if form.department.data else None,
        )
        db.session.add(t)
        db.session.commit()
        current_app.audit_logger.info(f"Teacher created: {t.name}")
        flash("Teacher created.", "success")
        return redirect(url_for("admin.teachers_list"))
    return render_template("teacher_form.html", form=form, title="New Teacher")


@admin_bp.route("/teachers/<int:tid>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def teachers_edit(tid: int):
    """Edit an existing teacher record."""
    t = Teacher.query.get_or_404(tid)
    form = TeacherForm(obj=t)
    if form.validate_on_submit():
        t.name = form.name.data.strip()
        t.email = form.email.data.strip()
        t.department = form.department.data.strip() if form.department.data else None
        db.session.commit()
        current_app.audit_logger.info(f"Teacher updated: {t.id}")
        flash("Teacher updated.", "success")
        return redirect(url_for("admin.teachers_list"))
    return render_template("teacher_form.html", form=form, title=f"Edit Teacher #{tid}")


@admin_bp.route("/teachers/<int:tid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def teachers_delete(tid: int):
    """Delete a teacher record."""
    t = Teacher.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    current_app.audit_logger.info(f"Teacher deleted: {tid}")
    flash("Teacher deleted.", "info")
    return redirect(url_for("admin.teachers_list"))

# --- Backup / Restore ---

@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup_page():
    """Render the backup page where an admin can download or restore backups."""
    return render_template("backup.html")


@admin_bp.route("/backup/download")
@login_required
@role_required("admin")
def backup_download():
    """Encrypt and download a backup of the SQLite database."""
    # Read sqlite file and encrypt
    db_path = "sms.db"
    if not os.path.exists(db_path):
        flash("Database not found.", "danger")
        return redirect(url_for("admin.backup_page"))
    with open(db_path, "rb") as f:
        db_bytes = f.read()
    fernet = get_fernet()
    if not fernet:
        flash("Encryption key not configured. Set ENCRYPTION_KEY in .env", "danger")
        return redirect(url_for("admin.backup_page"))
    enc = fernet.encrypt(db_bytes)
    bio = io.BytesIO(enc)
    bio.seek(0)
    current_app.audit_logger.info("Backup downloaded by admin")
    return send_file(bio, as_attachment=True, download_name="sms_backup.enc", mimetype="application/octet-stream")


@admin_bp.route("/backup/restore", methods=["POST"])
@login_required
@role_required("admin")
def backup_restore():
    """Restore the SQLite database from an encrypted backup file."""
    file = request.files.get("file")
    if not file:
        flash("No file uploaded.", "warning")
        return redirect(url_for("admin.backup_page"))
    data = file.read()
    fernet = get_fernet()
    if not fernet:
        flash("Encryption key not configured.", "danger")
        return redirect(url_for("admin.backup_page"))
    try:
        dec = fernet.decrypt(data)
    except Exception as e:
        flash(f"Failed to decrypt backup: {e}", "danger")
        return redirect(url_for("admin.backup_page"))
    # Replace sqlite file
    db_path = "sms.db"
    with open(db_path, "wb") as f:
        f.write(dec)
    current_app.audit_logger.info("Backup restored by admin")
    flash("Restore completed. Please restart the app.", "success")
    return redirect(url_for("admin.backup_page"))