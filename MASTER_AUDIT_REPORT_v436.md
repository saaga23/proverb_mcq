# MASTER AUDIT REPORT: ProverbGap v4.3.6

> **Date:** 2026-05-25  
> **Auditors:** 4 parallel agents (Local Pipeline, Kaggle Notebook, Data/Output, Evaluation Logic)  
> **Verdict:** 🔴 **CRITICAL — Multiple bugs corrupt benchmark integrity. Do not submit to EACL without fixes.**

---

## THE BIG PICTURE

You asked us to review your code for the kinds of "funny things" that happened before — wrong data, truncated outputs, models not evaluating properly. **We found all of those and more.**

The most dangerous finding: **Your evaluation prompts leak the correct answer to the models.** This means your accuracy numbers may be artificially inflated because the evaluator is told the answer before being asked to choose.

---

## 🔴 TIER 1: BUGS THAT CORRUPT RESULTS (Fix Before Anything Else)

### 1. CORRECT ANSWER LEAKED IN EVALUATION PROMPT
**Files:** `proverbgap_minimal_local.py`, `proverbgap_kaggle_final.py`, `evaluation_pilot.py`

The evaluation prompt includes:
```
Proverb: {mcq['source_proverb']}
Cultural meaning: {mcq['proverb_en']}

What is the correct meaning?
```

Since `load_data()` overwrites `proverb_en` with `correct_meaning`/`Cultural_Context`, the model is literally told the correct answer before choosing. **This makes accuracy metrics meaningless.**

**Fix:** Remove `proverb_en` from the evaluation prompt. The model should only see the proverb text and the four options, not the gold standard meaning.

---

### 2. DEFAULT DATA DIRECTORY IS `original_data` (WRONG)
**Files:** `proverbgap_kaggle_final.py`, `pilot_v2.py`, `test_pilot_v2.py`

`kaggle_final.py` line 121 and `pilot_v2.py` line 59 default to `original_data/`. But `original_data/` has been **deleted from the repo** (git shows `D` status). The correct data is in `actual_data/`.

**Impact:**
- Kaggle notebook loads wrong data on fresh checkout
- `test_pilot_v2.py` hardcodes `--data-dir original_data` in every test
- Local runs fail silently or crash

**Fix:** Change ALL defaults to `actual_data/`. Update all tests.

---

### 3. `pilot_v2.py` HAS ZERO QA_FLAG FILTERING
**File:** `pilot_v2.py`

`_load_and_prepare_data()` never checks `QA_Flag`. **39 Yoruba items flagged `DROP` will leak into generation and evaluation.**

**Fix:** Add QA_Flag filtering identical to `kaggle_final.py`:
```python
if 'QA_Flag' in df.columns:
    df = df[df['QA_Flag'] != 'DROP']
```

---

### 4. `pilot_v2.py` AUDIT USES `max_tok=5` — TRUNCATES ANSWERS
**File:** `pilot_v2.py` line 795

`audit_one_model()` requests only 5 tokens. Any model that emits:
- A newline first
- A `<think>` tag
- Even "The answer is B"

...will have its response truncated. This creates false "non-responding" predictions.

**Fix:** Increase to `max_tok=128` or higher for audit.

---

### 5. `best_effort` ITEMS TREATED AS STRICT S2
**File:** `proverbgap_kaggle_final.py`

When S2 generation fails BOTH length and semantic gates, `kaggle_final.py` returns `best_options` with `is_fallback=False` and `info="best_effort"`. These garbage items are included in the "strict S2" accuracy calculation.

**Fix:** Change `best_effort` to `fallback=True`.

---

### 6. ANSWER EXTRACTION USES FIRST MATCH (WRONG)
**Files:** `pilot_v2.py`, `evaluation_pilot.py`

If a model reasons: *"A is wrong... B is wrong... C is correct"*, the regex extracts **A** (first match) instead of **C** (last match). `minimal_local.py` correctly uses last match.

**Fix:** Switch to last-match extraction in `pilot_v2.py` and `evaluation_pilot.py`.

---

