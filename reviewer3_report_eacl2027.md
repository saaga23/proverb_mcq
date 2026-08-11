# Reviewer #3 Report — Literature, Novelty & Venue/Category Fit
**Paper:** ProverbGap: Hardened Adversarial Distractor Generation for Low-Resource Figurative Language  
**Venue:** EACL 2027 ARR Submission  
**Date:** 2026-07-12

---

## Executive Summary
The paper presents a principled methodology (hardened distractor generation + blind options-only audit) applied to 180 proverb MCQs in English, Arabic, and Yoruba. The failure taxonomy and cross-lingual asymmetry findings are genuine contributions. However, the related-work coverage has a **critical misattributed citation** ("Kang et al." → actually Lee et al.), **omits the closest proverb benchmark** (MAPS, NAACL 2024), and **under-situates its LLM-as-judge claims** against a crowded 2025–2026 literature. The novelty is honest and incremental but real; the category fit is acceptable but needs sharper positioning. Most issues are **Major** fixes, not reject-level.

---

## (a) Citation-Accuracy Audit: Real vs. Suspect

| Citation | Status | Verdict |
|----------|--------|---------|
| Azime et al. (2025) *ProverbEval*, NAACL 2025 Findings | ✅ **REAL** | arXiv:2411.05049; ACL Anthology 2025.findings-naacl.350. Correctly characterized: 4 Ethiopian languages + English, 3 tasks, 50% choice-order variance. |
| Magdy et al. (2025) *JAWAHER*, NAACL 2025 Long | ✅ **REAL** | ACL Anthology 2025.naacl-long.613; arXiv:2503.00231. 10,037 Arabic proverbs, 20 dialects. Correctly characterized. |
| Kalhor & Bahrak (2026) *MasalBench*, arXiv:2601.22050 | ✅ **REAL** | arXiv published 29 Jan 2026. Persian proverb benchmark, contextual + cross-cultural. Correctly characterized. |
| Balepur & Rudinger (2024) *Choices-Only Cheater*, arXiv:2407.01992 | ✅ **REAL** | Published at 1st KnowLLM Workshop (2024). Correctly characterized: Kendall's τ ≈ 0.9 between choices-only and full-question ranks. |
| Balepur, Rudinger & Boyd-Graber (2025) ACL 2025 Long | ✅ **REAL** | ACL Anthology 2025.acl-long.169; arXiv:2502.14127. "A) Forced B) Flawed C) Fixable D) All of the Above." Correctly characterized. |
| Wang et al. (2025) COLING 2025 | ✅ **REAL** | ACL Anthology 2025.coling-main.390; arXiv:2402.01349. "LLMs May Perform MCQA by Selecting the Least Incorrect Option." Correctly characterized: 84–99% confidence on unselected options. |
| Fernandez et al. (2024) *DiVERT*, EMNLP 2024 | ✅ **REAL** | ACL Anthology 2024.emnlp-main.512. Variational errors-as-text for math distractors. Correctly characterized. |
| Alhazmi et al. (2025) EMNLP 2025 | ⚠️ **REAL BUT IMPRECISE** | Actual venue: **Findings of EMNLP 2025** (2025.findings-emnlp.533), not main EMNLP. Characterized correctly as contrastive learning for distractors. |
| Muhammad et al. (2025) *BRIGHTER*, ACL 2025 Long | ✅ **REAL** | ACL Anthology 2025.acl-long.436; arXiv:2502.11926. Multi-label emotion, 28 languages. Correctly characterized. |
| Xuan et al. (2025) *MMLU-ProX*, EMNLP 2025 | ✅ **REAL** | ACL Anthology 2025.emnlp-main.79; arXiv:2503.10497. 29-language MMLU-Pro extension. Correctly characterized. |
| **Kang et al. (ACL 2025)** | 🚨 **FABRICATED / MISATTRIBUTED** | The actual paper *"Generating Plausible Distractors for Multiple-Choice Questions via Student Choice Prediction"* (ACL Anthology 2025.acl-long.1154; arXiv:2501.13125) is authored by **Yooseop Lee, Suin Kim, and Yohan Jo**. There is no author named "Kang." **This must be corrected immediately.** |

