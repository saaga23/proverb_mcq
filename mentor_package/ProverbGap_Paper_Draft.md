# ProverbGap: A Cross-Lingual MCQ Benchmark for Proverb Understanding with Adversarial Distractor Generation

**Draft v1.0 | May 2026**

---

## Abstract

We present ProverbGap, a cross-lingual multiple-choice question benchmark designed to evaluate whether large language models (LLMs) genuinely understand proverbial figurative language or merely exploit surface-level shortcuts. Covering English, Arabic, and Yoruba, ProverbGap employs a two-strategy distractor generation pipeline: Strategy 1 uses in-domain negative sampling to establish a baseline, while Strategy 2 leverages cross-family LLM paraphrasing to produce semantically plausible adversarial distractors. Each generated item is audited by a heterogeneous committee of API models with pre-flight health validation, position-bias testing, and a leakage heuristic. Our N=150 pilot (50 per language) achieves 86.8% accuracy on Strategy 1 and 62.5% on Strategy 2, with McNemar's test confirming a statistically significant difficulty gap (p < 0.001). We report extensive negative results---including same-family model exploitation, reasoning collapse under chain-of-thought prompting, and catastrophic API infrastructure failures---that inform the design of robust evaluation pipelines for low-resource figurative language. All code, data, and evaluation artifacts are released for reproducibility.

---

## 1. Introduction

Proverbs represent one of the most challenging forms of figurative language for computational models. Unlike literal text, proverbs convey culturally embedded wisdom through idiomatic expressions whose meanings cannot be derived compositionally from their constituent words. While recent benchmarks have advanced evaluation of LLMs on mathematical reasoning, code generation, and factual recall, proverb understanding remains underrepresented---particularly for low-resource languages outside the Indo-European family.

Existing proverb benchmarks are limited in three critical ways. First, most cover only a single language or language family. Second, many rely on human-written distractors that are expensive to scale and may not generalize across models. Third, few benchmarks systematically test for shortcut exploitation---the tendency of LLMs to rely on lexical overlap, position bias, or stylistic fingerprints rather than genuine semantic understanding.

We introduce ProverbGap to address these gaps. ProverbGap is a cross-lingual MCQ benchmark spanning English (high-resource), Arabic (medium-resource, morphologically complex), and Yoruba (low-resource, tonal, oral tradition). The benchmark is constructed through an adversarial pipeline that generates distractors at two difficulty levels and validates them through a multi-model audit committee. Our contributions are:

1. **A scalable two-strategy distractor generation pipeline** that combines in-domain negative sampling with cross-family LLM paraphrasing, grounded in literature on distractor quality and style-bias mitigation.
2. **A hardened evaluation protocol** featuring pre-flight model validation, per-model position shuffling, position-bias statistical testing, and a leakage heuristic to detect memorization.
3. **Extensive negative results** documenting same-family model exploitation, chain-of-thought reasoning collapse, API infrastructure fragility, and the unique challenges of low-resource figurative language generation.
4. **A pilot dataset of 300 MCQs** (150 Strategy 1, 150 Strategy 2) with encoder baselines, per-language stratification, and reproducible Kaggle execution.

---

## 2. Related Work

### 2.1 Proverb and Figurative Language Benchmarks

Evaluation of proverb understanding has emerged as an active research area within figurative-language NLP. ProverbEval (Azime et al., NAACL 2025) evaluates Ethiopian languages through MCQ, fill-in-the-blank, and generation tasks. Jawaher (NAACL 2025) provides 10,037 Arabic proverbs across 20 dialects with translation and explanation tasks. PRONE (CODI 2025) offers 2,830 Nepali MCQs with human-written distractors. MasalBench (Kalhor et al., 2026) presents Persian proverb understanding with LLM-generated distractors and manual curation.

ProverbGap focuses explicitly on **adversarial distractor generation** and **shortcut exploitation detection**. Unlike prior work that often treats distractors as secondary, we center them as a primary research question, drawing on evidence that LLMs generate low-quality distractors without systematic hardening (Alhazmi et al., EMNLP 2024).

### 2.2 Distractor Generation Methodology

The distractor generation literature identifies four critical quality dimensions: plausibility (semantic relevance to the question), incorrectness (the distractor must not be correct), diversity (minimal redundancy among options), and fluency (grammatical correctness) (Gales et al., Eval4NLP 2023; DG Survey, 2024).

