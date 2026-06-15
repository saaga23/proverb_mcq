# Cross-Verification Report

**Documents reviewed:**
- `docs/ProverbGap_Paper_Draft.md`
- `docs/ProverbGap_Mentor_Briefing.md`
- `memory.md`
- `kaggle_analysis/Last_run/FINAL_AUDIT_v434.md`

**Source files verified:**
- `kaggle_analysis/Last_run/evaluation_results.csv` (1,500 API evaluations)
- `kaggle_analysis/Last_run/encoder_results.csv` (1,200 encoder evaluations)
- `kaggle_analysis/Last_run/mcqs_strategy1.csv` (150 MCQs)
- `kaggle_analysis/Last_run/mcqs_strategy2.csv` (150 MCQs)
- `kaggle_analysis/Last_run/mcq-pass-shortcut.log` (v4.3.4 execution log)
- `original_data/*.csv` (proverb source files)

---

## Contradictions Found

### 1. Consensus table mislabels "any unanimous" as "unanimous correct"
**Location:** Paper Draft §5.8, Table 5.8  
**Issue:** The table reports 82.0% (369/450) for S1 and 68.4% (308/450) for S2 under the heading **"Unanimous Correct"**, with "Unanimous Wrong" shown as `--` (0%).

**Source verification:** Using the exact consensus logic from `proverbgap_kaggle_final.py` on `evaluation_results.csv`:

| Strategy | Unanimous Correct | Unanimous Wrong | Split |
|----------|-------------------|-----------------|-------|
| S1 | **78.2%** (352/450) | **3.8%** (17/450) | 18.0% (81/450) |
| S2 | **45.8%** (206/450) | **22.7%** (102/450) | 31.6% (142/450) |

The paper’s 82.0% and 68.4% actually correspond to **any unanimous decision** (correct *or* wrong), not unanimous correct. The "Unanimous Wrong" column is falsely reported as zero when the source data shows non-trivial rates, especially for S2 (22.7%).

**Severity:** High — misrepresents a key quality metric.

### 2. Mentor Briefing cites outdated Yoruba fallback rate without run attribution
**Location:** Mentor Briefing, Chapter 4 ("Strategy 2 Crisis")  
**Issue:** The mentor doc states "43.3% of Yoruba S2 items fell back to placeholder distractors." However, the v4.3.4 source data shows **36.0%** (18/50) Yoruba fallback. The 43.3% figure comes from an earlier run (v4.2-era) but is presented in the narrative of "what went wrong" without clear temporal distinction from the v4.3.4 results in Part 2.

**Severity:** Medium — creates ambiguity about which run the number belongs to.

---

## Unsupported Claims

### 1. Dataset size (7,172 proverbs) is unverifiable from repository source files
**Location:** Paper §3.1, Mentor Briefing Chapter 1  
**Issue:** Both documents claim 7,172 proverbs across six languages (English 2,278; Arabic 913; Yoruba 3,931; French 161; German 142; Spanish 63). The `original_data/*.csv` files in the repository are **placeholder files** (~100 rows each; 669 total). There is no verifiable source for the claimed 7,172 proverbs.

**Severity:** High — a benchmark paper must have verifiable data provenance.

### 2. Abstract omits "strict" qualifier for Strategy 2 accuracy
**Location:** Paper Abstract  
**Issue:** The abstract states "62.5% on Strategy 2" without specifying that this is the **strict** accuracy (excluding 32 hard-fallback items). The total S2 accuracy across all 750 evaluations is **62.8%** (471/750). The distinction is methodologically important because fallback items use generic placeholder distractors ("Incorrect alternative," etc.) and are not true Strategy 2 items.

**Severity:** Medium — the abstract’s brevity obscures a key methodological distinction that is properly documented in the results table.

### 3. Negative results in the abstract are conflated with the N=150 pilot
**Location:** Paper Abstract  
**Issue:** The abstract says "Our N=150 pilot... We report extensive negative results---including same-family model exploitation, reasoning collapse under chain-of-thought prompting, and catastrophic API infrastructure failures."

- **Same-family exploitation** was observed in v4.3.1/v4.3.2 (Meta generator + Meta evaluator) and eliminated before v4.3.4 by switching to qwen3-32b.
- **CoT reasoning collapse** (23/24 NaN predictions) was observed in v4.3.2 and prevented in v4.3.4 by skipping CoT for llama-4-maverick.
- **Catastrophic API meltdown** refers primarily to the v4.3.3 infrastructure cascade (S1 collapsed to 24.2%).

These negative results informed the final protocol but were **not observed in the v4.3.4 N=150 pilot itself**. The abstract’s phrasing bundles them under the pilot.

**Severity:** Medium — reviewers may ask why the reported pilot contains failures that the methodology already fixed.

### 4. "23 of 24 NaN predictions" cited as v4.3.4 methodology justification
**Location:** Paper §4.5  
**Issue:** The paper cites "23 of 24 NaN predictions, 29% accuracy" to justify skipping CoT for llama-4-maverick. In the v4.3.4 source data, llama-4-maverick has **zero CoT evaluations** (the style is skipped entirely). The cited evidence is from v4.3.2, not the reported run. While it is reasonable to use prior observations to justify protocol choices, the paper does not explicitly flag this as pre-pilot evidence.

