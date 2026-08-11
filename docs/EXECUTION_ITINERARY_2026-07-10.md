# ProverbGap EACL 2027 ARR — Execution Itinerary
**Target deadline:** August 3, 2026 (ARR submission)  
**Today:** July 10, 2026  
**Days remaining:** 24  
**Current state:** v68 production dataset (180 MCQs), budget exhausted, v69/v70 blocked, no human annotation.

---

## Ground Rules (Read Before Starting)

1. **No endless loops.** Every phase has a hard stop date and a go/no-go gate.
2. **No hallucination.** Every claim in the paper must map to an existing CSV/JSON/PNG in `kaggle/run_logs/v68/` or a newly generated artifact with a recorded command.
3. **Budget reality.** OpenRouter credits are exhausted (`403 Budget limit exceeded`). Anything requiring API calls is **Phase 3 only** and will not start until budget is confirmed renewed.
4. **Human validation is NOT in this itinerary.** It is listed as planned future work only. Do not spend time recruiting annotators.
5. **Paper-first over data-first.** We submit with v68 N=5 (180 MCQs) if v69/v70 cannot run. The contribution is methodology + failure taxonomy, not benchmark size.
6. **All P0 gaps from `docs/gap_liability_analysis_2026-07-10.md` must be closed before submission.**

---

## Phase 0: Paper Integrity & P0 Gap Closure
**Duration:** Days 1–3 (July 10–12)  
**Budget required:** $0  
**Go/No-go gate at end of Day 3:** Every item below is verified by file existence and content check.

### Day 1 (July 10): Abstract & Legacy Claim Cleanup

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 0.1 | Rewrite abstract in `docs/ProverbGap_Reframed_Title_Abstract.md` | Edit file: replace `2,313 MCQs` with `180 MCQs`; remove `86.8% vs 62.5%` S1/S2 numbers; remove encoder baseline claim; remove cross-lingual boundary `8.9pp / 2.2pp` claim; remove Allam-2-7b and CoT collapse numbers (legacy Groq). | Abstract states: 180 MCQs, 3 languages, v68 hardened pipeline, corpus-fallback bottleneck, position bias, HCW 27.8%, partial+fallback 43.9%. | `grep -c "2,313" docs/ProverbGap_Reframed_Title_Abstract.md` == 0; `grep -c "180" docs/ProverbGap_Reframed_Title_Abstract.md` >= 1. |
| 0.2 | Update section outline table in same file | Remove S1/S2 columns; replace with current 4-variant × 3-language structure. Remove encoder baseline row from Table 4. | Section 4 and 5 tables reference only v68 data. | Manual diff of `docs/ProverbGap_Reframed_Title_Abstract.md`. |
| 0.3 | Split `table7_failure_taxonomy.csv` | Create `table7_legacy_findings.csv` (same-family 31.1pp, CoT 34.7pp, MSP 100%, position 60.6pp, API 90%) with source column = `legacy_groq_pilot2`. Create `table7_v68_findings.csv` (corpus fallback 43.9%, HCW 27.8%, partial+fallback 43.9%). | Two CSV files in `kaggle/run_logs/v68/`. | `ls kaggle/run_logs/v68/table7*.csv`. |
| 0.4 | Audit the reframed abstract for unsupported claims | Read line by line; every number must map to a v68 CSV. Flag any that do not. | List of approved/disapproved claims. | Manual checklist. |

**End-of-day checkpoint:** Abstract has zero legacy numbers. `table7` is split. No S1/S2 language remains.

---