DiVERT (Fernandez et al., EMNLP 2024) emphasizes that high-quality distractors must anticipate learner misconceptions rather than merely produce plausible text. GSM-DC (Yang et al., EMNLP 2025) demonstrates that controlled distractor injection improves out-of-distribution robustness. D-GEN (ACL 2025) explicitly forbids paraphrasing the correct answer during generation, a principle we enforce in our Strategy 2 prompt.

For automatic quality assessment, Joint Generation of Distractors (CMC 2025) incorporates BERTScore and cosine similarity to evaluate distractor relevance. SEFD (PMC 2025) establishes that semantic similarity scores remain high even after LLM paraphrasing, validating the use of embedding-based gates. SemEval 2025 employs multi-qa-mpnet-base-cos-v1 with a cosine threshold of 0.5 for hallucination detection via semantic similarity.

### 2.3 Same-Family Detection and Stylistic Bias

A critical vulnerability in LLM-generated evaluation is same-family exploitation: evaluator models can recognize stylistic fingerprints from generator models of the same architecture family, leading to artificially inflated performance (Panickssery et al., NeurIPS 2024). Ackerman and Panickssery (ICLR 2025) show that chat and instruct models retain family-specific fingerprints, while base models lack this ability. Sun et al. (2025) report 97.1% cross-family detection accuracy but only 59.8% within-family accuracy, confirming the vulnerability.

Dubois et al. (EMNLP 2025) find that nucleus (top-p) sampling produces the least detectable text, and same-family detectors only work reliably under greedy decoding. Krishna et al. (NeurIPS 2023) demonstrate that cross-model paraphrasing---specifically using DIPPER, a different-family paraphraser---drops DetectGPT accuracy from 70.3% to 4.6%. These findings directly motivated our choice of qwen3-32b (Alibaba) as the generator, distinct from our committee models (Meta llama-4-maverick and Saudi allam-2-7b).

### 2.4 Shortcut Learning in MCQ

Du et al. (2022) formalize shortcut learning in NLP, categorizing lexical, overlap, position, and style biases. Zhou et al. (EMNLP 2024 Findings) expand this taxonomy to occurrence, style, and concept shortcuts, directly validating length-normalization approaches. Zheng et al. (ICLR 2024) identify token bias as primary and position bias as secondary in MCQ settings. Gupta et al. (2024) show that MMLU answer reordering drops performance by 13 percentage points, demonstrating the severity of position bias.

Our pipeline implements multiple debiasing strategies: deterministic position rotation with per-model seeded shuffling, length validation gates, and explicit style-variation prompting in Strategy 2.

### 2.5 LLM-as-a-Judge and Committee Evaluation

The LLM-as-a-Judge paradigm has gained traction for automated evaluation, but reliability concerns persist. The LLM-as-a-Judge Survey (Gu et al., 2024) warns that "post-processing rule-based extraction methods are inherently brittle and susceptible to minor variations." AgentProp-Bench (Gurram et al., 2026) recommends that any study using LLM judges report agreement with human labels, bias direction, and calibrated estimates.

The Language Model Council (Zhao et al., NAACL 2025) demonstrates that heterogeneous judge pools improve ranking robustness, and that filtering inconsistent votes improves ensemble quality. The Roundtable Policy (2025) proposes confidence-weighted consensus over flat majority voting. Our committee design---combining a 17B-parameter Meta model and a 7B-parameter Arabic model---explicitly pursues architectural and cultural diversity.

### 2.6 Low-Resource Language Evaluation

Evaluation of low-resource languages reveals consistent performance degradation. AmharicStoryQA (2026) reports model collapse to 20--35% on Amharic narrative understanding. EACL 2026 documents a 14 percentage point "Pragmatics Gap" for Egyptian Arabic idioms. BEA 2025 finds that LLM performance correlates strongly with training data representation, disadvantaging underrepresented languages.

Yoruba, in particular, presents unique challenges: tonal marking, agglutinative morphology, and oral tradition provenance make both translation and automated generation difficult. Our results confirm this gradient: English achieves 97.6% S1 accuracy while Yoruba reaches only 70.0%, with Strategy 2 generation failing 36% of the time for Yoruba versus 8% for English.

---

## 3. The ProverbGap Dataset

### 3.1 Data Collection

ProverbGap comprises 7,172 proverbs across six languages (hosted on Kaggle; local development uses placeholder samples). The current benchmark uses three languages:

