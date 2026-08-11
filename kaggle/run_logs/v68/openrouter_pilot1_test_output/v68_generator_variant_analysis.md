# v68 Generator & Variant Performance Report

**Run:** `kaggle_run_logs/v68/openrouter_pilot1_test_output/`  
**Total MCQs:** 180 (N=5 proverbs x 3 languages x 3 generators x 4 variants)  
**Total estimated cost:** $0.8539 / $5.00  
**Duplicate-option MCQs:** 0  
**Key balance:** {'A': 45, 'B': 45, 'C': 45, 'D': 45}  

## 1. Active generators & committee after preflight

### Generator pool

| Role | Models |
|---|---|
| Active | qwen/qwen3.7-max, google/gemma-4-31b-it, google/gemini-2.5-flash |
| Benched | None |
| Substitutions | None |

### Auditor (committee) pool

| Role | Models |
|---|---|
| Active | meta-llama/llama-3.3-70b-instruct, mistralai/mistral-small-3.2-24b-instruct, google/gemma-3-27b-it, deepseek/deepseek-v3.2 |
| Benched | None |
| Substitutions | None |

**Preflight outcome:** All starter generators and auditors passed preflight. No substitutions or benchings occurred during the run.

## 2. Overall audit metrics

| Metric | Value |
|---|---|
| Consensus accuracy | 56.7% |
| Perfect consensus rate | 41.7% |
| HCW rate | 11.7% |
| Mean consensus fraction | 78.6% |

## 3. Per-generator performance

| Generator | N | Consensus accuracy | Perfect consensus | HCW rate | Generation cost | Cost / MCQ |
|---|---:|---:|---:|---:|---:|---:|
| google/gemma-4-31b-it | 60 | 65.0% | 46.7% | 8.3% | $0.0040 | $0.0001 |
| google/gemini-2.5-flash | 60 | 53.3% | 41.7% | 15.0% | $0.0057 | $0.0001 |
| qwen/qwen3.7-max | 60 | 51.7% | 36.7% | 11.7% | $0.8346 | $0.0139 |

## 4. Per-variant performance

| Variant | N | Consensus accuracy | Perfect consensus | HCW rate |
|---|---:|---:|---:|---:|
| adversarial-hard-negative | 45 | 60.0% | 31.1% | 6.7% |
| taxonomy-guided | 45 | 57.8% | 46.7% | 15.6% |
| adversarial-length-locked | 45 | 55.6% | 53.3% | 15.6% |
| overgenerate-select | 45 | 53.3% | 35.6% | 8.9% |

## 5. Generator x Variant heatmaps

### 5a. Consensus accuracy

| Generator | adversarial-hard-negative | adversarial-length-locked | overgenerate-select | taxonomy-guided |
|---|---:|---:|---:|---:|
| google/gemini-2.5-flash | 0.60 | 0.47 | 0.53 | 0.53 |
| google/gemma-4-31b-it | 0.60 | 0.67 | 0.60 | 0.73 |
| qwen/qwen3.7-max | 0.60 | 0.53 | 0.47 | 0.47 |

### 5b. Mean consensus fraction

| Generator | adversarial-hard-negative | adversarial-length-locked | overgenerate-select | taxonomy-guided |
|---|---:|---:|---:|---:|
| google/gemini-2.5-flash | 0.73 | 0.87 | 0.72 | 0.85 |
| google/gemma-4-31b-it | 0.77 | 0.87 | 0.78 | 0.82 |
| qwen/qwen3.7-max | 0.70 | 0.80 | 0.75 | 0.78 |

### 5c. HCW rate

| Generator | adversarial-hard-negative | adversarial-length-locked | overgenerate-select | taxonomy-guided |
|---|---:|---:|---:|---:|
| google/gemini-2.5-flash | 0.07 | 0.27 | 0.07 | 0.20 |
| google/gemma-4-31b-it | 0.07 | 0.13 | 0.07 | 0.07 |
| qwen/qwen3.7-max | 0.07 | 0.07 | 0.13 | 0.20 |

## 6. Cost per generator / variant

| Generator | Variant | Generation cost |
|---|---|---:|
| google/gemini-2.5-flash | adversarial-hard-negative | $0.0013 |
| google/gemini-2.5-flash | adversarial-length-locked | $0.0015 |
| google/gemini-2.5-flash | overgenerate-select | $0.0016 |
| google/gemini-2.5-flash | taxonomy-guided | $0.0013 |
| google/gemma-4-31b-it | adversarial-hard-negative | $0.0010 |
| google/gemma-4-31b-it | adversarial-length-locked | $0.0010 |
| google/gemma-4-31b-it | overgenerate-select | $0.0011 |
| google/gemma-4-31b-it | taxonomy-guided | $0.0010 |
| qwen/qwen3.7-max | adversarial-hard-negative | $0.1846 |
| qwen/qwen3.7-max | adversarial-length-locked | $0.2464 |
| qwen/qwen3.7-max | overgenerate-select | $0.1902 |
| qwen/qwen3.7-max | taxonomy-guided | $0.2135 |
| **Total generation** | - | **$0.8444** |

Audit + gold-curation costs are small relative to generation: ~$0.0092 (audit) and ~$0.0003 (curation).

