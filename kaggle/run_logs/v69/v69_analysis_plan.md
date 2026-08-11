# v69 Statistical Analysis Plan — ProverbGap MCQ

**Prepared for:** v69 Kaggle run (LLM fallback ablation)  
**Baseline:** v68 N=5 corpus-fallback run  
**Comparison design:** Same seed (20260615), same 15 proverbs, same 4 variants, same 3 active generators, same 4 auditors.

---

## 1. Goal

Decide, within 30 minutes of downloading v69 outputs, whether to:

1. **Scale** the LLM-fallback config to N=15 (v70).
2. **Scale with caveats** or run one more focused ablation.
3. **Pivot to paper-first** and stop scaling.

---

## 2. Immediate post-download steps

1. Copy v69 `openrouter_pilot1_test_output/` to `kaggle_run_logs/v69/`.
2. Run the integrity checklist (`v69_post_download_checklist.md`).
3. Run quick standalone metrics:
   ```bash
   python kaggle_run_logs/v69/v69_quick_metrics.py
   ```
4. Run the paired v68-vs-v69 comparison:
   ```bash
   python kaggle_run_logs/v69/compare_v68_v69.py
   ```
5. Fill in the v69 detailed analysis template (`v69_detailed_analysis_report.md`).
6. Record the go/no-go decision in `AGENTS.md` and `memory.md`.

---

## 3. Metrics to compute

### 3.1 Aggregate (required for decision)

| Metric | Source columns / computation |
|---|---|
| Total MCQs | `len(pilot1_test_generated_mcqs.csv)` |
| Total cost | `pilot1_test_summary.json` → `estimated_cost_usd` |
| Perfect consensus rate | `consensus_frac == 1.0` |
| HCW rate | `consensus_frac >= 0.75` AND `consensus_correct == 0` |
| Consensus accuracy | `consensus_correct.mean()` |
| Partial + fallback rate | `generation_status in ["partial", "length_fallback", "parse_fallback"]` |
| Hard fallback rate | `generation_status == "length_fallback"` |
| Mean fallback count | `fallback_count.mean()` |
| Mean NLI replacements | `nli_replaced.mean()` |
| Mean leak replacements | `leak_replaced.mean()` |
| Mean length replacements | `length_replaced.mean()` |
| Duplicate options | `duplicate_options.sum()` |
| Correct-key balance | `correct_label.value_counts()` |

### 3.2 Per-language

- Consensus accuracy with Wilson 95% CI.
- Perfect consensus rate.
- HCW rate.
- Partial + fallback rate.
- Mean fallback count and replacement breakdown.
- Correct-key balance.

### 3.3 Paired v69-vs-v68 tests

- **McNemar** for binary outcomes: consensus correct, HCW, perfect consensus, partial+fallback, any fallback.
- **Wilcoxon signed-rank** + bootstrap 95% CI for continuous outcomes: consensus fraction, fallback count, NLI/leak/length replacements.
- **Relative change** v69 vs v68 for HCW, partial+fallback, perfect consensus, consensus accuracy, mean fallback count.

### 3.4 LLM-fallback-specific diagnostics

- Number of LLM fallback calls (from summary/cost history if tracked).
- Number of rejected LLM fallback calls.
- Mean cost per LLM fallback call.
- HCW and partial+fallback rates stratified by `fallback_count == 0` vs `> 0`.
- HCW and partial+fallback rates stratified by `generation_status`.

---

## 4. Go / no-go thresholds

| Tier | HCW | Partial + fallback | Cost | Decision |
|---|---|---|---|---|
| **Strong pass** | <10% | <15% | <$1.50 | **Scale to N=15 (v70).** Freeze config. |
| **Marginal** | 10–15% | 15–30% | <$1.50 | **Scale with caveats** or run one more focused ablation. |
| **Fail** | ≥15% | ≥30% | ≥$1.50 | **Pivot to paper-first.** Do not scale. |

**Notes:**

- These thresholds apply to the v69 N=5 run.
- If v69 is marginal, the N=15 v70 run must be treated as a final validation, not a guaranteed scale.
- Cost ≥$1.50 at N=5 implies ≥$4.50 extrapolated for N=15, leaving no budget margin or room for human-validation sampling.

---

## 5. Figures to generate

### From `compare_v68_v69.py`

1. `fig_v68_v69_metric_bars.png` — side-by-side bar chart of all aggregate rates.
2. `fig_v68_v69_paired_scatter.png` — paired scatter plots (consensus fraction, fallback count, NLI replacements, leak replacements) with diagonal reference.
3. `fig_v68_v69_delta_by_language.png` — per-language delta plots for HCW, partial+fallback, consensus accuracy, mean fallback count.

### From `v69_quick_metrics.py`

4. `fig_v69_status_distribution.png` — generation-status counts.
5. `fig_v69_replacement_breakdown.png` — total length/leak/NLI replacements.
6. `fig_v69_consensus_by_language.png` — accuracy / HCW / perfect consensus by language.

### Optional deep-dive figures

7. Per-variant HCW heatmap (generator × variant × language).
8. Per-generator HCW and partial+fallback bar chart.
9. HCW rate vs. fallback count (binned) to show whether LLM fallback reduced confident-wrong items.
10. Box/violin plot of `consensus_frac` by generation status (`generated`, `partial`, `length_fallback`).

---

## 6. Analysis artifacts

| Artifact | Path |
|---|---|
| v68-vs-v69 comparison report | `kaggle_run_logs/v69/v68_v69_comparison_report.md` |
| Comparison CSV | `kaggle_run_logs/v69/v68_v69_comparison_table.csv` |
| Per-language CSV | `kaggle_run_logs/v69/v68_v69_per_language.csv` |
| Per-variant CSV | `kaggle_run_logs/v69/v68_v69_per_variant.csv` |
| Per-generator CSV | `kaggle_run_logs/v69/v68_v69_per_generator.csv` |
| Paired data CSV | `kaggle_run_logs/v69/v68_v69_paired_metrics.csv` |
| Statistical tests CSV | `kaggle_run_logs/v69/v68_v69_statistical_tests.csv` |
| v69 quick metrics JSON | `kaggle_run_logs/v69/v69_quick_metrics.json` |
| v69 quick metrics text | `kaggle_run_logs/v69/v69_quick_metrics.txt` |
| v69 detailed analysis template | `kaggle_run_logs/v69/v69_detailed_analysis_report.md` |
| Post-download checklist | `kaggle_run_logs/v69/v69_post_download_checklist.md` |

---

## 7. Contingencies

- **If v69 outputs are incomplete or columns are missing:** `compare_v68_v69.py` now validates required columns and raises a clear error. Fix the notebook export or the download and re-run.
- **If v69 data is not yet available:** Running the scripts writes a v68-only baseline template so the pipeline can be tested in advance.
- **If plots fail:** Re-run with `--no-plots`; tables and statistics are still produced.

---

## 8. Decision workflow

```text
v69 outputs downloaded
        │
        ▼
Run v69_quick_metrics.py
        │
        ▼
Run compare_v68_v69.py
        │
        ▼
Check gates
        │
        ├─ HCW <10% AND partial+fallback <15% AND cost <$1.50 ──► STRONG PASS → scale v70 N=15
        │
        ├─ HCW 10–15% OR partial+fallback 15–30% ───────────────► MARGINAL → scale with caveats or ablate
        │
        └─ HCW ≥15% OR partial+fallback ≥30% OR cost ≥$1.50 ────► FAIL → pivot to paper-first
```
