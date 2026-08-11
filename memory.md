# ProverbGap MCQ — Project Memory

**Project:** Hardened Adversarial Distractor Generation for Low-Resource Figurative Language: A Case Study in Proverb Understanding  
**Researcher:** Sunday Aspita Abraham (2026 Fatima Fellowship Fellow)  
**Target venue:** EACL 2027 via ARR (submission deadline 3 August 2026)  
**Last updated:** 2026-06-22

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




---

## Current State Update - June 19, 2026 (OpenRouter Pilot 1 TEST v2.1)

### Summary

The OpenRouter Pilot 1 TEST notebook (`openrouter_pilot_distractor_generation_test_nano_opus.ipynb`) was built to stress-test a multi-model distractor-generation and blind-audit pipeline before committing to the full Strategy-2 evaluation. An N=1 smoke test (3 proverbs: 1 per language) completed on 2026-06-17 with **infrastructure PASS, quality FAIL**. v2.1 fixes were applied and locally validated.

### Key files

| File | Purpose |
|---|---|
| `openrouter_pilot_distractor_generation_test_nano_opus.py` | Full source (config, dynamic pools, prompts, generation, self-critique, audit, visualisations). |
| `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` | Self-contained Kaggle notebook regenerated from the source; **upload this**. |
| `pilot1_prompt_variants.json` | 5 adversarial prompt variants; embedded as base64 in the notebook. |
| `kaggle_analysis/preflight_audit_test_nano_opus.md` | Methodology / preflight report (updated for v2.1). |
| `kaggle_analysis/Last_run/pilot 1/` | N=1 smoke-test outputs from 2026-06-17. |
| `docs/Elite_Research_Execution_Plan.md` | Research plan and reviewer-risk checklist. |
| `AGENTS.md` | Agent handover with latest findings and next-step checklist. |
| `memory.md` | This file. |

### Configuration

```python
N_PER_LANG = 1                       # 3 proverbs total
SEED = 20260615
COST_CAP_USD = 5.0
CRITIC_MODEL = "anthropic/claude-3.5-haiku"
USE_SELF_CRITIQUE = True
MAX_TOKENS_GEN = 4096
MAX_TOKENS_AUDIT = 256

GENERATOR_POOL (starters) = [
    "qwen/qwen3.5-397b-a17b",
    "google/gemma-4-31b-it",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-v4-pro",
    "anthropic/claude-opus-4.8",
    "qwen/qwen3.7-max",
]
GENERATOR_POOL (substitutes) = [
    "google/gemini-2.5-pro",
    "google/gemini-2.5-flash",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1-nano",
]

COMMITTEE_POOL (starters) = [
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct",
    "google/gemma-3-27b-it",
    "qwen/qwen3-32b",
]
COMMITTEE_POOL (substitutes) = [
    "openai/gpt-4o-mini",
    "deepseek/deepseek-v3.2",
    "meta-llama/llama-3.1-405b-instruct",
    "amazon/nova-lite-v1",
]
```

### N=1 smoke-test results (2026-06-17)

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 95 (6 active generators × 5 variants × 3 proverbs, plus partial rows) |
| MCQs audited | 95 |
| Total cost | **$0.64 / $5.00** (12.8% of cap) |
| Wall duration | ~46 minutes |
| Hard fallback rate | 2.1% (2/95) ✅ |
| Active generators after preflight | 6 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **49.5%** (47/95) — too high |
| High-consensus-wrong rate | **26.3%** (25/95 with consensus_frac ≥ 0.75 but wrong) |
| Duplicate options | 0 ✅ |
| Correct-key balance | A=24, B=24, C=24, D=23 ✅ |
| Partial / fallback items | 31.6% (30/95) — too high |

**Per-language consensus correctness:**
| Language | Consensus correct |
|---|---|
| English | 75.0% |
| Arabic | 53.1% |
| **Yoruba** | **35.5%** ❌ |

**Per-auditor hit rates:**
| Auditor | Hit rate |
|---|---|
| meta-llama/llama-3.3-70b-instruct | 57.9% |
| google/gemma-3-27b-it | 52.6% |
| mistralai/mistral-small-3.2-24b-instruct | 52.6% |
| openai/gpt-4o-mini *(substitute)* | 42.9% ❌ |

`anthropic/claude-sonnet-4` (benched) missed **83.2%** of votes due to parse failures.

### Critical issues found

1. **Self-critique disabled:** `google/gemini-2.5-flash-preview` is **not a valid OpenRouter model ID**.
2. **Weak auditor starter:** `anthropic/claude-sonnet-4` produced unparseable votes; substitute `gpt-4o-mini` had the lowest hit rate.
3. **Confident-wrong consensus:** 26.3% of items had strong consensus (≥0.75) but wrong label — signature of shared surface shortcuts.
4. **Yoruba pipeline broken:** 35.5% consensus correctness.
5. **High partial/fallback rate:** 21.1% partial + 8.4% length_fallback + 2.1% hard_fallback.
6. **Meta-text leaks:** options contained markdown headings like `**Crafting Options**`.
7. **Resume-state bug:** `pool_state.json` reported `generation_done=false` and `audit_done=false` despite completion.
8. **Unreliable generators:** `qwen/qwen3-14b` 73.3% fallback, `llama-4-scout` 100% failure, `gpt-4.1` 33.3% fallback.

### v2.1 fixes applied

1. **Self-critique:** switched to valid `anthropic/claude-3.5-haiku`.
2. **Audit starters:** reordered; removed `claude-sonnet-4` from starters.
3. **Generator substitutes:** replaced high-fallback models with `gemini-2.5-pro`, `gemini-2.5-flash`, `gpt-4.1-mini`, `gpt-4.1-nano`.
4. **Meta-text rejection:** `has_meta_text()` treats markdown / instruction leaks as parse failures.
5. **Length check:** median-of-four-options reference instead of correct-meaning-only reference.
6. **Vote extraction:** hardened for bold, parentheses, markers, JSON answer objects.
7. **Resume state:** `save_state()` now passes `generation_done` / `audit_done` flags.
8. **Prompt catalog:** replaced `few-shot-predictive` (55.6% fallback) with `adversarial-contrastive`.
9. **Documentation:** updated `AGENTS.md`, preflight report, conversion script, and this memory file.
10. **Local validation:** end-to-end dry-run with mocked APIs produced 90 MCQs, 0 duplicates, balanced keys, and correct state flags.

### Quality gates for the next N=1 smoke test

| Gate | Target |
|---|---|
| Hard fallback rate | < 5% |
| Partial + fallback rate | < 15% |
| Active generators/auditors after preflight | ≥ 3 each |
| Perfect consensus rate | < 30% |
| High-consensus-wrong rate | < 10% |
| Per-language consensus correctness | ≥ 50% each (especially Yoruba) |
| Duplicate options | 0% |
| Correct-key balance | ~25% each for A-D |
| Cost | Under $5.00 |

### Concrete next steps

1. Upload the regenerated `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` to Kaggle.
2. Add Kaggle Secret `OPENROUTER_API_KEY` and attach dataset `abrahamsunday123/full-data-complete`.
3. Run with `N_PER_LANG = 1`.
4. Download `/kaggle/working/openrouter_pilot1_test_output/`.
5. Verify gates above; if any fail, fix and repeat before raising `N_PER_LANG` to 5.
6. Continue parallel work on S1 determinism patch / main Kaggle S1+S2 re-run.

---

*End of Current State Update - June 19, 2026 (OpenRouter Pilot 1 TEST v2.1)*


---

## Post-Smoke-Test Analysis and v2.2 Fixes - June 19, 2026

A second N=1 smoke test was executed on Kaggle on 2026-06-19 using the v2.1 notebook.
The output was downloaded to `kaggle_analysis/last_run_june_19th/results_extracted/openrouter_pilot1_test_output/`.

### June 19 N=1 smoke-test results

| Metric | Value |
|---|---|
| Sample | 3 proverbs (1 Arabic, 1 English, 1 Yoruba) |
| MCQs generated | 90 |
| MCQs audited | 90 |
| Total cost | **$0.94 / $5.00** (18.8% of cap) |
| Wall duration | ~68 minutes |
| Hard fallback rate | 2.2% (2/90) ✅ |
| Partial + fallback rate | 11.1% (10/90) ✅ |
| Active generators after preflight | 6 ✅ |
| Active auditors after preflight | 4 ✅ |
| Perfect consensus rate | **55.6%** (50/90) ❌ |
| High-consensus-wrong rate | **38.9%** (35/90) ❌ |
| Duplicate options | 0 ✅ |
| Correct-key balance | A=23, B=23, C=22, D=22 ✅ |

### Per-language consensus correctness (June 19)

| Language | Consensus correct |
|---|---|
| English | 86.7% ✅ |
| Arabic | 53.3% ⚠️ |
| **Yoruba** | **16.7%** ❌ |

### Per-auditor hit rates (June 19)

| Auditor | Hit rate |
|---|---|
| mistralai/mistral-small-3.2-24b-instruct | 54.4% |
| meta-llama/llama-3.3-70b-instruct | 47.8% |
| google/gemma-3-27b-it | 46.7% |
| openai/gpt-4o-mini *(substitute)* | 37.9% ❌ |

`qwen/qwen3-32b` was benched after missing **97.8%** of audit votes due to a `ValueError` during vote extraction.

### New critical findings

1. **Audit committee quality degraded.** `qwen/qwen3-32b` failed to produce parseable votes and was replaced by `openai/gpt-4o-mini`, the weakest auditor. This substitution increased confident-wrong consensus.
2. **Self-critique is ineffective.** With a valid critic model, the critic picked the correct answer on every item and triggered a rewrite, but the rewrites did not reduce perfect consensus or high-consensus-wrong rates. The loop added cost, latency, and meta-text leakage risk.
3. **Yoruba quality collapsed.** Consensus correctness dropped from 35.5% to 16.7%. Generators inserted generic English idioms/proverbs (e.g., "a bird in the hand is worth two in the bush") as distractors, which are culturally mismatched.
4. **Confident-wrong consensus increased.** High-consensus-wrong rose from 26.3% to 38.9%, indicating distractors still carry shared surface shortcuts.
5. **Meta-text leaks persist.** `google/gemini-2.5-pro` and `google/gemini-2.5-flash` still occasionally emitted markdown headings such as `**Generating Options**`.

### v2.2 fixes applied

1. **Audit committee:**
   - Removed `qwen/qwen3-32b` from starter auditors (97.8% missing votes).
   - Removed `openai/gpt-4o-mini` from substitutes (37.9% hit rate).
   - Removed `meta-llama/llama-3.1-405b-instruct` from substitutes (404 Not Found in preflight).
   - New starters: `meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-small-3.2-24b-instruct`, `google/gemma-3-27b-it`, `anthropic/claude-3.5-haiku`.
   - New substitutes: `deepseek/deepseek-v3.2`, `amazon/nova-lite-v1`.
2. **Self-critique:** disabled (`USE_SELF_CRITIQUE = False`) for the next smoke test. The infrastructure remains in place so it can be redesigned later if needed.
3. **Yoruba hardening:**
   - Added a Yoruba cultural-context instruction to the generation prompt, instructing models to avoid generic English idioms and stay within a Yoruba cultural frame.
   - Added `_YORUBA_ENGLISH_IDIOM_BLOCKLIST` and `has_yoruba_english_idiom()` validator. If any Yoruba option matches a generic English proverb/idiom, the response is treated as a parse fallback and replaced with corpus fallback distractors.
4. **Notebook:** regenerated `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` from the updated source and conversion script.
5. **Local validation:** syntax check and mocked end-to-end dry-run passed, producing 90 MCQs, balanced keys, and correct state flags. The Yoruba blocklist correctly triggered parse_fallback on mocked generic-idiom outputs.

### Updated success criteria for the next N=1 smoke test

| Gate | Target |
|---|---|
| Hard fallback rate | < 5% |
| Partial + fallback rate | < 15% |
| Active generators/auditors after preflight | ≥ 3 each |
| Perfect consensus rate | < 30% |
| High-consensus-wrong rate | < 10% |
| Per-language consensus correctness | ≥ 50% each (especially Yoruba) |
| Duplicate options | 0% |
| Correct-key balance | ~25% each for A-D |
| Cost | Under $5.00 |

---

*End of Current State Update - June 19, 2026 (v2.2)*


---

## Current State Update - June 19, 2026 (OpenRouter Pilot 2 v3 S1/S2 evaluator)

### Focus

User clarified they wanted the pilot S1/S2 evaluator notebook upgraded with the hardened patterns from the generation pilot notebook, not the legacy Groq main pipeline.

### Action taken

Created `openrouter_pilot_s1_s2_evaluator_v3.py` and regenerated `openrouter_pilot_s1_s2_evaluator.ipynb`.

**Deep upgrades from `openrouter_pilot_distractor_generation_test_nano_opus.py`:**
1. **Same data source:** uses `/kaggle/input/datasets/abrahamsunday123/full-data-complete` with local fallback `actual_data/cleaned`; identical CSV column renaming for English/Arabic/Yoruba.
2. **Dynamic model pools:**
   - `GENERATOR_POOL`: 2 starters (`google/gemini-2.5-pro`, `qwen/qwen3.5-397b-a17b`) + 4 substitutes.
   - `AUDIT_POOL`: 4 starters (`meta-llama/llama-3.3-70b-instruct`, `mistralai/mistral-small-3.2-24b-instruct`, `google/gemma-3-27b-it`, `anthropic/claude-3.5-haiku`) + 2 substitutes.
   - Pools are **disjoint** to prevent audit contamination.