### Day 2 (July 11): Statistical Rigor & Data Provenance

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 0.5 | Add McNemar + Wilcoxon + Holm-Bonferroni to paper-first notebook | Run `python -c "from scipy.stats import wilcoxon, mcnemar; ..."` on the 4-variant paired subsets. Save results to `kaggle/run_logs/v68/statistical_tests.csv`. | CSV with test name, variant pair, statistic, p-value, holm-corrected p, significant flag. | File exists; p-values are numeric (not NaN) for all 6 variant pairs. |
| 0.6 | Add bootstrap CIs for ALL metrics | Extend existing bootstrap script to cover: perfect_consensus_rate, hcw_rate, partial_or_fallback_rate, hard_fallback_rate, per-language accuracy. Save to `table_bootstrap_cis.csv`. | CSV with metric, point estimate, lower, upper, N. | `wc -l` >= 20 rows. |
| 0.7 | Compute per-auditor accuracy vs. gold | Script: for each auditor model, compute fraction matching `curated_meaning`. Save to `table_auditor_vs_gold.csv`. | CSV: auditor, hit_rate_vs_gold, wilson_ci. | File exists; 4 rows. |
| 0.8 | Fill `DATA_PROVENANCE_TEMPLATE.md` | Populate English source URLs, Arabic source dataset name and license, Yoruba copyright status (Owomoyela 2005 UNP, no redistribution permission). | Completed template. | No blank `[TBD]` fields remain. |
| 0.9 | Add Yoruba copyright decision | Decision: **scope paper to English + Arabic only for data release**. Yoruba MCQs remain in the analysis but are excluded from the public dataset release. Document in `DATA_PROVENANCE_TEMPLATE.md` and paper Discussion. | One-sentence decision logged. | Manual check. |

**End-of-day checkpoint:** `statistical_tests.csv` and `table_bootstrap_cis.csv` exist. `DATA_PROVENANCE_TEMPLATE.md` is complete. Yoruba release decision is recorded.

---

### Day 3 (July 12): Audit Committee & Bias Fixes

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 0.10 | Compute position-bias chi-square on committee | Script: for each position A/B/C/D, count consensus-correct vs. consensus-wrong. Run chi-square. Save to `table_position_bias_chi2.csv`. | CSV: position, correct, wrong, total, accuracy, expected, chi2_contrib. | File exists; chi2 statistic > 10 (significant). |
| 0.11 | Add position-corrected consensus metric | Define `consensus_accuracy_position_corrected = mean(accuracy_by_position)` weighted equally across A/B/C/D (not by key count). Compare to raw consensus accuracy. Save to `table_position_corrected_metrics.csv`. | CSV: metric, raw, corrected, delta. | File exists; delta != 0. |
| 0.12 | Verify position shuffling code is active | Read `openrouter_pilot_distractor_generation_test_nano_opus.py` for `shuffle_positions` or equivalent in `assemble_mcq()`. If inactive, activate it. | Code diff showing shuffling enabled. | `grep -n "shuffle" openrouter_pilot_distractor_generation_test_nano_opus.py` returns >= 1 match in assembly function. |
| 0.13 | Add committee family diversity analysis | Script: map each auditor to family (Meta, Mistral, Google, DeepSeek). Compute per-family accuracy vs. gold. Save to `table_committee_family.csv`. | CSV: family, model, accuracy_vs_gold. | File exists; 4 rows. |

**End-of-day checkpoint (GATE):** All P0 items from `gap_liability_analysis_2026-07-10.md` marked completed. Run final grep check:

```bash
# These must all return 0 matches in the paper source:
grep -rn "2,313" docs/ kaggle/run_logs/v68/
grep -rn "S1.*86.8" docs/ kaggle/run_logs/v68/
grep -rn "encoder.*baseline" docs/ kaggle/run_logs/v68/ | grep -v "table_encoder"
grep -rn "8\.9pp" docs/ kaggle/run_logs/v68/
```

If any grep returns a match, do not proceed to Phase 1 until fixed.

---

## Phase 1: Baselines & Robustness Metrics (No Budget Needed)
**Duration:** Days 4–7 (July 13–16)  
**Budget required:** $0  
**Go/No-go gate:** All tables exist and populate the paper section draft.

