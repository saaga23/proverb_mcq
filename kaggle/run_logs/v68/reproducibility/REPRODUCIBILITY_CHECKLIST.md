# Reproducibility Checklist — ProverbGap v68

**Dataset version:** v68 N=5  
**Run date:** 2026-06-22  
**Seed:** 20260615  
**Generated:** 2026-07-10  

---

## 1. Environment

| Item | Value |
|------|-------|
| Python version | 3.12.3 |
| Key libraries | pandas 2.3.3, numpy (system), sentence-transformers (installed on Kaggle), scikit-learn (installed on Kaggle) |
| Lockfile | `reproducibility/requirements.lock` (from Kaggle environment) |
| Dockerfile | Not yet created |
| Conda env | Not yet created |

## 2. Model Catalog Snapshot

**File:** `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`

Generator pool (active):
- `qwen/qwen3.7-max`
- `google/gemma-4-31b-it`
- `google/gemini-2.5-flash`

Committee pool (active):
- `meta-llama/llama-3.3-70b-instruct`
- `mistralai/mistral-small-3.2-24b-instruct`
- `google/gemma-3-27b-it`
- `deepseek/deepseek-v3.2`

## 3. Seed and State

- Fixed seed: `20260615`
- Position counter persisted in state: Yes
- Resume state file: `pilot1_test_state.json`

## 4. Cost

| Item | Value |
|------|-------|
| Total cost | $0.8539 |
| Cost per MCQ | $0.0047 |
| Cost per audit vote | $0.0012 |
| Total API calls | 1,260 (estimated) |

## 5. Output Artifacts

| File | SHA256 |
|------|--------|
| `pilot1_test_generated_mcqs.csv` | See `reproducibility/v68_output_hashes.txt` |
| `pilot1_test_audit_results.csv` | See `reproducibility/v68_output_hashes.txt` |
| `pilot1_test_raw_outputs.csv` | See `reproducibility/v68_output_hashes.txt` |
| `pilot1_test_summary.json` | See `reproducibility/v68_output_hashes.txt` |

## 6. Reproduction Steps

```bash
# 1. Clone repo
git clone <repo-url>
cd MCQ

# 2. Install dependencies
pip install -r reproducibility/requirements.lock

# 3. Set OpenRouter API key
export OPENROUTER_API_KEY="your-key"

# 4. Run notebook or script
# Option A: Kaggle notebook
# Upload openrouter_pilot_distractor_generation_test_nano_opus.ipynb to Kaggle
# Attach OPENROUTER_API_KEY secret
# Run all cells

# Option B: Local script
python src/generation/openrouter_pilot_distractor_generation_test_nano_opus.py

# 5. Verify output hashes match
sha256sum -c reproducibility/v68_output_hashes.txt
```

## 7. Known Limitations

- OpenRouter model IDs may change; use catalog snapshot for exact reproduction.
- API costs may vary with live pricing.
- Yoruba data source has copyright restrictions; reproducibility requires Owomoyela (2005) or equivalent.
- Position shuffling is INACTIVE in v68; v70 should enable it.

## 8. Contact

For reproduction issues, contact the authors or open an issue on GitHub.

---

*Checklist created: 2026-07-10*
