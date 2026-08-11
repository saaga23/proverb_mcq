# PAT Rotation Checklist

This document records the current PAT exposure incident and the steps required to complete rotation.

## Incident summary

- A GitHub Personal Access Token (PAT) was previously stored in plaintext at `.env.local.token`.
- The plaintext token has been **removed** from the working tree and is now gitignored.
- Git history may still contain the token if it was committed before being added to `.gitignore`.

## Immediate actions

- [x] Remove `.env.local.token` from the working tree
- [x] Verify `.env.local.token` is listed in `.gitignore`
- [x] Scan tracked files for exposed secrets (no matches found)
- [ ] Revoke the exposed PAT on GitHub
- [ ] Generate a new fine-grained PAT with minimum required scopes
- [ ] Store the new PAT only in `.env.local.token` (gitignored) or a secrets manager
- [ ] If the old PAT was committed historically, purge it from Git history

## How to revoke the old PAT

1. Go to <https://github.com/settings/tokens>.
2. Find the token named `proverbgap-annotation-app` (or similar) and click **Delete**.
3. Confirm deletion.

## How to generate a new PAT

1. Go to <https://github.com/settings/tokens>.
2. Click **Generate new token (fine-grained)**.
3. Set a short expiration (e.g., 30 days) unless you need longer access.
4. Under **Repository access**, select only the repositories this token needs.
5. Under **Permissions**, grant only:
   - `Contents` → `Read and write` (if you need to push)
   - `Metadata` → `Read-only` (usually granted automatically)
6. Click **Generate token** and copy it immediately.
7. Store it in `.env.local.token` (gitignored).

## How to purge a token from Git history

If the old PAT was committed to the repository:

```bash
# Install git-filter-repo if needed
pip install git-filter-repo

# Rewrite history to remove the file containing the token
git filter-repo --path .env.local.token --invert-paths

# Force-push the cleaned history
git push --force --all
git push --force --tags
```

**Warning:** force-pushing rewrites history. Coordinate with any collaborators before doing this.

## Branch protection

After the PAT is rotated, enable branch protection on `main`:

1. Open the repository on GitHub.
2. Go to **Settings → Branches → Add rule**.
3. Branch name pattern: `main`
4. Enable:
   - **Require a pull request before merging**
   - **Require status checks to pass before merging**
     - Add `python-tests` and `annotation-app-lint`
   - **Require branches to be up to date before merging**
   - **Do not allow bypassing the above settings**
5. Click **Create** or **Save**.

## Prevention

- Never commit `.env*` files or tokens.
- Use a secrets manager for shared credentials.
- Enable a pre-commit hook such as `gitleaks` or `detect-secrets` to catch future leaks.
