# ProverbGap Pilot 1 TEST — v68 Kaggle Run Deep Analysis

**Run:** `kaggle_run_logs/v68/openrouter_pilot1_test_output/`  
**Notebook:** `abrahamsunday123/mcq-pass-shortcut` (version 68)  
**Timestamp:** 2026-06-22T00:30:01Z  
**Seed:** 20260615  
**Config:** v67 frozen baseline (`USE_LLM_FALLBACK = False`), `N_PER_LANG = 5`

---

## Executive summary

v68 is the first N=5 smoke test of the frozen v67 configuration. The run completed successfully, cost **$0.85 / $5.00**, and produced **180 MCQs** (15 proverbs × 4 variants × 3 generators) with perfect key balance and zero exact-duplicate options. However, **all shortcut-resistance gates failed** except duplicate options and key balance:

| Gate | v68 N=5 | Target | Pass? |
|---|---|---|---|
| Hard fallback rate (< 5%) | 16.1% | < 5% | ❌ |
| Partial + fallback (< 15%) | 43.9% | < 15% | ❌ |
| High-consensus-wrong, HCW (< 10%) | 27.8% | < 10% | ❌ |
| Perfect consensus (< 30%) | 41.7% | < 30% | ❌ |
| Per-language consensus correctness ≥ 50% | English 65.0%, Arabic 53.3%, Yoruba 51.7% | ≥ 50% | ⚠️ fragile |
| Duplicate options | 0 | 0 | ✅ |
| Correct-key balance (A/B/C/D) | 45 / 45 / 45 / 45 | ~25% each | ✅ |

The most serious regression is **HCW**, which rose from 11.1% in v65 (N=1) to **27.8%** at N=5. The diagnosis is unchanged: **the corpus-based fallback sampler is the bottleneck.** When NLI paraphrase or correct-meaning-leak filters reject a model-generated distractor, the pipeline samples a fallback from other proverbs’ meanings. At N=5, those fallbacks are frequently plausible enough to attract auditor consensus but wrong, producing confident-wrong items. NLI replacements (mean 0.36/MCQ) and leak replacements (mean 0.35/MCQ) are the dominant drivers, not length (mean 0.15/MCQ).

**Recommendation:** Do **not** scale to N=15 with the current corpus fallback. Run a focused **v69 ablation** enabling `USE_LLM_FALLBACK = True` at N=5. If HCW drops below ~15% and partial+fallback drops below ~30%, freeze the config and scale to N=15 (v70). If the ablation does not help, treat v68/v69 as the production data for the paper and frame the corpus-fallback failure mode as a contribution, moving immediately to human validation and paper drafting.

---

## 1. Run setup and cost

| Item | Value |
|---|---|
| `N_PER_LANG` | 5 |
| Total proverbs | 15 (5 English + 5 Arabic + 5 Yoruba) |
| Variants | 4 (`adversarial-length-locked`, `adversarial-hard-negative`, `overgenerate-select`, `taxonomy-guided`) |
| Active generators | 3 (`qwen/qwen3.7-max`, `google/gemma-4-31b-it`, `google/gemini-2.5-flash`) |
| Active auditors | 4 (`llama-3.3-70b`, `mistral-small-3.2-24b`, `gemma-3-27b-it`, `deepseek-v3.2`) |
| Total MCQs | 180 |
| Total cost | **$0.8539 / $5.00** |
| Extrapolated N=15 cost | ~**$2.56** (still under cap) |

All 4 auditors voted on every MCQ (0 missing votes). No generator or auditor substitutions occurred, confirming roster stability.

---

## 2. Aggregate quality metrics

| Metric | v68 N=5 | v65 N=1 (baseline) | v66 N=1 (regression) | Target |
|---|---|---|---|---|
| Perfect consensus | **41.7%** (75/180) | 41.7% | 55.6% | < 30% ❌ |
| High-consensus-wrong (HCW) | **27.8%** (50/180) | 11.1% | 22.2% | < 10% ❌ |
| Consensus accuracy | **56.7%** (102/180) | 63.9% | 69.4% | — |
| Partial + fallback | **43.9%** (79/180) | 36.1% | 50.0% | < 15% ❌ |
| Hard fallback (`length_fallback`) | **16.1%** (29/180) | — | — | < 5% ❌ |
| Parse/hard fallback | 0.0% | — | — | < 5% ✅ |
| Duplicate options | 0 | 0 | 0 | 0 ✅ |
| Correct-key balance | 45/45/45/45 | 8/10/7/11 | — | ~25% ✅ |

