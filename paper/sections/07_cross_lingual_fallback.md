#### 7. Cross-Lingual Fallback Asymmetry

### 7.1 Quantifying the Gradient

| Language | Fallback Count/MCQ | NLI Replaced | Leak Replaced | Length Replaced |
|----------|-------------------|--------------|---------------|-----------------|
| English | 0.43 | 0.15 | 0.15 | 0.07 |
| Arabic | 1.52 | 0.62 | 0.43 | 0.25 |
| Yoruba | 1.03 | 0.32 | 0.47 | 0.13 |

Arabic requires **3.5Ã— more fallback replacements** than English. The dominant drivers are NLI (36.3% of all replacements) and leak (35.2%), not length (15.1%).

### 7.2 Variant Ã— Language Interaction

| Variant | English Fallback | Arabic Fallback | Yoruba Fallback | Arabic/English Ratio |
|---------|-----------------|-----------------|-----------------|----------------------|
| `adversarial-hard-negative` | 1.13 | 2.93 | 1.80 | **2.59Ã—** |
| `adversarial-length-locked` | 0.33 | 1.73 | 1.13 | **5.24Ã—** |
| `overgenerate-select` | 0.00 | 0.60 | 0.80 | â€” |
| `taxonomy-guided` | 0.27 | 0.80 | 0.40 | **2.96Ã—** |

The `adversarial-hard-negative` variant is 2.6Ã— more aggressive in Arabic than English. The `adversarial-length-locked` variant is 5.2Ã— more aggressive. This is a **prompt Ã— resource interaction effect**: adversarial prompts that produce tempting distractors in English trigger NLI/leak filters aggressively in Arabic, forcing corpus fallback.

### 7.3 Interpretations

We propose three explanatory factors:

1. **Morphological complexity:** Arabic has richer inflectional morphology, making paraphrase detection harder for NLI models trained primarily on English.
2. **Training-data density:** English has 100Ã— more LLM training data than Arabic. Models produce higher-quality English distractors that survive filters; Arabic distractors are more likely to be rejected and replaced.
3. **Paraphrase fidelity:** LLM-generated Arabic paraphrases of proverbs are more likely to be literal translations or awkward calques, triggering the leak filter.

**Implication:** Adversarial paraphrasing does not fail to transfer difficulty â€” the pipeline itself is calibrated for English. To create hard Arabic/Yoruba distractors, we need language-specific filter thresholds and fallback samplers, not harder prompts.

---


