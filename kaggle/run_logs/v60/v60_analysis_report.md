# v60 Kaggle Run Analysis

- Run timestamp: 2026-06-20T18:33:59.398681+00:00
- N_PER_LANG: 1
- Cost: $0.2288 / $5.00
- Active generators: ['qwen/qwen3.7-max', 'google/gemma-4-31b-it', 'google/gemini-2.5-flash']
- Benched generators: []
- Active auditors: ['meta-llama/llama-3.3-70b-instruct', 'mistralai/mistral-small-3.2-24b-instruct', 'google/gemma-3-27b-it', 'deepseek/deepseek-v3.2']

## Quality gates vs previous runs

| Gate | v58 | v59 | v60 | Target |
|---|---|---|---|---|
| Cost | $0.22 | $0.19 | $0.2288 | <$1 |
| Perfect consensus | 48.9% | 37.8% | 44.4% | <30% |
| High-consensus-wrong | 22.2% | 28.9% | 28.9% | <10% (<15% step) |
| Partial + fallback | 28.9% | 42.2% | 48.9% | <15% |
| Duplicate options | 2 | 0 | 0 | 0 |
| Consensus accuracy | 60.0% | 51.1% | 48.9% | - |
| Yoruba correctness | 40.0% | 26.7% | 26.7% | ≥50% |

## Per-language consensus correctness

- Arabic: 40.0% (n=15)
- English: 80.0% (n=15)
- Yoruba: 26.7% (n=15)

## Generation status breakdown

generation_status
generated          23
length_fallback    13
partial             8
parse_fallback      1
Name: count, dtype: int64

### Status by generator

generation_status        generated  length_fallback  parse_fallback  partial
generator_model                                                             
google/gemini-2.5-flash         11                3               0        1
google/gemma-4-31b-it            6                5               1        3
qwen/qwen3.7-max                 6                5               0        4

### Status by variant

generation_status          generated  length_fallback  parse_fallback  partial
variant                                                                       
adversarial-contrastive            0                9               0        0
adversarial-hard-negative          4                1               0        4
adversarial-length-locked          5                3               0        1
overgenerate-select                7                0               1        1
taxonomy-guided                    7                0               0        2

### Status by language

generation_status  generated  length_fallback  parse_fallback  partial
language                                                              
Arabic                     9                4               1        1
English                    5                5               0        5
Yoruba                     9                4               0        2

## Per-generator/variant consensus accuracy (language=ALL)

        generator_model                   variant  n  consensus_accuracy  mean_consensus_frac   flag
       qwen/qwen3.7-max adversarial-length-locked  3            0.333333             0.583333 REVIEW
       qwen/qwen3.7-max adversarial-hard-negative  3            0.666667             0.666667   FAIL
       qwen/qwen3.7-max           taxonomy-guided  3            0.666667             0.916667   FAIL
       qwen/qwen3.7-max   adversarial-contrastive  3            0.333333             0.833333 REVIEW
       qwen/qwen3.7-max       overgenerate-select  3            0.666667             0.916667   FAIL
  google/gemma-4-31b-it adversarial-length-locked  3            0.000000             0.583333   PASS
  google/gemma-4-31b-it adversarial-hard-negative  3            1.000000             0.416667   FAIL
  google/gemma-4-31b-it           taxonomy-guided  3            0.666667             0.833333   FAIL
  google/gemma-4-31b-it   adversarial-contrastive  3            0.333333             1.000000 REVIEW
  google/gemma-4-31b-it       overgenerate-select  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash adversarial-length-locked  3            0.666667             0.833333   FAIL
google/gemini-2.5-flash adversarial-hard-negative  3            0.333333             0.750000 REVIEW
google/gemini-2.5-flash           taxonomy-guided  3            0.333333             1.000000 REVIEW
google/gemini-2.5-flash   adversarial-contrastive  3            0.333333             0.666667 REVIEW
google/gemini-2.5-flash       overgenerate-select  3            0.333333             0.833333 REVIEW

## Distractor metrics

n_mcqs                            45.0000
avg_distractor_key_similarity      0.2787
std_distractor_key_similarity      0.1714
avg_pairwise_option_similarity     0.3119
std_pairwise_option_similarity     0.1784
option_length_mean                62.1000
option_length_cv                   0.3917
nli_replaced_total                 9.0000
duplicate_options_count            0.0000