HCW is defined as consensus fraction ≥ 0.75 with consensus label ≠ correct label (i.e., at least 3 of 4 auditors agreed on the wrong answer).

**Interpretation:**
- The v66 spike in perfect consensus was not reproduced at N=5; perfect consensus returned to the v65 level.
- **HCW degraded sharply** with more proverbs: 11.1% → 27.8%. The pipeline is producing attractive distractors, but auditors agree on the wrong option too often.
- Consensus accuracy dropped to 56.7%, meaning the blind audit committee is only slightly better than random on options alone.
- Partial+fallback remains far above the 15% gate.

---

## 3. Per-language analysis

| Language | MCQs | Consensus accuracy | Perfect consensus | HCW (≥3/4 wrong) | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| English | 60 | **65.0%** (39/60) | 45.0% (27/60) | 18.3% (11/60) | 48 | 8 | 4 |
| Arabic | 60 | **53.3%** (32/60) | 50.0% (30/60) | 31.7% (19/60) | 25 | 21 | 14 |
| Yoruba | 60 | **51.7%** (31/60) | 30.0% (18/60) | 33.3% (20/60) | 28 | 21 | 11 |

**Key observations:**
- **English** is still the easiest language. 65.0% consensus accuracy is well above the other two, but 45.0% perfect consensus means distractors are not tempting enough: auditors disagree or converge on the key.
- **Arabic** has the highest perfect-consensus rate (50.0%) but also the lowest accuracy (53.3%), indicating many confident-wrong items. Arabic drives 19/50 HCW cases.
- **Yoruba** has the lowest perfect-consensus rate (30.0%) but the highest HCW rate (33.3%). When Yoruba auditors do agree, they are often wrong. The per-language correctness gate (≥50%) is technically met at 51.7%, but it is fragile.
- Position bias is perfectly controlled: A/B/C/D = 15/15/15/15 for every language.

**Mean replacements per MCQ by language:**

| Language | fallback_count | nli_replaced | leak_replaced | length_replaced |
|---|---:|---:|---:|---:|
| English | 0.43 | 0.15 | 0.15 | 0.07 |
| Arabic | 1.52 | 0.62 | 0.43 | 0.25 |
| Yoruba | 1.03 | 0.32 | 0.47 | 0.13 |

Arabic requires the most fallback replacements; English requires the least. NLI and leak filters are the main drivers in Arabic and Yoruba.

---

## 4. Per-generator and per-variant analysis

### 4.1 Per-generator consensus performance

| Generator | MCQs | Accuracy | Perfect consensus | HCW | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| `google/gemini-2.5-flash` | 60 | 53.3% | 41.7% | 46.7% | 30 | 25 | 5 |
| `google/gemma-4-31b-it` | 60 | 65.0% | 46.7% | 35.0% | 40 | 14 | 6 |
| `qwen/qwen3.7-max` | 60 | 51.7% | 36.7% | 46.7% | 31 | 11 | 18 |

`google/gemma-4-31b-it` is the strongest generator on this sample: highest accuracy, lowest HCW, and the cleanest generation-status profile (66.7% fully generated). `qwen/qwen3.7-max` has the highest `length_fallback` rate (30.0%) and the highest mean `fallback_count` (1.33). `google/gemini-2.5-flash` produces many partial items (41.7%) driven by NLI replacements.

### 4.2 Per-variant consensus performance

| Variant | MCQs | Accuracy | Perfect consensus | HCW | Generated | Partial | Length fallback |
|---|---|---:|---:|---:|---:|---:|---:|
| `adversarial-hard-negative` | 45 | 60.0% | 31.1% | 40.0% | 12 | 14 | 19 |
| `adversarial-length-locked` | 45 | 55.6% | 53.3% | 44.4% | 27 | 9 | 9 |
| `overgenerate-select` | 45 | 53.3% | 35.6% | 46.7% | 32 | 12 | 1 |
| `taxonomy-guided` | 45 | 57.8% | 46.7% | 40.0% | 30 | 15 | 0 |

**Variant interpretation:**
- `adversarial-hard-negative` has the most HCW (40.0%) and the worst generation-status profile: only 26.7% fully generated, 42.2% `length_fallback`. The prompt succeeds at producing tempting distractors, but the sanitizers reject them and the corpus fallbacks are confident-wrong traps.
- `adversarial-length-locked` has the highest perfect-consensus rate (53.3%) but also high HCW (44.4%).
- `overgenerate-select` and `taxonomy-guided` are cleaner in generation status but still produce high HCW because the selected distractors are too tempting.

### 4.3 Cross-tab: generator × generation status