| Language | Count | Source | Prefix |
|----------|-------|--------|--------|
| English | 2,278 | Public proverb collections | ENG |
| Arabic | 913 | Classical Arabic (amsal) collections | MID |
| Yoruba | 3,931 | Yoruba oral tradition and ethnographic records | YOR |

French (161), German (142), and Spanish (63) proverbs are collected but excluded from the current benchmark due to insufficient sample sizes for statistical validity.

Each entry includes the original proverb text, an English translation, and a cultural explanation of usage and significance. Arabic entries use Modern Standard Arabic (fus-ha) rather than dialectal variants. Yoruba entries preserve tonal marks where available.

### 3.2 Contamination Filter

English proverbs pose a contamination risk because canonical sayings (e.g., "A bird in the hand," "Actions speak louder than words") appear widely in LLM pre-training corpora. We implement a hardcoded filter matching 25 famous proverb substrings, excluding contaminated items before sampling. This filter removes approximately 8.3% of English proverbs.

### 3.3 Known Limitations

1. **Dialectal homogeneity**: Arabic proverbs are primarily MSA; dialectal variation is not labeled.
2. **Size imbalance**: Yoruba has 4x more proverbs than Arabic, reflecting collection availability.
3. **Translation quality**: English translations of Yoruba and Arabic are interpretive; no inter-annotator agreement was computed.
4. **No temporal metadata**: Proverbs are undated, preventing temporal train/test splits.

---

## 4. Methodology

### 4.1 Overview

The ProverbGap pipeline consists of four phases: (1) data loading and contamination filtering, (2) MCQ generation via Strategy 1 and Strategy 2, (3) committee evaluation with multiple prompting styles, and (4) statistical analysis and baseline comparison. The entire pipeline is implemented as a self-contained Kaggle notebook with SQLite API caching, incremental checkpointing, and reproducible random seeds.

### 4.2 Strategy 1: In-Domain Negative Sampling

Strategy 1 serves as the baseline. For each target proverb, three distractors are sampled without replacement from other proverbs in the same language pool. This approach leverages the finding that in-domain negative sampling creates harder negatives than synthetic distractors (DISTO, EDM 2024).

The sampling uses a fixed random seed (SEED = 42) combined with the item index to ensure reproducibility. If fewer than three alternative proverbs exist in the language pool, the pipeline falls back to placeholder distractors.

Strategy 1 has a 0% fallback rate and acts as the "easy" condition against which Strategy 2 hardness is measured.

### 4.3 Strategy 2: Cross-Family LLM Paraphrasing

Strategy 2 generates adversarial distractors through LLM paraphrasing. The generator model is qwen3-32b (Alibaba), chosen explicitly to be architecturally distinct from the committee evaluation models (Meta and Saudi), following the cross-family paraphrasing recommendation of Krishna et al. (NeurIPS 2023).

**Generation parameters:** temperature = 0.7, top_p = 0.9, seed = 42. The temperature of 0.7 (rather than greedy 0.0) follows Dubois et al. (EMNLP 2025), who find that nucleus sampling produces the least detectable text.

The model is prompted to return a JSON list of four strings: the first is a correct paraphrase of the proverb's meaning, and the remaining three are incorrect direct translations with subtle meaning shifts. All four options must be "roughly similar length (within 35% of each other's character count)."

**Dual-gate validation:**
1. **Length gate**: The relative length difference between each distractor and the correct option must not exceed 35%.
2. **Semantic gate**: Jaccard similarity between the word sets of the generated paraphrase and the reference translation must be at least 0.25.

If either gate passes, the generation is accepted immediately. If both fail, the pipeline retries with exponential backoff (up to 8 retries for English/Arabic, 12 for Yoruba). If all retries fail, a hard fallback substitutes generic placeholder distractors ("Incorrect alternative," "Another wrong option," "Not the right choice").

### 4.4 MCQ Assembly and Position Bias Mitigation

Each MCQ places the correct answer at a pseudo-random position. The base position is determined by `idx % 4`, but each committee model receives a model-specific seeded shuffle (`seed = hash(model) + idx`). This ensures that different models see different answer orderings, preventing position bias from being confounded with model capability.

### 4.5 Committee Evaluation

The evaluation committee comprises two reliable API models:
- meta/llama-4-maverick-17b-128e-instruct (NVIDIA API, 17B active parameters)
- allam-2-7b (Groq API, 7B parameters, Arabic-centric)

