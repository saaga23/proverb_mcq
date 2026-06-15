# Kaggle Secrets Setup Guide — ProverbGap

## What Was Wrong

Your previous Kaggle run **only found 1 valid API key** out of 4 attempted:

```
[INIT] Loaded 4 API keys for rotation
[KEY] Key 1: VALID
[KEY] Key 2: INVALID (401) — removing from rotation
[KEY] Key 3: INVALID (401) — removing from rotation
[KEY] Key 4: INVALID (401) — removing from rotation
[INIT] 1 valid keys after validation
```

**Root cause:** The old notebook code only tried to load **ONE** Kaggle Secret named `GROQ_API_KEY`. If you stored multiple keys as separate secrets (e.g. `GROQ_KEY_1`, `GROQ_KEY_2`), the code never saw them.

With only **1 valid key** handling ~1,050 API calls on a shared Kaggle IP, Groq throttled aggressively → **63% failure rate**.

---

## What I Fixed

### New Multi-Secret Loader
The notebook now probes for secrets with **multiple naming patterns**:

| Secret Name | Purpose |
|---|---|
| `GROQ_API_KEY_1` | First key |
| `GROQ_API_KEY_2` | Second key |
| `GROQ_API_KEY_3` | Third key |
| … | … |
| `GROQ_API_KEY_10` | Tenth key |
| `GROQ_API_KEY` | Fallback single key (or comma-separated list) |

**Features:**
- ✅ Loads **all** matching secrets, not just one
- ✅ Supports **comma-separated** values in a single secret
- ✅ Shows **verbose logs** so you can see exactly what loaded
- ✅ Validates each key at startup and reports 401s
- ✅ Deduplicates automatically

---

## Step-by-Step: Add Your 7 Keys to Kaggle

### Step 1 — Open the Secrets Panel
In your Kaggle notebook, click:
```
Add-ons → Secrets
```
A sidebar will open on the right.

### Step 2 — Add Each Key as a Separate Secret
For **each** Groq API key, click **"Add Secret"** and fill in:

| Label | Value |
|---|---|
| `GROQ_API_KEY_1` | Paste your 1st Groq key here |
| `GROQ_API_KEY_2` | Paste your 2nd Groq key here |
| `GROQ_API_KEY_3` | Paste your 3rd Groq key here |
| `GROQ_API_KEY_4` | Paste your 4th Groq key here |
| `GROQ_API_KEY_5` | Paste your 5th Groq key here |
| `GROQ_API_KEY_6` | Paste your 6th Groq key here |
| `GROQ_API_KEY_7` | Paste your 7th Groq key here |

**Critical:** After adding each secret, toggle the **"Trusted"** switch to **ON** (green). Untrusted secrets are invisible to notebooks.

### Alternative: One Comma-Separated Secret
If you prefer, you can paste all 7 keys into **ONE** secret:
- **Label:** `GROQ_API_KEY`
- **Value:** `key1,key2,key3,key4,key5,key6,key7`

But separate secrets are **recommended** — easier to manage and replace individually.

---

## Step 3 — Run the Diagnostic First

Before running the full pipeline, **run the diagnostic script** to verify your secrets are accessible.

Upload `kaggle_secrets_diagnostic.py` to your Kaggle notebook and run:

```python
%run kaggle_secrets_diagnostic.py
```

### Expected Output (Good)
```
[KAGGLE] GROQ_API_KEY_1: loaded
[KAGGLE] GROQ_API_KEY_2: loaded
[KAGGLE] GROQ_API_KEY_3: loaded
...
[SUMMARY] Unique valid keys: 7
[RESULT] 7/7 keys passed validation
🎉 You have enough valid keys to run the full 3-model benchmark!
```

### Expected Output (Bad)
```
[IMPORT] ❌ Cannot import kaggle_secrets
...
⚠️  NO KEYS FOUND
```
**Fix:** Go back to Step 2 and double-check the secret names and Trusted toggle.

---

## Step 4 — Run the Full Pipeline

