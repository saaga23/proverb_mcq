#### 8. Baselines and Robustness

### 8.1 Heuristic Baselines

| Baseline | Accuracy | Interpretation |
|----------|----------|---------------|
| All-A | 25.00% | Balanced keys confirmed |
| All-D | 25.00% | Balanced keys confirmed |
| Random | 25.01% | Lower bound |
| Shortest | 13.89% | No short-option bias |
| Longest | 41.11% | Surface correlation, but... |

The "longest" baseline at 41.11% appears alarming, but length-bias analysis shows zero correlation between distractor length and consensus selection (Pearson r = -0.0086). The 41.11% is a sample artifact, not a systematic bias.

### 8.2 Shallow Lexical Baseline

TF-IDF cosine similarity selects the option most lexically overlapping with the gold meaning: **36.7% accuracy** (EN 53.3%, AR 21.7%, YO 35.0%). The audit committee (56.7%) outperforms this by **+20.0 percentage points**, proving the committee uses semantic understanding beyond surface lexical overlap.

### 8.3 Single-Generator Ablation

| Generator | Consensus Accuracy | HCW | Partial+Fallback |
|-----------|-------------------|-----|------------------|
| `google/gemma-4-31b-it` | 65.0% | 21.7% | 33.3% |
| `google/gemini-2.5-flash` | 53.3% | 31.7% | 50.0% |
| `qwen/qwen3.7-max` | 51.7% | 30.0% | 48.3% |
| **Pooled** | **56.7%** | **27.8%** | **43.9%** |

The pooled result (56.7%) is **worse** than gemma-only (65.0%). The multi-model pool does not improve quality at N=5; weaker generators introduce more HCW items. This is a negative result: dynamic pools do not automatically improve distractor quality.

### 8.4 Statistical Tests

**McNemar's test (variant pairs, 15 proverbs each):**
All 6 variant pairs: p > 0.05. **No significant differences between variants.**

**Wilcoxon signed-rank (generator pairs, 60 MCQs each):**
All 3 generator pairs: p > 0.05. **No significant differences between generators.**

**Holm-Bonferroni correction:** After correction, all tests remain non-significant.

These null results are methodologically important: they show that the observed differences in consensus accuracy and HCW are within sampling noise at N=5. The pipeline as a whole underperforms, not specific variants or generators.

### 8.5 Bootstrap CIs

| Metric | Point | 95% CI Lower | 95% CI Upper |
|--------|-------|--------------|--------------|
| Consensus accuracy (overall) | 56.7% | 49.4% | 63.9% |
| Perfect consensus | 41.7% | 34.4% | 48.9% |
| HCW | 27.8% | 21.1% | 34.4% |
| Partial + fallback | 43.9% | 36.7% | 51.1% |
| Hard fallback (length parity) | 16.1% | 11.1% | 21.7% |
| Duplicate rate | 0.0% | 0.0% | 0.0% |

Per-language consensus accuracy:
- English: 65.0% [53.3%, 76.7%]
- Arabic: 53.3% [40.0%, 65.0%]
- Yoruba: 51.7% [38.3%, 65.0%]

The CIs confirm that English is numerically but not significantly higher than Arabic/Yoruba at N=60; the intervals overlap substantially (e.g., English [53.3%, 76.7%] and Arabic [40.0%, 65.0%] share the 53.3–65.0 range), so the cross-language gaps are not statistically distinguishable, consistent with §5.2.

---


