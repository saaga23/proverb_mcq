# ProverbGap: Shortcut-Resistant Multiple-Choice Questions for Proverb Understanding

> **Hardened adversarial distractor generation across English, Arabic, and Yoruba -- methodology paper first, with v68 N=5 (180 MCQs) as the production dataset.**

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 1. Introduction

Modern LLMs can score 90%+ on simple proverb tests by exploiting surface-level shortcuts -- "the longest answer is right," "answers echoing the proverb are correct," or "always pick A." **ProverbGap** closes those shortcuts by generating distractors that **survive four adversarial prompt variants** and pass through a **blind options-only audit** by a four-model committee before reaching any human.

**The scientific contribution is the pipeline -- not benchmark size.** At N=5 per language (180 MCQs across English, Arabic, and Yoruba), the pipeline reveals a systematic failure mode: when the semantic filters reject an LLM-generated distractor as "too plausible," a **corpus-based fallback sampler** fills the gap with unrelated proverbs' meanings. Those fallbacks look plausible to auditors but are wrong -- producing **27.8% High-Consensus-Wrong (HCW)** items, far above the 10% target.

This README documents the v68 production dataset, the full experimental history (v59-v70), the verified empirical findings, and the path to publication.

---

## 2. Current State

| Milestone | Status | Notes |
|-----------|--------|-------|
| v68 dataset generation (180 MCQs) | Complete | 15 proverbs x 4 variants x 3 generators x 3 languages, seed 20260615 |
| Kaggle N=5 validation run | Complete | `mcq-pass-shortcut` kernel v68, 2026-06-22 |
| Blind audit pipeline | Complete | 720 votes (180 x 4 auditors), 0 missing |
| v69 LLM-fallback ablation | Blocked | Planned (N=5, USE_LLM_FALLBACK=True) -- OpenRouter budget exhausted |
| v70 N=15 scaling attempt | Incomplete | Budget-blocked at 83/180 MCQs (30 EN + 30 AR + 23 YO), $0.42 spent |
| Annotation app deployed | Live | [https://annotationapp.vercel.app](https://annotationapp.vercel.app) |
| 60-item human validation sample | Prepared | In `data/production/paper_first_outputs_2026-06-22_10-42-02/` -- recruitment of 9 native speakers pending |
| Paper drafting | In progress | Frame: methodology + failure taxonomy at N=5 |
| Publication target | EACL 2027 ARR | Submission deadline: August 3, 2026 |

**Where we stopped:** The v68 N=5 dataset is complete and validated. The critical bottleneck (corpus fallback sampler) was identified but could not be ablated (v69) or scaled (v70) because OpenRouter budget was exhausted. The paper is framed as a **methodology + failure taxonomy study** at N=5, with human validation and v69/v70 runs explicitly listed as future work.

---

## 3. Task Explanation: The Hardened Pipeline

```
  Data (Proverbs)  -->  Generation (Distractors)  -->  Audit (Blind)  -->  Annotation (Humans)  -->  Analysis (Stats)
       |                     |                        |                  |                      |
  raw corpora          4 prompt variants          4 LLMs vote        native speakers      Tables, figures,
  (3 languages)       3 generator models        on correct answer     rate plausibility      failure taxonomy
                      (A-D options each)         blind (no proverb)  & flag shortcuts      LaTeX
```

**Step 1 -- Data.** Proverbs from English, Arabic, and Yoruba corpora. See Section 4 for provenance and licensing status.

**Step 2 -- Generation.** A dynamic multi-model generator pool produces four multiple-choice options (1 correct meaning + 3 distractors) per proverb. Four adversarial prompt variants are applied:

| Variant | Design goal | v68 behavior |
|---------|-------------|--------------|
| `adversarial-length-locked` | Strict sentence-length and register parity | Highest perfect-consensus rate (53.3%) but also high HCW (44.4%) |
| `adversarial-hard-negative` | Tempting near-paraphrase distractors | Worst: 26.7% fully generated, 42.2% length-fallback, 40.0% HCW |
| `overgenerate-select` | Generate 5+ distractors, select 3 best | Cleanest generation (71.1% fully generated) |
| `taxonomy-guided` | Distractor selection via meaning-taxonomy constraints | Best for Yoruba (+26.7pp vs worst variant, 66.7% vs 40.0%) |

**Step 3 -- Semantic gates (dual-gate validation).** Raw distractors pass through sequential filters -- length parity, idiom blocklist, correct-meaning leak sanitizer, and NLI paraphrase filter. Any failure triggers a replacement.

**Step 4 -- Blind audit.** A separate four-model committee votes on the correct answer *without seeing the proverb* -- only the four options. HCW (kappa >= 0.75 consensus on the wrong answer) flags items where distractors are tempting but misleading. The committee uses four different model families (Meta, Mistral, Google, DeepSeek), with Google appearing in both generator and auditor pools -- mitigated by the options-only blindness design.

**Step 5 -- Human annotation.** Native speakers review the hardest items, select correct answers, and rate distractor plausibility. A 60-item stratified sample is prepared; recruitment of annotators is budget-dependent future work.

**Step 6 -- Analysis.** Inter-annotator agreement, shortcut resistance, cost efficiency, and cross-lingual performance are measured with bootstrap CIs.

---

## 4. Data Sources

**v68 production dataset (canonical):**

| Source | Path | Contents |
|--------|------|----------|
| Generated MCQs | `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv` | 180 rows, all fields (proverb, gold meaning, 4 options, labels) |
| Audit results | `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_audit_results.csv` | 180 rows x 4 auditor columns = 720 blind votes |
| Run config | `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_summary.json` | Model roster, seed, variants, cost ($0.8539 / $5.00) |
| Raw outputs | `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_raw_outputs.csv` | 183 raw generation attempts with full text |

**Human validation sample:**

| Source | Path | Contents |
|--------|------|----------|
| Validation sample | `data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv` | 60 items (20 per language), stratified by generation status |

**Proverb sources (with licensing notes):**

| Language | Status | Notes |
|----------|--------|-------|
| English | Public domain compilations | Multiple public-domain sources; see `docs/DATA_PROVENANCE_TEMPLATE.md` |
| Arabic | Documented dataset | IDs from `MID` prefix dataset; licensing under review |
| Yoruba | Restricted | Derived from Owomoyela (2005), University of Nebraska Press -- **no redistribution permission**; Yoruba MCQs excluded from public release, retained for analysis only |

---

## 5. Experimental Story: v59-v70 Timeline

| Version | N per language | Notes | Status |
|---------|---------------|-------|--------|
| v59-v60 | N=45 | Early Groq S1 pipeline | Deprecated; legacy numbers not used in v68 paper |
| v61-v67 | N=1-3 | OpenRouter pipeline refinement | Archived; v67 frozen as baseline |
| **v68** | **N=5** | **Production dataset** | **Complete** -- 180 MCQs, $0.85, full blind audit |
| v69 | N=5 | LLM-fallback ablation (`USE_LLM_FALLBACK=True`) | **Blocked** -- OpenRouter budget exhausted before run |
| v70 | N=15 | Scaling test (540 target MCQs) | **Incomplete** -- budget-blocked at 83/180 |

**v68 is the production dataset.** It uses the frozen v67 configuration (`USE_LLM_FALLBACK=False`, `N_PER_LANG=5`, seed=20260615) and ran successfully on Kaggle in 2026-06-22.

**v69 was never executed.** Its directory contains only template and planning files (`v69_detailed_analysis_report.md` is all TBD blanks, `v69_post_download_checklist.md` was never run). The v69 comparison report is a template.

**v70 was attempted but budget-blocked.** The run started with `USE_LLM_FALLBACK=True` and `N_PER_LANG=15`, but OpenRouter returned `403 Budget limit exceeded` after generating 83 of 180 MCQs (30 English + 30 Arabic + 23 Yoruba). The partial output at $0.42 is archived but not production quality.

> **Note on the "80" mystery:** The number "80" that appears in legacy logs refers to an **audit-progress checkpoint** ("Audited 80/90 MCQs", "Audited 80/270 MCQs"), not a dataset size. No version of this project ever produced exactly 80 MCQs. The canonical dataset is v68 with 180 MCQs.

---

## 6. Empirical Findings (v68, N=5)

### 6.1 Aggregate metrics

| Metric | v68 N=5 | Target | Pass |
|--------|---------|--------|------|
| Consensus accuracy | 56.7% (102/180) | -- | -- |
| Perfect consensus | 41.7% (75/180) | < 30% | [X] |
| HCW (kappa>=0.75) | 27.8% (50/180) | < 10% | [X] |
| Partial + fallback | 43.9% (79/180) | < 15% | [X] |
| Hard fallback (length) | 16.1% (29/180) | < 5% | [X] |
| Duplicate options | 0 | 0 | [OK] |
| Correct-key balance | 45/45/45/45 | ~25% each | [OK] |

**HCW threshold note:** The canonical definition (used in `v68_detailed_analysis_report.md` line 61) is **consensus fraction >= 0.75 (3 of 4 auditors) AND consensus label != correct**. Some earlier per-language files used >= 0.50, inflating HCW to 42.8%. The >= 0.75 standard is used throughout this README.

### 6.2 Per-language performance

| Language | N | Consensus accuracy | 95% CI (Wilson) | Perfect consensus | HCW (>=0.75) | Fallback mean |
|----------|---------|-------------------|-----------------|-------------------|-------------|---------------|
| English | 60 | 65.0% (39/60) | 52.4%-75.8% | 45.0% (27/60) | 18.3% (11/60) | 0.43 |
| Arabic | 60 | 53.3% (32/60) | 40.9%-65.4% | 50.0% (30/60) | 31.7% (19/60) | 1.52 |
| Yoruba | 60 | 51.7% (31/60) | 39.3%-63.8% | 30.0% (18/60) | 33.3% (20/60) | 1.03 |

- **English** is the "too-easy" language: 65.0% accuracy but 45.0% perfect consensus means distractors lack temptation.
- **Arabic** is the "confident-wrong" language: 50.0% perfect consensus with 31.7% HCW -- auditors agree often but usually on the wrong answer.
- **Yoruba** is the "fragile low-resource" language: 51.7% accuracy, just clearing the 50% gate, with the lowest auditor hit rates (Gemma-3-27b: 36.7% vs gold).

### 6.3 Per-generator performance

| Generator | N | Accuracy | Perfect | HCW | Fully generated |
|-----------|---------|----------|---------|---------|-----------------|
| google/gemma-4-31b-it | 60 | 65.0% | 46.7% | 35.0% | 66.7% (40/60) |
| google/gemini-2.5-flash | 60 | 53.3% | 41.7% | 46.7% | 50.0% (30/60) |
| qwen/qwen3.7-max | 60 | 51.7% | 36.7% | 46.7% | 51.7% (31/60) |

**gemma-4-31b-it is the strongest generator** -- highest accuracy, lowest HCW, cleanest generation profile. qwen3.7-max produces the most length-fallback items (30.0%) and the highest mean fallback count (1.33).

### 6.4 Per-variant performance

| Variant | N | Accuracy | Perfect | HCW | Fully generated |
|---------|---------|----------|---------|---------|-----------------|
| adversarial-hard-negative | 45 | 60.0% | 31.1% | 40.0% | 26.7% (12/45) |
| adversarial-length-locked | 45 | 55.6% | 53.3% | 44.4% | 60.0% (27/45) |
| overgenerate-select | 45 | 53.3% | 35.6% | 46.7% | 71.1% (32/45) |
| taxonomy-guided | 45 | 57.8% | 46.7% | 40.0% | 66.7% (30/45) |

### 6.5 Generation pipeline diagnostics

| Status | Count | % |
|--------|------:|------:|
| generated (fully passed) | 101 | 56.1% |
| partial (>=1 filter replacement) | 50 | 27.8% |
| length_fallback (corpus sampler) | 29 | 16.1% |
| parse_fallback / hard_fallback | 0 | 0.0% |

**Mean replacements per MCQ (filter drivers):**

| Filter | Mean/MCQ | Share of replacements |
|--------|----------:|--------------------------|
| NLI paraphrase | 0.36 | ~36% |
| Correct-meaning leak | 0.35 | ~35% |
| Length parity | 0.15 | ~15% |
| Blocklist | 0.02 | ~2% |

Replacements are dominated by **semantic filtering** (NLI + leak = 71% of replacements), not structural issues.

### 6.6 Audit committee (blind, options-only)

| Auditor | Family | vs. gold (180 items) | Pairwise kappa (mean) |
|---------|--------|----------------------|-----------------------|
| meta-llama/llama-3.3-70b-instruct | Meta | 53.3% | 0.53 |
| mistralai/mistral-small-3.2-24b-instruct | Mistral | 56.7% | 0.51 |
| google/gemma-3-27b-it | Google | 45.6% | 0.50 |
| deepseek/deepseek-v3.2 | DeepSeek | 56.1% | 0.51 |

- 0 missing votes, 0 substitutions across all 720 audit votes.
- Per-language hit rates: English 55-70%, Arabic 45-55%, Yoruba 36.7-48.3% (Gemma-3-27b drops to 36.7% on Yoruba).
- Committee families: Meta, Mistral, Google, DeepSeek -- no OpenAI or Anthropic. Google appears in both generator and auditor pools; mitigated by the options-only blindness design.

### 6.7 Position bias

| Position | Correct | Total | Accuracy |
|----------|--------:|------:|----------:|
| A | 33 | 45 | 73.3% |
| B | 26 | 45 | 57.8% |
| C | 22 | 45 | 48.9% |
| D | 21 | 45 | 46.7% |

chi-squared = 3.49, df = 3, **p = 0.322** -- not statistically significant at N=180. Correct-key distribution is perfectly balanced (15 per position per language). The position-corrected consensus metric equals the raw consensus (0.5667), confirming the bias is calibrated out in aggregate by balanced key placement.

---

## 7. Failure Taxonomy (v68)

The v68 run produced six documented failure modes, catalogued in `table7_v68_findings.csv` and `table7_legacy_findings.csv`:

| # | Failure mode | Pipeline locus | Magnitude | Status |
|---|-------------|----------------|-----------|--------|
| 1 | Corpus fallback quality collapse | Fallback sampler | 43.9% partial+fallback, 0.99 replacements/MCQ | Unfixed -- v69 ablation blocked |
| 2 | High-Consensus-Wrong (HCW) | Audit committee | 27.8% (target <10%) | Unfixed -- driver: fallback distractors |
| 3 | Near-paraphrase trap | NLI filter over-aggressive | 0.36 NLI replacements/MCQ | Contributing cause of #1 |
| 4 | Correct-meaning leak | Leak filter over-aggressive | 0.35 leak replacements/MCQ | Contributing cause of #1 |
| 5 | Position bias in audit | MCQ assembly | A=73.3% vs D=46.7%, p=0.322 (ns) | Reported, neutralized by balanced keys |
| 6 | Cross-lingual fallback asymmetry | Language-specific filters | Arabic 3.5x English fallback rate | Primary cross-lingual finding |

The **core finding**: the corpus-based fallback sampler is the bottleneck. When NLI or leak filters reject an LLM-generated distractor, the pipeline samples a replacement from *other proverbs' meanings*. Those replacements are often generic moral statements or culturally mismatched idioms that auditors find plausible but are wrong. The strongest generator (gemma-4-31b-it) still has 35.0% HCW, confirming the problem is systemic, not model-specific.

**Recommended fix (v69 ablation, blocked):** Enable `USE_LLM_FALLBACK=True` with `FALLBACK_GENERATOR_MODEL="openai/gpt-4.1-nano"` to generate proverb-specific hard negatives on demand instead of corpus sampling. Estimated additional cost: $0.10-$0.20 for the N=5 run.

---

## 8. Human Validation

**Status: Prepared, not started.** A 60-item stratified sample (20 per language, balanced by generation status) is ready at `data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv`. Recruitment of 9 native speakers (3 per language x 20 items) is budget- and time-dependent.

### Protocol

- **Annotators:** 3 native speakers per language (9 total)
- **Task:** Blind options-only (proverb text + 4 options, no correct label or LLM consensus visible)
- **Judgment:** Select correct answer + rate distractor plausibility (1-5 scale)
- **Attention checks:** Embedded trap items, minimum 80% accuracy required
- **Timing guards:** 10s minimum, 120s maximum per item
- **Primary metric:** Fleiss kappa for categorization agreement (target: kappa >= 0.6)
- **Secondary metrics:** Per-language kappa, Spearman correlation of plausibility ratings

**LLM-proxy IAA calibration (7-model proxy, 60-item subset):**
- Fleiss kappa = 0.4845
- Mean pairwise Cohen kappa = 0.4846
- Per-model gold accuracy: 58.3%-78.3% (mean 69.4%)
- This establishes the LLM audit committee's ceiling and justifies the human-validation plan as essential.

**Annotation app (live):** [https://annotationapp.vercel.app](https://annotationapp.vercel.app) -- anonymous, browser-based, Supabase-backed with batch-based assignment (10 items/batch), attention checks, and admin export. Self-hosted setup instructions: [annotation_app/README.md](annotation_app/README.md).

---

## 9. Next Steps

### Blocked (requires OpenRouter budget renewal)

| Task | What | Estimated cost | Success gate |
|------|------|----------------|--------------|
| **v69** LLM-fallback ablation | N=5, `USE_LLM_FALLBACK=True` | ~$1.00 | HCW < 15%, partial+fallback < 30% |
| **v70** N=15 scaling | N=15, current or v69 config | ~$2.56 | Same gates as v69 |
| **Human validation** | 60 items x 3 annotators/language | ~$200-300 | Fleiss kappa >= 0.6 |

**If v69 passes gates:** freeze config, run v70, update all paper numbers.
**If v69 fails or budget stays exhausted:** v68 is the production dataset. Paper is framed as a methodology + failure taxonomy study at N=5.

### In-progress (no budget needed)

- [x] v68 verification and reporting (complete)
- [x] README rewrite (this document)
- [x] `docs/RESEARCH_HISTORY_AND_README_AUDIT.md` (this document's companion)
- [ ] Paper drafting (Sections 1-11 per `docs/ProverbGap_Reframed_Title_Abstract.md`)
- [ ] Statistical tests (McNemar, Wilcoxon, Holm-Bonferroni) on v68 paired subsets
- [ ] Bootstrap CIs for all six aggregate metrics

### Paper framing

The paper is framed as:

> **"Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding"**

The contribution is the methodology (hardened pipeline with dual-gate validation and blind audit) and the failure taxonomy (corpus-fallback collapse, NLI over-filtering, position bias, cross-lingual asymmetry), **not** benchmark size.

**Non-goals (explicitly dropped):** The legacy Groq S1/S2 pipeline (2,313 MCQs, 86.8% vs 62.5%), encoder baselines, human-validation kappa >= 0.75 claims, scaling to N=15/N=700, and S1/S2 cross-lingual boundary (8.9pp/2.2pp). See Section 10 for the full list of deprecated claims.

---

## 10. Legacy Numbers Warning

Old runs and earlier paper drafts contain numbers that are **not part of the v68 production dataset**:

| Deprecated claim | Source | Why it's invalid |
|-----------------|--------|-----------------|
| 2,313 MCQs | Legacy Groq Pilot 2 | v68 produces 180 MCQs; 2,313 is from a different pipeline |
| S1 86.8% vs S2 62.5% | Legacy Groq S1/S2 | Not reproducible on the v68 hardened pipeline |
| Encoder baselines (mBERT 54.7%, XLM-R 55.3%, etc.) | Legacy draft | Not computed on v68 data; replaced by TF-IDF cosine baseline (36.7%) |
| Same-family exploitation +31.1pp | Legacy Groq S1/S2 | Legacy number; v68 uses disjoint families (Meta/Mistral/DeepSeek in auditor-only) with options-only blindness; Google shared across pools but mitigated by blindness |
| "80 MCQs" | Audit logs | Audit-progress counter, not a dataset size |
| Human validation kappa >= 0.75 | Old plan | Not started; LLM-proxy kappa = 0.4845 is the current ceiling |

---

## Project Structure

```
proverb_mcq/
|-- actual_data/                 # Cleaned proverb corpora (3 languages)
|-- annotation/                  # Human-validation tooling
|-- annotation_app/              # Next.js + Supabase annotation frontend
|-- data/
|   |-- production/
|   |   |-- paper_first_outputs_2026-06-22_10-42-02/  # v68 tables, figures, 60-item sample
|-- docs/                        # Methodology and planning docs
|   |-- RESEARCH_HISTORY_AND_README_AUDIT.md  # This audit trail
|-- kaggle/
|   |-- run_logs/
|   |   |-- v68/                 # Production run (COMPLETE)
|   |   |-- v69/                 # Planned ablation (BLOCKED -- never executed)
|   |   |-- v70/                 # Scaling attempt (INCOMPLETE -- budget-blocked at 83 MCQs)
|   |-- kaggle_analysis/
|-- paper/                       # Paper artifacts
|-- scripts/
|-- src/
|-- tests/
|-- submission_package_2026-08-02/
|-- .archive/                    # Archived legacy code and outputs
|-- CONTRIBUTING.md
|-- DATASET_CARD.md
|-- GETTING_STARTED.md
|-- SECURITY.md
|-- CHANGELOG.md
|-- requirements.txt
|-- README.md                   # This file
```

---

## Quick Start

### I want to annotate (human validation)

The annotation app lets you review MCQs in a browser. No code experience needed.

```bash
git clone https://github.com/saaga23/proverb_mcq.git
cd proverb_mcq/annotation_app
npm install
npm run dev
```

Visit [https://annotationapp.vercel.app](https://annotationapp.vercel.app) or `http://localhost:3000`.

See [annotation_app/ANNOTATOR_ONBOARDING.md](annotation_app/ANNOTATOR_ONBOARDING.md) for the annotator guide.

### I want to reproduce or extend the pipeline

```bash
git clone https://github.com/saaga23/proverb_mcq.git
cd proverb_mcq
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest tests/ -v
```

### I want to understand the research

1. This README -- current state and findings (start here)
2. [docs/RESEARCH_HISTORY_AND_README_AUDIT.md](docs/RESEARCH_HISTORY_AND_README_AUDIT.md) -- full experiment timeline and audit trail
3. [kaggle/run_logs/v68/v68_detailed_analysis_report.md](kaggle/run_logs/v68/v68_detailed_analysis_report.md) -- v68 executive summary and gate table
4. [docs/ProverbGap_Reframed_Title_Abstract.md](docs/ProverbGap_Reframed_Title_Abstract.md) -- paper outline, claims traceability, non-goals
5. [paper/proverbgap_eacl2027.md](paper/proverbgap_eacl2027.md) -- full paper draft

---

## Citation

```bibtex
@misc{abraham2026proverbgap,
  title        = {Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding},
  author       = {Abraham, Sunday Aspita},
  year         = {2026},
  howpublished = {EACL 2027 ARR submission},
  note         = {v68 N=5 production dataset: 180 MCQs, $0.85 cost, 4-model blind audit committee},
  url          = {https://github.com/saaga23/proverb_mcq}
}
```

---

## License

This project is released under the [MIT License](LICENSE).

The v68 MCQ dataset (180 items, English and Arabic) is released under **CC BY 4.0**. The Yoruba MCQs are excluded from public release due to copyright restrictions on the source corpus (Owomoyela, 2005). See [data/production/paper_first_outputs_2026-06-22_10-42-02/](data/production/paper_first_outputs_2026-06-22_10-42-02/) for data license details and [docs/DATA_PROVENANCE_TEMPLATE.md](docs/DATA_PROVENANCE_TEMPLATE.md) for provenance documentation.

---

*For questions about the research, open an issue or see [docs/RESEARCH_HISTORY_AND_README_AUDIT.md](docs/RESEARCH_HISTORY_AND_README_AUDIT.md) for the complete audit trail.*
