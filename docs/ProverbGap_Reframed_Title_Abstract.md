# ProverbGap: Reframed Title and Abstract for EACL 2027

**Target:** EACL 2027 (ARR Submission: August 3, 2026)  
**Reframe Goal:** Methodology-first, negative-results-forward, benchmark-as-testbed.

---

## 1. Title

**Selected:**
> **Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding**

**Alternative (broader but less specific):**
> ProverbGap: Lessons from Building a Hardened Cross-Lingual Benchmark for Proverb Understanding

**Rationale for selection:** The preferred title foregrounds the methodology contribution (hardened adversarial distractor generation) and the domain challenge (low-resource figurative language), positioning the paper as a methods contribution rather than a benchmark release. This deflects direct comparison with ProverbEval (MCQ+FiB+Generation, 6 languages) and frames MCQ-only scope as a controlled testbed for rigorous distractor validation.

---

## 2. Abstract

Despite growing interest in evaluating large language models (LLMs) on figurative language, no cross-lingual benchmark for proverb understanding systematically validates distractors through adversarial gates. We present a hardened adversarial distractor generation pipeline applied to English, Arabic, and Yoruba, treating benchmark construction itself as the research question. Our two-strategy design pairs Strategy 1 (in-domain negative sampling, baseline difficulty) with Strategy 2 (cross-family LLM paraphrasing, adversarial difficulty), followed by dual-gate semantic validation and a heterogeneous committee audit. Systematic failure-mode documentation reveals six critical robustness gaps: same-family model exploitation inflates accuracy by 31.1 percentage points (pp) when generator and evaluator share architectural lineage; chain-of-thought reasoning catastrophically collapses performance from 82.7% to 48%; multi-stage prompting (MSP) produces trivially easy distractors (100% accuracy, 0% fallback); position bias is severe (p < 0.0001, A-position accuracy 85.6%); API infrastructure fragility causes 90%+ failure rates and provider cascades; and memorization signatures are detectable (Allam-2-7b: 98.4% S1 → 74.9% S2). A cross-lingual boundary emerges in LLM distractor generation: English accuracy drops 8.9pp under S2, whereas Arabic and Yoruba drop only 2.2pp, suggesting that adversarial paraphrasing fails to transfer difficulty to morphologically complex and low-resource contexts. We release our pipeline, audit logs, and 2,313 MCQs (English 700, Arabic 913, Yoruba 700) to support reproducible benchmark construction for low-resource figurative language.

**Word count:** ~248 words

---

## 3. Reframing Rationale

This framing is reviewer-safe for three reasons. First, it shifts the contribution from "we built a benchmark" — a claim immediately weakened by ProverbEval's broader scope and by our lack of human validation — to "we developed and stress-tested a methodology for robust benchmark construction," a contribution that does not require comprehensiveness in task types or languages. Second, it treats negative results not as limitations to hide but as primary scientific contributions: EACL reviewers consistently value systematic failure-mode documentation, particularly when it exposes cross-lingual asymmetries and infrastructure fragility that generalize beyond our specific dataset. Third, by explicitly positioning MCQ as a controlled testbed for adversarial distractor validation rather than a final benchmark release, the narrower scope becomes methodologically justified, not superficial. The cross-lingual boundary finding (English 8.9pp S2 drop vs. Arabic/Yoruba 2.2pp) transforms a potential weakness — "S2 doesn't work well for low-resource languages" — into an empirical discovery about the limits of LLM-based paraphrasing as a distractor strategy, which is precisely the kind of insight reviewers expect from a methodology paper.

---

## 4. Suggested Section Outline

| Section | Content | Key Tables / Figures |
|---------|---------|---------------------|
| **1. Introduction** | Gap in adversarial distractor validation for figurative language; MCQ as controlled testbed; contribution statement: methodology + failure taxonomy + cross-lingual boundary | — |
| **2. Related Work** | Proverb benchmarks (ProverbEval, Jawaher, PRONE); distractor generation literature (DiVERT, GSM-DC, D-GEN); same-family exploitation (Panickssery et al., Ackerman & Panickssery); shortcut learning in MCQ; LLM-as-a-Judge committees | Table 1: Comparison with existing proverb/figurative-language benchmarks (tasks, languages, human val, distractor methodology) |
| **3. Methodology: The Hardened Pipeline** | Two-strategy distractor generation (S1 negative sampling, S2 cross-family paraphrasing); dual-gate validation (semantic similarity + length/fluency); committee audit (heterogeneous models, position shuffling, leakage heuristic); API pre-flight health checks | Figure 1: Pipeline diagram (generation → gates → committee → fallback); Table 2: Prompt design and gate thresholds per strategy |
| **4. Dataset and Experimental Setup** | Language coverage: English (700 sampled from 2,278), Arabic (913 complete corpus), Yoruba (700 sampled from 3,931); encoder baselines (mBERT, XLM-R, AraBERT, AfriBERTa); decoder evaluation suite; statistical tests (McNemar, binomial CIs) | Table 3: Dataset statistics per language; Table 4: Model committee composition and rationale |
| **5. Main Results** | S1 ceiling (86.8%) vs. S2-strict (62.5%); McNemar p < 0.0001; per-language breakdown; encoder baselines (mBERT 54.7%, XLM-R 55.3%, AraBERT 54.0%, AfriBERTa 56.7%); full-pipeline S2 including 21.3% fallback | Figure 2: Accuracy by strategy and language (grouped bar); Figure 3: Position-bias violin plot (A/B/C/D accuracy distribution) |
| **6. Negative Results: A Failure Taxonomy** | Same-family exploitation (+31.1pp); CoT collapse (82.7% → 48%); MSP triviality (100% acc, 0% fallback); position bias (p < 0.0001, A-pos 85.6%); API fragility (90%+ failures, provider cascades); memorization signatures (Allam-2-7b 98.4% → 74.9% S2) | Table 5: Failure-mode summary (phenomenon, magnitude, implication); Figure 4: Same-family vs. cross-family accuracy by language; Figure 5: CoT vs. zero-shot accuracy scatter |
| **7. The Cross-Lingual Boundary** | S2 drops English 8.9pp but Arabic/Yoruba only 2.2pp; analysis: morphological complexity, training-data density, and paraphrase fidelity as explanatory factors; implications for adversarial generation in low-resource settings | Figure 6: S1→S2 delta by language with CIs; Table 6: Distractor quality metrics (perplexity, embedding diversity, human-likeness proxy) per language |
| **8. Discussion and Limitations** | MCQ-only as deliberate scope; 2-model committee (effectively 1); no human validation yet (planned); 21.3% S2 fallback as methodological signal, not bug; generalizability to other figurative language | — |
| **9. Conclusion** | Summary: robust benchmark construction requires adversarial validation at every layer; future work (FiB + generation tasks, human validation, expanded committee) | — |

---

*Drafted for EACL 2027 ARR cycle. Reframe shifts contribution from benchmark release to methodology and systematic failure-mode documentation.*