Once the diagnostic shows **≥3 valid keys**, run the main notebook cell:

```python
# This will now print something like:
[INIT] Loading API keys...
    [KAGGLE] GROQ_API_KEY_1: loaded
    [KAGGLE] GROQ_API_KEY_2: loaded
    [KAGGLE] GROQ_API_KEY_3: loaded
    ...
    [HARDCODED] 3 fallback keys
[INIT] 10 unique key(s) loaded before validation
    [KEY] Key 1 (gsk_vBp3...jIW): ✅ VALID
    [KEY] Key 2 (gsk_Y1y3...C6q): ❌ INVALID (401) — removed
    ...
[INIT] 7 valid keys after validation
```

With **7 valid keys** and a **5s base delay**:
- 900 eval calls ÷ 7 keys ≈ **129 calls per key**
- At 5s delay = **12 calls/min per key**
- Groq limit: **30 RPM** per key
- **You are well under the rate limit.** ✅

---

## Updated Files

| File | What Changed |
|---|---|
| `kaggle_full_pipeline_notebook.py` | New multi-secret loader, better validation logging |
| `kaggle_full_pipeline_notebook.ipynb` | Same update in notebook format |
| `kaggle_secrets_diagnostic.py` | **NEW** — run this first to test your secrets |
| `tomorrow_resume/` | Backup copies of all updated files |

---

## Quick Checklist Before Your Next Kaggle Run

- [ ] Added `GROQ_API_KEY_1` through `GROQ_API_KEY_7` in Kaggle Secrets
- [ ] Toggled **Trusted = ON** for every secret
- [ ] Ran `kaggle_secrets_diagnostic.py` and saw ≥3 valid keys
- [ ] Uploaded the **new** `kaggle_full_pipeline_notebook.ipynb`
- [ ] Set notebook timeout to **≥4 hours** (Kaggle defaults to 9h for GPU, 12h for CPU)

---

## If It Still Doesn't Work

**Problem: Diagnostic says "kaggle_secrets not available"**
→ You are not running inside a Kaggle notebook session. Upload the file and run it there.

**Problem: Keys load but all fail validation (401)**
→ Your Groq keys are expired or revoked. Generate new ones at https://console.groq.com/keys

**Problem: Only some secrets are found**
→ Check the **exact spelling** of secret labels (must be `GROQ_API_KEY_1`, not `groq_key_1` or `GROQ_KEY_1`).

**Problem: Secrets found but "Untrusted"**
→ In the Kaggle Secrets panel, click the toggle next to each secret to make it green (Trusted).

---

## 🔄 New: Smart Hibernation When Keys Are Exhausted

The notebook now tracks how many consecutive failures happen across **all** keys. If every key fails repeatedly (≈3 full rotations), the notebook will:

1. Save `pipeline_state.json` containing:
   - Current key rotation index
   - Per-model adaptive delay state
   - Failure counters
   - `exhausted: true` flag
2. Print a clear message: `🔴 All N API keys exhausted... Halting so you can refresh keys and resume tomorrow.`
3. Stop cleanly without losing progress

### How to Resume the Next Day

1. Refresh/replace your Groq keys in Kaggle Secrets
2. Re-run the notebook **from the beginning**
3. The notebook will:
   - Load existing `eval_results.csv` / `mcqs_s2.csv` to skip completed items
   - Load `pipeline_state.json` to resume key rotation and delays
   - Verify that your key set hasn't changed (uses MD5 hash)
   - Continue from exactly where it stopped

### Files That Enable Resume

| File | Purpose |
|---|---|
| `mcqs_s1.csv` | Already-generated S1 MCQs (skipped on resume) |
| `mcqs_s2.csv` | Already-generated S2 MCQs (skipped on resume) |
| `eval_results.csv` | Already-completed evaluations (skipped on resume) |
| `pipeline_state.json` | Key rotation index + client delay state |
| `*_progress.csv` | Incremental backup files |

**Important:** Download these files before the Kaggle session ends, or use Kaggle's auto-save to `/kaggle/working`.
