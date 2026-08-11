# v69 Post-Download Analysis Checklist

Run this checklist immediately after the v69 Kaggle output folder is copied to
`kaggle_run_logs/v69/openrouter_pilot1_test_output/`.

---

## 1. File integrity

- [ ] `kaggle_run_logs/v69/openrouter_pilot1_test_output/` exists.
- [ ] `pilot1_test_generated_mcqs.csv` is present and non-empty.
- [ ] `pilot1_test_audit_results.csv` is present and non-empty.
- [ ] `pilot1_test_summary.json` is present and parseable.
- [ ] `pilot1_test_raw_outputs.csv` is present (for forensic deep dives).
- [ ] `pool_state.json` is present (for generator/auditor substitution log).
- [ ] Expected PNG figures were produced (if the notebook generated them).
- [ ] File sizes look reasonable (MCQ CSV ~> 50 KB, audit CSV ~> 30 KB for N=5).

## 2. Run metadata (from `pilot1_test_summary.json`)

- [ ] `n_per_language` == 5.
- [ ] `seed` == 20260615 (matches v68 for paired comparison).
- [ ] `USE_LLM_FALLBACK` is `True` (verify by inspecting raw outputs or config if serialized).
- [ ] Active generator count >= 3.
- [ ] Active auditor count >= 4.
- [ ] Generator/auditor substitutions are documented; no unexpected model dropouts.
- [ ] `estimated_cost_usd` is recorded and < $1.50.

## 3. Aggregate metrics to compute

Run `python kaggle_run_logs/v69/compare_v68_v69.py` and verify these outputs:

- [ ] `v68_v69_comparison_table.csv`
- [ ] `v68_v69_per_language.csv`
- [ ] `v68_v69_per_variant.csv`
- [ ] `v68_v69_per_generator.csv`
- [ ] `v68_v69_paired_metrics.csv`
- [ ] `v68_v69_statistical_tests.csv`
- [ ] `fig_v68_v69_metric_bars.png`
- [ ] `fig_v68_v69_paired_scatter.png`
- [ ] `fig_v68_v69_delta_by_language.png`
- [ ] `v68_v69_comparison_report.md`

Then fill in the following table from the report:

| Metric | v68 (corpus) | v69 (LLM fallback) | Delta | Target |
|---|---|---|---|---|
| Total MCQs | 180 | TBD | — | 180 |
| Cost (USD) | $0.8539 | TBD | — | <$1.50 |
| Perfect consensus rate | 41.7% | TBD | — | <30% |
| HCW rate | 27.8% | TBD | — | <10% (strong), <15% (marginal) |
| Consensus accuracy | 56.7% | TBD | — | ≥50% |
| Partial + fallback rate | 43.9% | TBD | — | <15% (strong), <30% (marginal) |
| Hard fallback (`length_fallback`) rate | 16.1% | TBD | — | <5% |
| Mean fallback count | 0.99 | TBD | — | decrease |
| Mean NLI replacements | 0.36 | TBD | — | — |
| Mean leak replacements | 0.35 | TBD | — | — |
| Mean length replacements | 0.15 | TBD | — | — |
| Duplicate options | 0 | TBD | — | 0 |
| Correct-key balance (A/B/C/D) | 45/45/45/45 | TBD | — | ~25% each |

## 4. Per-language consensus correctness (with Wilson 95% CI)

Compute or copy from `v68_v69_per_language.csv` and the detailed script:

| Language | Correct / Total | Accuracy | Wilson 95% CI | Pass ≥50%? |
|---|---|---|---|---|
| English | TBD | TBD | TBD | TBD |
| Arabic | TBD | TBD | TBD | TBD |
| Yoruba | TBD | TBD | TBD | TBD |

## 5. Per-language HCW and perfect consensus

| Language | Perfect consensus | HCW (≥75% vote, wrong) | Non-perfect consensus |
|---|---|---|---|
| English | TBD | TBD | TBD |
| Arabic | TBD | TBD | TBD |
| Yoruba | TBD | TBD | TBD |

## 6. Generation-status distribution

From `pilot1_test_generated_mcqs.csv`:

| Status | Count | Percentage |
|---|---|---|
| `generated` | TBD | TBD |
| `partial` | TBD | TBD |
| `length_fallback` | TBD | TBD |
| `parse_fallback` | TBD | TBD |
| `hard_fallback` | TBD | TBD |

## 7. LLM fallback-specific diagnostics

- [ ] Count of `llm_fallback_used` calls (if recorded in summary or raw outputs).
- [ ] Count of `llm_fallback_rejected` calls (if recorded).
- [ ] Mean cost per LLM fallback call (from `cost_history` purpose == `llm_fallback` or similar).
- [ ] Compare fallback distractor quality: HCW rate split by `fallback_count == 0` vs `fallback_count > 0`.
- [ ] Compare HCW rate split by `generation_status == "generated"` vs `"partial"` vs `"length_fallback"`.

## 8. Paired statistical tests (v69 vs v68)

From `v68_v69_statistical_tests.csv`, verify these outcomes are present:

- [ ] McNemar: consensus correct.
- [ ] McNemar: HCW.
- [ ] McNemar: perfect consensus.
- [ ] McNemar: partial or fallback.
- [ ] McNemar: any fallback.
- [ ] Wilcoxon + bootstrap CI: fallback count.
- [ ] Wilcoxon + bootstrap CI: NLI replacements.
- [ ] Wilcoxon + bootstrap CI: leak replacements.
- [ ] Wilcoxon + bootstrap CI: length replacements.

## 9. Per-variant and per-generator forensic checks

- [ ] Identify which variant has highest HCW.
- [ ] Identify which variant has highest partial+fallback.
- [ ] Identify which generator has highest HCW.
- [ ] Identify which generator has highest `length_fallback` rate.
- [ ] Flag any generator that was benched or substituted.

## 10. Go / no-go decision

Use the thresholds below and record the decision in `v69_detailed_analysis_report.md`.

### Thresholds

| Tier | HCW | Partial + fallback | Cost | Decision |
|---|---|---|---|---|
| **Strong pass** | <10% | <15% | <$1.50 | Scale to N=15 (v70). |
| **Marginal** | 10–15% | 15–30% | <$1.50 | Scale to N=15 with caveats OR run one more focused ablation. |
| **Fail** | ≥15% | ≥30% | ≥$1.50 | Pivot to paper-first. Do not scale. |

### Decision record

- [ ] HCW: __________%
- [ ] Partial + fallback: __________%
- [ ] Cost: $__________
- [ ] Decision: ☐ STRONG PASS  ☐ MARGINAL  ☐ FAIL
- [ ] Justification: ___________________________________________________

## 11. Next actions

- [ ] If STRONG PASS: freeze v69 config, queue v70 N=15 run, prepare human-validation sampling plan.
- [ ] If MARGINAL: draft caveat list, decide on final ablation, update AGENTS.md and paper outline.
- [ ] If FAIL: finalize v68/v69 dataset as paper evidence, begin 60-item human validation, start paper drafting.
- [ ] Update `AGENTS.md` with the v69 decision and updated status.
