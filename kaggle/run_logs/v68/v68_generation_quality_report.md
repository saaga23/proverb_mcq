# v68 Kaggle Run — Generation Pipeline Quality Report

**Run path:** `C:/Users/USER/Downloads/THe proverbeval container/MCQ/kaggle_run_logs/v68/openrouter_pilot1_test_output`  
**Total MCQs:** 180 ({'Arabic': 60, 'English': 60, 'Yoruba': 60})  
**Total generation-stage raw rows:** 183  

---

## 1. Distribution of `generation_status`

| Status | Count | Percentage |
|---|---:|---:|
| generated | 101 | 56.1% |
| partial | 50 | 27.8% |
| length_fallback | 29 | 16.1% |
| parse_fallback | 0 | 0.0% |
| hard_fallback | 0 | 0.0% |

**Interpretation:** Only **56.1%** of MCQs were fully `generated`; **43.9%** needed at least one corpus fallback (`partial` + `length_fallback`). No parse or hard fallbacks occurred.

---

## 2. Mean replacements per MCQ

| Metric | Mean per MCQ | Notes |
|---|---:|---|
| `fallback_count` | 0.994 | Avg. corpus-fallback replacements |
| `length_replaced` | 0.150 | Length-parity replacements |
| `nli_replaced` | 0.361 | NLI paraphrase replacements |
| `leak_replaced` | 0.350 | Correct-meaning leak replacements |
| `duplicate_options` | 0.000 | Exact duplicate option pairs (reported) |

**Raw-generation attempt means (n=183):**

| Metric | Mean |
|---|---:|
| `blocklist_replaced` | 0.016 |
| `dup_replaced` | 0.000 |
| `correct_length_outlier` | 0.027 |
| `fallback_count` (raw) | 0.989 |
| `length_replaced` (raw) | 0.148 |

*Note:* `blocklist_replaced` and `dup_replaced` are logged at the raw generation-attempt level. The 3 blocklist hits all occurred on rows with a missing `mcq_id`, so the per-MCQ aggregated count is 0; `dup_replaced` is 0 everywhere.

---

## 3. Duplicate and near-duplicate options

| Type | Count |
|---|---:|
| Exact duplicate option pairs | 0 |
| Near-duplicate pairs (Jaccard > 0.50) | 3 |
| Near-duplicate pairs (token overlap ≥ 0.85) | 0 |
| `duplicate_options_count` (metrics file) | 0 |

The pipeline reported **zero exact duplicate options**, and our independent check confirms no exact collisions. Near-duplicate token overlap is also minimal.

---

## 4. Per-generator and per-variant patterns

### 4a. Status by generator

| generator_model         |   generated |   length_fallback |   partial |   All |
|:------------------------|------------:|------------------:|----------:|------:|
| google/gemini-2.5-flash |          30 |                 5 |        25 |    60 |
| google/gemma-4-31b-it   |          40 |                 6 |        14 |    60 |
| qwen/qwen3.7-max        |          31 |                18 |        11 |    60 |
| All                     |         101 |                29 |        50 |   180 |

**Mean replacements by generator:**

| generator_model         |   fallback_count |   length_replaced |   nli_replaced |   leak_replaced |
|:------------------------|-----------------:|------------------:|---------------:|----------------:|
| google/gemini-2.5-flash |            0.9   |             0.167 |          0.567 |           0.067 |
| google/gemma-4-31b-it   |            0.75  |             0.117 |          0.333 |           0.217 |
| qwen/qwen3.7-max        |            1.333 |             0.167 |          0.183 |           0.767 |

- `qwen/qwen3.7-max` produced the most `length_fallback` items (18/60 = 30.0%) and the highest mean `fallback_count`.
- `google/gemma-4-31b-it` had the cleanest status profile: 40/60 `generated` (66.7%).
- `google/gemini-2.5-flash` sits in the middle but contributed heavily to `partial` (25/60 = 41.7%).

### 4b. Status by variant

| variant                   |   generated |   length_fallback |   partial |   All |
|:--------------------------|------------:|------------------:|----------:|------:|
| adversarial-hard-negative |          12 |                19 |        14 |    45 |
| adversarial-length-locked |          27 |                 9 |         9 |    45 |
| overgenerate-select       |          32 |                 1 |        12 |    45 |
| taxonomy-guided           |          30 |                 0 |        15 |    45 |
| All                       |         101 |                29 |        50 |   180 |

**Mean replacements by variant:**

| variant                   |   fallback_count |   length_replaced |   nli_replaced |   leak_replaced |
|:--------------------------|-----------------:|------------------:|---------------:|----------------:|
| adversarial-hard-negative |            1.956 |             0.267 |          0.644 |           0.844 |
| adversarial-length-locked |            1.067 |             0.156 |          0.267 |           0.489 |
| overgenerate-select       |            0.467 |             0.089 |          0.289 |           0.022 |
| taxonomy-guided           |            0.489 |             0.089 |          0.244 |           0.044 |

- `adversarial-hard-negative` is the most troubled variant: only 12/45 `generated` (26.7%) and 19/45 `length_fallback` (42.2%).
- `overgenerate-select` and `taxonomy-guided` are the cleanest, with 32/45 and 30/45 fully `generated`, respectively.
- `adversarial-length-locked` produced a moderate level of `length_fallback` (9/45 = 20.0%).

### 4c. Status by language