### 7. FEW-SHOT EXAMPLES ALWAYS HAVE ANSWER 'A'
**File:** `proverbgap_kaggle_final.py`

The two in-context examples are hardcoded with answer position 'A'. This leaks position bias into few-shot prompting.

**Fix:** Rotate answer positions in few-shot examples.

---

### 8. EVALUATION PLURALITY VOTE INSTEAD OF MAJORITY
**File:** `evaluation_pilot.py`

Consensus uses `max(set, key=...)` — plurality (most common), not majority (>50%). With 2 models, a 1-1 split picks one arbitrarily.

**Fix:** Use majority threshold: `count > len(preds) / 2`.

---

## 🟡 TIER 2: BUGS THAT BIAS OR HIDE PROBLEMS

### 9. `hash()` IS NON-DETERMINISTIC FOR POSITION SHUFFLING
**File:** `proverbgap_kaggle_final.py`

`seed = hash(model) + idx` uses Python's `hash()`, which is randomized per process (PYTHONHASHSEED). Position shuffling is **not reproducible** across runs.

**Fix:** Use `hashlib.md5(model.encode()).hexdigest()` or `mmh3`.

---

### 10. NO PER-MODEL POSITION SHUFFLING IN `pilot_v2.py`
**File:** `pilot_v2.py`

`assemble_mcq()` accepts a `model_seed` parameter but `_generate_strategy1()` and `generate_language_strategy2()` never pass it. All committee models see the **same** option ordering.

**Fix:** Pass `model_seed` in generation functions.

---

### 11. PREFLIGHT VALIDATION READS FROM STALE CACHE
**File:** `pilot_v2.py`

`preflight_validate_committee()` calls `call_api()`, which returns cached responses. A model with a dead API key appears healthy because yesterday's cached response is reused.

**Fix:** Add `skip_cache=True` to preflight probes.

---

### 12. PROGRESS COUNTS FAILURES AS SUCCESS
**File:** `proverbgap_kaggle_final.py`

`eval_worker()` increments the progress counter for RuntimeError, Exception, and CIRCUIT_OPEN outcomes. A run can log "2700/2700 complete" with 50% null predictions.

**Fix:** Separate "attempted" from "succeeded" counters.

---

### 13. UNCLOSED `<think>` TAGS NOT STRIPPED IN `pilot_v2.py`
**File:** `pilot_v2.py`

`_RE_THINK` requires a closing `</think>`. Reasoning models often leave tags unclosed. The minimal script handles this with `\Z`; `pilot_v2.py` does not.

**Fix:** Use `r'<think>.*?(</think>|\Z)'` pattern.

---

### 14. S1 FALLBACK CREATES 4 IDENTICAL OPTIONS
**File:** `proverbgap_minimal_local.py`

`generate_s1()` fallback returns `[row['proverb_en']] * 4`. `assemble_mcq()` has zero deduplication, creating completely invalid MCQs.

**Fix:** Generate distinct fallback distractors.

---

### 15. NO POST-WRITE CSV VALIDATION
**Files:** ALL scripts

After `to_csv()`, no script reads the file back to verify row count, encoding, or integrity. Corrupted writes go undetected.

**Fix:** Add post-write assertions:
```python
df_check = pd.read_csv(path)
assert len(df_check) == expected_rows
```

---

## 🟢 TIER 3: CODE QUALITY / MAINTAINABILITY

