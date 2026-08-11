<!-- ⚠️ DEPRECATED — 2026-06-19. This report analyzes missing-data patterns in the old Groq-based pipeline. The active pilots use OpenRouter and a different generation/evaluation architecture. Retained for historical context only. -->

# Statistical Impact Analysis: API Failure Impact on Benchmark Validity

**Date:** 2026-06-04  
**Analyst:** Statistical Impact Analyst (Missing Data Specialist)  
**Data:** `kaggle_analysis/Last_run/extracted/evaluation_results.csv` (2100 rows)  
**Context:** 559 API failures (26.6%) on llama-3.3-70b-versatile

---

## Executive Summary

The 559 API failures (26.6%) are **infrastructure-induced missing data** (Groq HTTP 429 rate limits) concentrated entirely on `llama-3.3-70b-versatile`. Statistical tests show the missingness is **approximately random** with respect to language, style, strategy, and item difficulty. However, the effective committee shrinks from 3 to 2 models for **93.2% of ZS/FS items**, which materially weakens any claim of a "3-model committee." The core S1 vs S2 comparison remains statistically viable (McNemar p<0.001 with 409 discordant pairs), but transparent disclosure is **mandatory**.

**Critical note:** Answer choices were shuffled per model using deterministic seeds during evaluation. The `hit` column in the CSV is authoritative and correct. Analysis below uses `hit` directly.

---

## 1. Missing Data Pattern: Random or Systematic?

### Table 1: Failure Rates by Dimension

| Dimension | Category | Failures / Total | Rate | Test | p-value | Verdict |
|-----------|----------|------------------|------|------|---------|---------|
| **Language** | English | 186 / 600 | 31.0% | Chi-square | 0.936 | **Uniform** |
| | Arabic | 190 / 600 | 31.7% | | | |
| | Yoruba | 183 / 600 | 30.5% | | | |
| **Style** | Zero-shot | 268 / 900 | 29.8% | -- | -- | Balanced |
| | Few-shot | 291 / 900 | 32.3% | | | |
| **Strategy** | S1 | 280 / 900 | 31.1% | -- | -- | Balanced |
| | S2 | 279 / 900 | 31.0% | | | |
| **Difficulty** | Easy (median split) | 199 / 210 | 94.8% | Pearson r | 0.323 | **No correlation** |
| | Hard (median split) | 360 / 390 | 92.3% | | | |

*Note: Difficulty is defined as 1 - mean accuracy of the two surviving models (llama-3.1-8b + allam).*

### Key Finding
The failures show **no systematic bias** across languages, styles, strategies, or item difficulty. The missingness pattern is consistent with a Missing-At-Random (MAR) mechanism driven purely by API infrastructure (rate-limiting on the largest model), not by item content.

---

## 2. Committee Shrinkage Impact

### Table 2: Effective Committee Size Distribution

| Committee Size | All Items (n=900) | ZS/FS Items Only (n=600) | Interpretation |
|----------------|-------------------|--------------------------|----------------|
| 1 model | 300 (33.3%) | 0 (0.0%) | CoT items (only allam runs CoT) |
| 2 models | 559 (62.1%) | 559 (93.2%) | llama-3.3-70b failed; llama-3.1-8b + allam available |
| 3 models | 41 (4.6%) | 41 (6.8%) | Full committee (all models succeeded) |

### Consensus Impact
- **Items with 2-model disagreement (tie-breaker role for llama-3.3-70b):** 349 items
  - In these cases, the missing 3rd model would have been decisive for consensus.
  - With only 2 models, consensus is reduced to "both agree" (unanimity), which is stricter than majority.
- **Items where BOTH llama models failed:** 0 (0.0%)
  - llama-3.1-8b-instant had 100% uptime, so the committee never shrank to 1 model for ZS/FS.

---

## 3. Accuracy Bias

### Table 3: Accuracy Under Different Committee Assumptions

| Metric | S1 | S2 | n |
|--------|-----|-----|-----|
| Original per-evaluation accuracy (all available models) | **63.8%** | **29.7%** | 770 / 771 |
| 2-model per-evaluation (llama-3.1-8b + allam only) | 63.6% | 29.3% | 750 / 750 |
| 2-model majority-correct (item-level) | 35.0% | 35.0% | 600 / 600 |
| 3-model majority-correct (item-level, where available) | 36.2% | 36.2% | 600 / 600 |
| 2-model accuracy on items where llama-3.3-70b **succeeded** | 26.8% | -- | 41 |
| 2-model accuracy on items where llama-3.3-70b **failed** | 35.6% | -- | 559 |

### Statistical Tests

**S1 vs S2 gap preservation:**
- Per-evaluation accuracies are nearly identical with or without llama-3.3-70b (63.8% vs 63.6% for S1; 29.7% vs 29.3% for S2).
- The missing data does **not** artificially inflate or deflate the S1-S2 gap.

**Did llama-3.3-70b fail more on hard items?**
- Mean difficulty where llama succeeded: 0.598
- Mean difficulty where llama failed: 0.528
- T-test: t=0.989, p=0.323
- **Verdict:** No evidence that failures correlate with item difficulty.