3. **Hardened OpenRouter client:** `openrouter_chat` now uses `max_completion_tokens` for OpenAI reasoning families and falls back through 400/422 rejection strategies.
4. **Cost control:** `CostTracker` with `refresh_price_table()` and a `$5` hard cap.
5. **Preflight:** live catalog fetch, cheap echo-letter probes (`api_preflight`), and real-path S1/S2 probes before the main spend.
6. **Robust parsers:** copied `parse_options`, `extract_choice`, and `parser_self_test` from the generation pilot.
7. **S1 generation:** proverb → 4 English meanings; meta-text / meta-word rejection; length parity ±20%; optional sentence-transformer paraphrase guard (threshold 0.85); Yoruba English-idiom blocklist; corpus-based fallback.
8. **S2 generation:** English meaning → 4 source-language proverbs; source-language retention; duplicate/rewording rejection; ASCII-ratio guard; meta-text rejection; corpus-based fallback.
9. **Audit:** blind A-D votes from the dynamic committee, consensus computation with deterministic tie-breaking.
10. **Outputs & state:** `mcqs_s1.csv`, `mcqs_s2.csv`, `pilot2_eval_results.csv`, `pilot2_summary.json`, `pilot2_state.json`, `pilot2_raw_outputs.csv`.

### Files changed

- `openrouter_pilot_s1_s2_evaluator_v3.py` (new)
- `openrouter_pilot_s1_s2_evaluator.ipynb` (regenerated from v3)
- `convert_pilot2_to_notebook.py` (points to v3, installs `sentence-transformers`)
- `test_pilot2_local.py` (rewritten for v3)
- `AGENTS.md`
- `memory.md`

### Validation

- `python -m py_compile openrouter_pilot_s1_s2_evaluator_v3.py` ✅
- `python convert_pilot2_to_notebook.py` ✅
- `python test_pilot2_local.py` ✅ (mocked end-to-end; produces all expected outputs)

### Next steps

1. Upload `openrouter_pilot_s1_s2_evaluator.ipynb` to Kaggle.
2. Add `OPENROUTER_API_KEY` secret and attach `abrahamsunday123/full-data-complete`.
3. Run a small smoke test (`N_PER_LANG = 2–3`) to confirm live-model behavior and cost, then scale to 10.
4. Inspect `pilot2_summary.json` for fallback rates and consensus accuracy; iterate if needed.

---

*End of Current State Update - June 19, 2026 (OpenRouter Pilot 2 v3)*


---

## Current State Update - June 19, 2026 (Anthropic cost reduction)

### Decision

User wanted to drop the expensive `anthropic/claude-opus-4.8` ($5 input / $25 output per 1M tokens) from the pilot notebooks and use a cheaper Anthropic model that still works.

### Action taken

- **Pilot 1 TEST generator pool:** replaced `anthropic/claude-opus-4.8` with `anthropic/claude-sonnet-4` ($3 / $15 per 1M).
- **Pilot 2 v3 generator pool:** added `anthropic/claude-sonnet-4` as a starter (alongside `google/gemini-2.5-pro` and `qwen/qwen3.5-397b-a17b`). `claude-opus-4.8` is not used anywhere in Pilot 2 v3.
- Both notebooks regenerated from their updated `.py` sources.
- Updated `test_pilot1_nano_opus_local.py` mock signature to match the current `openrouter_chat(..., response_format=...)` API; test now passes end-to-end.
- `test_pilot2_local.py` still passes.

### Validation

```bash
python -m py_compile openrouter_pilot_distractor_generation_test_nano_opus.py
python convert_test_nano_opus_to_notebook.py
python test_pilot1_nano_opus_local.py        # ✅

python -m py_compile openrouter_pilot_s1_s2_evaluator_v3.py
python convert_pilot2_to_notebook.py
python test_pilot2_local.py                  # ✅
```

---

*End of Current State Update - June 19, 2026 (Anthropic cost reduction)*


---

## Current State Update - June 19, 2026 (OpenRouter Kaggle runs + stale-markdown cleanup)

### 1. Two Kaggle pilots were executed and deeply audited

Both notebooks were uploaded to Kaggle and run; outputs were downloaded and analyzed line-by-line.

#### Generation Pilot (Pilot 1 TEST, v2.2)

| | |
|---|---|
| Notebook | `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` |
| Sample | `N_PER_LANG = 1` → 3 proverbs → 90 MCQs |
| Cost | **$0.52 / $5.00** |
| Hard fallback | 2.2% ✅ |
| Partial + fallback | 16.7% ❌ (target <15%) |
| Perfect consensus | **61.1%** ❌ (target <30%) |
| High-consensus-wrong | **20.0%** ❌ (target <10%) |
| Yoruba consensus correct | **43.3%** ❌ (target ≥50%) |
| English consensus correct | 90.0% ✅ |
| Arabic consensus correct | 60.0% ✅ |
| Key balance | 23/23/22/22 ✅ |
| Duplicates | 0 ✅ |

**Verdict:** infrastructure PASS, quality FAIL.

#### S1/S2 Pilot (Pilot 2 v3)

| | |
|---|---|
| Notebook | `openrouter_pilot_s1_s2_evaluator.ipynb` |
| Sample | `N_PER_LANG = 10` → 30 proverbs → 60 MCQs |
| Cost | **$0.78 / $5.00** |
| S1 consensus accuracy | 76.7% |
| S2 consensus accuracy | 83.3% (unexpectedly easier than S1) |
| High-confidence-wrong | 15.0% ❌ (target <10%) |
| Perfect consensus | 68.3% ❌ (target <30%) |
| S1 partial+fallback | 43.3% ❌ |
| S2 partial+fallback | 26.7% ❌ |

**Verdict:** infrastructure PASS, quality FAIL, plus two critical bugs.

### 2. Critical bugs discovered

| Priority | Bug | Evidence | Fix required |
|---|---|---|---|
| **P0** | `anthropic/claude-3.5-haiku` is EOL on OpenRouter/AWS Bedrock (404). | Both runs hit `This model version has reached the end of its life.` It was auto-benched and substituted by `deepseek/deepseek-v3.2`. | Permanently replace `claude-3.5-haiku` with a verified active Anthropic model in **both** pilot sources. The substitute `deepseek/deepseek-v3.2` performed well (66–80% hit rates), so it can be promoted to starter. |
| **P0** | S1/S2 position bias. | S1 correct answers were **only A or C**; S2 correct answers were **only B or D**. The `assemble_mcq()` function used `idx % 4` inside separate S1 and S2 loops. | Use a shared global position counter so A/B/C/D are each correct ~25% of the time across S1+S2. Re-key the existing `mcqs_s1.csv` / `mcqs_s2.csv` from the Pilot 2 run so the data is not wasted. |
| **P0** | S1/S2 single-generator usage. | All 60 final MCQs list `generator_model = google/gemini-2.5-pro` even though the pool had 3 active generators. | Actually rotate generators per item instead of always using `active[0]`. |
| **P1** | Pilot 1 distractors are too easy. | 61.1% perfect consensus, 20% high-consensus-wrong, Yoruba 43.3% consensus-correct. | Sharpen length/register locks, reject generic/unrelated distractors, add post-generation filter dropping items where >2 auditors agree on the correct answer. |
| **P1** | Yoruba generation collapsed. | Generic English idioms leaked into Yoruba options. | Harden Yoruba prompt + blocklist; add few-shot examples; constrain corpus fallback. |
| **P1** | Arabic gold-meaning alignment crisis. | Same 3 Arabic proverbs (`160`, `591`, `396`) failed in both S1 and S2 with confident wrong consensus; S1 Arabic consensus correct only 50%. | Manually review source gold meanings for these proverbs; consider excluding or re-annotating if the source alignment is wrong. |
| **P1** | Meta-text leaks persist. | Gemini 2.5 Pro still emitted markdown headings (`**Generating Options**`, `**Crafting Options**`). | Strengthen `has_meta_text()` patterns and treat any heading-like string as a hard parse failure. |
| **P2** | S2 easier than S1. | S2 accuracy 83.3% > S1 76.7%, contradicting the intended difficulty gap. | After fixing position bias and generator rotation, verify whether the semantic paraphrase guard is too aggressive or whether S2 prompts need to be made harder. |
| **P2** | Generator reliability. | In Pilot 1, `qwen/qwen3.5-397b-a17b`, `meta-llama/llama-4-maverick`, and `deepseek/deepseek-v4-pro` were benched due to truncation/empty responses. | Continue relying on dynamic substitution; consider demoting these models to lower-priority substitutes. |

### 3. Stale-markdown cleanup

A large set of root-level and nested markdown files claimed authority but described outdated code, models, file paths, or plans. They were archived to keep the working tree from misleading future agents.

**Archive location:** `.archive/stale_markdown_2026-06-19/`

**Manifest:** `.archive/stale_markdown_2026-06-19/ARCHIVED_STALE_MARKDOWN_MANIFEST.md`

**Most dangerous archived files:**
- `OPENROUTER_PILOT_SPEC.md` — wrong model IDs, wrong notebook names, wrong paths.
- `PLAN_v4.3_FINAL.md` / `HANDOVER_FINAL_v436.md` — claimed to be authoritative but described the old Groq v4.3.6 pipeline.
- `EACL_7DAY_EXECUTION_PLAN.md` — stale sprint plan with team assignments and Overleaf setup.
- `KAGGLE_UPLOAD_GUIDE.md` — old workflow plus a **hardcoded Groq API key in plain text** (security exposure).
- `CATASTROPHIC_MISMATCH_SYNTHESIS.md`, `EACL_STRATEGY_SYNTHESIS.md`, old `MASTER_AUDIT_REPORT*.md`, old `MCQ_QUALITY_REVIEW.md`, etc.
- `tomorrow_resume/` — duplicate/stale copies of mentor briefs, notebook, and run outputs.
- `kaggle_analysis/Last_run/{forensic_audit_report.md, generation_failure_report.md, quality_and_recommendations_report.md}` — described the 2026-06-13 Kaggle run that had 76.7% S1 answer-key drift.

**Deprecation headers added to (kept in place but flagged):**
- `kaggle_analysis/AGENTS.md`
- `kaggle_analysis/README.md`
- `kaggle_analysis/comparison_report.md`
- `kaggle_analysis/MISSING_DATA_IMPACT_REPORT.md`
- `kaggle_analysis/reports/MENTOR_REPORT.md`
- `kaggle_analysis/reports/scale_readiness_report.md`
- `kaggle_analysis/reports/unified_analysis_report.md`

**Security note:** `KAGGLE_UPLOAD_GUIDE.md` contained a plaintext Groq key. The file has been archived out of the active working tree. If that key was ever committed or shared, it should be rotated.

### 4. Updated model pool guidance

Based on the two live runs:

- **`anthropic/claude-3.5-haiku` must be removed** from both Pilot 1 TEST and Pilot 2 v3 source files. It is EOL and returns AWS Bedrock 404.
- **`deepseek/deepseek-v3.2` performed reliably** as an auditor substitute and can be promoted to a starter or kept as the first substitute.
- **`qwen/qwen3.5-397b-a17b`, `meta-llama/llama-4-maverick`, and `deepseek/deepseek-v4-pro` are risky generators** due to truncation/empty responses; keep them in the pool but expect substitution.
- **`anthropic/claude-opus-4.8` is already removed** from both pilots (cost reduction). `anthropic/claude-sonnet-4` is the current Anthropic stand-in.

### 5. Concrete next steps

#### P0 — Fix before any re-run
1. Replace EOL `anthropic/claude-3.5-haiku` in both `openrouter_pilot_distractor_generation_test_nano_opus.py` and `openrouter_pilot_s1_s2_evaluator_v3.py`.
2. Fix Pilot 2 v3 position bias: shared global counter for S1+S2 `assemble_mcq()`.
3. Fix Pilot 2 v3 generator rotation so all 3 active generators are actually used.
4. Re-key the existing `mcqs_s1.csv` / `mcqs_s2.csv` from the Pilot 2 run so the data is usable.
5. Regenerate both notebooks from updated sources.
6. Re-run local mocked tests (`test_pilot1_nano_opus_local.py`, `test_pilot2_local.py`).

#### P1 — Harden quality before scaling
7. Reduce perfect consensus in Pilot 1 from 61% to <30%:
   - Add a post-generation filter that drops items where >2 auditors agree on the correct answer.
   - Tighten length/register parity rules.
   - Reject generic/unrelated distractors more aggressively.
8. Fix Yoruba generation: add few-shot examples, strengthen the English-idiom blocklist, and constrain corpus fallback.
9. Investigate the 3 repeat-failing Arabic proverbs (`160`, `591`, `396`) and decide if source gold meanings are wrong.
10. Lower partial+fallback rates in Pilot 2, especially Yoruba S2.

#### P2 — Validate
11. Re-run **Pilot 1** N=1 smoke test.
12. Re-run **Pilot 2** N=2–3 smoke test, then N=10.
13. Only scale to N=5/N=15 after both smoke tests pass all gates.

*End of Current State Update - June 19, 2026 (Kaggle runs + markdown cleanup)*


---

## Current State Update - June 20, 2026 (OpenRouter Pilot P0 fixes + literature audit + cleanup)

### Summary

A deep research-driven audit cycle was executed to decide whether the blind shortcut audit is over-engineered, fix the P0 bugs discovered in the June 19 Kaggle runs, clean the working tree, and prepare for iterative smoke-test-and-fix cycles.

Three foreground agents were used in parallel:
- **Research agent:** literature review on options-only / shortcut audits in MCQA.
- **Code audit agent:** line-level audit of both pilot source files.
- **Cleanup inventory agent:** rigorous classification of stale files/folders.

All P0 bugs were fixed, both notebooks regenerated, local mocked tests passed, existing Pilot 2 CSVs were re-keyed, and the working tree was substantially cleaned.

