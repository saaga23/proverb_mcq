# Literature Review Scratch Notes — ProverbGap MCQ (2026-07-10)

## Search queries run
1. ProverbEval proverb understanding benchmark low-resource 2025 ACL
2. MasalBench Jawaher proverb benchmark Arabic LLM 2025
3. LLM-based distractor generation MCQ 2025 EMNLP
4. LLM-as-judge options-only audit shortcut detection MCQA 2025
5. MasalBench Persian proverbs 2025/2026
6. cross-lingual evaluation gap low-resource LLM 2025 EMNLP ACL
7. human validation annotation standards NLP dataset 2025 native speaker
8. adversarial distractor generation MCQ shortcut-resistant 2025
9. Balepur 2025 "Which of These Best Describes MCQA" ACL abstract

## TOPIC 1 — PROVERB UNDERSTANDING BENCHMARKS

### [P1] ProverbEval
- Azime, Tonja, Belay, Chanie, Balcha, Abadi, et al.
- NAACL 2025 Findings. https://aclanthology.org/2025.findings-naacl.350 / arXiv 2411.05049
- 4 Ethiopian low-resource languages (Amharic, Tigrinya, Ge'ez written in Ethiopic script; Oromo) + English.
- 3 tasks: (1) meaning multiple-choice (4 options, detailed explanation each, 1 correct); (2) fill-in-the-blank; (3) generation (proverb given description).
- HUMAN ANNOTATION: Yes — volunteer annotators (co-authors) collected proverbs, wrote native+English explanations, verified correctness. Data public domain proverbs.
- METHODS: lm-eval harness; log-likelihood + generation for open-source; accuracy for MC; chrF/BLEU/TER for generation; GPT-4o for closed.
- METRICS: accuracy, chrF.
- KEY FINDINGS: up to ~50% accuracy variance from choice ORDER in MC; native-language prompts LOWER accuracy than English prompts; monolingual generation > cross-lingual; tokenization/fertility matters (Ge'ez script worse); translating proverbs to English does NOT help low-resource models.
- GAPS: small/Geez data thin (Ge'ez descriptions done via Amharic); no systematic human evaluation of option quality; MC task inherited from lm-eval so choice-order sensitivity unmitigated.

### [P2] JAWAHER
- Magdy, Kwon, Alwajih, Abdelfadil, Shehata, Abdul-Mageed.
- NAACL 2025 Long. https://aclanthology.org/2025.naacl-long.613 / arXiv 2503.00231
- 10,037 Arabic proverbs, 20 Arabic dialects, paired with idiomatic/literal English translations + explanations (Arabic & English).
- Tasks: translation, explanation (Arabic & English), contextualization.
- HUMAN ANNOTATION: Yes — 2 expert annotators (linguistics + translation degrees) for human eval on 1–5 scales (translation accuracy/idiomaticity; explanation clarity, depth, correctness, cultural relevance).
- METHODS: zero-shot mLLMs (open + closed); GPT-4o as LLM-judge (LangChain string evaluator).
- METRICS: BLEURT, BERTScore-F1 (auto); human 1–5; GPT-4o judge.
- KEY FINDINGS: models produce idiomatically correct translations but STRUGGLE on culturally-nuanced explanations (historical/cultural context). Closed-source > open-source but both limited.
- GAPS: explanations weak; LLM-judge only validates English tasks (BLEURT English-only); no MCQA-style difficulty control; human eval limited to 2 experts, small sampled (10/dialect).

### [P3] MasalBench
- Kalhor, Bahrak.
- arXiv 2026 (CoRR abs/2601.22050), Jan 2026.
- Persian proverbs (low-resource). 8 SOTA LLMs.
- Tasks: identify Persian proverb in context; identify equivalent English proverb.
- HUMAN ANNOTATION: Not explicitly reported (built from proverb collections / likely curated by authors).
- METRICS: accuracy.
- KEY FINDINGS: >0.90 accuracy identifying Persian proverbs in context; drops to 0.79 for equivalent English proverbs → cross-cultural / analogical reasoning gap.
- GAPS: no human annotation of option quality; no distractors analysis (pure identification, not MCQA distractor design); single language.

## TOPIC 2 — DISTRACTOR GENERATION FOR MCQs

### [D1] Contrastive Learning for In-Context Distractor Generation
- Alhazmi, Sheng, Zhang, Thanoon, Zhuang, Soltani, Zaib.
- EMNLP 2025 Findings. https://aclanthology.org/2025.findings-emnlp.533
- Text2Text encoder-decoder + InfoNCE/Triplet contrastive loss.
- DATASETS: SciQ (crowd-sourced science MCQ, 1 correct + 3 distractors), MCQ (fill-in-blank, 1 correct + 3 distractors). ~2,321 MCQ train.
- METHODS: contrastive objective aligns (Q,A,distractor) pairs; few-shot + beam-search baselines.
- METRICS: NDCG@3 (24.68→32.33 MCQ; 26.66→36.68 SciQ), P@1, R@1, F1@3, MRR; human eval.
- HUMAN ANNOTATION: Yes — "automatic and manual evaluations" (manual/human eval of relevance & fluency).
- GAPS: word-level options in MCQ dataset (avg 1 token) limit semantic distractors; no cross-lingual; no shortcut-resistance audit.

### [D2] Generating Plausible Distractors via Student Choice Prediction
- (Korean CS education authors) — Kang, et al.
- ACL 2025 Long. https://aclanthology.org/2025.acl-long.1154
- Pipeline: pairwise ranker (GPT-4o) → student-choice dataset → distractor generator via SFT + DPO.
- DATASET: nationwide Korean online-learning CS MCQs (Python, DB/SQL, MLDL) WITH student selection rates (hundreds of students per question).
- HUMAN ANNOTATION: Yes — pairwise ranker accuracy "comparable to human experts"; human-authored distractors as reference.
- METRICS: ranking accuracy, item discrimination index (DI), plausibility.
- KEY FINDINGS: DPO improves plausibility; higher DI than baselines; 1.45 newly added distractors rank top-3 per question (as plausible as human).
- GAPS: domain-specific (CS); relies on real student logs (not always available); English-centric framing; no low-resource / multilingual.

### [D3] BiFlow / Think Both Ways
- ACL 2025 Findings. https://aclanthology.org/2025.findings-acl.432
- Teacher-student bidirectional reasoning + PathFinder (BFS + CoT). Extends FairytaleQA → FairytaleMCQ (narrative distractors via GPT-4 generator + checker).
- Distractor criteria: Deceptiveness (syntactically/semantically similar to answer) + Consistency (contextually relevant, matches answer type).
- HUMAN ANNOTATION: Not detailed in snippet; GPT-4 used for generation/checking.
- GAPS: English narrative only; no shortcut audit; no human validation reported in snippet.

### [D4] DiVERT (math MCQ distractors)
- Fernandez, Scarlatos, Feng, Woodhead, Lan.
- EMNLP 2024. https://aclanthology.org/2024.emnlp-main.512
- Variational errors-represented-as-text; 7B open LLM beats GPT-4o on distractor generation.
- DATASET: Eedi real-world math MCQ, 1,434 questions, 3 distractors each, teacher error labels.
- HUMAN ANNOTATION: Yes — math educators human eval of error labels (comparable to human-authored).
- METRICS: exact/partial/proportional match of generated vs human distractors; human error-quality eval.
- GAPS: math-specific; no cross-lingual; small.

### [D5] DisGeM
- Çavuşoğlu, Şen, Sert.
- EMNLP 2024 Findings. https://aclanthology.org/2024.findings-emnlp.568
- Span-masking + PLM, two-stage (candidate gen + selection), NO training/fine-tuning.
- HUMAN ANNOTATION: Yes — human eval confirms more effective/engaging distractors.
- GAPS: English; no LLM; limited semantic control.

### [D6] GradQuiz (adversarial, robust against LLMs)
- Bonifazi, Buratti, Marchetti, Parlapiano, Traini, Ursino, et al.
- 2026 (ACM). https://doi.org/10.1145/3803797
- Gradient-based signals from target LLM to perturb influential entities → adversarial distractors.
- DATASETS: OpenTriviaQA, MMLU.
- RESULTS: reduces gemma-3-27b accuracy 67.26% vs original; 51.07% vs strongest adversarial baseline on MMLU.
- HUMAN ANNOTATION: Yes — human eval confirms pedagogical coherence; student study shows no added difficulty for non-LLM students.
- GAPS: targets "LLM-cheating" not human difficulty; English; adversarial perturbations may not be linguistically natural.

### [D7] Adversarial distractor generation (in-context + rule-based)
- Yigit, Amasyali.
- NLP Journal 2025 (10.1016/j.nlp.2025.100186).
- Llama-7b in-context learning + rule-based garbage-value appending. T5-Base, RoBERTa-Large; 3 MCQA datasets.
- GAPS: rule-based garbage values are not pedagogically meaningful; English.

### [D8] Rethinking MCQs for RLVR: Iterative Distractor Curation (IDC)
- ACL 2026 Findings. https://aclanthology.org/2026.findings-acl.1003
- Studies option-count mismatch + distractor strength on RLVR. IDC self-generates strong distractors blocking elimination shortcuts.
- DATASETS: MMLU-Pro Health, MedXpertQA, PubMedQA, SuperGPQA Clinical.
- KEY: even 2-way questions work with strong distractors; option-count train/test mismatch hurts; models self-generate challenging options.
- GAPS: focuses RL training not eval; medical English.

### [D9] Joint Generation of Distractors (text-to-text)
- Rodriguez-Torrealba, Garcia-Lopez, Garcia-Cabot. 2025.
- FlanT5/LongT5 (LoRA + 4-bit) on RACE; joint 3-distractor generation.
- METRICS: BLEU, ROUGE-L, BERTScore.
- GAPS: English only; BERTScore overestimates similarity for negations; no human confusion study.

## TOPIC 3 — LLM-AS-JUDGE / OPTIONS-ONLY AUDIT / SHORTCUT DETECTION

### [S1] "Which of These Best Describes MCQA? A) Forced B) Flawed C) Fixable D) All of the Above"
- Balepur, Rudinger, Boyd-Graber.
- ACL 2025 Long (pp 3394–3418). https://aclanthology.org/2025.acl-long.169 / arXiv 2502.14127
- POSITION PAPER. Argues MCQA flawed in FORMAT (can't test generation/subjectivity; misaligns with LLM use cases; poorly tests knowledge) and DATASETS (leakage; unanswerability; shortcuts; saturation).
- FIXES from education: rubrics to flag MCQ errors; scoring methods to bridle guessing (shortcuts); Item Response Theory to cull shoddy MCQs / build harder ones; constructed-response & explanation MCQA.
- Directly relevant to options-only audit: §5.3 shortcuts let LLMs "cheat"; §6.2 bias toward options/cultures/languages.
- GAPS/LIMITS: admits "this is all too much work"; doesn't abandon MCQA; language/modality applicability claimed but not demonstrated for low-resource.

### [S2] LLMs May Perform MCQA by Selecting the Least Incorrect Option
- Wang, Zhao, Qiang, Xi, Qin, Liu.
- COLING 2025. https://aclanthology.org/2025.coling-main.390
- Shows LLMs treat unselected options as partially correct (83.6–99.4% confidence of correct option).
- MCQA+ augmentation: original; reordered; T/F from correct; T/F from incorrect; NOTA; no-correct.
- METRICS: mean accuracy across settings.
- KEY: MCQA+ (×1) cheaply reveals true capability drops.

### [S3] Is Your LLM Knowledgeable or a Choices-Only Cheater?
- Balepur, Rudinger.
- arXiv 2407.01992 (2024).
- Graph mining to build 820-question contrast set from UnifiedQA (6 commonsense datasets).
- 12 LLMs; few-shot full vs choices-only. Kendall's τ ~0.9 → ranks NOT driven by choices-only shortcuts.
- GAPS: commonsense English datasets; doesn't cover proverb/cultural MCQA.

### [S4] Artifacts or Abduction (choices-only MCQA)
- Balepur, Rudinger, Boyd-Graber.
- ACL 2024 Long. https://aclanthology.org/2024.acl-long.555
- 4 LLMs, 3 datasets; choices-only prompts; abductive question inference (AQI).
- Finds high choices-only accuracy NOT always surface artifacts — models sometimes recover missing question.

### [S5] Test-Time Reasoners Are Strategic MC Test-Takers
- Balepur, Desai, Rudinger.
- arXiv 2510.07761 (2025).
- 12 LLMs, 36 LLM-benchmark combos, full vs choices-only, with/without reasoning.
- 5 strategies in choices-only traces: SHALLOW, ELIMINATE, FACT, PATTERNS, INFER-Q. Mostly non-problematic.
- Directly relevant: reasoning traces can SEPARATE problematic data from less-problematic reasoning — useful for options-only audit design.

### [S6] Reasoning Models are Test Exploiters
- arXiv 2507.15337 (2025).
- 15 benchmarks (MMLU, HLE, GSM8K, MATH...), 25 LLMs.
- MCQA inflates vs free-text when reasoning-after-options; CoT-MC-1T / CoT-MCNA-CoT mitigations; NOTA.
- KEY: MCQA "no longer a good proxy" for SOTA reasoning models.

### [S7] Eliminating Discriminative Shortcuts in MC Evaluations with Answer Matching
- Chandak, Goel, Prabhu, Hardt, Geiping.
- OpenReview (2025).

## TOPIC 4 — CROSS-LINGUAL GAPS IN LOW-RESOURCE LANGUAGES

### [C1] MMLU-ProX
- Xuan, Yang, Qi, et al.
- EMNLP 2025. https://aclanthology.org/2025.emnlp-main.79
- 29 languages, 11,829 identical questions per language (lite: 658). Translation by LLMs + EXPERT REVIEW (cultural relevance).
- 36 LLMs. Significant disparity; African languages worst.

### [C2] P-MMEval
- Zhang, Wan, Deng, et al.
- EMNLP 2025. https://aclanthology.org/2025.emnlp-main.242
- Parallel multilingual multitask benchmark, consistent language coverage, parallel samples.

### [C3] MEXA
- ACL 2025 Findings. https://aclanthology.org/2025.findings-acl.1385
- Cross-lingual alignment via parallel sentences; Pearson 0.90 predicted vs actual. Llama/Gemma/Mistral/OLMo.
- LIMIT: non-generative only; closed models excluded; machine-translated tasks bias low-resource.

### [C4] GlotEval
- EMNLP 2025 Demo. https://aclanthology.org/2025.emnlp-demos.43
- 27 benchmarks, 1500+ languages, ISO 639-3, 9 tasks.
- LIMIT: reference-free metrics biased; low-resource data scarce; cultural/linguistic bias toward dominant dialects.

### [C5] Disentangling Language and Culture
- ACL 2025 Long. https://aclanthology.org/2025.acl-long.1082
- Dual Evaluation framework: linguistic medium × cultural context. "Cultural-Linguistic Synergy" — ask culture-specific Q in its language > English.
- LIMIT: single cultural context per language; probing on small models only.

### [C6] Cross-Lingual Pitfalls
- ACL 2025 Long. https://aclanthology.org/2025.acl-long.404

### [C7] Cross-Lingual Auto Evaluation
- ACL 2025 Long. https://aclanthology.org/2025.acl-long.1419

### [C8] Quantifying Language Disparities in Multilingual LLMs
- EMNLP 2025. https://aclanthology.org/2025.emnlp-main.199

## TOPIC 5 — HUMAN VALIDATION REQUIREMENTS / STANDARDS

### [H1] BRIGHTER
- Muhammad, Ousidhoum, Abdulmumin, Wahle, Ruas, Beloucif, et al.
- ACL 2025 Long. https://aclanthology.org/2025.acl-long.436
- 28 languages emotion recognition; multi-label (anger, sadness, fear, disgust, joy, surprise + neutral) + 4-point intensity (0–3).
- HUMAN ANNOTATION STANDARDS (model example):
  - fluent speakers / native speakers directly recruited (not just MTurk) for low-resource.
  - IAA + reliability scores distinguished; ≥2 annotators; ≥5 for intensity.
  - final label if ≥2 annotators pick label w/ intensity ≥1 AND avg score > T (T=0.5).
  - releases INDIVIDUAL (non-aggregated) annotations (disagreement as signal; Plank 2022).
  - AMT for English, Toloka for RU/UK/TT, LabelStudio/Potato for low-resource.
- GAPS: emotion not MCQA; high-resource skew; class imbalance.

### [H2] Who Annotates in NLP?
- Kunilovskaya, Bhatia, Albertelli, Chen, Greisinger, Kiefer, et al.
- arXiv 2606.02255 (2026).
- Large-scale assessment of human annotation REPORTING 2018–2025. (Reporting standards focus.)

### [H3] Just Put a Human in the Loop?
- Schroeder, Roy, Kabbara.
- ACL 2025 Findings. https://aclanthology.org/2025.findings-acl.1323
- Pre-registered: 350 annotators, 7,000 annotations, 4 conditions, 2 models, 2 datasets.
- FINDING: LLM suggestions don't speed annotators but raise self-confidence; annotators strongly adopt LLM suggestions → label distribution shift → inflated model-performance scores when used to eval LLMs.
- IMPLICATION: "human-approved" LLM-annotated data can bias conclusions — relevant to our human-validation design (avoid LLM-suggestion contamination).

### [H4] NagaNLP (human-in-the-loop synthetic)
- Maiti et al. 2025. https://huggingface.co/papers/2512.12537
- Nagamese Creole; LLM (Gemini) generates, native speakers validate/annotate.
- 4 annotators (3 native, 1 fluent); Cohen's Kappa 0.92 POS, 0.88 NER.
- HiTL critical: +9 F1 POS, +13 F1 NER vs raw synthetic.

### [H5] MMLU-ProX expert review (see C1) — translation + cultural relevance expert check.
### [H6] JAWAHER 2-expert linguistics/translation annotators (see P2).

## SYNTHESIS FOR PROVERBGAP PAPER
- Proverb/cultural MCQA benchmarks (P1–P3) use human annotation but NONE do shortcut-resistant distractor generation or options-only audit.
- Options-only / choices-only shortcut literature (S1–S7) is almost entirely English commonsense; our Yoruba/Arabic/English proverb MCQA + blind options-only audit is novel cross-lingual application.
- Human-validation best practices (H1, H3, H4): native-speaker recruitment, IAA (Cohen's Kappa / ≥2 annotators), release individual labels, AVOID LLM-suggestion contamination (H3), expert review for translation/cultural relevance (C1, P2).
- v68 gaps mirror S1 §5.3 (shortcuts) and ProverbEval §choice-order: our HCW (27.8%) and perfect-consensus (41.7%) are exactly the shortcut/order-sensitivity failure modes these papers warn about.