### Suspect / Missing Citations (Detailed in Section b)

---

## (b) 5–10 Must-Add Recent Papers with Real Citations

The following papers are highly relevant and expected by a literature reviewer. At minimum, **MAPS** and **Lee et al. (ACL 2025)** are essential.

### 1. MAPS — Multicultural Proverbs and Sayings
> **Liu, C. C., Koto, F., Baldwin, T., & Gurevych, I. (2024).** Are Multilingual LLMs Culturally-Diverse Reasoners? An Investigation into Multicultural Proverbs and Sayings. *NAACL 2024 Long Papers*.  
> ACL Anthology: [2024.naacl-long.112](https://aclanthology.org/2024.naacl-long.112/) | arXiv: [2309.08591](https://arxiv.org/abs/2309.08591)

**Why must-add:** 2,313 proverbs across 6 languages (English, German, Russian, Bengali, Mandarin, Indonesian) with conversational context and inference tasks. Directly comparable to ProverbGap; Liu et al. explicitly study culture gaps, memorization vs. reasoning, and negative questions. Cites 124+ times. **This is the single biggest omission in §2.1.**

### 2. Correction to "Kang et al." → Lee et al.
> **Lee, Y., Kim, S., & Jo, Y. (2025).** Generating Plausible Distractors for Multiple-Choice Questions via Student Choice Prediction. *ACL 2025 Long Papers*.  
> ACL Anthology: [2025.acl-long.1154](https://aclanthology.org/2025.acl-long.1154/) | arXiv: [2501.13125](https://arxiv.org/abs/2501.13125)

**Why must-add:** Fixes the fabricated "Kang et al." citation. The paper trains a pairwise ranker + DPO distractor generator on student choice data. Directly relevant to distractor plausibility.

### 3. Kinayat — Arabic Figurative Language & Pragmatic Use
> **Attia, M., Muhamed, A., Alkhamissi, M., Solorio, T., & Diab, M. T. (2026).** Beyond Understanding: Evaluating the Pragmatic Gap in LLMs' Cultural Processing of Figurative Language. *EACL 2026 Long Papers*.  
> DOI: [10.18653/v1/2026.eacl-long.341](https://doi.org/10.18653/v1/2026.eacl-long.341)

**Why must-add:** Evaluates 22 LLMs on Egyptian Arabic idioms, multidialectal Arabic proverbs, and English proverbs. Finds Arabic proverb accuracy 4.29% below English, pragmatic use 14.07% below understanding. Directly supports ProverbGap's cross-lingual findings. Released Kinayat dataset (325 Egyptian idioms).

### 4. FFE-Hallu — Persian Figurative Hallucination Benchmark
> **Hosseini, F., Yousefzadeh, M., & Yaghoobzadeh, Y. (2026).** FFE-Hallu: Hallucinations in Fixed Figurative Expressions: A Benchmark of Idioms and Proverbs in the Persian Language. *EACL 2026 Long Papers*.  
> DOI: [10.18653/v1/2026.eacl-long.241](https://doi.org/10.18653/v1/2026.eacl-long.241)

**Why must-add:** Directly complements MasalBench. Studies figurative hallucination (authentic vs. fabricated idioms/proverbs) in Persian. Probes LLM-as-judge reliability for figurative language (Cohen's κ reported). Very recent, same venue family.

### 5. Alhazmi & Sheng et al. (2026) — Distractor Generation Follow-up
> **Alhazmi, E., Sheng, Q. Z., Zhang, W. E., et al. (2026).** Beyond Fine-Tuning: In-Context Learning and Chain-of-Thought for Reasoned Distractor Generation. *arXiv:2604.17574*.  
> arXiv: [2604.17574](https://arxiv.org/abs/2604.17574)

**Why should-add:** Direct follow-up to the cited EMNLP 2025 Findings paper. Studies ICL and CoT for distractor generation without fine-tuning — exactly the generation regime ProverbGap operates in.

### 6. GradQuiz — Adversarial Distractor Generation
> **Bonifazi, G., Buratti, C., Marchetti, M., Parlapiano, F., Traini, D., & Ursino, D. (2026).** Leveraging Adversarial Attacks to Generate Multiple-Choice Quizzes Robust Against Large Language Models. *ACM Transactions on Intelligent Systems and Technology*.  
> DOI: [10.1145/3803797](https://doi.org/10.1145/3803797)

**Why should-add:** Directly generates adversarial distractors via gradient-based perturbations, reducing LLM accuracy by up to 67% on MMLU. This is the closest prior work to ProverbGap's "adversarial hardening" goal. ProverbGap should position itself relative to this.

### 7. "Reliability without Validity" — LLM-as-Judge Systematic Evaluation
> **Unknown authors (2026).** Reliability without Validity: A Systematic, Large-Scale Evaluation of LLM-as-a-Judge Models Across Agreement, Consistency, and Bias. *arXiv:2606.19544*.  
> arXiv: [2606.19544](https://arxiv.org/abs/2606.19544)

**Why should-add:** 21 judges, 3 benchmarks, ~541k judgments. Key findings: kappa deflation of 33–41pp between exact match and Cohen's κ; consistency–bias paradox (high test–retest + high position bias); JudgeBench discriminates 4.5× more sharply than MT-Bench. Directly validates ProverbGap's blind audit design choices and κ reporting.

### 8. Sharma et al. (2025) — LLM Annotation Consistency
> **Sharma, N., Agarwal, N., & Sirts, K. (2025).** Towards Consistent Detection of Cognitive Distortions: LLM-Based Annotation and Dataset-Agnostic Evaluation. *arXiv:2511.01482*.  
> arXiv: [2511.01482](https://arxiv.org/html/2511.01482)

**Why should-add:** Reports Fleiss κ = 0.78 for GPT-4 across multiple runs on a subjective NLP task. Critical context for ProverbGap's κ = 0.4845 claim — shows that "moderate" κ can vary widely by task, model, and temperature.

### 9. "Right Answer, Wrong Score" — MCQA Evaluation Inconsistencies
> **Unknown authors (2025).** Right Answer, Wrong Score: Uncovering the Inconsistencies of LLM Evaluation in Multiple-Choice Question Answering. *ACL 2025 Findings*.  
> ACL Anthology: [2025.findings-acl.950](https://aclanthology.org/2025.findings-acl.950.pdf)

**Why should-add:** Studies how prompt constraints and answer-extraction strategies affect MCQA scores. Found that constrained prompts improve consistency but hide true capabilities. Relevant to ProverbGap's vote-extraction design.

### 10. "How Reliable is Multilingual LLM-as-a-Judge?"
> **Fu, X., & Liu, W. (2025).** How Reliable is Multilingual LLM-as-a-Judge? *arXiv:2505.12201*.  
> arXiv: [2505.12201](https://arxiv.org/html/2505.12201)

**Why should-add:** Reports average Fleiss κ ≈ 0.3 across 25 languages for LLM judges, with poor performance in low-resource languages. Directly contextualizes ProverbGap's cross-lingual audit findings.

---

## (c) Novelty Verdict

### What is genuinely new or incrementally novel:

1. **Failure taxonomy + pipeline locus mapping:** The six-mode taxonomy (§6) linking each failure to a specific pipeline component (generator, Gate 1, fallback sampler, committee) is a clear contribution. No prior distractor-generation paper documents systematic failure modes at this granularity.

2. **Blind options-only audit + position-bias calibration finding:** While Balepur & Ruding er and Wang et al. established that choices-only shortcuts exist, ProverbGap is the first to operationalize a blind options-only audit **as a distractor-quality screen** rather than an LLM-knowledge probe. The A-position 73.3% vs D-position 46.7% finding, and the decision to report it rather than hide it, is methodologically sound.

3. **Cross-lingual fallback asymmetry quantification:** The 3.5× Arabic/English fallback asymmetry (§7) and the prompt × resource interaction (adversarial-hard-negative 2.6×, adversarial-length-locked 5.2×) provide empirical evidence that "adversarial" prompting calibrated for English actively harms low-resource pipelines. This is a genuine insight.

4. **Cost-efficient reproduction artifacts:** Versioned model IDs, catalog snapshots, SHA256 hashes, and $0.85 total cost are useful for the reproducibility community.

### What is incremental or already covered:

1. **Distractor generation hardening:** NLI paraphrase filters, length parity, idiom blocklists, and duplicate repair are individually present in prior work (e.g., Lee et al. 2025 uses DPO for plausibility; Alhazmi et al. 2025 uses contrastive learning). ProverbGap's combination is novel, but each component is not.

2. **MCQA shortcut documentation:** Position bias, length bias, and choices-only effects are well-documented in Balepur & Rudinger (2024, 2025), Wang et al. (2025), and Zheng et al. (2024). ProverbGap confirms these in a new domain (proverbs, 3 languages) but does not discover a new shortcut mechanism.

3. **LLM-proxy IAA:** Seven LLMs annotating 60 items yields κ = 0.4845. This is useful but not groundbreaking; the literature already has κ = 0.3–0.78 range across tasks. The paper does not adequately benchmark its κ against comparable distractor-plausibility or figurative-language annotation studies.

### Honest Assessment:
The contribution is **incremental but legitimate**. It is strongest as a **methodology + failure-taxonomy paper** rather than a "here is a perfect benchmark" paper. The paper's own admission that 43.9% of MCQs require fallback and 27.8% are HCW actually strengthens its methodological honesty. Reviewers will appreciate the transparent negative results if framed correctly.

---

## (d) Recommended ARR Category and Venue-Fit Rationale

### Recommended Category: **ARR Long Paper**
**Primary Area:** `Resources and Evaluation`  
**Secondary Area:** `Multilinguality and Language Diversity` (or `NLP Applications`)

### Rationale:
- The paper presents a **reproducible methodology** (hardened pipeline) plus **evaluation artifacts** (180 MCQs, audit logs, failure taxonomy, analysis scripts). This fits `Resources and Evaluation`'s scope: "evaluation methodologies; datasets for low resource languages; reproducibility; statistical testing for evaluation."
- The cross-lingual gradient (Arabic 3.5× more fallbacks than English) and low-resource language focus (Yoruba) also align with `Multilinguality and Language Diversity`.
- EACL 2027's special theme is **"The Human in Language"**. The paper's eventual human-validation plan (§4.5, §10.6) and LLM-vs-human agreement analysis (§9) resonate with this theme, though the current draft is pre-human-validation.

### Alternative Consideration:
- **Short Paper:** Too narrow. The methodology, 6-mode taxonomy, and 3-language empirical analysis require more than 8 pages.
- **Theme Track:** Possible if the paper emphasizes the "human in the loop" angle more strongly (e.g., human validation as the central unsolved problem, with LLM audit as a necessary cheap screen). But this would require a rewrite.
- **Findings:** Not appropriate — the work is complete and self-contained.

### Venue-Fit Verdict:
**EACL 2027 Long Paper is correct.** The paper is within EACL's scope, the methodology is relevant to the NLP community, and the low-resource figurative-language angle fits European multilingualism interests. It is **not** strong enough for a top-tier benchmark splash (like ACL 2025) due to the failing quality gates, but it is strong enough for EACL as a **methodology + negative-result** contribution if framed honestly.

---

## (e) Ranked Critique List (by Severity)

### 🔴 REJECT / MAJOR (Must fix before acceptance)

#### 1. [CRITICAL] Fabricated/misattributed citation: "Kang et al. (ACL 2025)"
- **Problem:** The distractor-generation paper cited as "Kang et al. (ACL 2025)" is actually **Lee, Kim & Jo (ACL 2025)**. There is no author named Kang on that paper.
- **Fix:** Change all instances of "Kang et al." to "Lee et al." and update the References entry to:  
  `Lee, Yooseop, Suin Kim, and Yohan Jo. 2025. Generating Plausible Distractors for Multiple-Choice Questions via Student Choice Prediction. ACL 2025 Long.`
- **Severity:** **Major.** Fabricated citations are an immediate red flag for any reviewer and can trigger desk rejection or ethics investigation.

#### 2. [MAJOR] Missing closest related benchmark: MAPS (Liu et al., NAACL 2024)
- **Problem:** §2.1 claims ProverbEval, JAWAHER, and MasalBench are the related benchmarks, but **omits MAPS** — a 2,313-proverb, 6-language benchmark with conversational context and inference tasks, published at NAACL 2024 and cited 124+ times. MAPS is the single most comparable prior work.
- **Fix:** Add MAPS to §2.1. Characterize it accurately: Liu et al. study memorization vs. reasoning, culture gaps, and negative questions. Position ProverbGap as the first to study **adversarial distractor hardening** for proverbs, while MAPS studies **proverb reasoning evaluation**.
- **Severity:** **Major.** Any reviewer working on proverbs/figurative language will know MAPS. Omission suggests incomplete literature coverage.

#### 3. [MAJOR] Missing recent Arabic/figurative-language benchmarks: Kinayat (EACL 2026) and FFE-Hallu (EACL 2026)
- **Problem:** §2.1 claims no prior work applies adversarial hardening to proverb distractors, but ignores two 2026 benchmarks that directly study Arabic proverbs and Persian idioms/proverbs respectively.
- **Fix:** Add Kinayat (Attia et al., EACL 2026) to §2.1 as the closest Arabic proverb work; note that Kinayat finds Arabic proverb accuracy 4.29% below English. Add FFE-Hallu (Hosseini et al., EACL 2026) as related cross-lingual figurative-language work.
- **Severity:** **Major.** These are the most recent, most directly comparable papers. Not citing them signals the literature review was frozen before early 2026.

#### 4. [MAJOR] Under-situated LLM-as-judge / κ = 0.4845 claim
- **Problem:** §9 presents Fleiss κ = 0.4845 as "moderate agreement" without contextualizing it. Recent literature shows:  
  - Fu & Liu (2025): κ ≈ 0.3 across 25 languages for multilingual judges  
  - Sharma et al. (2025): κ = 0.78 for GPT-4 on subjective annotation  
  - "Reliability without Validity" (2026): κ deflation of 33–41pp between exact match and chance-corrected agreement  
  - "Coin Flip Judge" (2026): pairwise flip rates of 13.6%, position bias 72% A-majority
- **Fix:** In §9.3, contextualize κ = 0.4845 against comparable distractor-plausibility or figurative-language annotation studies. Explain why this magnitude is expected or surprising for proverb distractors. Consider reporting pairwise κ by language pair and model pair (not just pooled).
- **Severity:** **Major.** The κ claim is presented as a standalone contribution, but without context reviewers cannot assess whether 0.4845 is high, low, or typical.

#### 5. [MAJOR] Missing adversarial distractor generation baseline: GradQuiz (Bonifazi et al., 2026)
- **Problem:** §2.2 claims "no prior work applies adversarial hardening or blind audit" to proverb distractors, but **GradQuiz** (ACM TIST 2026) explicitly generates adversarial distractors via gradient-based attacks and reduces LLM accuracy by 67% on MMLU.
- **Fix:** Cite GradQuiz in §2.2 and position ProverbGap as complementary: GradQuiz uses white-box gradients; ProverbGap uses black-box LLM generation with semantic/structural validation. Acknowledge that GradQuiz targets general MCQA while ProverbGap targets figurative language.
- **Severity:** **Major.** GradQuiz is a direct competitor in adversarial distractor generation. Ignoring it weakens the novelty claim.

---

### 🟡 MINOR (Should fix; strengthens paper)

#### 6. [MINOR] Missing Alhazmi & Sheng et al. (2026) follow-up
- **Problem:** The paper cites Alhazmi et al. (EMNLP 2025) but not their 2026 follow-up on ICL/CoT for distractor generation — the exact generation regime ProverbGap uses.
- **Fix:** Add citation in §2.2 or §3.3. Briefly discuss how ProverbGap's prompt variants relate to ICL/CoT for distractor generation.

#### 7. [MINOR] BRIGHTER citation is weakly motivated
- **Problem:** §2.5 cites BRIGHTER (Muhammad et al., ACL 2025) as evidence that low-resource languages suffer performance drops. But BRIGHTER is an **emotion-recognition** dataset, not a proverb or figurative-language benchmark. The analogy is superficial.
- **Fix:** Keep the citation but soften the claim. Better yet, replace with MMLU-ProX (already cited) or Kinayat (newly added) which actually include Arabic/Yoruba proverb/MCQA results.

#### 8. [MINOR] Missing "Right Answer, Wrong Score" (ACL 2025 Findings) on evaluation inconsistencies
- **Problem:** §3.6 describes regex vote extraction but does not cite work showing that answer-extraction strategies systematically affect MCQA scores.
- **Fix:** Add "Right Answer, Wrong Score" (ACL 2025 Findings) to §2.3 or §3.6. It validates ProverbGap's choice of regex extraction as a conservative extractor.

#### 9. [MINOR] Fleiss κ = 0.4845 needs pairwise analysis by language
- **Problem:** Table 9.1 shows per-model accuracy by language, but the pooled κ = 0.4845 aggregates across all languages. Given that DeepSeek-R1-32B drops to 25% on Yoruba, the pooled κ may mask severe language-specific disagreement.
- **Fix:** Report Fleiss κ per language (EN, AR, YO) and per model pair. This will strengthen the cross-lingual analysis in §7.

#### 10. [MINOR] Self-consistency / "Coin Flip Judge" (2026) missing from audit methodology
- **Problem:** §3.6 describes a single-run, single-temperature audit. Recent work (Yagubyan 2026) shows that pairwise preferences flip 13.6% of the time on average, and 28% of questions exceed 20% flip rate.
- **Fix:** In §3.6 or §10.3, discuss whether single-run audit votes are sufficient. ProverbGap's 4-model committee partially mitigates this, but citing the "Coin Flip Judge" results would validate the design choice or motivate multi-run aggregation in future work.

---

## Additional Reviewer-Simulation Flags (Not in Ranked List)

### A. The "N=5 as Methodology Study" Defense
The paper frames itself as a methodology study to justify small N. This is reasonable, but reviewers will want to see **power analysis** or **planned sample-size justification** for the N=5 → N=15 scaling. The current draft mentions N=15 is "planned" but does not justify why N=5 was chosen as the pilot. Add a brief power calculation in §4 or §10.3.

### B. Reproducibility vs. API Volatility
The paper emphasizes reproducibility (§3.7, §10.4) but uses OpenRouter model IDs that may deprecate. The catalog snapshot is good, but reviewers will ask: **can others run this without OpenRouter credits?** Consider adding a Dockerfile or offline replay mode using saved raw outputs.

### C. Yoruba Data Provenance
The paper notes Owomoyela (2005) is copyrighted and excludes raw Yoruba proverbs from public release. This is transparent, but reviewers in low-resource NLP may view this as a **serious limitation** for reproducibility. Add a concrete plan (or actual progress) toward public-domain Yoruba proverb sources.

### D. Correct-Key Balance Deserves More Discussion
The perfect 45/45/45/45 balance is a strength, but combined with the A-position 73.3% accuracy, it suggests the committee is **systematically wrong about D** and **systematically right about A** — yet the balanced keys mask this in aggregate. This is actually a **finding**, not just a calibration note. Elevate it in §6.6.

---

## Summary Action Items

| Priority | Action | Section(s) |
|----------|--------|------------|
| **P0** | Fix "Kang et al." → "Lee et al." in text and References | All |
| **P0** | Add MAPS (Liu et al., NAACL 2024) to §2.1 | §2.1 |
| **P1** | Add Kinayat (Attia et al., EACL 2026) and FFE-Hallu (Hosseini et al., EACL 2026) to §2.1 | §2.1 |
| **P1** | Add GradQuiz (Bonifazi et al., 2026) to §2.2 | §2.2 |
| **P1** | Contextualize κ = 0.4845 against Fu & Liu (2025), Sharma et al. (2025), and "Reliability without Validity" (2026) | §9.3 |
| **P2** | Per-language Fleiss κ in §9.2 | §9.2 |
| **P2** | Add Alhazmi & Sheng et al. (2026) follow-up | §2.2 |
| **P2** | Soften BRIGHTER citation or replace with more relevant analogy | §2.5 |
| **P2** | Cite "Right Answer, Wrong Score" (ACL 2025 Findings) | §3.6 or §2.3 |
| **P2** | Add power analysis / sample-size justification for N=5 | §4 or §10.3 |

---

*Review completed. All citations verified via web search against ACL Anthology, arXiv, and DOI registries on 2026-07-12.*
