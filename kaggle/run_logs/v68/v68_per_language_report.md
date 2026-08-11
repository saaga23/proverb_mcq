# V68 Kaggle Run — Per-Language Performance Report

**Run:** 2026-06-22 | **Sample:** N=5 proverbs/language × 3 generators × 4 variants = 180 MCQs (60/language).
**Generator pool:** qwen/qwen3.7-max, google/gemma-4-31b-it, google/gemini-2.5-flash (all active, 0 benched).
**Audit committee:** 4 models, 0 missing votes, 0 substitutions.

## 1. Per-language consensus correctness (Wilson 95% CI)

Consensus correctness = fraction of MCQs where the plurality auditor vote matches the correct label.

| Language | Correct / Total | Accuracy | Wilson 95% CI |
|----------|----------------|----------|---------------|
| English | 39/60 | 65.0% | 52.4%-75.8% |
| Arabic | 32/60 | 53.3% | 40.9%-65.4% |
| Yoruba | 31/60 | 51.7% | 39.3%-63.8% |

- **English** leads but is still only ~65%; the high share of too-easy items drags the meaningful signal down.
- **Arabic** and **Yoruba** are statistically similar and both just clear the 50% bar.

## 2. Perfect consensus & high-consensus-wrong (HCW)

**HCW definition used in the main v68 report:** consensus fraction ≥ 0.75 (i.e., at least 3 of 4 auditors) and consensus label ≠ correct label.

| Language | Perfect consensus | HCW (≥3/4 vote, wrong) | Non-perfect consensus |
|----------|-------------------|--------------------------|-----------------------|
| English | 27/60 (45.0%) | 11/60 (18.3%) | 33/60 (55.0%) |
| Arabic | 30/60 (50.0%) | 19/60 (31.7%) | 30/60 (50.0%) |
| Yoruba | 18/60 (30.0%) | 20/60 (33.3%) | 42/60 (70.0%) |

- **Perfect consensus** is far above the <30% target in all languages; English and Arabic are near or above 45%.
- **HCW** is high (18–33%). When 3+ auditors agree, they agree on the wrong answer a substantial fraction of the time, especially in Arabic and Yoruba.
- **Non-perfect consensus** is highest for Yoruba (~70%) and lowest for Arabic (~50%), suggesting Yoruba options create more auditor disagreement.

*Note: An earlier draft of this section used a ≥50% HCW threshold, which counts weaker agreement as confident-wrong. The ≥75% threshold is the project standard and is used in `v68_detailed_analysis_report.md`.*

## 3. Correct-key distribution per language (position bias)

| Language | A | B | C | D |
|----------|---|---|---|---|
| English | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) |
| Arabic | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) |
| Yoruba | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) | 15 (25.0%) |

- Position bias is perfectly controlled at 25% per key for every language.

## 4. Auditor behavior per language

### English

| Auditor | Missing votes | Hit rate |
|---------|---------------|----------|
| meta-llama_llama-3.3-70b-instruct | 0/60 (0.0%) | 36/60 (60.0%) |
| mistralai_mistral-small-3.2-24b-instruct | 0/60 (0.0%) | 42/60 (70.0%) |
| google_gemma-3-27b-it | 0/60 (0.0%) | 33/60 (55.0%) |
| deepseek_deepseek-v3.2 | 0/60 (0.0%) | 41/60 (68.3%) |

- Mean consensus fraction: **0.792**

### Arabic

| Auditor | Missing votes | Hit rate |
|---------|---------------|----------|
| meta-llama_llama-3.3-70b-instruct | 0/60 (0.0%) | 31/60 (51.7%) |
| mistralai_mistral-small-3.2-24b-instruct | 0/60 (0.0%) | 33/60 (55.0%) |
| google_gemma-3-27b-it | 0/60 (0.0%) | 27/60 (45.0%) |
| deepseek_deepseek-v3.2 | 0/60 (0.0%) | 31/60 (51.7%) |

- Mean consensus fraction: **0.821**

### Yoruba

| Auditor | Missing votes | Hit rate |
|---------|---------------|----------|
| meta-llama_llama-3.3-70b-instruct | 0/60 (0.0%) | 29/60 (48.3%) |
| mistralai_mistral-small-3.2-24b-instruct | 0/60 (0.0%) | 27/60 (45.0%) |
| google_gemma-3-27b-it | 0/60 (0.0%) | 22/60 (36.7%) |
| deepseek_deepseek-v3.2 | 0/60 (0.0%) | 29/60 (48.3%) |

- Mean consensus fraction: **0.746**

- Auditor hit rates drop sharply on Yoruba (Gemma-3-27b only 36.7%), confirming that Yoruba meanings are hardest to identify from options alone.
- No missing votes and no substitutions: the audit pipeline is stable.

## 5. Specific failure examples

### 5.1 Yoruba — distractors override the literal/cultural key