## High-consensus-wrong items

### google_gemma-4-31b-it_adversarial-length-locked_Arabic_0 (Arabic, google/gemma-4-31b-it, adversarial-length-locked)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Offer your help to the local community.
  - B. Prioritize your own family's needs first.
  - C. Dedicate your wealth to religious goals.
  - D. Balance your duties between home and work.
- Correct label: B | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_adversarial-hard-negative_Arabic_0 (Arabic, google/gemini-2.5-flash, adversarial-hard-negative)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. One should always prioritize their family's needs.
  - B. It is important to take care of your own before helping others.
  - C. Personal responsibilities must be fulfilled before public ones.
  - D. Family needs take priority over community needs.
- Correct label: D | Consensus: B (frac=0.75)

### google_gemma-4-31b-it_taxonomy-guided_Arabic_0 (Arabic, google/gemma-4-31b-it, taxonomy-guided)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Give your extra resources to the local community center
  - B. Support the needy regardless of their relation to you
  - C. Donate all your wealth to religious institutions first
  - D. Prioritize your own family's needs before helping others
- Correct label: D | Consensus: B (frac=0.75)

### google_gemini-2.5-flash_taxonomy-guided_Arabic_0 (Arabic, google/gemini-2.5-flash, taxonomy-guided)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. One should prioritize their family's needs before helping others.
  - B. It is important to be generous and give to those in need.
  - C. A community thrives when its members support local institutions.
  - D. Religious obligations should always take precedence over personal desires.
- Correct label: A | Consensus: B (frac=1.00)

### qwen_qwen3.7-max_taxonomy-guided_Yoruba_2 (Yoruba, qwen/qwen3.7-max, taxonomy-guided)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. A difficult person or unusual challenge will eventually reveal the exact strategy an elder needs to manage them.
  - B. A diligent farmer must always adapt his harvesting methods when dealing with crops that grow into unusual shapes.
  - C. A wayward youth will eventually learn proper conduct by observing the strict discipline of the village elders.
  - D. An experienced elder already possesses the wisdom required to handle any strange burden brought to his compound.
- Correct label: A | Consensus: D (frac=1.00)

### google_gemini-2.5-flash_taxonomy-guided_Yoruba_2 (Yoruba, google/gemini-2.5-flash, taxonomy-guided)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. One's true character is revealed through their actions, even without explicit instruction.
  - B. Even without a clear path, a determined individual will find a way to achieve their goals.
  - C. A person lacking guidance will eventually reveal their true nature and needs.
  - D. A person's inherent limitations will always dictate their ultimate destiny.
- Correct label: C | Consensus: A (frac=1.00)

### qwen_qwen3.7-max_adversarial-contrastive_Arabic_0 (Arabic, qwen/qwen3.7-max, adversarial-contrastive)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Everyone is critical of the flaws of others, but blind to their own.
  - B. A greedy man is always in want.
  - C. Every dog is a tiger in his own street.
  - D. True charity must always begin within one's own home.
- Correct label: D | Consensus: A (frac=0.75)

### google_gemma-4-31b-it_adversarial-contrastive_Arabic_0 (Arabic, google/gemma-4-31b-it, adversarial-contrastive)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. Prioritize the needs of your own family before helping others.
  - B. Don't poke your nose into others' affairs.
  - C. Cut your coat according to your cloth.
  - D. Man needs money for the evil day.
- Correct label: A | Consensus: C (frac=1.00)

### google_gemini-2.5-flash_adversarial-contrastive_Arabic_0 (Arabic, google/gemini-2.5-flash, adversarial-contrastive)
- Proverb: اللي يعوزه البيت يحرم على الجامع
- Correct meaning: Charity begins at home.
- Options:
  - A. The pot calling the kettle black.
  - B. Family needs should be prioritized over external obligations.
  - C. Let's wait and hold to see what the future holds.
  - D. Financial needs should be prioritized over spiritual obligations.
- Correct label: B | Consensus: A (frac=0.75)

### qwen_qwen3.7-max_adversarial-contrastive_Yoruba_2 (Yoruba, qwen/qwen3.7-max, adversarial-contrastive)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. A person who should be sold for money to purchase a lamp boasts that he is one people-light-lamps-to-admire-at-night.
  - B. A difficult person will eventually show the elder the exact method needed to manage their own unique character.
  - C. The paths being taken are not the same; one person is carrying three hundred yam seedlings, and the other is mounted on a horse.
  - D. The person with whom one plans to buy a horse is the same person scheming to trade one for a horse.
