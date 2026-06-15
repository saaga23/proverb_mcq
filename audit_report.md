# Audit Analysis Report: pilot_v5_audit_a_strategy_1.csv

**File:** `Last_run/results_unzipped/run_20260518_221600_879404/pilot_v5_audit_a_strategy_1.csv`

## 1. Dataset Overview
- **Total rows:** 90
- **Total columns:** 8 (`lang`, 5 model hit columns, 1 consensus column)

### Breakdown by Language
| Language | Count | Proportion |
|----------|-------|------------|
| Arabic | 30 | 33.3% |
| English | 30 | 33.3% |
| Yoruba | 30 | 33.3% |

## 2. Per-Model Accuracy

### Overall Accuracy (Mean Hit Rate)
| Model | Accuracy | Hits / Total |
|-------|----------|--------------|
| llama-3.3-70b-versatile | 0.2889 (28.89%) | 25 / 90 |
| llama-3.1-8b-instant | 0.3222 (32.22%) | 29 / 90 |
| llama-3.2-11b-vision-preview | 0.1222 (12.22%) | 11 / 90 |
| llama-3.2-3b-preview | 0.1000 (10.00%) | 9 / 90 |
| qwen3-32b | 0.0000 (0.00%) | 0 / 90 |

### Per-Language Accuracy
| Language | llama-3.3-70b-versatile | llama-3.1-8b-instant | llama-3.2-11b-vision-preview | llama-3.2-3b-preview | qwen3-32b |
|----------|----------|----------|----------|----------|----------|
| Arabic | 0.2333 | 0.4000 | 0.0000 | 0.0000 | 0.0000 |
| English | 0.3333 | 0.2000 | 0.2000 | 0.1667 | 0.0000 |
| Yoruba | 0.3000 | 0.3667 | 0.1667 | 0.1333 | 0.0000 |

## 3. Consensus Accuracy

### Overall Consensus Accuracy
- **Consensus accuracy:** 0.1667 (16.67%)
- **Consensus hits:** 15 / 90

### Per-Language Consensus Accuracy
| Language | Consensus Accuracy | Hits / Total |
|----------|--------------------|--------------|
| Arabic | 0.2000 (20.00%) | 6 / 30 |
| English | 0.2000 (20.00%) | 6 / 30 |
| Yoruba | 0.1000 (10.00%) | 3 / 30 |

## 4. Correlation Between Individual Model Accuracy and Consensus

### Row-Level Pearson Correlation (each row's model hit vs consensus hit)
| Model | Pearson r | p-value | Interpretation |
|-------|-----------|---------|----------------|
| llama-3.3-70b-versatile | 0.5701 | 0.0000 | Moderate positive |
| llama-3.1-8b-instant | 0.5210 | 0.0000 | Moderate positive |
| llama-3.2-11b-vision-preview | 0.5613 | 0.0000 | Moderate positive |
| llama-3.2-3b-preview | 0.6460 | 0.0000 | Moderate positive |
| qwen3-32b | nan | nan | Very weak / none |

### Language-Level Pearson Correlation (per-language accuracy vs consensus)
| Model | Pearson r | p-value |
|-------|-----------|---------|
| llama-3.3-70b-versatile | -0.1890 | 0.8790 |
| llama-3.1-8b-instant | -0.3592 | 0.7661 |
| llama-3.2-11b-vision-preview | -0.3592 | 0.7661 |
| llama-3.2-3b-preview | -0.3273 | 0.7877 |
| qwen3-32b | nan | nan |

## 5. Strongest / Weakest Auditor

### Ranking by Total Hits
| Rank | Model | Total Hits | Accuracy |
|------|-------|------------|----------|
| 1 | llama-3.1-8b-instant | 29 | 0.3222 (32.22%) |
| 2 | llama-3.3-70b-versatile | 26 | 0.2889 (28.89%) |
| 3 | llama-3.2-11b-vision-preview | 11 | 0.1222 (12.22%) |
| 4 | llama-3.2-3b-preview | 9 | 0.1000 (10.00%) |
| 5 | qwen3-32b | 0 | 0.0000 (0.00%) |

