<!-- ⚠️ DEPRECATED — 2026-06-19. This report compares the old Groq-based local v5 run with the 2026-06-13 Kaggle Last_run. The 2026-06-13 Kaggle run suffered from S1 answer-key drift (76.7% mismatched keys), so numbers here must not be treated as current ground truth. See memory.md for the updated state. -->

# ProverbGap Kaggle Run Comparison Report

**Generated:** 2026-06-13
**New run:** `kaggle_analysis/Last_run/extracted_new/`
**Previous run:** `kaggle_analysis/input/`
**Local baseline:** `local_test_output_v5/` (same 3 models)

## 1. Did the fixes work? (New vs Previous)

### 1.1 Overall failure rates

| Metric | New run | Previous run | Change |
|---|---|---|---|
| Total evaluations | 900 | 2700 | — |
| Valid predictions | 765 | 260 | +505 |
| Failures | 135 | 2440 | -2305 |
| Failure rate | 15.0% | 90.4% | **-75.4pp** |
| Valid-prediction rate | 85.0% | 9.6% | **+75.4pp** |

**Finding:** The new run produced valid predictions for **85.0%** of evaluations vs only **9.6%** in the previous run — a **75.4 percentage-point improvement** in yield.

### 1.2 Per-model failure rates

| Model | New failures/total | New rate | Previous model | Previous failures/total | Previous rate |
|---|---|---|---|---|---|
| llama33-70b | 0/300 | 0.0% | llama-3.3-70b-versatile | 804/900 | 89.3% |
| gptoss120b | 135/300 | 45.0% | meta/llama-4-maverick-17b-128e-instruct | 793/900 | 88.1% |
| qwen3-32b | 0/300 | 0.0% | allam-2-7b | 843/900 | 93.7% |

*Note: Models are not identical across runs. Previous run used `llama-3.3-70b-versatile`, `meta/llama-4-maverick-17b-128e-instruct`, and `allam-2-7b`. New run uses `llama33-70b`, `gptoss120b`, and `qwen3-32b`.*

### 1.3 Error / failure types

**New run failures:**

| error | count |
|---|---|
| empty_response | 135 |

**Previous run top failures:**

| error | count |
|---|---|
| All providers failed for allam-2-7b: None | 837 |
| All providers failed for meta/llama-4-maverick-17b-128e-instruct: None | 793 |
| All providers failed for llama-3.3-70b-versatile: None | 792 |
| All providers failed for llama-3.3-70b-versatile: 429 Client Error: Too Many Requests for url: https://integrate.api.nvidia.com/v1/chat/completions | 12 |
| All providers failed for allam-2-7b: 429 Client Error: Too Many Requests for url: https://api.groq.com/openai/v1/chat/completions | 6 |

### 1.4 Runtime indicators

| Indicator | New run | Previous run |
|---|---|---|
| Wall time | ~5,056 s (~84 min) | unknown (log incomplete) |
| Evaluations completed | 900 / 900 (100%) | 2,700 rows, 9.6% valid |
| Explicit 429 lines in log | 0 | 18 rows mention 429 in eval_results.csv |
| Final log timestamp | 5055.9 s | 2363.4 s |

**Critical correction:** The figure "2,326 429s" from memory is a misreading. `2326.1s` in the new log is a wall-clock timestamp at eval 409/900, not an error count. The new run has **no HTTP 429 errors**; failures are `empty_response` from gptoss120b.

## 2. Comparison with local baseline (same 3 models)

### 2.1 Overall (same 3 models only)

| Run | Total | Failures | Failure rate | Valid accuracy | Overall success |
|---|---|---:|---:|---:|---:|
| NEW | 900 | 135 | 15.0% | 0.797 | 0.678 |
| LOCAL | 900 | 181 | 20.1% | 0.780 | 0.623 |

**Finding:** The new run has a lower failure rate than the local same-3-model run (15.0% vs 20.1%) and higher overall success (67.8% vs 62.3%).

### 2.2 Per-model comparison

| Model | Run | Total | Failures | Failure rate | Valid accuracy | Overall success |
|---|---|---:|---:|---:|---:|---:|
| llama33-70b | NEW | 300 | 0 | 0.0% | 0.773 | 0.773 |
| llama33-70b | LOCAL | 300 | 32 | 10.7% | 0.780 | 0.697 |
| gptoss120b | NEW | 300 | 135 | 45.0% | 0.958 | 0.527 |
| gptoss120b | LOCAL | 300 | 149 | 49.7% | 0.987 | 0.497 |
| qwen3-32b | NEW | 300 | 0 | 0.0% | 0.733 | 0.733 |
| qwen3-32b | LOCAL | 300 | 0 | 0.0% | 0.677 | 0.677 |