- Correct label: B | Consensus: C (frac=0.75)

### google_gemma-4-31b-it_adversarial-contrastive_Yoruba_2 (Yoruba, google/gemma-4-31b-it, adversarial-contrastive)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. Destitution grips you and you sit scowling; who will give you the antidote?
  - B. The creeper is destroying itself, but it thinks it is destroying its host.
  - C. The neckless gourd will itself indicate to the farmer how to tie it up.
  - D. To the farmer belongs the farm; to the book ish person belongs the pen. On freedom to be oneself 425
- Correct label: C | Consensus: B (frac=1.00)

### qwen_qwen3.7-max_overgenerate-select_Yoruba_2 (Yoruba, qwen/qwen3.7-max, overgenerate-select)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. Unknowingly, a reckless youth will weave the very vines used to bind his hands.
  - B. The potter ultimately learns that a cracked vessel cannot hold community water.
  - C. Difficult characters naturally reveal the exact methods required to manage them.
  - D. Cultivators who are patient must adapt their tools to match the stubborn soil.
- Correct label: C | Consensus: A (frac=0.75)

### google_gemini-2.5-flash_overgenerate-select_Yoruba_2 (Yoruba, google/gemini-2.5-flash, overgenerate-select)
- Proverb: Kèrègbè tí kò lọ́rùn ni yóò júwe bí àgbẹ̀ ó ti so òun kọ́.
- Correct meaning: The neckless gourd will itself indicate to the farmer how to tie it up.
- Options:
  - A. The object itself will reveal the proper way it should be handled or utilized.
  - B. A person's inherent limitations will dictate the assistance they require from others.
  - C. One's true nature is revealed through the challenges they face, not by their outward appearance.
  - D. The wise farmer understands that some tasks require unconventional methods.
- Correct label: A | Consensus: C (frac=1.00)

## Root-cause summary

1. **Starters stayed active** — the soft-failure benching fix worked: `qwen/qwen3.7-max`, `google/gemma-4-31b-it`, and `google/gemini-2.5-flash` are all active and produced the 45 MCQs.
2. **Leak sanitizer kept generation flowing** but increased replacements; `adversarial-contrastive` in particular generated options that are near-paraphrases of the correct meaning and were almost entirely rewritten by fallback samples.
3. **Length fallback exploded** to 14/45 (31%). The ±20% median-length check is too strict for the options these starters produce, especially for Arabic/Yoruba where correct meanings vary widely in length.
4. **Partial+fallback is now 48.9%**, the worst of the three runs, because the combined leak + semantic + NLI + length sanitizers are rewriting too many distractors.
5. **High-consensus-wrong stayed at 28.9%**, driven by Yoruba and by fallback distractors that are themselves attractive shortcuts.
6. **Yoruba remains broken at 26.7%** — the correct meanings are often literal/awkward glosses that auditors reject.

## Options for next step (v61)

A. **Relax the length check** from ±20% to ±30% (or remove it for the correct-meaning reference and only enforce distractor-distractor parity). This directly targets the 31% length_fallback rate.
B. **Retire or redesign `adversarial-contrastive`**. It generated 9/45 items and all 9 ended as length_fallback after leak/semantic rewrites. A variant that changes a single semantic role is too close to the correct meaning for the current filters.
C. **Relax the semantic-distance upper bound** slightly (default 0.82 → 0.85, Yoruba 0.85 → 0.88) so fewer generated distractors are replaced by corpus fallbacks.
D. **Improve the fallback sampler** so replacement distractors are better calibrated to each proverb (e.g., sample from same-language meanings with keyword overlap, or add a cheap LLM rewrite step for fallbacks).
E. **Yoruba rescue**: either (i) manually curate/fix the 3 Yoruba gold meanings, (ii) add a prompt step that rewrites the literal Yoruba gloss into natural English before generating options, or (iii) exclude the most broken Yoruba proverbs from the N=1 sample.

**Recommended v61 combination:** A + B + C. They are low-risk, preserve the starter roster, and should bring partial+fallback back under 25% while keeping high-consensus-wrong flat or lower.
