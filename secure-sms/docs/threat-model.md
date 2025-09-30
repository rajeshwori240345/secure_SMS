# Threat Model (Initial)

## Scope & Assets
- **Assets:** Student PII (names, emails, grades), credentials, session tokens, audit logs, backups.
- **Components:** Flask web app, database, CI/CD pipeline, GitHub repo.

## Actors
- External attacker (unauthenticated)
- Authenticated user (Student/Teacher/Admin)
- Malicious insider
- Automated bot/scanner

## Assumptions
- HTTPS will be enforced in production
- Database not exposed publicly
- Secrets managed via environment/CI secrets

## STRIDE Analysis (Highlights)
- **Spoofing:** Credential stuffing → Mitigate with strong hashing (bcrypt), 2FA, rate limiting
- **Tampering:** SQL injection → Use ORM/parameterized queries; input validation
- **Repudiation:** Lack of audit logs → Implement structured audit logging
- **Information Disclosure:** XSS, misconfig → Output encoding, CSP, secure headers
- **Denial of Service:** Brute-force, resource exhaustion → Lockouts, basic rate limiting
- **Elevation of Privilege:** Broken access control → RBAC, deny-by-default on routes

## High-Level Data Flows
1. User → Web App (login, CRUD) → DB
2. CI/CD → Build/Test/Scan → Staging Deploy → DAST
3. Logs → Aggregation (future) → Alerting (future)

## Risks (Initial)
- R1: Secret leakage in repo → Secret scanning in CI, .env in .gitignore
- R2: Vulnerable dependencies → SCA in CI (pip-audit/Safety/OWASP DC)
- R3: Missing security headers → Add HSTS/CSP later; verify via ZAP
- R4: Weak auth → Enforce bcrypt, 2FA, lockout policy
