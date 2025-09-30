# Secure Student Management System (DevSecOps-Driven)

This repository hosts the Secure Student Management System (SMS) developed with a DevSecOps mindset.
Security is integrated from day one via CI/CD, automated checks, and clear security requirements.

## Project Goals
- Build a web-based SMS using Flask with strong built-in security
- Adopt DevSecOps: shift-left, automation, continuous testing, monitoring
- Deliver a clean CI/CD pipeline that scales as features are added

## Initial Security Requirements (will evolve)
- Use version control with protected branches and PR reviews
- No secrets in code; use environment variables and CI secrets
- Enforce secure defaults (later): CSRF protection, secure cookies, TLS, headers
- Plan for SAST/DAST, dependency scanning, and secret scanning in CI/CD

## Iteration Plan (high-level)
1. **(This commit)** Repo bootstrap + CI skeleton
2. Threat model & requirements docs
3. CI: lint + test scaffold
4. CI: SAST
5. CI: secret scanning
6. CI: dependency/SCA scanning
7. Tests + PR review gates
8. Staging deploy + DAST
9. Monitoring & audit logging
10. Full Flask app integration & release

## Local Dev (placeholder)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m flask --app app.app run
```

## Status
- CI pipeline skeleton is in place and runs on every push/PR.
- App code is a *placeholder only*. Full features land in the final iteration.


## Documentation
- See `docs/threat-model.md` for identified assets, threats, and mitigations.
- See `docs/security-requirements.md` for detailed functional and security requirements.


## CI: Linting & Test Scaffold (Iteration 3)
- Uses **flake8** for lint checks
- Uses **pytest** for tests
- Sample test covers the `/health` endpoint
Run locally:
```bash
pip install -r requirements.txt -r requirements-dev.txt
flake8
pytest -q
```


## SAST with Sonar (Iteration 4)
- Adds `sonar-project.properties` and a `sast-sonar` job in CI.
- Configure **SonarCloud** (recommended for simplicity):
  1. Create a project in SonarCloud and note the `projectKey` and `organization`.
  2. Set **Repository Secret** `SONAR_TOKEN` (from SonarCloud) in GitHub → Settings → Secrets → Actions.
  3. Edit `sonar-project.properties` with your `projectKey` & `organization`.
- On each push/PR, CI runs lint+tests. If `SONAR_TOKEN` is set, SAST runs and waits for the quality gate.


## Secret Scanning (Iteration 5)
- Adds **TruffleHog** to CI to detect leaked secrets (API keys, tokens) in repo/history.
- The job fails if verified secrets are found. Remove/rotate any flagged credentials and re-push.
- Tip: Keep secrets in environment variables or GitHub Actions Secrets—never in code.


## Dependency Vulnerability Scanning (Iteration 6)
- Adds **pip-audit** job (`sca-deps`) to CI to detect known CVEs in Python dependencies.
- Fails the job if high/critical vulnerabilities are found.
- Adds **Dependabot** (`.github/dependabot.yml`) to auto-open PRs for outdated/vulnerable packages.


## Tests & PR Review Gates (Iteration 7)
- Adds **CODEOWNERS** to enforce reviews from designated teams/users.
- Recommended repo settings (GitHub → Settings → Branches → Branch protection rules):
  - Require pull request reviews before merging (at least 1–2 reviewers)
  - Require status checks to pass (CI jobs: lint, tests, SAST, secrets, SCA)
  - Require branches up to date before merging
- The pipeline already fails on lint/test errors; SAST/secrets/SCA also gate merges.
