#!/usr/bin/env python3
"""
Kaggle Secrets Diagnostic Tool for ProverbGap
==============================================
Run this FIRST on Kaggle to verify your secrets are accessible.

HOW TO USE:
1. Upload this file to your Kaggle notebook
2. Run it in a cell:  %run kaggle_secrets_diagnostic.py
3. Check the output — it will tell you exactly which secrets were found

HOW TO STORE YOUR KEYS IN KAGGLE SECRETS:
1. In your Kaggle notebook, click:  Add-ons → Secrets
2. Click "Add Secret" for EACH key:
   - Label: GROQ_API_KEY_1   → Value: your first key
   - Label: GROQ_API_KEY_2   → Value: your second key
   - ... up to GROQ_API_KEY_7 (or more)
3. Click "Save" after each one
4. Make sure the notebook is set to "Trusted" (toggle in the Secrets panel)

ALTERNATIVE: Store all keys in ONE secret as comma-separated:
   - Label: GROQ_API_KEY   → Value: key1,key2,key3,key4,key5,key6,key7
"""
import os
import sys

print("=" * 70)
print("KAGGLE SECRETS DIAGNOSTIC")
print("=" * 70)

# ── 1. Check if we are on Kaggle ─────────────────────────────────────────────
is_kaggle = os.path.exists("/kaggle")
print(f"\n[ENV] Running on Kaggle: {is_kaggle}")
print(f"[ENV] Python version: {sys.version.split()[0]}")

# ── 2. Try to import kaggle_secrets ──────────────────────────────────────────
print("\n[IMPORT] Trying to import kaggle_secrets...")
try:
    from kaggle_secrets import UserSecretsClient
    print("[IMPORT] ✅ kaggle_secrets imported successfully")
    secrets_available = True
except ImportError as e:
    print(f"[IMPORT] ❌ Cannot import kaggle_secrets: {e}")
    print("         This is normal if you're not on Kaggle.")
    secrets_available = False

if not secrets_available:
    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE — kaggle_secrets not available.")
    print("Run this script INSIDE a Kaggle notebook.")
    print("=" * 70)
    sys.exit(0)

# ── 3. Try to create a UserSecretsClient ─────────────────────────────────────
print("\n[CLIENT] Creating UserSecretsClient...")
try:
    client = UserSecretsClient()
    print("[CLIENT] ✅ UserSecretsClient created successfully")
except Exception as e:
    print(f"[CLIENT] ❌ Failed to create UserSecretsClient: {e}")
    sys.exit(1)

# ── 4. Probe for secrets with different naming patterns ──────────────────────
print("\n[PROBE] Probing for Groq API keys with different secret names...")
print("-" * 70)

# Patterns to try
patterns = [
    "GROQ_API_KEY",
    "GROQ_API_KEY_1", "GROQ_API_KEY_2", "GROQ_API_KEY_3",
    "GROQ_API_KEY_4", "GROQ_API_KEY_5", "GROQ_API_KEY_6",
    "GROQ_API_KEY_7", "GROQ_API_KEY_8", "GROQ_API_KEY_9", "GROQ_API_KEY_10",
    "GROQ_KEY", "GROQ_KEY_1", "GROQ_KEY_2", "GROQ_KEY_3",
    "groq_api_key", "groq_key",
]

found_secrets = []
for name in patterns:
    try:
        val = client.get_secret(name)
        if val and len(val.strip()) > 10:
            masked = val[:8] + "..." + val[-4:] if len(val) > 15 else "[too short]"
            comma_count = val.count(",")
            if comma_count > 0:
                parts = [p.strip() for p in val.split(",") if len(p.strip()) > 10]
                print(f"  ✅ {name}: FOUND (value={masked}, contains {comma_count+1} comma-separated entries → {len(parts)} valid keys)")
                found_secrets.extend(parts)
            else:
                print(f"  ✅ {name}: FOUND (value={masked})")
                found_secrets.append(val.strip())
        else:
            print(f"  ⚠️  {name}: found but empty/too short")
    except Exception as e:
        # get_secret raises when secret doesn't exist — this is expected
        print(f"  ❌ {name}: NOT FOUND ({type(e).__name__})")

# ── 5. Deduplicate and summarize ─────────────────────────────────────────────
unique_keys = list(dict.fromkeys(found_secrets))  # preserve order, dedup
print("\n" + "-" * 70)
print(f"[SUMMARY] Total secret entries found: {len(found_secrets)}")
print(f"[SUMMARY] Unique valid keys:          {len(unique_keys)}")

if len(unique_keys) == 0:
    print("\n" + "=" * 70)
    print("⚠️  NO KEYS FOUND")
    print("=" * 70)
    print("""
You have 0 Groq API keys accessible from Kaggle Secrets.

POSSIBLE REASONS:
1. Secrets are not saved yet — go to Add-ons → Secrets and add them.
2. Secrets are saved but the notebook is not "Trusted".
   In the Secrets panel, make sure the toggle is ON (green).
3. Secret names don't match what the code is looking for.
   The code probes for: GROQ_API_KEY, GROQ_API_KEY_1, GROQ_KEY, etc.
4. You are running this locally — Kaggle Secrets only work inside Kaggle.

RECOMMENDED FIX:
- Go to Add-ons → Secrets in your Kaggle notebook
- Add secrets with these EXACT labels:
    GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3, ...
- Paste one key per secret
- Toggle "Trusted" ON for each
- Re-run this diagnostic
""")
else:
    print("\n" + "=" * 70)
    print(f"✅ FOUND {len(unique_keys)} UNIQUE KEY(S)")
    print("=" * 70)
    for i, k in enumerate(unique_keys, 1):
        masked = k[:8] + "..." + k[-4:]
        print(f"  Key {i}: {masked}  (length={len(k)})")

    # ── 6. Quick validation test ────────────────────────────────────────────
    print("\n[VALIDATE] Quick validation against Groq API...")
    import requests
    valid_count = 0
    for i, key in enumerate(unique_keys, 1):
        try:
            r = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            if r.status_code == 200:
                print(f"  Key {i}: ✅ VALID (200)")
                valid_count += 1
            elif r.status_code == 401:
                print(f"  Key {i}: ❌ INVALID (401 Unauthorized)")
            else:
                print(f"  Key {i}: ⚠️  Status {r.status_code}")
        except Exception as e:
            print(f"  Key {i}: ⚠️  Error during validation: {e}")

    print(f"\n[RESULT] {valid_count}/{len(unique_keys)} keys passed validation")

    if valid_count >= 3:
        print("\n🎉 You have enough valid keys to run the full 3-model benchmark!")
    elif valid_count >= 1:
        print(f"\n⚠️  You have {valid_count} valid key(s). The benchmark will run but")
        print("   rate-limiting may still occur. Consider adding more keys.")
    else:
        print("\n❌ None of the found keys are valid. They may be expired or revoked.")
        print("   Generate new keys at https://console.groq.com/keys")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
