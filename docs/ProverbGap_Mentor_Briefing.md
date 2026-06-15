# ProverbGap: Busayou Review Document

**From Pilot to Scale: A Complete Journey**

**Version:** 1.0 | **Date:** May 2026

---

## A Note to Busayou

I want to sincerely apologize for the delay in delivering this document. What was meant to be a straightforward pipeline build turned into a much longer journey than anticipated, compounded by a hardware failure that stopped work entirely for several days. Below is an honest account of the obstacles encountered, so you understand why this took the time it did.

### Technical Problems Faced

1. **Yoruba data cleaning.** The Yoruba proverb collection required extensive normalization: inconsistent orthography, missing tonal marks, mixed dialects, and duplicate entries. This alone consumed far more time than budgeted.

2. **Same-family model exploitation.** Early runs used a Meta generator (llama-4-scout) and a Meta evaluator (llama-3.3-70b). The evaluator scored 57.8% on generated distractors versus 26.7% on human-written ones---not because it understood the proverbs, but because it recognized Meta's stylistic fingerprint. Fixing this required switching to a cross-family generator (qwen3-32b) and extensive literature review.

3. **GPU local models failed completely.** ALLaM-7B produced garbled tokens. AfroLLaMA showed suspicious memorization patterns (94.7% accuracy on easy questions). BLOOM-7B ran out of GPU memory. All three had to be abandoned, forcing a switch to API-only evaluation.

4. **API provider meltdown.** DeepInfra returned persistent 402/404 errors. SambaNova timed out on every request. Cerebras had wrong model IDs. Groq rate-limited aggressively, causing 15,131 HTTP errors in a single run. The committee shrank from 5 models to 2.

5. **Strategy 2 distractor quality crisis.** The fallback rate exploded to 37.8%. kNN retrieval generated nonsense numeric options. Multi-Stage Prompting produced explanations instead of paraphrases, making questions trivially easy. Fixing this required building a dual-gate validation system and iterative retry logic.

6. **Position bias was catastrophic.** Early pilots showed 85.6% accuracy when the correct answer was in position A, but only 64--67% for B/C/D. Models were exploiting position, not reading options. This required building deterministic rotation and per-model shuffling.

7. **Chain-of-thought reasoning collapse.** CoT prompting caused accuracy to drop from ~90% to ~50%. One model produced 23 of 24 NaN predictions under CoT. CoT had to be disabled for that model entirely.

8. **The v4.3.3 catastrophic regression.** After a successful v4.3.2 run, a single NVIDIA API timeout during health check excluded one model. All 8 worker threads then saturated the remaining Groq provider, causing 769 of 790 evaluations to fail. S1 accuracy collapsed from 85.4% to 24.2%. Recovery required adding health-check retries, provider-cooldown waits, and dynamic worker caps.

9. **Contamination detection.** Famous English proverbs ("A bird in the hand," "Actions speak louder than words") are likely in LLM training data, creating a memorization risk. A manual contamination filter had to be built and validated.

### Hardware Failure

My laptop cooling fan was damaged and stopped working completely. This halted all work for several days until the fan was repaired and the machine was usable again. Running Kaggle-scale evaluations and API tests on an overheating laptop was impossible.

### The Result

Despite these setbacks, the pipeline is now hardened, validated, and ready to scale. The document below reflects a complete, end-to-end system that has survived every failure mode described above.

---

## Executive Summary

ProverbGap is a cross-lingual benchmark that tests whether AI models truly understand proverbs---not just memorized phrases, but culturally embedded figurative language. We built it because existing benchmarks focus on English math and coding, while ignoring the wisdom sayings that carry cultural knowledge across generations.

This document tells the full story: where we started, what broke, how we fixed it, where we are now, and what comes next. It is written for Busayou and stakeholders who need the big picture without diving into every line of code.

---

## Part 1: The Journey (What We Built, What Broke, What We Learned)

### Chapter 1: The Beginning (Data Collection and Cleaning)

