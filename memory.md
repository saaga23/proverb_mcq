# ProverbGap MCQ — Project Memory

**Project:** Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding  
**Researcher:** Sunday Aspita Abraham (2026 Fatima Fellowship Fellow)  
**Target venue:** EACL 2027 via ARR (submission deadline 3 August 2026)  
**Last updated:** 2026-06-13

---

## 1. One-sentence summary

Cross-lingual MCQ benchmark for proverb understanding in English, Arabic, and Yoruba, built around a hardened adversarial distractor-generation pipeline and a heterogeneous model committee.

## 2. Track record used for compute applications

- **DSA 2026** — "What Happens to AI When the Lights Go Out? Infrastructure-Aware Robustness Benchmarking of Vision and NLP Models Under African Deployment Conditions" — **accepted for oral presentation**.
- **PMLR 319 / IndabaX 2026** — "Bridging the Domain Gap: Transfer Learning and Aggressive Fine-Tuning for Robust Plant Disease Detection in Low-Resource African Agriculture" — **published**.
- **DLI 2026** — "AfriKnow v11: Confident and Wrong About Africa" — submitted; reviewer feedback will guide the next venue decision (tier-B or tier-A).

## 3. Authoritative pilot results

| Setting | Result |
|---------|--------|
| Strategy 1 accuracy | 86.8% (bootstrap 95% CI [84.3%, 89.2%]) |
| Strategy 2 strict accuracy | 62.5% (bootstrap 95% CI [58.1%, 66.6%]) |
| S2 fallback rate | 21.3% |
| McNemar S1 vs S2 | χ² = 131.3, p < 0.001 |
| Per-language S1 / S2 strict | English 97.6% / 71.3%; Arabic 92.8% / 65.5%; Yoruba 70.0% / 46.2% |

## 4. Failure-mode taxonomy (negative results treated as contributions)

1. Same-family model exploitation inflated accuracy by **+31.1 pp** when generator and evaluator shared architectural lineage.
2. Chain-of-thought reasoning collapsed performance from **82.7% to 48%**.
3. Multi-stage prompting produced trivially easy distractors (100% accuracy, 0% fallback).
4. Position bias was severe (**A-position 85.6%**, p < 0.0001) before mitigation.
5. API infrastructure fragility caused **90%+ failure** rates and provider cascades.
6. Memorization signatures detectable (**Allam-2-7b: 98.4% S1 → 74.9% S2**).

## 5. Modal / Fatima compute-credit application abstract

> I am a 2026 Fatima Fellow building rigorous evaluation benchmarks for low-resource African and Arabic NLP. My track record includes an accepted oral presentation at Data Science Africa 2026, a published PMLR paper on plant-disease domain adaptation, and a Deep Learning Indaba 2026 submission on LLM confidence disparity for African versus European knowledge whose reviewer feedback will guide the next venue choice.
>
> ProverbGap MCQ tests whether large language models genuinely understand culturally embedded proverbs or exploit surface shortcuts. Covering English, Arabic, and Yoruba, the project pairs in-domain negative-sampling distractors with cross-family LLM paraphrasing, then audits every item through a heterogeneous model committee with leakage and position-bias controls. A 150-item pilot already shows a statistically significant difficulty gap (Strategy 1: 86.8%; Strategy 2: 62.5%; McNemar p < 0.001) and surfaces six reproducible failure modes, including same-family model exploitation (+31.1 pp), chain-of-thought collapse, and severe API fragility.
>
> Scaling to the planned N=700 per language, adding fill-in-the-blank and generation tasks, and running a 100-item human validation require compute that is both reliable and larger than Kaggle’s free tier. Modal credits would let me run containerized batch inference for the qwen3-32b generator and the llama-4-maverick / allam-2-7b evaluation committee without Groq rate-limit outages. AWS Trainium would support encoder baselines and small fine-tuning runs, while OpenRouter credits would provide provider failover and model diversity. I will share the resulting pipeline, audit logs, and dataset splits with other Fatima fellows, especially those working on Arabic NLP and document-AI evaluation, so the infrastructure benefits the wider cohort.

**Word count:** ~240 words.

## 6. Next steps

1. Scale pilot from N=150 to N=700 proverbs per language.
2. Add fill-in-the-blank and generation tasks.
3. Complete 100-item human validity audit.
4. Submit to EACL 2027 ARR (3 Aug 2026).

---
*Single source of truth for the MCQ sub-project. If any other document conflicts with this file, this file wins unless the conflict is explicitly flagged for resolution.*


---

## CURRENT STATE UPDATE - June 13, 2026 (Kaggle Last_run Deep Analysis)

### Summary

Deep multi-agent analysis of `kaggle_analysis/Last_run/` completed. The infrastructure fixes **worked**: 8 valid Groq keys, zero HTTP 429 errors, 15.0% failure rate (down from ~90%), and 900/900 evaluations completed.

However, a **critical S1 answer-key drift bug** was discovered. The saved `mcqs_s1.csv` was regenerated after evaluation, and because S1 uses `random.shuffle` without a per-item seed, 76.7% of S1 evaluation rows have answer keys that do not match the saved MCQ files. **S2 is unaffected and valid.**

### Key Findings