| # | Issue | File | Fix |
|---|-------|------|-----|
| 16 | `original_data/` directory missing, tests crash | `test_pilot_v2.py` | Use `actual_data/` |
| 17 | JSON parser extracts FIRST list, not answer list | `pilot_v2.py` | Use last list or JSON mode |
| 18 | Hardcoded API keys in plaintext | `minimal_local.py`, `kaggle_final.py` | Use env vars |
| 19 | Provider disabled too aggressively | `pilot_v2.py` | Disable per-model, not per-provider |
| 20 | Semantic validator is English-only | `pilot_v2.py` | Document limitation or use multilingual model |
| 21 | Cache concurrency risk | `pilot_v2.py` | Add proper locking |
| 22 | `subprocess` imported inside `main()` | `pilot_v2.py` | Move to top level |
| 23 | Encoder results excluded from main stats | `kaggle_final.py` | Concatenate or document |
| 24 | S2 dual-gate is OR not AND | `kaggle_final.py` | Document or change to AND |
| 25 | `max_tok=512` may truncate JSON | `kaggle_final.py` | Validate JSON completeness |
| 26 | No contamination filter in `pilot_v2.py`/`minimal_local.py` | multiple | Add shared filter utility |
| 27 | `eval_worker` shuffles with different seed than generation | `kaggle_final.py` | Use same seed or document |
| 28 | Position bias test always null in stratified mode | `kaggle_final.py` | Fix test logic |
| 29 | Suspicious/invalid model IDs in committee | `pilot_v2.py` | Verify: `gpt-oss-120b`, `mistral-large-3-675b` |
| 30 | Tests reimplement logic instead of calling production code | `test_pilot_v2.py` | Call actual functions |

---

## WHAT THE PREVIOUS "CATASTROPHIC MISMATCH" MISSED

Your earlier v4.3.6 fix corrected the **data-model mismatch** (using `Correct_Meaning` instead of `Translation`). But these agents found that:

1. **The fix was applied inconsistently** — `pilot_v2.py` still uses different columns than `kaggle_final.py`
2. **Evaluation prompts still leak the answer** — even with the right data, the prompt architecture is broken
3. **Output validation was never added** — you can't tell if CSVs are correct
4. **Test suite validates the wrong defaults** — tests hardcode `original_data`
5. **Position shuffling is broken in multiple ways** — non-deterministic hash, not used in pilot_v2, different seeds in eval vs generation

---

## RECOMMENDED FIX ORDER

### Week 1: Fix Corrupting Bugs
| Day | Task | Files |
|-----|------|-------|
| 1 | Fix evaluation prompt leak | `minimal_local.py`, `kaggle_final.py`, `evaluation_pilot.py` |
| 1 | Change all defaults to `actual_data/` | `kaggle_final.py`, `pilot_v2.py`, `test_pilot_v2.py` |
| 2 | Add QA_Flag filtering to `pilot_v2.py` | `pilot_v2.py` |
| 2 | Fix `max_tok=5` → `128` | `pilot_v2.py` |
| 3 | Fix answer extraction (first→last match) | `pilot_v2.py`, `evaluation_pilot.py` |
| 3 | Fix few-shot 'A' leak | `kaggle_final.py` |
| 4 | Fix `best_effort`→fallback | `kaggle_final.py` |
| 4 | Fix plurality→majority | `evaluation_pilot.py` |
| 5 | Fix `hash()` non-determinism | `kaggle_final.py` |
| 5 | Add per-model position shuffling | `pilot_v2.py` |

### Week 2: Validation & Testing
| Day | Task |
|-----|------|
| 6 | Re-run N=5 local test with all fixes |
| 7 | Verify CSV outputs match expected counts |
| 8 | Run test suite, fix failing tests |
| 9 | Scale to N=50 for confidence |
| 10 | Full N=700 run |

---

## VERIFICATION CHECKLIST (After Fixes)

- [ ] Evaluation prompt does NOT contain correct meaning
- [ ] All scripts default to `actual_data/`
- [ ] QA_Flag DROP items excluded everywhere
- [ ] Answer extraction uses LAST match
- [ ] Few-shot examples rotate answer positions
- [ ] `best_effort` items classified as fallback
- [ ] Consensus uses majority (>50%), not plurality
- [ ] Position shuffling uses deterministic hash
- [ ] Per-model position shuffling active in all scripts
- [ ] Preflight skips cache
- [ ] Progress counter distinguishes attempted vs succeeded
- [ ] Post-write CSV validation asserts row counts
- [ ] N=5 local run produces expected results
- [ ] Test suite passes on clean checkout

---

*This audit was conducted by 4 independent agents reviewing `proverbgap_minimal_local.py`, `proverbgap_kaggle_final.py`, `pilot_v2.py`, `test_pilot_v2.py`, and `evaluation_pilot.py`.*