- **Strongest auditor:** llama-3.1-8b-instant (29 hits, 32.22%)
- **Weakest auditor:** qwen3-32b (0 hits, 0.00%)

## 6. Items Where All Models Agree

- **All models agree (all hit=1):** 0 items
- **All models agree (all hit=0):** 45 items
- **Total unanimous items:** 45 / 90 (50.00%)

### All hit=1 Breakdown by Language
| Language | Count |
|----------|-------|
| Arabic | 0 |
| English | 0 |
| Yoruba | 0 |

### All hit=0 Breakdown by Language
| Language | Count |
|----------|-------|
| Arabic | 17 |
| English | 17 |
| Yoruba | 11 |

**Interpretation:**
- Unanimous `hit=0` items (45) are cases where every model (and consensus) agrees the literal translation is incorrect or poor â€” these are **clear failures** likely representing genuinely bad candidates.
- Unanimous `hit=1` items (0) are cases where every model agrees the literal translation is correct â€” these are **clear successes** representing high-quality candidates.
- The high number of unanimous `hit=0` items relative to `hit=1` suggests the dataset contains many obviously incorrect translations, or that models are conservative in assigning hits.

## 7. Items Where Models Strongly Disagree

- **Items with disagreement (1â€“4 models say hit):** 45 / 90 (50.00%)

### Disagreement by Number of Models Voting Hit
| Models Voting Hit | Count |
|-------------------|-------|
| 1 | 27 |
| 2 | 10 |
| 3 | 4 |
| 4 | 4 |

### Disagreement Breakdown by Language
| Language | Disagreeing Items |
|----------|-------------------|
| Arabic | 13 |
| English | 13 |
| Yoruba | 19 |

**Interpretation:**
- Disagreement indicates **ambiguous or borderline items** where some models find the translation acceptable and others do not.
- Items with exactly 1 model voting hit are outliers â€” possibly false positives from a single lenient model.
- Items with 2â€“4 models voting hit are genuinely contested cases where consensus becomes valuable.

### Consensus vs Model Majority
- **Items where consensus differs from simple majority (>=3 models):** 7
| lang | model_sum | consensus |
|------|-----------|-----------|
| English | 2 | 1 |
| Arabic | 2 | 1 |
| Arabic | 2 | 1 |
| Arabic | 2 | 1 |
| Arabic | 2 | 1 |
| Arabic | 2 | 1 |
| Arabic | 2 | 1 |

## 8. Data Quality Issues

### Missing Values
| Column | Missing Count |
|--------|---------------|
| lang | 0 |
| hit_llama-3.3-70b-versatile | 0 |
| hit_llama-3.1-8b-instant | 0 |
| hit_llama-3.2-11b-vision-preview | 0 |
| hit_llama-3.2-3b-preview | 0 |
| hit_qwen3-32b | 0 |
| hit_consensus | 0 |
| model_sum | 0 |
*No missing values detected.*

### Unexpected Values
*No unexpected values detected. All hit columns contain only 0 or 1.*

### Column Data Types
| Column | Dtype |
|--------|-------|
| lang | object |
| hit_llama-3.3-70b-versatile | int64 |
| hit_llama-3.1-8b-instant | int64 |
| hit_llama-3.2-11b-vision-preview | int64 |
| hit_llama-3.2-3b-preview | int64 |
| hit_qwen3-32b | int64 |
| hit_consensus | int64 |
| model_sum | int64 |
| model_majority | int64 |

---

## Summary

| Metric | Value |
|--------|-------|
| Total rows | 90 |
| Languages | Arabic, English, Yoruba |
| Strongest model | llama-3.1-8b-instant (32.22%) |
| Weakest model | qwen3-32b (0.00%) |
| Consensus accuracy | 0.1667 (16.67%) |
| Unanimous items | 45 (50.00%) |
| Disagreeing items | 45 (50.00%) |

