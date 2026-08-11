# Phase 3: Budget-Dependent Execution Plan

**Status:** PENDING BUDGET RENEWAL  
**Decision date:** 2026-07-10  
**Deadline:** August 1, 2026 (2 days before ARR submission)  

---

## Decision Rule

```
IF OpenRouter budget is renewed by July 26:
    EXECUTE v69 (USE_LLM_FALLBACK=True, N=5)
    IF v69 passes gates (HCW < 15%, partial+fallback < 30%, cost < $1.50):
        EXECUTE v70 (USE_LLM_FALLBACK=True, N=15)
        Replace v68 numbers in paper with v70 numbers
    ELSE:
        Keep v68 as primary; add v69 as robustness check
ELSE:
    Submit with v68 N=5 as production dataset
    Frame paper explicitly as N=5 methodology study
```

---

## v69 Configuration

**File to modify:** `src/generation/openrouter_pilot_distractor_generation_test_nano_opus.py`

```python
# v69 config
N_PER_LANG = 5
USE_LLM_FALLBACK = True
FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"
# All other v68 constants unchanged
```

**Success gates:**
- HCW < 15% (step target; ideally < 10%)
- Partial + fallback < 30% (step target; ideally < 15%)
- No increase in perfect consensus above 45%
- Cost < $1.50 for N=5

**Expected cost:** $0.10–$0.20 additional (one cheap LLM call per replacement × ~180 replacements)

---

## v70 Configuration (if v69 passes)

```python
# v70 config
N_PER_LANG = 15
USE_LLM_FALLBACK = True
FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"
# All other v69 constants unchanged
```

**Expected cost:** ~$2.56 (extrapolated from v68 $0.85 × 3 for N=15, plus LLM fallback overhead)

---

## Execution Steps (When Budget Confirmed)

### Step 1: Confirm Budget
- Check OpenRouter dashboard for available credits
- Document in `docs/budget_status.md`

### Step 2: Configure v69
- Edit `src/generation/openrouter_pilot_distractor_generation_test_nano_opus.py`
- Set `USE_LLM_FALLBACK = True`
- Set `FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"`
- Keep `N_PER_LANG = 5`

### Step 3: Regenerate Notebook
```bash
python convert_test_nano_opus_to_notebook.py
```

### Step 4: Push to Kaggle
```bash
python scripts/trigger_kaggle_run.py \
    --slug abrahamsunday123/mcq-pass-shortcut \
    --metadata kaggle_upload_pilot1_test/kernel-metadata.json \
    --notebook openrouter_pilot_distractor_generation_test_nano_opus.ipynb
```

### Step 5: Monitor Run
- Check Kaggle every 4 hours
- If run fails, capture error and decide: retry or fall back to v68

### Step 6: Download and Analyze v69
```bash
kaggle datasets download -r <run_id> -p kaggle/run_logs/v69/
```

Run analysis scripts from `kaggle/run_logs/v68/analysis_scripts/` against v69 data.

### Step 7: v69 Gate Check
Compare v69 metrics to targets. Record in `docs/v69_gate_check.md`.

### Step 8: If v69 Passes, Run v70
Repeat Steps 2–6 with `N_PER_LANG = 15`.

### Step 9: If v69 Fails or Budget Exhausted
Use v68 as production dataset. Document in `docs/production_dataset_decision.md`.

---

## Paper Update Procedure (If v69/v70 Succeeds)

1. Replace all v68 numbers in `paper/proverbgap_eacl2027.md` with v69/v70 numbers
2. Regenerate figures from v69/v70 data
3. Re-run bootstrap CIs and statistical tests
4. Update `docs/ProverbGap_Reframed_Title_Abstract.md`
5. Run final consistency check

---

## Submission Package Structure

```
submission_package_2026-08-02/
  proverbgap_eacl2027.md          # Full paper draft
  README.md                       # Package description
  reviewer_risk_checklist.md      # P0/P1/P2 status
  reproducibility/
    requirements.lock
    openrouter_catalog_snapshot_2026-06-22.json
    v68_output_hashes.txt
    REPRODUCIBILITY_CHECKLIST.md
  tables/
    (all table CSVs from v68)
  figures/
    (all PNG figures)
  DATA_PROVENANCE_TEMPLATE.md
  EXECUTION_ITINERARY_2026-07-10.md
```

---

## Fallback Plan (If Budget Not Renewed)

1. Submit v68 N=5 paper on August 1, 2026
2. Frame explicitly as "N=5 methodology study"
3. Include v69 as planned ablation (not executed)
4. State: "We plan to run v69 with LLM-based fallback when budget renews"
5. Release 180 MCQs as testbed, not final benchmark

---

*Phase 3 prepared: 2026-07-10. Execution blocked on budget renewal.*
