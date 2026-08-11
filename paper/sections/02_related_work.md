#### 2. Related Work

### 2.1 Proverb and Figurative-Language Benchmarks

ProverbEval (Azime et al., 2025) is the most closely related benchmark: it covers 6 languages (4 Ethiopian + English) with three tasks (MCQ, fill-in-the-blank, generation) and reports that answer-choice order causes up to 50% accuracy variance. However, ProverbEval does not validate distractors through adversarial gates or blind audit. JAWAHER (Magdy et al., 2025) covers 20 Arabic dialects with expert human annotation and GPT-4o as an LLM judge, but its MCQ component lacks difficulty control or shortcut resistance. MasalBench (Kalhor & Bahrak, 2026) evaluates Persian proverb identification but does not analyze distractor quality.

These benchmarks share a common gap: they treat MCQ construction as a data-collection task rather than a methodological challenge. ProverbGap explicitly addresses this gap by making distractor validation the primary scientific contribution.

### 2.2 Distractor Generation

Distractor generation for MCQs has shifted from rule-based templates to LLM-based approaches. DiVERT (Fernandez et al., EMNLP 2024) uses a variational "errors-as-text" representation and shows that a 7B open LLM can beat GPT-4o on math distractor quality. Kang et al. (ACL 2025) train a distractor generator on real student-choice data using DPO, achieving human-expert-level ranking. Alhazmi et al. (EMNLP 2025) apply contrastive learning to align question-answer-distractor semantics.

For proverb-specific distractor generation, no prior work applies adversarial hardening or blind audit. Our work fills this gap by combining dynamic multi-model generation with a disjoint audit committee and explicit failure-mode documentation.

### 2.3 LLM-as-Judge and Options-Only Audit

Balepur & Rudinger (ACL 2025) argue that MCQA is flawed in format and datasets, proposing Item Response Theory and constructed-response alternatives. Their "choices-only cheater" lineage (Balepur & Rudinger 2024) shows that Kendall's Ï„ â‰ˆ 0.9 between choices-only and full-question ranks, suggesting models rely heavily on option content.

Wang et al. (COLING 2025) show that LLMs treat unselected options as 84â€“99% as confident as the correct one, proposing MCQA+ augmentations to expose this weakness.

We adopt a blind options-only audit not as a substitute for human validation, but as a necessary shortcut screen. Our four-model heterogeneous committee reduces same-family exploitation; we note one residual family overlap (a Google generator and a Google auditor) and rely on the blind options-only design — auditors never see generator identity or outputs — to limit stylistic contamination. We explicitly report position bias as a calibration finding rather than hiding it.

### 2.4 Shortcut Learning in MCQA

Position bias, length bias, and lexical overlap are well-documented shortcuts in MCQA. ProverbEval (Azime et al., 2025) found 50% accuracy variance from choice order. Our work confirms position bias in the audit committee (A-position 73.3% vs D-position 46.7%), but shows that balanced key distribution neutralizes it in aggregate metrics.

### 2.5 Cross-Lingual Evaluation Gaps

MMLU-ProX (Xuan et al., EMNLP 2025) and BRIGHTER (Muhammad et al., ACL 2025) show that African and low-resource languages suffer severe performance drops in multilingual evaluation. Our cross-lingual fallback asymmetry finding (Arabic 3.5Ã— more replacements than English) aligns with this literature: pipeline components calibrated for English fail silently on morphologically complex languages.

---