### Day 4 (July 13): Heuristic Baselines

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 1.1 | Generate all-A / all-D / random baselines | For each of the 180 MCQs in `generated_mcqs.csv`, compute: (a) accuracy if always picking A, (b) always D, (c) random 25%. Save to `table_heuristic_baselines.csv`. | CSV with 3 rows + overall. | File exists; values in [0,1]. |
| 1.2 | Generate length-matched corpus baseline | For each MCQ, compute mean option length. Sample 1,000 random option-length-matched distractors from the full corpus. Compute accuracy. Save to `table_length_matched_baseline.csv`. | CSV: baseline_type, accuracy, ci_lower, ci_upper. | File exists. |
| 1.3 | Single-generator ablation using existing v68 data | Extract MCQs generated by `google/gemma-4-31b-it` only (the strongest generator). Compute accuracy, HCW, partial+fallback for that subset. Compare to pooled. Save to `table_single_generator_ablation.csv`. | CSV: generator, accuracy, hcw, partial_fallback, N. | File exists; 1 row for gemma pooled. |

### Day 5 (July 14): Length Bias & Shuffling Robustness

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 1.4 | Length-bias analysis | Script: for each MCQ, compute mean length of all 4 options. Correlate length with consensus-correct vs. consensus-wrong. Save to `table_length_bias.csv`. | CSV: length_bin, correct_rate, wrong_rate, n. | File exists; at least 4 bins. |
| 1.5 | Shuffling robustness test | Pick 20 MCQs stratified by language. For each, generate 10 random shuffles of A/B/C/D. Compute accuracy per shuffle. Record flip rate (how often correct label changes position). Save to `table_shuffling_robustness.csv`. | CSV: mcq_id, shuffle_i, accuracy, correct_position. | File exists; 200 rows (20 × 10). |

### Day 6 (July 15): Cost & Environment Pinning

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 1.6 | Per-model cost breakdown | Read `pilot1_test_summary.json` cost fields. Compute cost per model per phase. Save to `table_cost_by_model.csv`. | CSV: model, prompt_cost, completion_cost, total_calls, total_cost_usd. | File exists; sum matches $0.85. |
| 1.7 | Per-language and per-variant cost | Cross-tab cost by language and variant. Save to `table_cost_by_language_variant.csv`. | CSV: language, variant, cost. | File exists; 12 rows. |
| 1.8 | Generate requirements.lock | Run `pip freeze > requirements.lock` in the project venv (or Kaggle runner packages). Save to `reproducibility/requirements.lock`. | Lockfile with pinned versions. | File exists; `wc -l` > 10. |
| 1.9 | Snapshot OpenRouter model catalog | Read `/models` response from v68 run logs (if saved) or document model IDs + pricing in `reproducibility/openrouter_catalog_snapshot_2026-06-22.json`. | JSON with model IDs and prices. | File exists. |

### Day 7 (July 16): Reproducibility Package & Phase 1 Gate

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 1.10 | Create `REPRODUCIBILITY_CHECKLIST.md` | List: seed, model IDs, cost, output hashes, commands to run. | Markdown checklist. | File exists. |
| 1.11 | Compute SHA256 hashes of all v68 output CSVs | `sha256sum kaggle/run_logs/v68/openrouter_pilot1_test_output/*.csv > reproducibility/v68_output_hashes.txt` | Hashes file. | File exists; at least 5 hashes. |
| 1.12 | Phase 1 gate review | Verify all deliverables in `docs/phase1_gate_check.md`. If any missing, do not proceed to Phase 2. | Gate checklist. | All checks pass. |

---

## Phase 2: Paper Drafting (No Budget Needed)
**Duration:** Days 8–16 (July 17–25)  
**Budget required:** $0  
**Go/No-go gate:** Complete LaTeX/Markdown draft with all tables and figures.