| Generator | Generated | Length fallback | Partial | Total |
|---|---:|---:|---:|---:|
| `google/gemini-2.5-flash` | 30 | 5 | 25 | 60 |
| `google/gemma-4-31b-it` | 40 | 6 | 14 | 60 |
| `qwen/qwen3.7-max` | 31 | 18 | 11 | 60 |

---

## 5. Generation pipeline diagnostics

### 5.1 Status distribution

| Status | Count | Percentage |
|---|---:|---:|
| `generated` | 101 | 56.1% |
| `partial` | 50 | 27.8% |
| `length_fallback` | 29 | 16.1% |
| `parse_fallback` | 0 | 0.0% |
| `hard_fallback` | 0 | 0.0% |

No parse or hard fallbacks occurred, indicating parser and API stability. However, **43.9%** of MCQs required at least one corpus fallback.

### 5.2 Mean replacements per MCQ

| Metric | Mean per MCQ | Interpretation |
|---|---:|---|
| `fallback_count` | 0.99 | Corpus replacements per MCQ |
| `nli_replaced` | 0.36 | NLI paraphrase filter replacements |
| `leak_replaced` | 0.35 | Correct-meaning leak replacements |
| `length_replaced` | 0.15 | Length-parity replacements |
| `duplicate_options` | 0.00 | Exact duplicate pairs |

The dominant replacement drivers are **NLI paraphrase filtering** and **correct-meaning leak filtering**, not length. This means the sanitizers are aggressively rewriting distractors, and the corpus fallback is being invoked frequently.

### 5.3 Highest-fallback items

There are **29** MCQs with `fallback_count ≥ 3`. The worst cases combine NLI and leak replacements on Arabic and Yoruba proverbs, often under the `adversarial-hard-negative` variant. Examples:

- `google_gemma-4-31b-it_adversarial-length-locked_Arabic_3`: fallback_count = 6 (1 length, 1 NLI, 3 leak).
- `qwen_qwen3.7-max_adversarial-hard-negative_Arabic_4`: fallback_count = 5 (2 length, 0 NLI, 3 leak).

These items are almost always `length_fallback` status, but the replacements are driven by semantic/NLI/leak filters, not just length.

### 5.4 Blocklist and duplicates

- Only **3** raw generation attempts triggered the generic-English idiom blocklist, all on Arabic proverbs where the model produced “Charity begins at home.” These were repaired at the option level.
- **0** exact duplicate option pairs. Independent near-duplicate checks found 3 Jaccard > 0.50 pairs and 0 token-overlap ≥ 0.85 pairs.

---

## 6. Root cause: corpus fallback sampler is the bottleneck

The evidence confirms the pre-run diagnosis:

1. **43.9%** of MCQs need corpus fallback replacements.
2. Mean **0.99** fallback replacements per MCQ.
3. Replacements are dominated by **NLI** and **leak** filters, not length or blocklist.
4. The `adversarial-hard-negative` variant — designed to produce tempting distractors — is rewritten by filters 73.3% of the time, and the resulting corpus fallbacks frequently become HCW items.
5. Arabic and Yoruba are disproportionately affected; English is largely fine.
6. The strongest generator (`gemma-4-31b-it`) still has a 35.0% HCW rate, so the problem is systemic, not model-specific.

**Mechanism:** The corpus sampler pulls distractors from other proverbs’ meanings. Those meanings are often generic moral statements or culturally mismatched idioms. When placed next to a curated gold meaning, they can look plausible to auditors, especially when the original tempting distractor was removed by NLI/leak filters. The result is confident-wrong consensus.

---

## 7. Next-step recommendations

### 7.1 Immediate: do not scale to N=15
Scaling to N=15 with the current corpus fallback would waste budget and produce a larger set with the same HCW problem. The v68 N=5 data already shows HCW is unacceptably high.

### 7.2 v69 ablation: enable LLM-based fallback generator
The code already contains `generate_llm_fallback_distractor()` gated by `USE_LLM_FALLBACK = False`. The function uses `openai/gpt-4.1-nano` to generate a single proverb-specific hard negative on demand, then applies the same semantic/NLI/length/blocklist filters.

**Proposed v69 config:**
```python
N_PER_LANG = 5
USE_LLM_FALLBACK = True
FALLBACK_GENERATOR_MODEL = "openai/gpt-4.1-nano"
# All other v68 constants unchanged
```

**Expected cost:** Additional ~$0.10–$0.20 (one cheap LLM call per replacement × ~180 replacements). Total should remain well under $1.50.

**Success gates for v69:**
- HCW < 15% (step target; ideally < 10%).
- Partial + fallback < 30% (step target; ideally < 15%).
- No increase in perfect consensus above 45%.
- Cost < $1.50 for N=5.

