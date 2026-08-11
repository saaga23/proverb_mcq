# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| v68.x   | Yes                |
| < v68   | No                 |

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **please do not open a public issue.**

Instead, report it privately via email to the project maintainers at the address listed in the repository profile. Include:

- A description of the vulnerability and its potential impact
- Steps to reproduce the issue
- Any relevant logs, screenshots, or payloads
- Suggested remediation, if available

We will acknowledge receipt within 5 business days and provide a detailed response within 30 days. Please do not disclose the vulnerability publicly until we have had a chance to investigate and release a patch.

## Historical API Key Exposure

### Background

Early versions of this project included OpenRouter API keys in plaintext within notebook cells and configuration files. These notebooks were pushed to Kaggle and shared publicly as part of the research workflow.

### Remediation

- All notebooks and scripts now read API keys from environment variables (`.env` files, which are git-ignored).
- Kaggle secrets (`OPENROUTER_API_KEY`) are used for remote execution.
- A `.gitignore` entry prevents `.env` files from being committed.
- Automated pre-commit checks flag any new plaintext key patterns.

### Key Rotation

If you used a shared or exposed key, you should rotate it immediately:

1. Log in to [OpenRouter](https://openrouter.ai/keys).
2. Revoke the compromised key.
3. Generate a new key and store it securely in `.env` and Kaggle Secrets.
4. Audit your OpenRouter usage for any unauthorized spend.

## Secrets in Git History

This repository previously contained plaintext API keys in the Git history. If you cloned an older version of the repository, run:

```bash
# Verify no secrets are present in your working tree
git secret --check  # if git-secret is installed
# Or scan with truffleHog / gitleaks
```

Do not share or publish forks that contain historical keys. If you have already published a fork, purge its Git history or contact GitHub Support to remove cached copies.

## Third-Party Dependencies

This project depends on third-party Python and TypeScript packages. We periodically update dependencies to address security advisories. You can audit your local install with:

```bash
# Python
pip install pip-audit
pip-audit

# Node.js
npm audit
npm audit fix
```

## Security Updates

Security patches and advisories will be documented in [SECURITY.md](SECURITY.md) and, where applicable, in [CHANGELOG.md](CHANGELOG.md). Watch the repository for notifications.