**Severity:** Low — methodologically defensible but lacks transparency about run provenance.

---

## Gaps

### 1. Mentor doc missing "Embedding-Based Distractor Diversity" phase
**Location:** Paper §7.6 vs. Mentor Briefing Part 3  
**Issue:** The paper’s "Remaining 10%" lists six items. The mentor doc’s "Next Phase" lists five phases, omitting **"Embedding-Based Distractor Diversity"** (Paper §7.6). Since the mentor doc is intended to give stakeholders the "big picture," the omission of one planned workstream is a gap.

### 2. Allam-2-7b leakage analysis omits error-excluded calculation
**Location:** Paper §5.4  
**Issue:** The paper applies the leakage heuristic (S1 ≥ 95% AND drop ≥ 20pp) to all evaluations including API errors, yielding "No signal" for allam-2-7b (82.9% S1, 32.9pp drop). However, excluding API errors:
- Allam S1 accuracy: **98.9%** (373/377 successful evaluations)
- Allam S2 accuracy: **74.5%** (225/302 successful evaluations)
- Drop: **24.4pp**

This **would** trigger the HIGH leakage threshold. The paper attributes the drop to Groq rate-limiting but does not present the error-excluded analysis, which is a material omission.

### 3. No source file or checksum for the full proverb collection
**Location:** Paper §3.1, DATASET_CARD.md  
**Issue:** Although `DATASET_CARD.md` documents provenance, the actual repository contains only placeholder CSVs. A reviewer-accessible URL or SHA checksum for the full 7,172-proverb dataset is not provided in any of the reviewed documents.

### 4. Per-model position bias p-values are exactly 1.000
**Location:** Paper §5.6, `mcq-pass-shortcut.log` lines 546–549  
**Issue:** The paper reports stratified per-model chi-squared tests with **p = 1.0000** for both models and both strategies. A p-value of exactly 1.000 is highly unusual for real data and suggests the test may be underpowered or degenerate due to small cell counts per model-stratum. The paper does not discuss this oddity or provide contingency tables.

---

## Recommendations

1. **Fix Table 5.8 (Consensus):** Replace the mislabeled "Unanimous Correct" column with three columns: "Unanimous Correct," "Unanimous Wrong," and "Split," using the verified figures from the source data (78.2% / 3.8% / 18.0% for S1; 45.8% / 22.7% / 31.6% for S2).

2. **Clarify Abstract:** Change "62.5% on Strategy 2" to "62.5% on Strategy 2 (strict, non-fallback)" or add a parenthetical note.

3. **Disambiguate negative results:** Add a sentence in §6.2 or the abstract distinguishing negative results observed in **iterative development** (same-family exploitation, CoT collapse, v4.3.3 meltdown) from those observed in the **final v4.3.4 pilot** (API fragility, Yoruba generation stress).

4. **Add missing phase to Mentor doc:** Either add "Embedding-Based Distractor Diversity" to Part 3 or remove it from the paper’s "Remaining 10%" if it is no longer planned.

5. **Provide verifiable data artifact:** Replace placeholder CSVs with the actual dataset, or provide a permanent URL / SHA-256 checksum in `DATASET_CARD.md` and the paper.

6. **Report allam leakage analysis transparently:** Present both the all-evaluations heuristic ("No signal") and the error-excluded heuristic ("HIGH risk") in §5.4, with a brief discussion of why API errors confound the metric.

7. **Explain p = 1.000 position bias tests:** Add a footnote or appendix table showing the per-model position-bias contingency tables, or switch to a more appropriate test if cell counts are too small.

---

## Overall Verdict

**Status: CONDITIONALLY SOLID — requires corrections before submission.**

The **core empirical claims** of the v4.3.4 pilot are **well-supported** by the source files:
- S1 accuracy 86.8% (651/750) ✓
- S2 strict accuracy 62.5% (369/590) ✓
- S2 fallback rate 21.3% (32/150) ✓
- Per-language breakdown (English 97.6%/71.3%; Arabic 92.8%/65.5%; Yoruba 70.0%/46.2%) ✓
- Per-model breakdown (llama-4-maverick 92.7%/82.0%; allam-2-7b 82.9%/50.0%) ✓
- Per-style breakdown, encoder baselines, McNemar’s test, bootstrap CIs, and position bias p-values all match the execution log and CSVs ✓
- Paper does **not** mention the $50 budget ✓
- Mentor doc does **not** contradict the paper’s primary methodology or results ✓
- "Remaining 10%" and "Next Phase" are **mostly aligned** (5 of 6 items match) ✓

However, **three issues must be fixed**:
1. The consensus table contains a **labeling error** that misrepresents unanimous correct by ~4–23 percentage points.
2. The **dataset size claim** (7,172 proverbs) is **unverifiable** from the repository.
3. The **abstract conflates** negative results from earlier iterations with the final pilot, risking reviewer pushback.

Once these are corrected, the cross-verification between documents and source files will be clean.