### Days 8–10 (July 17–19): Sections 1–3 (Introduction, Related Work, Methodology)

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 2.1 | Draft Introduction (Section 1) | Write 1.5 pages: gap, contribution, scope. Use reframed outline. Use `paper_first_analysis_2026-06-22_10-42-02.ipynb` for context. | `paper/sections/01_introduction.md` | File exists; `wc -w` >= 500. |
| 2.2 | Draft Related Work (Section 2) | Write 1.5–2 pages: proverb benchmarks, distractor generation, LLM-as-judge, shortcut learning, low-resource eval. Insert Table 1 (benchmark comparison). | `paper/sections/02_related_work.md` | File exists. |
| 2.3 | Draft Methodology (Section 3) | Write 3 pages: pipeline overview, generator pool, prompt variants, dual-gate validation, fallback sampler, blind audit committee, reproducibility. Insert Figure 1 (pipeline diagram) and Table 2 (prompt thresholds). | `paper/sections/03_methodology.md` | File exists. |
| 2.4 | Generate Figure 1 (pipeline diagram) | Use Mermaid or draw.io. Export PNG. Save to `paper/figures/fig1_pipeline.png`. | PNG, 300 dpi min. | File exists; width >= 1200px. |

### Days 11–13 (July 20–22): Sections 4–5 (Dataset, Experiments, Results)

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 2.5 | Draft Dataset & Experiments (Sections 4–5) | Write using `table3_dataset_stats.csv`, `table4_committee.csv`, `table_heuristic_baselines.csv`, `table_single_generator_ablation.csv`, `table_encoder_baselines.csv` (if re-run; otherwise remove from outline). | `paper/sections/04_dataset_experiments.md` | File exists. |
| 2.6 | Draft Results (Section 5 continued) | Write using `kaggle/run_logs/v68/v68_detailed_analysis_report.md`, `table_bootstrap_cis.csv`, `statistical_tests.csv`, `table_position_bias_chi2.csv`, `table_position_corrected_metrics.csv`. Insert Figure 2 (per-language accuracy), Figure 3 (position bias violin), Figure 4 (HCW by variant), Figure 5 (cost frontier). | `paper/sections/05_results.md` | File exists. |
| 2.7 | Generate figures 2–5 | Use matplotlib/seaborn from existing CSVs. Save PNGs. | 4 PNG files. | Files exist. |

### Days 14–15 (July 23–24): Sections 6–8 (Failure Taxonomy, Discussion, Conclusion)

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 2.8 | Draft Failure Taxonomy (Section 6) | Write using `table7_v68_findings.csv` and legacy notes from `table7_legacy_findings.csv`. Insert Table 5. | `paper/sections/06_failure_taxonomy.md` | File exists. |
| 2.9 | Draft Discussion + Limitations + Conclusion (Sections 8–9) | Write 1.5 pages: interpretation of corpus fallback bottleneck, cross-lingual boundary, limitations (N=5, no human validation, API dependency), ethics/bias, future work. | `paper/sections/08_discussion.md`, `09_conclusion.md` | Files exist. |
| 2.10 | Draft Human Validation Plan (Section 7) | Write 1 page: sample, annotators, tasks, agreement metric, budget, timeline. **Do not claim validation is complete.** | `paper/sections/07_human_validation_plan.md` | File exists. |

### Day 16 (July 25): Assemble Full Draft & Phase 2 Gate

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 2.11 | Merge sections into single paper | Concatenate sections with LaTeX/Markdown headers. Save to `paper/proverbgap_eacl2027.md`. | Full draft. | File exists; `wc -w` >= 5000. |
| 2.12 | Figure/table cross-check | Every `\ref{}` or `[Figure X]` must point to an existing file. Run script to verify. | Cross-check report. | Zero missing references. |
| 2.13 | Abstract-body consistency check | Every number in the abstract must appear verbatim in the body tables. Script: extract numbers from abstract, grep in body. | Consistency report. | Zero unmatched numbers. |

**End-of-day checkpoint (GATE):** Full paper draft exists. All figures and tables are present. Every abstract number maps to a table. If not, return to relevant day above.

---

## Phase 3: Budget-Dependent Runs (v69 + v70)
**Duration:** Days 17–24 (July 26–August 1)  
**Budget required:** OpenRouter renewed (~$2–$4 estimated)  
**Go/No-go gate:** Budget confirmation received before any command runs.

### Decision Rule for Phase 3