**Accuracy on success vs failure items:**
- Two-proportion z-test: z=-1.216, p=0.224
- **Verdict:** No significant difference in 2-model accuracy between items where llama succeeded vs failed.

---

## 4. Statistical Power Loss

### Table 4: Effective Sample Size

| Analysis | Intended n | Effective n | Retention |
|----------|-----------|-------------|-----------|
| Full 3-model ZS/FS evaluations | 900 | 41 item-instances | 4.6% |
| 2-model ZS/FS evaluations | -- | 559 item-instances | 93.2% |
| Per-language per-strategy | ~100 | ~85 | ~85% |
| McNemar paired S1-vs-S2 | ~1500 | 754 pairs | 50.3% |

### McNemar's Test Power
- **Discordant pairs:** 409 (b=333 S1-only correct, c=76 S2-only correct)
- **Asymmetry ratio:** 4.4:1 (S1 correct >> S2 correct)
- **Power assessment:** With n=409 discordant pairs, McNemar has ample power to detect the observed difference at alpha=0.05. The highly asymmetric discordant ratio (4.4:1) makes the result robust even with reduced sample size.
- **Confidence intervals:** Standard binomial/Wald CIs remain valid under MAR. The 26.6% missingness widens CIs by approximately 8-10% relative to full data.

---

## 5. Publication Risk Assessment

### 5a. Can the paper claim "3-model committee"?

**VERDICT: NO** -- not without major qualification.

Evidence:
- llama-3.3-70b-versatile had 559/700 possible ZS/FS evaluations fail (**79.9% failure rate**).
- For **93.2%** of intended 3-model items, the committee was effectively 2 models.
- The largest/most capable model is systematically underrepresented.

### 5b. Recommended Transparent Reporting

**Option A (Preferred):**
> "We evaluate using a 2-model primary committee (llama-3.1-8b-instant and allam-2-7b), with a third model (llama-3.3-70b-versatile) providing supplementary evaluations where API availability permitted (20.1% coverage)."

**Option B (Detailed):**
> "Committee evaluations were obtained for 1541/2100 intended model-instance pairs (73.4%). The primary committee consists of llama-3.1-8b-instant and allam-2-7b (both 100% coverage). A third model, llama-3.3-70b-versatile, experienced 79.9% API failure due to rate limiting and is included as available in sensitivity analyses."

### 5c. Suggested Disclosure Table for Paper

```
+-------------------------------------+----------+----------+----------+
| Model                               | S1 Evals | S2 Evals | Failure  |
+-------------------------------------+----------+----------+----------+
| llama-3.3-70b-versatile             | 20/350   | 21/350   | 94.3%    |
| llama-3.1-8b-instant                | 300/300  | 300/300  | 0.0%     |
| allam-2-7b                          | 450/450  | 450/450  | 0.0%     |
| CoT (allam-2-7b only)               | 150/150  | 150/150  | 0.0%     |
+-------------------------------------+----------+----------+----------+
```

**Required disclosures:**
1. Exact failure count and rate by model.
2. Nature of failure: API rate limiting (HTTP 429), not model error.
3. Impact on effective sample size per analysis.
4. Sensitivity analysis: results with vs without the affected model.
5. Missing data mechanism: MAR (infrastructure-driven, independent of item content).
6. **Per-model answer shuffling was used to control position bias; this must be disclosed in methods.**

### 5d. Key Risks to Validity

| Risk | Severity | Mitigation |
|------|----------|------------|
| Overstating committee robustness | HIGH | Report as 2-model primary + 1-model supplementary |
| Biased S2 performance estimate | LOW | Sensitivity analysis shows no bias; failures are random |
| Cross-lingual comparisons underpowered | MODERATE | Report exact n per comparison; use exact binomial CIs |
| Reviewer rejection due to >25% missing data | MODERATE | Proactive transparency + sensitivity analyses |

---

## 6. Final Verdict

**BIAS ASSESSMENT: MODERATE CONCERN — MANAGEABLE WITH TRANSPARENCY**

The 559 API failures introduce structural missingness that:

1. **DOES** appear to be roughly random across languages, styles, and strategies.
2. **DOES NOT** appear correlated with item difficulty (infrastructure failures).
3. **DOES** reduce the committee from 3→2 models for ~93% of ZS/FS items.
4. **DOES NOT** fatally undermine the core S1 vs S2 comparison (McNemar p<0.001 with 409 discordant pairs remains robust).

### Bottom Line

| Recommendation | Status |
|----------------|--------|
| Paper CAN proceed | ✅ Yes, with transparent disclosure |
| Claim "3-model committee" without qualification | ❌ No |
| Rerun with better API key rotation | 🔄 Ideal, but not strictly required |
| Include sensitivity analyses (2-model vs 3-model) | ✅ Mandatory |
| Disclose per-model answer shuffling | ✅ Mandatory |
| Report exact n for every subgroup analysis | ✅ Mandatory |

---

*Analysis script: `kaggle_analysis/missing_data_impact_analysis_v2.py`*  
*Raw output: `kaggle_analysis/missing_data_impact_report.txt`*