Earlier iterations attempted 3--5 model committees, but API instability forced reduction. The llama-3.3-70b model was dropped due to a 79% API failure rate; qwen3-32b and gemma2-9b failed pre-flight validation.

Each MCQ is evaluated under three prompting styles:
1. **Zero-shot**: Direct question with constraint to reply only with A, B, C, or D.
2. **Chain-of-thought (CoT)**: Model instructed to think step by step and write the final answer on the last line.
3. **Few-shot**: Two in-language examples precede the target question.

CoT is skipped for llama-4-maverick due to observed reasoning collapse (23 of 24 NaN predictions, 29% accuracy).

**Pre-flight health check:** Before the main evaluation, each model receives a trivial probe ("Reply with exactly the letter B"). Models failing this check are excluded. In v4.3.4, a three-attempt retry with 10-second sleep was added to handle transient timeouts.

### 4.6 Answer Extraction

Model outputs are parsed through a multi-stage extraction pipeline:
1. Strip `<think>` and `<reasoning>` tags.
2. First-character shortcut: if the response starts with A--D and is either a single character or followed by punctuation/whitespace, return immediately.
3. Fallback regex patterns (preferring last match to avoid reasoning-trace pollution): "answer is X," "Answer: X," "\boxed{X}," "FINAL ANSWER: X," and word-boundary `[A-D]`.

### 4.7 Encoder Baselines

Four multilingual encoder models provide zero-shot cosine-similarity baselines:
- mBERT (bert-base-multilingual-cased)
- XLM-RoBERTa (xlm-roberta-base)
- AraBERT (aubmindlab/bert-base-arabertv2)
- AfriBERTa (castorini/afriberta_large)

For each MCQ, the model computes mean-pooled embeddings for the proverb and each option. The option with highest cosine similarity to the proverb embedding is selected. These baselines establish a lower bound representing similarity-based retrieval without explicit reasoning.

### 4.8 Statistical Testing

**Position bias:** Chi-squared test with df = 3, requiring minimum n = 20. Tests whether accuracy differs significantly across answer positions A, B, C, D.

**McNemar's test:** Continuity-corrected chi-squared with df = 1, comparing Strategy 1 vs Strategy 2 accuracy per item. Run on all items and on non-fallback items separately.

**Bootstrap confidence intervals:** 1,000 resamples with 95% confidence level for S1 and S2-strict accuracy.

**Leakage heuristic:** Models with S1 accuracy >= 95% and S1-to-S2 drop >= 20 percentage points are flagged as HIGH leakage risk.

---

## 5. Results

### 5.1 Pilot Overview

The N = 150 pilot (50 proverbs per language) generated 300 MCQs and 1,500 API evaluations. Total runtime was approximately 22 minutes on Kaggle CPU. All checkpoints flushed successfully; no data loss occurred.

| Metric | Value |
|--------|-------|
| MCQs generated | 300 (150 S1 + 150 S2) |
| API evaluations | 1,500 (750 S1 + 750 S2) |
| Encoder evaluations | 1,200 (4 encoders x 300 each) |
| Total runtime | 1,320 seconds (~22 minutes) |
| Checkpoints saved | 7 (6 background + 1 final) |
| Figures generated | 6/6 |

### 5.2 Primary Accuracy Results

| Strategy | Accuracy | N | Bootstrap 95% CI |
|----------|----------|---|------------------|
| Strategy 1 (S1) | 86.8% | 750 | [84.3%, 89.2%] |
| Strategy 2 (strict) | 62.5% | 590 | [58.1%, 66.6%] |
| S2 fallback rate | 21.3% | 32/150 | -- |
| S2 fallback accuracy | 63.7% | 160 | -- |
| Random baseline | 25.0% | -- | -- |

McNemar's test confirms a statistically significant difficulty gap between S1 and S2 (chi-squared = 131.3, p < 0.001 for all items; chi-squared = 110.8, p < 0.001 for non-fallback items).

### 5.3 Per-Language Breakdown

| Language | S1 Accuracy | S2 Strict Accuracy | S2 Fallback Rate | S2 Items Evaluated |
|----------|-------------|--------------------|------------------|--------------------|
| English | 97.6% | 71.3% | 8.0% (4/50) | 46 |
| Arabic | 92.8% | 65.5% | 20.0% (10/50) | 40 |
| Yoruba | 70.0% | 46.2% | 36.0% (18/50) | 32 |

