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
   set FLASK_APP=run.py
   set FLASK_ENV=development
   flask run
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

## Screenshot Checklist
1. Registration page (filled example).
2. Login page (failed attempt message, then success).
3. OTP entry page + console showing OTP code.
4. Biometric simulation page (fingerprint verify button).
5. Dashboard (grade distribution chart).
6. Students list (admin view) showing decrypted addresses.
7. New/Edit Student form.
8. Teachers list and New/Edit Teacher form (admin).
9. RBAC demo: teacher trying to access admin teachers page (403).
10. Backup page + downloading encrypted backup.
11. Restore form (file chooser) + success flash.
12. Audit log snippet (logs/audit.log) with recent actions.
13. Postman screenshot: `/api/login` to get JWT, then `/api/students` with Bearer token.
14. XSS defense: a student name with `<script>` shows as text in list (no alert).

## JWT API Examples
- Login to get token:
  ```http
  POST /api/login
  Content-Type: application/json

  {"username":"admin","password":"Admin@123"}
  ```
  Response: `{"access_token":"<JWT>", "role":"admin"}`

- List students:
  ```http
  GET /api/students
  Authorization: Bearer <JWT>
  ```

- Create student:
  ```http
  POST /api/students
  Authorization: Bearer <JWT>
  Content-Type: application/json

  {"name":"Test User","email":"test.user@example.com","address":"Somewhere","grade":"A"}
  ```

## Security Practices
- Passwords hashed with bcrypt.
- CSRF protection via Flask-WTF.
- XSS mitigated via Jinja auto-escape.
- SQL injection prevented by SQLAlchemy ORM/params.
- Sensitive fields encrypted with Fernet (store key in `.env`).

## Troubleshooting
- If OTP email fails, check console for `[EMAIL DEV]` message and use that code.
- If you see `InvalidToken` on viewing student addresses, your `ENCRYPTION_KEY` changed after data was created. Regenerate DB (`python init_db.py`) or restore with the matching key.