**What we did:**
We collected 7,172 proverbs across six languages: English (2,278), Arabic (913), Yoruba (3,931), French (161), German (142), and Spanish (63). Each entry includes the original text, an English translation, and a cultural explanation.

**The hardest part: Yoruba cleaning.**
Yoruba proverbs come from oral tradition collections with inconsistent formatting, missing tonal marks, and mixed dialects. We spent significant effort normalizing orthography, standardizing translations, and removing duplicate entries. The result: 3,931 clean Yoruba proverbs---the largest single-language collection in the dataset.

**What we learned:** Low-resource language data is never "ready." It requires manual curation, community validation, and tolerance for imperfection. The Yoruba collection is 4x larger than Arabic not by design, but because more ethnographic material was available. Note: the local CSV files are placeholder samples; the full 7,172-proverb dataset resides on Kaggle.

---

### Chapter 2: First Attempts (Early Methodology and Failures)

**The original idea was simple:** Build multiple-choice questions where the correct answer is the proverb's meaning, and distractors are wrong meanings. Test LLMs on these questions. Report accuracy.

**What broke immediately:**

1. **Position bias was catastrophic.** In our first pilot, models chose answer "A" 85.6% of the time when it was correct, but only 64--67% for positions B, C, and D. The models were not reading the options---they were exploiting position. We fixed this with deterministic rotation and per-model shuffling.

2. **Same-family exploitation.** We used a Meta model (llama-4-scout) to generate distractors, and another Meta model (llama-3.3-70b) to evaluate them. The evaluator scored 57.8% on generated distractors versus 26.7% on human-written ones. It was recognizing Meta's "writing style," not understanding the proverbs. We fixed this by switching to qwen3-32b (Alibaba) for generation---a different model family entirely.

3. **GPU models failed completely.** We tried running local models on Kaggle's GPU (ALLaM-7B, AfroLLaMA, BLOOM-7B). ALLaM produced garbled tokens. AfroLLaMA scored suspiciously high (94.7%) on easy questions but crashed on hard ones, suggesting memorization. BLOOM ran out of memory. We disabled all GPU models and switched to API-only evaluation.

---

### Chapter 3: The API Meltdown (Infrastructure Failures)

**The problem:** Running 5 models across 6 API providers sounds robust. In practice, it was a house of cards.

**What failed:**
- **DeepInfra:** Persistent 402 (payment required) and 404 (wrong model IDs).
- **SambaNova:** Every single request timed out.
- **Cerebras:** Wrong model IDs caused 404s for all requests.
- **Groq:** Rate limiting hit repeatedly, causing 15,131 HTTP 400 errors in one run.
- **NVIDIA:** Intermittent timeouts, especially on larger models.

**The committee shrank from 5 models to 3, then finally to 2.** qwen3-32b output thinking tags instead of answers. gemma2-9b returned full sentences. llama-3.3-70b suffered a 79% failure rate due to API errors. Only allam-2-7b (Groq) and llama-4-maverick (NVIDIA) remained reliable.

**What we learned:** API infrastructure for LLMs is fundamentally fragile. A benchmark pipeline must assume providers will fail and design for graceful degradation. We added pre-flight health checks, provider cooldown logic, automatic model exclusion, and SQLite caching to survive outages.

---

### Chapter 4: Strategy 2 Crisis (Distractor Quality)

**The goal:** Strategy 2 uses an LLM to paraphrase the correct meaning and generate subtle wrong meanings. This should be harder than Strategy 1 (sampling other proverbs as distractors).

**What went wrong:**
- **Fallback rate exploded to 37.8%.** The LLM kept generating distractors that were too short, too long, or semantically broken.
- **Yoruba was worst affected.** 43.3% of Yoruba S2 items fell back to placeholder distractors. The paraphrase model simply could not handle low-resource figurative language.
- **kNN retrieval failed.** We tried retrieving similar proverbs as distractor templates. It generated numeric options ("20", "23", "30") for English proverbs. Useless.
- **Multi-Stage Prompting (MSP) failed.** We tried a sophisticated prompting technique from the literature. It generated explanations instead of paraphrases, making the questions trivially easy (100% accuracy).