English shows the strongest performance and lowest fallback rate, consistent with high-resource language advantages. Arabic performs well on S1 but shows moderate fallback on S2. Yoruba exhibits the lowest S1 accuracy and highest S2 fallback, reflecting the challenges of low-resource figurative language generation.

### 5.4 Per-Model Breakdown

| Model | S1 Accuracy | S2 Accuracy | S1-to-S2 Drop | Leakage Signal | Error Rows |
|-------|-------------|-------------|---------------|----------------|------------|
| llama-4-maverick | 92.7% | 82.0% | 10.7 pp | LOW risk | 0 |
| allam-2-7b | 82.9% | 50.0% | 32.9 pp | No signal | 221 |

llama-4-maverick shows a modest 10.7 percentage point drop from S1 to S2, consistent with a strong model facing a harder task. allam-2-7b drops 32.9 percentage points, but the leakage heuristic flags no memorization signal, suggesting the drop reflects genuine reasoning difficulty with paraphrased distractors rather than contamination.

The 221 error rows for allam-2-7b (14.7% of all evaluations) are entirely attributable to Groq API rate limiting. No errors occurred for llama-4-maverick on NVIDIA.

### 5.5 Per-Style Breakdown

| Style | S1 Accuracy | S2 Accuracy |
|-------|-------------|-------------|
| Zero-shot | 91.7% | 72.7% |
| Chain-of-thought | 89.3% | 55.3% |
| Few-shot | 80.7% | 56.7% |

Zero-shot performs best. Few-shot shows lower accuracy, likely because the two synthetic examples (which use dummy distractors labeled "Wrong 1/2/3") do not calibrate the model effectively for the target task. CoT for S2 shows a sharp drop, consistent with reasoning challenges on adversarial distractors.

### 5.6 Position Bias

Pooled chi-squared tests show no significant position bias for either strategy (S1: p = 0.739, S2: p = 0.746). Stratified per-model tests are also non-significant (all p = 1.000). The position-shuffling mitigation is effective.

### 5.7 Encoder Baselines

| Encoder | S1 Accuracy | S2 Accuracy | S1 Gap vs API | S2 Gap vs API |
|---------|-------------|-------------|---------------|---------------|
| AfriBERTa | 56.7% | 30.0% | -30.1 pp | -32.8 pp |
| AraBERT | 54.0% | 29.3% | -32.8 pp | -33.5 pp |
| mBERT | 54.7% | 29.3% | -32.1 pp | -33.5 pp |
| XLM-R | 55.3% | 36.0% | -31.5 pp | -26.8 pp |

All encoders perform far below the API committee, confirming that the task requires reasoning beyond surface similarity. XLM-R shows the smallest S2 gap, possibly due to better cross-lingual representation.

### 5.8 Unanimous Consensus

| Strategy | Unanimous (Any) | Unanimous Correct | Unanimous Wrong | Split |
|----------|-----------------|-------------------|-----------------|-------|
| S1 | 82.0% (369/450) | 78.2% (352/450) | 3.8% (17/450) | 18.0% |
| S2 | 68.4% (308/450) | 45.8% (206/450) | 22.7% (102/450) | 31.6% |

S2 shows lower consensus, reflecting genuine disagreement between models on harder items rather than systematic bias.

---

## 6. Discussion

### 6.1 What Worked

The two-strategy design successfully creates a measurable difficulty gradient. S2 is significantly harder than S1 (McNemar p < 0.001), and the 24.3 percentage point gap confirms that cross-family paraphrasing produces meaningfully adversarial distractors. Position bias is effectively mitigated. The contamination filter removes known LLM training data. The pre-flight health check prevents silent model failures from corrupting results.

### 6.2 Negative Results and Lessons Learned

**Same-family exploitation.** Early iterations used llama-4-scout (Meta) as the generator and llama-3.3-70b (Meta) as an evaluator. The evaluator scored 57.8% on S2 versus 26.7% on S1---a smoking gun for stylistic fingerprint recognition (Panickssery et al., NeurIPS 2024). Switching to qwen3-32b (Alibaba) as the generator eliminated this bias.