| language   |   generated |   length_fallback |   partial |   All |
|:-----------|------------:|------------------:|----------:|------:|
| Arabic     |          25 |                14 |        21 |    60 |
| English    |          48 |                 4 |         8 |    60 |
| Yoruba     |          28 |                11 |        21 |    60 |
| All        |         101 |                29 |        50 |   180 |

- English is the easiest: 48/60 fully `generated` (80.0%).
- Arabic and Yoruba are comparable and much harder: only ~42% Arabic and ~47% Yoruba fully `generated`, with Arabic leaning toward `length_fallback` and Yoruba toward `partial`.

---

## 5. Problematic items

### 5a. Highest fallback counts (≥3)

There are **29** MCQs with `fallback_count ≥ 3`. The top 10:

| mcq_id | generator_model | variant | language | status | fallback_count | length | NLI | leak |
|---|---|---|---|---|---|---|---:|---:|
| google_gemma-4-31b-it_adversarial-length-locked_Arabic_3 | google/gemma-4-31b-it | adversarial-length-locked | Arabic | length_fallback | 6 | 1 | 1 | 3 |
| qwen_qwen3.7-max_adversarial-hard-negative_Arabic_4 | qwen/qwen3.7-max | adversarial-hard-negative | Arabic | length_fallback | 5 | 2 | 0 | 3 |
| google_gemini-2.5-flash_adversarial-hard-negative_Arabic_3 | google/gemini-2.5-flash | adversarial-hard-negative | Arabic | length_fallback | 5 | 0 | 1 | 3 |
| qwen_qwen3.7-max_adversarial-length-locked_Arabic_2 | qwen/qwen3.7-max | adversarial-length-locked | Arabic | length_fallback | 5 | 0 | 0 | 3 |
| qwen_qwen3.7-max_adversarial-hard-negative_English_9 | qwen/qwen3.7-max | adversarial-hard-negative | English | length_fallback | 5 | 1 | 0 | 3 |
| google_gemma-4-31b-it_adversarial-hard-negative_Arabic_3 | google/gemma-4-31b-it | adversarial-hard-negative | Arabic | length_fallback | 4 | 1 | 1 | 1 |
| qwen_qwen3.7-max_adversarial-hard-negative_English_6 | qwen/qwen3.7-max | adversarial-hard-negative | English | length_fallback | 4 | 0 | 0 | 3 |
| qwen_qwen3.7-max_adversarial-hard-negative_Yoruba_10 | qwen/qwen3.7-max | adversarial-hard-negative | Yoruba | length_fallback | 4 | 0 | 0 | 3 |
| qwen_qwen3.7-max_adversarial-hard-negative_Arabic_0 | qwen/qwen3.7-max | adversarial-hard-negative | Arabic | length_fallback | 4 | 0 | 1 | 2 |
| google_gemma-4-31b-it_adversarial-length-locked_Yoruba_11 | google/gemma-4-31b-it | adversarial-length-locked | Yoruba | length_fallback | 4 | 1 | 0 | 3 |


### 5b. Blocklist replacements

Only **3** raw generation rows triggered the generic-English idiom blocklist.

| mcq_id | generator_model | variant | language | status | blocklist_replaced | raw output |
|---|---|---|---|---|---:|---|
| nan | google/gemini-2.5-flash | adversarial-length-locked | Arabic | partial | 1.0 | ["One should prioritize their immediate family's needs before assisting those outside their household.", "It is important to contribute to community projects before focusing on personal matters.", "Charity begins at home, but extends equally to all members of society.", "Family obligations should always take precedence over religious duties."] |
| nan | google/gemini-2.5-flash | adversarial-hard-negative | Arabic | length_fallback | 1.0 | ["One should prioritize their family's needs over external charitable acts.", "Charity begins at home, but should not end there.", "It is important to ensure your family is well-provided for before helping others.", "You should only help others if your family has no needs at all."] |
| nan | google/gemini-2.5-flash | taxonomy-guided | Arabic | partial | 1.0 | ["One should prioritize their immediate family's needs before extending assistance to the wider community.", "It is important to contribute to your local community whenever possible.", "Charity begins at home, but it should not end there.", "Helping others is a noble act, regardless of your personal circumstances."] |


### 5c. Parse failures / hard fallbacks

`parse_fallback` and `hard_fallback` counts are **zero** in this run. All 180 MCQs reached one of `generated`, `partial`, or `length_fallback`.

---

## 6. Is the corpus fallback sampler still the main bottleneck?

**Yes.** The evidence is:

1. **43.9%** of MCQs required corpus fallback replacements (`partial` + `length_fallback`).
2. The average MCQ has **0.99** fallback replacements.
3. The dominant replacement drivers are **NLI paraphrase filtering** (`nli_replaced` = 0.36) and **correct-meaning leak filtering** (`leak_replaced` = 0.35), not length (`length_replaced` = 0.15).
4. `adversarial-hard-negative` — the variant explicitly designed to produce tempting distractors — is almost always rewritten by the filters (only 26.7% fully generated, 42.2% `length_fallback`), and Qwen 3.7 Max is disproportionately affected.
5. Blocklist and duplicate repairs are negligible, so the bottleneck is not post-processing noise; it is the **semantic/NLI/leak filters rejecting model output and the corpus sampler being asked to fill the gaps**.

**Conclusion:** The corpus-based fallback sampler remains the critical bottleneck. Replacing it with an LLM-based hard-negative generator (or a deterministic perturbation template) is still the highest-leverage next fix, especially for Arabic/Yoruba and for the `adversarial-hard-negative` variant.