**How we fixed it:**
- Added a dual-gate validation system: length gate (within 35%) AND semantic gate (Jaccard similarity >= 0.25).
- Increased retries from 3 to 8 (12 for Yoruba).
- Added language-specific retry prompts.
- Fallback rate dropped from 37.8% to 21.3%.

---

### Chapter 5: The v4.3.3 Catastrophe (And Recovery)

**What happened:** After a successful v4.3.2 run (85.4% S1, 69.3% S2), we applied five "minor" fixes for v4.3.3. The result: S1 collapsed to 24.2%, S2 to 0.0%. The pipeline was effectively broken.

**Root cause:** Not the code fixes, but an infrastructure cascade. NVIDIA's API timed out during health check, excluding llama-4-maverick. All 8 worker threads then hammered Groq's allam-2-7b simultaneously, triggering rate limits. 769 of 790 evaluations failed. The models were not broken---the API was drowning.

**Recovery:** We added health-check retries (3 attempts), provider-cooldown retries (15-second wait), and dynamic worker capping (limit concurrency to available provider slots). v4.3.4 restored performance: 86.8% S1, 62.5% S2.

**Lesson:** Even "minor" infrastructure changes can cascade into total failure. Always test with reduced load first.

---

## Part 2: Current State (What Works Now)

### The Pipeline

The current pipeline is a self-contained Kaggle notebook that runs end-to-end in approximately 22 minutes for N=150 (50 proverbs per language). It performs the following steps:

1. **Load and filter data:** Remove contaminated English proverbs, sample 50 per language.
2. **Generate Strategy 1 MCQs:** Sample distractors from other proverbs in the same language.
3. **Generate Strategy 2 MCQs:** Use qwen3-32b to paraphrase meanings and generate adversarial distractors, with dual-gate validation.
4. **Evaluate with committee:** Two reliable models (llama-4-maverick, allam-2-7b) evaluate each MCQ under three prompting styles.
5. **Run encoder baselines:** Four multilingual BERT variants provide similarity-based baselines.
6. **Compute statistics:** Accuracy, position bias, McNemar test, bootstrap confidence intervals, consensus analysis, leakage heuristic.
7. **Generate figures:** Six publication-ready figures saved as PNG.

### Current Results (N=150 Pilot)

| Metric | Result |
|--------|--------|
| Strategy 1 accuracy | 86.8% |
| Strategy 2 strict accuracy | 62.5% |
| S2 fallback rate | 21.3% |
| Position bias | Not significant (p = 0.74) |
| McNemar S1 vs S2 | Significant (p < 0.001) |
| Runtime | ~22 minutes |

**Per language:**
- English: 97.6% S1, 71.3% S2, 8% fallback
- Arabic: 92.8% S1, 65.5% S2, 20% fallback
- Yoruba: 70.0% S1, 46.2% S2, 36% fallback

**What this means:** The pipeline works. S2 is genuinely harder than S1. English and Arabic perform well. Yoruba is challenging due to low-resource generation difficulties, which is expected and documented.

**Quick glossary for non-technical readers:**
- **S1 / S2:** Strategy 1 (easy baseline) vs Strategy 2 (hard adversarial questions).
- **Fallback:** When the AI fails to generate good distractors, we fall back to simple placeholder options.
- **McNemar test:** A statistical test that checks whether two strategies produce genuinely different difficulty levels.
- **Bootstrap CI:** A method to estimate the range within which the true accuracy likely falls.
- **Leakage heuristic:** A check to detect if a model has memorized answers from its training data.

### What is Validated

- Data quality: Zero empty options, zero duplicate options, zero answer-key errors.
- Position bias: Effectively eliminated.
- Leakage: No memorization signal detected.
- Reproducibility: Fixed seeds, deterministic shuffling, version-pinned code.

---

## Part 3: Next Phase (Scaling and Beyond)

### Phase 1: Scale to N = 700

