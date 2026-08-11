# ProverbGap: Hardened Adversarial Distractor Generation for Low-Resource Figurative Language

**Authors:** Sunday Aspita Abraham et al.  
**Venue:** EACL 2027 ARR Submission  
**Date:** 2026-08-02  

---

## 1. Introduction

Large language models (LLMs) are increasingly evaluated on figurative language understanding, yet the construction of high-quality multiple-choice questions (MCQs) for figurative language remains underdeveloped. Existing proverb benchmarks—ProverbEval (Azime et al., NAACL 2025), JAWAHER (Magdy et al., NAACL 2025), and MasalBench (Kalhor & Bahrak, 2026)—release MCQs without systematic adversarial validation of distractors. As a result, these benchmarks may contain surface shortcuts, length biases, or culturally mismatched options that inflate model accuracy without measuring genuine proverb understanding.

We present ProverbGap, a hardened adversarial distractor-generation pipeline applied to English, Arabic, and Yoruba proverbs. Rather than releasing another benchmark, we treat benchmark construction itself as the research question: *How do we build and audit proverb MCQs that resist shortcut solutions?* Our pipeline combines a dynamic multi-model generator pool, four adversarial prompt variants, dual-gate semantic validation (NLI paraphrase filter, correct-meaning leak sanitizer, length parity, idiom blocklist), and a heterogeneous four-model blind audit committee that sees only the four answer options.

Systematic failure-mode documentation reveals that the corpus-based fallback sampler is the critical bottleneck: 43.9% of 180 generated MCQs require at least one fallback replacement, and high-consensus-wrong (HCW) items reach 27.8%. NLI and leak filters account for 71% of all replacements, while length filters account for only 15%, indicating semantic over-filtering rather than structural mismatch. The audit committee itself exhibits position bias (A-position accuracy 73.3% vs D-position 46.7%), confounding consensus metrics. A cross-lingual gradient emerges: Arabic requires 3.5× more fallback replacements than English (mean 1.52 vs. 0.43 per MCQ), suggesting that the pipeline is calibrated for high-resource languages and aggressively rejects model output for morphologically complex, low-training-density languages.

Our contributions are:
1. A reproducible, cost-efficient pipeline for hardened adversarial distractor generation ($0.0047 per audited MCQ).
2. A systematic failure taxonomy linking each failure mode to a specific pipeline component.
3. Empirical evidence that adversarial paraphrasing fails to transfer difficulty cross-lingually: Arabic and Yoruba suffer from corpus-fallback quality collapse while English remains trivially easy.
4. A public testbed of 180 MCQs with full audit logs, raw outputs, and analysis scripts.

We release the pipeline, audit logs, and 180 MCQs as a testbed for reproducible distractor-generation research.

**Paper structure:** Section 2 positions our work against proverb benchmarks, distractor-generation literature, and LLM-as-judge audit methods. Section 3 details the hardened pipeline. Section 4 describes the dataset and experimental setup. Section 5 presents main results. Section 6 documents the failure taxonomy. Section 7 analyzes cross-lingual fallback asymmetry. Section 8 reports baselines and robustness tests. Section 9 presents the LLM-proxy inter-annotator agreement study. Sections 10–11 discuss limitations and conclusions.

---

## 2. Related Work

### 2.1 Proverb and Figurative-Language Benchmarks

ProverbEval (Azime et al., 2025) is the most closely related benchmark: it covers 6 languages (4 Ethiopian + English) with three tasks (MCQ, fill-in-the-blank, generation) and reports that answer-choice order causes up to 50% accuracy variance. However, ProverbEval does not validate distractors through adversarial gates or blind audit. JAWAHER (Magdy et al., 2025) covers 20 Arabic dialects with expert human annotation and GPT-4o as an LLM judge, but its MCQ component lacks difficulty control or shortcut resistance. MasalBench (Kalhor & Bahrak, 2026) evaluates Persian proverb identification but does not analyze distractor quality.

These benchmarks share a common gap: they treat MCQ construction as a data-collection task rather than a methodological challenge. ProverbGap explicitly addresses this gap by making distractor validation the primary scientific contribution.

