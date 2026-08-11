# ProverbGap Pilot 1 TEST — v69 Kaggle Run Deep Analysis

**Run:** `kaggle_run_logs/v69/openrouter_pilot1_test_output/`  
**Notebook:** `abrahamsunday123/mcq-pass-shortcut` (version 69)  
**Timestamp:** <!-- e.g. 2026-06-22T00:30:01Z -->  
**Seed:** 20260615  
**Config:** v69 LLM-fallback ablation (`USE_LLM_FALLBACK = True`), `N_PER_LANG = 5`

---

## Executive summary

<!-- Replace the placeholder bullets with v69 findings after the run. -->

- v69 is the LLM-fallback ablation of the frozen v67/v68 configuration.
- Total cost: **$____ / $5.00**.
- Total MCQs: **____** (15 proverbs × 4 variants × 3 generators = 180 expected).
- Primary gate status:
  - HCW: **____%** (target <10% strong, <15% marginal)
  - Partial + fallback: **____%** (target <15% strong, <30% marginal)
  - Cost: **$____** (target <$1.50)
  - Consensus accuracy: **____%**
  - Duplicate options: **____**
  - Correct-key balance: **____**

**Decision:** <!-- STRONG PASS / MARGINAL / FAIL -->

<!-- One-paragraph interpretation: Did the LLM fallback reduce confident-wrong consensus? Did it increase partial+fallback? Which languages improved? -->

---

## 1. Run setup and cost

| Item | Value |
|---|---|
| `N_PER_LANG` | 5 |
| Total proverbs | 15 (5 English + 5 Arabic + 5 Yoruba) |
| Variants | 4 (`adversarial-length-locked`, `adversarial-hard-negative`, `overgenerate-select`, `taxonomy-guided`) |
| Active generators | <!-- list models --> |
| Benched generators | <!-- list models, if any --> |
| Active auditors | <!-- list models --> |
| Total MCQs | 180 expected |
| Total cost | **$____ / $5.00** |
| Extrapolated N=15 cost | ~**$____** |
| LLM fallback calls | ____ (if tracked) |
| LLM fallback rejections | ____ (if tracked) |

<!-- Note any substitutions, missing votes, or API errors. -->

---

## 2. Aggregate quality metrics

| Metric | v68 N=5 (corpus) | v69 N=5 (LLM fallback) | Delta | Target |
|---|---|---|---|---|
| Perfect consensus | 41.7% | ____ | ____ | <30% ❌/✅ |
| High-consensus-wrong (HCW) | 27.8% | ____ | ____ | <10% ❌/✅ |
| Consensus accuracy | 56.7% | ____ | ____ | ≥50% ❌/✅ |
| Partial + fallback | 43.9% | ____ | ____ | <15% strong / <30% marginal ❌/✅ |
| Hard fallback (`length_fallback`) | 16.1% | ____ | ____ | <5% ❌/✅ |
| Parse/hard fallback | 0.0% | ____ | ____ | <5% ❌/✅ |
| Duplicate options | 0 | ____ | — | 0 ❌/✅ |
| Correct-key balance | 45/45/45/45 | ____ | — | ~25% ❌/✅ |

**Interpretation:**

<!-- Explain which gates pass and which fail. Compare to v68. -->

---

## 3. Per-language analysis

| Language | MCQs | Consensus accuracy | Perfect consensus | HCW (≥3/4 wrong) | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| English | 60 | ____ | ____ | ____ | ____ | ____ | ____ |
| Arabic | 60 | ____ | ____ | ____ | ____ | ____ | ____ |
| Yoruba | 60 | ____ | ____ | ____ | ____ | ____ | ____ |

**Mean replacements per MCQ by language:**

| Language | fallback_count | nli_replaced | leak_replaced | length_replaced |
|---|---:|---:|---:|---:|
| English | ____ | ____ | ____ | ____ |
| Arabic | ____ | ____ | ____ | ____ |
| Yoruba | ____ | ____ | ____ | ____ |

**Key observations:**

<!-- Which language improved? Which worsened? Did LLM fallback reduce replacements in Arabic/Yoruba? -->

---

## 4. Per-generator and per-variant analysis

### 4.1 Per-generator consensus performance

| Generator | MCQs | Accuracy | Perfect consensus | HCW | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| `<!-- generator -->` | 60 | ____ | ____ | ____ | ____ | ____ | ____ |
| `<!-- generator -->` | 60 | ____ | ____ | ____ | ____ | ____ | ____ |
| `<!-- generator -->` | 60 | ____ | ____ | ____ | ____ | ____ | ____ |

### 4.2 Per-variant consensus performance

| Variant | MCQs | Accuracy | Perfect consensus | HCW | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| `adversarial-hard-negative` | 45 | ____ | ____ | ____ | ____ | ____ | ____ |
| `adversarial-length-locked` | 45 | ____ | ____ | ____ | ____ | ____ | ____ |
| `overgenerate-select` | 45 | ____ | ____ | ____ | ____ | ____ | ____ |
| `taxonomy-guided` | 45 | ____ | ____ | ____ | ____ | ____ | ____ |

**Variant / generator interpretation:**

<!-- Which variant/generator benefits most from LLM fallback? Which still suffers from NLI/leak replacements? -->

---

## 5. Generation pipeline diagnostics

### 5.1 Status distribution

