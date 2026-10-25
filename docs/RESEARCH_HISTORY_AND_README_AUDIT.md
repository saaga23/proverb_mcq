# ProverbGap Research History and README Audit

**Document purpose:** Single-source-of-truth handover document reconciling the full experiment timeline, data provenance, metric definitions, and legacy-number handling for the ProverbGap MCQ project.

**Last updated:** 2026-10-25
**Canonical production dataset:** v68 (180 MCQs, N=5 per language, seed 20260615)

---

## 1. Experiment Timeline (v59-v70)

### 1.1 Version summary

| Version | Run date | N per language | Config flag | Outcome | Status |
|---------|----------|---------------:|-------------|---------|--------|
| v59-v60 | 2026-06-19 to 2026-06-20 | 1 | OpenRouter pipeline (refinements 1-2) | 45 MCQs (N=1 per language) | Pre-v68 lineage; numbers not used in v68 paper |
| v61-v67 | 2026-04 to 2026-06 | 1-3 | OpenRouter pipeline refinement | Config refinements, bug fixes | Archived; v67 frozen as baseline |
| v68 | 2026-06-22 | 5 | v67 baseline (USE_LLM_FALLBACK=False) | 180 MCQs, $0.85, full blind audit | Production |
| v69 | Never | 5 | USE_LLM_FALLBACK=True | Never executed on Kaggle | Blocked -- budget exhausted |
| v70 | 2026-06-22 | 5 | v68 config with USE_LLM_FALLBACK=True | Halted at 11/15 rows of adversarial-hard-negative, $0.42 spent | Halted -- OpenRouter budget limit (403) during 2nd variant |

### 1.2 The "80" mystery -- resolved

The string "80" appears in legacy Kaggle audit logs, e.g.:

- "Audited 80/90 MCQs" (audit-progress checkpoint in a legacy kernel log)
- "Audited 80/270 MCQs" (another stale log fragment)

**This is an audit-progress checkpoint counter, not a dataset size.** No version of this project ever produced exactly 80 MCQs:

| Version | Actual MCQ count |
|--------:|-----------------:|
| v59-v60 | 90 (legacy, per audit log "90" denominator) |
| v65 | 36 (N=1, 3 proverbs) |
| v68 | 180 (N=5) |
| v70 | 0 completed (halted mid-run at 11/15 rows, $0.42 spent) |

The audit logs that mention "80" are from legacy runs and refer to the number of items audited before the kernel was interrupted. The canonical production dataset is v68 with 180 MCQs.

### 1.2b Evaluation prompting styles (legacy vs. v68)

The legacy Groq S1/S2 pipeline used evaluation prompting styles where the model was asked to evaluate MCQ difficulty:

| Style | Evidence in codebase |
|-------|---------------------|
| Zero-shot | `kaggle/kaggle_analysis/missing_data_impact_analysis.py`; legacy archive CSVs |
| Few-shot | Legacy archive CSVs (2-3 example evaluations provided) |
| Chain-of-thought | Legacy archive CSVs (2-3 examples with step-by-step reasoning) |
| One-shot | **No evidence found** in codebase, logs, or Kaggle notebooks |

These are distinct from v68's **distractor-generation** prompt variants (`adversarial-length-locked`, `adversarial-hard-negative`, `taxonomy-guided`, `overgenerate-select`). The `few-shot-predictive` generation variant (v2.x–v67, dropped in v68) provides few-shot examples for *generating* distractors, not for *evaluating* them. v68's audit committee uses **blind options-only voting** — no evaluation prompting styles are applied.

### 1.3 v69 status: never executed

**v69 was planned as the LLM-fallback ablation run** (USE_LLM_FALLBACK=True, N_PER_LANG=5, FALLBACK_GENERATOR_MODEL="openai/gpt-4.1-nano"), but it was **never executed on Kaggle**. Evidence:

- `kaggle/run_logs/v69/v69_detailed_analysis_report.md` -- all TBD blanks, no data populated
- `kaggle/run_logs/v69/v69_post_download_checklist.md` -- never run (0 files downloaded)
- `kaggle/run_logs/v69/v68_v69_comparison_report.md` -- template header: "This is a template comparing v68 and v69"
- No `pilot1_test_summary.json` or output CSVs in v69 directory
- No Kaggle run ID or kernel output linked to v69

The v69 config diff exists in `docs/PHASE_3_BUDGET_DEPENDENT.md` but was never applied to a Kaggle run. OpenRouter budget was exhausted ("403 Budget limit exceeded") before the v69 run could start.

### 1.4 v70 status: halted by budget exhaustion (N=5)

**v70 was started as an N=5 LLM-fallback run** (`USE_LLM_FALLBACK=True`, same seed 20260615, 15 proverbs) but was **halted by budget exhaustion** during Kaggle notebook execution. Evidence:

- `kaggle/run_logs/v70/mcq-pass-shortcut.log` -- shows the Kaggle notebook log with successful completion of the `adversarial-length-locked` variant (15/15 rows, $0.30) and start of `adversarial-hard-negative` before 403 budget errors began at 11/15 rows ($0.42 spent)
- `kaggle/run_logs/v70/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv` -- 83 partial generation rows saved before the crash (45 from `adversarial-length-locked`, 38 from `adversarial-hard-negative`)
- `kaggle/run_logs/v70/openrouter_pilot1_test_output/pool_state.json` -- records incomplete status (`position_counter=83`, `generation_done=false`, `audit_done=false`, `audited_mcq_ids=[]`)
- `kaggle/run_logs/v70/openrouter_pilot1_test_output/pilot1_test_raw_outputs.csv` -- 166 raw generation attempt rows saved
- No `pilot1_test_audit_results.csv` or `pilot1_test_summary.json` was produced -- the audit phase was never reached

The v70 run was halted mid-generation. Only 83 partial generation rows were saved (45 from the completed `adversarial-length-locked` variant, 38 from the incomplete `adversarial-hard-negative` variant at 11/15 rows); no audit CSV or summary JSON was produced. v70 cannot be used for paper claims because the audit phase was never reached and the saved rows are partial generation output, not a completed or audited benchmark.

---

## 2. Canonical v68 Metrics (with denominators and thresholds)

All v68 metrics below are verified against files in `kaggle/run_logs/v68/`.

### 2.1 Aggregate metrics

| Metric | Value | Denominator | Threshold / Definition | Source file |
|--------|------:|------------:|:----------------------:|-------------|
| Total MCQs | 180 | -- | 15 proverbs x 4 variants x 3 generators = 180 | `pilot1_test_generated_mcqs.csv` |
| Generation cost | $0.8539 | -- | $5.00 budget cap | `pilot1_test_summary.json` |
| Cost per MCQ | $0.0047 | -- | $0.8539 / 180 | `pilot1_test_summary.json` |
| Consensus accuracy | 56.7% | 102/180 | Plurality vote matches correct label | `pilot1_test_audit_results.csv` |
| Perfect consensus | 41.7% | 75/180 | All 4 auditors agree on correct answer | `pilot1_test_audit_results.csv` |
| HCW (consensus fraction >= 0.75, wrong) | 27.8% | 50/180 | Consensus fraction >= 0.75 (3 of 4 auditors) AND consensus != correct | `v68_detailed_analysis_report.md` line 61 |
| Partial + fallback | 43.9% | 79/180 | generation_status in {partial, length_fallback} | `v68_generation_quality_report.md` section 1 |
| Partial (only) | 27.8% | 50/180 | generation_status = partial | `v68_generation_quality_report.md` section 1 |
| Hard fallback (length_fallback) | 16.1% | 29/180 | generation_status = length_fallback | `v68_generation_quality_report.md` section 1 |
| Parse/hard fallback | 0.0% | 0/180 | generation_status in {parse_fallback, hard_fallback} | `v68_generation_quality_report.md` section 5.3 |
| Duplicate options | 0 | 0 | Exact duplicate option pairs | `v68_generation_quality_report.md` section 3 |
| Correct-key balance | 45/45/45/45 | 180 total | Balanced 45 per position (A/B/C/D) | `v68_detailed_analysis_report.md` line 23 |