**Chain-of-thought reasoning collapse.** CoT prompting caused catastrophic accuracy drops: 48.0% in pilot, 52.7% at N=50, versus 82--92% for zero-shot. For llama-4-maverick, CoT produced 23 of 24 NaN predictions. We now skip CoT for this model. This aligns with findings that reasoning traces can introduce noise when the task requires direct pattern matching rather than explicit deduction.

**API infrastructure fragility.** The project experienced multiple provider meltdowns: DeepInfra (402/404), SambaNova (all timeout), Cerebras (404), and Groq rate limiting (1,040 implied failures in the v4.3.4 run). The committee shrank from 5 models to 2. GPU local models failed entirely (ALLaM-7B garbled tokens, AfroLLaMA contamination suspicion, BLOOM-7B OOM). These failures motivated the hardened health-check retry, provider-cooldown retry, and dynamic worker-cap mechanisms in v4.3.4.

**kNN in-context learning.** Following Feng et al. (NAACL 2024), we experimented with kNN retrieval for distractor generation. While fallback was low (13.3%), outputs were broken---generating numeric options ("20", "23", "30", "22") for English proverbs. The limited retrieval corpus for low-resource languages made this approach unsuitable.

**Multi-Stage Prompting (MSP).** Maity et al. (ECIR 2024) propose MSP for multilingual distractor generation. Our implementation achieved 0% fallback but generated explanations rather than style-matched paraphrases, resulting in trivial 100% accuracy. MSP is unsuitable for hard distractor generation.

### 6.3 Limitations

1. **Committee size.** The current committee has only 2 models due to API instability. A 3--5 model committee would improve consensus robustness.
2. **API failure rate.** The 14.7% failure rate for allam-2-7b, while absorbed by retry logic, indicates provider capacity constraints that may worsen at scale.
3. **Yoruba S2 quality.** The 36% hard-fallback rate for Yoruba suggests that qwen3-32b struggles with low-resource figurative language paraphrasing. This may require language-specific prompt tuning or hybrid rule-based fallbacks.
4. **No human evaluation.** Following KNIGHT (2025), a minimum of 100 human-audited items for validity (unambiguity, answerability, option uniqueness) is desirable but not yet performed.
5. **Missing languages.** French, German, and Spanish proverbs are collected but not yet benchmarked.

---

## 7. Future Work and the Remaining 10%

The ProverbGap pipeline is approximately 90% complete for the MCQ benchmark. The remaining 10% comprises:

### 7.1 Scale to N = 700

The immediate next phase is scaling from N = 150 to N = 700 proverbs per language. Projected runtime at current settings is approximately 1.7 hours---well within Kaggle's 9-hour limit. To manage Groq rate limiting at scale, we will:
- Reduce concurrent workers from 8 to 4--5 for the allam-2-7b evaluation stream.
- Add jitter to retry sleep intervals.
- Consider provider rotation (NVIDIA, OpenRouter) for allam-2-7b if Groq limits become prohibitive.

### 7.2 Additional Languages

French (161 proverbs), German (142), and Spanish (63) are already collected and cleaned. Integration requires only updating the LANGUAGES list and verifying S2 generation quality for each new language.

### 7.3 Fill-in-the-Blank (FiB) Task

Following ProverbEval (NAACL 2025) and PRONE (CODI 2025), we plan to add a fill-in-the-blank variant where the model must complete a proverb given partial context. This tests recall and cultural knowledge rather than discrimination, providing a complementary evaluation dimension.

### 7.4 Generation Task

A generation task will ask models to explain the meaning of a proverb in context. This tests deeper comprehension beyond multiple-choice discrimination and enables human evaluation of explanation quality.

### 7.5 Human Evaluation

Per KNIGHT (2025), we will conduct a human audit of 100 items (30 per strategy per language) for unambiguity, answerability, and option uniqueness. This is essential for reviewer acceptance at venues like EMNLP.

### 7.6 Embedding-Based Distractor Diversity

We will add embedding-based diversity scoring for S2 distractors, following Joint Generation of Distractors (CMC 2025) and Eval4NLP (Gales et al., 2023), to ensure generated options are semantically distinct from each other.

---

## 8. Conclusion

We present ProverbGap, a cross-lingual MCQ benchmark for proverb understanding with an adversarial two-strategy distractor generation pipeline. Our N = 150 pilot demonstrates a statistically significant difficulty gap between baseline negative sampling (86.8%) and cross-family paraphrased distractors (62.5%), with strong performance on English and Arabic but expected degradation on low-resource Yoruba. Through extensive negative results, we document critical vulnerabilities in LLM-based evaluation---same-family exploitation, reasoning collapse, and API fragility---and present hardened mitigations including pre-flight validation, position-bias testing, and leakage detection. The pipeline is ready for scaling to N = 700, with fill-in-the-blank and generation tasks planned as future extensions.