| Status | Count | Percentage |
|---|---:|---:|
| `generated` | ____ | ____ |
| `partial` | ____ | ____ |
| `length_fallback` | ____ | ____ |
| `parse_fallback` | ____ | ____ |
| `hard_fallback` | ____ | ____ |

### 5.2 Mean replacements per MCQ

| Metric | Mean per MCQ | Interpretation |
|---|---:|---|
| `fallback_count` | ____ | Corpus + LLM replacements per MCQ |
| `nli_replaced` | ____ | NLI paraphrase filter replacements |
| `leak_replaced` | ____ | Correct-meaning leak replacements |
| `length_replaced` | ____ | Length-parity replacements |
| `duplicate_options` | ____ | Exact duplicate pairs |

### 5.3 LLM fallback performance

<!-- Fill only if the v69 code tracks LLM fallback usage. If not, infer from raw outputs / cost history. -->

| Item | Value |
|---|---|
| LLM fallback calls | ____ |
| LLM fallback rejections | ____ |
| Mean cost per fallback call | $____ |
| HCW rate when fallback_count == 0 | ____ |
| HCW rate when fallback_count > 0 | ____ |
| Partial+fallback rate when fallback_count == 0 | ____ |
| Partial+fallback rate when fallback_count > 0 | ____ |

### 5.4 Highest-fallback items

<!-- List 2–3 worst items with mcq_id, fallback_count breakdown, and HCW status. -->

---

## 6. Paired statistical comparison with v68

Results from `v68_v69_comparison_report.md` and `v68_v69_statistical_tests.csv`:

| Outcome | v68 rate/mean | v69 rate/mean | Δ | p-value | Interpretation |
|---|---|---|---|---|---|
| Consensus correct | ____ | ____ | ____ | ____ | ____ |
| HCW | ____ | ____ | ____ | ____ | ____ |
| Perfect consensus | ____ | ____ | ____ | ____ | ____ |
| Partial or fallback | ____ | ____ | ____ | ____ | ____ |
| Any fallback | ____ | ____ | ____ | ____ | ____ |
| Fallback count | ____ | ____ | ____ | ____ | ____ |
| NLI replacements | ____ | ____ | ____ | ____ | ____ |
| Leak replacements | ____ | ____ | ____ | ____ | ____ |
| Length replacements | ____ | ____ | ____ | ____ | ____ |

---

## 7. Go / no-go decision and next steps

### 7.1 Decision classification

| Criterion | Value | Pass? |
|---|---|---|
| HCW <10% | ____% | ____ |
| Partial + fallback <15% | ____% | ____ |
| Cost <$1.50 | $____ | ____ |

**Decision:** ☐ STRONG PASS  ☐ MARGINAL  ☐ FAIL

### 7.2 If STRONG PASS

- Freeze v69 config (`USE_LLM_FALLBACK = True`, current prompt/length/NLI settings).
- Run v70 at `N_PER_LANG = 15` (same seed or new deterministic seed).
- Target cost <$2.70; extrapolate from v69 N=5 cost.
- Prepare 60-item human-validation sample (20 per language) from v70.
- Update `AGENTS.md` and paper outline.

### 7.3 If MARGINAL

- List caveats: ________________________________________
- Decide: scale to N=15 with caveats OR run one focused ablation (e.g., NLI embedding guard sweep, variant removal).
- If scaling, flag the risky variant/language for extra human validation.
- If ablating, choose the single highest-leverage knob and run v69.1 N=5.

### 7.4 If FAIL

- Do **not** scale to N=15.
- Treat v68 + v69 as the final dataset for the paper (180 + 180 = 360 MCQs, paired).
- Document the LLM-fallback ablation as a negative/insufficient result.
- Begin 60-item human validation on the better of v68/v69 (or a stratified sample from both).
- Draft paper around methodology + reproducible failure taxonomy.

---

## 8. Appendices

### 8.1 Auditor behavior

| Auditor | Votes | Missing | Accuracy |
|---|---:|---:|---:|
| `<!-- auditor -->` | ____ | ____ | ____ |
| `<!-- auditor -->` | ____ | ____ | ____ |
| `<!-- auditor -->` | ____ | ____ | ____ |
| `<!-- auditor -->` | ____ | ____ | ____ |

### 8.2 Example high-consensus-wrong items

<!-- Show 2–3 representative HCW items with options and explain why auditors converged. -->

### 8.3 Example partial / fallback-heavy items

<!-- Show 2–3 items with high fallback_count and explain replacement chain. -->

### 8.4 Files produced by this analysis

- `kaggle_run_logs/v69/v69_detailed_analysis_report.md` (this report)
- `kaggle_run_logs/v69/v68_v69_comparison_report.md`
- `kaggle_run_logs/v69/v68_v69_comparison_table.csv`
- `kaggle_run_logs/v69/v68_v69_per_language.csv`
- `kaggle_run_logs/v69/v68_v69_per_variant.csv`
- `kaggle_run_logs/v69/v68_v69_per_generator.csv`
- `kaggle_run_logs/v69/v68_v69_statistical_tests.csv`
- `kaggle_run_logs/v69/fig_v68_v69_metric_bars.png`
- `kaggle_run_logs/v69/fig_v68_v69_paired_scatter.png`
- `kaggle_run_logs/v69/fig_v68_v69_delta_by_language.png`

---

*Report template generated before v69 run. Fill in all TBD/blank cells after outputs are downloaded.*