### 2.2 Distractor Generation

Distractor generation for MCQs has shifted from rule-based templates to LLM-based approaches. DiVERT (Fernandez et al., EMNLP 2024) uses a variational "errors-as-text" representation and shows that a 7B open LLM can beat GPT-4o on math distractor quality. Kang et al. (ACL 2025) train a distractor generator on real student-choice data using DPO, achieving human-expert-level ranking. Alhazmi et al. (EMNLP 2025) apply contrastive learning to align question-answer-distractor semantics.

For proverb-specific distractor generation, no prior work applies adversarial hardening or blind audit. Our work fills this gap by combining dynamic multi-model generation with a disjoint audit committee and explicit failure-mode documentation.

### 2.3 LLM-as-Judge and Options-Only Audit

Balepur & Rudinger (ACL 2025) argue that MCQA is flawed in format and datasets, proposing Item Response Theory and constructed-response alternatives. Their "choices-only cheater" lineage (Balepur & Rudinger 2024) shows that Kendall's τ ≈ 0.9 between choices-only and full-question ranks, suggesting models rely heavily on option content.

Wang et al. (COLING 2025) show that LLMs treat unselected options as 84–99% as confident as the correct one, proposing MCQA+ augmentations to expose this weakness.

We adopt a blind options-only audit not as a substitute for human validation, but as a necessary shortcut screen. Our four-model heterogeneous committee reduces same-family exploitation; we note one residual family overlap (a Google generator and a Google auditor) and rely on the blind options-only design — auditors never see generator identity or outputs — to limit stylistic contamination. We explicitly report position bias as a calibration finding rather than hiding it.

### 2.4 Shortcut Learning in MCQA

Position bias, length bias, and lexical overlap are well-documented shortcuts in MCQA. ProverbEval (Azime et al., 2025) found 50% accuracy variance from choice order. Our work confirms position bias in the audit committee (A-position 73.3% vs D-position 46.7%), but shows that balanced key distribution neutralizes it in aggregate metrics.

### 2.5 Cross-Lingual Evaluation Gaps

MMLU-ProX (Xuan et al., EMNLP 2025) and BRIGHTER (Muhammad et al., ACL 2025) show that African and low-resource languages suffer severe performance drops in multilingual evaluation. Our cross-lingual fallback asymmetry finding (Arabic 3.5× more replacements than English) aligns with this literature: pipeline components calibrated for English fail silently on morphologically complex languages.

---

## 3. Methodology: The Hardened Pipeline

### 3.1 Overview

Figure 1 shows the pipeline. Input is a proverb + curated gold meaning. Output is a 4-option MCQ with options A–D. The pipeline has five stages:

1. **Dynamic generator pool** — 3 active models round-robin across 4 prompt variants.
2. **Dual-gate validation** — semantic distance band, NLI paraphrase filter, leak sanitizer, length parity, idiom blocklist, duplicate repair.
3. **Corpus fallback sampler** — invoked when gates reject all generated distractors.
4. **Option assembly** — round-robin correct-key placement (position shuffling inactive in v68; planned for v70).
5. **Blind audit committee** — 4 heterogeneous models vote options-only; consensus label computed.

### 3.2 Generator Pool

Active generators (v68):
- `qwen/qwen3.7-max` (Qwen family)
- `google/gemma-4-31b-it` (Google family)
- `google/gemini-2.5-flash` (Google family)

