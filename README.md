# secure_SMS

## CI/CD

This repo includes GitHub Actions workflows:

- **CI (Lint & Test)**: runs Ruff and Pytest on every push/PR.
- **CodeQL**: static analysis for security issues.
- **Build Docker Image**: builds and publishes a container image to GHCR when pushing to `main`/`master`.
- **SonarCloud** *(optional)*: runs coverage and sends analysis to SonarCloud if `SONAR_TOKEN` is configured.

### Quick start
1. Go to **Settings → Actions → General** and ensure Actions are enabled.
2. (Optional) Create **SonarCloud** secret: `SONAR_TOKEN`.
3. Push changes. See workflow runs under the **Actions** tab.
