# Secure Student Management System (Flask)

A secure Student Management System built with Flask for local Windows development.

## Features
- Registration, Login, Logout
- **2FA via Email OTP** (also always printed in console)
- **Simulated Biometric Step** after OTP
- **RBAC** (admin, teacher, student)
- **CRUD** for Students (admin/teacher) and Teachers (admin)
- **AES encryption (Fernet)** for sensitive fields (student address)
- **JWT API** for programmatic access (`/api/login`, `/api/students` GET/POST)
- **Audit Logging** to `logs/audit.log`
- **Analytics Dashboard** (grade distribution with Chart.js)
- **Encrypted Backup/Restore** of SQLite DB
- **Sample Data** (admin/teacher/student users + students/teachers)

## Quick Start (Windows)
1. **Install Python 3.8+** and git (optional).
2. Unzip this project, open terminal here.
3. Create venv and install deps:
   ```bat
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Configure environment:
   - Copy `.env.example` to `.env` and fill values.
   - Generate `ENCRYPTION_KEY`:
     ```bat
     python generate_key.py
     ```
     Copy output into `.env` as `ENCRYPTION_KEY=...`
   - (Optional) Set SMTP settings for email OTP in `.env`. If not set, OTP still prints to console.
5. Initialize database with sample data:
   ```bat
   python init_db.py
   ```
6. Run the app:
   ```bat
   python run.py
   ```
   Open http://127.0.0.1:5000

**Sample accounts**
- Admin: `admin / Admin@123`
- Teacher: `teacher1 / Teacher@123`
- Student: `student1 / Student@123`

## Notes
- **Avoid "cryptography.fernet.InvalidToken"**: Ensure `ENCRYPTION_KEY` is set **before** running `init_db.py` or creating any encrypted data. If you change the key later, previously encrypted fields/backups cannot be decrypted.
- OTP emails are attempted via Flask-Mail and **always logged/printed** to console for dev.
- After restore, **restart** the app so SQLAlchemy picks up the new DB.

## Security Practices
- Passwords hashed with bcrypt.
- CSRF protection via Flask-WTF.
- XSS mitigated via Jinja auto-escape.
- SQL injection prevented by SQLAlchemy ORM/params.
- Sensitive fields encrypted with Fernet (store key in `.env`).

## Troubleshooting
- If OTP email fails, check console for `[EMAIL DEV]` message and use that code.
- If you see `InvalidToken` on viewing student addresses, your `ENCRYPTION_KEY` changed after data was created. Regenerate DB (`python init_db.py`) or restore with the matching key.