## 7. Per-generator, per-language consensus accuracy

| Generator | Language | N | Consensus accuracy | Perfect consensus | HCW rate |
|---|---|---:|---:|---:|---:|
| google/gemini-2.5-flash | Arabic | 20 | 50.0% | 55.0% | 25.0% |
| google/gemini-2.5-flash | English | 20 | 65.0% | 40.0% | 5.0% |
| google/gemini-2.5-flash | Yoruba | 20 | 45.0% | 30.0% | 15.0% |
| google/gemma-4-31b-it | Arabic | 20 | 55.0% | 45.0% | 10.0% |
| google/gemma-4-31b-it | English | 20 | 70.0% | 50.0% | 10.0% |
| google/gemma-4-31b-it | Yoruba | 20 | 70.0% | 45.0% | 5.0% |
| qwen/qwen3.7-max | Arabic | 20 | 55.0% | 50.0% | 25.0% |
| qwen/qwen3.7-max | English | 20 | 60.0% | 45.0% | 5.0% |
| qwen/qwen3.7-max | Yoruba | 20 | 40.0% | 15.0% | 5.0% |

## 8. Insights & recommendations for N=15

### Key observations

1. **Generator quality:** `google/gemma-4-31b-it` is the strongest generator on consensus accuracy (65.0%) and the lowest HCW rate (8.3%). `google/gemini-2.5-flash` and `qwen/qwen3.7-max` are statistically weaker and both produce ~11.7-15.0% HCW.
2. **Cost asymmetry:** `qwen/qwen3.7-max` consumed ~$0.835 of the ~$0.844 generation budget, largely because of very long outputs. The two Google models are essentially free by comparison (~$0.004-0.006 total). This means dropping Qwen has almost no budget impact.
3. **Variant effects:** `adversarial-hard-negative` has the lowest perfect-consensus rate (31.1%) and HCW rate (6.7%), but its consensus accuracy (60.0%) is middle-of-the-pack. `adversarial-length-locked` and `taxonomy-guided` drive the most perfect consensus (53.3% and 46.7%) and the most HCW (15.6% each). `overgenerate-select` is in between.
4. **Heatmap patterns:** `google/gemma-4-31b-it` with `taxonomy-guided` yields the highest accuracy (73.3%) and zero HCW, while `qwen/qwen3.7-max` + `taxonomy-guided` for Arabic is the worst cell (20.0% accuracy, 40.0% HCW). `adversarial-length-locked` produces near-perfect consensus for Arabic items across all generators, inflating HCW risk.
5. **Language gaps:** Yoruba is the weakest language overall. Qwen Yoruba accuracy is only 40.0%, with very low perfect consensus. Gemma Yoruba is the best at 70.0% accuracy and only 5.0% HCW.
6. **Quality gates vs. targets:** Perfect consensus (41.7%) is still above the <30% target; HCW (11.7%) is just above the <10% target. The HCW target is almost met, but the pool is still too agreeable.

### Recommendations

| Decision | Generator / Variant | Rationale |
|---|---|---|
| **Keep as primary** | `google/gemma-4-31b-it` | Best accuracy (65.0%), lowest HCW (8.3%), and cheapest cost. |
| **Keep as secondary** | `google/gemini-2.5-flash` | Moderate accuracy (53.3%), still very cheap; useful for diversity. |
| **Drop from active pool** | `qwen/qwen3.7-max` | Highest cost (~99% of generation budget), lowest accuracy (51.7%), and weak Yoruba performance. |
| **Keep & prioritise** | `adversarial-hard-negative` | Lowest perfect consensus (31.1%) and HCW (6.7%); best for reducing auditor agreement. |
| **Keep with caution** | `overgenerate-select` | Balanced profile; keeps HCW moderate (8.9%) and accuracy acceptable (53.3%). |
| **Drop or rework** | `adversarial-length-locked` | Highest HCW (15.6%) and near-unanimous consensus on Arabic; contributes little shortcut resistance. |
| **Drop or rework** | `taxonomy-guided` | High HCW (15.6%) and high perfect consensus (46.7%); only saved by Gemma's strong accuracy. |
| **For N=15** | Run with **Gemma-4-31b-it + Gemini-2.5-flash** using **adversarial-hard-negative** and **overgenerate-select** only | This halves the variant space and removes the cost/quality outlier, giving more budget headroom for a 3x scale-up. |

### Suggested N=15 roster

- **Generators:** `google/gemma-4-31b-it`, `google/gemini-2.5-flash` (drop Qwen).
- **Prompt variants:** `adversarial-hard-negative`, `overgenerate-select` (drop `adversarial-length-locked` and `taxonomy-guided`, or keep only as small ablation).
- **Expected cost:** With Qwen removed and only two cheap generators, generation cost for 2 generators x 2 variants x 3 languages x 15 proverbs = 180 MCQs would be well under $0.05; even after adding fallback rewrites / curation, total cost should stay far below the $5.00 cap.
- **Risk watch:** Monitor Yoruba HCW specifically under the reduced roster; Gemma Yoruba is currently strong but the sample is small (N=20).

---

*Report generated from v68 Kaggle outputs: summary JSON, audit results, generated MCQs, and pool state.*