```
IF OpenRouter budget is renewed by July 26:
    Run v69 (USE_LLM_FALLBACK=True, N=5)
    IF v69 passes gates (HCW < 15%, partial+fallback < 30%):
        Run v70 (USE_LLM_FALLBACK=True, N=15)
        Replace v68 numbers in paper with v70 numbers
    ELSE:
        Keep v68 as primary; add v69 as robustness check
ELSE:
    Submit with v68 N=5 as production dataset
    Frame paper explicitly as N=5 methodology study
```

### Day 17 (July 26): Budget Check & v69 Prep

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 3.1 | Confirm budget renewal | Check OpenRouter dashboard or ask user. Record status in `docs/budget_status.md`. | Status file: RENEWED or EXHAUSTED. | File content. |
| 3.2 | If renewed: configure v69 | Edit `openrouter_pilot_distractor_generation_test_nano_opus.py`: set `USE_LLM_FALLBACK = True`, `FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"`, `N_PER_LANG = 5`. | Config diff saved. | `grep` confirms settings. |
| 3.3 | If renewed: regenerate notebook | Run `python convert_test_nano_opus_to_notebook.py`. | Updated `.ipynb`. | File timestamp updated. |
| 3.4 | If renewed: push to Kaggle | Run `python trigger_kaggle_run.py` or equivalent. | Kaggle run started. | Kaggle API response shows run_in_progress. |

### Days 18–19 (July 27–28): v69 Execution & Analysis

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 3.5 | Monitor v69 run | Check Kaggle every 4 hours. If run fails, capture error. | Run completion or failure log. | Output files downloaded. |
| 3.6 | If v69 succeeds: download outputs | `kaggle datasets download -r <run_id> -p kaggle/run_logs/v69/`. | Output directory with CSVs. | `ls kaggle/run_logs/v69/` shows expected files. |
| 3.7 | If v69 succeeds: run analysis | Execute `kaggle/run_logs/v68/v68_detailed_analysis_report.md` logic against v69 data. Save to `v69_detailed_analysis_report.md`. | Analysis report. | File exists; HCW and partial+fallback rates listed. |
| 3.8 | v69 gate check | Compare v69 metrics to targets: HCW < 15%, partial+fallback < 30%, cost < $1.50. | Gate report: PASS or FAIL. | Explicit PASS/FAIL text in file. |

### Days 20–22 (July 29–31): v70 Execution (if v69 passes)

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 3.9 | If v69 passes: configure v70 | Edit config: `N_PER_LANG = 15`, keep `USE_LLM_FALLBACK = True`. | Config diff. | `grep` confirms N=15. |
| 3.10 | If v69 passes: regenerate, push, run Kaggle v70 | Same as 3.3–3.5. | Kaggle run started. | API response. |
| 3.11 | Monitor and download v70 | Same monitoring cadence. Download to `kaggle/run_logs/v70/`. | Output files. | `ls` shows files. |
| 3.12 | v70 analysis | Generate v70 detailed analysis report. | `v70_detailed_analysis_report.md`. | File exists. |

### Days 23–24 (August 1–2): Final Numbers & Paper Update

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 3.13 | Determine production dataset | If v70 passed: use v70. If v69 passed but v70 failed/blocked: use v69. If neither: use v68. Record in `docs/production_dataset_decision.md`. | Decision file with rationale. | File exists. |
| 3.14 | Regenerate all paper tables from production dataset | Run paper-first notebook or custom scripts on production CSV. Overwrite tables in `paper/tables/`. | Fresh table files. | Timestamps >= Day 23. |
| 3.15 | Update paper draft with final numbers | Replace all `XX%` placeholders in `paper/proverbgap_eacl2027.md` with production numbers. | Updated paper draft. | `grep -c "XX%" paper/proverbgap_eacl2027.md` == 0. |
| 3.16 | Final consistency check | Run grep checks from Day 3 again on the updated paper. | Zero-legacy-numbers report. | All greps return 0. |

---