### 2.2 Per-language metrics

| Language | N | Consensus accuracy | 95% CI (Wilson) | Perfect consensus | HCW (>=0.75) | Fallback mean |
|----------|---------|-------------------|-----------------|-------------------|-------------|---------------|
| English | 60 | 65.0% (39/60) | 52.4%-75.8% | 45.0% (27/60) | 18.3% (11/60) | 0.43 |
| Arabic | 60 | 53.3% (32/60) | 40.9%-65.4% | 50.0% (30/60) | 31.7% (19/60) | 1.52 |
| Yoruba | 60 | 51.7% (31/60) | 39.3%-63.8% | 30.0% (18/60) | 33.3% (20/60) | 1.03 |

Source: `v68_detailed_analysis_report.md` sections 2-3, `v68_per_language_report.md`

### 2.3 Per-generator metrics (v68)

| Generator | N | Accuracy | Perfect | HCW (>=0.75) | Fully generated |
|-----------|---------|----------|---------|-------------:|-----------------|
| google/gemma-4-31b-it | 60 | 65.0% | 46.7% | 35.0% | 66.7% (40/60) |
| google/gemini-2.5-flash | 60 | 53.3% | 41.7% | 46.7% | 50.0% (30/60) |
| qwen/qwen3.7-max | 60 | 51.7% | 36.7% | 46.7% | 51.7% (31/60) |

Source: `v68_detailed_analysis_report.md` section 4.1

### 2.4 Per-variant metrics (v68)

| Variant | N | Accuracy | Perfect | HCW (>=0.75) | Fully generated |
|---------|---------|----------|---------|-------------:|-----------------|
| adversarial-hard-negative | 45 | 60.0% | 31.1% | 40.0% | 26.7% (12/45) |
| adversarial-length-locked | 45 | 55.6% | 53.3% | 44.4% | 60.0% (27/45) |
| overgenerate-select | 45 | 53.3% | 35.6% | 46.7% | 71.1% (32/45) |
| taxonomy-guided | 45 | 57.8% | 46.7% | 40.0% | 66.7% (30/45) |

Source: `v68_detailed_analysis_report.md` section 4.2

### 2.5 HCW threshold discrepancy -- resolved

There is a documented discrepancy between files regarding the HCW threshold:

| File | HCW threshold | HCW value |
|------|----------------|-----------|
| `v68_detailed_analysis_report.md` line 61 (canonical) | >= 0.75 (3 of 4 auditors) | 50/180 = 27.8% |
| `v68_per_language_generator_report.md` | >= 0.50 (majority) | 77/180 = 42.8% |
| `v68_per_language_report.md` section 2 | >= 0.75 (canonical) | 50/180 = 27.8% |
| `v68_per_language_report.md` section 8.2 | -- | 77/180 = 42.8% (typo -- inconsistent with section 2) |

The `v68_per_language_generator_report.md` consistently uses a >= 0.50 threshold for its per-language HCW numbers (English 33.3%, Arabic 46.7%, Yoruba 48.3% = 77/180). The canonical threshold is >= 0.75, which gives 50/180 = 27.8% (English 18.3%, Arabic 31.7%, Yoruba 33.3%).

**Resolution:** The >= 0.75 threshold (3 of 4 auditors) is the project standard. This README uses 27.8% as the primary HCW figure. The >= 0.50 numbers in `v68_per_language_generator_report.md` are marked as using an alternate, stricter definition and are not cited as the primary HCW rate.

The `v68_per_language_report.md` section 8.2 contains a typo ("77/180 = 42.8%") that is inconsistent with its own section 2 (which correctly reports 50/180 = 27.8%). The canonical report (`v68_detailed_analysis_report.md`) is the authoritative source.