**What:** Increase from 50 to 700 proverbs per language.
**Projected runtime:** ~1.7 hours (well within Kaggle's 9-hour limit).
**Risk:** Groq rate limiting will intensify. Mitigation: reduce concurrent workers and add retry jitter.
**Timeline:** 1--2 weeks (mostly waiting for Kaggle runs).

### Phase 2: Add Remaining Languages

French (161), German (142), and Spanish (63) proverbs are already collected. Integration requires only adding them to the language list and verifying S2 generation quality.

### Phase 3: Fill-in-the-Blank Task

In addition to multiple-choice, we will test models on fill-in-the-blank: given a partial proverb, complete it correctly. This tests recall and cultural memory, not just discrimination.

### Phase 4: Generation Task

Ask models to explain a proverb's meaning in context. This evaluates deeper comprehension and enables human judgment of explanation quality.

### Phase 5: Human Evaluation

Per best practices, 100 items will be manually audited for unambiguity, answerability, and option uniqueness. This is required for publication at top-tier venues.

---

## Part 4: Budget and Resource Recommendations ($50)

The current pipeline runs entirely on free API tiers and Kaggle's free CPU/GPU. However, scaling to N=700 will stress these limits. Here are tangible, essential investments:

### Recommended Purchases (Prioritized)

| Priority | Item | Cost | Why It Helps |
|----------|------|------|--------------|
| **P0** | Groq Pro tier (1 month) | ~$15 | Higher rate limits (100+ RPM vs 20 RPM free). Eliminates the 14.7% API failure rate that slows evaluation and risks timeouts. |
| **P0** | OpenRouter credits | ~$10 | Backup provider for allam-2-7b when Groq is saturated. Diversifies provider risk. |
| **P1** | Hugging Face Pro (1 month) | ~$9 | Faster model downloads for encoder baselines. Reduces Kaggle runtime overhead. |
| **P1** | Kaggle Notebooks Plus (1 month) | ~$10 | Longer runtime limits (12h vs 9h) and more GPU hours. Safety margin for N=700. |
| **P2** | DeepL API credits | ~$5 | Quality-check Arabic and Yoruba translations during human evaluation. |

**Total: ~$49** (within $50 budget)

### What This Buys

- **Reliability:** Groq Pro eliminates rate-limit failures, ensuring clean data.
- **Speed:** Higher rate limits + faster downloads = shorter runtime.
- **Redundancy:** OpenRouter fallback prevents single-provider catastrophic failure.
- **Safety margin:** Kaggle Plus provides buffer if N=700 takes longer than projected.

### What NOT to Spend On

- Expensive models (GPT-4, Claude Opus): Overkill for evaluation; current models are sufficient.
- Custom GPU servers: Kaggle's free T4 is adequate; pipeline is CPU-bound.
- Professional translation services: Not needed for benchmark construction; DeepL is sufficient for validation.

---

## Timeline

| Week | Activity |
|------|----------|
| 1 | Secure $50 budget; set up Groq Pro and OpenRouter accounts |
| 2 | Run N=700 pilot on Kaggle with hardened pipeline |
| 3 | Validate results; add French, German, Spanish |
| 4 | Build fill-in-the-blank task; run pilot |
| 5 | Build generation task; run pilot |
| 6 | Conduct human evaluation (100 items) |
| 7 | Finalize paper draft; submit to EMNLP/ACL |

---

## Conclusion

ProverbGap has progressed from a fragile prototype with 5 models and 37.8% fallback rates to a hardened, reproducible pipeline with 2 reliable models, 21.3% fallback, and statistically validated results. The journey involved multiple catastrophic failures---same-family exploitation, API meltdowns, reasoning collapse---each of which taught a lesson that improved the pipeline.

The remaining work is scaling, extension, and validation. The core methodology is locked. The code is stable. The results are trustworthy.

With a small $50 investment in API reliability, we can complete the N=700 benchmark, add fill-in-the-blank and generation tasks, conduct human evaluation, and submit to a top-tier NLP venue within 7 weeks.

---

*Document prepared from project memory files, audit reports, and Kaggle run logs. All metrics verified against empirical data from run_20260523_224443.*
