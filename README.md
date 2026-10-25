# ProverbGap: Shortcut-Resistant Distractor Generation for Proverb Understanding

> **What happens when you ask LLMs to generate distractors for proverb MCQs, then audit them blind?** The distractors look plausible but often wrong. This README documents the ProverbGap pipeline, the v68 N=5 experiment (180 MCQs across English, Arabic, and Yoruba), and why the system fails its own quality gates.

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [What Makes a Good Distractor](#2-what-makes-a-good-distractor)
3. [The Four Variants](#3-the-four-variants)
4. [The Pipeline](#4-the-pipeline)
5. [What v68 Showed](#5-what-v68-showed)
6. [Why It Failed](#6-why-it-failed)
7. [What We Learned](#7-what-we-learned)
8. [Data, Code, and License](#8-data-code-and-license)
9. [Human Validation (Planned)](#9-human-validation-planned)
10. [Status and Next Steps](#10-status-and-next-steps)
11. [Reproducing the Numbers](#11-reproducing-the-numbers)

---

## 1. The Problem

Large language models can score 90%+ on simple proverb tests by exploiting surface-level shortcuts:

- **"Longest answer is right"** — models use answer length as a signal
- **"Echoing the proverb is correct"** — distractors that mirror the proverb's structure win by association
- **"Always pick A"** — positional biases in both generation and evaluation

Most proverb benchmarks (ProverbEval, JAWAHER, MasalBench) release MCQs without systematically checking whether distractors resist these shortcuts. **ProverbGap** treats MCQ construction itself as the research question: *How do you build and audit proverb MCQs that resist shortcut solutions?*

The pipeline combines adversarial generation (four deliberately different prompt strategies), semantic filtering, corpus-based fallback, and a **blind options-only audit** by a four-model committee.

---

## 2. What Makes a Good Distractor

A useful distractor is **plausible but wrong**. It tempts a fluent speaker who hasn't heard the specific proverb, but is demonstrably incorrect once the proverb is known.

A **shortcut-prone** distractor fails this test in one of three ways:

1. **Too generic** — unrelated to the proverb's meaning at all ("Charity begins at home" as a distractor for *A bird in the hand.*)
2. **Too close** — a near-paraphrase of the correct meaning that the NLI/paraphrase filter rejects
3. **Length-mismatched** — clearly longer or shorter than the correct option, enabling a length shortcut

The pipeline's semantic filters catch #2 and #3. When they reject a distractor, a **corpus fallback sampler** fills the gap by pulling a meaning from another proverb. This is where the system breaks.

---

## 3. The Four Variants

A **prompt variant** is a deliberately different set of instructions given to the language model when it generates distractors. The proverb and its intended meaning stay the same, but each variant emphasizes a different strategy for producing the three incorrect answer options. Comparing variants reveals which strategies produce usable distractors and which lead to filter rejection or fallback.

The four distractor-generation variants are defined in [`kaggle/run_logs/v68/pilot1_prompt_variants.json`](kaggle/run_logs/v68/pilot1_prompt_variants.json). Each generates 4 options (index 0 = correct, indices 1-3 = incorrect distractors) under shared constraints: ±35% length parity, no negated/antonym traps, no meta-words, no source-language leakage.

| Variant | How it works | Intended benefit | What v68 showed |
|---------|-------------|-----------------|-----------------|
| `adversarial-hard-negative` | Instructs the model to produce "hard negatives" — distractors that are **semantically close** to the correct meaning but wrong in a fine-grained way (misattributed agency, changed scope, wrong situation). | Force distractors that require real understanding to reject, not obvious wrong answers. | 24.4% HCW. Lowest perfect-consensus rate (31.1%) means auditors disagree more — but 42.2% needed length fallback because filters rejected the tempting distractors. |
| `adversarial-length-locked` | Enforces strict ±35% character count parity across all four options and a register/style lock. Bans simple negations and antonyms. | Prevent length-based shortcuts (longest answer is right) and surface-pattern matching. | 35.6% HCW. Highest perfect-consensus rate (53.3%) — auditors agree too eagerly, often on the wrong answer. |
| `taxonomy-guided` | Uses a structured error taxonomy (Haladyna & Downing / VERGE-inspired) to construct distractors for specific misunderstanding types: (1) partial meaning, (2) sensible but wrong situation, (3) missing key condition or nuance. | Systematically cover different ways a reader can misunderstand a proverb. | 28.9% HCW. 66.7% fully generated, 0.0% length fallback — cleanest generation status, but still high HCW because distractors are too tempting. |
| `overgenerate-select` | Generates 8+ candidate distractors, then selects the 3 that would be **hardest to rule out** in a blind audit while still being wrong. | Use adversarial filtering to find the most tempting valid distractors. | 22.2% HCW. **71.1% fully generated** (highest) and 2.2% length fallback (lowest) — cleanest generation profile. |

**Key insight:** higher generation-completion rate does **not** mean higher question quality. The `overgenerate-select` variant produces the most complete MCQs (71.1% with zero filter rejections), but still has 22.2% HCW items — its surviving distractors are too tempting to auditors. Meanwhile, `adversarial-hard-negative` produces the most tempting distractors but the filters reject 73.3% of them, triggering corpus fallbacks that become confident-wrong traps.

### These are NOT the same as legacy evaluation-prompting styles

The legacy Groq S1/S2 pipeline used evaluation prompting styles to *rate MCQ difficulty*:

- **Zero-shot** — model rates difficulty with no examples
- **Few-shot** — 2–3 example ratings provided
- **Chain-of-thought** — examples with step-by-step reasoning before self-rating

These are **evaluation** techniques, distinct from v68's **distractor-generation** variants. v68's audit committee uses **blind options-only voting** — it receives only the four answer options and selects the correct one without seeing the proverb. No evaluation prompting styles are applied at any stage.

---

## 4. The Pipeline

```
Data (Proverbs) → Generation (4 variants × 3 generators) → Semantic filters (NLI, leak, length, blocklist)
                     ↓                                        ↓
                Corpus fallback sampler (when filters reject) → Option assembly (balanced A/B/C/D)
                     ↓
                Blind audit committee (4 models, options-only, no proverb)
                     ↓
                HCW detection (≥0.75 consensus on wrong answer)
```

**Stage 1 — Generation.** Three generators (`google/gemma-4-31b-it`, `google/gemini-2.5-flash`, `qwen/qwen3.7-max`) are applied to 15 proverbs (5 per language) across 4 variants, producing 180 MCQs.

**Stage 2 — Semantic gates.** Generated distractors pass through NLI paraphrase filtering (rejects near-paraphrases of the correct meaning), leak sanitization (rejects distractors echoing the gold meaning), length parity check, and idiom blocklist. When a distractor fails, it is replaced.

**Stage 3 — Corpus fallback.** When all generated distractors for an MCQ fail the gates, the pipeline samples replacement options from **other proverbs' meanings**. This is the bottleneck (see §6).

**Stage 4 — Blind audit.** A **separate** four-model committee (`llama-3.3-70b`, `mistral-small-3.2`, `gemma-3-27b-it`, `deepseek-v3.2`) votes on the correct answer **seeing only the four options** — no proverb text, no generator identity.

**Stage 5 — HCW detection.** Items where ≥3 of 4 auditors agree on the *wrong* answer (consensus fraction ≥ 0.75) are flagged as **High-Consensus-Wrong (HCW)**. This is the key diagnostic: it reveals when the corpus fallback produces distractors that look plausible to an LLM committee but are wrong.

---

## 5. What v68 Showed

v68 is the **complete and validated** production dataset: 180 MCQs (15 proverbs × 4 variants × 3 generators), generated on 2026-06-22 at a cost of $0.85. All 720 audit votes (180 × 4 auditors) are present with zero missing.

### 5.1 Aggregate results

| Metric | Value | 95% Bootstrap CI | Target | Status |
|--------|------:|------------------|--------|--------|
| Consensus accuracy | 56.7% (102/180) | [49.4%, 63.9%] | — | — |
| Perfect consensus | 41.7% (75/180) | [34.4%, 48.9%] | < 30% | ❌ Fail |
| High-consensus-wrong (HCW) | 27.8% (50/180) | [21.1%, 34.4%] | < 10% | ❌ Fail |
| Partial + fallback | 43.9% (79/180) | [36.7%, 51.1%] | < 15% | ❌ Fail |
| Hard fallback (length parity) | 16.1% (29/180) | [11.1%, 21.7%] | < 5% | ❌ Fail |
| Duplicate options | 0 | [0%, 0%] | 0% | ✅ Pass |
| Correct-key balance | 45/45/45/45 | — | ~25% each | ✅ Pass |

**HCW definition:** consensus fraction ≥ 0.75 (at least 3 of 4 auditors agree) AND consensus label ≠ correct label. This is **not** the same as "all incorrect consensus answers" (43.3% = 100% − 56.7% accuracy). All HCW values in this README use the ≥ 0.75 threshold.

### 5.2 Per-language results

| Language | N | Consensus accuracy | 95% CI (Wilson) | Perfect consensus | HCW (≥0.75) |
|----------|---|-------------------|-----------------|-------------------|-------------|
| English | 60 | 65.0% (39/60) | [52.4%, 75.8%] | 45.0% (27/60) | 18.3% (11/60) |
| Arabic | 60 | 53.3% (32/60) | [40.9%, 65.4%] | 50.0% (30/60) | 31.7% (19/60) |
| Yoruba | 60 | 51.7% (31/60) | [39.3%, 63.8%] | 30.0% (18/60) | 33.3% (20/60) |

English is numerically easier but CIs overlap substantially with Arabic and Yoruba — the gap is not statistically significant at N=60 per language.

### 5.3 Per-generator results

| Generator | N | Accuracy | Perfect consensus | HCW (≥0.75) | Fully generated |
|-----------|---|----------|-------------------|-------------|-----------------|
| `google/gemma-4-31b-it` | 60 | 65.0% | 46.7% | 21.7% | 66.7% (40/60) |
| `google/gemini-2.5-flash` | 60 | 53.3% | 41.7% | 31.7% | 50.0% (30/60) |
| `qwen/qwen3.7-max` | 60 | 51.7% | 36.7% | 30.0% | 51.7% (31/60) |

**Pooled accuracy (56.7%) is worse than gemma-only (65.0%).** Weaker generators drag down the pool, introducing more HCW items. A multi-model pool does not automatically improve distractor quality at N=5.

### 5.4 Per-variant results

| Variant | N | Accuracy | Perfect consensus | HCW (≥0.75) | Fully generated | Length fallback |
|---------|---|----------|-------------------|-------------|-----------------|-----------------|
| `adversarial-hard-negative` | 45 | 60.0% | 31.1% | 24.4% | 26.7% (12/45) | 42.2% |
| `adversarial-length-locked` | 45 | 55.6% | 53.3% | 35.6% | 60.0% (27/45) | 20.0% |
| `overgenerate-select` | 45 | 53.3% | 35.6% | 22.2% | 71.1% (32/45) | 2.2% |
| `taxonomy-guided` | 45 | 57.8% | 46.7% | 28.9% | 66.7% (30/45) | 0.0% |

### 5.5 Position bias

Correct-key distribution is perfectly balanced: 45/45/45/45. Committee accuracy by position:

| Position | Correct | Total | Accuracy |
|----------|--------:|------:|----------:|
| A | 33 | 45 | 73.3% |
| B | 26 | 45 | 57.8% |
| C | 22 | 45 | 48.9% |
| D | 21 | 45 | 46.7% |

Chi-square goodness-of-fit: χ² = 3.49, df = 3, **p = 0.322** — not significant at α = 0.05. The position bias trend is present (73.3% vs 46.7%) but does not reach significance at N=180. Balanced key placement means the bias **cancels out in aggregate metrics**, but the per-position variance indicates committee calibration issues — it is not eliminated.

### 5.6 Audit committee (blind, options-only)

Each auditor votes on 180 MCQs seeing only the four options. Individual accuracy against the **gold** correct label:

| Auditor | Family | Accuracy vs gold |
|---------|--------|------------------|
| `meta-llama/llama-3.3-70b-instruct` | Meta | 53.3% (96/180) |
| `mistralai/mistral-small-3.2-24b-instruct` | Mistral | 56.7% (102/180) |
| `google/gemma-3-27b-it` | Google | 45.6% (82/180) |
| `deepseek/deepseek-v3.2` | DeepSeek | 56.1% (101/180) |

The committee's 56.7% consensus accuracy is only slightly above random (25% for 4 options), confirming that options-only selection is a **diagnostic** — it reveals what the distractors themselves invite, not whether the pipeline produces valid MCQs for human use.

### 5.7 Filter replacement analysis

| Filter | Mean replacements/MCQ | Share |
|--------|----------------------:|-------|
| NLI paraphrase | 0.36 | ~36% |
| Correct-meaning leak | 0.35 | ~35% |
| Length parity | 0.15 | ~15% |
| Blocklist | 0.02 | ~2% |
| **Total** | **0.99** | 100% |

Semantic filters (NLI + leak = 71%) dominate replacements, not structural issues.

---

## 6. Why It Failed

The v68 experiment failed four of six shortcut-resistance gates. The root cause is the **corpus fallback sampler**:

1. **43.9%** of MCQs needed at least one fallback replacement (mean 0.99 replacements/MCQ).
2. The NLI and leak filters are **over-aggressive**: they reject semantically close distractors that could be genuinely good hard negatives, replacing them with unrelated proverb meanings.
3. Those corpus fallbacks are often generic moral statements or culturally mismatched idioms that **look plausible to auditors but are wrong** — producing 27.8% HCW items.
4. **English is trivially easy** (65.0% accuracy, 45.0% perfect consensus) — distractors don't tempt.
5. **Cross-lingual asymmetry**: Arabic requires 3.5× more fallback replacements than English (1.52 vs 0.43 per MCQ), indicating the pipeline is calibrated for English.

**This is a systematic failure, not a stochastic one.** The pipeline's infrastructure is robust (zero API failures, zero missing votes), but the fallback sampler's quality collapse is structural: when semantic filters reject a distractor, the only replacement source is other proverbs' meanings, which are too generic to serve as targeted hard negatives.

The v68 report's full failure taxonomy is documented in [`v68_detailed_analysis_report.md`](kaggle/run_logs/v68/v68_detailed_analysis_report.md).

---

## 7. What We Learned

1. **The corpus fallback sampler is the bottleneck — not the generators.** Even the strongest generator (gemma-4-31b-it, 65.0% accuracy) still produces 21.7% HCW because fallbacks override good initial generation.
2. **Higher completion rate ≠ better quality.** `overgenerate-select` has 71.1% clean generation but 22.2% HCW. Filters reject the tempting distractors; fallback produces plausible-but-wrong options.
3. **NLI + leak filters over-fire.** 71% of replacements come from semantic filters (NLI 36%, leak 35%), not length or structure. The thresholds may be too aggressive for non-English languages.
4. **Cross-lingual calibration gap.** Arabic and Yoruba trigger 3.5× more fallbacks than English. The pipeline works for English but aggressively rejects output for morphologically complex languages.
5. **The LLM audit is a diagnostic, not validation.** The blind options-only committee reveals what the distractor set invites, but 56.7% accuracy shows auditors struggle without the proverb context.

### Research direction change

The original plan was to scale to N=15 (540 MCQs) if v68 passed quality gates. Since v68 failed all shortcut-resistance gates, the project **pivoted to paper-first framing**: documenting the methodology, failure taxonomy, and diagnostic value of the v68 dataset.

The **v69 ablation** (enabling `USE_LLM_FALLBACK=True` to replace the corpus sampler with a proverb-specific hard-negative generator) was planned as the primary fix but was **never executed** — OpenRouter budget was exhausted before the run could start.

---

## 8. Data, Code, and License

### Code

All Python code is licensed under the **MIT License** (see [`LICENSE`](LICENSE)).

### Datasets

**Data licensing is BLOCKED PENDING PROVENANCE/RIGHTS REVIEW.** The datasets are **not** released under CC BY 4.0. See [`LICENSE`](LICENSE) for the full status:

- **English**: Scraped from public-domain sources. Specific URLs were not recovered; rights verification pending.
- **Arabic**: From a `MID`-prefix academic dataset. Source unidentified; licensing under review.
- **Yoruba**: Derived from Owomoyela (2005), *Yoruba Proverbs* (University of Nebraska Press, ISBN 978-0-8032-1843-7). **Copyrighted.** No redistribution permission obtained. Despite prior documentation claiming exclusion, the public v68 CSV currently contains 60 Yoruba MCQ rows. This exposure is documented as an unresolved data-rights issue; removal of Yoruba rows is pending owner approval.

### Provenance documentation

[`DATA_PROVENANCE_TEMPLATE.md`](DATA_PROVENANCE_TEMPLATE.md) (also in [`submission_package_2026-08-02/`](submission_package_2026-08-02/DATA_PROVENANCE_TEMPLATE.md)) documents all three language sources with explicit liability notes.

### v68 production artifacts

| Artifact | Path | Contents |
|----------|------|----------|
| Generated MCQs | [`kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv`](kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv) | 180 rows (includes 60 Yoruba rows — see rights note above) |
| Audit results | [`kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_audit_results.csv`](kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_audit_results.csv) | 180 × 4 = 720 blind audit votes |
| Run config | [`kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_summary.json`](kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_summary.json) | Model roster, seed, variants, cost ($0.8539) |
| Analysis report | [`kaggle/run_logs/v68/v68_detailed_analysis_report.md`](kaggle/run_logs/v68/v68_detailed_analysis_report.md) | Executive summary, gate table, failure taxonomy |
| Generator-variant analysis | [`kaggle/run_logs/v68/openrouter_pilot1_test_output/v68_generator_variant_analysis.md`](kaggle/run_logs/v68/openrouter_pilot1_test_output/v68_generator_variant_analysis.md) | Per-generator/variant HCW at ≥0.75 |

**Full execution history and metric definitions** are documented in [`docs/RESEARCH_HISTORY_AND_README_AUDIT.md`](docs/RESEARCH_HISTORY_AND_README_AUDIT.md).

---

## 9. Human Validation (Planned, Not Started)

A 60-item stratified sample (20 per language, balanced by generation status) is prepared at [`data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv`](data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv).

**Status: Prepared, not started.** Recruitment of 9 native speakers (3 per language) is budget-dependent.

### What is NOT ready

The **LLM-proxy inter-annotator agreement** (7-model proxy, 60-item subset) shows Fleiss κ = 0.4845 and mean pairwise Cohen κ = 0.4846. This is a **calibration anchor** — it shows what agreement looks like when 7 models annotate the same items. It does **not** establish an upper limit for human agreement, and it is not a substitute for human validation. Native-speaker IAA must be measured separately.

**Planned human validation:** annotators see the proverb + four options (no gold label, no LLM votes), select the correct answer, and rate distractor plausibility. This is fundamentally different from the blind options-only audit (which withholds the proverb).

---

## 10. Status and Next Steps

### Current state

| Milestone | Status |
|-----------|--------|
| v68 dataset generation (180 MCQs) | **Complete** — seed 20260615, $0.85 cost |
| Blind audit pipeline (720 votes) | **Complete** — 0 missing, 0 substitutions |
| v68 metric verification | **Complete** — all values recomputed from raw CSVs |
| Statistical tests (McNemar, Wilcoxon, Holm-Bonferroni) | **Complete** — all null (p > 0.05); results in [`paper/tables/table_statistical_tests_corrected.csv`](paper/tables/table_statistical_tests_corrected.csv) |
| Bootstrap CIs (all metrics) | **Complete** — 10,000 resamples; in [`kaggle/run_logs/v68/table_bootstrap_cis.csv`](kaggle/run_logs/v68/table_bootstrap_cis.csv) |
| v69 LLM-fallback ablation | **Blocked** — never executed (budget exhausted before start) |
| v70 LLM-fallback run | **Halted** — incomplete at 83/180 rows, no audit phase reached |
| Human validation (60 items) | **Not started** — recruitment pending |
| Paper draft | **In progress** — see [`paper/proverbgap_eacl2027.md`](paper/proverbgap_eacl2027.md) |

### Publication status

The paper targets **EACL 2027 ARR**. The submission deadline was **August 3, 2026**. No submission record, paper ID, or reviewer decision has been documented in this repository. Submission status is **unconfirmed** and must be verified by the owner.

### Next steps (no budget needed)

- [x] v68 verification and metric reconciliation (this README)
- [x] Paper drafting complete through Section 11
- [ ] Tests: add HCW threshold (>=0.75) and length-fallback status verification tests

### Next steps (requires OpenRouter budget)

| Task | Estimated cost | Success gate |
|------|----------------|--------------|
| v69 LLM-fallback ablation (N=5) | ~$1.00 | HCW < 15%, partial+fallback < 30% |
| Human validation (60 items × 3 annotators) | ~$200–300 | Fleiss κ ≥ 0.6 |

**If v69 passes gates:** freeze config, scale to N=15 (v70 re-run), update paper numbers.  
**If v69 fails or budget stays exhausted:** v68 is the production dataset. Paper is framed as a methodology + failure taxonomy study at N=5.

---

## 11. Reproducing the Numbers

To recompute all v68 metrics from the raw CSVs:

```bash
# HCW at the canonical >= 0.75 threshold
python kaggle/run_logs/v68/openrouter_pilot1_test_output/analyze_v68.py

# Bootstrap CIs for all six aggregate metrics (10,000 resamples)
python kaggle/run_logs/v68/analysis_scripts/analyze_bootstrap_cis.py

# Statistical tests (McNemar, Wilcoxon, Holm-Bonferroni)
python kaggle/run_logs/v68/analysis_scripts/analyze_statistical_tests.py

# Run the test suite
pytest tests/ -v
```

All scripts read from the canonical CSVs:
- `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_audit_results.csv`
- `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv`

No external API calls or model generation is triggered by the analysis scripts.

---

## Citation

```bibtex
@misc{abraham2026proverbgap,
  title        = {Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding},
  author       = {Abraham, Sunday Aspita},
  year         = {2026},
  howpublished = {EACL 2027 ARR submission (status unconfirmed)},
  note         = {v68 N=5 production dataset: 180 MCQs, $0.85 cost, 4-model blind audit committee},
  url          = {https://github.com/saaga23/proverb_mcq}
}
```

---

*For the full experiment timeline, model roster details, claims audit, and evidence file index, see [docs/RESEARCH_HISTORY_AND_README_AUDIT.md](docs/RESEARCH_HISTORY_AND_README_AUDIT.md).*