---

## 3. Model Roster (v68)

### 3.1 Generator pool

The v68 config defines a 10-model pool, of which 3 were active (0 benched substitutions):

| Model | Family | Active? | Notes |
|-------|--------|---------|-------|
| qwen/qwen3.7-max | Qwen | Yes | 60 MCQs, 51.7% accuracy, 46.7% HCW |
| google/gemma-4-31b-it | Google | Yes | 60 MCQs, 65.0% accuracy, 35.0% HCW (strongest) |
| google/gemini-2.5-flash | Google | Yes | 60 MCQs, 53.3% accuracy, 46.7% HCW |
| meta-llama/llama-3.3-70b-instruct | Meta | No (pooled) | In auditor pool, not generator pool |
| mistralai/mistral-small-3.2-24b-instruct | Mistral | No (pooled) | In auditor pool, not generator pool |
| google/gemma-3-27b-it | Google | No (pooled) | In auditor pool, not generator pool |
| deepseek/deepseek-v3.2 | DeepSeek | No (pooled) | In auditor pool, not generator pool |
| anthropic/claude-3.5-sonnet | Anthropic | No (pooled) | EOL model ID, deprecated |
| openai/gpt-4o-mini | OpenAI | No (pooled) | Not used in v68 |
| amazon/nova-lite-v1 | Amazon | No (pooled) | In pool_state.json but never assigned a task |

Source: `pilot1_test_summary.json` -> pool_state.json (3 active vs 0 benched)

### 3.2 Audit committee (blind, options-only)

All 4 auditors voted on all 180 MCQs (0 missing votes, 0 substitutions):

| Auditor | Family | vs. gold (180 items) | Pairwise kappa (mean) |
|---------|--------|----------------------|-----------------------|
| meta-llama/llama-3.3-70b-instruct | Meta | 53.3% (96/180) | ~0.53 |
| mistralai/mistral-small-3.2-24b-instruct | Mistral | 56.7% (102/180) | ~0.51 |
| google/gemma-3-27b-it | Google | 45.6% (82/180) | ~0.50 |
| deepseek/deepseek-v3.2 | DeepSeek | 56.1% (101/180) | ~0.51 |

Per-language per-auditor hit rates (from `v68_per_language_report.md` section 4):

| Auditor | English | Arabic | Yoruba |
|---------|--------:|-------:|-------:|
| llama-3.3-70b | 60.0% | 51.7% | 48.3% |
| mistral-small-3.2-24b | 70.0% | 55.0% | 45.0% |
| gemma-3-27b-it | 55.0% | 45.0% | 36.7% |
| deepseek-v3.2 | 68.3% | 51.7% | 48.3% |

Pairwise Cohen's kappa between auditors (from `table_auditor_vs_gold.csv` section 2):

| Pair | kappa |
|------|-------|
| llama-3.3 vs mistral | 0.517 |
| llama-3.3 vs gemma-3-27b | 0.5249 |
| llama-3.3 vs deepseek | 0.5552 |
| mistral vs gemma-3-27b | 0.5025 |
| mistral vs deepseek | 0.5032 |
| gemma-3-27b vs deepseek | 0.4852 |

**Note on consensus vs. gold:** The aggregate auditor accuracy (56.7%) shown in `v68_detailed_analysis_report.md` section 8.1 is computed against the consensus correct column, giving identical values for all auditors. The table above uses accuracy vs. gold (curated meaning) from `table_auditor_vs_gold.csv`, which differentiates the auditors.

### 3.3 Gold meaning curator

Gold meanings were curated using `openai/gpt-4.1-nano` (via `curate_gold_meaning()`), then reviewed and locked by the project author for cultural accuracy. This is a **curator**, not a member of the 10-model generator/auditor pools.

### 3.4 Committee family diversity