## Phase 4: Submission Package & Final Polish
**Duration:** Days 23–24 (August 1–2)  
**Budget required:** $0  
**Go/No-go gate:** Package ready for upload.

| # | Task | Command / Action | Deliverable | Verification |
|---|------|------------------|-------------|--------------|
| 4.1 | Create submission directory | `mkdir -p submission_package_2026-08-02/`. | Directory. | `ls` shows dir. |
| 4.2 | Copy final artifacts | Paper draft, all tables, all figures, reproducibility checklist, hashes, data license statement. | Packaged files. | `ls` shows >= 15 files. |
| 4.3 | Write README for submission package | Explain what is included, what is excluded (Yoruba raw corpus), how to reproduce. | `submission_package_2026-08-02/README.md`. | File exists. |
| 4.4 | ZIP package | `zip -r submission_package_2026-08-02.zip submission_package_2026-08-02/`. | ZIP file. | File exists; size > 100KB. |
| 4.5 | Final reviewer-risk checklist | Run through `docs/gap_liability_analysis_2026-07-10.md` Section "Prioritized Fix List" and mark each P0/P1 as FIXED or PLANNED. Save to `submission_package_2026-08-02/reviewer_risk_checklist.md`. | Checklist. | All P0 items = FIXED. |

---

## Parallel Track: Literature Alignment (Ongoing Days 1–16)
**Budget required:** $0  
**Owner:** Concurrent with main track; do not block Phase 0–2.

| Day | Task |
|-----|------|
| 1–3 | Read and annotate 10 recent papers from the literature review output: ProverbEval (NAACL 2025), JAWAHER (NAACL 2025), MasalBench (2026), DiVERT (EMNLP 2024), Balepur & Rudinger (ACL 2025), BRIGHTER (ACL 2025), GradQuiz (ACM 2026), Kang et al. (ACL 2025), Alhazmi et al. (EMNLP 2025 Findings), MMLU-ProX (EMNLP 2025). Extract: their dataset size, whether they use human validation, their shortcut-resistance methods, their failure analysis depth. |
| 4–6 | Write Related Work section draft (Section 2) incorporating these papers. Explicitly position ProverbGap against: (a) ProverbEval for cross-lingual coverage gap, (b) DiVERT for distractor quality, (c) Balepur & Rudinger for shortcut audit methodology, (d) BRIGHTER for human annotation standards. |
| 7–10 | Identify 2–3 papers that reviewers will cite against us (e.g., "ProverbEval has 6 languages and human validation, why don't you?"). Write preemptive rebuttal paragraphs in Discussion/Limitations. |
| 11–16 | Update Related Work and Discussion with any new citations found during paper drafting. |

---

## Decision Gates Summary

| Gate | When | Criteria to proceed | If failed |
|------|------|---------------------|-----------|
| **Phase 0 Gate** | Day 3 end | Zero legacy numbers in paper source; `table7` split; `DATA_PROVENANCE_TEMPLATE.md` complete; statistical tests generated. | Fix failing items; do not write paper until clean. |
| **Phase 1 Gate** | Day 7 end | All baseline, bias, cost, and reproducibility files exist and populate the paper draft. | Extend Phase 1 by 1–2 days; do not skip. |
| **Phase 2 Gate** | Day 16 end | Full paper draft assembled; all figures/tables present; abstract-body consistency verified. | Return to missing section day. |
| **Phase 3 Gate** | Day 24 end | Production dataset selected; paper updated with final numbers; submission package zipped. | If budget not renewed, submit with v68 and explicit N=5 framing. |

---

## Failure Modes & Explicit Exits

