#### 1. Introduction

Large language models (LLMs) are increasingly evaluated on figurative language understanding, yet the construction of high-quality multiple-choice questions (MCQs) for figurative language remains underdeveloped. Existing proverb benchmarksâ€”ProverbEval (Azime et al., NAACL 2025), JAWAHER (Magdy et al., NAACL 2025), and MasalBench (Kalhor & Bahrak, 2026)â€”release MCQs without systematic adversarial validation of distractors. As a result, these benchmarks may contain surface shortcuts, length biases, or culturally mismatched options that inflate model accuracy without measuring genuine proverb understanding.

We present ProverbGap, a hardened adversarial distractor-generation pipeline applied to English, Arabic, and Yoruba proverbs. Rather than releasing another benchmark, we treat benchmark construction itself as the research question: *How do we build and audit proverb MCQs that resist shortcut solutions?* Our pipeline combines a dynamic multi-model generator pool, four adversarial prompt variants, dual-gate semantic validation (NLI paraphrase filter, correct-meaning leak sanitizer, length parity, idiom blocklist), and a heterogeneous four-model blind audit committee that sees only the four answer options.

Systematic failure-mode documentation reveals that the corpus-based fallback sampler is the critical bottleneck: 43.9% of 180 generated MCQs require at least one fallback replacement, and high-consensus-wrong (HCW) items reach 27.8%. NLI and leak filters account for 71% of all replacements, while length filters account for only 15%, indicating semantic over-filtering rather than structural mismatch. The audit committee itself exhibits position bias (A-position accuracy 73.3% vs D-position 46.7%), confounding consensus metrics. A cross-lingual gradient emerges: Arabic requires 3.5Ã— more fallback replacements than English (mean 1.52 vs. 0.43 per MCQ), suggesting that the pipeline is calibrated for high-resource languages and aggressively rejects model output for morphologically complex, low-training-density languages.

Our contributions are:
1. A reproducible, cost-efficient pipeline for hardened adversarial distractor generation ($0.0047 per audited MCQ).
2. A systematic failure taxonomy linking each failure mode to a specific pipeline component.
3. Empirical evidence that adversarial paraphrasing fails to transfer difficulty cross-lingually: Arabic and Yoruba suffer from corpus-fallback quality collapse while English remains trivially easy.
4. A public testbed of 180 MCQs with full audit logs, raw outputs, and analysis scripts.

We release the pipeline, audit logs, and 180 MCQs as a testbed for reproducible distractor-generation research.

**Paper structure:** Section 2 positions our work against proverb benchmarks, distractor-generation literature, and LLM-as-judge audit methods. Section 3 details the hardened pipeline. Section 4 describes the dataset and experimental setup. Section 5 presents main results. Section 6 documents the failure taxonomy. Section 7 analyzes cross-lingual fallback asymmetry. Section 8 reports baselines and robustness tests. Section 9 presents the LLM-proxy inter-annotator agreement study. Sections 10â€“11 discuss limitations and conclusions.

---