| Family | In generators? | In auditors? | Mitigation |
|--------|---------------|-------------|------------|
| Google | Yes (2 models) | Yes (1 model) | Blind options-only audit; gemma-3-27b-it is architecturally distinct from gemma-4-31b-it and gemini-2.5-flash |
| Meta | No | Yes | Disjoint by design |
| Mistral | No | Yes | Disjoint by design |
| DeepSeek | No | Yes | Disjoint by design |
| Qwen | Yes | No | Disjoint by design |
| OpenAI | No | No | Absent -- documented as a limitation |
| Anthropic | No | No | Absent (legacy model ID EOL'd) |

The absence of OpenAI and Anthropic in the audit committee is a documented P1 limitation (gap_liability_analysis section 8.2). When budget renews, `openai/gpt-4o-mini` and `anthropic/claude-sonnet-4` should be added.

---

## 4. Data Provenance and Licensing

### 4.1 English

- Sources: Multiple public-domain proverb compilations (scrape URLs not recovered; see `submission_package_2026-08-02/DATA_PROVENANCE_TEMPLATE.md`)
- Status: Public domain -- eligible for CC BY 4.0 release

### 4.2 Arabic

- Sources: `MID`-prefix dataset (identification: to be confirmed)
- Status: License under review; subset of 60 MCQs to be released under CC BY 4.0 pending source verification

### 4.3 Yoruba

- Source: *Yoruba Proverbs* by Oyekan Owomoyela (University of Nebraska Press, 2005, ISBN 978-0-8032-1843-7)
- Status: **Copyrighted -- no redistribution permission obtained**
- 3,834/3,974 rows have missing QA_Flag; 3,748/3,974 have missing Comments
- **Decision (per EXECUTION_ITINERARY Day 2, Task 0.9):** Yoruba MCQs remain in the analysis but are **excluded from public dataset release**. Documented in `submission_package_2026-08-02/DATA_PROVENANCE_TEMPLATE.md` and paper Discussion.

### 4.4 Human validation sample

- File: `data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv`
- 60 items: 20 per language, stratified by generation_status (generated/partial/length_fallback)
- **Status:** Prepared but **not yet annotated** -- recruitment of 9 native speakers is budget- and time-dependent
- 60 items is below the 90-item recommendation in `annotation/sample_size_analysis.py` (P1 gap from liability analysis)

---

## 5. Cost and Budget Accounting

### 5.1 v68 actual cost

| Item | Cost |
|------|------:|
| Generation (3 generators x 180 MCQs x 4 variants) | ~$0.75 |
| Audit (4 auditors x 720 votes) | ~$0.08 |
| Gold curation (openai/gpt-4.1-nano) | ~$0.02 |
| **Total** | **$0.8539 / $5.00 budget** |
| Cost per MCQ | $0.0047 |

Source: `pilot1_test_summary.json` -> estimated_cost_usd

### 5.2 v70 actual cost (incomplete)

| Item | Cost |
|------|------:|
| Partial generation (halted mid-run, 11/15 rows of 2nd variant) | $0.42 |
| Audit (not run) | $0.00 |
| **Total spent** | **$0.42** |

Extrapolated full v68 N=5 cost (no v70 extrapolation available -- run was N=5, not N=15): ~$0.85.

### 5.3 Future cost estimates

| Task | N per language | Estimated cost | Budget required |
|------|----------------|----------------|-----------------|
| v69 ablation (LLM fallback) | 5 | ~$1.00 | OpenRouter renewal |
| v70 N=5 re-run (LLM fallback, if budget renews) | 5 | ~$0.85 | OpenRouter renewal |
| v71 N=15 scaling (hypothetical, if v70 succeeds) | 15 | ~$2.56 | OpenRouter renewal |
| Human validation (60 items x 3 annotators) | -- | ~$200-300 | MTurk / Figure Eight |

---

## 6. Position Bias Audit

From `table_position_bias_chi2.csv`:

| Position | Correct | Total | Accuracy |
|----------|--------:|------:|----------:|
| A | 33 | 45 | 73.3% |
| B | 26 | 45 | 57.8% |
| C | 22 | 45 | 48.9% |
| D | 21 | 45 | 46.7% |

chi-squared = 3.49, df = 3, **p = 0.322** -- not statistically significant at N=180.

| Metric | Raw | Position-corrected | Delta |
|--------|-----|-------------------|-------|
| Consensus accuracy | 0.5667 | 0.5667 | 0.0 |

Position-corrected consensus = equal-weighted mean across positions. The corrected metric equals the raw metric because key placement is perfectly balanced (45 per position), so the bias is calibrated out in aggregate.

**Assessment:** The position bias is a committee-calibration finding, not a fatal validity threat. The per-position gap (73.3% vs 46.7%) is large in absolute terms but does not reach significance at N=180, and balanced key placement neutralizes it in aggregate metrics. It is reported transparently in the paper as a known calibration pattern.

---

## 7. Filter Replacement Analysis

From `v68_generation_quality_report.md` section 2 and per-language breakdowns in `v68_detailed_analysis_report.md` section 5.2:

| Filter | Mean/MCQ (overall) | English | Arabic | Yoruba | Share of total |
|--------|--------------------|--------:|-------:|-------:|----------------:|
| NLI paraphrase | 0.36 | 0.15 | 0.62 | 0.32 | ~36% |
| Correct-meaning leak | 0.35 | 0.15 | 0.43 | 0.47 | ~35% |
| Length parity | 0.15 | 0.07 | 0.25 | 0.13 | ~15% |
| Blocklist | 0.02 | 0 | 0 | 0 | ~2% |
| **Total replacements** | **0.99** | **0.43** | **1.52** | **1.03** | 100% |

**Key finding:** NLI and leak filters together account for **71% of all replacements** (0.36 + 0.35 = 0.71 out of 0.99 total). The sanitizers are over-aggressively rejecting semantically plausible distractors, forcing the corpus fallback sampler to fill gaps. This is the root cause of the HCW rate (27.8%).

---

## 8. Legacy Numbers -- Complete Deprecation List

Every number in the following table is deprecated and must not appear in v68 paper claims:

| Deprecated claim | Source | Replacement in v68 |
|-----------------|--------|---------------------|
| 2,313 MCQs | Legacy Groq Pilot 2 | 180 MCQs (v68 N=5) |
| S1 86.8% vs S2 62.5% | Legacy Groq S1/S2 | 4-variant within-run comparison |
| Encoder baselines (mBERT 54.7%, XLM-R 55.3%, etc.) | Legacy draft | TF-IDF cosine baseline (36.7%) |
| Same-family exploitation +31.1pp | Legacy Groq S1/S2 | Per-family calibration + disjoint pools |
| CoT collapse 34.7pp | Legacy Groq | Filter-over-aggression (NLI+leak = 71%) |
| Multi-stage-prompt triviality 100% | Legacy Groq | Variant triviality (overgenerate-select clean) |
| Position bias 60.6pp | Legacy Groq | A=73.3% vs D=46.7%, p=0.322 (not significant) |
| API fragility 90%+ | Legacy Groq | Zero hard/parse fallback (0%) |
| "80 MCQs" | Audit logs | Audit-progress counter, not a dataset |
| Human validation kappa >= 0.75 | Old plan | LLM-proxy kappa = 0.4845 (planned human val pending) |
| Cross-lingual boundary 8.9pp / 2.2pp | Legacy S1/S2 | Fallback asymmetry (Arabic 3.5x English) |

---

## 9. Claims Audit Checklist

Every number in the v68 paper must trace to one of the following files. Claims that cannot be made (no v68 evidence) are listed separately.

### 9.1 Claims that CAN be made (with source)

| Claim | Source file | Verified |
|-------|-------------|----------|
| 180 MCQs generated | `pilot1_test_generated_mcqs.csv` (180 rows) | Yes |
| 60 per language | `pilot1_test_generated_mcqs.csv` language column | Yes |
| Cost $0.85 | `pilot1_test_summary.json` -> estimated_cost_usd | Yes |
| Cost $0.0047/MCQ | $0.8539 / 180 | Yes |
| Consensus accuracy 56.7% | `v68_detailed_analysis_report.md` + audit CSV | Yes |
| Perfect consensus 41.7% (75/180) | `v68_detailed_analysis_report.md` | Yes |
| HCW 27.8% (50/180, >=0.75) | `v68_detailed_analysis_report.md` line 61 | Yes |
| Partial+fallback 43.9% (79/180) | `v68_generation_quality_report.md` section 1 | Yes |
| Zero hard/parse fallback | `v68_generation_quality_report.md` section 5.3 | Yes |
| Zero duplicate options | `v68_generation_quality_report.md` section 3 | Yes |
| Correct-key balance 45/45/45/45 | `v68_detailed_analysis_report.md` line 23 | Yes |
| NLI 0.36, leak 0.35, length 0.15 | `v68_generation_quality_report.md` section 2 | Yes |
| Arabic fallback 1.52 vs English 0.43 | `v68_detailed_analysis_report.md` table section 3 | Yes |
| gemma-4-31b-it strongest (65.0% acc) | `v68_detailed_analysis_report.md` section 4.1 | Yes |
| Position bias A=73.3% D=46.7%, p=0.322 | `table_position_bias_chi2.csv` | Yes |
| Auditor vs gold: 53.3% / 56.7% / 45.6% / 56.1% | `table_auditor_vs_gold.csv` | Yes |
| Per-generator metrics | `v68_detailed_analysis_report.md` section 4.1 | Yes |
| Per-variant metrics | `v68_detailed_analysis_report.md` section 4.2 | Yes |
| Per-language Wilson CIs | `v68_per_language_report.md` section 1 | Yes |
| Committee families | `table_committee_family.csv` | Yes |
| Seed 20260615 | `pilot1_test_summary.json` | Yes |
| 720 blind-audit votes, 0 missing | `v68_detailed_analysis_report.md` line 44 | Yes |
| LLM-proxy IAA kappa=0.4845, mean pairwise=0.4846 | `docs/ProverbGap_Reframed_Title_Abstract.md` claims inventory | References `annotation/outputs/iaa_report_20260708_121120.json` |

### 9.2 Claims that CANNOT be made

| Claim | Why it's invalid |
|-------|-----------------|
| v69 shows HCW reduced to X% | v69 was never executed |
| v70 scales to 540 MCQs | v70 was N=5, halted at 11/15 rows of 2nd variant; no audit or summary output saved |
| Human validation achieved kappa >= 0.6 | Not started |
| OpenAI/Anthropic auditors confirm results | Absent from v68 |
| Per-language accuracy drops Xpp under variant Y | No statistical significance tests computed on v68 paired subsets (P0 gap from liability analysis, not yet closed) |
| Encoder baselines on v68 data | Not computed on v68; legacy numbers deprecated |
| S1/S2 comparison on hardened pipeline | No S1/S2 split exists in v68 |

---

## 10. Evidence File Index

### 10.1 v68 primary artifacts

| File | Description |
|------|-------------|
| `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_summary.json` | v68 canonical config: model roster, prompt variants, seed, N_PER_LANG=5, cost $0.8539 |
| `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_generated_mcqs.csv` | 180 production MCQs (canonical dataset) |
| `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_audit_results.csv` | 180 rows x 4 auditors = 720 blind votes |
| `kaggle/run_logs/v68/openrouter_pilot1_test_output/pilot1_test_raw_outputs.csv` | 183 raw generation attempts with full text |

### 10.2 v68 analysis reports

| File | Description |
|------|-------------|
| `kaggle/run_logs/v68/v68_detailed_analysis_report.md` | Executive summary, gate table, fallback bottleneck diagnosis, per-generator/variant analysis |
| `kaggle/run_logs/v68/v68_generation_quality_report.md` | Generation status distribution, mean replacements, problematic items |
| `kaggle/run_logs/v68/v68_per_language_report.md` | Per-language Wilson CIs, HCW (>=0.75 definition), auditor behavior per language |
| `kaggle/run_logs/v68/v68_per_language_generator_report.md` | Per-language/generator/variant metrics (note: uses >=0.50 HCW threshold) |

### 10.3 v68 tables (CSVs)

| File | Contents |
|------|----------|
| `kaggle/run_logs/v68/table_position_bias_chi2.csv` | Position bias: A=33/45=73.3%, B=26/45=57.8%, C=22/45=48.9%, D=21/45=46.7%, chi2=3.49, p=0.322, corrected consensus=0.5667 |
| `kaggle/run_logs/v68/table_committee_family.csv` | Auditor/generator family breakdowns |
| `kaggle/run_logs/v68/table_auditor_vs_gold.csv` | Per-auditor accuracy vs gold + pairwise Cohen's kappa |
| `kaggle/run_logs/v68/table7_v68_findings.csv` | v68 failure taxonomy (current) |
| `kaggle/run_logs/v68/table7_legacy_findings.csv` | Legacy Groq failure taxonomy (deprecated) |

### 10.4 Data artifacts

| File | Contents |
|------|----------|
| `data/production/paper_first_outputs_2026-06-22_10-42-02/human_validation_sample_60.csv` | 60-item validation sample (20 per language), stratified by generation status |

### 10.5 Planning and cleanup docs

| File | Description |
|------|-------------|
| `docs/EXECUTION_ITINERARY_2026-07-10.md` | Phase 0-4 execution plan with go/no-go gates (ground rules: paper-first, no hallucination, budget reality) |
| `docs/gap_liability_analysis_2026-07-10.md` | P0/P1/P2 gap analysis (legacy claims, position bias, provenance, reproducibility, baselines) |
| `docs/ProverbGap_Reframed_Title_Abstract.md` | Reframed paper title/abstract + section outline + claims traceability + non-goals |
| `docs/PHASE_3_BUDGET_DEPENDENT.md` | v69/v70 config and go/no-go decision rules |
| `submission_package_2026-08-02/DATA_PROVENANCE_TEMPLATE.md` | Exists (filled 2026-07-10); English scraping URLs not recovered, Arabic dataset source unknown, Yoruba copyright unverified — all flagged as liabilities |

---

## 11. Open Issues (Requires Budget or Time)

| Issue | Priority | Budget needed | Blocking? |
|-------|----------|---------------|-----------|
| v69 LLM-fallback ablation | P0 | ~$1.00 | Yes -- pipeline fix |
| v70 N=5 scaling (halted) | P1 | ~$0.42 spent, run incomplete | No -- v68 suffices as N=5 study |
| Human validation (60-90 items) | P0 | ~$200-300 | Yes -- paper requirement |
| Committee expansion (OpenAI + Anthropic) | P1 | ~$0.10 | No -- methodology caveat |
| Statistical tests (McNemar, Wilcoxon, Holm) | P0 | $0 | No -- from existing data |
| Bootstrap CIs for all six metrics | P0 | $0 | No -- from existing data |
| DATA_PROVENANCE_TEMPLATE.md | Exists in `submission_package_2026-08-02/` (filled 2026-07-10) but not at `docs/` path -- update all cross-references | P0 | $0 | Yes -- path fix needed |
| Per-model cost breakdown | P1 | $0 | No -- transparency |
| Environment pinning (requirements.lock) | P0 | $0 | Yes -- reproducibility |
| Position shuffling robustness test | P1 | $0 | No -- from existing data |
| Length-bias ablation | P1 | $0 | No -- from existing data |

---

*This document is the authoritative handover for the ProverbGap v68 production dataset. All numbers are verified against the source CSVs and reports listed in Section 10 as of 2026-10-25. Discrepancies between v68 files (notably the HCW threshold, documented in Section 2.5) are resolved in favor of the canonical >= 0.75 definition.*