| Failure mode | Exit condition | Action |
|-------------|---------------|--------|
| Endless prompt tuning on abstract | Abstract rewrite takes > 4 hours | Write the ugly version first; refine in Phase 2. |
| Legacy data contamination | Cannot trace a number to a CSV | **Delete the number.** Do not keep it "just in case." |
| Budget not renewed by Day 17 | No API access confirmed | Skip Phase 3 entirely. Submit v68 paper on Day 24. |
| v69/v70 fail or time out | Run crashes or exceeds 48h | Use best available dataset (v68 preferred; v69 if partial). Do not wait for re-run. |
| Statistical tests too complex | scipy/mcnemar unavailable | Fall back to bootstrap CIs + non-parametric rank sums. Do not block paper on one test. |
| Figure generation stalls | matplotlib/seaborn broken | Use ASCII tables or CSV references. Figures are supplementary; text claims are primary. |
| Scope creep (adding S1/S2, human validation, encoder baselines) | Any task not in this itinerary | **Drop it.** It is future work. |

---

## Artifact Inventory (By End of Phase 2)

```
docs/
  ProverbGap_Reframed_Title_Abstract.md          (rewritten)
  gap_liability_analysis_2026-07-10.md           (original, reference only)
  phase1_gate_check.md                            (new)
  budget_status.md                                (new)
  production_dataset_decision.md                  (new)

kaggle/run_logs/v68/
  v68_detailed_analysis_report.md
  v68_generation_quality_report.md
  v68_per_language_report.md
  v68_per_language_generator_report.md
  table7_legacy_findings.csv                     (new)
  table7_v68_findings.csv                        (new)
  statistical_tests.csv                          (new)
  table_bootstrap_cis.csv                        (new)
  table_auditor_vs_gold.csv                      (new)
  table_position_bias_chi2.csv                   (new)
  table_position_corrected_metrics.csv           (new)
  table_heuristic_baselines.csv                  (new)
  table_length_matched_baseline.csv              (new)
  table_single_generator_ablation.csv            (new)
  table_length_bias.csv                          (new)
  table_shuffling_robustness.csv                 (new)
  table_cost_by_model.csv                        (new)
  table_cost_by_language_variant.csv             (new)
  table_committee_family.csv                     (new)

kaggle/run_logs/v69/                               (populated if budget renewed)
kaggle/run_logs/v70/                               (populated if budget renewed)

reproducibility/
  requirements.lock
  openrouter_catalog_snapshot_2026-06-22.json
  v68_output_hashes.txt
  REPRODUCIBILITY_CHECKLIST.md

paper/
  proverbgap_eacl2027.md                          (full draft)
  sections/
    01_introduction.md
    02_related_work.md
    03_methodology.md
    04_dataset_experiments.md
    05_results.md
    06_failure_taxonomy.md
    07_human_validation_plan.md
    08_discussion.md
    09_conclusion.md
  figures/
    fig1_pipeline.png
    fig2_per_language_accuracy.png
    fig3_position_bias_violin.png
    fig4_hcw_by_variant.png
    fig5_cost_frontier.png
  tables/
    table1_benchmark_comparison.csv
    table2_prompt_variants.csv
    table3_dataset_stats.csv
    table4_committee.csv
    table5_failure_taxonomy.csv
    table6_distractor_quality.csv
    table7_legacy_findings.csv
    table7_v68_findings.csv
    table_bootstrap_cis.csv
    table_position_bias_chi2.csv
    [... all other tables ...]

submission_package_2026-08-02/
  proverbgap_eacl2027.md
  README.md
  reviewer_risk_checklist.md
  reproducibility/
  tables/
  figures/
  submission_package_2026-08-02.zip
```

---

## Explicit Non-Goals (Do Not Start These)

1. **Human annotator recruitment.** Blocked by time/budget. Mentioned only as planned future work.
2. **Encoder baseline re-execution.** If not already in v68 outputs, remove from paper. Do not waste days running them.
3. **S1/S2 legacy re-execution.** The legacy numbers are dropped from the paper. Do not attempt to recreate them.
4. **Endless prompt tuning.** v68 config is frozen. Do not change prompts, thresholds, or model pools during this itinerary.
5. **New Kaggle kernel versions.** Do not push v71/v72. The only allowed pushes are v69 and v70 if budget is renewed.

---

*Itinerary written: 2026-07-10. Execute sequentially. Phase 0 → Phase 1 → Phase 2 → Phase 3 (budget-dependent). Do not skip gates.*