### 2.3 Per-language comparison

| Language | Run | Total | Failures | Failure rate | Valid accuracy | Overall success |
|---|---|---:|---:|---:|---:|---:|
| English | NEW | 300 | 4 | 1.3% | 0.986 | 0.973 |
| English | LOCAL | 300 | 3 | 1.0% | 0.976 | 0.967 |
| Arabic | NEW | 300 | 46 | 15.3% | 0.823 | 0.697 |
| Arabic | LOCAL | 300 | 50 | 16.7% | 0.836 | 0.697 |
| Yoruba | NEW | 300 | 85 | 28.3% | 0.507 | 0.363 |
| Yoruba | LOCAL | 300 | 128 | 42.7% | 0.360 | 0.207 |

### 2.4 Strategy difficulty (S1 vs S2)

| Strategy | Run | Total | Failures | Failure rate | Valid accuracy | Overall success |
|---|---|---:|---:|---:|---:|---:|
| S1 | NEW | 450 | 64 | 14.2% | 0.793 | 0.680 |
| S1 | LOCAL | 450 | 70 | 15.6% | 0.800 | 0.676 |
| S2 | NEW | 450 | 71 | 15.8% | 0.802 | 0.676 |
| S2 | LOCAL | 450 | 111 | 24.7% | 0.758 | 0.571 |

### 2.5 Per-model x strategy breakdown

| Model | Strategy | Run | Valid | Total | Failure rate | Valid accuracy | Overall success |
|---|---|---|---|---:|---:|---:|---:|
| llama33-70b | S1 | NEW | 150 | 150 | 0.0% | 0.773 | 0.773 |
| llama33-70b | S1 | LOCAL | 150 | 150 | 0.0% | 0.773 | 0.773 |
| llama33-70b | S2 | NEW | 150 | 150 | 0.0% | 0.773 | 0.773 |
| llama33-70b | S2 | LOCAL | 118 | 150 | 21.3% | 0.788 | 0.620 |
| gptoss120b | S1 | NEW | 86 | 150 | 42.7% | 0.977 | 0.560 |
| gptoss120b | S1 | LOCAL | 80 | 150 | 46.7% | 1.000 | 0.533 |
| gptoss120b | S2 | NEW | 79 | 150 | 47.3% | 0.937 | 0.493 |
| gptoss120b | S2 | LOCAL | 71 | 150 | 52.7% | 0.972 | 0.460 |
| qwen3-32b | S1 | NEW | 150 | 150 | 0.0% | 0.707 | 0.707 |
| qwen3-32b | S1 | LOCAL | 150 | 150 | 0.0% | 0.720 | 0.720 |
| qwen3-32b | S2 | NEW | 150 | 150 | 0.0% | 0.760 | 0.760 |
| qwen3-32b | S2 | LOCAL | 150 | 150 | 0.0% | 0.633 | 0.633 |

### 2.6 gptoss120b failure breakdown (new run)

| Language | Strategy | Total | Failures | Valid | Valid accuracy |
|---|---|---:|---:|---:|---:|
| English | S1 | 50 | 0 | 50 | 1.000 |
| English | S2 | 50 | 4 | 46 | 0.978 |
| Arabic | S1 | 50 | 24 | 26 | 0.923 |
| Arabic | S2 | 50 | 22 | 28 | 0.857 |
| Yoruba | S1 | 50 | 40 | 10 | 1.000 |
| Yoruba | S2 | 50 | 45 | 5 | 1.000 |

## 3. Data consistency

### 3.1 MCQ identity (new vs local)

- S1 sample_id ordering identical: **True**
- S2 sample_id ordering identical: **True**
- S1 rows with different Answer letter (choice shuffle): **115/150**
- S2 rows with different Answer letter (choice shuffle): **1/150**

**Interpretation:** The underlying proverbs/sample_ids are identical across new and local runs, but choice order (and therefore the correct Answer letter) was shuffled, which is expected behavior. Each run's predictions were evaluated against its own correct mapping, so accuracy comparisons remain valid.

*Previous-run MCQ ids use a different scheme (e.g., `ENG2109`) and cannot be matched directly.*

### 3.2 Accuracy pattern consistency

| Pattern | New run | Local run | Consistent? |
|---|---|---|---|
| English overall success | 0.973 | 0.967 | Yes |
| Arabic overall success | 0.697 | 0.697 | Yes |
| Yoruba overall success | 0.363 | 0.207 | Yes |
| S1 overall success | 0.680 | 0.676 | Yes |
| S2 overall success | 0.676 | 0.571 | Yes |

