#### 6. Failure Taxonomy

We document six failure modes observed across v58â€“v69. Each entry includes pipeline locus, empirical magnitude from v68, and implication.

### 6.1 Generic Reversal / Idiom Shortcut (English Too Easy)

**Locus:** Generator prompting  
**Magnitude:** English consensus accuracy 65.0%, perfect consensus 45.0%  
**Evidence:** English distractors are generic reversals or unrelated idioms that auditors reject or accept trivially. The NLI embedding guard for English (0.58) may be too permissive, allowing obvious non-paraphrases to pass.

**Implication:** English is not a valid test of adversarial difficulty. The pipeline needs an English-specific variant targeting common misreadings.

### 6.2 Near-Paraphrase Trap (NLI Over-Filtering)

**Locus:** Gate 1 â€” NLI paraphrase filter  
**Magnitude:** NLI accounts for 36.3% of all replacements (0.36 per MCQ)  
**Evidence:** The NLI filter removes tempting distractors that are semantically close to the correct meaning. The fallback sampler then replaces them with unrelated proverb meanings, producing either trivial or confident-wrong distractors.

**Implication:** The NLI threshold is over-aggressive. A grid search over 0.40â€“0.65 could reduce unnecessary replacements.

### 6.3 Confident-Wrong Corpus Fallback

**Locus:** Corpus fallback sampler  
**Magnitude:** 43.9% partial+fallback, HCW 27.8%, fallback items have mean 0.99 replacements  
**Evidence:** When NLI/leak filters reject model-generated distractors, the corpus sampler pulls meanings from other proverbs. These are often generic moral statements or culturally mismatched idioms that auditors find plausible but wrong.

**Implication:** The fallback sampler is the critical bottleneck. An LLM-based fallback generator (v69 ablation) is the highest-leverage fix.

### 6.4 Cultural Mismatch in Low-Resource Languages

**Locus:** Corpus fallback sampler + generator prompts  
**Magnitude:** Arabic fallback count 1.52/MCQ vs. English 0.43/MCQ (3.5Ã— asymmetry)  
**Evidence:** Arabic and Yoruba proverbs have fewer training examples and more ambiguous semantic spaces. The NLI and leak filters aggressively reject model output, forcing fallback use. Fallbacks from other languages' proverbs are culturally mismatched.

**Implication:** The pipeline is calibrated for English. Low-resource languages need language-specific fallback samplers and cultural-expert review.

### 6.5 Variant Triviality

**Locus:** Generator prompting  
**Magnitude:** `overgenerate-select`: 71.1% fully generated, 2.2% length fallback, 46.7% consensus-wrong (22.2% high-consensus-wrong)  
**Evidence:** Some variants produce distractors so clean that they pass all gates, but the resulting MCQs are trivially easy (46.7% consensus-wrong, of which 22.2% are high-consensus-wrong, means auditors agree on the wrong answer, indicating distractors lack temptation).

**Implication:** Variant choice is itself a failure mode. The variant that produces the most "complete" outputs (`overgenerate-select`) is not the most adversarial.

### 6.6 Committee Position Bias

**Locus:** MCQ assembly + audit committee calibration  
**Magnitude:** A-position accuracy 73.3% vs. D-position 46.7% (26.6pp gap), Ï‡Â² p = 0.322  
**Evidence:** The committee is not position-invariant. When correct answer is A, auditors agree 73.3% of the time; when D, only 46.7%. Balanced keys prevent aggregate bias, but per-position variance indicates committee calibration issues.

**Implication:** Position shuffling in v70 is essential. The position-corrected consensus metric should replace raw consensus for aggregate claims.

---