| Finding | Value | Status |
|---|---|---|
| Valid Groq keys loaded | 8 / 11 | PASS |
| HTTP 429 errors in log | 0 | PASS |
| API client `total_failures` | 0 all models | PASS |
| Evaluations completed | 900 / 900 | PASS |
| Overall failure rate | 15.0% (135 / 900) | PASS |
| All failures from `gptoss120b` empty_response | 135 / 135 | WARNING |
| S2 fallback rate | 4.67% | PASS |
| S1 answer-key mismatches | 345 / 450 (76.7%) | FAIL |
| S2 answer-key mismatches | 0 / 450 | PASS |
| Log-reported S1 accuracy | 79.3% | INVALID |
| Actual S1 accuracy vs saved MCQs | 25.9% | ARTIFACT |
| Actual S2 accuracy vs saved MCQs | 80.2% | VALID |

### Root Cause

S1 generation in `kaggle_full_pipeline_notebook.py`:
- Uses a single global `random.seed(SEED)`.
- Does not re-seed per item.
- Has no resume guard (`if mcqs_s1.csv exists: skip`).

Because `main()` runs twice in the Kaggle notebook (full run + final resume/check), S1 was generated twice with different RNG states, producing different answer-letter mappings. S2 has resume logic and was not regenerated.

### Per-Model Failure Pattern (New Run)

| Model | Calls | Failures | Failure Rate | Valid Accuracy |
|---|---|---|---|---|
| llama33-70b | 300 | 0 | 0.0% | 77.3% |
| qwen3-32b | 522* | 0 | 0.0% | 73.3% |
| gptoss120b | 300 | 135 | 45.0% | 95.8% |

* Qwen's extra 222 calls are from S2 adversarial distractor generation.

`gptoss120b` empty-response breakdown:
- English: 4.0% failure
- Arabic: 46.0% failure
- Yoruba: 85.0% failure

### Comparison with Local Same-3-Model Baseline

| Metric | New Kaggle | Local v5 (3 models) |
|---|---|---|
| Failure rate | 15.0% | 20.1% |
| Overall success | 67.8% | 62.3% |
| Valid accuracy | 79.7% | 78.0% |

The new Kaggle run is actually cleaner than the local same-3-model baseline, mainly because `llama33-70b` had 0% failures on Kaggle vs 10.7% locally.

### Actions Taken

1. **Patched `kaggle_full_pipeline_notebook.py`:**
   - Added per-item deterministic seed before S1 sampling/shuffling: `random.seed(SEED + hash(sid) % 10_000_000)`.
   - Added S1 resume guard: skip generation if `mcqs_s1.csv` already exists.
   - Added post-evaluation answer-key consistency check that prints a warning if mismatch is detected.

2. **Created `audit_answer_key_consistency.py`:**
   - Standalone script to validate any run directory.
   - Usage: `python audit_answer_key_consistency.py kaggle_analysis/Last_run/extracted_new`

3. **Wrote decision report:**
   - `kaggle_analysis/Last_run/DECISION_REPORT.md`
   - Updated `kaggle_analysis/comparison_report.md` with the S1 finding.

4. **Created project history Word document:**
   - `ProverbGap_MCQ_Project_History.docx` (June 15, 2026)
   - Plain-language summary of the entire project from v1 to current state, including hypotheses, fallbacks, reviewer concerns, and OpenRouter plan.

### Updated Decisions

| Decision | Date | Rationale |
|---|---|---|
| Fix S1 determinism + resume guard | 2026-06-13 | Prevents answer-key drift on re-generation |
| Re-run Kaggle once more | 2026-06-13 | Infrastructure works; only S1 bug remains |
| Delete eval CSVs before re-run | 2026-06-13 | Forces re-evaluation against deterministic S1 |
| Use audit script after every run | 2026-06-13 | Catch answer-key mismatches automatically |
| Keep gptoss120b with caveats | 2026-06-13 | 55% valid responses; very accurate when valid |
| Fatima/HF compute as parallel track | 2026-06-13 | Not blocking; pursue for credits/larger models |
| Use OpenRouter credits for committee diversity | 2026-06-15 | Adds reliable evaluators, replaces GPT-OSS for AR/YO |

### Concrete Next Steps

1. Apply the S1 patch to the Kaggle notebook (already done in local `.py` source).
2. Before uploading to Kaggle, delete `eval_results.csv` and `eval_results_progress.csv` from the working directory.
3. Re-run the notebook on Kaggle.
4. After the run, run `python audit_answer_key_consistency.py <run_dir>` locally to confirm S1/S2 consistency.
5. If consistent, use the new run as the primary paper result.
6. If not possible to re-run, fall back to hybrid (local S1 + Kaggle S2) or pre-computed local dataset.
7. Use OpenRouter credits to test 1-2 additional committee models on small N=10/20 samples before adding to main run.
8. Continue Fatima mentor outreach in parallel.

### Updated Data Points

| Fact | Value |
|---|---|
| Latest Kaggle failure rate | 15.0% |
| Latest Kaggle HTTP 429 errors | 0 |
| Valid Groq keys | 8 |
| S1 answer-key mismatch (Last_run) | 76.7% |
| S2 validity (Last_run) | PASS consistent |
| S2 fallback rate | 4.67% |
| gptoss120b Yoruba failure rate | 85.0% |
| S2 actual accuracy vs saved MCQs | 80.2% |
| Project history document | ProverbGap_MCQ_Project_History.docx |

---

*End of Current State Update - June 15, 2026*