### 3.3 Major discrepancies

1. **gptoss120b failure rate** is comparable across environments (45.0% new vs 49.7% local), but still the dominant source of missing predictions.
2. **llama33-70b is more reliable on Kaggle** (0% failures vs 10.7% local), which drives the new run's higher overall success.
3. **Yoruba gptoss120b** has only ~15 valid predictions across both strategies on Kaggle; any per-model Yoruba number for this model is unstable.
4. **Valid-only accuracies are directionally consistent** across new and local runs; the main difference is infrastructure yield, not model capability.

## 4. Critical Data-Integrity Finding

### 4.1 S1 answer-key mismatch

During analysis, a **critical bug** was discovered in the saved S1 outputs:

- The log shows S1 generation ran **twice**: once at the start of the run (used for evaluation) and again at the very end (overwrote `mcqs_s1.csv`).
- Because S1 uses `random.shuffle` without a per-item seed, the two shuffles produced different correct-answer positions.
- **345 / 450 S1 evaluation rows (76.7%)** have `correct` letters that do not match the saved `mcqs_all.csv` `Answer` column.
- **S2 is unaffected** (0 / 450 mismatches) because S2 has resume logic and was not regenerated.

### 4.2 Corrected S1 accuracy

| Metric | Log-reported | Corrected vs saved MCQ keys |
|---|---|---|
| S1 valid predictions | 386 | 386 |
| S1 correct | 306 | **100** |
| S1 accuracy | 79.3% | **25.9%** |

The corrected 25.9% is not a real model-performance number; it is an artifact of the answer-key drift.

### 4.3 Root cause

In `kaggle_full_pipeline_notebook.py`, S1 generation:
1. Uses a single global `random.seed(SEED)`.
2. Calls `random.shuffle(choices)` without re-seeding per item.
3. Has **no resume guard** (`if mcqs_s1.csv exists: skip`).

Consequently, any other randomness in the pipeline (S2 retries, API jitter, etc.) changes the RNG state and causes a different S1 shuffle on re-generation.

---

## 5. Verdict

### 5.1 Is the new run acceptable for a paper?

**Partially.** The run proves the API/infrastructure fixes succeeded, and the S2 results are valid. However, **S1 results from this run cannot be used as-is** because of the answer-key drift.

- **Coverage:** 900 / 900 intended evaluations completed (100%). ✅
- **Failure rate:** 15.0% (new) vs 90.4% (previous) vs 20.1% (local same 3 models). ✅
- **S2 validity:** Confirmed consistent with saved MCQs. ✅
- **S1 validity:** Corrupted by answer-key drift. ❌
- **Quality signal:** S2 valid-only accuracy (~80%) matches local patterns and shows expected ordering: English > Arabic > Yoruba. ✅
- **Main caveat:** gptoss120b's 135 empty responses are concentrated in Arabic and Yoruba, so per-language gptoss120b numbers should include valid-N caveats.

### 5.2 Gaps vs local results

| Gap | Magnitude | Impact |
|---|---|---|
| S1 answer-key consistency | 76.7% mismatched in new run | **Critical** — must fix or use local S1 |
| gptoss120b failure rate | 45.0% (new) vs 49.7% (local) | Comparable; still the weakest model |
| llama33-70b failure rate | 0.0% (new) vs 10.7% (local) | New better |
| Yoruba gptoss120b valid N | 15 total on Kaggle | Severe for per-model Yoruba reporting |
| Overall failure rate | 15.0% (new) vs 20.1% (local same 3) | New better |

### 5.3 Recommended next actions

1. **Patch S1 determinism and resume guard** in `kaggle_full_pipeline_notebook.py`:
   - Add `random.seed(SEED + hash(sid))` before each S1 item's sampling/shuffling.
   - Skip S1 generation if `mcqs_s1.csv` already exists.
2. **Delete `eval_results.csv` and `eval_results_progress.csv`** before the next Kaggle run so evaluation is recomputed against the deterministic S1.
3. **Re-run on Kaggle once.** S2 will resume, S1 will be deterministic and resumable, and the answer-key mismatch will be eliminated.
4. **Validate the new outputs** with `python audit_answer_key_consistency.py <run_dir>`.
5. **If re-run is not possible:** use a hybrid dataset (local S1 + Kaggle S2) or publish pre-computed local results as a Kaggle Dataset.
6. **Report gptoss120b per-language numbers with valid-N caveats** (e.g., Yoruba S2 has only 5 valid predictions).
7. **Do not cite "2,326 429s"** from memory; the log shows that number was a timestamp, not an error count.
8. **Archive the pipeline state and logs** alongside the CSVs for reproducibility.