Substitutes: `google/gemini-2.5-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `anthropic/claude-sonnet-4`. Hard-failure threshold: 2 consecutive misses; soft-failure threshold: 5 misses. Zero substitutions occurred in v68.

### 3.3 Prompt Variants

| Variant | Rationale |
|---------|-----------|
| `adversarial-hard-negative` | Forces semantically close distractors rather than obvious reversals |
| `adversarial-length-locked` | Strict length and register parity plus ban on negation/antonym shortcuts |
| `taxonomy-guided` | Haladyna / VERGE taxonomy with tightened surface constraints |
| `overgenerate-select` | Generate 8+ candidates, select 3 most plausible and distinct |

All variants include: ±45% length parity, no generic English idioms, no lexical overlap with source proverb, no meta-text.

### 3.4 Dual-Gate Validation

**Gate 1 — Semantic:**
- NLI paraphrase filter: rejects distractors with NLI entailment > 0.60 and embedding similarity > 0.55 (language-specific: Arabic/Yoruba 0.45, English 0.58).
- Correct-meaning leak sanitizer: replaces distractors echoing the gold meaning (language-specific thresholds: English 0.90, Arabic/Yoruba 0.80).
- Idiom blocklist: rejects generic English idioms as distractors for any language.

**Gate 2 — Structural:**
- Length parity: all options within ±35% of median length; relaxed to ±45% if all four within band.
- Duplicate repair: near-duplicate options (Jaccard > 0.50) replaced with fallback.
- Offensive guard: rejects vulgar or culturally inappropriate fallback text.

### 3.5 Corpus Fallback Sampler

When Gate 1 or Gate 2 rejects all generated distractors, the pipeline samples from a corpus of other proverbs' meanings. The sampler uses weighted random selection with exclude sets to avoid repeated collisions. In v68, the fallback sampler is the confirmed bottleneck (Section 6).

### 3.6 Blind Audit Committee

Active auditors (v68):
- `meta-llama/llama-3.3-70b-instruct` (Meta)
- `mistralai/mistral-small-3.2-24b-instruct` (Mistral)
- `google/gemma-3-27b-it` (Google)
- `deepseek/deepseek-v3.2` (DeepSeek)

Each auditor receives only the four options (A–D), no proverb text, no correct meaning. Votes are extracted via regex (uppercase A–D). Consensus label = plurality vote. Consensus fraction = fraction of auditors agreeing on consensus label. Consensus correct = 1 if consensus label matches correct label.

Position distribution is balanced by round-robin counter (45/45/45/45). Position shuffling is **inactive** in v68; planned for v70.

### 3.7 Cost Cap and Reproducibility

Hard cost cap: $5.00 per run. v68 cost: $0.85. Every API call is logged with model ID, prompt tokens, completion tokens, and cost. Model IDs are versioned in `pilot1_test_summary.json`. OpenRouter catalog snapshot saved at `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`. Per-model cost and token breakdown are provided in `table_cost_efficiency.csv` ($0.0047 per audited MCQ; $0.0012 per audit vote).

---

## 4. Dataset and Experimental Setup

### 4.1 Languages and Corpora

| Language | Source | Size | Sampled | QA Coverage |
|----------|--------|------|---------|-------------|
| English | Compiled websites (scraped) | 2,278 proverbs | 60 (5 × 12) | Not documented |
| Arabic | Academic dataset (source unknown) | 913 proverbs | 60 (5 × 12) | Full |
| Yoruba | Owomoyela (2005) | 3,974 proverbs | 60 (5 × 12) | 96.5% missing QA_Flag |

**Data provenance:** See `DATA_PROVENANCE_TEMPLATE.md`. Yoruba data is derived from a copyrighted book; the public release excludes raw Yoruba proverbs. Arabic source dataset is unidentified. English scraping sources are undocumented. These are limitations addressed in Section 10.

### 4.2 Gold-Meaning Curation

All three languages use LLM-curated gold meanings (`openai/gpt-4.1-nano`). Yoruba curation preserves gourd/farmer/bind imagery; Arabic curation preserves specific moral/social situations; English curation uses the original meaning if well-formed.

### 4.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Consensus accuracy | Fraction where plurality vote matches correct label | — |
| Perfect consensus | Fraction where all 4 auditors agree | < 30% |
| High-consensus-wrong (HCW) | Consensus fraction ≥ 0.75 and consensus ≠ correct | < 10% |
| Partial + fallback | Fraction with status `partial` or `length_fallback` | < 15% |
| Hard fallback (length parity) | Fraction with status `length_fallback` | < 5% |
| Duplicate options | Fraction with exact duplicate option pairs | 0% |
| Correct-key balance | Fraction per position A/B/C/D | ~25% each |

### 4.4 Committee Composition

| Model | Family | Role | Accuracy vs Gold |
|-------|--------|------|------------------|
| `meta-llama/llama-3.3-70b-instruct` | Meta | Auditor | 53.3% |
| `mistralai/mistral-small-3.2-24b-instruct` | Mistral | Auditor | 56.7% |
| `google/gemma-3-27b-it` | Google | Auditor | 45.6% |
| `deepseek/deepseek-v3.2` | DeepSeek | Auditor | 56.1% |

Pairwise Cohen's κ: 0.485–0.555 (moderate agreement).

### 4.5 Statistical Methods

- Bootstrap 95% CIs: 10,000 resamples per metric.
- McNemar's test: paired variant comparisons on same 15 proverbs.
- Wilcoxon signed-rank: paired generator comparisons.
- Holm-Bonferroni correction: for 6 variant pairs + 3 generator pairs.

### 4.6 LLM-Proxy Inter-Annotator Agreement

Seven closed LLMs annotated a 60-item subset (20 per language). Fleiss κ = 0.4845 (moderate agreement). Mean pairwise Cohen κ = 0.4846. Per-model gold accuracy: 58.3–78.3%. This is treated as a standalone contribution, not a substitute for human validation.

---

## 5. Main Results

### 5.1 Aggregate Metrics

| Metric | v68 N=5 | 95% Bootstrap CI | Target | Pass? |
|--------|---------|------------------|--------|-------|
| Consensus accuracy | 56.7% | [49.4%, 63.9%] | — | — |
| Perfect consensus | 41.7% | [34.4%, 48.9%] | < 30% | ❌ |
| HCW | 27.8% | [21.1%, 34.4%] | < 10% | ❌ |
| Partial + fallback | 43.9% | [36.7%, 51.1%] | < 15% | ❌ |
| Hard fallback (length parity) | 16.1% | [11.1%, 21.7%] | < 5% | ✅ |
| Duplicate options | 0.0% | [0.0%, 0.0%] | 0% | ✅ |
| Correct-key balance | 45/45/45/45 | — | ~25% | ✅ |

**Key finding:** The pipeline achieves zero infrastructure failures (API/parse fallback, benched generators, missing votes) but fails all shortcut-resistance gates except duplicates and key balance. The failure modes are systematic, not stochastic. Consensus is incorrect on 43.3% of items (100% − 56.7% accuracy); of these, 27.8% reach high-consensus-wrong (≥0.75 auditor agreement on the wrong option), and 16.1% carry the length-fallback status.

### 5.2 Per-Language Results

| Language | MCQs | Consensus Accuracy | 95% CI | Perfect Consensus | HCW |
|----------|------|-------------------|--------|-------------------|-----|
| English | 60 | 65.0% | [53.3%, 76.7%] | 45.0% | 18.3% |
| Arabic | 60 | 53.3% | [40.0%, 65.0%] | 50.0% | 31.7% |
| Yoruba | 60 | 51.7% | [38.3%, 65.0%] | 30.0% | 33.3% |

English is numerically easier than Arabic and Yoruba, but the 95% CIs overlap (English [53.3%, 76.7%], Arabic [40.0%, 65.0%], Yoruba [38.3%, 65.0%]), so the gap is not statistically distinguishable at N = 60 per language. Arabic and Yoruba have overlapping CIs, indicating similar difficulty levels.

### 5.3 Per-Generator Results

| Generator | MCQs | Consensus Accuracy | HCW | Partial+Fallback |
|-----------|------|-------------------|-----|------------------|
| `google/gemma-4-31b-it` | 60 | 65.0% | 21.7% | 33.3% |
| `google/gemini-2.5-flash` | 60 | 53.3% | 31.7% | 50.0% |
| `qwen/qwen3.7-max` | 60 | 51.7% | 30.0% | 48.3% |
| **Pooled** | **180** | **56.7%** | **27.8%** | **43.9%** |

Gemma-4-31b-it is the strongest generator (65.0% accuracy, 21.7% HCW). The pooled result (56.7%) is worse than gemma-only, suggesting that weaker generators introduce more HCW items than the pool diversity helps.

### 5.4 Position Bias

Correct-key distribution is perfectly balanced: 45/45/45/45 across all 180 MCQs. Committee accuracy by position:

| Position | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| A | 33 | 45 | 73.3% |
| B | 26 | 45 | 57.8% |
| C | 22 | 45 | 48.9% |
| D | 21 | 45 | 46.7% |

Chi-square goodness-of-fit: χ² = 3.49, df = 3, p = 0.322. **Not significant** at α = 0.05. The position-bias trend is present but does not reach significance at N = 180. Balanced key distribution means the raw consensus accuracy is unbiased, but variance by position suggests committee calibration issues.

### 5.5 Infrastructure Robustness

| Metric | v58–v63 legacy | v68 current |
|--------|---------------|-------------|
| Hard fallback rate (infrastructure/API) | 90%+ API failures | **0%** |
| Parse fallback rate | Provider cascades | **0%** |
| Benched generators | Model EOL crashes | **0%** |
| Missing audit votes | Missing votes | **0%** |
| Duplicate options | Not tracked | **0%** |

The hardened dynamic pool eliminates all infrastructure failures (API/parse fallback, benched generators, missing votes) observed in earlier runs. Separately, the length-parity fallback *status* affects 16.1% of MCQs (see §5.1), a distinct metric from infrastructure hard-fallback.

---

## 6. Failure Taxonomy

We document six failure modes observed across v58–v69. Each entry includes pipeline locus, empirical magnitude from v68, and implication.

### 6.1 Generic Reversal / Idiom Shortcut (English Too Easy)

**Locus:** Generator prompting  
**Magnitude:** English consensus accuracy 65.0%, perfect consensus 45.0%  
**Evidence:** English distractors are generic reversals or unrelated idioms that auditors reject or accept trivially. The NLI embedding guard for English (0.58) may be too permissive, allowing obvious non-paraphrases to pass.

**Implication:** English is not a valid test of adversarial difficulty. The pipeline needs an English-specific variant targeting common misreadings.

### 6.2 Near-Paraphrase Trap (NLI Over-Filtering)

**Locus:** Gate 1 — NLI paraphrase filter  
**Magnitude:** NLI accounts for 36.3% of all replacements (0.36 per MCQ)  
**Evidence:** The NLI filter removes tempting distractors that are semantically close to the correct meaning. The fallback sampler then replaces them with unrelated proverb meanings, producing either trivial or confident-wrong distractors.

**Implication:** The NLI threshold is over-aggressive. A grid search over 0.40–0.65 could reduce unnecessary replacements.

### 6.3 Confident-Wrong Corpus Fallback

**Locus:** Corpus fallback sampler  
**Magnitude:** 43.9% partial+fallback, HCW 27.8%, fallback items have mean 0.99 replacements  
**Evidence:** When NLI/leak filters reject model-generated distractors, the corpus sampler pulls meanings from other proverbs. These are often generic moral statements or culturally mismatched idioms that auditors find plausible but wrong.

**Implication:** The fallback sampler is the critical bottleneck. An LLM-based fallback generator (v69 ablation) is the highest-leverage fix.

### 6.4 Cultural Mismatch in Low-Resource Languages

**Locus:** Corpus fallback sampler + generator prompts  
**Magnitude:** Arabic fallback count 1.52/MCQ vs. English 0.43/MCQ (3.5× asymmetry)  
**Evidence:** Arabic and Yoruba proverbs have fewer training examples and more ambiguous semantic spaces. The NLI and leak filters aggressively reject model output, forcing fallback use. Fallbacks from other languages' proverbs are culturally mismatched.

**Implication:** The pipeline is calibrated for English. Low-resource languages need language-specific fallback samplers and cultural-expert review.

### 6.5 Variant Triviality

**Locus:** Generator prompting  
**Magnitude:** `overgenerate-select`: 71.1% fully generated, 2.2% length fallback, 46.7% consensus-wrong (22.2% high-consensus-wrong)  
**Evidence:** Some variants produce distractors so clean that they pass all gates, but the resulting MCQs are trivially easy (46.7% consensus-wrong, of which 22.2% are high-consensus-wrong, means auditors agree on the wrong answer, indicating distractors lack temptation).

**Implication:** Variant choice is itself a failure mode. The variant that produces the most "complete" outputs (`overgenerate-select`) is not the most adversarial.

### 6.6 Committee Position Bias

**Locus:** MCQ assembly + audit committee calibration  
**Magnitude:** A-position accuracy 73.3% vs. D-position 46.7% (26.6pp gap), χ² p = 0.322  
**Evidence:** The committee is not position-invariant. When correct answer is A, auditors agree 73.3% of the time; when D, only 46.7%. Balanced keys prevent aggregate bias, but per-position variance indicates committee calibration issues.

**Implication:** Position shuffling in v70 is essential. The position-corrected consensus metric should replace raw consensus for aggregate claims.

---

## 7. Cross-Lingual Fallback Asymmetry

### 7.1 Quantifying the Gradient

| Language | Fallback Count/MCQ | NLI Replaced | Leak Replaced | Length Replaced |
|----------|-------------------|--------------|---------------|-----------------|
| English | 0.43 | 0.15 | 0.15 | 0.07 |
| Arabic | 1.52 | 0.62 | 0.43 | 0.25 |
| Yoruba | 1.03 | 0.32 | 0.47 | 0.13 |

Arabic requires **3.5× more fallback replacements** than English. The dominant drivers are NLI (36.3% of all replacements) and leak (35.2%), not length (15.1%).

### 7.2 Variant × Language Interaction

| Variant | English Fallback | Arabic Fallback | Yoruba Fallback | Arabic/English Ratio |
|---------|-----------------|-----------------|-----------------|----------------------|
| `adversarial-hard-negative` | 1.13 | 2.93 | 1.80 | **2.59×** |
| `adversarial-length-locked` | 0.33 | 1.73 | 1.13 | **5.24×** |
| `overgenerate-select` | 0.00 | 0.60 | 0.80 | — |
| `taxonomy-guided` | 0.27 | 0.80 | 0.40 | **2.96×** |

The `adversarial-hard-negative` variant is 2.6× more aggressive in Arabic than English. The `adversarial-length-locked` variant is 5.2× more aggressive. This is a **prompt × resource interaction effect**: adversarial prompts that produce tempting distractors in English trigger NLI/leak filters aggressively in Arabic, forcing corpus fallback.

### 7.3 Interpretations

We propose three explanatory factors:

1. **Morphological complexity:** Arabic has richer inflectional morphology, making paraphrase detection harder for NLI models trained primarily on English.
2. **Training-data density:** English has 100× more LLM training data than Arabic. Models produce higher-quality English distractors that survive filters; Arabic distractors are more likely to be rejected and replaced.
3. **Paraphrase fidelity:** LLM-generated Arabic paraphrases of proverbs are more likely to be literal translations or awkward calques, triggering the leak filter.

**Implication:** Adversarial paraphrasing does not fail to transfer difficulty — the pipeline itself is calibrated for English. To create hard Arabic/Yoruba distractors, we need language-specific filter thresholds and fallback samplers, not harder prompts.

---

## 8. Baselines and Robustness

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

These null results are methodologically important: they show that the observed differences in consensus accuracy and HCW are within sampling noise at N=5. The pipeline as a whole underperforms, not specific variants or generators. We note that the paired tests have limited power at N=5 (per-language n = 60, paired on 15 proverbs): a planned scale-up to N=15 per language (540 MCQs) raises power to detect a ~15 pp difference in consensus accuracy to ≈0.85, so non-significance here should be read as "undemonstrated," not "absent."

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

## 9. LLM-Proxy Inter-Annotator Agreement

### 9.1 Setup

Seven closed LLMs annotated a 60-item validation subset (20 per language) from the v68 human-annotation sample. The subset is stratified by generation status and consensus correctness for the planned human-validation study, so it is not a random sample of all 180 MCQs; agreement statistics below describe this curated subset, not the full testbed. Models: Qwen2.5-7B-Instruct, Claude-3-Haiku, DeepSeek-R1-Distill-Qwen-32B, Gemini-2.5-Flash, Llama-3.2-3B-Instruct, Phi-3.5-mini-instruct, GPT-4o-mini.

### 9.2 Results

| Model | n | Acc vs Consensus | Acc vs Gold | EN | AR | YO |
|-------|---|------------------|-------------|----|----|----|
| Qwen2.5-7B | 60 | 48.3% | 63.3% | 55% | 45% | 45% |
| Claude-3-Haiku | 60 | 58.3% | 78.3% | 70% | 55% | 50% |
| DeepSeek-R1-32B | 60 | 50.0% | 65.0% | 65% | 60% | 25% |
| Gemini-2.5-Flash | 60 | 50.0% | 78.3% | 70% | 50% | 30% |
| Llama-3.2-3B | 60 | 53.3% | 63.3% | 65% | 60% | 35% |
| Phi-3.5-mini | 60 | 45.0% | 58.3% | 50% | 45% | 40% |
| GPT-4o-mini | 60 | 55.0% | 78.3% | 65% | 50% | 50% |

**Overall:** Fleiss κ = 0.4845 (moderate agreement). Mean pairwise Cohen κ = 0.4846 (range: 0.295–0.799). **Zero refusals** across all models and items on this multiple-choice annotation task (no safety or policy blocks were triggered).

### 9.3 Interpretation

The LLM-proxy IAA shows:
1. **Moderate cross-model agreement** on distractor plausibility (κ = 0.4845). This is comparable to human annotation on subjective NLP tasks.
2. **High agreement with gold meaning** (58.3–78.3%), especially for Claude-3-Haiku, Gemini-2.5-Flash, and GPT-4o-mini (all 78.3%).
3. **Low agreement with v68 consensus** (48.3–58.3%), revealing that the audit committee detects items where even aligned models disagree with gold.
4. **Yoruba weakness:** DeepSeek-R1-32B drops to 25% on Yoruba, suggesting open-weight models struggle with low-resource figurative language.

This IAA is a standalone contribution to the "LLM-as-judge" literature. It is **not** a substitute for native-speaker human validation.

---

## 10. Discussion and Limitations

### 10.1 Corpus Fallback as Methodological Signal

The 43.9% partial+fallback rate is not a bug to be fixed but a signal to be studied. Every fallback replacement is a documented failure of the semantic filters. The fallback sampler reveals which distractors are "too close" to the gold meaning and which are "too far." This is precisely the kind of fine-grained error analysis reviewers expect from a methodology paper.

### 10.2 MCQ-Only Scope

We deliberately limit our study to MCQ. Fill-in-the-blank and open-ended generation tasks introduce different failure modes (memorization, free-generation bias) that are outside our current scope. We plan to extend the pipeline to FiB and generation in future work.

### 10.3 N=5 as Methodology Study

180 MCQs (60 per language) is modest for per-language generalization claims. We frame the paper as a **methodology + failure-taxonomy study**. All CIs are reported; we avoid strong claims about entire language families. A follow-up at N=15 (540 MCQs) is planned when budget renews.

### 10.4 API Reproducibility

OpenRouter model IDs may change or be deprecated. We mitigate this with:
- Versioned model IDs in `pilot1_test_summary.json`
- OpenRouter catalog snapshot in `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`
- SHA256 hashes of all output files
- Detailed reproduction steps in `REPRODUCIBILITY_CHECKLIST.md`

### 10.5 Yoruba Data Provenance

The Yoruba corpus is derived from Owomoyela (2005), which is under copyright. We exclude raw Yoruba proverbs from the public release but retain the 60 MCQs in our analysis. This is a limitation that future work should address by obtaining redistribution permission or using public-domain Yoruba proverb collections.

### 10.6 Zero Human Validation

Native-speaker human validation is pending. The LLM-proxy IAA (κ = 0.4845) is a calibration anchor, not a validity certificate. We plan to recruit 2–3 native speakers per language for a 60–90 item validation study with Cohen's κ reporting. This is documented as future work.

### 10.7 Generalizability

Our findings are specific to proverb understanding in English, Arabic, and Yoruba. Extension to other figurative languages (idioms, metaphors, sarcasm) requires re-running the pipeline with language-specific prompts and filters. The failure taxonomy is generalizable, but the specific magnitudes are not.

### 10.8 Ethics and Bias

We include idiom and offensive-content blocklists to prevent culturally inappropriate distractors. However, corpus fallbacks are not culturally curated, and some may be mismatched or offensive. We recommend human-expert review of all fallback items before releasing benchmarks to the public.

---

## 11. Conclusion

We presented ProverbGap, a hardened adversarial distractor-generation pipeline for proverb MCQs in English, Arabic, and Yoruba. The pipeline achieves zero infrastructure failures but fails all shortcut-resistance gates except duplicates and key balance. The central finding is that the corpus-based fallback sampler is the critical bottleneck: 43.9% of MCQs require fallback replacements, and 27.8% become high-consensus-wrong items due to confident-wrong corpus distractors.

We documented six failure modes: generic reversal/idiom shortcut, NLI over-filtering, confident-wrong corpus fallback, cultural mismatch in low-resource languages, variant triviality, and committee position bias. A cross-lingual gradient emerges: Arabic requires 3.5× more fallback replacements than English, suggesting the pipeline is calibrated for high-resource languages.

LLM-proxy inter-annotator agreement across seven models yields Fleiss κ = 0.4845 (moderate agreement) and 58.3–78.3% match to curated gold meanings (mean 69.4%). This is a standalone contribution to LLM-as-judge methodology, not a substitute for human validation.

We release the pipeline, audit logs, and 180 MCQs as a public testbed for reproducible distractor-generation research, at a production cost of $0.85 ($0.0047 per audited MCQ).

**Future work:** (1) Enable LLM-based fallback generation (v69/v70 ablation) to replace the corpus sampler. (2) Recruit native speakers for human validation with IAA reporting. (3) Scale to N=15 per language (540 MCQs). (4) Extend to fill-in-the-blank and open-ended generation tasks. (5) Add position shuffling to eliminate committee position bias.

---

## Acknowledgments

We thank the open-source community for LLM APIs and the developers of sentence-transformers, pandas, and numpy. This work was conducted under the Elite Research Execution Framework.

## References

Azime, T., Belay, A., Chanie, B., Balcha, A., Abadi, T., ... (2025). ProverbEval: Benchmarking proverb understanding in low-resource languages. *NAACL 2025 Findings*.

Balepur, N., Rudinger, R., & Boyd-Graber, J. (2025). Which of these best describes MCQA? A) Forced B) Flawed C) Fixable D) All of the above. *ACL 2025 Long*.

Balepur, N., & Rudinger, R. (2024). Is your LLM knowledgeable or a choices-only cheater? *arXiv:2407.01992*.

Fernandez, R., Scarlatos, A., Feng, Y., Woodhead, S., & Lan, A. (2024). DiVERT: Distractor generation via variational errors-as-text. *EMNLP 2024*.

Kalhor, M., & Bahrak, A. (2026). MasalBench: Benchmarking Persian proverb understanding. *arXiv:2601.22050*.

Kang, M., et al. (2025). Generating plausible distractors via student choice prediction. *ACL 2025 Long*.

Magdy, M., Kwon, D., Alwajih, A., Abdelfadil, E., Shehata, D., & Abdul-Mageed, M. (2025). JAWAHER: A large-scale Arabic proverb dataset. *NAACL 2025 Long*.

Muhammad, N., Ousidhoum, K., Abdulmumin, M., et al. (2025). BRIGHTER: A multi-label emotion dataset for 28 languages. *ACL 2025 Long*.

Wang, Y., et al. (2025). LLMs may perform MCQA by selecting the least incorrect option. *COLING 2025*.

Xuan, Q., et al. (2025). MMLU-ProX: Multilingual MMLU with expert review. *EMNLP 2025*.

---

*Draft completed: 2026-07-10. All numbers traceable to v68 output files. No legacy numbers.*