### Literature verdict on the blind shortcut audit

**KEEP the audit, but reframe it as SUPPLEMENTARY** to a broader distractor-quality validation suite. It is **not over-engineered**:

- **Balepur et al. (ACL 2024)** introduced *choices-only* prompts as a standard shortcut baseline and call for stronger MCQA baselines.
- **Chandak et al. (2025)** report 83% accuracy on TruthfulQA v2 and 39% on MMLU **without the question**, framing options-only performance as a lower-bound on discriminative shortcuts.
- **Turner & Kurzeja (2025)** show an "odd one out" heuristic reaches 73% on TruthfulQA MC1 while hiding the question.
- **Balepur (2026) BenchMarker** packages options-only shortcut detection into a reusable MCQA auditing toolkit.
- Recent proverb benchmarks (ProverbEval, Jawaher, MasalBench, FFE-Hallu, ePiC) combine automatic diagnostics with human plausibility verification and report position/shuffling effects.

**What reviewers will expect alongside the audit:**
1. Human plausibility/validity audit with IAA (0-2 rubric, Cohen's κ).
2. Distractor-efficiency metrics (functional vs. non-functional distractors).
3. Option-shuffling robustness (flip rate, accuracy variance).
4. All-A / all-D / random baselines.
5. Length / format / meta-text audit.
6. Contrast sets or question-inference checks to distinguish abduction from shallow shortcuts.
7. LLM-as-judge calibration against human ratings.

Full report: `agent_literature_shortcut_audit.md`.

### P0 fixes applied

#### Both pilots
- **Replaced EOL `anthropic/claude-3.5-haiku`** with `deepseek/deepseek-v3.2` in:
  - Pilot 1 TEST: `CRITIC_MODEL` and `COMMITTEE_POOL` starter.
  - Pilot 2 v3: `AUDIT_POOL` starter.
- Removed the `anthropic/claude-3.5-haiku` price-table entry from both files.
- Hardened `_META_PATTERNS` to catch markdown bold/italic/inline code, stage labels (`step 1`, `final output`, `selected options`), and additional instruction leaks.
- Expanded and fuzzy-matched the Yoruba English-idiom blocklist (now ~120 entries) with punctuation-insensitive `_normalize_for_blocklist()` matching.

#### Pilot 2 v3
- **Fixed position bias:** split the single `POSITION_COUNTER` into independent `S1_POSITION_COUNTER` and `S2_POSITION_COUNTER`, updated `assemble_mcq(opts, counter_name=...)` to accept a strategy name, and updated all S1/S2 calls, state save/load, and the local test.
- **Fixed generator rotation:** replaced the `generator_model = generator_pool.active[0]` bug with a round-robin `_generator_rotation_index` that cycles through `generator_pool.active` per proverb.
- Fixed `extract_choice()` regexes to accept `answer = X` and `{"answer": "X"}` patterns (`[:=]` instead of `[:]`).
- Added Yoruba English-idiom blocklist enforcement to S2 generation.
- Updated the generation cost estimate to average across active generators instead of assuming only `active[0]`.

#### Pilot 1 TEST
- Docstrings/comments updated to reflect the new audit/critic model.

### Validation

```bash
python -m py_compile openrouter_pilot_distractor_generation_test_nano_opus.py
python -m py_compile openrouter_pilot_s1_s2_evaluator_v3.py
python convert_test_nano_opus_to_notebook.py
python convert_pilot2_to_notebook.py
python test_pilot1_nano_opus_local.py      # PASS
python test_pilot2_local.py                # PASS
```

Pilot 2 position-distribution check after the fix (N=15 mocked run):
- S1: A=4, B=4, C=4, D=3
- S2: A=4, B=4, C=4, D=3
- Generators used: `google/gemini-2.5-pro`, `qwen/qwen3.5-397b-a17b`, `anthropic/claude-sonnet-4`

### Re-keying of existing Pilot 2 data

The June 19 Pilot 2 run produced valid options but biased correct-key positions (S1 only A/C, S2 only B/D). A re-keying script, `rekey_s1_s2_pilot_v1.py`, was created and run:

```bash
python rekey_s1_s2_pilot_v1.py
```

Output:
- `S1_S2_pilot_v1/extracted/mcqs_s1_rekeyed.csv` — Answer distribution A=8, B=8, C=7, D=7
- `S1_S2_pilot_v1/extracted/mcqs_s2_rekeyed.csv` — Answer distribution A=8, B=8, C=7, D=7

**Note:** The audit results (`pilot2_eval_results.csv`) still reflect the old key positions; if those are needed, the audit must be re-run on the re-keyed options.

### Working-tree cleanup

A rigorous cleanup was executed based on `agent_cleanup_inventory.md`:
- Deleted cache/build/temp/log artifacts, stale backups, and empty output folders.
- Archived legacy v3/v4.3.6/Groq scripts and notebooks to `.archive/legacy_code_2026-06-19/`.
- Archived old local run outputs to `.archive/legacy_outputs_2026-06-19/`.
- Archived old zip packages and Word docs.
- Relocated MCP memory JSON exports to `.archive/memory_exports_2026-06-19/`.

Remaining **REVIEW** items left for human decision:
- `API_keys_test/` (possible plaintext keys)
- `Busayou_Package/` (external reviewer package)
- `actual_data/` root duplicates vs. `actual_data/cleaned/`
- `model_cache/` (may be needed by sentence-transformer guard)
- `neurips_review/` (conference notes)
- `kaggle_analysis/` mixed active/stale contents

### Updated model pool guidance

- `anthropic/claude-3.5-haiku` is **permanently removed** from both pilots.
- `deepseek/deepseek-v3.2` is promoted to a starter auditor in both pilots.
- Pilot 2 v3 now uses a rotating roster of `google/gemini-2.5-pro`, `qwen/qwen3.5-397b-a17b`, and `anthropic/claude-sonnet-4` for generation.

### Files changed

- `openrouter_pilot_distractor_generation_test_nano_opus.py`
- `openrouter_pilot_distractor_generation_test_nano_opus.ipynb`
- `openrouter_pilot_s1_s2_evaluator_v3.py`
- `openrouter_pilot_s1_s2_evaluator.ipynb`
- `test_pilot2_local.py`
- `rekey_s1_s2_pilot_v1.py` (new)
- `agent_literature_shortcut_audit.md` (new)
- `agent_code_audit_report.md` (new)
- `agent_cleanup_inventory.md` (new)
- `memory.md` (this file)

### Concrete next steps

#### Before the next Kaggle smoke test
1. Upload the regenerated `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` to Kaggle and run N_PER_LANG=1.
2. Upload the regenerated `openrouter_pilot_s1_s2_evaluator.ipynb` to Kaggle and run N_PER_LANG=2-3.
3. Verify all quality gates:
   - Hard fallback < 5%
   - Partial + fallback < 15%
   - Active generators/auditors ≥ 3 each
   - Perfect consensus < 30%
   - High-consensus-wrong < 10%
   - Per-language consensus correctness ≥ 50%
   - 0 duplicate options
   - Balanced A-D keys
   - Cost < $5.00

#### Quality hardening (P1)
4. If perfect consensus remains high, add a post-generation filter that drops/regenerates items with `consensus_frac >= 0.75`.
5. Investigate Arabic proverbs `160`, `591`, `396` for gold-meaning alignment.
6. Continue Yoruba prompt hardening and corpus fallback constraints.
7. Add option-shuffling robustness and all-A/all-D baselines to the audit.

#### Submission readiness
8. Plan a stratified human plausibility/validity audit with IAA.
9. Document the full validation suite in the paper and supplementary materials.

---

*End of Current State Update - June 20, 2026*

---

## v59 phased-fix update — 2026-06-19

### What changed
- Implemented P0 blocklist expansion, correct-meaning leak filter, duplicate/near-duplicate repair, and randomized fallback sampler.
- Implemented P1 NLI paraphrase filter (`cross-encoder/nli-deberta-v3-xsmall`) with embedding guard (0.55) to suppress false positives.
- Implemented P2 distractor-quality metrics CSV/JSON, `nli_replaced`/`duplicate_options` tracking, with-proverb baseline audit, and improved human-annotation export.
- Fixed `repair_duplicate_options()` collision bug and fallback sampler determinism.
- Regenerated Kaggle notebook and pushed version 59.

### Validation
- `test_p0_filters.py` passes.
- `test_p1_nli.py` passes.
- `test_integration.py` passes (no duplicate-filled option sets).

### Next step
Run Pilot 1 TEST N=1 smoke test on Kaggle (`abrahamsunday123/mcq-pass-shortcut` v59) and check v59 gates.

---

## v60 fix update — 2026-06-20

### What changed
- Converted `has_correct_meaning_leak()` from a hard parse-fallback into `_sanitize_correct_meaning_leak()`, which replaces only the leaking distractor(s).
- Added `_is_correct_meaning_leak()` helper for per-distractor checks.
- Updated `ModelPool.record_failure()` to use a higher `soft_fail_threshold` (5) for weight-1 failures, so generators are not benched for occasional quality-filter misses.
- Regenerated notebook and pushed version 60 to `abrahamsunday123/mcq-pass-shortcut`.
- Background poller monitoring v60 run; outputs will land in `kaggle_run_logs/v60/`.

### Validation
- `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` still pass.

### Next step
Analyze v60 outputs when the run completes and decide whether to iterate again or scale to N=2/N=5.

---

## v61 fix update — 2026-06-20

### What changed
- Relaxed `LENGTH_CHECK_THRESHOLD` from 0.20 to 0.30 (±20% → ±30%).
- Widened `SEMANTIC_DISTANCE_BAND`: default max 0.82 → 0.85; Yoruba max 0.85 → 0.88.
- Removed the `adversarial-contrastive` prompt variant from `pilot1_prompt_variants.json` (it produced near-paraphrases that collapsed into length_fallback in v60).
- Updated all remaining prompt templates and shared constraints to reference ±30% length parity.
- Regenerated notebook and pushed version 61 to `abrahamsunday123/mcq-pass-shortcut`.
- Background poller monitoring v61 run; outputs will land in `kaggle_run_logs/v61/`.

### Validation
- Source syntax, `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

### Next step
Analyze v61 outputs when the run completes and decide whether to iterate again or scale.

---

## v61 run analysis — 2026-06-20

### Results (N=1, 3 proverbs, 36 MCQs)

| Metric | v61 | Target |
|---|---|---|
| Cost | $0.1864 / $5.00 | <$1 ✅ |
| Perfect consensus | 47.2% | <30% ❌ |
| High-consensus-wrong | 25.0% | <10% ❌ |
| Partial + fallback | 47.2% | <15% ❌ |
| Consensus accuracy | 61.1% | — |
| Yoruba correctness | 33.3% | ≥50% ❌ |
| Duplicate options | 0 | 0 ✅ |
| Correct-key balance | 9/9/9/9 | balanced ✅ |

**Per-language consensus correctness:** English 91.7%, Arabic 58.3%, Yoruba 33.3%.

### Key findings

1. **Sanitizers still rewrite ~47% of items.** Length relaxation and semantic widening helped slightly, but semantic/NLI/leak/length sanitizers continue to discard most model-generated distractors.
2. **Length_fallback label is misleading.** Many `length_fallback` items have acceptable length spreads but hit the ≥3-replacement threshold from semantic/NLI/leak sanitizers. The `adversarial-length-locked` and `adversarial-hard-negative` variants are the most brittle.
3. **English is too easy.** 91.7% consensus correctness drives perfect consensus up; distractors are not tempting enough.
4. **Yoruba remains broken.** Literal/awkward gold meanings, weak distractors, and culturally mismatched corpus fallbacks (some offensive) keep correctness at 33.3%.
5. **Fallback sampler can produce inappropriate content.** Some corpus-sampled Yoruba distractors contain vulgar or culturally jarring text.
6. **Cost is healthy.** $0.19 leaves headroom for extra LLM calls.

### v62 options under consideration

- **A.** Make length check more lenient or smarter (e.g., compare each distractor to the closest other option, or skip if all options are within ±40%).
- **B.** Weaken the leak sanitizer for English (raise threshold from 0.80 to 0.90) so legitimate hard negatives are not replaced.
- **C.** Tune semantic band per language (English max 0.88, Yoruba 0.90).
- **D.** Replace `adversarial-hard-negative` or `adversarial-length-locked` with a less brittle variant.
- **E.** Yoruba rescue: pre-process Yoruba gold meanings with a cheap LLM call to rewrite literal glosses into natural English before option generation.
- **F.** Fallback quality guard: filter/rewrite offensive or generic corpus fallbacks.

**Recommended v62 combination:** A + B + E + F.

### Next step
Decide which v62 interventions to implement, update source/notebook, push version 62, and run another N=1 smoke test on Kaggle.

---

## v62 fix update — 2026-06-21

### What changed
Recommended A+B+E+F intervention applied to `openrouter_pilot_distractor_generation_test_nano_opus.py`:

- **A — Smarter length parity:**
  - `LENGTH_CHECK_THRESHOLD` 0.30 → 0.35.
  - Added `LENGTH_RELAXED_THRESHOLD = 0.45`: accept the whole option set if all four are within ±45% of each other.
  - `passes_length_check()` accepts an optional `relaxed_threshold`.
  - Status logic labels `length_fallback` only when `length_replaced >= 2`.
- **B — Per-language leak threshold:**
  - `LEAK_THRESHOLD_BY_LANGUAGE`: English 0.90, default 0.80.
- **C — Supporting semantic-band tuning:**
  - `SEMANTIC_DISTANCE_BAND`: English max 0.88, default max 0.86, Yoruba max 0.90.
- **E — Yoruba gold-meaning curation:**
  - Added `curate_yoruba_meaning()` using `openai/gpt-4.1-nano` to rewrite literal/awkward Yoruba glosses into natural English, with per-proverb caching.
  - RAW outputs record `original_meaning` and `curated_meaning`.
- **F — Fallback quality guard:**
  - Added `_FALLBACK_OFFENSIVE_BLOCKLIST` and `_is_offensive_or_inappropriate()`.
  - `semantically_distinct_negative_sample()` rejects offensive/vulgar corpus fallbacks.
- **Prompt catalog:** updated `pilot1_prompt_variants.json` to ±35% (±45% relaxed all-within).
- **Notebook regenerated** and **pushed version 63** to `abrahamsunday123/mcq-pass-shortcut` (v62 contained the code changes; v63 corrected the markdown cell copy).

### Validation
- `python -m py_compile openrouter_pilot_distractor_generation_test_nano_opus.py` passes.
- `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

### Next step
Run the v62 N=1 smoke test on Kaggle and analyze whether partial+fallback, HCW, perfect consensus, and Yoruba correctness now meet the gates.

---

## v63 run analysis — 2026-06-21

### Results (N=1, 3 proverbs, 36 MCQs)

| Metric | v63 | v61 | Target |
|---|---|---|---|
| Cost | $0.1909 / $5.00 | $0.1864 | <$1 ✅ |
| Perfect consensus | 52.8% | 47.2% | <30% ❌ |
| High-consensus-wrong | 33.3% | 25.0% | <10% ❌ |
| Partial + fallback | 36.1% | 47.2% | <15% ❌ |
| Consensus accuracy | 55.6% | 61.1% | — |
| Yoruba correctness | 25.0% | 33.3% | ≥50% ❌ |
| Arabic correctness | 41.7% | 58.3% | ≥50% ❌ |
| English correctness | 100.0% | 91.7% | ≥50% ✅ |
| Duplicate options | 0 | 0 | ✅ |
| Correct-key balance | 9/9/9/9 | 9/9/9/9 | ✅ |

### Key findings

1. **Partial+fallback improved to 36.1%.** v62 length/leak relaxations worked; `length_fallback` only 8.3%, mean `fallback_count` 0.75.
2. **HCW and perfect consensus worsened.** HCW 33.3%, perfect consensus 52.8%. Distractors are now attractive enough for auditors to agree, but often on the wrong answer.
3. **English still too easy.** 100% consensus correctness; 10/12 perfect consensus.
4. **Arabic and Yoruba drive HCW.** Arabic 6/12 HCW, Yoruba 6/12 HCW. Generic English idioms leaked into Arabic distractors; Yoruba distractors cluster around gourd/farmer/bind.
5. **NLI barely fired.** Only 5 replacements; embedding guard likely suppresses legitimate paraphrase flags.
6. **Yoruba curation ran** (raw outputs confirm rewrite) but did not lift correctness.
7. **`google/gemma-4-31b-it` benched**; `anthropic/claude-sonnet-4` promoted.

### v64 options

- **A.** Curate all gold meanings (English, Arabic, Yoruba) into natural, non-idiomatic English.
- **B.** Expand generic-English idiom blocklist with v63 leakages (`People in glass houses...`, `The smarter you are...`, `Speech is silver...`, `The proof's in the pudding`, etc.).
- **C.** Lower NLI embedding guard for Arabic/Yoruba to ~0.45 to catch more paraphrase distractors.
- **D.** Improve Yoruba curation prompt to preserve key entities (`neckless gourd`, `farmer`, `tie/bind`).
- **E.** Post-generation difficulty rejection rule (cheap single-auditor probe) if consensus_frac == 1.0.
- **F.** Replace/de-prioritise brittle variant/generator pairs (`adversarial-length-locked`, `google/gemini-2.5-flash`).

**Recommended v64 combination:** A + B + C + D.

### Next step
Implement v64, push version 64, run N=1 smoke test.

---

## v64 fix update — 2026-06-21

### What changed
Recommended A+B+C+D follow-up to v63 applied to `openrouter_pilot_distractor_generation_test_nano_opus.py`:

- **A — Curate all gold meanings.** Renamed `curate_yoruba_meaning()` to `curate_gold_meaning()` and applied it to English, Arabic, and Yoruba. Uses `openai/gpt-4.1-nano` with language-specific instructions:
  - Yoruba: preserve neckless/collarless gourd, farmer, tying/binding.
  - Arabic: preserve specific moral/social situation; avoid generic English idioms.
- **B — Expanded generic-English idiom blocklist.** Added v63 leakages: `People in glass houses...`, `The proof is in the pudding`, `Speech is silver, silence is gold`, `Silence is golden`, `Mind your own business`, `Add fuel to the flames`, `Better suffer ill than do ill`, `Experience is the best teacher`, etc.
- **C — Language-specific NLI embedding guard.** Added `NLI_EMBEDDING_GUARD_BY_LANGUAGE`: Arabic/Yoruba 0.45, default 0.55.
- **D — Improved Yoruba curation prompt.** Preserves concrete gourd/farmer/bind imagery.
- **CSV metadata:** `pilot1_test_generated_mcqs.csv` records `original_meaning` and `curated_meaning`; `correct_meaning` is the curated version.
- **Notebook regenerated** and **pushed version 64** to `abrahamsunday123/mcq-pass-shortcut`.

### Validation
- `python -m py_compile openrouter_pilot_distractor_generation_test_nano_opus.py` passes.
- `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` all pass.

### Next step
Run the v64 N=1 smoke test on Kaggle and analyze whether HCW, perfect consensus, and per-language correctness meet the gates.


---

## Memory digest — 2026-06-21 (OpenRouter Pilot 1 TEST v58–v66 + v67a pivot)

### Conversation summary

The session began with a request to digest the full chat since the project memory had not been updated. Two legacy pilot folders were forensically analyzed: `generation_pilot_v1/` (Pilot 1 TEST N=1, 90 MCQs, $0.52) and `S1_S2_pilot_v1/` (Pilot 2 v4 N=10, 60 MCQs, $0.78). Both showed infrastructure PASS but quality FAIL. Pilot 1 had 55.6% perfect consensus, 38.9% HCW, and Yoruba correctness of only 16.7%; Pilot 2 suffered from position bias (S1 keys only A/C, S2 keys only B/D) and single-generator use. A batch of P0 fixes was implemented for both OpenRouter notebooks: replacing the EOL `anthropic/claude-3.5-haiku` auditor with `deepseek/deepseek-v3.2`, fixing Pilot 2 position bias and generator rotation, re-keying existing Pilot 2 CSVs, hardening meta-text rejection and the Yoruba idiom blocklist, and creating a proof-of-work notebook.

The session then shifted to iterative Kaggle runs of the Pilot 1 TEST distractor-generation notebook (`abrahamsunday123/mcq-pass-shortcut`). Versions v58 through v66 were executed, analyzed, and tuned. Early versions reduced duplicates and improved Yoruba correctness, but partial+fallback and HCW rates remained above gates. v65 achieved the best HCW so far (11.1%) by applying option-level idiom blocking, excluding duplicate repair from fallback counts, and not counting correct-option length outliers as fallbacks. v66 regressed: prompt hardening and length relaxation increased NLI replacements from 8 to 16, pushing partial+fallback to 50.0% and HCW back to 22.2%. This led to a strategic pivot away from tail-chasing on N=1 prompt tuning toward a paper-first freeze-and-scale plan, which the user approved.

### Key decisions made

1. **Approved paper-first strategy.** Freeze v67 config, scale to N=5 then N=15, add human validation, and frame the paper around methodology + failure taxonomy rather than chasing every N=1 gate.
2. **Selected v67a bundle.** Revert v66 prompt/length changes to the v65 baseline (`LENGTH_CHECK_THRESHOLD=0.35`, `LENGTH_RELAXED_THRESHOLD=0.45`, prompt variants at ±35%/±45%), keep v65 roster + dup bookkeeping + correct-option length fix, and replace the corpus fallback sampler with an LLM-based fallback distractor generator.
3. **Chosen fallback generator model.** `FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"`.
4. **Kept reordered generator pool.** `qwen/qwen3.7-max`, `google/gemini-2.5-flash`, `google/gemma-4-31b-it` as starters; `google/gemini-2.5-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `anthropic/claude-sonnet-4` as substitutes (emergency-only for the last).
5. **Migrated legacy outputs.** Re-keyed `S1_S2_pilot_v1/mcqs_s1.csv` and `mcqs_s2.csv` to balanced A-D keys so the N=10 Pilot 2 data is not wasted.

### Version run table (Pilot 1 TEST, N=1, 3 proverbs, ~36 MCQs unless noted)

| Version | Cost | Perfect consensus | HCW | Partial+fallback | English | Arabic | Yoruba | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| v58 | $0.2237 | 48.9% | 22.2% | 28.9% | — | — | 40.0% | 2 duplicates |
| v59 | $0.1864 | 37.8% | 28.9% | 42.2% | — | — | — | EOL auditor removed; 0 duplicates |
| v60 | $0.2300 | 44.4% | 28.9% | 48.9% | — | — | 26.7% | Starters stayed active; adversarial-contrastive 0/9 generated |
| v61 | $0.1864 | 47.2% | 25.0% | 47.2% | 91.7% | 58.3% | 33.3% | Removed adversarial-contrastive; relaxed length/semantic |
| v63 (v62 code) | $0.1909 | 52.8% | 33.3% | 36.1% | 100.0% | 41.7% | 25.0% | Length/leak relaxations helped partial but hurt HCW |
| v64 | $0.1700 | 47.2% | 19.4% | 41.7% | 91.7% | 58.3% | 50.0% | Curated all gold meanings; per-language NLI guard; blocklist flagged Arabic correct option |
| v65 | $0.1879 | 41.7% | 11.1% | 36.1% | 100.0% | 50.0% | 41.7% | Best HCW; option-level blocklist; correct-option length outliers not counted as fallback |
| v66 | $0.1754 | 55.6% | 22.2% | 50.0% | 100.0% | 58.3% | 50.0% | Prompt hardening + length relaxation backfired; NLI replacements doubled (8→16) |

*Targets: perfect consensus <30%, HCW <10% (step <15%), partial+fallback <15%, per-language correctness ≥50%, cost <$1.00 for N=1.*

### Current blockers / next steps

1. **Wire v67a fallback generator.** Ensure `_set_llm_fallback_context()` / `_clear_llm_fallback_context()` are called inside `generate_options()` and that `semantically_distinct_negative_sample()` uses the LLM fallback for `n==1` replacements.
2. **Regenerate notebook.** Run `convert_test_nano_opus_to_notebook.py` to produce the updated Kaggle notebook.
3. **Push v67.** Upload the notebook to `abrahamsunday123/mcq-pass-shortcut`.
4. **Run Kaggle N=1 smoke test.** Analyze perfect consensus, HCW, partial+fallback, and per-language correctness.
5. **If gates pass, scale to N=5 then N=15.** Do not jump to N=15 without raising the cost cap.
6. **Add human validation** on a 100-item subset.
7. **Draft paper** around the adversarial distractor methodology and the reproducible failure taxonomy.

### MCP entities/relations to create or update

**Entities:**
- `ProverbGap MCQ`
- `OpenRouter Pilot 1 TEST`
- `Pilot 1 TEST v67a config`
- `LLM fallback distractor generator`
- `openai/gpt-4.1-nano`
- `deepseek/deepseek-v3.2`
- `abrahamsunday123/mcq-pass-shortcut`
- `abrahamsunday123/openrouter-key-mcq`
- `S1_S2_pilot_v1`
- `Yoruba English-idiom blocklist`
- `Proof of work P0 fixes 2026-06-20`

**Relations:**
- `OpenRouter Pilot 1 TEST` — `has_version` → `Pilot 1 TEST v67a config`
- `Pilot 1 TEST v67a config` — `replaces` → `v66 config`
- `Pilot 1 TEST v67a config` — `reverts_to` → `v65 config`
- `LLM fallback distractor generator` — `uses_model` → `openai/gpt-4.1-nano`
- `OpenRouter Pilot 1 TEST` — `audited_by` → `deepseek/deepseek-v3.2`
- `OpenRouter Pilot 1 TEST` — `hosted_at` → `abrahamsunday123/mcq-pass-shortcut`
- `OpenRouter Pilot 1 TEST` — `blocked_by` → `corpus fallback sampler`
- `LLM fallback distractor generator` — `mitigates` → `corpus fallback sampler`
- `S1_S2_pilot_v1` — `has_fix` → `Proof of work P0 fixes 2026-06-20`
- `Yoruba English-idiom blocklist` — `part_of` → `OpenRouter Pilot 1 TEST`

---

## v67 frozen config + scaling decision — 2026-06-21

### Decision
Stopped the N=1 prompt-tuning loop. Approved a paper-first freeze-and-scale plan:

1. **Freeze v67 config:** revert v66 prompt/length changes, keep only proven working parts from v65 and v66 local.
2. **Scale to N=5 first, then N=15:** 15 proverbs (~$0.90) then 45 proverbs (~$2.70), both under the $5 cap.
3. **Add human validation:** 60 MCQs (20 per language) from the N=15 run, 2–3 annotators, IAA reported.
4. **Write the paper** around methodology + reproducible failure taxonomy.
5. **Optional ablation:** LLM-based fallback distractor generator can be compared on a subset, but does not block the paper.

### Frozen v67 config

```python
N_PER_LANG = 5                       # scale to 15 after N=5 check
USE_LLM_FALLBACK = False             # disabled by default; optional ablation only
LENGTH_CHECK_THRESHOLD = 0.35
LENGTH_RELAXED_THRESHOLD = 0.45
NLI_EMBEDDING_GUARD_BY_LANGUAGE = {
    "default": 0.55,
    "english": 0.58,
    "arabic": 0.45,
    "yoruba": 0.45,
}
USE_GOLD_MEANING_CURATION = True
GOLD_CURATION_MODEL = "openai/gpt-4.1-nano"
```

**Kept from v65:**
- Option-level idiom blocklist (`_sanitize_blocked_idioms`) that skips the correct option.
- Correct-option length outlier counted separately, not toward fallback/partial status.
- Per-language NLI embedding guard.
- Gold-meaning curation for English, Arabic, Yoruba.

**Kept from v66 local:**
- `dup_replaced` excluded from `fallback_count` / partial status.
- Reordered stable generator roster: starters `qwen/qwen3.7-max`, `google/gemma-4-31b-it`, `google/gemini-2.5-flash`; substitutes `google/gemini-2.5-pro`, `openai/gpt-4.1-mini`, `openai/gpt-4.1-nano`, `anthropic/claude-sonnet-4` (emergency-only).

**Reverted from v66:**
- Length parity back to ±35% / ±45% (was ±45% / ±55%).
- Prompt variants back to v65 shared constraints (removed generic-reversal bans).

### Source changes

- Added `USE_LLM_FALLBACK = False` flag and gated the LLM fallback call in `semantically_distinct_negative_sample()`.
- Changed `N_PER_LANG` from 1 to 5.
- Updated `AGENTS.md` with the paper-first scaling strategy.
- Local tests `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` pass.

### Next steps

1. Regenerate Kaggle notebook from frozen source.
2. Push version 67 to `abrahamsunday123/mcq-pass-shortcut`.
3. Run Pilot 1 TEST N=5 on Kaggle.
4. Analyze N=5 quality/cost; if stable, run N=15.
5. Sample 60 MCQs for human validation.
6. Draft paper using `docs/ProverbGap_Reframed_Title_Abstract.md` framing.

---

## Kaggle kernel run trigger mechanism — 2026-06-21

### Finding
The Kaggle CLI (`python -m kaggle kernels push`) uploads a new notebook version but does **not** automatically execute it. The web UI "Run" button corresponds to the Kaggle SDK `create_kernel_session` API call, which is exposed through `kagglesdk` but not through the CLI.

### How to trigger a run programmatically

```python
from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import ApiCreateKernelSessionRequest

client = KaggleClient()
req = ApiCreateKernelSessionRequest()
req.slug = "abrahamsunday123/mcq-pass-shortcut"
req.language = "python"
req.kernel_type = "notebook"
req.enable_internet = True
resp = client.kernels.kernels_api_client.create_kernel_session(req)
print(resp)
# {"name": "operations/create-kernel-session/<id>", "metadata": {"kernelSessionId": <id>}, "done": false}
```

Required fields for `ApiCreateKernelSessionRequest`:
- `slug`: full kernel slug `{username}/{kernel-slug}`
- `language`: `"python"`, `"r"`, or `"rmarkdown"`
- `kernel_type`: `"notebook"` or `"script"`
- `enable_internet`: bool

Optional fields:
- `docker_image`: Kaggle-provided image SHA (can be omitted for default)
- `machine_shape`: `"NvidiaTeslaT4"`, `"NvidiaTeslaP100"`, `"Tpu1VmV38"`

### Polling for completion

The `ApiGetKernelSessionStatusRequest` uses `user_name`, `kernel_slug`, and `version_label` rather than `kernel_session_id`. The easiest reliable poll is the existing CLI:

```bash
python -m kaggle kernels status "abrahamsunday123/mcq-pass-shortcut"
```

Or poll via SDK using the latest version label obtained from `list_kernels` / `get_kernel`.

### Downloading outputs

```bash
python -m kaggle kernels output "abrahamsunday123/mcq-pass-shortcut" -p kaggle_run_logs/vNN/
```

### Applied
Used this mechanism to trigger v67 N=5 run on 2026-06-21 after pushing via CLI.

### Correction: the actual "Run all" API call

The web UI **Run** button corresponds to `ApiSaveKernelRequest` with `kernel_execution_type = KernelExecutionType.SAVE_AND_RUN_ALL`, not `create_kernel_session`. The latter creates an interactive session only.

`create_kernel_session` creates an interactive editing session; it does **not** execute all cells.

The correct pattern to push **and** run is:

```python
from kagglesdk import KaggleClient
from kagglesdk.kernels.types.kernels_api_service import ApiSaveKernelRequest, KernelExecutionType
import json

client = KaggleClient()
req = ApiSaveKernelRequest()
req.slug = "abrahamsunday123/mcq-pass-shortcut"
req.text = open("openrouter_pilot_distractor_generation_test_nano_opus.ipynb").read()
req.language = "python"
req.kernel_type = "notebook"
req.is_private = True
req.enable_internet = True
req.dataset_data_sources = ["abrahamsunday123/full-data-complete", "abrahamsunday123/openrouter-key-mcq"]
req.kernel_execution_type = KernelExecutionType.SAVE_AND_RUN_ALL
resp = client.kernels.kernels_api_client.save_kernel(req)
```

The standard CLI `kaggle kernels push` does **not** set `kernel_execution_type`, so it only saves a new version.


---

# PROJECT STATE SNAPSHOT — 2026-06-22 00:45 UTC

This section is a self-contained handover snapshot. A new chat should read this, `AGENTS.md`, and the MCP entities `ProverbGap MCQ`, `Pilot 1 TEST v67a config`, `Paper-first strategy 2026-06-21`, and `Kaggle kernel run trigger` to become fully operational.

## 1. What this project is

**ProverbGap MCQ** generates shortcut-resistant multiple-choice distractors for proverb understanding across English, Arabic, and Yoruba. It uses OpenRouter models with a dynamic generator pool, a disjoint blind audit committee, semantic/NLI filters, and length/fluency guards. Outputs are evaluated via a blind options-only shortcut audit and published-ready CSV/JSON/PNG artifacts.

**Project path:** `C:/Users/USER/Downloads/THe proverbeval container/MCQ`

## 2. Current strategic mode: freeze-and-scale

On 2026-06-21 we stopped the N=1 prompt-tuning loop. The v67 config is frozen and we are scaling:

1. **v68 analysis complete** (N=5, 15 proverbs, $0.85) — all shortcut-resistance gates failed except duplicates and key balance. HCW 27.8%, partial+fallback 43.9%, perfect consensus 41.7%.
2. **v69 ablation** (N=5) — enable `USE_LLM_FALLBACK = True` to test whether LLM-based fallback distractors reduce HCW and partial+fallback. Do not scale to N=15 before this ablation.
3. **If v69 passes gates** (HCW <15%, partial+fallback <30%, cost <$1.50), freeze and run **v70 at N=15**.
4. **If v69 fails** or improves only marginally, treat v68/v69 as the production dataset and move directly to human validation + paper drafting, framing the corpus-fallback bottleneck as a known limitation.
5. **Human validation** on 60 MCQs (20 per language) from the final N=15 or best N=5 run.
6. **Paper draft** around methodology + reproducible failure taxonomy (generic shortcut, near-paraphrase trap, confident-wrong fallback, cultural mismatch, length/register imbalance).

The paper framing is in `docs/ProverbGap_Reframed_Title_Abstract.md`. Target venue: EACL 2027 / ARR August 3, 2026.

## 3. Frozen v67 configuration

```python
N_PER_LANG = 5
COST_CAP_USD = 5.00
USE_LLM_FALLBACK = False             # optional ablation only
FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"

LENGTH_CHECK_THRESHOLD = 0.35
LENGTH_RELAXED_THRESHOLD = 0.45

SEMANTIC_DISTANCE_BAND = {
    "default": {"min": 0.12, "max": 0.86},
    "english": {"min": 0.12, "max": 0.88},
    "yoruba":  {"min": 0.10, "max": 0.90},
}

NLI_EMBEDDING_GUARD_BY_LANGUAGE = {
    "default": 0.55,
    "english": 0.58,
    "arabic": 0.45,
    "yoruba": 0.45,
}

LEAK_THRESHOLD_BY_LANGUAGE = {
    "default": 0.80,
    "english": 0.90,
}

USE_GOLD_MEANING_CURATION = True
GOLD_CURATION_MODEL = "openai/gpt-4.1-nano"

GENERATOR_POOL = [
    # Starters
    "qwen/qwen3.7-max",
    "google/gemma-4-31b-it",
    "google/gemini-2.5-flash",
    # Primary substitutes
    "google/gemini-2.5-pro",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1-nano",
    # Emergency substitutes
    "anthropic/claude-sonnet-4",
    "qwen/qwen3.5-397b-a17b",
    "meta-llama/llama-4-maverick",
    "deepseek/deepseek-v4-pro",
]

AUDIT_POOL = [
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct",
    "google/gemma-3-27b-it",
    "deepseek/deepseek-v3.2",
    "amazon/nova-lite-v1",
]
```

**Kept from v65:** option-level idiom blocklist, correct-option length outlier not counted as fallback, per-language NLI embedding guard, gold-meaning curation for all languages.

**Kept from v66 local:** `dup_replaced` excluded from fallback/partial status, reordered stable generator roster.

**Reverted from v66:** length parity back to ±35%/±45%; prompt variants back to v65 shared constraints (removed generic-reversal bans).

## 4. Run history (Pilot 1 TEST, N=1 unless noted)

| Version | Date | Cost | Perfect | HCW | Partial+FB | English | Arabic | Yoruba | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| v58 | 2026-06-20 | $0.2237 | 48.9% | 22.2% | 28.9% | 72.7% | 63.6% | 40.0% | 2 duplicates |
| v59 | 2026-06-20 | $0.1864 | 37.8% | 28.9% | 42.2% | — | — | — | EOL auditor removed |
| v60 | 2026-06-20 | $0.2300 | 44.4% | 28.9% | 48.9% | — | — | 26.7% | Starters stayed active |
| v61 | 2026-06-20 | $0.1864 | 47.2% | 25.0% | 47.2% | 91.7% | 58.3% | 33.3% | Removed adversarial-contrastive |
| v63 | 2026-06-21 | $0.1909 | 52.8% | 33.3% | 36.1% | 100.0% | 41.7% | 25.0% | v62 code; length/leak relaxations |
| v64 | 2026-06-21 | $0.1700 | 47.2% | 19.4% | 41.7% | 91.7% | 58.3% | 50.0% | Curated all gold meanings |
| v65 | 2026-06-21 | $0.1879 | 41.7% | 11.1% | 36.1% | 100.0% | 50.0% | 41.7% | Best HCW; option-level blocklist |
| v66 | 2026-06-21 | $0.1754 | 55.6% | 22.2% | 50.0% | 100.0% | 58.3% | 50.0% | Prompt/length hardening backfired |
| v67 | 2026-06-21 | $0.1718 | — | — | — | — | — | — | Pushed but ran stale N=1 output |
| **v68** | **2026-06-22** | **$0.8539** | **41.7%** | **27.8%** | **43.9%** | **65.0%** | **53.3%** | **51.7%** | **Frozen v67 config, N=5; all gates failed except duplicates/key balance** |

Targets: perfect <30%, HCW <10% (step <15%), partial+fallback <15%, per-language correctness ≥50%, 0 duplicates, balanced A-D, cost <$5.

## 5. v66 regression diagnosis and v68 N=5 confirmation

v66 moved gates in the wrong direction:
- Prompt hardening against generic reversals + length relaxation to ±45%/±55% backfired.
- NLI replacements doubled from 8 (v65) to 16.
- Partial+fallback rose from 36.1% to 50.0%; HCW rose from 11.1% to 22.2%.
- English remained 100% consensus-correct.
- Root cause: closer-to-correct attempts were caught by NLI and replaced by low-quality corpus fallbacks.

Decision: revert v66 prompt/length changes, keep v65 working parts, scale instead of tuning.

**v68 N=5 scaled test (frozen v67 config) confirmed the corpus-fallback bottleneck:**
- 43.9% partial+fallback; mean 0.99 corpus replacements per MCQ.
- HCW jumped to 27.8% (vs 11.1% in v65 N=1), driven by corpus fallbacks that attract auditor consensus.
- NLI replacements (mean 0.36/MCQ) and leak replacements (mean 0.35/MCQ) dominate; length replacements are minor (mean 0.15/MCQ).
- Arabic and Yoruba are disproportionately affected; English is largely fine.
- `adversarial-hard-negative` is the most damaged variant (only 26.7% fully generated, 42.2% length_fallback).
- Conclusion: scaling further without fixing the fallback sampler is not justified.

## 6. Key files and automation

| File | Purpose |
|---|---|
| `openrouter_pilot_distractor_generation_test_nano_opus.py` | Main source |
| `openrouter_pilot_distractor_generation_test_nano_opus.ipynb` | Kaggle notebook (regenerated from source) |
| `pilot1_prompt_variants.json` | 4 adversarial prompt variants |
| `convert_test_nano_opus_to_notebook.py` | Source → notebook converter |
| `trigger_kaggle_run.py` | Push **and** run via `ApiSaveKernelRequest` + `SAVE_AND_RUN_ALL` |
| `kaggle_upload_pilot1_test/kernel-metadata.json` | Kaggle metadata |
| `test_p0_filters.py`, `test_p1_nli.py`, `test_integration.py` | Local validation |
| `analyze_run.py`, `analyze_v61.py` … `analyze_v66.py` | Per-run analysis |
| `AGENTS.md` | Agent handover |
| `memory.md` | This long-form memory |
| `docs/ProverbGap_Reframed_Title_Abstract.md` | Paper framing |
| `docs/Elite_Research_Execution_Plan.md` | Research plan |

### Kaggle workflow

1. Regenerate notebook: `python convert_test_nano_opus_to_notebook.py`
2. Push + run: `python trigger_kaggle_run.py`
3. Poll status: `python -m kaggle kernels status "abrahamsunday123/mcq-pass-shortcut"`
4. Download outputs: `python -m kaggle kernels output "abrahamsunday123/mcq-pass-shortcut" -p kaggle_run_logs/vNN/ --force`

**Important:** `kaggle kernels push` only saves a version. The Run button maps to `ApiSaveKernelRequest` with `kernel_execution_type = SAVE_AND_RUN_ALL`.

## 7. Open blockers and next steps

### P1 blockers (scaling blocked until improved)
- **Corpus fallback sampler** is the confirmed bottleneck: 43.9% partial+fallback and 27.8% HCW at N=5.
- **HCW** more than doubled from v65 N=1 (11.1%) to v68 N=5 (27.8%).
- **English remains too easy**: 65.0% consensus accuracy, 45.0% perfect consensus.
- **Arabic/Yoruba fragile**: consensus accuracy 53.3% / 51.7%, HCW 31.7% / 33.3%.
- No human validation yet.

### Immediate next steps
1. ✅ v68 N=5 completed and analyzed (see `kaggle_run_logs/v68/v68_detailed_analysis_report.md`).
2. **Do not scale to N=15 yet.**
3. ✅ **v69 ablation implemented and triggered:** `USE_LLM_FALLBACK = True`, `N_PER_LANG = 5`, notebook regenerated, pushed as Kaggle version 69, run in progress.
4. ⏳ Poll Kaggle status and download v69 outputs to `kaggle_run_logs/v69/`.
5. Analyze v69 against gates: HCW <15%, partial+fallback <30%, cost <$1.50.
6. If v69 passes, freeze config and run **v70 N=15**.
7. If v69 fails or is marginal, use v68/v69 as production data and move to human validation + paper draft.
8. Draft paper failure taxonomy around: generic shortcut, near-paraphrase trap, confident-wrong fallback, cultural mismatch, length/register imbalance.

## 9. v69 ablation implementation details

Enabled the LLM-based fallback distractor generator (`openai/gpt-4.1-nano`) for the v69 Kaggle run:

- `USE_LLM_FALLBACK = True` (only config change from v68).
- Wired `_set_llm_fallback_context()` / `_clear_llm_fallback_context()` inside `generate_options()` so the fallback is proverb-aware and variant-aware.
- Fixed broken NLI check in fallback: symmetric forward/backward entailment, matching the main pipeline.
- Added correct-meaning leak guard and meta-text guard to the fallback; idiom/offensive guards were already present.
- `openrouter_chat()` now accepts an optional `temperature` parameter; fallback uses `temperature=0.0`.
- Recursion safety: missing-context guard and all-attempts-failed path both call corpus sampler with `use_llm=False`.
- Added `_LLM_FALLBACK_USED` / `_LLM_FALLBACK_REJECTED` counters and version metadata (`version`, `use_llm_fallback`, `fallback_generator_model`) to `pilot1_test_summary.json`.
- Local validation: `python -m py_compile` and `test_integration.py` pass.
- Kaggle version 69 pushed and run triggered via `trigger_kaggle_run.py`.

## 8. New-chat quick-start checklist

- [ ] Read `AGENTS.md` (current config + scaling plan).
- [ ] Read this `memory.md` section.
- [ ] Query MCP entities: `ProverbGap MCQ`, `Pilot 1 TEST v67a config`, `Paper-first strategy 2026-06-21`, `Kaggle kernel run trigger`.
- [ ] Check `kaggle_run_logs/v68/` for latest outputs.
- [ ] Run local tests: `python test_p0_filters.py`, `python test_p1_nli.py`, `python test_integration.py`.
- [ ] Check Kaggle status before any push/run.


---

## Update — 2026-06-22: OpenRouter budget exhausted; pivot to paper-first

- v68 N=5 (corpus fallback) completed: 180 MCQs, $0.8539, full audit.
- v69 LLM-fallback ablation and v70 N=15 scaling were blocked by OpenRouter `403 Budget limit exceeded`.
- v70 produced 83 MCQs (36 generated, 19 length-fallback, 18 partial, 10 hard-fallback) before crashing with `RuntimeError: No active generators remaining`.
- Decision: stop Kaggle/OpenRouter runs until budget is renewed.
- Pivot to paper-first using v68 as the production dataset.
- Created `paper_first_analysis_2026-06-22_10-42-02.ipynb` (no-API notebook producing tables/figures/60-item validation sample) and `next_steps_2026-06-22_10-42-02.md`.
- Next immediate actions: recruit native-speaker annotators for 60-item validation; draft paper sections; renew API budget.
- Created `ProverbGap_State_of_Work_2026-06-22.docx`, a 2-page DOCX with v68 figures and cost table, to request increased OpenRouter quota from the Fatima Fellowship.
- Packaged the DOCX, figures, and an Overleaf-ready LaTeX stub into `fatima_submission_package_2026-06-22/` (with `.zip` and `.tar.gz` archives) for easy submission and future LaTeX/Overleaf conversion.
- Final verification pass fixed v70 sample wording, removed the imprecise "v69-level scale" phrase from the quota request, cleaned LaTeX dollar escaping, and regenerated both archives.

---

## Update — 2026-07-07: Human-validation annotation subsystem built + live LLM-annotator runs

### Context (recovered from a crashed chat)

Two prior sessions were recovered via `kilo_local_recall`:
- `ses_0c8a060d1ffeoWKQZNq1xXZm17` (12:19, Jul 6): integrated skills/MCP; ran the "AI Agent Project Setup & Context Handover" prompt; established the **$19/mo budget = $9 OpenRouter + $10 Modal** hybrid; confirmed v68 = production dataset; decided the human-validation sample = **60 items (20/lang)** (smallest defensible size for reviewers).
- `ses_0c86f0b3dffe0XusVZFR4q7V0k` (14:14, Jul 6): built the annotation core framework (`protocol.md`, `rubric.py`, `blinded_export.py`, `sample_size_analysis.py`, `tests/`).

The chat crashed while trying to verify/fix a suspected `SyntaxError` in `openrouter_annotators.py`, before delivering a status report. The full intent: a **reviewer-proof, code-logged human-validation layer** — blinded 60-item packet + rubric + sample-size justification + dual LLM "annotator" proxies (OpenRouter closed models, Modal open models) with redacted logs, then compute IAA.

### Annotation subsystem created (all 2026-07-06, within 24h)

| File | Purpose |
|---|---|
| `annotation/__init__.py` | package version string |
| `annotation/protocol.md` | full annotation protocol (purpose, annotator reqs, task, rubric, blinding, quality controls, IAA plan) |
| `annotation/rubric.py` | `ANNOTATION_FIELDS`, `VALID_ANSWERS`, `VALID_CONFIDENCE`, `VALID_PLAUSIBILITY`, `SHORTCUT_FLAGS`, `validate_annotation_row()`, `create_annotation_schema()` |
| `annotation/blinded_export.py` | `load_production_sample()`, `create_blinded_annotation_pack()` (drops correct_label/consensus/vote columns), `unblind_results()` |
| `annotation/sample_size_analysis.py` | `fleiss_kappa_sample_size()`, `kappa_ci_width()`, `recommend_sample_size()` → recommends 90 items (30/lang), but project uses the approved **60** |
| `annotation/modal_annotators.py` | Modal (open-source) LLM-annotator harness (vLLM on A10G) |
| `annotation/openrouter_annotators.py` | OpenRouter (closed) LLM-annotator harness |
| `annotation/compute_iaa.py` | per-model accuracy, per-language accuracy, pairwise Cohen's κ, Fleiss' κ vs v68 `consensus_label`/`correct_label` (stdlib + pandas only) |
| `modal_requirements.txt` | torch/transformers/vllm/modal/pandas/pydantic |
| `annotation/tests/` | pytest for rubric + blinded_export (all pass) |

### Environment setup
- Copied `C:\Users\USER\Downloads\Revamp\.env` → `MCQ/.env` (contains `OPENROUTER_API_KEY`, `MODAL_TOKEN`, `MODAL_API_KEY`, `HF_TOKEN`). Already git-ignored via `.gitignore:2:*.env`. **No secrets in repo.**
- `modal` SDK 1.5.1 authenticated via `~/.modal.toml`.

### Data path used (definitive)
`paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv`
- The **v68 production 60-item stratified sample** (25 generated, 19 partial, 16 length_fallback; 20 per language).
- Columns include `validation_id`, `language`, `proverb`, `option_A…D`, `generation_status`, `correct_label`, `consensus_label`, `consensus_frac`. The LLM annotators read only `validation_id/language/proverb/options`; `correct_label`/`consensus_label` are **never** sent to the models (no leakage).

### Execution log (2026-07-07)

**A — Pipeline shape (no spend):** PASS. 60 rows, required cols present, prompt built with no `correct_label` leakage, rubric validation works.

**B — OpenRouter live probe (REAL, 5 items):** PASS — budget is **NOT** exhausted.
- Ran `openai/gpt-4o` + `google/gemini-2.5-flash`. `anthropic/claude-haiku-3` was auto-filtered by the live catalog (`get_openrouter_annotator_models()`) as **currently unavailable on OpenRouter**.
- Cost: **$0.0015** for 5 items × 2 models.
- `gemini-2.5-flash`: answered all 5 (Arabic_1→C, Arabic_2→A, Arabic_3→A, Arabic_4→A, Arabic_5→A).
- `gpt-4o`: **refused 3/5** ("I'm sorry, but I can't select the correct meaning") → `finish_reason=parse_failed`. Answered only Arabic_3→A, Arabic_4→C.
- Output: `annotation/outputs/openrouter_annotation_results_openrouter_annotator_20260707_154531.csv` + redacted `openrouter_annotator_log.jsonl`.

**C — Modal live (open-source), full 60-item sample:** IN PROGRESS (background pid 19644, started ~16:1x).
- Models: `Qwen/Qwen2.5-7B-Instruct` + `meta-llama/Llama-3.2-3B-Instruct` (fit A10G; `DeepSeek-V2.5` omitted — ~236GB, too large for A10G).
- `MODAL_TOKEN` exported into the run process from `.env` (not printed).
- Cold-start model download makes this slow (10–20 min); output CSV written only at completion.

**D — IAA script:** BUILT + VALIDATED (`python -m py_compile` OK; ran on the 5-item probe data).
- Probe-only numbers (tiny n artifact, gpt-4o mostly refused): Fleiss' κ = -0.96; gemini acc_vs_consensus = 0.6, acc_vs_correct = 0.4; gpt-4o ans=2/5, ref=3/5, acc=0.0; pairwise Cohen's κ(gemini,gpt-4o)=0.0.
- Final 4-model IAA (OpenRouter 2 + Modal 2) will be computed once the Modal run completes → `annotation/outputs/iaa_report_<ts>.json` + `iaa_summary_<ts>.csv`.

### Bugs fixed during execution (these were the crashed chat's unfinished defects)
1. `openrouter_annotators.py` — **dangling `finally:`** outside the `for`/`try` → `SyntaxError`. Repaired the `except/finally` structure inside the retry loop.
2. `modal_annotators.py` — `run_modal_annotation` called `annotate_item_modal(..., gpu=...)` but the param is `gpu_type=` → `TypeError`. Fixed.
3. `modal_annotators.py` — `@app.function` was on a **nested** function (Modal requires global scope) → "function must be in global scope" / "not hydrated". Restructured `app` + `run_inference` to **module level**, wrapped the loop in `with _MODAL_APP.run():` so the container stays warm across all items.
4. `modal_annotators.py` — was passing the **OpenRouter key** into Modal's env (`modal.environment(OPENROUTER_API_KEY=modal_token)`); replaced with proper `modal.Secret`. Then dropped the HF secret because the named secret `huggingface` was **not found in Modal workspace `godwinsunday11223`**; the chosen Qwen/Llama models are public on HF and don't require it.
5. `.gitignore` — added `annotation/outputs/*.jsonl` and `annotation/outputs/*mock*` (secrets already covered by `*.env`).

### Reviewer-safety guarantees (code trail, no hallucination)
- **No secrets in repo**: `.env` git-ignored; logs are redacted (`_redact` masks key-like lines; prompts/responses hashed in `*.jsonl`).
- **Deterministic, traceable data**: annotators consume the v68-derived 60-item sample; `validation_id` links back to master data via `unblind_results()`.
- **Reproducible**: every run writes a timestamped result CSV + redacted JSONL; `ANNOTATION_RUN_ID` tagged per row.
- **Cost-capped + logged**: OpenRouter harness enforces `cost_cap`; Modal estimates cost per call; full ledger will be in the IAA report.
- **Honest framing**: the LLM harnesses are **answer-only proxies** (single-letter selection), explicitly distinct from the full human rubric (plausibility 1–5, confidence 1–3, shortcut flags) delivered via `blinded_export.py` + `protocol.md`. The LLM proxies are evidence of cross-model agreement, not a substitute for native-speaker validation.
- **Known limitation to disclose**: 60 (not 90) items; gpt-4o refusal rate; Modal `huggingface` secret not configured (public models only). All will be stated in the paper's Limitations.

### Current status (2026-07-07 17:24)
| Step | Status | Evidence |
|---|---|---|
| A pipeline verify | DONE | no-spend check passed |
| B OpenRouter live probe | DONE | 5 items, $0.0015, 2 models, refusals logged |
| C Modal live 60-item | RUNNING (bg pid 19644) | Qwen-7B + Llama-3B on A10G |
| D compute_iaa | SCRIPT DONE, final run pending Modal | validated on probe; final 4-model IAA after C |

*Next: when the Modal background run completes, run `python annotation/compute_iaa.py` to emit the final `iaa_report_*.json` / `iaa_summary_*.csv`, then fold the 4-model agreement into the paper's human-validation section.*

---

## Update — 2026-07-07 (evening): empty-options bug found & fixed, valid OpenRouter IAA, Modal infra stall

This session picked up after the 17:24 snapshot above. The earlier "Modal live 60-item RUNNING" (bg pid 19644) and the IAA numbers it implied were **invalid** — see the empty-options bug below. Everything below supersedes the pre-fix IAA numbers.

### Environment facts (re-confirmed)
- `OPENROUTER_API_KEY` present in `.env` (len 73) → OpenRouter usable.
- `MODAL_TOKEN` present in `.env` (len 25); `modal` SDK 1.5.1 authenticated via `~/.modal.toml` → Modal usable.
- `HF_TOKEN` present in `.env` (len 25) → available for gated HF model pulls.
- Local GPU: NVIDIA GeForce MX250 (2 GB) — **too small** to run Qwen2.5-7B / Llama-3.2-3B / DeepSeek-V2.5 even quantized; open-source models must run on Modal cloud, not locally.

### THE critical bug: empty options (invalidated all earlier annotation/IAA)
- Both `annotation/openrouter_annotators.py` and `annotation/modal_annotators.py` built the option dict as
  `{k: str(row.get(k, "")) for k in ("A","B","C","D")}` — i.e. they read columns named `A,B,C,D`.
- The sample CSV `paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv` actually uses columns **`option_A, option_B, option_C, option_D`**.
- Result: every model was sent **empty options** (`Options:\nA) \nB) \n...`) and just guessed a letter.
- This fully explains the meaningless pre-fix IAA (Fleiss' κ ≈ 0.003, acc 0.15–0.33, near-chance) — it was NOT low model skill, it was empty prompts.
- **Fix (both files):** `{k: str(row.get(f"option_{k}", row.get(k, ""))) for k in ("A","B","C","D")}` (read `option_*` with fallback to `A/B/C/D`).

### OpenRouter fix + re-run (DONE, valid)
- User requested models: **gpt-4o-mini (or nano), claude-3, gemini-2.5-flash**. The `DEFAULT_OPENROUTER_MODELS` already matched: `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`, `google/gemini-2.5-flash`. Added the `anthropic/claude-3-haiku` pricing entry (`(0.25, 1.25)`) to `_estimate_cost()` so cost is estimated instead of falling back to the default `(2.0, 8.0)`.
- Re-ran `run_openrouter_annotation()` over the full 60-item sample → **60 × 3 = 180 calls, cost $0.0055**.
- Output: `annotation/outputs/openrouter_annotation_results_openrouter_annotator_20260707_212031.csv`.
- The earlier same-session OpenRouter run (`..._20260707_185933.csv`) used empty options → **invalid** → moved to `annotation/outputs/stale_runs_20260707/`. The 15:45 probe run (`..._20260707_154531.csv`, gpt-4o + gemini, 5 items) also archived there.

### Valid OpenRouter IAA (`python -m annotation.compute_iaa`)
Once the empty-options bug was fixed and the broken run archived, `compute_iaa.py` produced real numbers:

| Model | Answered | Acc vs v68 consensus | Acc vs gold |
|---|---|---|---|
| anthropic/claude-3-haiku | 60/60 | 0.5833 | 0.7833 |
| google/gemini-2.5-flash | 60/60 | 0.5000 | 0.7833 |
| openai/gpt-4o-mini | 54/60 | 0.5500 | 0.7778 |

- **Fleiss' κ = 0.6706** (substantial) — vs 0.003 before the fix.
- Pairwise Cohen's κ: claude×gemini 0.5765, claude×gpt-4o-mini 0.7988, gemini×gpt-4o-mini 0.6402.
- **Key finding:** all three closed models match the **gold curated meaning** ~78% of the time but the **v68 blind-committee consensus label** only 50–58%. Implication: the v68 `consensus_label` is unreliable on ~22% of items (or the curated gold meaning is the more trustworthy target). This is a citable methodological point for the paper's human-validation section.
- gpt-4o-mini had 6 `parse_failed` (no hard refusals, unlike the old `gpt-4o` which refused 60%).
- Artifacts: `annotation/outputs/iaa_report_20260707_212914.json`, `annotation/outputs/iaa_summary_20260707_212914.csv`.

### Modal fixes (code complete, run blocked by Modal cloud)
Three Modal defects were fixed in `annotation/modal_annotators.py`:
1. **Hydration** — old code called the GPU function `.remote()` from a helper that was not reliably inside `with app.run()`. Rewrote to **batch all prompts for one model into a single `_modal_annotate_batch.remote(model, prompts)` call** inside `with _MODAL_APP.run():`, and switched the inference engine from fragile **vLLM to a `transformers` pipeline** (more robust for these models). The model now loads **once per model**, not per item.
2. **Gated-model auth** — `meta-llama/Llama-3.2-3B-Instruct` and `deepseek-ai/DeepSeek-V2.5` are **gated** HF repos; the Modal container had no `HF_TOKEN`, so downloads 401'd (and the call appeared to hang). Added `_load_hf_token()` (reads `HF_TOKEN`/`HUGGING_FACE_HUB_TOKEN` from env or `.env`) and attached `secrets=[modal.Secret.from_dict({"HF_TOKEN":..., "HUGGING_FACE_HUB_TOKEN":...})]` to the function when a token exists.
3. **`device_map`** — changed `device_map="auto"` (accelerate auto-mapping, suspected of hanging on Modal's container) to `device_map="cuda" if torch.cuda.is_available() else None`.

### Modal stall diagnosis (NOT a code bug)
- Two background runs were attempted and both stalled with **zero log output** (the per-item JSONL only writes after a `.remote()` returns, so no entries = `app.run()` never entered):
  - `bgp_f3e711c7f001ElJwcUGg4315x3` (Qwen2.5-7B, 3 items) — hung ~50 min, killed.
  - `bgp_f3e882a0b001nwVjb0i6UF7r4C` (Qwen2.5-7B, 3 items, post `device_map` fix) — hung ~10 min, killed.
- Proof the code path is correct: isolated Modal tests all worked — heavy image build (torch+transformers) in **18s**, a trivial function call in **12s**, and a model-load attempt reached the HF **401 gating error in seconds** (confirming it got to model download, just blocked by auth before the secret fix). The stall is therefore **Modal cloud GPU scheduling / A10G capacity**, not our logic.
- `DEFAULT_MODAL_MODELS` = `Qwen/Qwen2.5-7B-Instruct` (public), `meta-llama/Llama-3.2-3B-Instruct` (gated), `deepseek-ai/DeepSeek-V2.5` (gated).

### Important caveats to remember
- The LLM annotators are **answer-only proxies** (single-letter selection), NOT a substitute for the native-speaker human validation delivered via `blinded_export.py` + `protocol.md` (plausibility 1–5, confidence 1–3, shortcut flags). The human validation is still the required paper deliverable.
- `compute_iaa.py` globs **all** `openrouter_annotation_results_*.csv` and `modal_annotation_results_*.csv` in `annotation/outputs/`. Stale/broken runs MUST stay archived in `annotation/outputs/stale_runs_20260707/` or they will pollute the IAA. Old Modal result CSVs (`..._20260707_154749.csv`, `..._20260707_155052.csv`) and the old IAA report are already archived there.
- For gated models to actually download, the HF account behind `HF_TOKEN` must have **accepted the Llama-3.2 and DeepSeek-V2.5 licenses**; otherwise it will 401 even with a valid token.
- The pre-fix IAA numbers (Fleiss 0.003, acc 0.15–0.33) are **superseded** by the valid run above.

### Where things are (file map)
| Path | Status |
|---|---|
| `annotation/openrouter_annotators.py` | fixed (option_*, models, pricing) |
| `annotation/modal_annotators.py` | fixed (batching, HF secret, device_map) |
| `annotation/compute_iaa.py` | unchanged; reads 60-item sample + result CSVs |
| `annotation/outputs/openrouter_annotation_results_openrouter_annotator_20260707_212031.csv` | **VALID** (60×3) |
| `annotation/outputs/iaa_report_20260707_212914.json` + `iaa_summary_20260707_212914.csv` | **VALID OpenRouter IAA** |
| `annotation/outputs/stale_runs_20260707/` | archived broken/invalid runs (keep out of IAA glob) |
| `paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv` | v68 60-item validation sample (option_A…D) |

### Next steps (ordered)
1. **Unblock Modal** — pick ONE: (a) retry later when A10G capacity is free; (b) **switch GPU class** to `L40S` or `A100` (edit the `gpu="A10G"` in `_modal_annotate_batch` decorator and in `run_modal_annotation`'s `gpu` param — note `run_modal_annotation` passes `gpu` but currently does not forward it to the decorator; the decorator hardcodes `A10G`, so change it there); (c) run on a larger local GPU if one becomes available (MX250 is too small).
2. Confirm the HF account has accepted the Llama-3.2 / DeepSeek-V2.5 licenses before expecting gated models to download.
3. Run Modal over the full 60-item sample → `modal_annotation_results_*.csv`.
4. Run `python -m annotation.compute_iaa` → **combined** OpenRouter (3) + Modal (3) 6-model IAA (Fleiss' κ, per-model acc vs gold/consensus, pairwise Cohen's κ).
5. Recruit the actual native-speaker annotators and populate `blinded_items.csv` answers; compute human IAA (Cohen's κ) — the paper-required deliverable.
6. Fold the LLM-proxy agreement + human IAA + the "v68 consensus vs gold disagreement (~22%)" finding into the paper's human-validation / limitations section.

### One-line summary
Fixed a silent empty-options bug that had made the LLM-annotator IAA look like chance; with real options the 3 closed OpenRouter models show substantial agreement (Fleiss κ=0.67, 78% match gold), while the Modal open-source run is blocked by Modal cloud GPU capacity (code is correct and ready to retry on L40S/A100 or later).

## 7. Current State Update - July 10, 2026 (Phase 0 + Phase 1 + Phase 2 Complete; Phase 3 Prepared)

### Summary

Completed a full paper-securing sprint: rewrote the abstract with actual v68 numbers, generated 18 traceable analysis tables from raw CSVs, drafted the complete paper, generated 4 figures, and prepared the submission package. All legacy claims from the Groq Pilot 2 pipeline have been removed or replaced with current v68 data. The paper is now submission-ready on v68 N=5 (180 MCQs) pending a final budget decision for v69/v70.

### Critical Corrections (Data Over Memory)

| Item | Previous belief | Actual value | Source |
|------|-----------------|--------------|--------|
| Fleiss κ (LLM proxy) | 0.6706 (3-model subset) | **0.4845** (7-model, 60 items) | `annotation/outputs/iaa_report_20260708_121120.json` |
| Position shuffling | Assumed active | **INACTIVE** — round-robin only | `src/generation/...py` line 1800+ |
| Position bias significance | Assumed severe | **p = 0.322** — not significant at N=180 | `table_position_bias_chi2.csv` |

### Phase 0: Paper Integrity & P0 Kill Risks (Completed 2026-07-10)

**Abstract rewrite:** `docs/ProverbGap_Reframed_Title_Abstract.md` completely rewritten. Claims now map to actual v68 artifacts. Legacy numbers removed:
- 2,313 MCQs → 180 MCQs
- S1 86.8% vs S2 62.5% → removed (legacy Groq cross-pipeline)
- Cross-lingual boundary 8.9pp/2.2pp → removed (legacy S1/S2 delta)
- Encoder baselines (mBERT 54.7%, etc.) → removed; replaced with TF-IDF cosine 36.7%
- Same-family exploitation +31.1pp → removed (legacy)
- CoT collapse 82.7%→48% → removed (legacy)
- MSP triviality 100% acc → removed (legacy)
- API fragility 90% → removed; replaced with zero-failure strength
- Position bias 60.6pp → removed; replaced with exact A=73.3% D=46.7%, p=0.322
- Human κ ≥ 0.75 → removed; replaced with κ = 0.4845

**Table split:** `table7_failure_taxonomy.csv` split into:
- `kaggle/run_logs/v68/table7_legacy_findings.csv` (5 legacy rows with source=legacy_groq_pilot2)
- `kaggle/run_logs/v68/table7_v68_findings.csv` (1 current row: corpus fallback 43.9%)

**Statistical tests added:**
- McNemar's test for 6 variant pairs (all non-significant, p > 0.05)
- Wilcoxon signed-rank for 3 generator pairs (all non-significant, p > 0.05)
- Holm-Bonferroni correction applied
- Bootstrap 95% CIs for ALL 6 primary metrics + per-language + per-variant

**Data provenance:** `DATA_PROVENANCE_TEMPLATE.md` fully filled with actual inventory data.
- Yoruba: copyrighted (Owomoyela 2005, UNP), no redistribution permission. **Decision:** scoped public release to English + Arabic only. Yoruba MCQs retained in analysis but excluded from public dataset.
- Arabic: source dataset unknown, license unknown. Flagged as liability.
- English: scraping sources undocumented. MCQ artifacts only will be released.

**Position bias analysis:**
- A-position: 73.3%, B: 57.8%, C: 48.9%, D: 46.7%
- Chi-square: χ² = 3.49, df = 3, p = 0.322 (NOT significant)
- Balanced key distribution (45/45/45/45) means raw consensus is unbiased
- Position-corrected consensus = raw consensus (no delta)
- Position shuffling verified: **INACTIVE in v68**, but 74.5% flip rate confirmed when enabled (tested on 20 MCQs × 10 shuffles)

### Phase 1: Baselines & Robustness (Completed 2026-07-10)

| Table | File | Key finding |
|-------|------|-------------|
| Heuristic baselines | `table_heuristic_baselines.csv` | All-A/D = 25.0%, Random = 25.0%, Shortest = 13.9%, Longest = 41.1% |
| Length bias | `table_length_bias.csv` | Pearson r = -0.0086 (zero correlation). Mean lengths perfectly balanced across positions (84.4–85.4 chars). |
| Shuffling robustness | `table_shuffling_robustness.csv` | 74.5% flip rate (149/200) across 20 MCQs stratified by language |
| Single-generator ablation | `table_single_generator_ablation.csv` | gemma-4-31b-it: 65.0% acc, 35.0% HCW. Pooled: 56.7% acc, 43.3% HCW. Pool is worse than best single generator. |
| Encoder baselines | `table_encoder_baselines_v68.csv` | TF-IDF cosine = 36.7% (EN 53.3%, AR 21.7%, YO 35.0%). Committee outperforms lexical by +20.0pp. |
| Cost efficiency | `table_cost_efficiency.csv` | $0.0047/MCQ, $0.0012/audit vote, 720 votes for $0.85 |
| LLM-proxy IAA | `table_llm_proxy_iaa.csv` | Fleiss κ = 0.4845, mean pairwise Cohen κ = 0.4846, per-model gold accuracy 58.3–78.3% |
| Committee family | `table_committee_family.csv` | Auditor families: Meta (53.3%), Mistral (56.7%), Google (45.6%), DeepSeek (56.1%). Pairwise Cohen κ 0.485–0.555. |

**Reproducibility package created:**
- `reproducibility/requirements.lock` (241 lines pinned)
- `reproducibility/openrouter_catalog_snapshot_2026-06-22.json` (model IDs + families)
- `reproducibility/v68_output_hashes.txt` (6 SHA256 hashes)
- `reproducibility/REPRODUCIBILITY_CHECKLIST.md` (full reproduction steps)

### Phase 2: Paper Drafting (Completed 2026-07-10)

**Full paper draft:** `paper/proverbgap_eacl2027.md` — 11 sections, ~12,000 words.
**Section files:** `paper/sections/01_introduction.md` through `11_conclusion.md`
**Figures generated (300 dpi PNGs):**
- `fig2_per_language_accuracy.png` — English 65.0%, Arabic 53.3%, Yoruba 51.7%
- `fig3_position_bias.png` — A=73.3%, D=46.7%
- `fig4_fallback_heatmap.png` — variant × language fallback counts
- `fig5_filter_breakdown.png` — NLI 36.3%, leak 35.2%, length 15.1%

**Claims inventory:** Every claim in the paper maps to a specific v68 CSV/JSON with ✅ verification. Traceability table in `docs/ProverbGap_Reframed_Title_Abstract.md` Section 6.

### Phase 3: Budget-Dependent Preparation (Completed 2026-07-10)

**Decision rule documented** in `docs/PHASE_3_BUDGET_DEPENDENT.md`:
```
IF OpenRouter budget renewed by July 26:
    Run v69 (USE_LLM_FALLBACK=True, N=5)
    IF HCW < 15% and partial+fallback < 30%:
        Run v70 (N=15)
    ELSE:
        Keep v68
ELSE:
    Submit v68 on August 1
```

**Cost estimate:**
- v69 only: ~$0.89
- v69 + v70: ~$3.55
- Combined well under $5.00 hard cap

**Kaggle trigger script ready:** `scripts/trigger_kaggle_run.py` (uses `ApiSaveKernelRequest` with `SAVE_AND_RUN_ALL`)

### Complete Artifact Inventory

```
docs/
  ProverbGap_Reframed_Title_Abstract.md          (rewritten, 131 lines)
  gap_liability_analysis_2026-07-10.md           (deep gap analysis)
  phase1_gate_check.md                            (new)
  budget_status.md                                (new)
  production_dataset_decision.md                  (new)
  EXECUTION_ITINERARY_2026-07-10.md              (day-by-day plan)
  PHASE_3_BUDGET_DEPENDENT.md                     (v69/v70 decision rule)

kaggle/run_logs/v68/
  v68_detailed_analysis_report.md
  v68_generation_quality_report.md
  v68_per_language_report.md
  table7_legacy_findings.csv                     (new)
  table7_v68_findings.csv                        (new)
  table_single_generator_ablation.csv            (new)
  table_encoder_baselines_v68.csv                (new)
  table_filter_replacement_analysis.csv          (new)
  table_variant_language_interaction.csv         (new)
  table_llm_proxy_iaa.csv                        (new)
  table_cost_efficiency.csv                      (new)
  table_statistical_tests_mcnemar.csv            (new)
  table_statistical_tests_wilcoxon.csv           (new)
  table_statistical_tests_corrected.csv          (new)
  table_bootstrap_cis.csv                        (new)
  table_auditor_vs_gold.csv                      (new)
  table_position_bias_chi2.csv                   (new)
  table_committee_family.csv                     (new)
  table_heuristic_baselines.csv                  (new)
  table_length_bias.csv                          (new)
  table_shuffling_robustness.csv                 (new)
  analysis_scripts/                              (11 Python scripts)
  reproducibility/                               (lockfile, snapshot, hashes, checklist)

paper/
  proverbgap_eacl2027.md                         (full draft, 11 sections)
  sections/01–11.md                              (individual sections)
  figures/fig2–5.png                             (4 publication-ready PNGs)
  tables/                                        (18 CSVs)
  generate_figures.py                            (figure generation script)

submission_package_2026-08-02/
  proverbgap_eacl2027.md
  README.md
  reviewer_risk_checklist.md
  DATA_PROVENANCE_TEMPLATE.md
  EXECUTION_ITINERARY_2026-07-10.md
  PHASE_3_BUDGET_DEPENDENT.md
  tables/ (18 CSVs)
  figures/ (4 PNGs)
  reproducibility/ (4 files)
```

### Key Decisions Made

| Decision | Date | Rationale |
|----------|------|-----------|
| Drop all legacy Groq S1/S2 claims | 2026-07-10 | Cross-pipeline contamination; cannot reproduce on hardened pipeline |
| Frame paper as methodology + testbed, not benchmark | 2026-07-10 | Deflects comparison with ProverbEval; aligns with actual N=5 data |
| Scope public data release to EN/AR only | 2026-07-10 | Yoruba copyright risk (Owomoyela 2005, UNP) |
| Use actual computed Fleiss κ = 0.4845, not memory claim 0.67 | 2026-07-10 | 0.67 was from earlier 3-model subset; 0.4845 is the valid 7-model run |
| Report position bias as p = 0.322 (not significant) | 2026-07-10 | Correct statistical interpretation; balanced keys neutralize aggregate bias |
| Enable shuffling in v70, not v68 | 2026-07-10 | v68 is frozen; v70 will have 74.5% flip rate mitigation |
| Submit with v68 if budget not renewed by Aug 1 | 2026-07-10 | Paper is ready; waiting for budget risks missing deadline |
| Do NOT attempt Modal replacement for generation/audit | 2026-07-10 | Code mismatch, time cost, and correctness risk outweigh savings |

### Reviewer Risk Status

| Risk Level | Count | Status |
|------------|-------|--------|
| P0 (desk-reject) | 8 | ALL FIXED |
| P1 (major-reject) | 10 | ALL FIXED or ADDRESSED |
| P2 (minor) | 2 | PLANNED or ACCEPTABLE |

### Next Actions (Ordered)

1. **Polish paper draft** — merge sections, tighten prose, fix citations (you)
2. **Check OpenRouter budget** — dashboard or support ticket (you)
3. **If budget renewed:** execute v69 via `scripts/trigger_kaggle_run.py` (Kilo)
4. **If budget NOT renewed:** submit v68 paper on August 1 (you)
5. **Convert to LaTeX** — ARR requires LaTeX; use ACL template (you)
6. **Refine Figure 1** — pipeline diagram (vector) (Kilo)
7. **Write cover letter** — emphasize methodology + failure taxonomy (you)
8. **Prepare rebuttal pre-doc** — top 5 reviewer attacks (you)

### One-line Summary

Paper is fully drafted, figures generated, 18 tables created from raw v68 data, all legacy claims purged, P0 kill risks fixed, and submission package complete — ready to submit on August 1 with v68 N=5 or to upgrade to v69/v70 if OpenRouter budget renews.

---
*End of Current State Update - July 10, 2026*

---

## Current State Update - 2026-07-12 (Paper claim-verification & corrections)

### Summary

A 12-item "critical-fix list" was reviewed against the current paper files. Verification showed the list was **partially stale/incorrect**: items 1–4, 6, 9, 11, 12 were genuine; items 7 and 8 were FALSE and must NOT be applied. The genuine issues were fixed across `docs/ProverbGap_Reframed_Title_Abstract.md`, `paper/proverbgap_eacl2027.md`, `paper/sections/*.md`, and `submission_package_2026-08-02/*`.

### Verified-true fixes applied

| Item | Issue | Fix |
|------|-------|-----|
| 1 | Abstract + Fig-3 caption + non-goals #9 still said `χ² significant at p < 0.001` (LEGACY Groq number) | Changed to `χ² = 3.49, p = 0.322 (not significant at N = 180)`; softened "severe position bias" to "position bias" |
| 2 | §5.2 claimed "non-overlapping CIs" for EN vs AR/YO | EN [53.3,76.7] vs AR [40.0,65.0] **overlap** → corrected to "numerically easier, CIs overlap, not statistically distinguishable at N=60/language" |
| 3 | Google in BOTH generator (`gemma-4-31b-it`, `gemini-2.5-flash`) and auditor (`gemma-3-27b-it`) pools; contradicted "prevents same-family exploitation" | Changed claim to "reduces same-family exploitation"; disclosed residual Google overlap, justified by blind options-only design; checklist updated to QUALIFIED |
| 4 | "78% match to gold" cherry-picked top model | Changed to "58.3–78.3% match to curated gold meanings (mean 69.4%)" in abstract + conclusion |
| 6 | Null McNemar/Wilcoxon reported without power note | Added power caveat to §8.4 (N=5 limited power; planned N=15 → ≈0.85) |
| 9 | IAA 60-item subset described as if representative | Added note in §9.1 that subset is stratified for human-validation (not a random sample) |
| 11 | No per-model cost breakdown | Added pointer to `table_cost_efficiency.csv` in §3.7 |
| 12 | "Zero refusals" lacked context | Added "on this multiple-choice annotation task (no safety/policy blocks triggered)" in §9.2 |

### Items correctly NOT applied

| Item | Why skipped |
|------|-------------|
| 7 | "Pool worse than gemma-only unexplained" — FALSE; §5.3 and §8.3 already explain it (weaker generators add HCW) |
| 8 | "5 × 12 arithmetic error → 15 proverbs × 4 variants" — FALSE; 5×12=60 is correct (5 proverbs × 12 generator×variant). "15 proverbs × 4 variants" is wrong per-language (only 5 proverbs/language; 15 is cross-language total) |

### Root cause of item 1

The July 10 Phase-0 abstract rewrite updated the non-goals list (memory line 1579) to `p = 0.322` but **left the actual abstract body and Fig-3 caption with the legacy `p < 0.001`**. The paper body (§5.4, §6.6) was already correct. Now abstract, figures, body, and checklist are consistent at `p = 0.322`.

### Files touched

- `docs/ProverbGap_Reframed_Title_Abstract.md` (abstract, Fig-3 caption, claims inventory, non-goals #9)
- `paper/proverbgap_eacl2027.md` (§2.3, §3.7, §5.2, §8.4, §9.1, §9.2, §11)
- `paper/sections/02_related_work.md`, `05_results.md`, `11_conclusion.md`
- `submission_package_2026-08-02/proverbgap_eacl2027.md` (mirror)
- `submission_package_2026-08-02/reviewer_risk_checklist.md` (same-family row → QUALIFIED)

### Verification

`grep` for `p < 0.001`, `non-overlapping`, `78% match`, `prevents same-family` in `paper/`, `submission_package/`, `docs/` → zero matches (excluding `.archive/` and historical `memory.md` legacy-pilot numbers).

---

*End of Current State Update - 2026-07-12*

---

## VENUE ROUTING UPDATE - 2026-07-29 (LATEST - supersedes earlier venue notes)

- CONFIRMED ON PLAN: EACL 2027 via ARR August 2026 cycle. Submit Aug 3, 2026 (AoE). Mandatory reviewer registration (ALL co-authors) by Aug 5, 2026. Author response Sept 14-24. Commitment deadline Oct 11, 2026. Notification Nov 12, 2026. Camera-ready Nov 26, 2026.
- EACL 2027: March 9-14, 2027, Athens, Greece. Virtual presentation is allowed and fully archival in the ACL Anthology (no distinction from in-person).
- COST/FUNDING: virtual presenter approx USD 300 student all-in (2026 precedent); authors from eligible regions (Nigeria qualifies) can get free/sliding-scale virtual registration; EACL D&I grants expected late 2026 (EACL 2026 precedent: registration waivers + travel support; student volunteers get registration waived).
- FALLBACK: AfricaNLP 2027 (CFP expected ~Oct-Dec 2026; virtual presenter fee ~USD 125, waivable for African-region authors; ACL Anthology archival; strong sponsorship tradition covering registration+travel+hotel for African applicants).
- PACING NOTE: self-imposed 1-2 papers per ARR cycle. This paper + Lemons_Lemondade are the two candidates for the Aug 3, 2026 cycle; AfriKnow goes in the Oct 12, 2026 cycle.
- Source: full venue audit 2026-07-29 - see C:\Users\USER\Downloads\CONFERENCE_VENUE_ROUTING_2026-07-29.md

---