**Ìdtí ò mátà; woléwolé lẹj bá wí.** (overgenerate-select, `google/gemma-4-31b-it`)
- Correct meaning: *Dirt does not matter; only the sanitary inspector fusses.* (correct key: **C**)
- Consensus: **B** @ 1.0 | status: `generated`, fallback_count=0
- A: The purity of a vessel is judged only by those who do not use it for labor.
- B: A diligent worker ignores the dust that the idle observer finds offensive.
- C: A farmer's gourd remains unbound by dirt, but only the inspector worries about cleanliness.
- D: True cleanliness is found in the tools of the field rather than the words of the chief.

**Ilé kì í jó kí oorun kun ojú.** (adversarial-length-locked, `google/gemini-2.5-flash`)
- Correct meaning: *A house does not burn and fill the eyes with sleep.* (correct key: **C**)
- Consensus: **A** @ 1.0 | status: `partial`, fallback_count=1
- A: A person's true character is often revealed through their actions during times of great adversity.
- B: One must always remain vigilant and prepared for unexpected challenges, even in times of peace.
- C: A community should not be so well-protected that it ignores internal conflicts and potential dangers.
- D: The head is never so frightened that it disappears into the shoulder.

**Kékeré lọ̀pọ̀lọ́ fi ga ju ilẹ̀ lọ.** (taxonomy-guided, `google/gemini-2.5-flash`)
- Correct meaning: *The toad is only slightly taller than the earth.* (correct key: **D**)
- Consensus: **A** @ 1.0 | status: `generated`, fallback_count=0
- A: Even a small person can achieve great things if they are determined and persistent in their efforts.
- B: A person's true character is revealed not by their outward appearance, but by the wisdom and respect they show to their elders.
- C: The smallest among us can still contribute significantly to the community if given the opportunity to lead.
- D: One's inherent limitations, no matter how much effort is expended, will always keep them grounded in their true nature.

### 5.2 Arabic — confident-wrong consensus on near-paraphrases / generic idioms

**مراية الحب عمياء/بصلة المحب خروف** (adversarial-length-locked, `google/gemini-2.5-flash`)
- Correct meaning: *Love is blind.* (correct key: **B**)
- Consensus: **A** @ 1.0 | status: `partial`, fallback_count=2
- A: Love can transform even the most humble offerings into something precious and valuable.
- B: Deep affection often blinds individuals to the imperfections of those they cherish.
- C: True devotion means accepting a partner's flaws without any desire for change.
- D: The believer is not bitten from the same hole twice

**عتبها على أهلها من قلة عقلها.** (adversarial-hard-negative, `qwen/qwen3.7-max`)
- Correct meaning: *A bad workman always blames his tools.* (correct key: **B**)
- Consensus: **A** @ 1.0 | status: `length_fallback`, fallback_count=5
- A: Knowing yourself is the beginning of all wisdom.
- B: A foolish woman blames her relatives for her own lack of wisdom.
- C: We judge others by our own standards.
- D: If you are always dwelling in trouble change the address.

**اللي يعوزه البيت يحرم على الجامع** (overgenerate-select, `qwen/qwen3.7-max`)
- Correct meaning: *Charity begins at home.* (correct key: **B**)
- Consensus: **C** @ 1.0 | status: `generated`, fallback_count=0
- A: True piety demands keeping sacred spaces separate from everyday domestic life.
- B: One must secure their own family's needs before giving to the wider community.
- C: Keeping resources at home deprives the wider society of essential public wealth.
- D: Religious duties to the congregation must outweigh everyday personal family desires.

### 5.3 English — too-easy / perfect-consensus-correct items

**Count of perfect-consensus-correct English items: 23 / 60 (38.3%)**

**After a calm comes a storm** (adversarial-length-locked, `qwen/qwen3.7-max`)
- Correct meaning: *A person might be overcome by trouble or adversity when least expected.* (correct key: **D**)
- A: Tranquil periods eventually return without delay following chaotic events.
- B: Careful preparations adequately protect against danger throughout quiet seasons.
- C: Minor problems steadily escalate into disasters throughout extended intervals.
- D: Severe difficulties frequently emerge without warning during tranquil periods.

**Know thyself** (adversarial-length-locked, `qwen/qwen3.7-max`)
- Correct meaning: *This proverb can be used as a caution that we should know our limits and weaknesses, or as motivation to disc over our strengths and hidden talents.* (correct key: **C**)
- A: Observing your outer environment enables you to discover your social limits and your public talents.
- B: Imagining your future potential enables you to create your personal goals and your ultimate triumphs.
- C: Examining your inner character enables you to discover your personal limits and your unique talents.
- D: Concealing your inner character enables you to protect your personal secrets and your hidden motives.

