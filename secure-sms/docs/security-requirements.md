# Security & Functional Requirements (Initial)

## Functional
- CRUD for students (admin), view for students/teachers
- Authentication and sessions
- Role-based access control (Admin/Teacher/Student)

## Security
- Passwords hashed (bcrypt); no plaintext credentials
- 2FA (TOTP) for Admin (mandatory), optional for others
- CSRF protection on state-changing requests
- Input validation & output encoding (prevent XSS)
- ORM/parameterized queries only (prevent SQLi)
- Secure cookies (HttpOnly, SameSite, Secure in prod)
- Audit logging for auth and admin actions
- Secrets via env/CI secrets; never in VCS
- Dependency and image scanning in CI
- SAST (static code analysis) and DAST (dynamic scan) in CI
- Branch protection with PR reviews before merge to main

## Non-Functional
- Availability target for demo/staging
- Basic rate limiting on auth endpoints
- Backups (encrypted) and documented restore
