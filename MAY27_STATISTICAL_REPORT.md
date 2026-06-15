# Statistical Analysis Report: May 27, 2026 Run
## File: kaggle_analysis/Last_run/evaluation_results.csv

Analyzed on its own merits. No comparison to other runs or documents.

---

## 1. DATA CLEANING

| Metric | Count |
|--------|-------|
| Total rows in CSV | **2,093** |
| Valid evaluations (pred in A/B/C/D) | **1,335** |
| API failures (pred is NaN) | **758** |
| Other invalid preds | **0** |

Valid row breakdown: S1=794, S2=541.

---

## 2. ACCURACY STATISTICS (clean data only)

Bootstrap 95% CIs computed with 10,000 resamples.

### Overall per strategy
| Strategy | Correct/Total | Accuracy | 95% CI |
|----------|---------------|----------|--------|
| S1 | 577/794 | 72.67% | [69.52%, 75.69%] |
| S2 | 364/541 | 67.28% | [63.40%, 71.16%] |

### Per-language per strategy
| Strategy | Language | Correct/Total | Accuracy | 95% CI |
|----------|----------|---------------|----------|--------|
| S1 | English | 328/343 | 95.63% | [93.29%, 97.67%] |
| S1 | Arabic | 196/298 | 65.77% | [60.40%, 71.14%] |
| S1 | Yoruba | 53/153 | 34.64% | [27.45%, 42.48%] |
| S2 | English | 218/322 | 67.70% | [62.73%, 72.67%] |
| S2 | Arabic | 146/219 | 66.67% | [60.27%, 72.60%] |
| S2 | Yoruba | 0/0 | -- | -- |

### Per-model per strategy
| Strategy | Model | Correct/Total | Accuracy | 95% CI |
|----------|-------|---------------|----------|--------|
| S1 | allam-2-7b | 231/306 | 75.49% | [70.59%, 80.07%] |
| S1 | llama-3.1-8b | 156/244 | 63.93% | [57.79%, 70.08%] |
| S1 | llama-3.3-70b | 190/244 | 77.87% | [72.54%, 82.79%] |
| S2 | allam-2-7b | 123/205 | 60.00% | [53.17%, 66.83%] |
| S2 | llama-3.1-8b | 114/168 | 67.86% | [60.71%, 75.00%] |
| S2 | llama-3.3-70b | 127/168 | 75.60% | [69.05%, 82.14%] |

### Per-style per strategy
| Strategy | Style | Correct/Total | Accuracy | 95% CI |
|----------|-------|---------------|----------|--------|
| S1 | zero-shot | 258/364 | 70.88% | [66.21%, 75.55%] |
| S1 | few-shot | 231/314 | 73.57% | [68.79%, 78.34%] |
| S1 | cot | 88/116 | 75.86% | [68.10%, 83.62%] |
| S2 | zero-shot | 173/251 | 68.92% | [62.95%, 74.50%] |
| S2 | few-shot | 145/208 | 69.71% | [63.46%, 75.96%] |
| S2 | cot | 46/82 | 56.10% | [45.12%, 67.07%] |

---

## 3. STATISTICAL TEST VERIFICATION

### McNemar test (S1 vs S2)

The log reports a table summing to 1,043 pairs: y1=1/y2=1=300, y1=1/y2=0=277, y1=0/y2=1=62, y1=0/y2=0=404, chi2=135.091, p<0.0001.

Our recalculation from the clean CSV yields different results:

| Pairing method | N pairs | y1y2 | y1n2 | n1y2 | n1n2 | chi2 | p-value |
|----------------|---------|------|------|------|------|------|---------|
| A. Per-evaluation row | 523 | 300 | 127 | 51 | 45 | 31.601 | <0.0001 |
| B. Per-item, majority | 83 | 49 | 19 | 9 | 6 | 2.893 | 0.089 |
| C. Per-item, any correct | 83 | 72 | 7 | 3 | 1 | 0.900 | 0.343 |

The log N=1,043 cannot be reproduced from this CSV under any pairing definition. The log was computed on a different dataset.

### Per-language McNemar (Bonferroni alpha=0.017)

| Language | N pairs | y1y2 | y1n2 | n1y2 | n1n2 | chi2 | p-value | Significant? |
|----------|---------|------|------|------|------|------|---------|--------------|
| English | 316 | 213 | 91 | 3 | 9 | 80.521 | <0.0001 | Yes |
| Arabic | 207 | 87 | 36 | 48 | 36 | 1.440 | 0.230 | No |
| Yoruba | 0 | -- | -- | -- | -- | -- | -- | No data |

These do not match the log values (English 104.4, Arabic 14.3, Yoruba 51.0).

### Position bias chi-square

| Source | Strategy | chi2 | p-value |
|--------|----------|------|---------|
| Log | S1 | 2.65 | 0.4482 |
| Log | S2 | 2.59 | 0.4586 |
| Our data | S1 | 4.497 | 0.2126 |
| Our data | S2 | 8.847 | 0.0314 |

The log statistics are irreconcilable with this CSV. From clean data, S2 shows significant position dependence (p=0.031), with position C at 77.5% vs position B at 61.5%.

---

## 4. DATA ANOMALIES

### Distribution of correct answer positions

| Strategy | A | B | C | D | chi2_uniform | p-value |
|----------|---|---|---|---|--------------|---------|
| S1 | 203 | 207 | 188 | 196 | 1.053 | 0.789 |
| S2 | 150 | 130 | 129 | 132 | 2.179 | 0.536 |

The correct-answer distribution is uniform for both strategies (no construction bias).

### Accuracy by position

