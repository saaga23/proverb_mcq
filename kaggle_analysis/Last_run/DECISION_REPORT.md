# ProverbGap Kaggle Last_run Decision Report

**Run date:** 2026-06-09  
**Analyzed:** 2026-06-13  
**Artifacts:** `C:/Users/USER/Downloads/THe proverbeval container/MCQ/kaggle_analysis/Last_run/`

---

## 1. Executive Summary

The infrastructure fixes **worked**. The new Kaggle run completed 900/900 evaluations with only **15.0% empty-response failures**, down from the previous run's ~90% failure rate. There are **zero HTTP 429 / rate-limit errors** in the log, and all 8 Groq Secret keys validated successfully.

However, a **critical data-integrity bug** was discovered: the saved `mcqs_s1.csv` was regenerated a second time after evaluation had already run, and because S1 uses `random.shuffle` without a per-item seed, the correct-answer letters shifted. This makes the printed S1 accuracy numbers **invalid for the saved MCQ files**.

**Verdict:** The run proves the API layer is now reliable, but the S1 results cannot be used as-is. The cleanest next action is to **patch S1 determinism/resume, delete the old evaluation CSVs, and re-run once more on Kaggle**. S2 generation and evaluation are already valid and can be resumed.

---

## 2. What Worked

### 2.1 Key pool and rate limiting

| Metric | Previous run | New run |
|---|---|---|
| API keys validated | 1 of 4 usable | **8 of 11 valid** |
| HTTP 429 errors | ~18 explicit mentions | **0** |
| API client `total_failures` | High | **0 for all 3 models** |
| Final adaptive delay | 20 s (capped) | **5.0 s for all models** |
| `pipeline_state.json` `exhausted` | — | **false** |

The multi-secret loader found 8 valid Groq keys, and the adaptive delay system never had to increase delays because no rate-limiting occurred.

### 2.2 Coverage

| Goal | Status | Evidence |
|---|---|---|
| S1 MCQs generated | ✅ | 150/150 |
| S2 MCQs generated | ✅ | 150/150 (7 hard fallbacks, 4.67%) |
| Evaluations completed | ✅ | 900/900 |
| Wall time | ✅ | ~84 minutes |

### 2.3 Overall failure rate

- **Total failures:** 135 / 900 = **15.0%**
- **All failures are `empty_response` from `gptoss120b`**
- `llama33-70b`: 0 failures
- `qwen3-32b`: 0 failures

This is a 75.4 percentage-point improvement over the previous run.

---

## 3. Critical Issue: S1 Answer-Key Drift

### 3.1 What happened

The log shows S1 generation ran **twice**:

```text
22.2s 50 [S1] Generated 150 MCQs        ← first generation, used for evaluation
...
5043.9s 1843 [S1] Generated 150 MCQs    ← second generation, overwrote mcqs_s1.csv
```

The first generation produced the MCQs that were evaluated. The second generation overwrote `mcqs_s1.csv` on disk. Because S1 shuffles choices with `random.shuffle` and does **not** re-seed per item, the two shuffles produced different correct-answer positions.

### 3.2 Impact

| Check | Result |
|---|---|
| S1 eval rows with mismatched `correct` vs saved `Answer` | **345 / 450 (76.7%)** |
| Unique S1 MCQs affected | **115 / 150** |
| S2 eval rows mismatched | **0 / 450** |

**Reported S1 accuracy (log):** 79.3%  
**Actual S1 accuracy vs saved MCQ keys:** **25.9%**

S2 is unaffected because S2 has proper resume logic and was not regenerated.

### 3.3 Root cause

In `kaggle_full_pipeline_notebook.py`:

```python
random.seed(SEED)   # global seed only
...
choices = [correct] + distractors
random.shuffle(choices)
answer_letter = ["A", "B", "C", "D"][choices.index(correct)]
```

There is **no per-item seed** and **no S1 resume guard** (`if mcqs_s1.csv exists: skip`).

---

## 4. Corrected Numbers

### 4.1 S1 (using saved `mcqs_all.csv` answer keys)

| Language | Valid | Correct | Accuracy |
|---|---|---|---|
| English | 150 | 35 | 23.3% |
| Arabic | 126 | 23 | 18.3% |
| Yoruba | 110 | 42 | 38.2% |
| **Total** | **386** | **100** | **25.9%** |

These numbers are **not meaningful** because the answer keys are mismatched.

### 4.2 S2 (valid, using saved answer keys)

| Language | Valid | Correct | Accuracy |
|---|---|---|---|
| English | 96 | 95 | 98.6% |
| Arabic | 128 | 102 | 79.7% |
| Yoruba | 155 | 107 | 69.0% |
| **Total** | **379** | **304** | **80.2%** |

S2 is trustworthy.

### 4.3 Model-level failure pattern (new run)