If v69 passes these gates, freeze and run **v70 at N=15**.

### 7.3 Parallel paper track
While the v69 ablation runs, begin drafting the paper around the following frame:

- **Methodology:** Hardened OpenRouter pipeline with dynamic model pools, adversarial prompt variants, gold-meaning curation, semantic/NLI/length/blocklist filters, and blind options-only audit committee.
- **Failure taxonomy:** Use v68 data to define a taxonomy of distractor failure modes:
  1. **Generic reversal / idiom shortcut** (English too easy).
  2. **Near-paraphrase trap** (NLI filters remove tempting distractors).
  3. **Confident-wrong fallback** (corpus fallbacks attract auditor consensus).
  4. **Cultural mismatch** (Yoruba/Arabic fallbacks from other languages or idioms).
  5. **Length/register imbalance** (partial/length_fallback items).
- **Human validation plan:** Sample 60 MCQs (20 per language) from the final N=15 run for human annotators, with inter-annotator agreement (IAA) against the audit committee.
- **Known limitation / contribution:** The corpus fallback sampler is a clear limitation that motivates the LLM-based fallback ablation; framing it as an iterative engineering contribution is reviewer-defensible.

### 7.4 Fallback-only if ablation fails
If v69 does not meaningfully improve HCW or partial+fallback, the LLM fallback is not the silver bullet. In that case:
- Use v68 (or the best subsequent run) as the production dataset.
- Document the corpus-fallback limitation explicitly.
- Move to N=15 **only if** the metrics are stable enough for human validation; otherwise cap the paper at N=5 with a larger human-validation sample.

### 7.5 Long-term: reconsider the NLI/leak thresholds
If v69 improves fallback quality but HCW remains high, the next knob is the NLI/leak filter thresholds. The current filters may be over-aggressive, removing legitimate tempting distractors and forcing fallback use. A grid search over NLI embedding guards (e.g., 0.45–0.65) and leak thresholds (0.75–0.90) could be a follow-up ablation.

---

## 8. Appendices

### 8.1 Auditor behavior

| Auditor | Votes | Missing | Accuracy |
|---|---:|---:|---:|
| `meta-llama/llama-3.3-70b-instruct` | 180 | 0 | 56.7% |
| `mistralai/mistral-small-3.2-24b-instruct` | 180 | 0 | 56.7% |
| `google/gemma-3-27b-it` | 180 | 0 | 56.7% |
| `deepseek/deepseek-v3.2` | 180 | 0 | 56.7% |

All auditors have identical overall accuracy because they are evaluated against the same consensus correct column; individual hit rates vary by MCQ.

### 8.2 Example high-consensus-wrong items

1. **Arabic, `google/gemini-2.5-flash`, `adversarial-length-locked`** — correct meaning: *Love is blind.*
   - A: *Love can transform even the most humble offerings into something precious and valuable.*
   - B: *Deep affection often blinds individuals to the imperfections of those they cherish.* ← auditors converged here (perfect consensus wrong).
   - C: *True devotion means accepting a partner's flaws without any desire for change.*
   - D: *The believer is not bitten from the same hole twice.*

2. **Arabic, `qwen/qwen3.7-max`, `adversarial-length-locked`** — correct meaning: *Charity begins at home.*
   - A: *The stupid might want to help you, but they just ended up hurting you.* ← 3/4 auditors.
   - B: *Let them drink and forget their poverty and remember their misery no more.*
   - C: *Individuals must prioritize supporting their immediate relatives before donating resources to the broader community.* (correct)
   - D: *But remember that good intentions pave many roads. Not all of them lead to hell.*

3. **Arabic, `google/gemma-4-31b-it`, `adversarial-length-locked`** — correct meaning: *A bird in the hand is worth two in the bush.*
   - A: *There is an excess of familiarity at the root of all hostilities.*
   - B: *Better is a dinner of herbs where love is, than a stalled ox and hatred therewith.* ← perfect consensus wrong.
   - C: *It is better to keep a small certainty than to risk it for a larger possibility.* (correct)
   - D: *All is not gold that glitters / Fine feathers do not make fine birds.*

These examples show the corpus fallback pulling unrelated proverbs or culturally mismatched English idioms that auditor models find plausible.

### 8.3 Files produced by this analysis

- `kaggle_run_logs/v68/v68_detailed_analysis_report.md` (this report)
- `kaggle_run_logs/v68/v68_generation_quality_report.md`
- `kaggle_run_logs/v68/v68_per_language_generator_report.md`

---

*Report generated 2026-06-21 from v68 Kaggle outputs.*
