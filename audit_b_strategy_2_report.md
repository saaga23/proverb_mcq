# Task B (Cultural Meaning) Audit Report -- Strategy 2

**File analyzed:** `pilot_v5_audit_b_strategy_2.csv`

---

## 1. Dataset Overview

- **Total rows:** 90

| Language | Count | % of Total |
|----------|-------|------------|
| Arabic | 30 | 33.3% |
| English | 30 | 33.3% |
| Yoruba | 30 | 33.3% |

---

## 2. Per-Model Accuracy (Overall)

| Model | Hits | Total | Accuracy |
|-------|------|-------|----------|
| hit_llama-3.3-70b-versatile | 29 | 90 | 32.2% |
| hit_llama-3.1-8b-instant | 29 | 90 | 32.2% |
| hit_llama-3.2-11b-vision-preview | 0 | 90 | 0.0% |
| hit_llama-3.2-3b-preview | 0 | 90 | 0.0% |
| hit_qwen3-32b | 0 | 90 | 0.0% |
| hit_consensus | 19 | 90 | 21.1% |

---

## 3. Per-Model Accuracy by Language

### Arabic (n=30)

| Model | Hits | Total | Accuracy |
|-------|------|-------|----------|
| hit_llama-3.3-70b-versatile | 8 | 30 | 26.7% |
| hit_llama-3.1-8b-instant | 11 | 30 | 36.7% |
| hit_llama-3.2-11b-vision-preview | 0 | 30 | 0.0% |
| hit_llama-3.2-3b-preview | 0 | 30 | 0.0% |
| hit_qwen3-32b | 0 | 30 | 0.0% |
| hit_consensus | 6 | 30 | 20.0% |

### English (n=30)

| Model | Hits | Total | Accuracy |
|-------|------|-------|----------|
| hit_llama-3.3-70b-versatile | 8 | 30 | 26.7% |
| hit_llama-3.1-8b-instant | 7 | 30 | 23.3% |
| hit_llama-3.2-11b-vision-preview | 0 | 30 | 0.0% |
| hit_llama-3.2-3b-preview | 0 | 30 | 0.0% |
| hit_qwen3-32b | 0 | 30 | 0.0% |
| hit_consensus | 5 | 30 | 16.7% |

### Yoruba (n=30)

| Model | Hits | Total | Accuracy |
|-------|------|-------|----------|
| hit_llama-3.3-70b-versatile | 13 | 30 | 43.3% |
| hit_llama-3.1-8b-instant | 11 | 30 | 36.7% |
| hit_llama-3.2-11b-vision-preview | 0 | 30 | 0.0% |
| hit_llama-3.2-3b-preview | 0 | 30 | 0.0% |
| hit_qwen3-32b | 0 | 30 | 0.0% |
| hit_consensus | 8 | 30 | 26.7% |

---

## 4. Consensus Accuracy Overall & Per Language

| Language | Consensus Hits | Total | Accuracy |
|----------|----------------|-------|----------|
| Arabic | 6 | 30 | 20.0% |
| English | 5 | 30 | 16.7% |
| Yoruba | 8 | 30 | 26.7% |
| **Overall** | **19** | **90** | **21.1%** |

---

## 5. Strategy 2 vs Strategy 1 Comparison (Task B)

### Overall Model Accuracy

| Model | Strategy 1 | Strategy 2 | Change (S2 - S1) |
|-------|------------|------------|------------------|
| hit_llama-3.3-70b-versatile | 21.1% (19/90) | 32.2% (29/90) | +11.1pp |
| hit_llama-3.1-8b-instant | 22.2% (20/90) | 32.2% (29/90) | +10.0pp |
| hit_llama-3.2-11b-vision-preview | 11.1% (10/90) | 0.0% (0/90) | -11.1pp |
| hit_llama-3.2-3b-preview | 11.1% (10/90) | 0.0% (0/90) | -11.1pp |
| hit_qwen3-32b | 0.0% (0/90) | 0.0% (0/90) | +0.0pp |
| hit_consensus | 15.6% (14/90) | 21.1% (19/90) | +5.6pp |

### Consensus by Language

| Language | S1 Consensus | S2 Consensus | Change |
|----------|--------------|--------------|--------|
| Arabic | 20.0% (6/30) | 20.0% (6/30) | +0.0pp |
| English | 16.7% (5/30) | 16.7% (5/30) | +0.0pp |
| Yoruba | 10.0% (3/30) | 26.7% (8/30) | +16.7pp |

---

## 6. Strongest / Weakest Auditor

### Ranking (by overall accuracy)

| Rank | Model | Accuracy | Hits |
|------|-------|----------|------|
| 1 | hit_llama-3.3-70b-versatile | 32.2% | 29/90 |
| 2 | hit_llama-3.1-8b-instant | 32.2% | 29/90 |
| 3 | hit_llama-3.2-11b-vision-preview | 0.0% | 0/90 |
| 4 | hit_llama-3.2-3b-preview | 0.0% | 0/90 |
| 5 | hit_qwen3-32b | 0.0% | 0/90 |

- **Strongest auditor:** hit_llama-3.3-70b-versatile (32.2%)
- **Weakest auditor:** hit_qwen3-32b (0.0%)

---

## 7. Agreement & Disagreement Analysis

### Strategy 2

| Category | Count | % of Total |
|----------|-------|------------|
| Unanimous YES (all 5 models = 1) | 0 | 0.0% |
| Unanimous NO (all 5 models = 0) | 51 | 56.7% |
| Strong Disagreement (2-3 split) | 19 | 21.1% |
| Mild Disagreement (1 or 4 votes) | 20 | 22.2% |

### Strategy 1 (for comparison)

| Category | Count | % of Total |
|----------|-------|------------|
| Unanimous YES (all 5 models = 1) | 0 | 0.0% |
| Unanimous NO (all 5 models = 0) | 56 | 62.2% |
| Strong Disagreement (2-3 split) | 14 | 15.6% |
| Mild Disagreement (1 or 4 votes) | 20 | 22.2% |

---

## 8. Data Quality Issues

- **Consensus rule:** Consensus = 1 iff BOTH llama-3.3-70b AND llama-3.1-8b vote 1 (AND rule between the two largest Llama models)

- **Duplicate vote patterns:** 4 distinct patterns appear more than once

| Pattern (70b, 8b, 11b, 3b, qwen, consensus) | Occurrences |
|---------------------------------------------|-------------|
| ('0', '0', '0', '0', '0', '0') | 51 |
| ('1', '1', '0', '0', '0', '1') | 19 |
| ('0', '1', '0', '0', '0', '0') | 10 |
| ('1', '0', '0', '0', '0', '0') | 10 |

- **Zero-hit models:** hit_llama-3.2-11b-vision-preview, hit_llama-3.2-3b-preview, hit_qwen3-32b

- **Low consensus languages (<10%):** None

- **Strategy 1 consensus rule check:** AND-rule on 70b+8b matches 88/90 rows

---

## Summary Highlights

- **Dataset:** 90 items across 3 languages (English: 30, Yoruba: 30, Arabic: 30)
- **Overall consensus accuracy:** 21.1% (19/90)
- **Strongest auditor:** hit_llama-3.3-70b-versatile (32.2%)
- **Weakest auditor:** hit_qwen3-32b (0.0%)
- **Unanimous agreement:** 51 items (56.7%)
- **Strong disagreement:** 19 items (21.1%)
- **Consensus change vs Strategy 1:** +5.6 percentage points