| Strategy | Pos A | Pos B | Pos C | Pos D |
|----------|-------|-------|-------|-------|
| S1 | 78.3% | 71.0% | 71.3% | 69.9% |
| S2 | 64.0% | 61.5% | 77.5% | 66.7% |

S2 shows a significant accuracy spike at position C and dip at B.

### Model position preference (prediction distribution uniformity)

| Strategy | Model | chi2 | p-value | Interpretation |
|----------|-------|------|---------|----------------|
| S1 | allam-2-7b | 6.288 | 0.098 | Marginal |
| S1 | llama-3.1-8b | 9.410 | 0.024 | Non-uniform |
| S1 | llama-3.3-70b | 6.164 | 0.104 | Not significant |
| S2 | allam-2-7b | 12.463 | 0.006 | Non-uniform |
| S2 | llama-3.1-8b | 3.952 | 0.267 | Not significant |
| S2 | llama-3.3-70b | 10.476 | 0.015 | Non-uniform |

Two models show significant position preferences in their predictions.

### Style accuracy comparison

- S1: ANOVA F=0.654, p=0.520 -> no significant style differences.
- S2: ANOVA F=2.776, p=0.063 -> marginally significant; CoT lags behind zero-shot and few-shot.

---

## 5. MISSING DATA ANALYSIS

### Where is data missing?

Out of 54 expected combinations (3 models x 3 styles x 2 strategies x 3 languages), every combination has some issue:

| Issue | Combos affected | Rows affected |
|-------|-----------------|---------------|
| Llama CoT completely absent | 12 combos | 600 rows missing from CSV entirely |
| Yoruba S2 all NaN | 6 combos | 300 rows present but all NaN |
| allam-2-7b heavy NaNs | 12 combos | 386 NaNs |
| English S1 one item short | 9 combos | 9 fewer rows than expected |

### Missing data is systematic, not random

| Factor | NaN count | Association test | Result |
|--------|-----------|------------------|--------|
| Strategy | S1: 249, S2: 509 | -- | S2 is 2x more failure-prone |
| Language | EN: 28, AR: 183, YO: 547 | -- | Yoruba dominates failures |
| Style | CoT: 101, FS: 375, ZS: 282 | chi2=0.778, p=0.378 | Similar rates BUT Llama CoT rows are completely missing from CSV |
| Model | allam: 386, llama-8b: 186, llama-70b: 186 | -- | allam has 2x more NaNs |

All NaN rows carry errors of the form All providers failed for <model>: ... -- these are API rate-limit or service failures, not model refusals.

### Impact on conclusions

1. Yoruba S2 is unmeasurable. Zero valid evaluations mean any claim about S2 Yoruba accuracy is impossible from this file.
2. CoT results are unrepresentative. Only allam-2-7b has CoT data; Llama models have none. The apparent CoT drop cannot be generalized.
3. S2 is under-sampled. Valid S2 rows (541) are only 68% of valid S1 rows (794), making direct comparisons underpowered.
4. English S1 is inflated. With 95.6% accuracy but only 343 valid rows (and missing the leaked item), the ceiling effect is severe.

---

## 6. S2 FALLBACK ANALYSIS

- S2 valid rows with fallback=True: 0 / 541
- S2 valid rows with fallback=False: 541 / 541

Consistent with generation log: The log states S2: 150 MCQs (0 hard-fallbacks = 0.0%, 0 best-effort = 0.0%). The evaluation data confirms zero fallback items.

### Is S2 accuracy genuinely lower than S1?

| Strategy | Overall accuracy | Driver |
|----------|-----------------|--------|
| S1 | 72.67% | English dominates at 95.6% |
| S2 | 67.28% | English collapses to 67.7%; Arabic stays flat; Yoruba absent |

Yes, S2 is lower in this data, but the comparison is confounded:

- English S1->S2 drop: 95.6% -> 67.7% (-27.9 pp). This is the single largest driver of the overall S1>S2 gap.
- Arabic S1->S2: 65.8% -> 66.7% (+0.9 pp). Essentially flat.
- Yoruba S2: Missing entirely. If Yoruba S2 had performed like S1 (~35%), including it would likely widen the S1>S2 gap.

Conclusion: The 5.4 pp overall S1 advantage is genuine within the subset of data that was successfully evaluated, but it is not a balanced comparison. The absence of Yoruba S2 means the S2 average is artificially inflated relative to S1 (missing the lowest-performing language), yet S2 still underperforms because of the massive English collapse.

---

## EXECUTIVE SUMMARY: WHAT THE DATA CAN AND CANNOT SUPPORT

### What it CAN support
- S1 outperforms S2 on English items by a large margin.
- Arabic accuracy is similar across S1 and S2.
- allam-2-7b suffers the largest S1->S2 drop among the three models.
- S2 exhibits significant position bias (position C is advantaged).
- API failures are systematic: concentrated in Yoruba, S2, and allam-2-7b.

### What it CANNOT support
- Any claim about Yoruba S2 performance -- there are zero valid evaluations.
- Any claim about Llama CoT performance -- these rows are completely absent from the CSV.
- The exact McNemar chi2=135.1 reported in the log -- that figure was computed on a different dataset (~1,043 pairs vs. 523 pairs in this file).
- The position-bias p-values from the log -- our recalculation yields different numbers (S2 is significant, not non-significant).
- A balanced S1 vs S2 comparison -- S2 is missing an entire language and ~36% of its expected evaluations.

### Data quality verdict
The CSV contains 1,335 valid evaluations out of 2,093 rows (63.8% usable). The missing 758 rows are not missing at random; they cluster by language (Yoruba), strategy (S2), and style/model (Llama CoT, allam generally). Any statistical conclusion drawn from this file must be hedged with explicit caveats about selective missingness and reduced power.