| Model | Calls | Failures | Failure rate | Valid accuracy |
|---|---|---|---|---|
| `llama33-70b` | 300 | 0 | 0.0% | 77.3% |
| `qwen3-32b` | 522* | 0 | 0.0% | 73.3% |
| `gptoss120b` | 300 | 135 | 45.0% | 95.8% |

\* Qwen's extra 222 calls are from S2 adversarial distractor generation.

`gptoss120b` is the only remaining problem. Its failures are concentrated in non-English:

| Language | `gptoss120b` failure rate |
|---|---|
| English | 4.0% (2/100) |
| Arabic | 46.0% (46/100) |
| Yoruba | **85.0%** (85/100) |

---

## 5. Comparison with Local Baseline

Using the same 3 models from `local_test_output_v5/`:

| Run | Failure rate | Overall success | Valid accuracy |
|---|---|---|---|
| **New Kaggle** | **15.0%** | **67.8%** | **79.7%** |
| Local same-3 | 20.1% | 62.3% | 78.0% |

The new Kaggle run is **better** than the local same-3-model baseline, mainly because `llama33-70b` had 0% failures on Kaggle vs 10.7% locally.

S2 patterns are consistent between Kaggle and local. S1 from local is valid and can be used if we choose the hybrid path.

---

## 6. Options and Recommendation

### Option A — Re-run Kaggle once more with S1 fix (RECOMMENDED)

**What to do:**
1. Patch `kaggle_full_pipeline_notebook.py`:
   - Add **per-item deterministic seed** before S1 shuffle: `random.seed(SEED + sample_id)`
   - Add **S1 resume guard**: skip generation if `mcqs_s1.csv` already exists
2. Delete `eval_results.csv` and `eval_results_progress.csv` from the working directory before the run
3. Re-run on Kaggle

**Why this is best:**
- Produces a single, self-consistent Kaggle run
- S2 generation will resume (skip), saving time and API calls
- S1 will be deterministic and resumable on future runs
- Fixes the answer-key mismatch permanently
- Total cost: ~900 evaluation calls + already-completed S2 (~84 minutes, same as before)

**Risk:** Low. The API layer is proven; only a deterministic bug needs fixing.

### Option B — Hybrid: local S1 + Kaggle S2

**What to do:**
- Use `local_test_output_v5/mcqs_s1.csv` and its S1 evaluations
- Use Kaggle `mcqs_s2.csv` and its S2 evaluations
- Merge into one analysis

**Pros:** No re-run, no additional API cost  
**Cons:** Less clean for a paper; two different environments for the two strategies

### Option C — Publish pre-computed local results only

**What to do:**
- Upload `local_test_output_v5/` artifacts as a Kaggle Dataset
- Treat the local run as the canonical result

**Pros:** Removes all API fragility from the public reproducibility path  
**Cons:** Does not demonstrate live Kaggle reproducibility

### Option D — Switch to Fatima / Hugging Face compute now

**Assessment:** Not needed yet. The Groq API layer is working for 2 of 3 models (`llama33-70b`, `qwen3-32b`) and S2 is valid. Fatima/HF compute should still be pursued as a **parallel track** for cost relief and to run larger models, but it is not the immediate blocker.

---

## 7. Concrete Next Steps

1. **Apply the S1 patch** to `kaggle_full_pipeline_notebook.py` (per-item seed + resume guard).
2. **Delete old eval CSVs** before uploading the notebook:
   - `eval_results.csv`
   - `eval_results_progress.csv`
3. **Re-run on Kaggle once**.
4. **Validate the new outputs** by checking:
   - S1 eval `correct` column matches `mcqs_s1.csv` `Answer` column
   - Overall failure rate stays ≤ 20%
   - 900/900 evaluations complete
5. **If the re-run succeeds:** use it as the primary paper result.
6. **If the re-run fails again:** fall back to Option B (hybrid) or Option C (pre-computed local dataset).
7. **Continue Fatima outreach** in parallel for future compute credits.

---

## 8. What to Report in the Paper (for now)

Until the re-run completes, **do not use the Kaggle S1 numbers** from this run. You can report:

- The API-reliability outcome: 8 valid keys eliminated rate-limit failures, reducing overall failure rate from ~90% to 15%.
- S2 results from this run (valid): ~80% accuracy, with expected difficulty ordering English > Arabic > Yoruba.
- `gptoss120b` caveat: 45% empty-response rate, concentrated in Arabic/Yoruba.
- Local baseline results for S1 or as the primary result if the re-run is delayed.

---

## 9. Bottom Line

**The Kaggle pipeline is now reliable. The only remaining issue is a deterministic S1 shuffle bug. Fix it, delete the old eval CSVs, and re-run once.** S2 is already clean and can be resumed, so the re-run cost is essentially 900 evaluation calls. This is the fastest path to a paper-ready, fully reproducible Kaggle result.
