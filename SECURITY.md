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

## Key Rotation Guide

This project uses several third-party services. If a key or token is compromised, rotate it immediately using the instructions below.

### OpenRouter API Key

OpenRouter is used for LLM generation and audit. The key is stored in `.env` locally and as a Kaggle Secret remotely.

**How to rotate:**

1. Log in to [openrouter.ai/keys](https://openrouter.ai/keys).
2. Find the compromised key and click **Revoke**.
3. Click **Create Key** and give it a descriptive name (e.g., `proverbgap-pipeline-v68`).
4. Copy the new key value.
5. Update locally:
   ```bash
   # Open .env in your editor
   OPENROUTER_API_KEY=new-key-here
   ```
6. Update on Kaggle:
   - Go to your Kaggle notebook → **Settings → Secrets**.
   - Edit `OPENROUTER_API_KEY` and paste the new value.
7. (Optional) Set a spending limit on OpenRouter to prevent unexpected charges.

**Prevention:** Never hard-code keys in notebooks or scripts. Always use environment variables or Kaggle Secrets.

### Supabase Keys

Supabase hosts the annotation database. There are two keys:

| Key | Where it's used | Exposure risk |
|-----|-----------------|---------------|
| `anon` key | Browser/client-side | Public by design (protected by RLS) |
| `service_role` key | Server-side scripts, admin API | **Secret** — bypasses all RLS |

**How to rotate `service_role` key:**

1. Log in to [supabase.com/dashboard](https://supabase.com/dashboard).
2. Select your project → **Project Settings → API**.
3. Under **service_role key**, click **Reset**.
4. Copy the new key.
5. Update locally:
   ```bash
   # Edit annotation_app/.env.local
   SUPABASE_SERVICE_ROLE_KEY=new-key-here
   ```
6. Update production (Vercel):
   - Go to Vercel dashboard → Your project → **Settings → Environment Variables**.
   - Update `SUPABASE_SERVICE_ROLE_KEY`.

**How to rotate `anon` key:**

1. Same steps as above, but click **Reset** next to the `anon public` key.
2. Update `NEXT_PUBLIC_SUPABASE_ANON_KEY` in all environments (local `.env.local`, Vercel, etc.).
3. The `anon` key is exposed to the browser, so rotating it is less urgent but still good hygiene.

**Prevention:** The `service_role` key should never be exposed to the browser. Verify that no client-side code references `SUPABASE_SERVICE_ROLE_KEY`.

### Vercel Tokens

Vercel is used to deploy the annotation app.

| Token/Secret | Where it's used |
|--------------|-----------------|
| Vercel API token | CI/CD, CLI deploys (`vercel` command) |
| Vercel environment variables | `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `ADMIN_PASSWORD` |

**How to rotate Vercel API token:**

1. Log in to [vercel.com/account/tokens](https://vercel.com/account/tokens).
2. Find the token and click **Revoke**.
3. Click **Create Token**, give it a name, and select the appropriate scope (usually full account access for a personal token).
4. Copy the new token and update any CI/CD secrets or local `~/.vercel` config.

**How to rotate environment variables in Vercel:**

1. Go to your Vercel project → **Settings → Environment Variables**.
2. Edit each variable and paste the new value.
3. Redeploy the project to apply changes.

**Prevention:** Use Vercel's team-level environment variable management instead of personal tokens when collaborating.

### GitHub Tokens

GitHub is used for repository hosting, CI/CD, and Kaggle notebook sync.

| Token/Secret | Where it's used |
|--------------|-----------------|
| GitHub Personal Access Token (PAT) | Git operations, CI/CD, API access |
| GitHub Actions secrets | Workflows that push to Kaggle, upload artifacts |

**How to rotate GitHub PAT:**

1. Log in to [github.com/settings/tokens](https://github.com/settings/tokens).
2. Find the token and click **Delete**.
3. Click **Generate new token (classic)** or **Generate new token (fine-grained)**.
4. Select the minimum required scopes:
   - `repo` (for private repos) or `public_repo` (for public repos)
   - `workflow` (if using GitHub Actions)
5. Copy the new token and update any local Git config or CI secrets.

**How to rotate GitHub Actions secrets:**

1. Go to your repository → **Settings → Secrets and variables → Actions**.
2. Click the secret name, then **Update secret**.
3. Paste the new value.

**Prevention:** Use fine-grained tokens with the minimum required permissions. Set an expiration date.

---

## What to Do If a Key Is Accidentally Committed

If you accidentally commit a key or secret to the repository:

### Immediate actions

1. **Rotate the key immediately.** Even if the repo is private, treat it as compromised.
2. **Remove the key from the code.**
   ```bash
   # Edit the file to remove the key
   git add <file>
   git commit -m "chore: remove accidentally committed API key"
   ```
3. **Force-push if the commit is the most recent:**
   ```bash
   git push --force
   ```
4. **If the key was committed in an earlier commit, purge Git history:**
   ```bash
   # Install git-filter-repo if you don't have it
   pip install git-filter-repo

   # Rewrite history to remove the key
   git filter-repo --path <file-with-key> --invert-paths
   git push --force --all
   ```

### Additional steps

- **Audit usage:** Check the service provider's dashboard for any unauthorized activity (e.g., unusual API calls on OpenRouter).
- **Notify collaborators:** If others have cloned the repo, ask them to re-clone or run `git pull --rebase`.
- **GitHub cache:** If the repo is public, GitHub may have cached the file. Contact GitHub Support to request cache purge.

### Prevention

- Add the file to `.gitignore` if not already there.
- Enable pre-commit hooks that scan for secrets (e.g., `pre-commit` with `detect-secrets` or `gitleaks`).
- Use a secrets manager (e.g., `git-secret`, `sops`, or environment variable injection) for sensitive configuration.

---

## Secrets in Git History

This repository previously contained plaintext API keys in the Git history. If you cloned an older version of the repository, run:

```bash
# Verify no secrets are present in your working tree
git secret --check  # if git-secret is installed
# Or scan with truffleHog / gitleaks
gitleaks detect --source .
```

Do not share or publish forks that contain historical keys. If you have already published a fork, purge its Git history or contact GitHub Support to remove cached copies.

---

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

---

## Security Updates

Security patches and advisories will be documented in [SECURITY.md](SECURITY.md) and, where applicable, in [CHANGELOG.md](CHANGELOG.md). Watch the repository for notifications.