**Know thyself** (adversarial-length-locked, `google/gemma-4-31b-it`)
- Correct meaning: *This proverb can be used as a caution that we should know our limits and weaknesses, or as motivation to disc over our strengths and hidden talents.* (correct key: **D**)
- A: Analyzing your past actions helps you predict how others will react to your future decisions.
- B: Studying your inner desires helps you achieve the goals that you have set for your career.
- C: Observing your daily habits helps you improve the way you interact with people in society.
- D: Understanding your true self helps you recognize both your limitations and your unique strengths.

## 6. Scaling gate assessment

| Gate | Target | English | Arabic | Yoruba |
|------|--------|---------|--------|--------|
| Consensus correctness | >=50% | 65.0% PASS | 53.3% PASS | 51.7% PASS |
| Perfect consensus | <30% | 45.0% FAIL | 50.0% FAIL | 30.0% FAIL |
| HCW rate | <10% | 33.3% FAIL | 46.7% FAIL | 48.3% FAIL |

### 6.1 Does Yoruba meet the >=50% correctness gate?

**Yes, barely.** Yoruba reaches 51.7% (95% CI 39.3%-63.8%), so it clears the 50% threshold but the lower CI bound is below 50%. With only 60 items the estimate is noisy; an N=15 run would tighten the interval.

### 6.2 Which languages are scaling blockers?

**All three are blockers for different reasons:**
- **English** is the 'too-easy' blocker: 45% perfect-consensus-correct means distractors are not tempting enough; the MCQs are shortcut-solvable for auditors.
- **Arabic** is the 'confident-wrong' blocker: 50% perfect consensus and 46.7% HCW — auditors agree too often and usually on attractive but wrong distractors.
- **Yoruba** is the 'fragile low-resource' blocker: lowest consensus fraction and lowest auditor hit rates; the literal/cultural key is systematically overridden by more generic or proverb-like distractors.

Because **HCW >> 10%** and **perfect consensus >> 30%** in every language, scaling to N=15 without further pipeline changes is not advisable. The primary failure modes are:
1. **Corpus fallback samplers** still inject low-quality or English-idiom distractors (visible in high `fallback_count` items, e.g. Arabic 'A bad workman...' with fallback_count=5).
2. **Yoruba gold-meaning curation** preserves literal translations that auditors do not recognize as the intended key.
3. **English distractors** are too semantically distant (antonyms / unrelated life advice) and are eliminated too easily.

## 7. Appendix: Per-variant and per-generator breakdown

### 7.1 Per-variant per-language

| Variant | English Acc / Perfect / HCW | Arabic Acc / Perfect / HCW | Yoruba Acc / Perfect / HCW |
|---------|------------------------------|------------------------------|------------------------------|
| adversarial-hard-negative | 73.3% / 46.7% / 26.7% | 46.7% / 26.7% / 53.3% | 60.0% / 20.0% / 40.0% |
| adversarial-length-locked | 66.7% / 53.3% / 33.3% | 60.0% / 86.7% / 40.0% | 40.0% / 20.0% / 60.0% |
| overgenerate-select | 60.0% / 46.7% / 40.0% | 60.0% / 33.3% / 40.0% | 40.0% / 26.7% / 60.0% |
| taxonomy-guided | 60.0% / 33.3% / 33.3% | 46.7% / 53.3% / 53.3% | 66.7% / 53.3% / 33.3% |

- `adversarial-length-locked` is especially harmful for Arabic (86.7% perfect consensus) and `taxonomy-guided` lifts Yoruba correctness to 66.7%.
- No single variant satisfies all three languages simultaneously.

### 7.2 Per-generator per-language

| Generator | English Acc / Perfect / HCW | Arabic Acc / Perfect / HCW | Yoruba Acc / Perfect / HCW |
|-----------|------------------------------|------------------------------|------------------------------|
| google/gemini-2.5-flash | 65.0% / 40.0% / 35.0% | 50.0% / 55.0% / 50.0% | 45.0% / 30.0% / 55.0% |
| google/gemma-4-31b-it | 70.0% / 50.0% / 30.0% | 55.0% / 45.0% / 45.0% | 70.0% / 45.0% / 30.0% |
| qwen/qwen3.7-max | 60.0% / 45.0% / 35.0% | 55.0% / 50.0% / 45.0% | 40.0% / 15.0% / 60.0% |

- `google/gemma-4-31b-it` is the most balanced generator (best Yoruba correctness at 70.0% and lowest Yoruba HCW at 30.0%).
- `qwen/qwen3.7-max` is the weakest on Yoruba (40.0% correctness, 60.0% HCW).

## 8. Overall aggregates

- Overall consensus correctness: **102/180 = 56.7%**
- Overall perfect consensus: **75/180 = 41.7%**
- Overall HCW: **77/180 = 42.8%**
- Duplicate options: **0**
- Mean fallback count: **0.99**
- Partial + length_fallback status share: **43.9%**

---
*Report generated from `pilot1_test_audit_results.csv`, `pilot1_test_generated_mcqs.csv`, and `pilot1_test_summary.json`.*