---

## References

Alhazmi, A., et al. (2024). A Survey on Automated Distractor Generation for Multiple-Choice Questions. *EMNLP 2024*.

Azime, T., et al. (2025). ProverbEval: Benchmarking Proverb Understanding for Ethiopian Languages. *NAACL 2025 Findings*.

Dubois, Y., et al. (2025). Optimal Sampling for Detecting LLM-Generated Text. *EMNLP 2025 Findings*.

Du, M., et al. (2022). Shortcut Learning of Large Language Models in Natural Language Understanding. *arXiv preprint*.

Fernandez, N., et al. (2024). DiVERT: Distractor Generation with Variational Errors Represented as Text. *EMNLP 2024*.

Gales, M., et al. (2023). Automated Assessment of Distractor Quality for Multiple-Choice Reading Comprehension. *Eval4NLP Workshop*.

Gu, L., et al. (2024). LLM-as-a-Judge: A Comprehensive Survey. *arXiv preprint*.

Gurram, S., et al. (2026). AgentProp-Bench: Benchmarking LLM Judge Reliability. *arXiv preprint*.

Gupta, A., et al. (2024). The Impact of Answer Position on LLM Performance in Multiple-Choice Questions. *arXiv preprint*.

Krishna, K., et al. (2023). Paraphrasing Evades Detectors of AI-Generated Text, but Retrieval is an Effective Defense. *NeurIPS 2023*.

Maity, S., et al. (2024). Multi-Stage Prompting for Multilingual Distractor Generation. *ECIR 2024*.

Panickssery, A., et al. (2024). LLM Evaluators Recognize and Favor Their Own Generations. *NeurIPS 2024*.

Sun, Y., et al. (2025). Cross-Family Detection of LLM-Generated Text. *CMU/Bosch*.

Yang, M., et al. (2025). How Is LLM Reasoning Distracted by Irrelevant Context? *EMNLP 2025*.

Zhao, J., et al. (2025). Language Model Council: Heterogeneous Judge Pools Improve Ranking Robustness. *NAACL 2025*.

Zheng, K., et al. (2024). Large Language Models Are Not Robust Multiple Choice Selectors. *ICLR 2024 Spotlight*.

Zhou, Y., et al. (2024). Navigating the Shortcut Maze: A Comprehensive Analysis of Shortcut Learning in Text Classification. *EMNLP 2024 Findings*.

Ackerman, K., and Panickssery, A. (2025). Family-Specific Fingerprints in Chat and Instruct Models. *ICLR 2025*.

BEA (2025). Workshop on Innovative Use of NLP for Building Educational Applications.

CMC (2025). Joint Generation of Distractors for Multiple-Choice Questions. *CMC 2025*.

D-GEN (2025). Controlled Distractor Generation with Semantic Constraints. *ACL 2025 Findings*.

DG Survey (2024). A Survey on Automated Distractor Generation. *arXiv preprint*.

DISTO (2024). In-Domain Negative Sampling for Distractor Generation. *EDM 2024*.

EACL (2026). Egyptian Arabic Idioms: A Pragmatics Gap Analysis. *EACL 2026*.

Jawaher (2025). Large-Scale Arabic Proverb Dataset with Dialectal Coverage. *NAACL 2025 Long Papers*.

Kalhor, A., et al. (2026). MasalBench: Persian Proverb Understanding Benchmark. *arXiv preprint*.

PRONE (2025). Nepali Proverb Evaluation with Human-Written Distractors. *CODI 2025*.

Roundtable Policy (2025). Confidence-Weighted Consensus for LLM Evaluation. *arXiv preprint*.

SEFD (2025). Semantic Similarity as a Robustness Metric for Paraphrased Text. *PMC 2025*.

SemEval (2025). Hallucination Detection via Semantic Similarity. *SemEval 2025*.

---

*This is a working draft. All metrics reflect the v4.3.4 Kaggle pilot run (run_20260523_224443) using N=150 items (50 per language) sampled from the full 7,172-proverb collection. Figures and tables are generated from empirical data. Human evaluation and N = 700 scaling are in progress.*
